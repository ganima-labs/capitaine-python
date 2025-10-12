#!/usr/bin/env python3
"""
Health check pour le service Piston
Vérifie que le service d'exécution de code fonctionne correctement
"""
import sys
import requests
import json
import subprocess
import time
from datetime import datetime

def check_piston_api():
    """Vérifie que l'API Piston répond"""
    try:
        response = requests.get("http://localhost:2000/api/v2/runtimes", timeout=10)
        if response.status_code != 200:
            return False, f"Piston API returned {response.status_code}"

        runtimes = response.json()
        if not isinstance(runtimes, list) or len(runtimes) == 0:
            return False, "No runtimes available"

        # Vérifier que Python est disponible
        python_found = False
        for runtime in runtimes:
            if runtime.get("language", "").lower() == "python":
                python_found = True
                break

        if not python_found:
            return False, "Python runtime not available"

        return True, f"Piston API healthy, {len(runtimes)} runtimes available"
    except Exception as e:
        return False, f"Piston API check failed: {str(e)}"

def check_piston_execution():
    """Test simple d'exécution de code"""
    try:
        test_code = """
print("Hello from health check")
print(2 + 2)
"""

        payload = {
            "language": "python",
            "version": "3.10.0",
            "files": [
                {
                    "name": "main.py",
                    "content": test_code
                }
            ]
        }

        response = requests.post(
            "http://localhost:2000/api/v2/execute",
            json=payload,
            timeout=15
        )

        if response.status_code != 200:
            return False, f"Code execution failed with status {response.status_code}"

        result = response.json()
        if result.get("compile", {}).get("code") != 0:
            return False, f"Code compilation failed: {result.get('compile', {}).get('stderr', '')}"

        if result.get("run", {}).get("code") != 0:
            return False, f"Code execution failed: {result.get('run', {}).get('stderr', '')}"

        output = result.get("run", {}).get("stdout", "")
        if "Hello from health check" not in output or "4" not in output:
            return False, f"Unexpected output: {output}"

        return True, "Code execution test successful"
    except Exception as e:
        return False, f"Code execution check failed: {str(e)}"

def check_disk_space():
    """Vérifie l'espace disque disponible"""
    try:
        import shutil
        total, used, free = shutil.disk_usage("/piston")
        free_percent = (free / total) * 100

        if free_percent < 10:
            return False, f"Low disk space: {free_percent:.1f}% free"

        return True, f"Disk space: {free_percent:.1f}% free"
    except Exception as e:
        return True, f"Disk space check failed: {str(e)}"

def check_process_status():
    """Vérifie le statut du processus Piston"""
    try:
        # Vérifier si le processus écoute sur le bon port
        result = subprocess.run(
            ["netstat", "-tlnp"],
            capture_output=True,
            text=True,
            timeout=5
        )

        if ":2000" in result.stdout:
            return True, "Piston process listening on port 2000"
        else:
            return False, "Piston process not found on port 2000"
    except Exception as e:
        # Alternative: utiliser curl
        try:
            subprocess.run(
                ["curl", "-f", "http://localhost:2000/api/v2/runtimes"],
                capture_output=True,
                timeout=5,
                check=True
            )
            return True, "Piston process responding"
        except:
            return False, "Cannot verify Piston process status"

def main():
    """Fonction principale de health check"""
    checks = [
        ("Piston API", check_piston_api),
        ("Code Execution", check_piston_execution),
        ("Disk Space", check_disk_space),
        ("Process Status", check_process_status)
    ]

    all_healthy = True
    results = []

    for name, check_func in checks:
        try:
            healthy, message = check_func()
            results.append({
                "service": name,
                "status": "healthy" if healthy else "unhealthy",
                "message": message,
                "timestamp": datetime.now().isoformat()
            })
            if not healthy:
                all_healthy = False
        except Exception as e:
            results.append({
                "service": name,
                "status": "error",
                "message": str(e),
                "timestamp": datetime.now().isoformat()
            })
            all_healthy = False

    # Afficher les résultats pour debugging
    for result in results:
        print(f"[{result['status'].upper()}] {result['service']}: {result['message']}")

    if not all_healthy:
        # Sauvegarder les résultats pour monitoring
        try:
            with open("/tmp/piston-health-results.json", "w") as f:
                json.dump(results, f, indent=2)
        except:
            pass

        sys.exit(1)

    print("✅ Piston service is healthy")
    sys.exit(0)

if __name__ == "__main__":
    main()