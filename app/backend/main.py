from fastapi import FastAPI, HTTPException, Request, UploadFile, File
from fastapi.responses import FileResponse, JSONResponse
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, validator, HttpUrl
import httpx
import os
import logging
import json
import hashlib
from typing import Optional, Dict, Any
from urllib.parse import urlparse

from .course_manager import course_manager
from .grader import build_harness_and_run, quick_syntax_check, run_code_with_inputs
from .secure_grader import quick_syntax_check as secure_syntax_check, build_harness_and_run as secure_build_harness
from .security import SecurityValidator
from .db import init_db, save_result, get_progress
from .exercise_validator import validate_exercise, validate_course

# Configuration du logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Configuration sécurisée avec fallback
EXECUTOR = os.getenv("EXECUTOR_URL", "http://piston:2000/api/v2/execute")
USE_SECURE_EXECUTOR = os.getenv("USE_SECURE_EXECUTOR", "true").lower() == "true"

app = FastAPI(
    title="Capitaine Python API",
    description="API sécurisée pour l'apprentissage du Python",
    version="2.0.0"
)

# Configuration CORS sécurisée
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://localhost:8080"],  # Origines autorisées
    allow_credentials=True,
    allow_methods=["GET", "POST"],  # Méthodes autorisées
    allow_headers=["*"],
)

# Monter les fichiers statiques (uniquement si les répertoires existent)
if os.path.exists("frontend"):
    app.mount("/static", StaticFiles(directory="frontend"), name="static")
if os.path.exists("backend/courses/images"):
    app.mount("/static/courses/images", StaticFiles(directory="backend/courses/images"), name="course-images")

init_db()

class Submission(BaseModel):
    course_id: str = "python-basics"
    exercise_id: Optional[str] = None
    code: str
    learner: str = "Hugo"

    @validator('course_id')
    def validate_course_id(cls, v):
        return SecurityValidator.validate_course_id(v)

    @validator('exercise_id')
    def validate_exercise_id(cls, v):
        if v is not None:
            return SecurityValidator.validate_exercise_id(v)
        return v

    @validator('code')
    def validate_code(cls, v):
        if not isinstance(v, str):
            raise ValueError("Code must be a string")
        if len(v.strip()) == 0:
            raise ValueError("Code cannot be empty")
        if len(v) > SecurityValidator.MAX_CODE_LENGTH:
            raise ValueError(f"Code too long (max {SecurityValidator.MAX_CODE_LENGTH} characters)")
        return v.strip()

    @validator('learner')
    def validate_learner(cls, v):
        return SecurityValidator.validate_learner_name(v)


class InteractiveSubmission(BaseModel):
    course_id: str = "python-basics"
    exercise_id: Optional[str] = None
    code: str
    inputs: list[str]
    learner: str = "Hugo"
    timeout: int = 30

    @validator('course_id')
    def validate_course_id(cls, v):
        return SecurityValidator.validate_course_id(v)

    @validator('exercise_id')
    def validate_exercise_id(cls, v):
        if v is not None:
            return SecurityValidator.validate_exercise_id(v)
        return v

    @validator('code')
    def validate_code(cls, v):
        if not isinstance(v, str):
            raise ValueError("Code must be a string")
        if len(v.strip()) == 0:
            raise ValueError("Code cannot be empty")
        if len(v) > SecurityValidator.MAX_CODE_LENGTH:
            raise ValueError(f"Code too long (max {SecurityValidator.MAX_CODE_LENGTH} characters)")
        return v.strip()

    @validator('inputs')
    def validate_inputs(cls, v):
        if not isinstance(v, list):
            raise ValueError("Inputs must be a list")
        if len(v) == 0:
            raise ValueError("At least one input is required")
        if len(v) > 10:
            raise ValueError("Too many inputs (max 10)")

        validated_inputs = []
        for i, inp in enumerate(v):
            if not isinstance(inp, str):
                raise ValueError(f"Input {i+1} must be a string")
            # Nettoyer et limiter chaque input
            clean_input = SecurityValidator.sanitize_string(inp, 100)
            validated_inputs.append(clean_input)

        return validated_inputs

    @validator('timeout')
    def validate_timeout(cls, v):
        if not isinstance(v, int) or v < 5 or v > 120:
            raise ValueError("Timeout must be between 5 and 120 seconds")
        return v

    @validator('learner')
    def validate_learner(cls, v):
        return SecurityValidator.validate_learner_name(v)

class CourseImport(BaseModel):
    url: HttpUrl
    course_id: Optional[str] = None
    overwrite: bool = False

    @validator('url')
    def validate_url(cls, v):
        # Utiliser le validateur de sécurité amélioré
        if not SecurityValidator.validate_url_domain(str(v)):
            raise ValueError("URL domain not allowed for course import")

        return v

class CourseImportResponse(BaseModel):
    success: bool
    course_id: Optional[str] = None
    message: str
    warnings: list = []
    imported_exercises: int = 0
    validation_errors: list = []

# --- Cours API ---
@app.get("/api/courses")
def list_courses():
    """Liste tous les cours disponibles"""
    return course_manager.get_course_list()

@app.get("/api/courses/{course_id}")
def get_course(course_id: str):
    """Retourne les détails d'un cours"""
    course = course_manager.get_course(course_id)
    if not course:
        raise HTTPException(404, "Course not found")
    return course

@app.get("/api/courses/{course_id}/theme")
def get_course_theme(course_id: str):
    """Retourne le thème d'un cours"""
    return course_manager.get_course_theme(course_id)

@app.post("/api/courses/{course_id}/select")
def select_course(course_id: str):
    """Sélectionne un cours comme cours actuel"""
    success = course_manager.set_current_course(course_id)
    if not success:
        raise HTTPException(404, "Course not found")
    return {"message": f"Course {course_id} selected", "current_course": course_id}

# --- Import de cours API ---
@app.post("/api/courses/import", response_model=CourseImportResponse)
async def import_course_from_url(import_request: CourseImport, request: Request):
    """
    Importe un cours depuis une URL externe (GitHub, GitLab, etc.)
    """
    client_ip = request.client.host
    logger.info(f"Course import request from {client_ip}: {import_request.url}")

    try:
        # Télécharger le contenu depuis l'URL
        async with httpx.AsyncClient(timeout=30.0) as client:
            response = await client.get(str(import_request.url))
            response.raise_for_status()

            # Vérifier que le contenu est du JSON
            content_type = response.headers.get('content-type', '')
            if 'application/json' not in content_type and not str(import_request.url).endswith('.json'):
                logger.warning(f"Suspicious content type for course import: {content_type}")

            course_data = response.json()

        # Valider le structure du cours
        validation_result = validate_course_structure(course_data, import_request.course_id)
        if not validation_result['valid']:
            logger.warning(f"Invalid course structure from {client_ip}: {validation_result['errors']}")
            return CourseImportResponse(
                success=False,
                message="Invalid course structure",
                validation_errors=validation_result['errors']
            )

        # Déterminer l'ID du cours
        course_id = import_request.course_id or course_data.get('meta', {}).get('id')
        if not course_id:
            return CourseImportResponse(
                success=False,
                message="Course ID is required"
            )

        # Validation de sécurité de l'ID
        try:
            course_id = SecurityValidator.validate_course_id(course_id)
        except ValueError as e:
            return CourseImportResponse(
                success=False,
                message=f"Invalid course ID: {str(e)}"
            )

        # Vérifier si le cours existe déjà
        if course_id in course_manager.courses and not import_request.overwrite:
            return CourseImportResponse(
                success=False,
                message=f"Course '{course_id}' already exists. Use overwrite=true to replace it."
            )

        # Validation de sécurité du contenu du cours
        security_result = validate_course_security(course_data)
        if not security_result['safe']:
            logger.warning(f"Security issues in imported course from {client_ip}: {security_result['issues']}")
            return CourseImportResponse(
                success=False,
                message="Course contains security violations",
                validation_errors=security_result['issues']
            )

        # Sauvegarder le cours
        success = await save_imported_course(course_id, course_data, import_request.overwrite)

        if success:
            # Recharger les cours
            course_manager.load_all_courses()

            exercise_count = len(course_data.get('exercises', []))
            logger.info(f"Successfully imported course '{course_id}' with {exercise_count} exercises from {client_ip}")

            return CourseImportResponse(
                success=True,
                course_id=course_id,
                message=f"Course '{course_id}' imported successfully",
                imported_exercises=exercise_count,
                warnings=validation_result.get('warnings', [])
            )
        else:
            return CourseImportResponse(
                success=False,
                message="Failed to save imported course"
            )

    except httpx.HTTPError as e:
        logger.error(f"HTTP error importing course from {import_request.url}: {e}")
        return CourseImportResponse(
            success=False,
            message=f"Failed to download course: {str(e)}"
        )
    except json.JSONDecodeError as e:
        logger.error(f"Invalid JSON in course import: {e}")
        return CourseImportResponse(
            success=False,
            message="Invalid JSON format in course data"
        )
    except Exception as e:
        logger.error(f"Unexpected error in course import: {e}")
        return CourseImportResponse(
            success=False,
            message="Internal server error during course import"
        )

@app.post("/api/courses/import/file", response_model=CourseImportResponse)
async def import_course_from_file(
    file: UploadFile = File(...),
    course_id: Optional[str] = None,
    overwrite: bool = False
):
    """
    Importe un cours depuis un fichier uploadé
    """
    logger.info(f"Course file import request: {file.filename}")

    try:
        # Validation de sécurité du nom de fichier
        if not file.filename:
            return CourseImportResponse(
                success=False,
                message="Filename is required"
            )

        # Validation du type de fichier par extension
        if not file.filename.lower().endswith('.json'):
            return CourseImportResponse(
                success=False,
                message="Only JSON files are allowed"
            )

        # Lire le contenu du fichier avec validation de sécurité
        content = await file.read()

        # Validation de sécurité du fichier uploadé
        try:
            file_validation = SecurityValidator.validate_file_upload(
                file.filename, content, max_size=2*1024*1024  # 2MB
            )
            if not file_validation['safe']:
                logger.warning(f"File validation failed: {file.filename}")
                return CourseImportResponse(
                    success=False,
                    message="File validation failed"
                )
        except ValueError as e:
            logger.warning(f"Security validation error for file {file.filename}: {e}")
            return CourseImportResponse(
                success=False,
                message=f"File security validation failed: {str(e)}"
            )

        # Parser le JSON avec validation
        try:
            course_data = json.loads(content.decode('utf-8'))
        except json.JSONDecodeError as e:
            logger.warning(f"Invalid JSON in uploaded file {file.filename}: {e}")
            return CourseImportResponse(
                success=False,
                message="Invalid JSON format in uploaded file"
            )

        # Validation et traitement similaire à l'import depuis URL
        validation_result = validate_course_structure(course_data, course_id)
        if not validation_result['valid']:
            return CourseImportResponse(
                success=False,
                message="Invalid course structure",
                validation_errors=validation_result['errors']
            )

        final_course_id = course_id or course_data.get('meta', {}).get('id')
        if not final_course_id:
            return CourseImportResponse(
                success=False,
                message="Course ID is required"
            )

        try:
            final_course_id = SecurityValidator.validate_course_id(final_course_id)
        except ValueError as e:
            return CourseImportResponse(
                success=False,
                message=f"Invalid course ID: {str(e)}"
            )

        if final_course_id in course_manager.courses and not overwrite:
            return CourseImportResponse(
                success=False,
                message=f"Course '{final_course_id}' already exists. Use overwrite=true to replace it."
            )

        security_result = validate_course_security(course_data)
        if not security_result['safe']:
            return CourseImportResponse(
                success=False,
                message="Course contains security violations",
                validation_errors=security_result['issues']
            )

        success = await save_imported_course(final_course_id, course_data, overwrite)
        if success:
            course_manager.load_all_courses()
            exercise_count = len(course_data.get('exercises', []))
            logger.info(f"Successfully imported course '{final_course_id}' from file with {exercise_count} exercises")

            return CourseImportResponse(
                success=True,
                course_id=final_course_id,
                message=f"Course '{final_course_id}' imported successfully from file",
                imported_exercises=exercise_count,
                warnings=validation_result.get('warnings', [])
            )
        else:
            return CourseImportResponse(
                success=False,
                message="Failed to save imported course"
            )

    except json.JSONDecodeError:
        return CourseImportResponse(
            success=False,
            message="Invalid JSON format in course file"
        )
    except Exception as e:
        logger.error(f"Error in course file import: {e}")
        return CourseImportResponse(
            success=False,
            message="Internal server error during course file import"
        )

@app.delete("/api/courses/{course_id}")
def delete_course(course_id: str):
    """
    Supprime un cours importé (ne peut pas supprimer les cours intégrés)
    """
    if course_id == "python-basics":
        raise HTTPException(403, "Cannot delete built-in course 'python-basics'")

    if course_id not in course_manager.courses:
        raise HTTPException(404, "Course not found")

    try:
        # Supprimer le fichier
        course_file = os.path.join(course_manager.courses_dir, f"{course_id}.json")
        if os.path.exists(course_file):
            os.remove(course_file)

        # Retirer de la mémoire
        del course_manager.courses[course_id]

        logger.info(f"Course '{course_id}' deleted successfully")
        return {"message": f"Course '{course_id}' deleted successfully"}

    except Exception as e:
        logger.error(f"Error deleting course '{course_id}': {e}")
        raise HTTPException(500, "Failed to delete course")

# Fonctions utilitaires pour l'import
def validate_course_structure(course_data: Dict[str, Any], suggested_id: Optional[str] = None) -> Dict[str, Any]:
    """
    Valide la structure d'un cours importé
    """
    errors = []
    warnings = []

    # Vérifier les champs obligatoires
    if 'meta' not in course_data:
        errors.append("Missing 'meta' section")
    else:
        meta = course_data['meta']
        if 'id' not in meta and not suggested_id:
            errors.append("Course ID is required in meta or as parameter")
        if 'title' not in meta:
            errors.append("Missing 'title' in meta section")
        elif not isinstance(meta['title'], dict) or 'fr' not in meta['title']:
            warnings.append("Course should have a French title")

    if 'exercises' not in course_data:
        errors.append("Missing 'exercises' section")
    elif not isinstance(course_data['exercises'], list):
        errors.append("'exercises' must be a list")
    else:
        # Valider chaque exercice
        for i, exercise in enumerate(course_data['exercises']):
            if not isinstance(exercise, dict):
                errors.append(f"Exercise {i+1} is not an object")
                continue

            if 'id' not in exercise:
                errors.append(f"Exercise {i+1} missing 'id'")
            if 'title' not in exercise:
                errors.append(f"Exercise {i+1} missing 'title'")
            if 'prompt' not in exercise:
                warnings.append(f"Exercise {i+1} missing 'prompt'")
            if 'tests' not in exercise:
                warnings.append(f"Exercise {i+1} missing 'tests'")

    return {
        'valid': len(errors) == 0,
        'errors': errors,
        'warnings': warnings
    }

def validate_course_security(course_data: Dict[str, Any]) -> Dict[str, Any]:
    """
    Valide la sécurité du contenu d'un cours
    """
    issues = []

    # Analyser tous les fragments de code dans le cours
    code_fragments = []

    # Code dans les exercices
    for exercise in course_data.get('exercises', []):
        # Starter code
        if 'starter' in exercise:
            if isinstance(exercise['starter'], str):
                code_fragments.append(exercise['starter'])
            elif isinstance(exercise['starter'], dict):
                for lang_code in exercise['starter'].values():
                    if isinstance(lang_code, str):
                        code_fragments.append(lang_code)

        # Tests
        if 'tests' in exercise:
            if isinstance(exercise['tests'], list):
                code_fragments.extend(exercise['tests'])

        # Théorie - exemples de code
        if 'theory' in exercise:
            if isinstance(exercise['theory'], dict):
                for lang_theory in exercise['theory'].values():
                    if isinstance(lang_theory, dict) and 'examples' in lang_theory:
                        code_fragments.extend(lang_theory['examples'])

    # Analyser chaque fragment de code
    for code_fragment in code_fragments:
        if isinstance(code_fragment, str) and len(code_fragment.strip()) > 0:
            security_analysis = SecurityValidator.analyze_code_security(code_fragment)
            if not security_analysis['safe']:
                issues.extend(security_analysis['issues'])

    return {
        'safe': len(issues) == 0,
        'issues': issues
    }

async def save_imported_course(course_id: str, course_data: Dict[str, Any], overwrite: bool = False) -> bool:
    """
    Sauvegarde un cours importé dans un fichier JSON
    """
    try:
        # S'assurer que le répertoire des cours existe
        os.makedirs(course_manager.courses_dir, exist_ok=True)

        course_file = os.path.join(course_manager.courses_dir, f"{course_id}.json")

        # Vérifier si le fichier existe
        if os.path.exists(course_file) and not overwrite:
            return False

        # Ajouter des métadonnées d'import
        if 'meta' not in course_data:
            course_data['meta'] = {}

        course_data['meta']['imported'] = True
        course_data['meta']['imported_at'] = None  # Will be set by the caller if needed
        course_data['meta']['import_source'] = 'external'

        # Sauvegarder le fichier
        with open(course_file, 'w', encoding='utf-8') as f:
            json.dump(course_data, f, indent=2, ensure_ascii=False)

        return True

    except Exception as e:
        logger.error(f"Error saving imported course '{course_id}': {e}")
        return False

# --- Exercices API ---
@app.get("/api/courses/{course_id}/exercises")
def list_course_exercises(course_id: str):
    """Liste les exercices d'un cours"""
    exercises = course_manager.get_course_exercises(course_id)
    if not exercises:
        raise HTTPException(404, "Course not found")
    return exercises

@app.get("/api/courses/{course_id}/exercises/{exercise_id}")
def get_exercise(course_id: str, exercise_id: str):
    """Retourne les détails d'un exercice"""
    exercise = course_manager.get_exercise(course_id, exercise_id)
    if not exercise:
        raise HTTPException(404, "Exercise not found")
    return exercise

# --- API legacy pour compatibilité ---
@app.get("/api/exercises")
def list_exercises_legacy():
    """API legacy - retourne les exercices du premier cours disponible"""
    courses = course_manager.get_course_list()
    if not courses:
        return []
    return course_manager.get_course_exercises(courses[0]["id"])

@app.get("/api/exercises/{eid}")
def get_exercise_legacy(eid: str):
    """API legacy - cherche l'exercice dans tous les cours"""
    courses = course_manager.get_course_list()
    for course in courses:
        exercise = course_manager.get_exercise(course["id"], eid)
        if exercise:
            return exercise
    raise HTTPException(404, "Exercise not found")

@app.post("/api/run")
async def run_code(s: Submission, request: Request):
    """
    Endpoint sécurisé pour l'exécution de code
    """
    try:
        # Logger la requête pour monitoring
        client_ip = request.client.host
        logger.info(f"Code execution request from {client_ip} for course {s.course_id}")

        # Validation de sécurité supplémentaire
        security_analysis = SecurityValidator.analyze_code_security(s.code)
        if not security_analysis['safe']:
            logger.warning(f"Security violation detected from {client_ip}: {security_analysis['issues']}")
            raise HTTPException(
                status_code=400,
                detail={
                    "error": "Code rejected for security reasons",
                    "issues": security_analysis['issues'],
                    "risk_level": security_analysis['risk_level']
                }
            )

        # Choisir le méthode d'exécution sécurisée
        if USE_SECURE_EXECUTOR:
            ok, out = await secure_syntax_check(EXECUTOR, s.code)
        else:
            # Utiliser l'ancien système avec validation
            ok, out = await quick_syntax_check(EXECUTOR, s.code)

        # Logger le résultat
        logger.info(f"Code execution result for {client_ip}: success={ok}")

        # Nettoyer la sortie pour éviter les fuites d'information
        if isinstance(out, dict):
            if 'stdout' in out:
                out['stdout'] = SecurityValidator.sanitize_error_message(str(out['stdout']))
            if 'stderr' in out:
                out['stderr'] = SecurityValidator.sanitize_error_message(str(out['stderr']))

        return out

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Unexpected error in run_code: {e}")
        raise HTTPException(
            status_code=500,
            detail={"error": "Internal server error during code execution"}
        )

@app.post("/api/run-with-inputs")
async def run_code_with_inputs_endpoint(s: InteractiveSubmission, request: Request):
    """
    Endpoint sécurisé pour l'exécution de code avec inputs utilisateur
    """
    try:
        # Logger la requête pour monitoring
        client_ip = request.client.host
        logger.info(f"Interactive code execution request from {client_ip} for course {s.course_id}")

        # Validation de sécurité avec autorisation pour input()
        security_analysis = SecurityValidator.analyze_code_security(s.code, allow_input=True)
        if not security_analysis['safe']:
            logger.warning(f"Security violation detected in interactive execution from {client_ip}: {security_analysis['issues']}")
            raise HTTPException(
                status_code=400,
                detail={
                    "error": "Code rejected for security reasons",
                    "issues": security_analysis['issues'],
                    "risk_level": security_analysis['risk_level']
                }
            )

        # Vérifier que le code utilise bien input() si l'utilisateur fournit des inputs
        if not security_analysis.get('has_input', False):
            logger.warning(f"No input() detected in code but inputs provided from {client_ip}")
            raise HTTPException(
                status_code=400,
                detail={
                    "error": "No input() function detected in code but inputs were provided",
                    "hint": "Make sure your code uses input() to read user input"
                }
            )

        # Exécuter le code avec les inputs fournis
        result = await run_code_with_inputs(EXECUTOR, s.code, s.inputs, s.timeout)

        # Nettoyer la sortie pour éviter les fuites d'information
        if result.get('output'):
            result['output'] = SecurityValidator.sanitize_error_message(str(result['output']))

        # Logger le résultat
        logger.info(f"Interactive code execution result for {client_ip}: success={result.get('ok')}, inputs_used={result.get('inputs_used', 0)}")

        # Ajouter des méta-informations sur le type d'exécution
        result['execution_type'] = 'interactive'
        result['inputs_provided'] = len(s.inputs)

        return result

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Unexpected error in run_code_with_inputs: {e}")
        raise HTTPException(
            status_code=500,
            detail={"error": "Internal server error during interactive code execution"}
        )

@app.post("/api/grade")
async def grade_code(s: Submission, request: Request):
    """
    Endpoint sécurisé pour la validation de code avec tests
    """
    try:
        # Logger la requête pour monitoring
        client_ip = request.client.host
        logger.info(f"Code grading request from {client_ip} for course {s.course_id}, exercise {s.exercise_id}")

        # Validation de l'exercice
        exercise = course_manager.get_exercise(s.course_id, s.exercise_id)
        if not exercise:
            raise HTTPException(404, "Exercise not found")

        # Validation de sécurité supplémentaire
        security_analysis = SecurityValidator.analyze_code_security(s.code)
        if not security_analysis['safe']:
            logger.warning(f"Security violation detected in grading from {client_ip}: {security_analysis['issues']}")
            raise HTTPException(
                status_code=400,
                detail={
                    "error": "Code rejected for security reasons",
                    "issues": security_analysis['issues'],
                    "risk_level": security_analysis['risk_level']
                }
            )

        # Validation de sécurité des tests
        test_code = "\n".join(exercise.get("tests", []))
        if test_code:
            test_security = SecurityValidator.analyze_code_security(test_code)
            if not test_security['safe']:
                logger.error(f"Security issue in test code for exercise {s.exercise_id}: {test_security['issues']}")
                raise HTTPException(
                    status_code=500,
                    detail={"error": "Exercise test code has security issues"}
                )

        # Choisir la méthode d'exécution sécurisée
        if USE_SECURE_EXECUTOR:
            result = await secure_build_harness(EXECUTOR, s.code, exercise["tests"])
        else:
            # Utiliser l'ancien système avec validation
            result = await build_harness_and_run(EXECUTOR, s.code, exercise["tests"])

        # Préparer les hints et messages
        if not result.get("ok"):
            hint_lines = ["Pas grave ! Quelques pistes 🔍 :"]
            for h in exercise.get("hints", []):
                hint_lines.append(f"- {h}")
            result["hint"] = "\n".join(hint_lines)
        else:
            result["hint"] = "Bravo ! 🟊 Tu gagnes " + "★"*exercise["stars"]

        # Nettoyer les résultats pour éviter les fuites d'information
        if 'raw' in result and isinstance(result['raw'], dict):
            if 'stdout' in result['raw']:
                result['raw']['stdout'] = SecurityValidator.sanitize_error_message(str(result['raw']['stdout']))
            if 'stderr' in result['raw']:
                result['raw']['stderr'] = SecurityValidator.sanitize_error_message(str(result['raw']['stderr']))

        # Sauvegarder le résultat
        save_result(s.learner, f"{s.course_id}_{exercise['id']}", result)

        # Logger le résultat
        logger.info(f"Code grading result for {client_ip}: success={result.get('ok')}")

        return {"result": result, "progress": get_progress(s.learner)}

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Unexpected error in grade_code: {e}")
        raise HTTPException(
            status_code=500,
            detail={"error": "Internal server error during code grading"}
        )

@app.get("/api/progress")
def get_user_progress(learner: str = "Hugo"):
    """
    Endpoint sécurisé pour récupérer la progression
    """
    try:
        # Validation du nom d'apprenant
        validated_learner = SecurityValidator.validate_learner_name(learner)
        return get_progress(validated_learner)
    except ValueError as e:
        raise HTTPException(status_code=400, detail={"error": str(e)})

@app.get("/api/health")
def health_check():
    """
    Endpoint de monitoring de santé de l'API
    """
    return {
        "status": "healthy",
        "version": "2.0.0",
        "security": {
            "secure_executor_enabled": USE_SECURE_EXECUTOR,
            "max_code_length": SecurityValidator.MAX_CODE_LENGTH,
            "max_execution_time": SecurityValidator.MAX_EXECUTION_TIME
        },
        "executor": EXECUTOR
    }

@app.get("/api/security/info")
def security_info():
    """
    Endpoint avec informations sur les mesures de sécurité
    """
    return {
        "security_features": [
            "Input validation and sanitization",
            "Code security analysis",
            "Obfuscation detection",
            "File upload security validation",
            "URL domain validation",
            "Sandboxed execution environment",
            "Resource limits enforcement",
            "Request logging and monitoring",
            "Error message sanitization",
            "CORS protection",
            "SQL injection prevention"
        ],
        "blocked_patterns": len(SecurityValidator.DANGEROUS_PATTERNS),
        "blocked_modules": len(SecurityValidator.DANGEROUS_MODULES),
        "max_code_length": SecurityValidator.MAX_CODE_LENGTH,
        "execution_timeout": SecurityValidator.MAX_EXECUTION_TIME,
        "max_file_size": 2*1024*1024,  # 2MB
        "allowed_file_types": ["json"],
        "allowed_domains": [
            'github.com', 'raw.githubusercontent.com', 'gitlab.com',
            'gist.githubusercontent.com', 'pastebin.com', 'dpaste.org'
        ]
    }

@app.post("/api/security/validate")
async def validate_code_security(request: Request):
    """
    Endpoint pour valider la sécurité d'un code sans l'exécuter
    """
    try:
        data = await request.json()
        code = data.get('code', '')

        if not isinstance(code, str):
            raise HTTPException(status_code=400, detail="Code must be a string")

        # Analyse de sécurité
        security_analysis = SecurityValidator.analyze_code_security(code)

        # Logging pour monitoring
        client_ip = request.client.host
        logger.info(f"Security validation request from {client_ip}: risk={security_analysis['risk_level']}")

        return {
            "safe": security_analysis['safe'],
            "risk_level": security_analysis['risk_level'],
            "issues": security_analysis['issues'],
            "warnings": security_analysis['warnings'],
            "code_length": len(code),
            "timestamp": logger.handlers[0].formatter.formatTime(logger.makeRecord(
                'security', 20, "", 0, "", (), None
            )) if logger.handlers else None
        }

    except Exception as e:
        logger.error(f"Error in security validation: {e}")
        raise HTTPException(status_code=500, detail="Security validation failed")

@app.get("/")
def front():
    if os.path.exists("frontend/index.html"):
        return FileResponse("frontend/index.html")
    else:
        return {"message": "Capitaine Python API", "version": "2.0.0"}

# --- Validation API ---
@app.post("/api/validate/exercise")
async def validate_exercise_endpoint(request: Request):
    """
    Endpoint pour valider la qualité d'un exercice
    """
    try:
        data = await request.json()
        exercise = data.get('exercise')
        strict_mode = data.get('strict_mode', False)

        if not exercise:
            raise HTTPException(status_code=400, detail="Exercise data is required")

        # Validation de l'exercice
        result = validate_exercise(exercise, strict_mode)

        # Logging pour monitoring
        client_ip = request.client.host
        logger.info(f"Exercise validation request from {client_ip}: exercise_id={result.get('exercise_id')}, valid={result.get('valid')}, score={result.get('score')}")

        return result

    except Exception as e:
        logger.error(f"Error in exercise validation: {e}")
        raise HTTPException(status_code=500, detail="Exercise validation failed")

@app.post("/api/validate/course")
async def validate_course_endpoint(request: Request):
    """
    Endpoint pour valider la qualité d'un cours complet
    """
    try:
        data = await request.json()
        course = data.get('course')
        strict_mode = data.get('strict_mode', False)

        if not course:
            raise HTTPException(status_code=400, detail="Course data is required")

        # Validation du cours
        result = validate_course(course, strict_mode)

        # Logging pour monitoring
        client_ip = request.client.host
        logger.info(f"Course validation request from {client_ip}: course_id={result.get('course_id')}, valid={result.get('valid')}, exercises={result.get('total_exercises')}")

        return result

    except Exception as e:
        logger.error(f"Error in course validation: {e}")
        raise HTTPException(status_code=500, detail="Course validation failed")

@app.get("/api/validate/courses/{course_id}")
def validate_existing_course(course_id: str):
    """
    Valide un cours existant dans le système
    """
    try:
        # Récupérer le cours
        course = course_manager.get_course(course_id)
        if not course:
            raise HTTPException(404, "Course not found")

        # Validation du cours
        result = validate_course(course, strict_mode=False)

        logger.info(f"Existing course validation: course_id={course_id}, valid={result.get('valid')}, score={result.get('average_score')}")

        return result

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error validating existing course {course_id}: {e}")
        raise HTTPException(status_code=500, detail="Course validation failed")

@app.get("/api/validate/exercises/{course_id}/{exercise_id}")
def validate_existing_exercise(course_id: str, exercise_id: str):
    """
    Valide un exercice existant dans le système
    """
    try:
        # Récupérer l'exercice
        exercise = course_manager.get_exercise(course_id, exercise_id)
        if not exercise:
            raise HTTPException(404, "Exercise not found")

        # Validation de l'exercice
        result = validate_exercise(exercise, strict_mode=False)

        logger.info(f"Existing exercise validation: course_id={course_id}, exercise_id={exercise_id}, valid={result.get('valid')}, score={result.get('score')}")

        return result

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error validating existing exercise {course_id}/{exercise_id}: {e}")
        raise HTTPException(status_code=500, detail="Exercise validation failed")

@app.get("/api/validate/stats")
def get_validation_stats():
    """
    Retourne des statistiques sur la qualité des exercices et cours
    """
    try:
        courses = course_manager.get_course_list()
        total_courses = len(courses)
        total_exercises = 0
        valid_exercises = 0
        total_score = 0
        error_count = 0
        warning_count = 0

        course_details = []

        for course in courses:
            course_data = course_manager.get_course(course['id'])
            if course_data:
                validation_result = validate_course(course_data, strict_mode=False)

                course_details.append({
                    'course_id': course['id'],
                    'title': course['title'],
                    'valid': validation_result['valid'],
                    'exercises': validation_result['total_exercises'],
                    'valid_exercises': validation_result['valid_exercises'],
                    'average_score': validation_result['average_score'],
                    'error_count': validation_result['error_count'],
                    'warning_count': validation_result['warning_count']
                })

                total_exercises += validation_result['total_exercises']
                valid_exercises += validation_result['valid_exercises']
                total_score += validation_result['average_score'] * validation_result['total_exercises']
                error_count += validation_result['error_count']
                warning_count += validation_result['warning_count']

        average_score = total_score / total_exercises if total_exercises > 0 else 0
        overall_quality = (valid_exercises / total_exercises * 100) if total_exercises > 0 else 0

        return {
            'summary': {
                'total_courses': total_courses,
                'total_exercises': total_exercises,
                'valid_exercises': valid_exercises,
                'overall_quality_percent': round(overall_quality, 1),
                'average_score': round(average_score, 1),
                'total_issues': error_count + warning_count,
                'error_count': error_count,
                'warning_count': warning_count
            },
            'courses': course_details,
            'health_status': {
                'status': 'healthy' if overall_quality >= 80 else 'needs_attention' if overall_quality >= 60 else 'poor',
                'message': f"🎯 Qualité globale: {overall_quality:.1f}% ({valid_exercises}/{total_exercises} exercices valides)"
            }
        }

    except Exception as e:
        logger.error(f"Error getting validation stats: {e}")
        raise HTTPException(status_code=500, detail="Failed to get validation stats")

@app.get("/test")
def test_page():
    """Page de test pour diagnostiquer les problèmes"""
    if os.path.exists("frontend/test.html"):
        return FileResponse("frontend/test.html")
    else:
        return {"error": "Test page not found"}
