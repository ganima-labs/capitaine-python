#!/usr/bin/env python3
"""
Analyse des incohérences dans l'utilisation de run_with_input
Identifie les exercices qui utilisent run_with_input dans les tests
mais dont le code starter ne contient pas input()
"""

import re

def has_input_function(code):
    """Détecte si le code contient un appel à input()"""
    if not code or not isinstance(code, str):
        return False

    # Supprimer les commentaires pour éviter les faux positifs
    code_without_comments = re.sub(r'#.*$', '', code, flags=re.MULTILINE)

    # Rechercher les appels à input()
    return bool(re.search(r'\binput\s*\(', code_without_comments))

def analyze_exercises():
    """Analyse tous les exercices pour détecter les incohérences"""

    # Importer les exercices depuis le fichier
    import sys
    import os
    sys.path.append(os.path.join(os.path.dirname(__file__), 'app', 'backend'))

    from exercises import EXERCISES

    inconsistencies = []

    for exercise in EXERCISES:
        ex_id = exercise['id']
        title = exercise['title']
        starter = exercise.get('starter', '')
        tests = exercise.get('tests', [])

        # Vérifier si le code starter contient input()
        has_input_in_starter = has_input_function(starter)

        # Vérifier si les tests utilisent run_with_input
        uses_run_with_input = any('run_with_input' in test for test in tests)

        # Détecter les incohérences
        if uses_run_with_input and not has_input_in_starter:
            inconsistencies.append({
                'id': ex_id,
                'title': title,
                'issue': 'run_with_input utilisé mais input() pas dans starter',
                'starter_code': starter,
                'tests_with_run_with_input': [test for test in tests if 'run_with_input' in test]
            })
        elif has_input_in_starter and not uses_run_with_input:
            inconsistencies.append({
                'id': ex_id,
                'title': title,
                'issue': 'input() dans starter mais run_with_input pas utilisé dans tests',
                'starter_code': starter,
                'issue_type': 'missing_run_with_input'
            })

    return inconsistencies

def main():
    """Fonction principale"""
    print("🔍 Analyse des incohérences run_with_input...")
    print("=" * 60)

    inconsistencies = analyze_exercises()

    if not inconsistencies:
        print("✅ Aucune incohérence détectée !")
        return

    print(f"⚠️  {len(inconsistencies)} incohérence(s) détectée(s) :")
    print()

    for i, issue in enumerate(inconsistencies, 1):
        print(f"{i}. Exercice {issue['id']} - {issue['title']}")
        print(f"   ❌ Problème : {issue['issue']}")
        print(f"   📝 Code starter :")
        for line in issue['starter_code'].split('\n'):
            print(f"      {line}")

        if issue['issue'] == 'run_with_input utilisé mais input() pas dans starter':
            print("   🧪 Tests qui utilisent run_with_input :")
            for test in issue['tests_with_run_with_input']:
                print(f"      • {test}")
            print("   💡 Suggestion : Remplacer run_with_input('') par exécution directe")
        else:
            print("   💡 Suggestion : Ajouter des tests avec run_with_input ou utiliser un autre pattern")

        print()

    # Générer le code corrigé
    print("🔧 Code suggéré pour les corrections :")
    print("=" * 60)

    for issue in inconsistencies:
        if issue['issue'] == 'run_with_input utilisé mais input() pas dans starter':
            print(f"# Exercice {issue['id']} - Correction")
            corrected_tests = []
            for test in issue['tests_with_run_with_input']:
                if test.strip().startswith("out = run_with_input('')"):
                    # Remplacer par exécution directe
                    corrected_test = test.replace("out = run_with_input('')", "out = execute_code()")
                    corrected_tests.append(corrected_test)
                else:
                    corrected_tests.append(test)

            print(f"  \"tests\": [")
            for test in corrected_tests:
                print(f"    \"{test}\",")
            print(f"  ],")
            print()

if __name__ == "__main__":
    main()