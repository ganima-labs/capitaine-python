import asyncio
import tempfile
import subprocess
import sys
import os
import signal
import resource
from contextlib import contextmanager
from typing import Dict, Any, List, Optional
import logging
from .security import SecurityValidator

logger = logging.getLogger(__name__)

class SecureCodeExecutor:
    """Classe d'exécution de code sécurisée avec sandboxing"""

    def __init__(self, max_execution_time: int = 10, max_memory: int = 128 * 1024 * 1024):
        self.max_execution_time = max_execution_time
        self.max_memory = max_memory
        self.security_validator = SecurityValidator()

    @contextmanager
    def timeout_context(self, timeout: int):
        """Context manager pour le timeout"""
        def timeout_handler(signum, frame):
            raise TimeoutError(f"Execution timed out after {timeout} seconds")

        # Sauvegarder l'ancien handler
        old_handler = signal.signal(signal.SIGALRM, timeout_handler)

        try:
            signal.alarm(timeout)
            yield
        finally:
            signal.alarm(0)  # Désactiver l'alarme
            signal.signal(signal.SIGALRM, old_handler)  # Restaurer l'ancien handler

    def _setup_sandbox(self) -> Dict[str, Any]:
        """Configure l'environnement sandbox pour l'exécution"""
        # Limites de ressources
        limits = {
            resource.RLIMIT_AS: self.max_memory,  # Mémoire virtuelle
            resource.RLIMIT_DATA: self.max_memory,  # Mémoire data
            resource.RLIMIT_STACK: 8 * 1024 * 1024,  # Stack 8MB
            resource.RLIMIT_FSIZE: 1024 * 1024,  # Taille de fichier 1MB
            resource.RLIMIT_NOFILE: 16,  # Nombre de fichiers ouverts
        }

        # Variables d'environnement sécurisées
        secure_env = {
            'PATH': '/usr/bin:/bin',
            'PYTHONPATH': '',
            'HOME': '/tmp',
            'TMPDIR': '/tmp',
            'PYTHONIOENCODING': 'utf-8',
            'LANG': 'C.UTF-8',
            'LC_ALL': 'C.UTF-8',
        }

        return {
            'limits': limits,
            'env': secure_env,
            'cwd': '/tmp'
        }

    async def execute_code_safely(self, code: str, test_code: Optional[str] = None) -> Dict[str, Any]:
        """
        Exécute du code Python de manière sécurisée

        Args:
            code: Le code de l'étudiant à exécuter
            test_code: Code de test optionnel à exécuter après le code étudiant

        Returns:
            Dict contenant le résultat de l'exécution
        """
        try:
            # 1. Validation de sécurité
            security_analysis = self.security_validator.analyze_code_security(code)
            if not security_analysis['safe']:
                return {
                    'ok': False,
                    'error': f"Code rejected for security reasons: {', '.join(security_analysis['issues'])}",
                    'security_issues': security_analysis['issues'],
                    'stdout': '',
                    'stderr': 'Security violation detected'
                }

            if test_code:
                test_security = self.security_validator.analyze_code_security(test_code)
                if not test_security['safe']:
                    return {
                        'ok': False,
                        'error': f"Test code rejected for security reasons: {', '.join(test_security['issues'])}",
                        'security_issues': test_security['issues'],
                        'stdout': '',
                        'stderr': 'Test code security violation detected'
                    }

            # 2. Préparation du code complet
            full_code = self._prepare_execution_code(code, test_code)

            # 3. Exécution sécurisée
            return await self._execute_in_sandbox(full_code)

        except Exception as e:
            logger.error(f"Error in secure code execution: {e}")
            return {
                'ok': False,
                'error': f"Execution error: {self.security_validator.sanitize_error_message(str(e))}",
                'stdout': '',
                'stderr': 'Internal execution error'
            }

    def _prepare_execution_code(self, student_code: str, test_code: Optional[str] = None) -> str:
        """Prépare le code complet pour l'exécution"""

        # Créer un environnement d'exécution sécurisé
        secure_context = self.security_validator.create_safe_execution_context()

        # Code d'amorce sécurisé
        harness_lines = [
            "import sys",
            "import io",
            "import traceback",
            "import contextlib",
            "",
            "# Contexte d'exécution sécurisé",
            "secure_globals = {",
            "    '__builtins__': {},",
            "    'print': print,",
            "    'len': len,",
            "    'range': range,",
            "    'str': str,",
            "    'int': int,",
            "    'float': float,",
            "    'list': list,",
            "    'dict': dict,",
            "    'set': set,",
            "    'tuple': tuple,",
            "    'bool': bool,",
            "    'abs': abs,",
            "    'min': min,",
            "    'max': max,",
            "    'sum': sum,",
            "    'sorted': sorted,",
            "    'reversed': reversed,",
            "    'enumerate': enumerate,",
            "    'zip': zip,",
            "    'map': map,",
            "    'filter': filter,",
            "}",
            "",
            "# Fonctions utilitaires sécurisées",
            "def run_with_input(input_data=''):",
            "    backup_stdin = sys.stdin",
            "    backup_stdout = sys.stdout",
            "    sys.stdin = io.StringIO(input_data)",
            "    buf = io.StringIO()",
            "    sys.stdout = buf",
            "    try:",
            "        exec(student_code, secure_globals)",
            "        return buf.getvalue()",
            "    finally:",
            "        sys.stdin = backup_stdin",
            "        sys.stdout = backup_stdout",
            "",
            "# Isoler le code de l'étudiant",
            "student_code = " + repr(student_code),
            "",
            "# Exécuter le code de l'étudiant dans le contexte sécurisé",
            "try:",
            "    exec(student_code, secure_globals)",
            "except Exception as e:",
            "    print(f'Error during student code execution: {e}')",
            "    sys.exit(1)",
            ""
        ]

        # Ajouter le code de test si fourni
        if test_code:
            harness_lines.extend([
                "# Code de test",
                "try:",
                test_code,
                "    print('__ALL_TESTS_OK__')",
                "except Exception as e:",
                "    print(f'Test execution error: {e}')",
                "    traceback.print_exc()",
                "    sys.exit(1)",
            ])
        else:
            harness_lines.append("print('__CODE_EXECUTION_OK__')")

        return "\n".join(harness_lines)

    async def _execute_in_sandbox(self, code: str) -> Dict[str, Any]:
        """Exécute le code dans un environnement sandbox"""

        # Créer un fichier temporaire
        with tempfile.NamedTemporaryFile(mode='w', suffix='.py', delete=False) as f:
            f.write(code)
            temp_file = f.name

        try:
            # Configuration du sandbox
            sandbox_config = self._setup_sandbox()

            # Préparer la commande
            cmd = [sys.executable, '-u', temp_file]  # -u pour unbuffered output

            # Exécuter avec timeout et limites de ressources
            process = await asyncio.create_subprocess_exec(
                *cmd,
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE,
                cwd=sandbox_config['cwd'],
                env=sandbox_config['env'],
                preexec_fn=self._apply_resource_limits(sandbox_config['limits'])
            )

            # Attendre la fin avec timeout
            try:
                stdout, stderr = await asyncio.wait_for(
                    process.communicate(),
                    timeout=self.max_execution_time
                )
            except asyncio.TimeoutError:
                process.kill()
                await process.wait()
                return {
                    'ok': False,
                    'error': f'Execution timed out after {self.max_execution_time} seconds',
                    'stdout': '',
                    'stderr': 'Timeout exceeded'
                }

            # Traiter les résultats
            stdout_text = stdout.decode('utf-8', errors='replace')
            stderr_text = stderr.decode('utf-8', errors='replace')

            # Vérifier si tout s'est bien passé
            success = (
                process.returncode == 0 and
                ('__ALL_TESTS_OK__' in stdout_text or '__CODE_EXECUTION_OK__' in stdout_text)
            )

            return {
                'ok': success,
                'stdout': stdout_text,
                'stderr': stderr_text,
                'returncode': process.returncode,
                'success_indicators': {
                    'tests_ok': '__ALL_TESTS_OK__' in stdout_text,
                    'code_ok': '__CODE_EXECUTION_OK__' in stdout_text
                }
            }

        except Exception as e:
            logger.error(f"Sandbox execution error: {e}")
            return {
                'ok': False,
                'error': f"Sandbox execution failed: {self.security_validator.sanitize_error_message(str(e))}",
                'stdout': '',
                'stderr': 'Sandbox error'
            }
        finally:
            # Nettoyer le fichier temporaire
            try:
                os.unlink(temp_file)
            except OSError:
                pass

    def _apply_resource_limits(self, limits: Dict[str, int]):
        """Applique les limites de ressources au processus"""
        def limit_resources():
            for resource_type, limit in limits.items():
                try:
                    resource.setrlimit(resource_type, (limit, limit))
                except (ValueError, OSError):
                    # Certaines limites peuvent ne pas être disponibles
                    pass
        return limit_resources


# Instance globale pour l'exécution sécurisée
secure_executor = SecureCodeExecutor()


async def quick_syntax_check(exec_url: str, code: str) -> tuple[bool, Dict[str, Any]]:
    """
    Vérification syntaxique rapide avec sécurité
    """
    try:
        # Validation de sécurité d'abord
        security_analysis = SecurityValidator.analyze_code_security(code)
        if not security_analysis['safe']:
            return False, {
                'ok': False,
                'error': f"Code rejected for security reasons: {', '.join(security_analysis['issues'])}",
                'security_issues': security_analysis['issues']
            }

        # Essayer d'exécuter avec l'ancien système si disponible
        try:
            import httpx
            async with httpx.AsyncClient(timeout=10) as client:
                from .grader import make_runner_payload
                response = await client.post(exec_url, json=make_runner_payload(code))
                result = response.json()

                ok = not ((result.get("compile") or {}).get("stderr") or
                         (result.get("run") or {}).get("stderr"))
                return ok, result
        except Exception as piston_error:
            logger.warning(f"Piston unavailable: {piston_error}")

        # Fallback vers l'exécution sécurisée locale
        result = await secure_executor.execute_code_safely(code)
        return result['ok'], result

    except Exception as e:
        logger.error(f"Syntax check error: {e}")
        return False, {
            'ok': False,
            'error': f"Syntax check failed: {SecurityValidator.sanitize_error_message(str(e))}"
        }


async def build_harness_and_run(exec_url: str, student_code: str, tests: List[str]) -> Dict[str, Any]:
    """
    Construit et exécute le harness de tests avec sécurité
    """
    try:
        # Validation de sécurité du code étudiant
        student_security = SecurityValidator.analyze_code_security(student_code)
        if not student_security['safe']:
            return {
                'ok': False,
                'error': f"Student code rejected: {', '.join(student_security['issues'])}",
                'security_issues': student_security['issues']
            }

        # Préparer le code de test
        test_code = "\n".join(tests)

        # Essayer avec Piston si disponible
        try:
            import httpx
            from .grader import make_runner_payload

            # Construire le harness comme avant
            harness_lines = [
                "import sys, io",
                f"student_code = {student_code!r}",
                "def run_with_input(input_data=\"\"):",
                "    backup_stdin = sys.stdin",
                "    backup_stdout = sys.stdout",
                "    sys.stdin = io.StringIO(input_data)",
                "    buf = io.StringIO()",
                "    sys.stdout = buf",
                "    try:",
                "        exec(student_code, {})",
                "        return buf.getvalue()",
                "    finally:",
                "        sys.stdin = backup_stdin",
                "        sys.stdout = backup_stdout",
                "ns = {}",
                "exec(student_code, ns)",
                test_code,
                "print(\"__ALL_TESTS_OK__\")",
            ]
            harness = "\n".join(harness_lines)

            async with httpx.AsyncClient(timeout=15) as client:
                response = await client.post(exec_url, json=make_runner_payload(harness))
                result = response.json()

                stdout = ((result.get("run") or {}).get("stdout") or "")
                return {"ok": "__ALL_TESTS_OK__" in stdout, "raw": result}

        except Exception as piston_error:
            logger.warning(f"Piston unavailable, using secure executor: {piston_error}")

        # Fallback vers l'exécution sécurisée
        result = await secure_executor.execute_code_safely(student_code, test_code)

        return {
            'ok': result.get('success_indicators', {}).get('tests_ok', False),
            'raw': result
        }

    except Exception as e:
        logger.error(f"Harness execution error: {e}")
        return {
            'ok': False,
            'error': f"Test execution failed: {SecurityValidator.sanitize_error_message(str(e))}"
        }