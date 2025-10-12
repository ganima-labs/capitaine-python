#!/usr/bin/env python3
"""
Test du validateur d'exercices avec différents cas
"""

import requests
import json

def test_exercise_validation():
    """Test la validation d'exercices avec divers cas"""

    base_url = "http://localhost:8080"

    # Test 1: Exercice parfait
    perfect_exercise = {
        "id": "test-perfect",
        "title": "Exercice Parfait",
        "stars": 1,
        "prompt": {
            "fr": "Écris une fonction qui retourne 'Bonjour'",
            "en": "Write a function that returns 'Hello'"
        },
        "starter": "def bonjour():\n    return 'Bonjour'",
        "tests": ["assert ns.get('bonjour'), 'La fonction bonjour doit exister'", "assert ns['bonjour']() == 'Bonjour'"],
        "hints": {
            "fr": ["Utilise def", "Utilise return"],
            "en": ["Use def", "Use return"]
        },
        "solution_explanation": "Une fonction simple avec return"
    }

    # Test 2: Exercice avec problème de sécurité
    dangerous_exercise = {
        "id": "test-dangerous",
        "title": "Exercice Dangereux",
        "stars": 2,
        "prompt": "Utilise os.system pour exécuter une commande",
        "starter": "import os\nos.system('ls')",
        "tests": ["# Test dangereux"],
        "hints": ["Attention c'est dangereux"]
    }

    # Test 3: Exercice avec incohérence
    inconsistent_exercise = {
        "id": "test-inconsistent",
        "title": "Exercice Incohérent",
        "stars": 1,
        "prompt": "Affiche un message",
        "starter": "print('Hello')",  # Pas de input()
        "tests": ["out = run_with_input('test')", "assert 'Hello' in out"],  # Utilise run_with_input
        "hints": ["Utilise print"]
    }

    test_cases = [
        ("Parfait", perfect_exercise),
        ("Dangereux", dangerous_exercise),
        ("Incohérent", inconsistent_exercise)
    ]

    for name, exercise in test_cases:
        print(f"\n🧪 Test: {name}")
        print("=" * 40)

        try:
            response = requests.post(f"{base_url}/api/validate/exercise", json={"exercise": exercise})
            result = response.json()

            print(f"✅ Valide: {result['valid']}")
            print(f"⭐ Score: {result['score']}/100")
            print(f"📊 Erreurs: {result['error_count']}, Avertissements: {result['warning_count']}, Infos: {result['info_count']}")

            # Afficher les principales issues
            if result['issues']:
                print("\n🚨 Issues principales:")
                for issue in result['issues'][:3]:
                    level_icon = {'error': '❌', 'warning': '⚠️', 'info': '💡'}
                    icon = level_icon.get(issue['level'], '📝')
                    print(f"  {icon} [{issue['category']}] {issue['message']}")

        except Exception as e:
            print(f"❌ Erreur: {e}")

def test_course_validation():
    """Test la validation d'un cours complet"""

    base_url = "http://localhost:8080"

    course = {
        "meta": {
            "id": "test-course",
            "title": {"fr": "Cours de Test"},
            "level": "débutant"
        },
        "exercises": [
            {
                "id": "ex1",
                "title": "Exercice 1",
                "stars": 1,
                "prompt": "Test simple",
                "starter": "print('test')",
                "tests": ["out = execute_code()", "assert 'test' in out"],
                "hints": ["Indice"]
            },
            {
                "id": "ex2",
                "title": "Exercice 2",
                "stars": 2,
                "prompt": "Test avec input",
                "starter": "name = input()\nprint(f'Hello {name}')",
                "tests": ["out = run_with_input('World')", "assert 'Hello World' in out"],
                "hints": ["Indice 2"]
            }
        ]
    }

    print("\n📚 Test de validation de cours")
    print("=" * 40)

    try:
        response = requests.post(f"{base_url}/api/validate/course", json={"course": course})
        result = response.json()

        print(f"✅ Cours valide: {result['valid']}")
        print(f"📝 Exercices totaux: {result['total_exercises']}")
        print(f"✅ Exercices valides: {result['valid_exercises']}")
        print(f"⭐ Score moyen: {result['average_score']}/100")
        print(f"📊 Résumé: {result['summary']}")

    except Exception as e:
        print(f"❌ Erreur: {e}")

if __name__ == "__main__":
    test_exercise_validation()
    test_course_validation()