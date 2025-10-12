"""
Tests End-to-End (E2E) pour l'interface utilisateur de Capitaine Python
Ces tests valident le workflow complet de l'utilisateur depuis le navigateur
"""

import pytest
import asyncio
import json
import time
from fastapi.testclient import TestClient
from .main import app
from .course_manager import course_manager

client = TestClient(app)


class TestE2EUserWorkflow:
    """Tests E2E pour le workflow utilisateur complet"""

    def test_complete_learning_workflow(self):
        """Test le workflow complet d'apprentissage"""

        # 1. Accès à la page d'accueil
        response = client.get("/")
        assert response.status_code == 200

        # 2. Récupération de la liste des cours
        courses_response = client.get("/api/courses")
        assert courses_response.status_code == 200
        courses = courses_response.json()
        assert len(courses) > 0

        # Sélectionner le premier cours
        first_course = courses[0]
        course_id = first_course["id"]

        # 3. Sélection du cours
        select_response = client.post(f"/api/courses/{course_id}/select")
        assert select_response.status_code == 200
        select_data = select_response.json()
        assert select_data["current_course"] == course_id

        # 4. Récupération des exercices du cours
        exercises_response = client.get(f"/api/courses/{course_id}/exercises")
        assert exercises_response.status_code == 200
        exercises = exercises_response.json()
        assert len(exercises) > 0

        # Sélectionner le premier exercice
        first_exercise = exercises[0]
        exercise_id = first_exercise["id"]

        # 5. Récupération des détails de l'exercice
        exercise_response = client.get(f"/api/courses/{course_id}/exercises/{exercise_id}")
        assert exercise_response.status_code == 200
        exercise_data = exercise_response.json()

        # Vérifier la structure de l'exercice
        assert "id" in exercise_data
        assert "title" in exercise_data
        assert "prompt" in exercise_data
        assert "starter" in exercise_data
        assert "tests" in exercise_data

        # 6. Soumission de code (test d'exécution simple)
        safe_submission = {
            "course_id": course_id,
            "exercise_id": exercise_id,
            "code": "print('Hello, World!')",
            "learner": "TestStudent"
        }

        run_response = client.post("/api/run", json=safe_submission)
        assert run_response.status_code == 200
        run_result = run_response.json()
        assert "stdout" in run_result or "error" in run_result

        # 7. Soumission pour validation (si pas de code dangereux)
        if "Hello" in str(run_result):
            grade_response = client.post("/api/grade", json=safe_submission)
            assert grade_response.status_code == 200
            grade_result = grade_response.json()
            assert "result" in grade_result
            assert "progress" in grade_result

    def test_course_import_workflow(self):
        """Test le workflow d'import de cours"""

        # Créer un cours de test
        test_course = {
            "meta": {
                "id": "test-e2e-course",
                "title": {"fr": "Cours Test E2E"},
                "description": {"fr": "Cours créé pour les tests E2E"},
                "level": "Beginner",
                "estimated_hours": 5
            },
            "theme": {
                "name": "test",
                "primary_color": "#0077be",
                "background_color": "#0a1929"
            },
            "exercises": [
                {
                    "id": "test-ex-1",
                    "title": {"fr": "Exercice Test"},
                    "stars": 1,
                    "prompt": {"fr": "Écris un code qui affiche 'Test'"},
                    "starter": {"fr": "# Écris ton code ici"},
                    "tests": [
                        "print('Test')"
                    ],
                    "hints": ["Utilise print()"]
                }
            ]
        }

        # Simulation d'import via l'API (bypass validation pour les tests)
        course_manager.courses["test-e2e-course"] = test_course

        # Vérifier que le cours est disponible
        courses_response = client.get("/api/courses")
        courses = courses_response.json()
        course_ids = [course["id"] for course in courses]
        assert "test-e2e-course" in course_ids

        # Sélectionner le cours importé
        select_response = client.post("/api/courses/test-e2e-course/select")
        assert select_response.status_code == 200

        # Vérifier les exercices
        exercises_response = client.get("/api/courses/test-e2e-course/exercises")
        assert exercises_response.status_code == 200
        exercises = exercises_response.json()
        assert len(exercises) == 1
        assert exercises[0]["id"] == "test-ex-1"

        # Nettoyer
        if "test-e2e-course" in course_manager.courses:
            del course_manager.courses["test-e2e-course"]

    def test_error_handling_workflow(self):
        """Test la gestion des erreurs dans le workflow utilisateur"""

        # 1. Essayer d'accéder à un cours inexistant
        response = client.get("/api/courses/nonexistent-course")
        assert response.status_code == 404

        # 2. Essayer de sélectionner un cours inexistant
        response = client.post("/api/courses/nonexistent-course/select")
        assert response.status_code == 404

        # 3. Essayer d'accéder aux exercices d'un cours inexistant
        response = client.get("/api/courses/nonexistent-course/exercises")
        assert response.status_code == 404

        # 4. Soumettre du code avec des données invalides
        invalid_submissions = [
            # Code vide
            {
                "course_id": "python-basics",
                "exercise_id": "hello-world",
                "code": "",
                "learner": "TestStudent"
            },
            # Course ID invalide
            {
                "course_id": "invalid@course",
                "code": "print('test')",
                "learner": "TestStudent"
            },
            # Learner invalide
            {
                "course_id": "python-basics",
                "code": "print('test')",
                "learner": "<script>alert('xss')</script>"
            }
        ]

        for submission in invalid_submissions:
            response = client.post("/api/run", json=submission)
            assert response.status_code in [400, 422]  # Bad Request ou Validation Error

    def test_security_robustness(self):
        """Test la robustesse face à des tentatives d'attaque"""

        # Codes malveillants qui devraient être bloqués
        malicious_codes = [
            "import os; os.system('ls')",
            "__import__('subprocess').run(['ls'])",
            "eval('__import__(\"os\").system(\"ls\")')",
            "exec('import os; os.system(\"ls\")')",
            "open('/etc/passwd', 'r').read()",
        ]

        for malicious_code in malicious_codes:
            submission = {
                "course_id": "python-basics",
                "exercise_id": "test-security",
                "code": malicious_code,
                "learner": "SecurityTest"
            }

            response = client.post("/api/run", json=submission)
            # Devrait être bloqué par la sécurité
            assert response.status_code == 400
            result = response.json()
            assert "security" in result.get("detail", {}).get("error", "").lower()

    def test_performance_limits(self):
        """Test les limites de performance et ressources"""

        # Code très long (devrait être rejeté)
        long_code = "print('x')\n" * 2000  # Environ 12000 caractères

        submission = {
            "course_id": "python-basics",
            "exercise_id": "test-performance",
            "code": long_code,
            "learner": "PerformanceTest"
        }

        response = client.post("/api/run", json=submission)
        assert response.status_code == 400
        result = response.json()
        assert "too long" in str(result).lower()

    def test_concurrent_requests(self):
        """Test la gestion des requêtes concurrentes"""
        import threading
        import queue

        results = queue.Queue()

        def make_request(request_id):
            try:
                response = client.get("/api/courses")
                results.put((request_id, response.status_code))
            except Exception as e:
                results.put((request_id, str(e)))

        # Lancer 10 requêtes concurrentes
        threads = []
        for i in range(10):
            thread = threading.Thread(target=make_request, args=(i,))
            threads.append(thread)
            thread.start()

        # Attendre que toutes les requêtes se terminent
        for thread in threads:
            thread.join()

        # Vérifier que toutes les requêtes ont réussi
        success_count = 0
        while not results.empty():
            request_id, status = results.get()
            if status == 200:
                success_count += 1

        assert success_count >= 8  # Au moins 80% de succès

    def test_data_consistency(self):
        """Test la cohérence des données entre les endpoints"""

        # Récupérer les cours
        courses_response = client.get("/api/courses")
        courses = courses_response.json()

        if courses:
            first_course = courses[0]
            course_id = first_course["id"]

            # Vérifier la cohérence entre les différents endpoints
            # 1. get_course vs get_course_list
            course_detail_response = client.get(f"/api/courses/{course_id}")
            course_detail = course_detail_response.json()

            assert course_detail["meta"]["id"] == first_course["id"]
            assert course_detail["meta"]["title"] == first_course["title"]

            # 2. get_course_exercises vs get_exercise
            exercises_response = client.get(f"/api/courses/{course_id}/exercises")
            exercises = exercises_response.json()

            if exercises:
                first_exercise = exercises[0]
                exercise_id = first_exercise["id"]

                exercise_detail_response = client.get(f"/api/courses/{course_id}/exercises/{exercise_id}")
                exercise_detail = exercise_detail_response.json()

                assert exercise_detail["id"] == first_exercise["id"]
                assert exercise_detail["title"] == first_exercise["title"]


class TestE2EIntegrationScenarios:
    """Tests d'intégration pour des scénarios réels"""

    def test_new_user_journey(self):
        """Test le parcours d'un nouvel utilisateur"""

        # 1. Nouvel utilisateur arrive sur la plateforme
        health_response = client.get("/api/health")
        assert health_response.status_code == 200
        health_data = health_response.json()
        assert health_data["status"] == "healthy"

        # 2. Découvre les cours disponibles
        courses_response = client.get("/api/courses")
        assert courses_response.status_code == 200
        courses = courses_response.json()
        assert len(courses) > 0

        # 3. Choisit le cours le plus simple
        beginner_courses = [c for c in courses if c.get("level") == "Beginner"]
        target_course = beginner_courses[0] if beginner_courses else courses[0]

        # 4. Sélectionne le cours
        select_response = client.post(f"/api/courses/{target_course['id']}/select")
        assert select_response.status_code == 200

        # 5. Explore les exercices
        exercises_response = client.get(f"/api/courses/{target_course['id']}/exercises")
        exercises = exercises_response.json()

        # 6. Commence par l'exercice le plus simple
        if exercises:
            easiest_exercise = min(exercises, key=lambda x: x.get("stars", 0))

            # 7. Essaye de résoudre l'exercice
            exercise_detail_response = client.get(
                f"/api/courses/{target_course['id']}/exercises/{easiest_exercise['id']}"
            )
            exercise_detail = exercise_detail_response.json()

            # 8. Soumet une solution simple
            submission = {
                "course_id": target_course["id"],
                "exercise_id": easiest_exercise["id"],
                "code": "print('Solution de test')",
                "learner": "NewUser"
            }

            run_response = client.post("/api/run", json=submission)
            assert run_response.status_code == 200

    def test_experienced_user_journey(self):
        """Test le parcours d'un utilisateur expérimenté"""

        # 1. Utilisateur expérimenté cherche des cours avancés
        courses_response = client.get("/api/courses")
        courses = courses_response.json()

        # 2. Filtre les cours par difficulté
        advanced_courses = [c for c in courses if "Advanced" in c.get("level", "")]

        if advanced_courses:
            target_course = advanced_courses[0]

            # 3. S'entraîne sur plusieurs exercices
            exercises_response = client.get(f"/api/courses/{target_course['id']}/exercises")
            exercises = exercises_response.json()

            # 4. Résout plusieurs exercices rapidement
            solved_count = 0
            for exercise in exercises[:3]:  # 3 premiers exercices
                submission = {
                    "course_id": target_course["id"],
                    "exercise_id": exercise["id"],
                    "code": f"# Solution pour {exercise['id']}\nprint('Test')",
                    "learner": "ExperiencedUser"
                }

                run_response = client.post("/api/run", json=submission)
                if run_response.status_code == 200:
                    solved_count += 1

            assert solved_count >= 2  # Au moins 2 exercices résolus

    def test_error_recovery(self):
        """Test la récupération après des erreurs"""

        # 1. Soumettre du code qui cause une erreur
        error_submission = {
            "course_id": "python-basics",
            "exercise_id": "hello-world",
            "code": "print(nonexistent_variable)",
            "learner": "ErrorTestUser"
        }

        response = client.post("/api/run", json=error_submission)
        assert response.status_code == 200  # Le code s'exécute mais produit une erreur

        # 2. Soumettre du code correct après l'erreur
        correct_submission = {
            "course_id": "python-basics",
            "exercise_id": "hello-world",
            "code": "print('Hello, World!')",
            "learner": "ErrorTestUser"
        }

        response = client.post("/api/run", json=correct_submission)
        assert response.status_code == 200

        # 3. Vérifier que la progression est enregistrée correctement
        progress_response = client.get("/api/progress?learner=ErrorTestUser")
        assert progress_response.status_code == 200


@pytest.mark.slow
class TestE2ELoadTesting:
    """Tests de charge E2E"""

    def test_multiple_users_simulation(self):
        """Simule plusieurs utilisateurs utilisant la plateforme simultanément"""
        import threading
        import queue
        import time

        results = queue.Queue()
        user_count = 5

        def simulate_user(user_id):
            try:
                start_time = time.time()

                # Chaque utilisateur suit le workflow complet
                courses_response = client.get("/api/courses")
                courses = courses_response.json()

                if courses:
                    course = courses[0]
                    exercises_response = client.get(f"/api/courses/{course['id']}/exercises")
                    exercises = exercises_response.json()

                    if exercises:
                        exercise = exercises[0]
                        submission = {
                            "course_id": course["id"],
                            "exercise_id": exercise["id"],
                            "code": f"print('User {user_id} solution')",
                            "learner": f"User{user_id}"
                        }

                        run_response = client.post("/api/run", json=submission)

                end_time = time.time()
                results.put((user_id, end_time - start_time, "success"))

            except Exception as e:
                results.put((user_id, 0, str(e)))

        # Lancer tous les utilisateurs en parallèle
        threads = []
        for i in range(user_count):
            thread = threading.Thread(target=simulate_user, args=(i,))
            threads.append(thread)
            thread.start()

        # Attendre que tous les threads se terminent
        for thread in threads:
            thread.join()

        # Analyser les résultats
        success_count = 0
        total_time = 0

        while not results.empty():
            user_id, duration, status = results.get()
            if status == "success":
                success_count += 1
                total_time += duration

        # Au moins 80% de succès
        assert success_count >= user_count * 0.8

        # Temps moyen raisonnable (< 2 secondes)
        if success_count > 0:
            avg_time = total_time / success_count
            assert avg_time < 2.0


if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])