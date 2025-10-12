"""
Tests de sécurité pour Capitaine Python
Ces tests valident que les mesures de sécurité fonctionnent correctement
"""

import pytest
import asyncio
from fastapi.testclient import TestClient
from .main import app
from .security import SecurityValidator
from .secure_grader import SecureCodeExecutor

client = TestClient(app)

class TestSecurityValidator:
    """Tests pour la classe SecurityValidator"""

    def test_validate_course_id_valid(self):
        """Test validation d'ID de cours valides"""
        valid_ids = ["python-basics", "advanced-python", "web_development", "data-science-101"]
        for course_id in valid_ids:
            result = SecurityValidator.validate_course_id(course_id)
            assert result == course_id.lower()

    def test_validate_course_id_invalid(self):
        """Test validation d'ID de cours invalides"""
        invalid_ids = [
            "python basics",  # espace
            "python@basics",  # caractère spécial
            "python/basics",  # slash
            "python..basics",  # double point
            "python*basics",  # astérisque
            "a" * 51,  # trop long
            "python<script>",  # injection
        ]
        for course_id in invalid_ids:
            with pytest.raises(ValueError):
                SecurityValidator.validate_course_id(course_id)

    def test_validate_exercise_id_valid(self):
        """Test validation d'ID d'exercice valides"""
        valid_ids = ["hello-world", "variables-101", "functions_test", "advanced_exercise"]
        for exercise_id in valid_ids:
            result = SecurityValidator.validate_exercise_id(exercise_id)
            assert result == exercise_id.lower()

    def test_validate_exercise_id_invalid(self):
        """Test validation d'ID d'exercice invalides"""
        invalid_ids = [
            "hello world",  # espace
            "hello@world",  # caractère spécial
            "../etc/passwd",  # path traversal
            "a" * 51,  # trop long
        ]
        for exercise_id in invalid_ids:
            with pytest.raises(ValueError):
                SecurityValidator.validate_exercise_id(exercise_id)

    def test_validate_learner_name_valid(self):
        """Test validation de noms d'apprenants valides"""
        valid_names = ["Hugo", "Alice", "bob_smith", "Student-123", "Jean Dupont"]
        for name in valid_names:
            result = SecurityValidator.validate_learner_name(name)
            assert isinstance(result, str)
            assert len(result) <= 50

    def test_validate_learner_name_invalid(self):
        """Test validation de noms d'apprenants invalides"""
        invalid_names = [
            "<script>alert('xss')</script>",  # XSS
            "Robert'); DROP TABLE users;--",  # SQL injection
            "a" * 100,  # trop long
            {"name": "object"},  # pas une string
            None,
        ]
        for name in invalid_names:
            with pytest.raises(ValueError):
                SecurityValidator.validate_learner_name(name)

    def test_analyze_code_security_safe_code(self):
        """Test analyse de code sécurisé"""
        safe_codes = [
            "print('Hello, World!')",
            "x = 5\ny = 10\nprint(x + y)",
            "def add(a, b):\n    return a + b\nprint(add(2, 3))",
            "for i in range(5):\n    print(i)",
        ]

        for code in safe_codes:
            result = SecurityValidator.analyze_code_security(code)
            assert result['safe'] is True
            assert len(result['issues']) == 0

    def test_analyze_code_security_dangerous_code(self):
        """Test analyse de code dangereux"""
        dangerous_codes = [
            "import os\nos.system('ls')",
            "eval('print(1)')",
            "exec('print(1)')",
            "__import__('os').system('ls')",
            "open('/etc/passwd', 'r')",
            "subprocess.run(['ls'])",
            "import sys\nsys.exit(0)",
        ]

        for code in dangerous_codes:
            result = SecurityValidator.analyze_code_security(code)
            assert result['safe'] is False
            assert len(result['issues']) > 0
            assert result['risk_level'] in ['medium', 'high']

    def test_analyze_code_code_length_limit(self):
        """Test limite de longueur de code"""
        long_code = "print('x')\n" * 1000  # Dépasse la limite
        with pytest.raises(ValueError, match="Code too long"):
            SecurityValidator.analyze_code_security(long_code)

    def test_sanitize_string(self):
        """Test sanitization de chaînes"""
        test_cases = [
            ("<script>alert('xss')</script>", "&lt;script&gt;alert(&#x27;xss&#x27;)&lt;/script&gt;"),
            ("Hello\nWorld", "Hello World"),
            ("Hello\tWorld", "Hello\tWorld"),
            ("Hello\x00World", "HelloWorld"),
        ]

        for input_str, expected in test_cases:
            result = SecurityValidator.sanitize_string(input_str)
            assert result == expected

    def test_sanitize_error_message(self):
        """Test sanitization des messages d'erreur"""
        error_messages = [
            "File not found: /home/user/data.txt",
            "Connection failed to 192.168.1.1:8080",
            "Error at /app/main.py: line 42",
        ]

        for msg in error_messages:
            sanitized = SecurityValidator.sanitize_error_message(msg)
            assert "/home/user" not in sanitized
            assert "192.168.1.1" not in sanitized
            assert "/app/main.py" not in sanitized
            assert "[PATH]" in sanitized or "[IP]" in sanitized


class TestSecureCodeExecutor:
    """Tests pour la classe SecureCodeExecutor"""

    @pytest.fixture
    def executor(self):
        return SecureCodeExecutor(max_execution_time=5, max_memory=64*1024*1024)

    def test_execute_safe_code(self, executor):
        """Test exécution de code sécurisé"""
        safe_code = """
print('Hello, World!')
result = 2 + 3
print(f'Result: {result}')
"""

        async def test():
            result = await executor.execute_code_safely(safe_code)
            assert result['ok'] is True
            assert 'Hello, World!' in result['stdout']
            assert 'Result: 5' in result['stdout']

        asyncio.run(test())

    def test_execute_dangerous_code(self, executor):
        """Test rejet de code dangereux"""
        dangerous_code = "import os; os.system('ls')"

        async def test():
            result = await executor.execute_code_safely(dangerous_code)
            assert result['ok'] is False
            assert 'Security violation' in result['error']
            assert len(result['security_issues']) > 0

        asyncio.run(test())

    def test_execute_with_test_code(self, executor):
        """Test exécution avec code de test"""
        student_code = """
def add(a, b):
    return a + b
"""
        test_code = """
result = add(2, 3)
assert result == 5
print('__ALL_TESTS_OK__')
"""

        async def test():
            result = await executor.execute_code_safely(student_code, test_code)
            assert result['ok'] is True
            assert result['success_indicators']['tests_ok'] is True

        asyncio.run(test())

    def test_execution_timeout(self, executor):
        """Test timeout d'exécution"""
        slow_code = """
import time
time.sleep(10)  # Plus long que le timeout
print('Done')
"""

        async def test():
            result = await executor.execute_code_safely(slow_code)
            assert result['ok'] is False
            assert 'timed out' in result['error'].lower()

        asyncio.run(test())


class TestAPISecurity:
    """Tests de sécurité pour les endpoints API"""

    def test_run_endpoint_safe_code(self):
        """Test endpoint /api/run avec code sécurisé"""
        safe_submission = {
            "course_id": "python-basics",
            "exercise_id": "hello-world",
            "code": "print('Hello, World!')",
            "learner": "TestUser"
        }

        response = client.post("/api/run", json=safe_submission)
        assert response.status_code == 200
        result = response.json()
        # Le résultat peut varier selon la configuration
        assert 'stdout' in result or 'error' in result

    def test_run_endpoint_dangerous_code(self):
        """Test endpoint /api/run avec code dangereux"""
        dangerous_submission = {
            "course_id": "python-basics",
            "exercise_id": "malicious",
            "code": "import os; os.system('ls')",
            "learner": "TestUser"
        }

        response = client.post("/api/run", json=dangerous_submission)
        assert response.status_code == 400
        result = response.json()
        assert 'security' in result['detail']['error'].lower()
        assert 'issues' in result['detail']

    def test_submission_validation_invalid_data(self):
        """Test validation des données de soumission"""
        invalid_submissions = [
            # course_id invalide
            {
                "course_id": "python<script>",
                "code": "print('test')",
                "learner": "TestUser"
            },
            # code vide
            {
                "course_id": "python-basics",
                "code": "",
                "learner": "TestUser"
            },
            # learner invalide
            {
                "course_id": "python-basics",
                "code": "print('test')",
                "learner": "<script>alert('xss')</script>"
            },
        ]

        for submission in invalid_submissions:
            response = client.post("/api/run", json=submission)
            assert response.status_code == 422  # Validation error

    def test_health_endpoint(self):
        """Test endpoint de santé"""
        response = client.get("/api/health")
        assert response.status_code == 200
        data = response.json()
        assert data['status'] == 'healthy'
        assert 'security' in data
        assert 'version' in data

    def test_security_info_endpoint(self):
        """Test endpoint d'informations de sécurité"""
        response = client.get("/api/security/info")
        assert response.status_code == 200
        data = response.json()
        assert 'security_features' in data
        assert 'blocked_patterns' in data
        assert 'blocked_modules' in data
        assert len(data['security_features']) > 0

    def test_cors_headers(self):
        """Test en-têtes CORS"""
        response = client.options("/api/health")
        # Vérifier que les en-têtes CORS sont présents
        assert 'access-control-allow-origin' in response.headers
        assert 'access-control-allow-methods' in response.headers


class TestInputValidation:
    """Tests pour la validation des entrées"""

    def test_sql_injection_attempts(self):
        """Test tentatives d'injection SQL"""
        sql_injection_attempts = [
            "'; DROP TABLE users; --",
            "Robert'); DROP TABLE users; --",
            "' OR '1'='1",
            "'; INSERT INTO users VALUES ('hacker', 'pass'); --"
        ]

        for injection in sql_injection_attempts:
            # Test dans course_id
            submission = {
                "course_id": injection,
                "code": "print('test')",
                "learner": "TestUser"
            }
            response = client.post("/api/run", json=submission)
            assert response.status_code in [400, 422]  # Sécurité ou validation

            # Test dans learner
            submission["learner"] = injection
            submission["course_id"] = "python-basics"
            response = client.post("/api/run", json=submission)
            assert response.status_code in [400, 422]

    def test_xss_attempts(self):
        """Test tentatives XSS"""
        xss_attempts = [
            "<script>alert('xss')</script>",
            "<img src=x onerror=alert('xss')>",
            "javascript:alert('xss')",
            "<iframe src=javascript:alert('xss')></iframe>"
        ]

        for xss in xss_attempts:
            submission = {
                "course_id": "python-basics",
                "code": "print('test')",
                "learner": xss
            }
            response = client.post("/api/run", json=submission)
            # Soit rejeté par validation, soit sanitisé
            assert response.status_code in [200, 400, 422]

            if response.status_code == 200:
                # Si accepté, vérifier que la réponse ne contient pas le XSS
                response_text = response.text.lower()
                assert '<script>' not in response_text
                assert 'javascript:' not in response_text


def test_integration_security_workflow():
    """Test d'intégration complet du workflow de sécurité"""
    # 1. Code sécurisé complet
    safe_workflow = {
        "course_id": "python-basics",
        "exercise_id": "hello-world",
        "code": "def hello(name):\n    return f'Hello, {name}!'\nprint(hello('World'))",
        "learner": "TestStudent"
    }

    # Test run
    response = client.post("/api/run", json=safe_workflow)
    assert response.status_code == 200

    # 2. Tenter code dangereux
    dangerous_workflow = {
        "course_id": "python-basics",
        "exercise_id": "malicious",
        "code": "import sys; print(sys.modules.keys())",
        "learner": "TestStudent"
    }

    response = client.post("/api/run", json=dangerous_workflow)
    assert response.status_code == 400
    assert 'security' in response.json()['detail']['error'].lower()


class TestAdvancedSecurityFeatures:
    """Tests pour les fonctionnalités de sécurité avancées"""

    def test_validate_file_upload_safe(self):
        """Test validation de fichier upload sécurisé"""
        import tempfile
        import os

        # Créer un fichier JSON temporaire
        safe_json_content = b'{"meta": {"id": "test"}, "exercises": []}'

        result = SecurityValidator.validate_file_upload(
            "test.json",
            safe_json_content
        )

        assert result['safe'] is True
        assert result['content_type'] == 'json'
        assert result['size'] == len(safe_json_content)

    def test_validate_file_upload_dangerous(self):
        """Test rejet de fichiers dangereux"""
        dangerous_files = [
            ("../../../etc/passwd", b"content"),  # Directory traversal
            ("malicious.exe", b"fake content"),  # Exécutable
            ("script.php", b"<?php echo 'hack'; ?>"),  # Script web
            ("huge.json", b"x" * 6*1024*1024),  # Trop gros
        ]

        for filename, content in dangerous_files:
            with pytest.raises(ValueError):
                SecurityValidator.validate_file_upload(filename, content)

    def test_validate_url_domain_allowed(self):
        """Test validation de domaines autorisés"""
        allowed_urls = [
            "https://github.com/user/course",
            "https://raw.githubusercontent.com/user/main/course.json",
            "https://gitlab.com/user/project",
            "http://localhost:3000/course.json",
        ]

        for url in allowed_urls:
            assert SecurityValidator.validate_url_domain(url) is True

    def test_validate_url_domain_blocked(self):
        """Test rejet de domaines bloqués"""
        blocked_urls = [
            "https://evil-site.com/malware.json",
            "https://phishing.net/course.json",
            "ftp://not-secure.com/data.json",
            "not-a-url",
        ]

        for url in blocked_urls:
            assert SecurityValidator.validate_url_domain(url) is False

    def test_detect_obfuscation_attempts(self):
        """Test détection d'obfuscation"""
        obfuscated_codes = [
            r"print('hello')\x68\x65\x6c\x6c\x6f",  # Hex escapes
            "e__v__a__l__('print(1)')",  # Eval obfuscation
        ]

        for code in obfuscated_codes:
            issues = SecurityValidator.detect_obfuscation_attempts(code)
            assert len(issues) > 0

    def test_security_validation_endpoint(self):
        """Test endpoint de validation de sécurité"""
        # Code sécurisé
        safe_request = {"code": "print('Hello, World!')"}
        response = client.post("/api/security/validate", json=safe_request)
        assert response.status_code == 200
        data = response.json()
        assert data['safe'] is True
        assert data['risk_level'] == 'low'

        # Code dangereux
        dangerous_request = {"code": "import os; os.system('ls')"}
        response = client.post("/api/security/validate", json=dangerous_request)
        assert response.status_code == 200
        data = response.json()
        assert data['safe'] is False
        assert data['risk_level'] in ['medium', 'high']
        assert len(data['issues']) > 0

    def test_enhanced_error_sanitization(self):
        """Test sanitization améliorée des erreurs"""
        error_messages = [
            "File /home/user/secrets.json not found",
            "Connection to 192.168.1.100:3306 failed",
            "Error in /app/database.py with key abc123def4567890abcdef1234567890ab",
            "Syntax error in script.py: line 42",
        ]

        for msg in error_messages:
            sanitized = SecurityValidator.sanitize_error_message(msg)
            # Vérifier que les informations sensibles sont masquées
            assert "/home/user" not in sanitized
            assert "192.168.1.100" not in sanitized
            assert "abc123def456" not in sanitized
            assert any(marker in sanitized for marker in ['[PATH]', '[IP]', '[FILE]', '[TOKEN]'])

    def test_security_info_endpoint_enhanced(self):
        """Test endpoint d'informations de sécurité enrichi"""
        response = client.get("/api/security/info")
        assert response.status_code == 200
        data = response.json()

        # Vérifier les nouvelles fonctionnalités
        assert 'obfuscation detection' in data['security_features']
        assert 'file upload security validation' in data['security_features']
        assert 'url domain validation' in data['security_features']
        assert 'max_file_size' in data
        assert 'allowed_file_types' in data
        assert 'allowed_domains' in data
        assert len(data['allowed_domains']) > 0


if __name__ == "__main__":
    # Exécuter les tests
    pytest.main([__file__, "-v", "--tb=short"])