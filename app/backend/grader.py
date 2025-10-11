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