from fastapi import FastAPI, HTTPException
from fastapi.responses import FileResponse, JSONResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel
import httpx, os
from .course_manager import course_manager
from .grader import build_harness_and_run, quick_syntax_check
from .db import init_db, save_result, get_progress

EXECUTOR = os.getenv("EXECUTOR_URL", "http://piston:2000/api/v2/execute")
app = FastAPI(title="Capitaine Python API")

# Monter les fichiers statiques
app.mount("/static", StaticFiles(directory="frontend"), name="static")
# Monter les images des cours
app.mount("/static/courses/images", StaticFiles(directory="backend/courses/images"), name="course-images")

init_db()

class Submission(BaseModel):
    course_id: str = "python-basics"
    exercise_id: str | None = None
    code: str
    learner: str = "Hugo"

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
def list_exercises():
    """API legacy - retourne les exercices du premier cours disponible"""
    courses = course_manager.get_course_list()
    if not courses:
        return []
    return course_manager.get_course_exercises(courses[0]["id"])

@app.get("/api/exercises/{eid}")
def get_exercise(eid: str):
    """API legacy - cherche l'exercice dans tous les cours"""
    courses = course_manager.get_course_list()
    for course in courses:
        exercise = course_manager.get_exercise(course["id"], eid)
        if exercise:
            return exercise
    raise HTTPException(404, "Exercise not found")

@app.post("/api/run")
async def run_code(s: Submission):
    # lightweight exec without tests
    ok, out = await quick_syntax_check(EXECUTOR, s.code)
    return out

@app.post("/api/grade")
async def grade_code(s: Submission):
    # Utiliser le course_id de la soumission
    exercise = course_manager.get_exercise(s.course_id, s.exercise_id)
    if not exercise:
        raise HTTPException(404, "Exercise not found")

    result = await build_harness_and_run(EXECUTOR, s.code, exercise["tests"])
    # add friendly hints if not ok
    if not result.get("ok"):
        hint_lines = ["Pas grave ! Quelques pistes 🔍 :"]
        for h in exercise.get("hints", []):
            hint_lines.append(f"- {h}")
        result["hint"] = "\n".join(hint_lines)
    else:
        result["hint"] = "Bravo ! 🟊 Tu gagnes " + "★"*exercise["stars"]

    save_result(s.learner, f"{s.course_id}_{exercise['id']}", result)
    return {"result": result, "progress": get_progress(s.learner)}

@app.get("/api/progress")
def get_user_progress(learner: str = "Hugo"):
    """Retourne la progression d'un apprenant"""
    return get_progress(learner)

@app.get("/")
def front():
    return FileResponse("frontend/index.html")
