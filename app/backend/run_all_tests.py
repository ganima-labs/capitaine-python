#!/usr/bin/env python3
"""
Script pour exécuter la suite complète de tests Capitaine Python
Ce script exécute tous les tests et génère des rapports détaillés
"""

import subprocess
import sys
import os
import time
import json
from datetime import datetime

def run_command(cmd, description, cwd=None):
    """Exécute une commande et retourne le résultat"""
    print(f"\n{'='*60}")
    print(f"🚀 {description}")
    print(f"{'='*60}")

    start_time = time.time()

    try:
        result = subprocess.run(
            cmd,
            shell=True,
            cwd=cwd or os.path.dirname(__file__),
            capture_output=True,
            text=True
        )

        end_time = time.time()
        duration = end_time - start_time

        print(f"⏱️  Durée: {duration:.2f} secondes")

        if result.returncode == 0:
            print(f"✅ {description} - SUCCÈS")
        else:
            print(f"❌ {description} - ÉCHEC")
            print(f"📄 stdout:\n{result.stdout}")
            print(f"📄 stderr:\n{result.stderr}")

        return result.returncode == 0, duration, result.stdout, result.stderr

    except Exception as e:
        print(f"💥 Erreur lors de l'exécution: {e}")
        return False, 0, "", str(e)

def main():
    """Fonction principale d'exécution des tests"""

    print("🧪 SUITE COMPLÈTE DE TESTS - CAPITAINE PYTHON")
    print(f"📅 Date: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"🐍 Python: {sys.version}")

    results = {}
    total_start_time = time.time()

    # 1. Tests unitaires (rapides)
    success, duration, stdout, stderr = run_command(
        "python -m pytest test_course_manager.py test_db.py test_exercises.py -v --tb=short",
        "Tests Unitaires Core",
        "app/backend"
    )
    results['unit_tests'] = {
        'success': success,
        'duration': duration,
        'stdout': stdout,
        'stderr': stderr
    }

    # 2. Tests de sécurité
    success, duration, stdout, stderr = run_command(
        "python -m pytest test_security.py -v --tb=short",
        "Tests de Sécurité",
        "app/backend"
    )
    results['security_tests'] = {
        'success': success,
        'duration': duration,
        'stdout': stdout,
        'stderr': stderr
    }

    # 3. Tests API
    success, duration, stdout, stderr = run_command(
        "python -m pytest test_main.py -v --tb=short",
        "Tests API",
        "app/backend"
    )
    results['api_tests'] = {
        'success': success,
        'duration': duration,
        'stdout': stdout,
        'stderr': stderr
    }

    # 4. Tests de performance (rapides)
    success, duration, stdout, stderr = run_command(
        "python -m pytest test_performance_monitoring.py::TestPerformanceMetrics -v --tb=short",
        "Tests de Performance",
        "app/backend"
    )
    results['performance_tests'] = {
        'success': success,
        'duration': duration,
        'stdout': stdout,
        'stderr': stderr
    }

    # 5. Tests E2E (rapides)
    success, duration, stdout, stderr = run_command(
        "python -m pytest test_e2e_ui.py::TestE2EUserWorkflow::test_complete_learning_workflow -v --tb=short",
        "Tests E2E Workflow",
        "app/backend"
    )
    results['e2e_tests'] = {
        'success': success,
        'duration': duration,
        'stdout': stdout,
        'stderr': stderr
    }

    # 6. Tests de couverture (si disponible)
    success, duration, stdout, stderr = run_command(
        "python -m pytest --cov=. --cov-report=term-missing --cov-report=html:htmlcov --cov-fail-under=80 test_course_manager.py",
        "Tests de Couverture (seuil: 80%)",
        "app/backend"
    )
    results['coverage_tests'] = {
        'success': success,
        'duration': duration,
        'stdout': stdout,
        'stderr': stderr
    }

    total_end_time = time.time()
    total_duration = total_end_time - total_start_time

    # Générer le rapport final
    print(f"\n{'='*60}")
    print("📊 RAPPORT FINAL DES TESTS")
    print(f"{'='*60}")

    total_tests = 0
    passed_tests = 0

    for test_type, result in results.items():
        status = "✅ SUCCÈS" if result['success'] else "❌ ÉCHEC"
        print(f"{status} {test_type}: {result['duration']:.2f}s")

        if result['success']:
            passed_tests += 1
        total_tests += 1

    print(f"\n📈 Résumé: {passed_tests}/{total_tests} suites de tests réussies")
    print(f"⏱️  Durée totale: {total_duration:.2f} secondes")

    # Extraire les statistiques des tests
    test_stats = {}
    for test_type, result in results.items():
        if result['stdout']:
            # Compter les tests passés/échoués
            lines = result['stdout'].split('\n')
            passed = sum(1 for line in lines if 'PASSED' in line)
            failed = sum(1 for line in lines if 'FAILED' in line)
            errors = sum(1 for line in lines if 'ERROR' in line)

            test_stats[test_type] = {
                'passed': passed,
                'failed': failed,
                'errors': errors,
                'total': passed + failed + errors
            }

    print(f"\n📋 Statistiques détaillées:")
    total_passed = 0
    total_failed = 0
    total_errors = 0

    for test_type, stats in test_stats.items():
        if stats['total'] > 0:
            print(f"  {test_type}: {stats['passed']}/{stats['total']} passés")
            total_passed += stats['passed']
            total_failed += stats['failed']
            total_errors += stats['errors']

    overall_total = total_passed + total_failed + total_errors
    if overall_total > 0:
        success_rate = (total_passed / overall_total) * 100
        print(f"\n🎯 Taux de réussite global: {success_rate:.1f}% ({total_passed}/{overall_total})")

    # Sauvegarder le rapport JSON
    report_data = {
        'timestamp': datetime.now().isoformat(),
        'total_duration': total_duration,
        'results': results,
        'statistics': test_stats,
        'summary': {
            'total_suites': total_tests,
            'passed_suites': passed_tests,
            'success_rate': success_rate if overall_total > 0 else 0,
            'total_tests_run': overall_total,
            'total_passed': total_passed,
            'total_failed': total_failed,
            'total_errors': total_errors
        }
    }

    report_file = f"test_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
    with open(report_file, 'w', encoding='utf-8') as f:
        json.dump(report_data, f, indent=2, ensure_ascii=False)

    print(f"\n📄 Rapport détaillé sauvegardé: {report_file}")

    # Afficher les recommandations
    print(f"\n💡 Recommandations:")
    if passed_tests == total_tests:
        print("  ✅ Tous les tests passent! La plateforme est prête pour le déploiement.")
    else:
        print("  ❌ Certains tests échouent. Veuillez corriger les problèmes avant le déploiement.")

    if success_rate >= 90:
        print("  🎯 Excellente couverture de tests!")
    elif success_rate >= 80:
        print("  📊 Bonne couverture de tests.")
    else:
        print("  ⚠️  La couverture de tests pourrait être améliorée.")

    # Code de sortie basé sur les résultats
    if passed_tests == total_tests:
        print(f"\n🚀 SUCCÈS TOTAL - Tous les tests passent!")
        sys.exit(0)
    else:
        print(f"\n💥 ÉCHEC - {total_tests - passed_tests} suites de tests échouent")
        sys.exit(1)

if __name__ == "__main__":
    main()