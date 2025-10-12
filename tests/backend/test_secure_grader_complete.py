"""
Tests complets pour le module secure_grader.py
Couvre tous les aspects de l'exécution sécurisée de code
"""

import pytest
import asyncio
import tempfile
import os
import signal
import resource
from unittest.mock import Mock, patch, AsyncMock, MagicMock
from typing import Dict, Any

from .secure_grader import SecureCodeExecutor, secure_executor, quick_syntax_check, build_harness_and_run


class TestSecureCodeExecutorInit:
    """Tests pour l'initialisation de SecureCodeExecutor"""

    def test_default_initialization(self):
        """Test initialisation avec valeurs par défaut"""
        executor = SecureCodeExecutor()
        assert executor.max_execution_time == 10
        assert executor.max_memory == 128 * 1024 * 1024
        assert executor.security_validator is not None

    def test_custom_initialization(self):
        """Test initialisation avec valeurs personnalisées"""
        executor = SecureCodeExecutor(max_execution_time=5, max_memory=64*1024*1024)
        assert executor.max_execution_time == 5
        assert executor.max_memory == 64 * 1024 * 1024


class TestTimeoutContext:
    """Tests pour le contexte de timeout"""

    def test_timeout_context_success(self):
        """Test contexte de timeout qui réussit"""
        executor = SecureCodeExecutor()

        def timeout_handler(signum, frame):
            raise TimeoutError("Should not be called")

        with patch('signal.signal') as mock_signal:
            with patch('signal.alarm') as mock_alarm:
                # Simuler une opération rapide
                result = None
                with executor.timeout_context(5):
                    result = "success"

                assert result == "success"
                mock_signal.assert_called()
                mock_alarm.assert_called()

    def test_timeout_context_timeout(self):
        """Test contexte de timeout qui expire"""
        executor = SecureCodeExecutor()

        with patch('signal.signal') as mock_signal:
            with patch('signal.alarm') as mock_alarm:
                # Simuler un timeout
                mock_alarm.side_effect = signal.SIGALRM

                with pytest.raises(TimeoutError, match="Execution timed out"):
                    with executor.timeout_context(1):
                        import time
                        time.sleep(2)


class TestSandboxSetup:
    """Tests pour la configuration du sandbox"""

    def test_setup_sandbox_returns_expected_structure(self):
        """Test que _setup_sandbox retourne la structure attendue"""
        executor = SecureCodeExecutor()
        sandbox_config = executor._setup_sandbox()

        # Vérifier les clés attendues
        assert 'limits' in sandbox_config
        assert 'env' in sandbox_config
        assert 'cwd' in sandbox_config

        # Vérifier les limites de ressources
        limits = sandbox_config['limits']
        assert resource.RLIMIT_AS in limits
        assert resource.RLIMIT_DATA in limits
        assert resource.RLIMIT_STACK in limits
        assert resource.RLIMIT_FSIZE in limits
        assert resource.RLIMIT_NOFILE in limits

        # Vérifier les variables d'environnement
        env = sandbox_config['env']
        assert 'PATH' in env
        assert 'PYTHONPATH' in env
        assert 'HOME' in env
        assert 'TMPDIR' in env
        assert env['PYTHONPATH'] == ''
        assert env['HOME'] == '/tmp'

        # Vérifier le répertoire de travail
        assert sandbox_config['cwd'] == '/tmp'

    def test_sandbox_limits_values(self):
        """Test les valeurs des limites du sandbox"""
        executor = SecureCodeExecutor(max_memory=64*1024*1024)
        sandbox_config = executor._setup_sandbox()

        limits = sandbox_config['limits']
        assert limits[resource.RLIMIT_AS] == 64*1024*1024
        assert limits[resource.RLIMIT_DATA] == 64*1024*1024
        assert limits[resource.RLIMIT_STACK] == 8*1024*1024
        assert limits[resource.RLIMIT_FSIZE] == 1024*1024
        assert limits[resource.RLIMIT_NOFILE] == 16


class TestCodeExecutionSafety:
    """Tests pour la sécurité de l'exécution de code"""

    @pytest.mark.asyncio
    async def test_reject_dangerous_code(self):
        """Test rejet de code dangereux"""
        executor = SecureCodeExecutor()
        dangerous_code = "import os; os.system('ls')"

        result = await executor.execute_code_safely(dangerous_code)

        assert result['ok'] is False
        assert 'Security violation detected' in result['error']
        assert result['stdout'] == ''
        assert result['stderr'] == 'Security violation detected'
        assert 'security_issues' in result

    @pytest.mark.asyncio
    async def test_reject_dangerous_test_code(self):
        """Test rejet de code de test dangereux"""
        executor = SecureCodeExecutor()
        safe_code = "print('Hello, World!')"
        dangerous_test = "import os; os.system('ls')"

        result = await executor.execute_code_safely(safe_code, dangerous_test)

        assert result['ok'] is False
        assert 'Test code rejected' in result['error']
        assert result['stdout'] == ''
        assert result['stderr'] == 'Test code security violation detected'

    @pytest.mark.asyncio
    async def test_execute_safe_code_success(self):
        """Test exécution réussie de code sécurisé"""
        executor = SecureCodeExecutor()
        safe_code = "print('Hello, World!')"

        with patch.object(executor, '_execute_in_sandbox') as mock_execute:
            mock_execute.return_value = {
                'ok': True,
                'stdout': 'Hello, World!\n',
                'stderr': '',
                'returncode': 0,
                'success_indicators': {
                    'code_ok': True,
                    'tests_ok': False
                }
            }

            result = await executor.execute_code_safely(safe_code)

            assert result['ok'] is True
            assert 'Hello, World!' in result['stdout']
            mock_execute.assert_called_once()

    @pytest.mark.asyncio
    async def test_execute_with_test_code_success(self):
        """Test exécution réussie avec code de test"""
        executor = SecureCodeExecutor()
        student_code = """
def add(a, b):
    return a + b
"""
        test_code = """
result = add(2, 3)
assert result == 5
print('__ALL_TESTS_OK__')
"""

        with patch.object(executor, '_execute_in_sandbox') as mock_execute:
            mock_execute.return_value = {
                'ok': True,
                'stdout': '__ALL_TESTS_OK__\n',
                'stderr': '',
                'returncode': 0,
                'success_indicators': {
                    'code_ok': True,
                    'tests_ok': True
                }
            }

            result = await executor.execute_code_safely(student_code, test_code)

            assert result['ok'] is True
            assert result['success_indicators']['tests_ok'] is True

    @pytest.mark.asyncio
    async def test_execution_error_handling(self):
        """Test gestion des erreurs d'exécution"""
        executor = SecureCodeExecutor()
        safe_code = "print('Hello')"

        with patch.object(executor, '_execute_in_sandbox') as mock_execute:
            mock_execute.side_effect = Exception("Sandbox error")

            result = await executor.execute_code_safely(safe_code)

            assert result['ok'] is False
            assert 'Sandbox execution failed' in result['error']
            assert result['stdout'] == ''
            assert result['stderr'] == 'Sandbox error'


class TestCodePreparation:
    """Tests pour la préparation du code"""

    def test_prepare_execution_code_no_test(self):
        """Test préparation du code sans test"""
        executor = SecureCodeExecutor()
        student_code = "print('Hello, World!')"

        full_code = executor._prepare_execution_code(student_code)

        # Vérifier que le code étudiant est inclus
        assert student_code in full_code
        # Vérifier l'indicateur de succès
        assert '__CODE_EXECUTION_OK__' in full_code
        # Vérifier que les imports nécessaires sont là
        assert 'import sys' in full_code
        assert 'import io' in full_code
        assert 'import traceback' in full_code

    def test_prepare_execution_code_with_test(self):
        """Test préparation du code avec test"""
        executor = SecureCodeExecutor()
        student_code = "def hello():\n    return 'Hello'"
        test_code = "result = hello()\nassert result == 'Hello'"

        full_code = executor._prepare_execution_code(student_code, test_code)

        # Vérifier que les deux codes sont inclus
        assert student_code in full_code
        assert test_code in full_code
        # Vérifier l'indicateur de test
        assert '__ALL_TESTS_OK__' in full_code

    def test_prepare_execution_code_secure_context(self):
        """Test préparation avec contexte sécurisé"""
        executor = SecureCodeExecutor()
        student_code = "x = 1 + 1"

        full_code = executor._prepare_execution_code(student_code)

        # Vérifier le contexte sécurisé
        assert 'secure_globals = {' in full_code
        assert "'__builtins__': {}" in full_code
        # Vérifier les fonctions autorisées
        assert "'print': print" in full_code
        assert "'len': len" in full_code
        assert "'range': range" in full_code

    def test_prepare_execution_code_escape_handling(self):
        """Test gestion des caractères d'échappement"""
        executor = SecureCodeExecutor()
        student_code = "print('Test with \"quotes\" and \\backslash\\')"

        full_code = executor._prepare_execution_code(student_code)

        # Le code doit être correctement représenté
        assert "Test with \"quotes\"" in full_code
        assert repr(student_code) in full_code


class TestSandboxExecution:
    """Tests pour l'exécution dans le sandbox"""

    @pytest.mark.asyncio
    async def test_execute_in_sandbox_success(self):
        """Test exécution réussie dans le sandbox"""
        executor = SecureCodeExecutor()
        test_code = """
print('Hello, World!')
print('__CODE_EXECUTION_OK__')
"""

        with patch('tempfile.NamedTemporaryFile') as mock_temp:
            mock_file = Mock()
            mock_file.name = '/tmp/test.py'
            mock_temp.return_value.__enter__.return_value = mock_file

            with patch('asyncio.create_subprocess_exec') as mock_subprocess:
                mock_process = AsyncMock()
                mock_process.communicate.return_value = (
                    b'Hello, World!\n__CODE_EXECUTION_OK__\n',
                    b''
                )
                mock_process.returncode = 0
                mock_subprocess.return_value = mock_process

                with patch.object(executor, '_setup_sandbox') as mock_setup:
                    mock_setup.return_value = {
                        'limits': {},
                        'env': {'PATH': '/usr/bin'},
                        'cwd': '/tmp'
                    }

                    result = await executor._execute_in_sandbox(test_code)

                    assert result['ok'] is True
                    assert 'Hello, World!' in result['stdout']
                    assert result['success_indicators']['code_ok'] is True

    @pytest.mark.asyncio
    async def test_execute_in_sandbox_timeout(self):
        """Test timeout dans le sandbox"""
        executor = SecureCodeExecutor(max_execution_time=1)
        slow_code = """
import time
time.sleep(5)
print('Done')
"""

        with patch('tempfile.NamedTemporaryFile'):
            with patch('asyncio.create_subprocess_exec') as mock_subprocess:
                mock_process = AsyncMock()
                mock_process.communicate.side_effect = asyncio.TimeoutError()
                mock_process.kill = AsyncMock()
                mock_process.wait = AsyncMock()
                mock_subprocess.return_value = mock_process

                with patch.object(executor, '_setup_sandbox'):
                    result = await executor._execute_in_sandbox(slow_code)

                    assert result['ok'] is False
                    assert 'timed out' in result['error'].lower()
                    mock_process.kill.assert_called_once()

    @pytest.mark.asyncio
    async def test_execute_in_sandbox_failure(self):
        """Test échec d'exécution dans le sandbox"""
        executor = SecureCodeExecutor()
        error_code = """
print(1 / 0)  # Division by zero
"""

        with patch('tempfile.NamedTemporaryFile'):
            with patch('asyncio.create_subprocess_exec') as mock_subprocess:
                mock_process = AsyncMock()
                mock_process.communicate.return_value = (
                    b'',
                    b'ZeroDivisionError: division by zero\n'
                )
                mock_process.returncode = 1
                mock_subprocess.return_value = mock_process

                with patch.object(executor, '_setup_sandbox'):
                    result = await executor._execute_in_sandbox(error_code)

                    assert result['ok'] is False
                    assert 'ZeroDivisionError' in result['stderr']

    @pytest.mark.asyncio
    async def test_execute_in_sandbox_cleanup(self):
        """Test nettoyage des fichiers temporaires"""
        executor = SecureCodeExecutor()
        test_code = "print('Hello')"

        with patch('tempfile.NamedTemporaryFile') as mock_temp:
            mock_file = Mock()
            mock_file.name = '/tmp/test.py'
            mock_temp.return_value.__enter__.return_value = mock_file

            with patch('asyncio.create_subprocess_exec'):
                with patch.object(executor, '_setup_sandbox'):
                    with patch('os.unlink') as mock_unlink:
                        mock_unlink.side_effect = OSError("File not found")

                        # Le nettoyage doit être appelé même en cas d'erreur
                        await executor._execute_in_sandbox(test_code)
                        mock_unlink.assert_called_once_with('/tmp/test.py')


class TestResourceLimits:
    """Tests pour les limites de ressources"""

    def test_apply_resource_limits(self):
        """Test application des limites de ressources"""
        executor = SecureCodeExecutor()
        limits = {
            resource.RLIMIT_AS: 128 * 1024 * 1024,
            resource.RLIMIT_DATA: 64 * 1024 * 1024,
        }

        limit_function = executor._apply_resource_limits(limits)

        # La fonction doit être callable
        assert callable(limit_function)

        # Mock resource.setrlimit pour éviter les effets de bord
        with patch('resource.setrlimit') as mock_setrlimit:
            with patch('resource.RLIMIT_AS', resource.RLIMIT_AS):
                limit_function()

                # Vérifier que setrlimit a été appelé pour chaque limite
                assert mock_setrlimit.call_count >= 2

    def test_apply_resource_limits_with_unavailable_limits(self):
        """Test gestion des limites non disponibles"""
        executor = SecureCodeExecutor()
        limits = {
            resource.RLIMIT_AS: 128 * 1024 * 1024,
            # Limite qui pourrait ne pas exister
            999: 64 * 1024 * 1024,
        }

        limit_function = executor._apply_resource_limits(limits)

        with patch('resource.setrlimit') as mock_setrlimit:
            # Simuler une erreur pour une limite non disponible
            mock_setrlimit.side_effect = [None, ValueError("Resource limit not available")]

            # Ne doit pas lever d'exception
            limit_function()
            assert mock_setrlimit.call_count >= 1


class TestQuickSyntaxCheck:
    """Tests pour quick_syntax_check"""

    @pytest.mark.asyncio
    async def test_quick_syntax_check_dangerous_code(self):
        """Test quick_syntax_check avec code dangereux"""
        dangerous_code = "import os; os.system('ls')"
        exec_url = "http://test-executor"

        result = await quick_syntax_check(exec_url, dangerous_code)

        assert result[0] is False  # ok = False
        assert 'security reasons' in result[1]['error']

    @pytest.mark.asyncio
    async def test_quick_syntax_check_piston_unavailable(self):
        """Test quick_syntax_check quand Piston n'est pas disponible"""
        safe_code = "print('Hello')"
        exec_url = "http://test-executor"

        with patch('httpx.AsyncClient') as mock_client:
            mock_client.return_value.__aenter__.side_effect = Exception("Piston unavailable")

            with patch.object(secure_executor, 'execute_code_safely') as mock_execute:
                mock_execute.return_value = {
                    'ok': True,
                    'stdout': 'Hello\n',
                    'stderr': ''
                }

                result = await quick_syntax_check(exec_url, safe_code)

                assert result[0] is True
                assert 'Hello' in result[1]['stdout']

    @pytest.mark.asyncio
    async def test_quick_syntax_check_success(self):
        """Test quick_syntax_check réussi"""
        safe_code = "print('Hello')"
        exec_url = "http://test-executor"

        with patch('httpx.AsyncClient') as mock_client:
            mock_response = AsyncMock()
            mock_response.json.return_value = {
                'compile': {'stderr': ''},
                'run': {'stderr': '', 'stdout': 'Hello\n'}
            }
            mock_client.return_value.__aenter__.return_value.post.return_value = mock_response

            with patch('grader.make_runner_payload') as mock_payload:
                mock_payload.return_value = {'language': 'python', 'source': 'print("Hello")'}

                result = await quick_syntax_check(exec_url, safe_code)

                assert result[0] is True
                assert 'compile' in result[1]
                assert 'run' in result[1]

    @pytest.mark.asyncio
    async def test_quick_syntax_check_syntax_error(self):
        """Test quick_syntax_check avec erreur de syntaxe"""
        invalid_code = "print('Hello'"  # Manque la parenthèse fermante
        exec_url = "http://test-executor"

        with patch('httpx.AsyncClient') as mock_client:
            mock_response = AsyncMock()
            mock_response.json.return_value = {
                'compile': {'stderr': 'SyntaxError: unexpected EOF while parsing'},
                'run': {'stderr': '', 'stdout': ''}
            }
            mock_client.return_value.__aenter__.return_value.post.return_value = mock_response

            with patch('grader.make_runner_payload'):
                result = await quick_syntax_check(exec_url, invalid_code)

                assert result[0] is False
                assert 'SyntaxError' in result[1].get('compile', {}).get('stderr', '')


class TestBuildHarnessAndRun:
    """Tests pour build_harness_and_run"""

    @pytest.mark.asyncio
    async def test_build_harness_dangerous_student_code(self):
        """Test rejet de code étudiant dangereux"""
        dangerous_code = "import sys; sys.exit(0)"
        tests = ["assert True"]
        exec_url = "http://test-executor"

        result = await build_harness_and_run(exec_url, dangerous_code, tests)

        assert result['ok'] is False
        assert 'Student code rejected' in result['error']

    @pytest.mark.asyncio
    async def test_build_harness_piston_success(self):
        """Test build_harness_and_run réussi avec Piston"""
        student_code = "def add(a, b):\n    return a + b"
        tests = ["assert add(2, 3) == 5"]
        exec_url = "http://test-executor"

        with patch('httpx.AsyncClient') as mock_client:
            mock_response = AsyncMock()
            mock_response.json.return_value = {
                'run': {'stdout': '__ALL_TESTS_OK__\n', 'stderr': ''}
            }
            mock_client.return_value.__aenter__.return_value.post.return_value = mock_response

            with patch('grader.make_runner_payload'):
                result = await build_harness_and_run(exec_url, student_code, tests)

                assert result['ok'] is True
                assert 'raw' in result

    @pytest.mark.asyncio
    async def test_build_harness_fallback_to_secure_executor(self):
        """Test fallback vers l'exécuteur sécurisé"""
        student_code = "def hello():\n    return 'Hello'"
        tests = ["assert hello() == 'Hello'"]
        exec_url = "http://test-executor"

        with patch('httpx.AsyncClient') as mock_client:
            mock_client.return_value.__aenter__.side_effect = Exception("Piston unavailable")

            with patch.object(secure_executor, 'execute_code_safely') as mock_execute:
                mock_execute.return_value = {
                    'ok': True,
                    'success_indicators': {'tests_ok': True}
                }

                result = await build_harness_and_run(exec_url, student_code, tests)

                assert result['ok'] is True
                assert 'raw' in result
                mock_execute.assert_called_once_with(student_code, "\n".join(tests))

    @pytest.mark.asyncio
    async def test_build_harness_test_failure(self):
        """Test échec des tests dans build_harness_and_run"""
        student_code = "def add(a, b):\n    return a - b"  # Mauvaise implémentation
        tests = ["assert add(2, 3) == 5"]
        exec_url = "http://test-executor"

        with patch.object(secure_executor, 'execute_code_safely') as mock_execute:
            mock_execute.return_value = {
                'ok': False,
                'success_indicators': {'tests_ok': False},
                'stdout': '',
                'stderr': 'AssertionError'
            }

            result = await build_harness_and_run(exec_url, student_code, tests)

            assert result['ok'] is False


class TestGlobalExecutor:
    """Tests pour l'exécuteur global"""

    def test_global_executor_exists(self):
        """Test que l'exécuteur global existe"""
        from secure_grader import secure_executor
        assert secure_executor is not None
        assert isinstance(secure_executor, SecureCodeExecutor)

    def test_global_executor_default_config(self):
        """Test configuration par défaut de l'exécuteur global"""
        from secure_grader import secure_executor
        assert secure_executor.max_execution_time == 10
        assert secure_executor.max_memory == 128 * 1024 * 1024


class TestIntegrationScenarios:
    """Tests d'intégration pour les scénarios complets"""

    @pytest.mark.asyncio
    async def test_complete_workflow_success(self):
        """Test workflow complet réussi"""
        student_code = """
def fibonacci(n):
    if n <= 1:
        return n
    return fibonacci(n-1) + fibonacci(n-2)
"""
        test_code = """
assert fibonacci(0) == 0
assert fibonacci(1) == 1
assert fibonacci(5) == 5
assert fibonacci(10) == 55
print('__ALL_TESTS_OK__')
"""

        executor = SecureCodeExecutor(max_execution_time=30)

        with patch.object(executor, '_execute_in_sandbox') as mock_execute:
            mock_execute.return_value = {
                'ok': True,
                'stdout': '__ALL_TESTS_OK__\n',
                'stderr': '',
                'returncode': 0,
                'success_indicators': {
                    'code_ok': True,
                    'tests_ok': True
                }
            }

            result = await executor.execute_code_safely(student_code, test_code)

            assert result['ok'] is True
            assert result['success_indicators']['tests_ok'] is True

    @pytest.mark.asyncio
    async def test_complete_workflow_security_breach(self):
        """Test workflow complet avec tentative de violation de sécurité"""
        malicious_code = """
def harmless_function():
    return "I'm harmless!"

# Tentative d'import caché
__import__('os').system('echo "pwned"')
"""

        executor = SecureCodeExecutor()
        result = await executor.execute_code_safely(malicious_code)

        assert result['ok'] is False
        assert 'Security violation' in result['error']
        assert len(result['security_issues']) > 0

    @pytest.mark.asyncio
    async def test_complete_workflow_timeout_scenario(self):
        """Test workflow complet avec timeout"""
        infinite_loop_code = """
while True:
    pass  # Boucle infinie
"""

        executor = SecureCodeExecutor(max_execution_time=1)

        with patch.object(executor, '_execute_in_sandbox') as mock_execute:
            mock_execute.return_value = {
                'ok': False,
                'error': 'Execution timed out after 1 seconds',
                'stdout': '',
                'stderr': 'Timeout exceeded'
            }

            result = await executor.execute_code_safely(infinite_loop_code)

            assert result['ok'] is False
            assert 'timed out' in result['error'].lower()