#!/usr/bin/env python3
"""
Script pour corriger les incohérences run_with_input dans le fichier python-basics.json
"""

import json
import re

def has_input_function(code):
    """Détecte si le code contient un appel à input()"""
    if not code or not isinstance(code, str):
        return False

    # Supprimer les commentaires pour éviter les faux positifs
    code_without_comments = re.sub(r'#.*$', '', code, flags=re.MULTILINE)

    # Rechercher les appels à input()
    return bool(re.search(r'\binput\s*\(', code_without_comments))

def fix_json_exercises(file_path):
    """Corrige les incohérences run_with_input dans un fichier JSON"""

    # Lire le fichier
    with open(file_path, 'r', encoding='utf-8') as f:
        data = json.load(f)

    fixed_count = 0

    # Analyser chaque exercice
    for exercise in data.get('exercises', []):
        starter = exercise.get('starter', {})
        tests = exercise.get('tests', [])

        # Vérifier si input() est dans le starter (peut être multilingue)
        has_input = False
        if isinstance(starter, dict):
            for lang, code in starter.items():
                if has_input_function(code):
                    has_input = True
                    break
        elif isinstance(starter, str):
            has_input = has_input_function(starter)

        # Corriger les tests si incohérence
        new_tests = []
        for test in tests:
            if 'run_with_input' in test and not has_input:
                # Remplacer run_with_input('') par execute_code()
                if "run_with_input('')" in test:
                    new_test = test.replace("run_with_input('')", "execute_code()")
                    new_tests.append(new_test)
                    fixed_count += 1
                else:
                    new_tests.append(test)
            else:
                new_tests.append(test)

        # Mettre à jour les tests
        exercise['tests'] = new_tests

    # Sauvegarder le fichier corrigé
    with open(file_path, 'w', encoding='utf-8') as f:
        json.dump(data, f, indent=2, ensure_ascii=False)

    return fixed_count

if __name__ == "__main__":
    file_path = "python-basics-backup.json"
    fixed = fix_json_exercises(file_path)
    print(f"✅ {fixed} tests corrigés dans {file_path}")

    # Vérification rapide
    with open(file_path, 'r') as f:
        data = json.load(f)

    inconsistencies = 0
    for ex in data['exercises']:
        starter = ex.get('starter', {})
        tests = ex.get('tests', [])

        has_input = False
        if isinstance(starter, dict):
            for lang, code in starter.items():
                if has_input_function(code):
                    has_input = True
                    break
        elif isinstance(starter, str):
            has_input = has_input_function(starter)

        uses_run_with_input = any('run_with_input' in test for test in tests)

        if uses_run_with_input and not has_input:
            inconsistencies += 1

    print(f"📊 Vérification: {inconsistencies} incohérences restantes")