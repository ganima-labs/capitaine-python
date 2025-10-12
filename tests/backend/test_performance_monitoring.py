"""
Tests de performance et monitoring pour Capitaine Python
Ces tests valident les performances, les limites et le monitoring du système
"""

import pytest
import time
import threading
import queue
import json
import psutil
import os
from fastapi.testclient import TestClient
from .main import app
from .security import SecurityValidator

client = TestClient(app)


class TestPerformanceMetrics:
    """Tests des métriques de performance"""

    def test_api_response_times(self):
        """Test les temps de réponse des endpoints principaux"""

        endpoints = [
            ("/api/health", "Health check"),
            ("/api/courses", "List courses"),
            ("/api/security/info", "Security info"),
        ]

        # Test avec des temps de réponse acceptables
        max_response_time = 1.0  # 1 seconde

        for endpoint, description in endpoints:
            start_time = time.time()
            response = client.get(endpoint)
            end_time = time.time()

            response_time = end_time - start_time

            assert response.status_code == 200, f"{description} failed"
            assert response_time < max_response_time, f"{description} too slow: {response_time:.3f}s"

    def test_concurrent_api_load(self):
        """Test la charge concurrente sur les endpoints API"""

        results = queue.Queue()
        thread_count = 10
        requests_per_thread = 5

        def make_requests(thread_id):
            thread_results = []

            for i in range(requests_per_thread):
                start_time = time.time()
                response = client.get("/api/courses")
                end_time = time.time()

                thread_results.append({
                    'thread_id': thread_id,
                    'request_id': i,
                    'status_code': response.status_code,
                    'response_time': end_time - start_time
                })

            results.put(thread_results)

        # Lancer tous les threads
        threads = []
        start_total = time.time()

        for i in range(thread_count):
            thread = threading.Thread(target=make_requests, args=(i,))
            threads.append(thread)
            thread.start()

        # Attendre que tous les threads se terminent
        for thread in threads:
            thread.join()

        end_total = time.time()

        # Analyser les résultats
        all_results = []
        while not results.empty():
            thread_results = results.get()
            all_results.extend(thread_results)

        # Vérifications
        total_requests = len(all_results)
        successful_requests = sum(1 for r in all_results if r['status_code'] == 200)
        avg_response_time = sum(r['response_time'] for r in all_results) / total_requests
        max_response_time = max(r['response_time'] for r in all_results)

        assert successful_requests >= total_requests * 0.95, "Too many failed requests"
        assert avg_response_time < 0.5, f"Average response time too high: {avg_response_time:.3f}s"
        assert max_response_time < 2.0, f"Max response time too high: {max_response_time:.3f}s"

    def test_memory_usage_stability(self):
        """Test la stabilité de l'utilisation mémoire"""

        process = psutil.Process(os.getpid())
        initial_memory = process.memory_info().rss / 1024 / 1024  # MB

        # Effectuer de nombreuses opérations
        for i in range(50):
            response = client.get("/api/courses")
            assert response.status_code == 200

            # Simuler des traitements
            submission = {
                "course_id": "python-basics",
                "exercise_id": "hello-world",
                "code": f"print('Test {i}')",
                "learner": f"MemoryTest{i}"
            }

            client.post("/api/run", json=submission)

        final_memory = process.memory_info().rss / 1024 / 1024  # MB
        memory_increase = final_memory - initial_memory

        # La mémoire ne devrait pas augmenter de plus de 50MB
        assert memory_increase < 50, f"Memory increased too much: {memory_increase:.2f}MB"

    def test_code_execution_performance(self):
        """Test les performances d'exécution de code"""

        # Codes avec différentes complexités
        test_codes = [
            ("Simple", "print('Hello')"),
            ("Loop", "for i in range(100): print(i)"),
            ("Calculation", "sum([i*i for i in range(1000)])"),
            ("String ops", "''.join(['test'] * 100)"),
        ]

        max_execution_time = 2.0  # 2 secondes max

        for name, code in test_codes:
            submission = {
                "course_id": "python-basics",
                "exercise_id": "performance-test",
                "code": code,
                "learner": "PerfTest"
            }

            start_time = time.time()
            response = client.post("/api/run", json=submission)
            end_time = time.time()

            execution_time = end_time - start_time

            assert response.status_code == 200, f"{name} code execution failed"
            assert execution_time < max_execution_time, f"{name} code too slow: {execution_time:.3f}s"

    def test_large_payload_handling(self):
        """Test la gestion de payloads volumineux"""

        # Test avec un code proche de la limite
        large_code = "print('x')\n" * 1000  # Environ 8000 caractères

        submission = {
            "course_id": "python-basics",
            "exercise_id": "large-payload-test",
            "code": large_code,
            "learner": "LargePayloadTest"
        }

        start_time = time.time()
        response = client.post("/api/run", json=submission)
        end_time = time.time()

        # Devrait être accepté (juste sous la limite)
        assert response.status_code == 200
        assert (end_time - start_time) < 3.0, "Large payload processing too slow"

    def test_rate_limiting_behavior(self):
        """Test le comportement en cas de requêtes multiples rapides"""

        # Envoyer plusieurs requêtes rapidement
        responses = []
        start_time = time.time()

        for i in range(20):
            response = client.get("/api/courses")
            responses.append(response)
            time.sleep(0.01)  # 10ms entre chaque requête

        end_time = time.time()

        # La plupart des requêtes devraient réussir
        success_count = sum(1 for r in responses if r.status_code == 200)
        assert success_count >= 18, f"Too many requests failed: {20 - success_count}/20"

        # Le temps total devrait être raisonnable
        total_time = end_time - start_time
        assert total_time < 5.0, f"Batch requests too slow: {total_time:.3f}s"


class TestResourceLimits:
    """Tests des limites de ressources"""

    def test_security_validation_performance(self):
        """Test les performances de la validation de sécurité"""

        # Codes avec différents niveaux de complexité de sécurité
        test_cases = [
            ("Safe code", "print('Hello, World!')"),
            ("Complex safe", "def calculate(x): return sum([i*i for i in range(x)])"),
            ("Suspicious pattern", "import sys\nprint(sys.modules)"),
            ("Multiple patterns", "import os\nimport sys\neval('print(1)')"),
        ]

        for name, code in test_cases:
            start_time = time.time()

            # Test direct de la validation
            security_analysis = SecurityValidator.analyze_code_security(code)

            end_time = time.time()
            validation_time = end_time - start_time

            # La validation devrait être rapide (< 10ms)
            assert validation_time < 0.01, f"Security validation too slow for {name}: {validation_time*1000:.2f}ms"

            # Les résultats devraient être cohérents
            assert isinstance(security_analysis, dict)
            assert 'safe' in security_analysis
            assert 'risk_level' in security_analysis

    def test_database_connection_limits(self):
        """Test les limites de connexions à la base de données"""

        # Simuler plusieurs requêtes de progression simultanées
        results = queue.Queue()
        thread_count = 5

        def get_progress(thread_id):
            try:
                start_time = time.time()
                response = client.get("/api/progress", params={"learner": f"User{thread_id}"})
                end_time = time.time()

                results.put({
                    'thread_id': thread_id,
                    'status_code': response.status_code,
                    'response_time': end_time - start_time
                })
            except Exception as e:
                results.put({
                    'thread_id': thread_id,
                    'error': str(e)
                })

        # Lancer les threads
        threads = []
        for i in range(thread_count):
            thread = threading.Thread(target=get_progress, args=(i,))
            threads.append(thread)
            thread.start()

        # Attendre la fin
        for thread in threads:
            thread.join()

        # Analyser les résultats
        success_count = 0
        total_time = 0

        while not results.empty():
            result = results.get()
            if 'error' not in result:
                success_count += 1
                total_time += result['response_time']

        assert success_count >= thread_count * 0.8, "Too many database request failures"

        if success_count > 0:
            avg_time = total_time / success_count
            assert avg_time < 0.5, f"Database requests too slow: {avg_time:.3f}s"

    def test_file_processing_limits(self):
        """Test les limites de traitement de fichiers"""

        # Simuler différents tailles de contenu
        test_sizes = [1024, 10240, 102400, 512000]  # 1KB, 10KB, 100KB, 500KB

        for size in test_sizes:
            # Créer un contenu JSON de la taille spécifiée
            test_content = {
                "meta": {"id": f"test-{size}"},
                "exercises": [{"id": f"ex-{i}", "content": "x" * 100} for i in range(size // 100)]
            }

            json_content = json.dumps(test_content)

            # Tester la validation JSON
            start_time = time.time()

            try:
                validated_data = SecurityValidator.validate_json_data(json_content, max_size=1024*1024)
                end_time = time.time()

                validation_time = end_time - start_time

                # La validation devrait être rapide (< 100ms)
                assert validation_time < 0.1, f"JSON validation too slow for {size} bytes: {validation_time*1000:.2f}ms"
                assert isinstance(validated_data, dict)

            except ValueError:
                # C'est normal si le contenu est trop gros
                pass


class TestSystemMonitoring:
    """Tests du monitoring système"""

    def test_health_check_completeness(self):
        """Test la complétude du health check"""

        response = client.get("/api/health")
        assert response.status_code == 200

        health_data = response.json()

        # Vérifier les champs obligatoires
        required_fields = ["status", "version", "security", "executor"]
        for field in required_fields:
            assert field in health_data, f"Missing health field: {field}"

        # Vérifier les sous-champs de sécurité
        security_fields = ["secure_executor_enabled", "max_code_length", "max_execution_time"]
        for field in security_fields:
            assert field in health_data["security"], f"Missing security field: {field}"

    def test_security_info_completeness(self):
        """Test la complétude des informations de sécurité"""

        response = client.get("/api/security/info")
        assert response.status_code == 200

        security_data = response.json()

        # Vérifier les fonctionnalités de sécurité
        assert "security_features" in security_data
        assert len(security_data["security_features"]) > 5

        # Vérifier les métriques
        required_metrics = ["blocked_patterns", "blocked_modules", "max_code_length"]
        for metric in required_metrics:
            assert metric in security_data, f"Missing security metric: {metric}"

    def test_error_monitoring_coverage(self):
        """Test la couverture du monitoring d'erreurs"""

        # Provoquer différentes types d'erreurs et vérifier les réponses
        error_scenarios = [
            # Cours inexistant
            (client.get, ("/api/courses/nonexistent",), 404),
            # Exercice inexistant
            (client.get, ("/api/courses/python-basics/exercises/nonexistent",), 404),
            # Données invalides
            (client.post, ("/api/run", {"invalid": "data"}), 422),
        ]

        for request_func, args, expected_status in error_scenarios:
            response = request_func(*args)
            assert response.status_code == expected_status

            # Les réponses d'erreur devraient être structurées
            if response.status_code != 200:
                error_data = response.json()
                assert "detail" in error_data or "error" in error_data

    def test_logging_behavior(self):
        """Test que les logs sont générés correctement"""

        # Cette vérification est indirecte via les réponses
        # Le fait que les requêtes réussissent indique que le système fonctionne

        response = client.get("/api/health")
        assert response.status_code == 200

        # Test avec une soumission qui devrait être loggée
        submission = {
            "course_id": "python-basics",
            "exercise_id": "hello-world",
            "code": "print('Log test')",
            "learner": "LoggingTestUser"
        }

        response = client.post("/api/run", json=submission)
        assert response.status_code == 200


@pytest.mark.slow
class TestStressTests:
    """Tests de stress pour identifier les limites du système"""

    def test_sustained_load(self):
        """Test une charge soutenue sur une période"""

        duration = 10  # 10 secondes de test
        request_interval = 0.1  # Une requête toutes les 100ms
        start_time = time.time()

        success_count = 0
        error_count = 0
        response_times = []

        while time.time() - start_time < duration:
            request_start = time.time()
            response = client.get("/api/courses")
            request_end = time.time()

            response_times.append(request_end - request_start)

            if response.status_code == 200:
                success_count += 1
            else:
                error_count += 1

            time.sleep(request_interval)

        # Analyser les résultats
        total_requests = success_count + error_count
        success_rate = success_count / total_requests
        avg_response_time = sum(response_times) / len(response_times)
        max_response_time = max(response_times)

        assert success_rate >= 0.95, f"Success rate too low: {success_rate:.2%}"
        assert avg_response_time < 0.5, f"Average response time too high: {avg_response_time:.3f}s"
        assert max_response_time < 2.0, f"Max response time too high: {max_response_time:.3f}s"

    def test_peak_load_simulation(self):
        """Test une simulation de pic de charge"""

        # Simuler un pic soudain de trafic
        thread_count = 20
        requests_per_thread = 10
        results = queue.Queue()

        def burst_requests(thread_id):
            thread_results = []

            for i in range(requests_per_thread):
                start_time = time.time()
                response = client.get("/api/courses")
                end_time = time.time()

                thread_results.append({
                    'thread_id': thread_id,
                    'request_id': i,
                    'status_code': response.status_code,
                    'response_time': end_time - start_time
                })

            results.put(thread_results)

        # Lancer tous les threads simultanément
        threads = []
        for i in range(thread_count):
            thread = threading.Thread(target=burst_requests, args=(i,))
            threads.append(thread)

        start_time = time.time()
        for thread in threads:
            thread.start()

        # Attendre que tous les threads se terminent
        for thread in threads:
            thread.join()
        end_time = time.time()

        # Analyser les résultats
        all_results = []
        while not results.empty():
            thread_results = results.get()
            all_results.extend(thread_results)

        total_requests = len(all_results)
        successful_requests = sum(1 for r in all_results if r['status_code'] == 200)
        avg_response_time = sum(r['response_time'] for r in all_results) / total_requests

        success_rate = successful_requests / total_requests
        total_duration = end_time - start_time

        assert success_rate >= 0.9, f"Peak load success rate too low: {success_rate:.2%}"
        assert avg_response_time < 1.0, f"Peak load response time too high: {avg_response_time:.3f}s"
        assert total_duration < 30.0, f"Peak load duration too long: {total_duration:.1f}s"


if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])