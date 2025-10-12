#!/usr/bin/env python3
"""
Script de test complet pour l'interface Capitaine Python
Teste toutes les fonctionnalités principales de l'application
"""

import requests
import json
import time
from typing import Dict, Any

API_BASE = "http://localhost:8080"

def test_api_health():
    """Test si l'API répond"""
    print("🔍 Test santé de l'API...")
    try:
        response = requests.get(f"{API_BASE}/api/courses")
        if response.status_code == 200:
            print("✅ API opérationnelle")
            return True
        else:
            print(f"❌ API erreur {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ API inaccessible: {e}")
        return False

def test_courses_endpoint():
    """Test l'endpoint des cours"""
    print("\n📚 Test endpoint /api/courses...")
    try:
        response = requests.get(f"{API_BASE}/api/courses")
        courses = response.json()

        print(f"✅ {len(courses)} cours trouvés")

        # Vérifier la structure des cours
        for course in courses[:2]:  # Vérifier les 2 premiers
            assert 'id' in course, "Cours sans id"
            assert 'title' in course, "Cours sans title"
            assert 'fr' in course['title'], "Titre sans traduction française"
            print(f"  - {course['id']}: {course['title']['fr']}")

        return courses
    except Exception as e:
        print(f"❌ Erreur courses: {e}")
        return []

def test_exercises_endpoint(courses):
    """Test l'endpoint des exercices"""
    print("\n🎯 Test endpoint /api/courses/{id}/exercises...")

    if not courses:
        print("❌ Pas de cours à tester")
        return []

    course_id = courses[0]['id']
    print(f"Test du cours: {course_id}")

    try:
        response = requests.get(f"{API_BASE}/api/courses/{course_id}/exercises")
        exercises = response.json()

        print(f"✅ {len(exercises)} exercices trouvés")

        # Vérifier la structure des exercices
        for exercise in exercises[:3]:  # Vérifier les 3 premiers
            assert 'id' in exercise, "Exercice sans id"
            assert 'title' in exercise, "Exercice sans title"
            assert 'fr' in exercise['title'], "Titre sans traduction française"
            assert 'stars' in exercise, "Exercice sans stars"
            print(f"  - {exercise['id']}: {exercise['title']['fr']} ({'⭐' * exercise['stars']})")

        return exercises
    except Exception as e:
        print(f"❌ Erreur exercices: {e}")
        return []

def test_exercise_detail_endpoint(exercises):
    """Test l'endpoint de détail d'exercice"""
    print("\n📖 Test endpoint /api/exercises/{id}...")

    if not exercises:
        print("❌ Pas d'exercices à tester")
        return None

    exercise_id = exercises[0]['id']
    print(f"Test de l'exercice: {exercise_id}")

    try:
        response = requests.get(f"{API_BASE}/api/exercises/{exercise_id}")
        exercise = response.json()

        print(f"✅ Détail exercice reçu")

        # Vérifier les champs requis
        required_fields = ['id', 'title', 'stars', 'prompt', 'starter']
        for field in required_fields:
            assert field in exercise, f"Exercice sans {field}"

        print(f"  - Titre: {exercise['title']['fr']}")
        print(f"  - Difficulté: {'⭐' * exercise['stars']}")
        print(f"  - Prompt: {exercise['prompt']['fr'][:50]}...")
        print(f"  - Starter: {len(exercise['starter']['fr'])} caractères")

        return exercise
    except Exception as e:
        print(f"❌ Erreur détail exercice: {e}")
        return None

def test_run_endpoint():
    """Test l'endpoint d'exécution de code"""
    print("\n▶️ Test endpoint /api/run...")

    test_code = """
print("Hello World!")
x = 5 + 3
print(f"Résultat: {x}")
"""

    try:
        response = requests.post(f"{API_BASE}/api/run",
                               json={"code": test_code, "exercise_id": "01-print"})
        result = response.json()

        print("✅ Code exécuté")
        print(f"  - Sortie: {result.get('output', '').strip()}")
        print(f"  - Statut: {result.get('status', 'unknown')}")

        return result
    except Exception as e:
        print(f"❌ Erreur exécution: {e}")
        return None

def test_grade_endpoint():
    """Test l'endpoint de validation"""
    print("\n✅ Test endpoint /api/grade...")

    # Code correct pour l'exercice 01-print
    correct_code = 'print("Hello World!")'

    try:
        response = requests.post(f"{API_BASE}/api/grade",
                               json={"code": correct_code, "exercise_id": "01-print"})
        result = response.json()

        print("✅ Code validé")
        print(f"  - Statut: {result.get('status', 'unknown')}")
        print(f"  - Tests passés: {result.get('tests_passed', 0)}/{result.get('total_tests', 0)}")
        print(f"  - Feedback: {result.get('feedback', {}).get('fr', 'No feedback')[:50]}...")

        return result
    except Exception as e:
        print(f"❌ Erreur validation: {e}")
        return None

def test_frontend_html():
    """Test si le frontend HTML est accessible"""
    print("\n🌐 Test page HTML principale...")

    try:
        response = requests.get(API_BASE)
        if response.status_code == 200:
            print("✅ Page HTML accessible")

            # Vérifier la présence des éléments clés
            content = response.text
            elements_to_check = [
                'course-list',
                'ex-list',
                'solutionBtn',
                'hintBtn',
                'runBtn',
                'gradeBtn'
            ]

            for element in elements_to_check:
                if f'id="{element}"' in content:
                    print(f"  ✅ {element} trouvé")
                else:
                    print(f"  ❌ {element} manquant")

            return True
        else:
            print(f"❌ Page erreur {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ Erreur page HTML: {e}")
        return False

def test_static_files():
    """Test si les fichiers statiques sont accessibles"""
    print("\n📁 Test fichiers statiques...")

    try:
        response = requests.get(f"{API_BASE}/static/app.js")
        if response.status_code == 200:
            print("✅ app.js accessible")

            # Vérifier la présence des fonctions clés
            content = response.text
            key_functions = [
                'loadCoursesSimple',
                'selectCourseSimple',
                'showSolutionView',
                'handleImport'
            ]

            for func in key_functions:
                if func in content:
                    print(f"  ✅ {func} trouvé")
                else:
                    print(f"  ❌ {func} manquant")

            return True
        else:
            print(f"❌ app.js erreur {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ Erreur fichiers statiques: {e}")
        return False

def run_full_test():
    """Exécute tous les tests"""
    print("🚀 Démarrage des tests complets de Capitaine Python")
    print("=" * 50)

    # Tests de base
    if not test_api_health():
        return

    # Test frontend
    test_frontend_html()
    test_static_files()

    # Tests API
    courses = test_courses_endpoint()
    exercises = test_exercises_endpoint(courses)
    exercise_detail = test_exercise_detail_endpoint(exercises)

    # Tests fonctionnels
    test_run_endpoint()
    test_grade_endpoint()

    print("\n" + "=" * 50)
    print("🎉 Tests terminés !")

if __name__ == "__main__":
    run_full_test()