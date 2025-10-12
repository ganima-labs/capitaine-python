import httpx
import subprocess
import tempfile
import os
import sys

def make_runner_payload(code: str, stdin: str = ""):
    return {
        "language": "python",
        "files": [{"name": "main.py", "content": code}],
        "stdin": stdin,
        "args": [],
        "compile_timeout": 7000,
        "run_timeout": 5000,
        "run_memory_limit": 128000000,
    }

async def run_local_python(code: str, stdin: str = "", timeout: int = 10):
    """Fallback pour exécuter le code Python localement si Piston n'est pas disponible"""
    try:
        with tempfile.NamedTemporaryFile(mode='w', suffix='.py', delete=False) as f:
            f.write(code)
            temp_file = f.name

        result = subprocess.run(
            [sys.executable, temp_file],
            input=stdin,
            text=True,
            capture_output=True,
            timeout=timeout
        )

        # Nettoyer le fichier temporaire
        os.unlink(temp_file)

        return {
            "ok": result.returncode == 0,
            "stdout": result.stdout,
            "stderr": result.stderr,
            "compile": {"stderr": ""},  # Pour compatibilité avec le format Piston
            "run": {"stdout": result.stdout, "stderr": result.stderr}
        }
    except subprocess.TimeoutExpired:
        if os.path.exists(temp_file):
            os.unlink(temp_file)
        return {
            "ok": False,
            "stdout": "",
            "stderr": "Timeout: execution took too long",
            "compile": {"stderr": ""},
            "run": {"stdout": "", "stderr": "Timeout: execution took too long"}
        }
    except Exception as e:
        return {
            "ok": False,
            "stdout": "",
            "stderr": str(e),
            "compile": {"stderr": ""},
            "run": {"stdout": "", "stderr": str(e)}
        }

async def quick_syntax_check(exec_url: str, code: str):
    try:
        async with httpx.AsyncClient(timeout=10) as c:
            r = await c.post(exec_url, json=make_runner_payload(code))
        out = r.json()
        ok = not ((out.get("compile") or {}).get("stderr") or (out.get("run") or {}).get("stderr"))
        return ok, out
    except Exception as e:
        # Fallback vers l'exécution locale si Piston n'est pas disponible
        print(f"Piston non disponible, utilisation du fallback local: {e}")
        out = await run_local_python(code)
        ok = not out.get("stderr")
        return ok, out

async def build_harness_and_run(exec_url: str, student_code: str, tests: list[str]):
    # Construit le harness SANS triple quotes → pas d'erreur d'échappement
    tests_src = "\n".join(tests)
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
        "def execute_code():",
        "    backup_stdout = sys.stdout",
        "    buf = io.StringIO()",
        "    sys.stdout = buf",
        "    try:",
        "        exec(student_code, {})",
        "        return buf.getvalue()",
        "    finally:",
        "        sys.stdout = backup_stdout",
        "ns = {}",
        "exec(student_code, ns)",
        tests_src,
        "print(\"__ALL_TESTS_OK__\")",
    ]
    harness = "\n".join(harness_lines)

    try:
        async with httpx.AsyncClient(timeout=15) as c:
            r = await c.post(exec_url, json=make_runner_payload(harness))
        out = r.json()
        stdout = ((out.get("run") or {}).get("stdout") or "")
        return {"ok": "__ALL_TESTS_OK__" in stdout, "raw": out}
    except Exception as e:
        # Fallback vers l'exécution locale si Piston n'est pas disponible
        print(f"Piston non disponible, utilisation du fallback local: {e}")
        out = await run_local_python(harness)
        stdout = out.get("stdout", "")
        return {"ok": "__ALL_TESTS_OK__" in stdout, "raw": out}


async def run_code_with_inputs(exec_url: str, student_code: str, inputs: list[str], timeout: int = 30):
    """
    Exécute du code Python avec des inputs utilisateur fournis
    """
    # Préparer les inputs (ajouter \n à chaque input sauf le dernier)
    prepared_inputs = []
    for i, inp in enumerate(inputs):
        if i < len(inputs) - 1:
            prepared_inputs.append(inp + "\n")
        else:
            prepared_inputs.append(inp)

    # Construire le code avec simulation d'inputs
    input_simulation = ";\n".join([f'inputs[{i}]' for i in range(len(inputs))])

    interactive_harness = [
        "import sys, io",
        f"student_code = {student_code!r}",
        f"inputs = {prepared_inputs!r}",
        "input_index = 0",
        "",
        "def mock_input(prompt=''):",
        "    global input_index",
        "    if input_index < len(inputs):",
        "        result = inputs[input_index]",
        "        input_index += 1",
        "        return result",
        "    return ''",
        "",
        "# Remplacer input() par notre mock",
        "backup_input = input",
        "input = mock_input",
        "",
        "# Configurer stdout pour capturer la sortie",
        "backup_stdout = sys.stdout",
        "buf = io.StringIO()",
        "sys.stdout = buf",
        "",
        "try:",
        "    exec(student_code, {})",
        "    output = buf.getvalue()",
        "except Exception as e:",
        "    output = f'Error: {str(e)}'",
        "finally:",
        "    sys.stdout = backup_stdout",
        "    input = backup_input",
        "",
        "print(output)",
        "print('___INTERACTIVE_EXECUTION_COMPLETE___')"
    ]

    harness = "\n".join(interactive_harness)

    try:
        # Utiliser un timeout plus long pour les interactions
        payload = make_runner_payload(harness)
        payload["run_timeout"] = timeout * 1000  # Convertir en ms

        async with httpx.AsyncClient(timeout=timeout + 5) as c:
            r = await c.post(exec_url, json=payload)
        out = r.json()

        stdout = ((out.get("run") or {}).get("stdout") or "")

        # Extraire la sortie de l'étudiant
        if "___INTERACTIVE_EXECUTION_COMPLETE___" in stdout:
            parts = stdout.split("___INTERACTIVE_EXECUTION_COMPLETE___")
            student_output = parts[0].strip()
            return {
                "ok": True,
                "output": student_output,
                "raw": out,
                "inputs_used": len(inputs)
            }
        else:
            # Erreur d'exécution
            return {
                "ok": False,
                "output": stdout.strip(),
                "raw": out,
                "inputs_used": len(inputs)
            }

    except Exception as e:
        # Fallback vers l'exécution locale
        print(f"Piston non disponible pour les inputs, utilisation du fallback local: {e}")
        out = await run_local_python(harness, "\n".join(inputs), timeout)
        stdout = out.get("stdout", "")

        if "___INTERACTIVE_EXECUTION_COMPLETE___" in stdout:
            parts = stdout.split("___INTERACTIVE_EXECUTION_COMPLETE___")
            student_output = parts[0].strip()
            return {
                "ok": True,
                "output": student_output,
                "raw": out,
                "inputs_used": len(inputs)
            }
        else:
            return {
                "ok": False,
                "output": stdout.strip(),
                "raw": out,
                "inputs_used": len(inputs)
            }