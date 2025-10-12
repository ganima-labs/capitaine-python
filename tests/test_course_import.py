# Tests pour la fonctionnalité d'import de cours

import pytest
import json
import tempfile
import os
from unittest.mock import Mock, patch, AsyncMock, mock_open
from fastapi.testclient import TestClient
from httpx import AsyncClient

# Importer l'application
import sys
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'app', 'backend'))

from main import app, validate_course_structure, validate_course_security, save_imported_course
from pydantic import ValidationError

# Client de test
client = TestClient(app)

# Données de test
VALID_COURSE_DATA = {
    "meta": {
        "id": "test-course",
        "title": {
            "fr": "Cours de Test",
            "en": "Test Course"
        },
        "level": "débutant",
        "estimated_hours": 5,
        "description": "Un cours de test pour l'import"
    },
    "theme": {
        "name": "test",
        "primary_color": "#0077be",
        "background_color": "#0a1929"
    },
    "exercises": [
        {
            "id": "01-test",
            "title": {
                "fr": "Exercice de test",
                "en": "Test Exercise"
            },
            "stars": 1,
            "prompt": {
                "fr": "Écris un programme qui affiche 'Hello'",
                "en": "Write a program that displays 'Hello'"
            },
            "starter": {
                "fr": "print('Hello')",
                "en": "print('Hello')"
            },
            "tests": [
                "print('Hello')"
            ],
            "hints": [
                {
                    "level": 1,
                    "text": {
                        "fr": "Utilise print()",
                        "en": "Use print()"
                    }
                }
            ]
        }
    ]
}

INVALID_COURSE_DATA = {
    "meta": {
        # ID manquant
        "title": "Cours invalide"
    },
    # exercises manquant
}

SECURITY_VIOLATION_COURSE = {
    "meta": {
        "id": "malicious-course",
        "title": {
            "fr": "Cours malveillant",
            "en": "Malicious Course"
        }
    },
    "exercises": [
        {
            "id": "01-dangerous",
            "title": "Exercice dangereux",
            "stars": 1,
            "prompt": "Test dangereux",
            "starter": "import os; os.system('rm -rf /')",
            "tests": ["import subprocess; subprocess.call('ls', shell=True)"]
        }
    ]
}

class TestCourseImportValidation:
    """Tests pour la validation de structure de cours"""

    def test_validate_valid_course_structure(self):
        """Test la validation d'une structure de cours valide"""
        result = validate_course_structure(VALID_COURSE_DATA)

        assert result['valid'] is True
        assert len(result['errors']) == 0
        assert isinstance(result['warnings'], list)

    def test_validate_course_missing_meta(self):
        """Test la validation d'un cours sans section meta"""
        course_data = {"exercises": []}
        result = validate_course_structure(course_data)

        assert result['valid'] is False
        assert "Missing 'meta' section" in result['errors']

    def test_validate_course_missing_id(self):
        """Test la validation d'un cours sans ID"""
        course_data = {
            "meta": {"title": "Test"},
            "exercises": []
        }
        result = validate_course_structure(course_data)

        assert result['valid'] is False
        assert "Course ID is required" in result['errors']

    def test_validate_course_with_suggested_id(self):
        """Test la validation avec un ID suggéré"""
        course_data = {
            "meta": {"title": "Test"},
            "exercises": []
        }
        result = validate_course_structure(course_data, "suggested-id")

        assert result['valid'] is True  # L'ID suggéré compense l'ID manquant

    def test_validate_course_missing_exercises(self):
        """Test la validation d'un cours sans exercices"""
        course_data = {
            "meta": {"id": "test", "title": "Test"}
        }
        result = validate_course_structure(course_data)

        assert result['valid'] is False
        assert "Missing 'exercises' section" in result['errors']

    def test_validate_course_invalid_exercises_type(self):
        """Test la validation avec un type invalide pour exercises"""
        course_data = {
            "meta": {"id": "test", "title": "Test"},
            "exercises": "not a list"
        }
        result = validate_course_structure(course_data)

        assert result['valid'] is False
        assert "'exercises' must be a list" in result['errors']

    def test_validate_exercise_missing_fields(self):
        """Test la validation d'exercices avec des champs manquants"""
        course_data = {
            "meta": {"id": "test", "title": "Test"},
            "exercises": [
                {
                    "id": "test-ex"
                    # title manquant
                }
            ]
        }
        result = validate_course_structure(course_data)

        assert result['valid'] is False
        assert "Exercise 1 missing 'title'" in result['errors']

    def test_validate_warnings_generation(self):
        """Test la génération d'avertissements pour les champs manquants"""
        course_data = {
            "meta": {"id": "test", "title": "Test"},  # title sans structure de langue
            "exercises": [
                {
                    "id": "test-ex",
                    "title": "Test Exercise",
                    # prompt et tests manquants -> devraient générer des warnings
                }
            ]
        }
        result = validate_course_structure(course_data)

        assert result['valid'] is True  # Pas d'erreurs bloquantes
        assert len(result['warnings']) > 0
        assert any("missing 'prompt'" in warning for warning in result['warnings'])
        assert any("missing 'tests'" in warning for warning in result['warnings'])


class TestCourseSecurityValidation:
    """Tests pour la validation de sécurité des cours"""

    @patch('main.SecurityValidator.analyze_code_security')
    def test_validate_secure_course(self, mock_analyze):
        """Test la validation d'un cours sécurisé"""
        mock_analyze.return_value = {'safe': True, 'issues': []}

        result = validate_course_security(VALID_COURSE_DATA)

        assert result['safe'] is True
        assert len(result['issues']) == 0
        mock_analyze.assert_called()

    @patch('main.SecurityValidator.analyze_code_security')
    def test_validate_course_with_security_violations(self, mock_analyze):
        """Test la validation d'un cours avec violations de sécurité"""
        mock_analyze.return_value = {
            'safe': False,
            'issues': ['Dangerous import detected: os', 'Forbidden function: system']
        }

        result = validate_course_security(SECURITY_VIOLATION_COURSE)

        assert result['safe'] is False
        assert len(result['issues']) == 2
        assert "Dangerous import detected: os" in result['issues']

    @patch('main.SecurityValidator.analyze_code_security')
    def test_validate_starter_code_multilingual(self, mock_analyze):
        """Test la validation du code starter multilingue"""
        mock_analyze.return_value = {'safe': True, 'issues': []}

        course_data = {
            "exercises": [
                {
                    "starter": {
                        "fr": "print('Bonjour')",
                        "en": "print('Hello')",
                        "es": "print('Hola')"
                    }
                }
            ]
        }

        result = validate_course_security(course_data)

        assert result['safe'] is True
        # Vérifier que tous les fragments de code ont été analysés
        assert mock_analyze.call_count == 3

    @patch('main.SecurityValidator.analyze_code_security')
    def test_validate_theory_examples(self, mock_analyze):
        """Test la validation des exemples dans la théorie"""
        mock_analyze.return_value = {'safe': True, 'issues': []}

        course_data = {
            "exercises": [
                {
                    "theory": {
                        "fr": {
                            "examples": [
                                "print('Example 1')",
                                "x = 5; print(x)"
                            ]
                        }
                    }
                }
            ]
        }

        result = validate_course_security(course_data)

        assert result['safe'] is True
        assert mock_analyze.call_count == 2  # Deux exemples

    def test_validate_empty_code_fragments(self):
        """Test que les fragments de code vides sont ignorés"""
        course_data = {
            "exercises": [
                {
                    "starter": "   ",  # Espaces vides
                    "tests": [""]     # Chaîne vide
                }
            ]
        }

        # Ne devrait pas appeler SecurityValidator pour du code vide
        with patch('main.SecurityValidator.analyze_code_security') as mock_analyze:
            result = validate_course_security(course_data)
            mock_analyze.assert_not_called()

        assert result['safe'] is True


class TestCourseImportAPI:
    """Tests pour les endpoints d'import de cours"""

    @patch('main.httpx.AsyncClient')
    @patch('main.save_imported_course')
    @patch('main.validate_course_structure')
    @patch('main.validate_course_security')
    @patch('main.course_manager')
    def test_import_course_from_url_success(self, mock_cm, mock_security, mock_structure, mock_save, mock_httpx):
        """Test l'import réussi depuis une URL"""
        # Configuration des mocks
        mock_response = Mock()
        mock_response.raise_for_status.return_value = None
        mock_response.headers = {'content-type': 'application/json'}
        mock_response.json.return_value = VALID_COURSE_DATA

        mock_client = AsyncMock()
        mock_client.get.return_value = mock_response
        mock_httpx.return_value.__aenter__.return_value = mock_client

        mock_structure.return_value = {'valid': True, 'errors': [], 'warnings': []}
        mock_security.return_value = {'safe': True, 'issues': []}
        mock_save.return_value = True
        mock_cm.load_all_courses.return_value = None

        # Test de l'endpoint
        response = client.post(
            "/api/courses/import",
            json={
                "url": "https://example.com/course.json",
                "course_id": "test-course",
                "overwrite": False
            }
        )

        assert response.status_code == 200
        data = response.json()
        assert data['success'] is True
        assert data['course_id'] == "test-course"
        assert data['imported_exercises'] == 1

    def test_import_course_invalid_url(self):
        """Test l'import avec une URL invalide"""
        response = client.post(
            "/api/courses/import",
            json={
                "url": "not-a-valid-url",
                "course_id": "test"
            }
        )

        assert response.status_code == 422  # Validation error

    @patch('main.httpx.AsyncClient')
    def test_import_course_http_error(self, mock_httpx):
        """Test l'import avec une erreur HTTP"""
        mock_client = AsyncMock()
        mock_client.get.side_effect = Exception("HTTP error")
        mock_httpx.return_value.__aenter__.return_value = mock_client

        response = client.post(
            "/api/courses/import",
            json={
                "url": "https://example.com/course.json"
            }
        )

        assert response.status_code == 200
        data = response.json()
        assert data['success'] is False
        assert "HTTP error" in data['message']

    @patch('main.httpx.AsyncClient')
    def test_import_course_json_decode_error(self, mock_httpx):
        """Test l'import avec du JSON invalide"""
        mock_response = Mock()
        mock_response.raise_for_status.return_value = None
        mock_response.json.side_effect = json.JSONDecodeError("Invalid JSON", "", 0)

        mock_client = AsyncMock()
        mock_client.get.return_value = mock_response
        mock_httpx.return_value.__aenter__.return_value = mock_client

        response = client.post(
            "/api/courses/import",
            json={
                "url": "https://example.com/course.json"
            }
        )

        assert response.status_code == 200
        data = response.json()
        assert data['success'] is False
        assert "Invalid JSON format" in data['message']

    @patch('main.save_imported_course')
    @patch('main.validate_course_structure')
    @patch('main.validate_course_security')
    def test_import_course_structure_validation_failed(self, mock_security, mock_structure, mock_save):
        """Test l'import avec échec de validation de structure"""
        mock_structure.return_value = {
            'valid': False,
            'errors': ['Missing exercises section'],
            'warnings': []
        }

        response = client.post(
            "/api/courses/import",
            json={
                "url": "https://example.com/course.json"
            }
        )

        assert response.status_code == 200
        data = response.json()
        assert data['success'] is False
        assert "Invalid course structure" in data['message']
        assert "Missing exercises section" in data['validation_errors']

    @patch('main.save_imported_course')
    @patch('main.validate_course_structure')
    @patch('main.validate_course_security')
    def test_import_course_security_validation_failed(self, mock_security, mock_structure, mock_save):
        """Test l'import avec échec de validation de sécurité"""
        mock_structure.return_value = {'valid': True, 'errors': [], 'warnings': []}
        mock_security.return_value = {
            'safe': False,
            'issues': ['Dangerous import detected']
        }

        response = client.post(
            "/api/courses/import",
            json={
                "url": "https://example.com/course.json"
            }
        )

        assert response.status_code == 200
        data = response.json()
        assert data['success'] is False
        assert "security violations" in data['message']

    def test_delete_course_builtin_protection(self):
        """Test que les cours intégrés ne peuvent pas être supprimés"""
        response = client.delete("/api/courses/python-basics")

        assert response.status_code == 403
        data = response.json()
        assert "Cannot delete built-in course" in data['detail']

    def test_delete_course_not_found(self):
        """Test la suppression d'un cours qui n'existe pas"""
        with patch('main.course_manager') as mock_cm:
            mock_cm.courses = {}  # Aucun cours

            response = client.delete("/api/courses/nonexistent-course")

            assert response.status_code == 404

    @patch('os.path.exists')
    @patch('os.remove')
    def test_delete_course_success(self, mock_remove, mock_exists):
        """Test la suppression réussie d'un cours importé"""
        mock_exists.return_value = True

        with patch('main.course_manager') as mock_cm:
            mock_cm.courses = {"test-course": VALID_COURSE_DATA}
            mock_cm.courses_dir = "/tmp/courses"

            response = client.delete("/api/courses/test-course")

            assert response.status_code == 200
            data = response.json()
            assert "deleted successfully" in data['message']


class TestCourseFileImport:
    """Tests pour l'import depuis un fichier"""

    def test_import_file_missing(self):
        """Test l'import avec aucun fichier"""
        response = client.post(
            "/api/courses/import/file",
            files={}
        )

        assert response.status_code == 422

    def test_import_file_wrong_extension(self):
        """Test l'import avec un fichier de mauvaise extension"""
        response = client.post(
            "/api/courses/import/file",
            files={"file": ("course.txt", "content", "text/plain")}
        )

        assert response.status_code == 200
        data = response.json()
        assert data['success'] is False
        assert "Only JSON files are allowed" in data['message']

    @patch('main.save_imported_course')
    @patch('main.validate_course_structure')
    @patch('main.validate_course_security')
    def test_import_file_success(self, mock_security, mock_structure, mock_save):
        """Test l'import réussi depuis un fichier"""
        mock_structure.return_value = {'valid': True, 'errors': [], 'warnings': []}
        mock_security.return_value = {'safe': True, 'issues': []}
        mock_save.return_value = True

        with patch('main.course_manager') as mock_cm:
            mock_cm.load_all_courses.return_value = None

            response = client.post(
                "/api/courses/import/file",
                files={"file": ("course.json", json.dumps(VALID_COURSE_DATA), "application/json")},
                data={"course_id": "test-course", "overwrite": "false"}
            )

            assert response.status_code == 200
            data = response.json()
            assert data['success'] is True
            assert data['course_id'] == "test-course"
            assert data['imported_exercises'] == 1


class TestCourseSave:
    """Tests pour la sauvegarde des cours importés"""

    def test_save_imported_course_new(self):
        """Test la sauvegarde d'un nouveau cours"""
        with tempfile.TemporaryDirectory() as temp_dir:
            course_data = VALID_COURSE_DATA.copy()

            result = save_imported_course("test-course", course_data, overwrite=False, courses_dir=temp_dir)

            assert result is True

            # Vérifier que le fichier a été créé
            file_path = os.path.join(temp_dir, "test-course.json")
            assert os.path.exists(file_path)

            # Vérifier le contenu
            with open(file_path, 'r', encoding='utf-8') as f:
                saved_data = json.load(f)

            assert saved_data['meta']['imported'] is True
            assert saved_data['meta']['import_source'] == 'external'

    def test_save_imported_course_overwrite_disabled(self):
        """Test la sauvegarde quand le fichier existe et overwrite=False"""
        with tempfile.TemporaryDirectory() as temp_dir:
            # Créer un fichier existant
            file_path = os.path.join(temp_dir, "existing-course.json")
            with open(file_path, 'w') as f:
                json.dump({"existing": True}, f)

            result = save_imported_course("existing-course", VALID_COURSE_DATA, overwrite=False, courses_dir=temp_dir)

            assert result is False

    def test_save_imported_course_overwrite_enabled(self):
        """Test la sauvegarde avec overwrite=True"""
        with tempfile.TemporaryDirectory() as temp_dir:
            # Créer un fichier existant
            file_path = os.path.join(temp_dir, "existing-course.json")
            with open(file_path, 'w') as f:
                json.dump({"existing": True}, f)

            result = save_imported_course("existing-course", VALID_COURSE_DATA, overwrite=True, courses_dir=temp_dir)

            assert result is True

            # Vérifier que le fichier a été écrasé
            with open(file_path, 'r', encoding='utf-8') as f:
                saved_data = json.load(f)

            assert saved_data['meta']['id'] == "test-course"

    @patch('builtins.open')
    def test_save_imported_course_error(self, mock_open):
        """Test la gestion des erreurs lors de la sauvegarde"""
        mock_open.side_effect = IOError("Permission denied")

        result = save_imported_course("test-course", VALID_COURSE_DATA, overwrite=False)

        assert result is False


@pytest.mark.asyncio
class TestCourseImportIntegration:
    """Tests d'intégration pour l'import de cours"""

    async def test_full_import_workflow(self):
        """Test le workflow complet d'import"""
        # Ces tests nécessiteraient une configuration plus complexe
        # avec des vrais fichiers et services HTTP
        pass


if __name__ == "__main__":
    pytest.main([__file__, "-v"])