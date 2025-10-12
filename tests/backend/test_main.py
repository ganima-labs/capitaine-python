"""
Tests pour le module main.py
Couvre les endpoints API et la logique principale
"""

import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), '..', '..'))
import pytest
import json
import os
import tempfile
from unittest.mock import Mock, patch, AsyncMock
from fastapi.testclient import TestClient
from fastapi import HTTPException
from io import StringIO

# Importer l'application
from backend.main import app
from backend.security import SecurityValidator

client = TestClient(app)


class TestHealthEndpoints:
    """Tests pour les endpoints de santé"""

    def test_health_check(self):
        """Test endpoint /api/health"""
        response = client.get("/api/health")
        assert response.status_code == 200

        data = response.json()
        assert data["status"] == "healthy"
        assert "version" in data
        assert "security" in data
        assert "executor" in data

        # Vérifier les informations de sécurité
        security_info = data["security"]
        assert "secure_executor_enabled" in security_info
        assert "max_code_length" in security_info
        assert "max_execution_time" in security_info

    def test_security_info_endpoint(self):
        """Test endpoint /api/security/info"""
        response = client.get("/api/security/info")
        assert response.status_code == 200

        data = response.json()
        assert "security_features" in data
        assert "blocked_patterns" in data
        assert "blocked_modules" in data
        assert "max_code_length" in data
        assert "execution_timeout" in data

        # Vérifier qu'il y a des features de sécurité
        assert len(data["security_features"]) > 0
        assert data["blocked_patterns"] > 0
        assert data["blocked_modules"] > 0


class TestRootEndpoint:
    """Tests pour l'endpoint racine"""

    def test_root_endpoint_without_frontend(self):
        """Test endpoint / quand le frontend n'existe pas"""
        response = client.get("/")
        assert response.status_code == 200

        data = response.json()
        assert data["message"] == "Capitaine Python API"
        assert data["version"] == "2.0.0"

    @patch('os.path.exists')
    def test_root_endpoint_with_frontend(self, mock_exists):
        """Test endpoint / quand le frontend existe"""
        mock_exists.return_value = True

        # Mock FileResponse
        with patch('main.FileResponse') as mock_file_response:
            mock_response = Mock()
            mock_file_response.return_value = mock_response

            response = client.get("/")
            assert response.status_code == 200


class TestSubmissionValidation:
    """Tests pour la validation des soumissions"""

    def test_valid_submission(self):
        """Test soumission valide"""
        submission = {
            "course_id": "python-basics",
            "exercise_id": "hello-world",
            "code": "print('Hello, World!')",
            "learner": "TestUser"
        }

        # Simuler la validation de sécurité
        with patch('security.SecurityValidator.analyze_code_security') as mock_security:
            mock_security.return_value = {'safe': True, 'issues': [], 'risk_level': 'low'}

            # Mock du grader
            with patch('main.quick_syntax_check') as mock_grader:
                mock_grader.return_value = (True, {'stdout': 'Hello, World!\n', 'stderr': ''})

                response = client.post("/api/run", json=submission)
                assert response.status_code == 200

    def test_submission_invalid_course_id(self):
        """Test soumission avec course_id invalide"""
        submission = {
            "course_id": "python<script>alert('xss')</script>",
            "code": "print('test')",
            "learner": "TestUser"
        }

        response = client.post("/api/run", json=submission)
        assert response.status_code == 422  # Validation error

    def test_submission_invalid_exercise_id(self):
        """Test soumission avec exercise_id invalide"""
        submission = {
            "course_id": "python-basics",
            "exercise_id": "../etc/passwd",
            "code": "print('test')",
            "learner": "TestUser"
        }

        response = client.post("/api/run", json=submission)
        assert response.status_code == 422

    def test_submission_empty_code(self):
        """Test soumission avec code vide"""
        submission = {
            "course_id": "python-basics",
            "code": "",
            "learner": "TestUser"
        }

        response = client.post("/api/run", json=submission)
        assert response.status_code == 422

    def test_submission_code_too_long(self):
        """Test soumission avec code trop long"""
        long_code = "print('x')\n" * 1000  # Dépasse la limite

        submission = {
            "course_id": "python-basics",
            "code": long_code,
            "learner": "TestUser"
        }

        response = client.post("/api/run", json=submission)
        assert response.status_code == 422

    def test_submission_invalid_learner_name(self):
        """Test soumission avec nom d'apprenant invalide"""
        submission = {
            "course_id": "python-basics",
            "code": "print('test')",
            "learner": "<script>alert('xss')</script>"
        }

        response = client.post("/api/run", json=submission)
        assert response.status_code == 422


class TestCodeExecutionSecurity:
    """Tests pour la sécurité de l'exécution de code"""

    def test_dangerous_code_rejection(self):
        """Test rejet de code dangereux"""
        dangerous_submission = {
            "course_id": "python-basics",
            "code": "import os; os.system('ls')",
            "learner": "TestUser"
        }

        response = client.post("/api/run", json=dangerous_submission)
        assert response.status_code == 400

        data = response.json()
        assert "security" in data["detail"]["error"].lower()
        assert "issues" in data["detail"]

    def test_code_execution_logging(self):
        """Test que l'exécution de code est bien loggée"""
        submission = {
            "course_id": "python-basics",
            "code": "print('Hello')",
            "learner": "TestUser"
        }

        with patch('main.logger') as mock_logger:
            with patch('security.SecurityValidator.analyze_code_security') as mock_security:
                mock_security.return_value = {'safe': True, 'issues': [], 'risk_level': 'low'}

                with patch('main.quick_syntax_check') as mock_grader:
                    mock_grader.return_value = (True, {'stdout': 'Hello\n', 'stderr': ''})

                    client.post("/api/run", json=submission)

                    # Vérifier que le logger a été appelé
                    mock_logger.info.assert_called()
                    mock_logger.error.assert_not_called()

    def test_error_sanitization(self):
        """Test sanitification des erreurs"""
        submission = {
            "course_id": "python-basics",
            "code": "print('test')",
            "learner": "TestUser"
        }

        with patch('security.SecurityValidator.analyze_code_security') as mock_security:
            mock_security.return_value = {'safe': True, 'issues': [], 'risk_level': 'low'}

            with patch('main.quick_syntax_check') as mock_grader:
                # Simuler une erreur avec chemin sensible
                mock_grader.return_value = (False, {
                    'stderr': 'Error at /home/user/secrets.txt: line 42'
                })

                response = client.post("/api/run", json=submission)
                assert response.status_code == 200

                # Vérifier que l'erreur a été sanitizée
                stderr_output = response.json()['stderr']
                assert '/home/user' not in stderr_output
                assert '[PATH]' in stderr_output


class TestGradingEndpoint:
    """Tests pour l'endpoint de grading"""

    def test_valid_grading_request(self):
        """Test requête de grading valide"""
        submission = {
            "course_id": "python-basics",
            "exercise_id": "hello-world",
            "code": "def hello():\n    return 'Hello, World!'",
            "learner": "TestUser"
        }

        with patch('security.SecurityValidator.analyze_code_security') as mock_security:
            mock_security.return_value = {'safe': True, 'issues': [], 'risk_level': 'low'}

            # Mock du course manager
            with patch('course_manager.course_manager.get_exercise') as mock_get_exercise:
                mock_exercise = {
                    "id": "hello-world",
                    "title": "Hello World",
                    "stars": 1,
                    "tests": ["result = hello()", "assert result == 'Hello, World!'"],
                    "hints": ["Use the print() function"]
                }
                mock_get_exercise.return_value = mock_exercise

                # Mock du grader
                with patch('main.secure_build_harness') as mock_grader:
                    mock_grader.return_value = {
                        'ok': True,
                        'stdout': '__ALL_TESTS_OK__\n',
                        'stderr': ''
                    }

                    response = client.post("/api/grade", json=submission)
                    assert response.status_code == 200

                    data = response.json()
                    assert "result" in data
                    assert "progress" in data

    def test_grading_nonexistent_exercise(self):
        """Test grading pour exercice inexistant"""
        submission = {
            "course_id": "python-basics",
            "exercise_id": "nonexistent",
            "code": "print('test')",
            "learner": "TestUser"
        }

        with patch('course_manager.course_manager.get_exercise') as mock_get_exercise:
            mock_get_exercise.return_value = None

            response = client.post("/api/grade", json=submission)
            assert response.status_code == 404

    def test_grading_with_hints(self):
        """Test que les hints sont générés pour les exercices échoués"""
        submission = {
            "course_id": "python-basics",
            "exercise_id": "hello-world",
            "code": "print('wrong')",
            "learner": "TestUser"
        }

        with patch('security.SecurityValidator.analyze_code_security') as mock_security:
            mock_security.return_value = {'safe': True, 'issues': [], 'risk_level': 'low'}

            with patch('course_manager.course_manager.get_exercise') as mock_get_exercise:
                mock_exercise = {
                    "id": "hello-world",
                    "stars": 2,
                    "hints": ["Use print()", "Check your syntax"]
                }
                mock_get_exercise.return_value = mock_exercise

                with patch('main.secure_build_harness') as mock_grader:
                    mock_grader.return_value = {'ok': False}

                    response = client.post("/api/grade", json=submission)
                    assert response.status_code == 200

                    data = response.json()
                    assert "hint" in data["result"]
                    assert "Pas grave" in data["result"]["hint"]
                    assert "★" in data["result"]["hint"]


class TestProgressEndpoint:
    """Tests pour l'endpoint de progression"""

    def test_get_progress_valid_learner(self):
        """Test récupération progression pour apprenant valide"""
        with patch('main.get_progress') as mock_get_progress:
            mock_get_progress.return_value = {
                "exercises_completed": 5,
                "total_exercises": 10,
                "courses": [
                    {"id": "python-basics", "progress": 0.8}
                ]
            }

            response = client.get("/api/progress?learner=TestUser")
            assert response.status_code == 200

            data = response.json()
            assert "exercises_completed" in data
            assert "total_exercises" in data
            assert "courses" in data

    def test_get_progress_invalid_learner_name(self):
        """Test récupération progression avec nom invalide"""
        response = client.get("/api/progress?learner=<script>alert('xss')</script>")
        assert response.status_code == 400

        data = response.json()
        assert "error" in data["detail"]


class TestCourseEndpoints:
    """Tests pour les endpoints de cours"""

    def test_list_courses(self):
        """Test liste des cours"""
        with patch('course_manager.course_manager.get_course_list') as mock_get_list:
            mock_get_list.return_value = [
                {"id": "python-basics", "title": "Python Basics"},
                {"id": "advanced-python", "title": "Advanced Python"}
            ]

            response = client.get("/api/courses")
            assert response.status_code == 200

            data = response.json()
            assert len(data) == 2
            assert data[0]["id"] == "python-basics"

    def test_get_course_valid(self):
        """Test récupération d'un cours valide"""
        with patch('course_manager.course_manager.get_course') as mock_get_course:
            mock_course = {
                "id": "python-basics",
                "title": "Python Basics",
                "description": "Learn Python fundamentals"
            }
            mock_get_course.return_value = mock_course

            response = client.get("/api/courses/python-basics")
            assert response.status_code == 200

            data = response.json()
            assert data["id"] == "python-basics"

    def test_get_course_invalid(self):
        """Test récupération d'un cours invalide"""
        with patch('course_manager.course_manager.get_course') as mock_get_course:
            mock_get_course.return_value = None

            response = client.get("/api/courses/nonexistent")
            assert response.status_code == 404

    def test_get_course_theme(self):
        """Test récupération du thème d'un cours"""
        with patch('course_manager.course_manager.get_course_theme') as mock_get_theme:
            mock_get_theme.return_value = {"primary": "#3B82F6", "secondary": "#1E40AF"}

            response = client.get("/api/courses/python-basics/theme")
            assert response.status_code == 200

            data = response.json()
            assert "primary" in data
            assert "secondary" in data

    def test_select_course(self):
        """Test sélection d'un cours"""
        with patch('course_manager.course_manager.set_current_course') as mock_set_course:
            mock_set_course.return_value = True

            response = client.post("/api/courses/python-basics/select")
            assert response.status_code == 200

            data = response.json()
            assert "python-basics" in data["message"]
            assert data["current_course"] == "python-basics"

    def test_select_invalid_course(self):
        """Test sélection d'un cours invalide"""
        with patch('course_manager.course_manager.set_current_course') as mock_set_course:
            mock_set_course.return_value = False

            response = client.post("/api/courses/nonexistent/select")
            assert response.status_code == 404


class TestExerciseEndpoints:
    """Tests pour les endpoints d'exercices"""

    def test_list_course_exercises(self):
        """Test liste des exercices d'un cours"""
        with patch('course_manager.course_manager.get_course_exercises') as mock_get_exercises:
            mock_get_exercises.return_value = [
                {"id": "ex1", "title": "Print Statement"},
                {"id": "ex2", "title": "Variables"}
            ]

            response = client.get("/api/courses/python-basics/exercises")
            assert response.status_code == 200

            data = response.json()
            assert len(data) == 2

    def test_get_exercise(self):
        """Test récupération d'un exercice"""
        with patch('course_manager.course_manager.get_exercise') as mock_get_exercise:
            mock_exercise = {
                "id": "ex1",
                "title": "Print Statement",
                "stars": 1,
                "prompt": "Print 'Hello, World!'"
            }
            mock_get_exercise.return_value = mock_exercise

            response = client.get("/api/courses/python-basics/exercises/ex1")
            assert response.status_code == 200

            data = response.json()
            assert data["id"] == "ex1"

    def test_legacy_list_exercises(self):
        """Test API legacy pour lister les exercices"""
        with patch('course_manager.course_manager.get_course_list') as mock_get_list:
            mock_get_list.return_value = [{"id": "python-basics"}]

            with patch('course_manager.course_manager.get_course_exercises') as mock_get_exercises:
                mock_get_exercises.return_value = [{"id": "ex1", "title": "Print"}]

                response = client.get("/api/exercises")
                assert response.status_code == 200

    def test_legacy_get_exercise(self):
        """Test API legacy pour récupérer un exercice"""
        with patch('course_manager.course_manager.get_course_list') as mock_get_list:
            mock_get_list.return_value = [{"id": "python-basics"}]

            with patch('course_manager.course_manager.get_exercise') as mock_get_exercise:
                mock_exercise = {"id": "ex1", "title": "Print"}
                mock_get_exercise.return_value = mock_exercise

                response = client.get("/api/exercises/ex1")
                assert response.status_code == 200


class TestErrorHandling:
    """Tests pour la gestion des erreurs"""

    def test_internal_server_error_handling(self):
        """Test gestion des erreurs internes du serveur"""
        submission = {
            "course_id": "python-basics",
            "code": "print('test')",
            "learner": "TestUser"
        }

        with patch('security.SecurityValidator.analyze_code_security') as mock_security:
            mock_security.return_value = {'safe': True, 'issues': [], 'risk_level': 'low'}

            # Simuler une erreur inattendue
            with patch('main.quick_syntax_check') as mock_grader:
                mock_grader.side_effect = Exception("Unexpected error")

                response = client.post("/api/run", json=submission)
                assert response.status_code == 500

                data = response.json()
                assert "Internal server error" in data["detail"]["error"]

    def test_logging_on_errors(self):
        """Test que les erreurs sont bien loggées"""
        submission = {
            "course_id": "python-basics",
            "code": "print('test')",
            "learner": "TestUser"
        }

        with patch('main.logger') as mock_logger:
            with patch('security.SecurityValidator.analyze_code_security') as mock_security:
                mock_security.return_value = {'safe': True, 'issues': [], 'risk_level': 'low'}

                with patch('main.quick_syntax_check') as mock_grader:
                    mock_grader.side_effect = Exception("Test error")

                    client.post("/api/run", json=submission)

                    # Vérifier que l'erreur a été loggée
                    mock_logger.error.assert_called()


class TestConfiguration:
    """Tests pour la configuration"""

    def test_executor_url_fallback(self):
        """Test configuration de l'URL de l'executor avec fallback"""
        with patch.dict(os.environ, {}, clear=True):
            # Recharger l'application pour tester la configuration
            from main import EXECUTOR
            assert EXECUTOR == "http://piston:2000/api/v2/execute"

    def test_secure_executor_disabled(self):
        """Test désactivation de l'exécuteur sécurisé"""
        with patch.dict(os.environ, {'USE_SECURE_EXECUTOR': 'false'}):
            # Recharger l'application
            import importlib
            import main
            importlib.reload(main)

            assert main.USE_SECURE_EXECUTOR is False