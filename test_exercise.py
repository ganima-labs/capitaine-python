#!/usr/bin/env python3
"""
Test simple pour vérifier qu'un exercice corrigé fonctionne toujours
"""

import requests
import json

def test_exercise():
    """Test l'exercice 01-print après correction"""

    url = "http://localhost:8080/api/grade"
    data = {
        "course_id": "python-basics",
        "exercise_id": "01-print",
        "code": "print(\"Salut Capitaine Python !\")",
        "learner": "TestUser"
    }

    try:
        response = requests.post(url, json=data)
        result = response.json()

        print("🧪 Test de l'exercice 01-print après correction:")
        print(f"📊 Status: {response.status_code}")

        if response.status_code == 200:
            exercise_result = result.get('result', {})
            success = exercise_result.get('ok', False)

            print(f"✅ Succès: {success}")

            if success:
                print("🎉 L'exercice fonctionne toujours correctement après la correction !")
                print("✨ La fonction execute_code() remplace bien run_with_input('')")
            else:
                print("❌ Problème détecté")
                hint = exercise_result.get('hint', 'No hint')
                print(f"💡 Hint: {hint}")
        else:
            print(f"❌ Erreur HTTP: {response.status_code}")
            print(f"📝 Response: {response.text}")

    except Exception as e:
        print(f"❌ Erreur de connexion: {e}")

if __name__ == "__main__":
    test_exercise()