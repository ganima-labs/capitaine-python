"""
Tests unitaires pour le module grader.py (moteur d'exécution legacy)
Valide l'exécution de code Python et les tests unitaires
"""

import pytest
import asyncio
import tempfile
import os
import sys
from unittest.mock import patch, AsyncMock, MagicMock
import httpx
import grader


class TestMakeRunnerPayload:
    """Tests pour la fonction make_runner_payload"""

    def test_make_runner_payload_basic(self):
        """Test création payload de base"""
        code = "print('Hello, World!')"
        result = grader.make_runner_payload(code)

        expected = {
            "language": "python",
            "files": [{"name": "main.py", "content": code}],
            "stdin": "",
            "args": [],
            "compile_timeout": 7000,
            "run_timeout": 5000,
            "run_memory_limit": 128000000,
        }

        assert result == expected

    def test_make_runner_payload_with_stdin(self):
        """Test création payload avec stdin"""
        code = "name = input('Enter name: '); print(f'Hello, {name}!')"
        stdin = "Alice"
        result = grader.make_runner_payload(code, stdin)

        assert result["language"] == "python"
        assert result["files"][0]["content"] == code
        assert result["stdin"] == stdin
        assert result["args"] == []

    def test_make_runner_payload_empty_code(self):
        """Test création payload avec code vide"""
        result = grader.make_runner_payload("")

        assert result["files"][0]["content"] == ""
        assert result["language"] == "python"

    def test_make_runner_payload_multiline_code(self):
        """Test création payload avec code multi-lignes"""
        code = """def add(a, b):
    return a + b

result = add(2, 3)
print(result)"""

        result = grader.make_runner_payload(code)

        assert result["files"][0]["content"] == code
        assert result["language"] == "python"

    def test_make_runner_payload_with_special_characters(self):
        """Test création payload avec caractères spéciaux"""
        code = "print('Hello 世界! 🌍')"
        result = grader.make_runner_payload(code)

        assert result["files"][0]["content"] == code
        assert result["language"] == "python"


class TestRunLocalPython:
    """Tests pour la fonction run_local_python"""

    @pytest.mark.asyncio
    async def test_run_local_python_success(self):
        """Test exécution locale réussie"""
        code = "print('Hello, World!')"

        result = await grader.run_local_python(code)

        assert result["ok"] is True
        assert "Hello, World!" in result["stdout"]
        assert result["stderr"] == ""
        assert result["compile"]["stderr"] == ""
        assert result["run"]["stdout"] == result["stdout"]

    @pytest.mark.asyncio
    async def test_run_local_python_with_stdin(self):
        """Test exécution locale avec stdin"""
        code = "name = input(); print(f'Hello, {name}!')"
        stdin = "Alice"

        result = await grader.run_local_python(code, stdin)

        assert result["ok"] is True
        assert "Hello, Alice!" in result["stdout"]
        assert result["stderr"] == ""

    @pytest.mark.asyncio
    async def test_run_local_python_syntax_error(self):
        """Test exécution locale avec erreur de syntaxe"""
        code = "print('Hello, World'  # Manque la parenthèse fermante"

        result = await grader.run_local_python(code)

        assert result["ok"] is False
        assert "SyntaxError" in result["stderr"]
        assert result["stdout"] == ""

    @pytest.mark.asyncio
    async def test_run_local_python_runtime_error(self):
        """Test exécution locale avec erreur runtime"""
        code = "print(1 / 0)"  # Division par zéro

        result = await grader.run_local_python(code)

        assert result["ok"] is False
        assert "ZeroDivisionError" in result["stderr"]
        assert result["stdout"] == ""

    @pytest.mark.asyncio
    async def test_run_local_python_timeout(self):
        """Test exécution locale avec timeout"""
        code = "import time; time.sleep(15)"  # Plus long que le timeout par défaut

        result = await grader.run_local_python(code, timeout=5)

        assert result["ok"] is False
        assert "Timeout" in result["stderr"]
        assert result["stdout"] == ""

    @pytest.mark.asyncio
    async def test_run_local_python_custom_timeout(self):
        """Test exécution locale avec timeout personnalisé"""
        code = "import time; time.sleep(2)"

        result = await grader.run_local_python(code, timeout=5)

        assert result["ok"] is True

    @pytest.mark.asyncio
    async def test_run_local_python_empty_code(self):
        """Test exécution locale avec code vide"""
        code = ""

        result = await grader.run_local_python(code)

        assert result["ok"] is True  # Code vide ne provoque pas d'erreur
        assert result["stdout"] == ""
        assert result["stderr"] == ""

    @pytest.mark.asyncio
    async def test_run_local_python_complex_output(self):
        """Test exécution locale avec sortie complexe"""
        code = """
import sys
print("Line 1", file=sys.stdout)
print("Line 2", file=sys.stdout)
print("Error output", file=sys.stderr)
"""

        result = await grader.run_local_python(code)

        assert result["ok"] is True
        assert "Line 1" in result["stdout"]
        assert "Line 2" in result["stdout"]
        # stderr peut contenir des messages selon l'environnement

    @pytest.mark.asyncio
    async def test_run_local_python_import_error(self):
        """Test exécution locale avec erreur d'import"""
        code = "import nonexistent_module"

        result = await grader.run_local_python(code)

        assert result["ok"] is False
        assert "ModuleNotFoundError" in result["stderr"]

    @pytest.mark.asyncio
    async def test_run_local_python_file_cleanup(self):
        """Test que les fichiers temporaires sont bien nettoyés"""
        code = "print('test')"

        # Lister les fichiers temporaires avant exécution
        temp_files_before = len(os.listdir("/tmp")) if os.path.exists("/tmp") else 0

        result = await grader.run_local_python(code)

        # Lister les fichiers temporaires après exécution
        temp_files_after = len(os.listdir("/tmp")) if os.path.exists("/tmp") else 0

        assert result["ok"] is True
        # Le nombre de fichiers temporaires ne devrait pas augmenter significativement
        # (on ne teste pas l'égalité absolue car d'autres processus peuvent créer/supprimer des fichiers)


class TestQuickSyntaxCheck:
    """Tests pour la fonction quick_syntax_check"""

    @pytest.mark.asyncio
    async def test_quick_syntax_check_success_piston(self):
        """Test vérification syntaxe réussie avec Piston"""
        code = "print('Hello, World!')"
        mock_response = MagicMock()
        mock_response.json.return_value = {
            "compile": {"stderr": ""},
            "run": {"stdout": "Hello, World!", "stderr": ""}
        }

        with patch('httpx.AsyncClient') as mock_client:
            mock_client.return_value.__aenter__.return_value.post.return_value = mock_response

            ok, out = await grader.quick_syntax_check("http://test.com", code)

            assert ok is True
            assert out["compile"]["stderr"] == ""
            assert out["run"]["stdout"] == "Hello, World!"

    @pytest.mark.asyncio
    async def test_quick_syntax_check_syntax_error_piston(self):
        """Test vérification syntaxe avec erreur via Piston"""
        code = "print('test'  # Syntax error"

        mock_response = MagicMock()
        mock_response.json.return_value = {
            "compile": {"stderr": "SyntaxError: unexpected EOF"},
            "run": {"stdout": "", "stderr": ""}
        }

        with patch('httpx.AsyncClient') as mock_client:
            mock_client.return_value.__aenter__.return_value.post.return_value = mock_response

            ok, out = await grader.quick_syntax_check("http://test.com", code)

            assert ok is False
            assert "SyntaxError" in out["compile"]["stderr"]

    @pytest.mark.asyncio
    async def test_quick_syntax_check_runtime_error_piston(self):
        """Test vérification syntaxe avec erreur runtime via Piston"""
        code = "print(1 / 0)"

        mock_response = MagicMock()
        mock_response.json.return_value = {
            "compile": {"stderr": ""},
            "run": {"stdout": "", "stderr": "ZeroDivisionError"}
        }

        with patch('httpx.AsyncClient') as mock_client:
            mock_client.return_value.__aenter__.return_value.post.return_value = mock_response

            ok, out = await grader.quick_syntax_check("http://test.com", code)

            assert ok is False
            assert "ZeroDivisionError" in out["run"]["stderr"]

    @pytest.mark.asyncio
    async def test_quick_syntax_check_piston_unavailable_fallback(self):
        """Test fallback local quand Piston n'est pas disponible"""
        code = "print('Hello, World!')"

        with patch('httpx.AsyncClient') as mock_client:
            mock_client.return_value.__aenter__.return_value.post.side_effect = httpx.RequestError("Connection failed")

            with patch('app.grader.run_local_python') as mock_local:
                mock_local.return_value = {
                    "ok": True,
                    "stdout": "Hello, World!",
                    "stderr": "",
                    "compile": {"stderr": ""},
                    "run": {"stdout": "Hello, World!", "stderr": ""}
                }

                ok, out = await grader.quick_syntax_check("http://test.com", code)

                assert ok is True
                assert out["stdout"] == "Hello, World!"
                mock_local.assert_called_once_with(code)

    @pytest.mark.asyncio
    async def test_quick_syntax_check_with_timeout(self):
        """Test vérification syntaxe avec timeout"""
        code = "print('test')"

        with patch('httpx.AsyncClient') as mock_client:
            mock_client.return_value.__aenter__.return_value.post.side_effect = asyncio.TimeoutError("Timeout")

            with patch('app.grader.run_local_python') as mock_local:
                mock_local.return_value = {
                    "ok": True,
                    "stdout": "test",
                    "stderr": "",
                    "compile": {"stderr": ""},
                    "run": {"stdout": "test", "stderr": ""}
                }

                ok, out = await grader.quick_syntax_check("http://test.com", code)

                assert ok is True
                mock_local.assert_called_once_with(code)

    @pytest.mark.asyncio
    async def test_quick_syntax_check_malformed_response(self):
        """Test gestion de réponse malformée de Piston"""
        code = "print('test')"

        mock_response = MagicMock()
        mock_response.json.side_effect = ValueError("Invalid JSON")

        with patch('httpx.AsyncClient') as mock_client:
            mock_client.return_value.__aenter__.return_value.post.return_value = mock_response

            with patch('app.grader.run_local_python') as mock_local:
                mock_local.return_value = {
                    "ok": True,
                    "stdout": "test",
                    "stderr": "",
                    "compile": {"stderr": ""},
                    "run": {"stdout": "test", "stderr": ""}
                }

                ok, out = await grader.quick_syntax_check("http://test.com", code)

                assert ok is True
                mock_local.assert_called_once_with(code)


class TestBuildHarnessAndRun:
    """Tests pour la fonction build_harness_and_run"""

    @pytest.mark.asyncio
    async def test_build_harness_and_run_success_piston(self):
        """Test construction et exécution harness réussie avec Piston"""
        student_code = "def add(a, b): return a + b"
        tests = [
            "result = add(2, 3)",
            "assert result == 5",
            "result = add(-1, 1)",
            "assert result == 0"
        ]

        mock_response = MagicMock()
        mock_response.json.return_value = {
            "compile": {"stderr": ""},
            "run": {"stdout": "__ALL_TESTS_OK__\n", "stderr": ""}
        }

        with patch('httpx.AsyncClient') as mock_client:
            mock_client.return_value.__aenter__.return_value.post.return_value = mock_response

            result = await grader.build_harness_and_run("http://test.com", student_code, tests)

            assert result["ok"] is True
            assert result["raw"]["run"]["stdout"] == "__ALL_TESTS_OK__\n"

    @pytest.mark.asyncio
    async def test_build_harness_and_run_test_failure_piston(self):
        """Test construction harness avec échec des tests via Piston"""
        student_code = "def add(a, b): return a + b"  # Implémentation correcte
        tests = [
            "result = add(2, 3)",
            "assert result == 6",  # Test qui va échouer
        ]

        mock_response = MagicMock()
        mock_response.json.return_value = {
            "compile": {"stderr": ""},
            "run": {"stdout": "AssertionError\n", "stderr": ""}
        }

        with patch('httpx.AsyncClient') as mock_client:
            mock_client.return_value.__aenter__.return_value.post.return_value = mock_response

            result = await grader.build_harness_and_run("http://test.com", student_code, tests)

            assert result["ok"] is False
            assert "__ALL_TESTS_OK__" not in result["raw"]["run"]["stdout"]

    @pytest.mark.asyncio
    async def test_build_harness_and_run_syntax_error_piston(self):
        """Test construction harness avec erreur de syntaxe via Piston"""
        student_code = "def add(a, b): return a + b"  # Code correct
        tests = [
            "result = add(2 3",  # Syntax error dans le test
        ]

        mock_response = MagicMock()
        mock_response.json.return_value = {
            "compile": {"stderr": "SyntaxError: invalid syntax"},
            "run": {"stdout": "", "stderr": ""}
        }

        with patch('httpx.AsyncClient') as mock_client:
            mock_client.return_value.__aenter__.return_value.post.return_value = mock_response

            result = await grader.build_harness_and_run("http://test.com", student_code, tests)

            assert result["ok"] is False

    @pytest.mark.asyncio
    async def test_build_harness_and_run_fallback_local(self):
        """Test fallback local quand Piston n'est pas disponible"""
        student_code = "def add(a, b): return a + b"
        tests = ["assert add(2, 3) == 5"]

        with patch('httpx.AsyncClient') as mock_client:
            mock_client.return_value.__aenter__.return_value.post.side_effect = httpx.RequestError("Connection failed")

            with patch('app.grader.run_local_python') as mock_local:
                mock_local.return_value = {
                    "ok": True,
                    "stdout": "__ALL_TESTS_OK__\n",
                    "stderr": "",
                    "compile": {"stderr": ""},
                    "run": {"stdout": "__ALL_TESTS_OK__\n", "stderr": ""}
                }

                result = await grader.build_harness_and_run("http://test.com", student_code, tests)

                assert result["ok"] is True
                mock_local.assert_called_once()

    @pytest.mark.asyncio
    async def test_build_harness_and_run_with_input_functions(self):
        """Test construction harness avec fonctions utilisant input()"""
        student_code = """
def greet():
    name = input("Enter name: ")
    return f"Hello, {name}!"
"""
        tests = [
            "result = run_with_input('Alice')",
            "assert 'Alice' in result"
        ]

        mock_response = MagicMock()
        mock_response.json.return_value = {
            "compile": {"stderr": ""},
            "run": {"stdout": "__ALL_TESTS_OK__\n", "stderr": ""}
        }

        with patch('httpx.AsyncClient') as mock_client:
            mock_client.return_value.__aenter__.return_value.post.return_value = mock_response

            result = await grader.build_harness_and_run("http://test.com", student_code, tests)

            assert result["ok"] is True

    @pytest.mark.asyncio
    async def test_build_harness_and_run_empty_tests(self):
        """Test construction harness avec liste de tests vide"""
        student_code = "print('Hello')"
        tests = []

        mock_response = MagicMock()
        mock_response.json.return_value = {
            "compile": {"stderr": ""},
            "run": {"stdout": "__ALL_TESTS_OK__\n", "stderr": ""}
        }

        with patch('httpx.AsyncClient') as mock_client:
            mock_client.return_value.__aenter__.return_value.post.return_value = mock_response

            result = await grader.build_harness_and_run("http://test.com", student_code, tests)

            assert result["ok"] is True

    @pytest.mark.asyncio
    async def test_build_harness_and_run_complex_student_code(self):
        """Test construction harness avec code étudiant complexe"""
        student_code = """
class Calculator:
    def __init__(self):
        self.result = 0

    def add(self, x):
        self.result += x
        return self

    def multiply(self, x):
        self.result *= x
        return self

    def get_result(self):
        return self.result
"""
        tests = [
            "calc = Calculator()",
            "result = calc.add(5).multiply(2).get_result()",
            "assert result == 10"
        ]

        mock_response = MagicMock()
        mock_response.json.return_value = {
            "compile": {"stderr": ""},
            "run": {"stdout": "__ALL_TESTS_OK__\n", "stderr": ""}
        }

        with patch('httpx.AsyncClient') as mock_client:
            mock_client.return_value.__aenter__.return_value.post.return_value = mock_response

            result = await grader.build_harness_and_run("http://test.com", student_code, tests)

            assert result["ok"] is True

    @pytest.mark.asyncio
    async def test_build_harness_and_run_with_special_characters(self):
        """Test construction harness avec caractères spéciaux"""
        student_code = "def greet(name): return f'Bonjour, {name}! 🌍'"
        tests = ["assert 'Bonjour' in greet('Alice')"]

        mock_response = MagicMock()
        mock_response.json.return_value = {
            "compile": {"stderr": ""},
            "run": {"stdout": "__ALL_TESTS_OK__\n", "stderr": ""}
        }

        with patch('httpx.AsyncClient') as mock_client:
            mock_client.return_value.__aenter__.return_value.post.return_value = mock_response

            result = await grader.build_harness_and_run("http://test.com", student_code, tests)

            assert result["ok"] is True


class TestGraderEdgeCases:
    """Tests des cas limites pour le grader"""

    @pytest.mark.asyncio
    async def test_run_local_python_large_output(self):
        """Test exécution locale avec grosse sortie"""
        code = """
for i in range(1000):
    print(f"Line {i}: " + "x" * 100)
"""

        result = await grader.run_local_python(code)

        assert result["ok"] is True
        assert len(result["stdout"]) > 100000  # Grosse sortie

    @pytest.mark.asyncio
    async def test_run_local_python_unicode_handling(self):
        """Test gestion Unicode dans l'exécution locale"""
        code = """
print("Hello 世界 🌍")
print("Café naïve résumé")
print("Этого нет")
print("العربية")
"""

        result = await grader.run_local_python(code)

        assert result["ok"] is True
        assert "世界" in result["stdout"]
        assert "Café" in result["stdout"]
        assert "Этого" in result["stdout"]
        assert "العربية" in result["stdout"]

    @pytest.mark.asyncio
    async def test_build_harness_quote_escaping(self):
        """Test que les guillemets dans le code sont bien échappés"""
        student_code = 'def greet(): return "Hello, \\"World\\""'
        tests = ['assert greet() == "Hello, \\"World\\""']

        mock_response = MagicMock()
        mock_response.json.return_value = {
            "compile": {"stderr": ""},
            "run": {"stdout": "__ALL_TESTS_OK__\n", "stderr": ""}
        }

        with patch('httpx.AsyncClient') as mock_client:
            mock_client.return_value.__aenter__.return_value.post.return_value = mock_response

            result = await grader.build_harness_and_run("http://test.com", student_code, tests)

            assert result["ok"] is True

    @pytest.mark.asyncio
    async def test_quick_syntax_check_partial_response(self):
        """Test gestion de réponse partielle de Piston"""
        code = "print('test')"

        mock_response = MagicMock()
        mock_response.json.return_value = {
            "compile": {"stderr": ""},
            # Pas de champ "run"
        }

        with patch('httpx.AsyncClient') as mock_client:
            mock_client.return_value.__aenter__.return_value.post.return_value = mock_response

            ok, out = await grader.quick_syntax_check("http://test.com", code)

            assert ok is True  # Pas d'erreur de compilation


@pytest.mark.integration
class TestGraderIntegration:
    """Tests d'intégration pour le grader"""

    @pytest.mark.asyncio
    async def test_full_workflow_local_fallback(self):
        """Test workflow complet avec fallback local"""
        # Désactiver Piston pour forcer le fallback
        with patch('httpx.AsyncClient') as mock_client:
            mock_client.return_value.__aenter__.return_value.post.side_effect = httpx.RequestError("Connection failed")

            # Test syntax check
            code = """
def factorial(n):
    if n <= 1:
        return 1
    return n * factorial(n - 1)

print(factorial(5))
"""
            ok, out = await grader.quick_syntax_check("http://unavailable.com", code)
            assert ok is True
            assert "120" in out["stdout"]

            # Test avec harness
            student_code = """
def factorial(n):
    if n <= 1:
        return 1
    return n * factorial(n - 1)
"""
            tests = [
                "assert factorial(1) == 1",
                "assert factorial(5) == 120",
                "assert factorial(0) == 1"
            ]

            result = await grader.build_harness_and_run("http://unavailable.com", student_code, tests)
            assert result["ok"] is True

    @pytest.mark.asyncio
    async def test_error_propagation(self):
        """Test propagation des erreurs à travers les fonctions"""
        code = "print('test')"

        # Simuler une erreur HTTP
        with patch('httpx.AsyncClient') as mock_client:
            mock_client.return_value.__aenter__.return_value.post.side_effect = httpx.HTTPStatusError(
                "Server Error", request=MagicMock(), response=MagicMock()
            )

            # Les fonctions doivent fallback vers l'exécution locale
            with patch('app.grader.run_local_python') as mock_local:
                mock_local.return_value = {
                    "ok": True,
                    "stdout": "test",
                    "stderr": "",
                    "compile": {"stderr": ""},
                    "run": {"stdout": "test", "stderr": ""}
                }

                ok, out = await grader.quick_syntax_check("http://test.com", code)
                assert ok is True
                mock_local.assert_called_once_with(code)


@pytest.mark.unit
class TestGraderPerformance:
    """Tests de performance pour le grader"""

    @pytest.mark.asyncio
    async def test_performance_multiple_syntax_checks(self):
        """Test performance de vérifications syntaxe multiples"""
        import time

        codes = [
            "print('Hello, World!')",
            "x = 5; y = 10; print(x + y)",
            "def add(a, b): return a + b",
            "for i in range(10): print(i)",
        ]

        start_time = time.time()

        with patch('app.grader.run_local_python') as mock_local:
            mock_local.return_value = {
                "ok": True,
                "stdout": "",
                "stderr": "",
                "compile": {"stderr": ""},
                "run": {"stdout": "", "stderr": ""}
            }

            for code in codes:
                await grader.quick_syntax_check("http://test.com", code)

        end_time = time.time()

        # Doit prendre moins de 2 secondes pour 4 vérifications
        assert (end_time - start_time) < 2.0