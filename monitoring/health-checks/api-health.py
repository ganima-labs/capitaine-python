#!/usr/bin/env python3
"""
Health check pour l'API Capitaine Python
Vérifie que l'API répond correctement et que les dépendances sont accessibles
"""
import sys
import requests
import time
import json
from datetime import datetime

def check_api_health():
    """Vérifie la santé de l'API"""
    try:
        # Test de l'endpoint principal
        response = requests.get("http://localhost:8080/api/health", timeout=5)
        if response.status_code != 200:
            return False, f"API health endpoint returned {response.status_code}"

        data = response.json()
        if data.get("status") != "healthy":
            return False, f"API status is {data.get('status')}"

        return True, "API is healthy"
    except Exception as e:
        return False, f"API health check failed: {str(e)}"

def check_piston_connectivity():
    """Vérifie la connectivité avec Piston"""
    try:
        response = requests.get("http://piston:2000/api/v2/runtimes", timeout=10)
        if response.status_code == 200:
            return True, "Piston is accessible"
        else:
            return False, f"Piston returned {response.status_code}"
    except Exception as e:
        return False, f"Piston connectivity failed: {str(e)}"

def check_database():
    """Vérifie l'accès à la base de données"""
    try:
        # Vérifier que le fichier de base de données est accessible
        import os
        db_path = "/data/progress.db"
        if os.path.exists(db_path) and os.access(db_path, os.R_OK):
            return True, "Database is accessible"
        else:
            return False, "Database file is not accessible"
    except Exception as e:
        return False, f"Database check failed: {str(e)}"

def check_memory_usage():
    """Vérifie l'utilisation mémoire"""
    try:
        import psutil
        memory = psutil.virtual_memory()
        if memory.percent < 90:
            return True, f"Memory usage: {memory.percent:.1f}%"
        else:
            return False, f"High memory usage: {memory.percent:.1f}%"
    except Exception as e:
        # psutil n'est pas installé, on ignore cette vérification
        return True, "Memory check skipped"

def main():
    """Fonction principale de health check"""
    checks = [
        ("API", check_api_health),
        ("Piston", check_piston_connectivity),
        ("Database", check_database),
        ("Memory", check_memory_usage)
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
            with open("/tmp/health-check-results.json", "w") as f:
                json.dump(results, f, indent=2)
        except:
            pass

        sys.exit(1)

    print("✅ All services are healthy")
    sys.exit(0)

if __name__ == "__main__":
    main()