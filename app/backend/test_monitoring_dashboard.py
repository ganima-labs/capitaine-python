#!/usr/bin/env python3
"""
Dashboard de monitoring des tests pour Capitaine Python
Affiche l'état des tests en temps réel avec métriques détaillées
"""

import json
import time
import threading
import queue
from datetime import datetime, timedelta
from typing import Dict, List, Any
import subprocess
import os


class TestMonitoringDashboard:
    """Dashboard de monitoring des tests en temps réel"""

    def __init__(self):
        self.test_results = queue.Queue()
        self.monitoring_active = True
        self.results_history = []
        self.current_session = {
            'start_time': datetime.now(),
            'tests_run': 0,
            'tests_passed': 0,
            'tests_failed': 0,
            'total_duration': 0,
            'current_test': None,
            'last_update': None
        }

    def clear_screen(self):
        """Nettoie l'écran du terminal"""
        os.system('clear' if os.name == 'posix' else 'cls')

    def display_header(self):
        """Affiche l'en-tête du dashboard"""
        print("🧪 DASHBOARD DE MONITORING DES TESTS")
        print("=" * 60)
        print(f"📅 Session: {self.current_session['start_time'].strftime('%Y-%m-%d %H:%M:%S')}")
        print(f"⏱️  Durée: {(datetime.now() - self.current_session['start_time']).total_seconds():.1f}s")
        print(f"🔧 Python: {os.sys.version.split()[0]}")
        print("=" * 60)

    def display_summary(self):
        """Affiche le résumé des tests"""
        session = self.current_session
        total = session['tests_run']
        passed = session['tests_passed']
        failed = session['tests_failed']

        if total > 0:
            success_rate = (passed / total) * 100
        else:
            success_rate = 0

        print(f"📊 RÉSUMÉ DE LA SESSION")
        print(f"  📈 Tests exécutés: {total}")
        print(f"  ✅ Tests réussis: {passed}")
        print(f"  ❌ Tests échoués: {failed}")
        print(f"  🎯 Taux de réussite: {success_rate:.1f}%")
        print(f"  ⏱️  Durée totale: {session['total_duration']:.2f}s")

        if session['current_test']:
            print(f"  🔄 Test en cours: {session['current_test']}")

    def display_recent_results(self):
        """Affiche les résultats récents"""
        print(f"\n📋 RÉSULTATS RÉCENTS")
        print("-" * 60)

        if not self.results_history:
            print("  Aucun résultat encore...")
            return

        # Afficher les 10 derniers résultats
        recent_results = self.results_history[-10:]

        for result in reversed(recent_results):
            status_icon = "✅" if result['success'] else "❌"
            duration_str = f"{result['duration']:.2f}s"
            timestamp = result['timestamp'].strftime('%H:%M:%S')

            print(f"  {status_icon} {timestamp} | {result['test_name']} | {duration_str}")

            if not result['success'] and result.get('error'):
                # Afficher la première ligne de l'erreur
                error_lines = result['error'].split('\n')
                if error_lines:
                    print(f"    ⚠️  {error_lines[0][:80]}...")

    def display_performance_metrics(self):
        """Affiche les métriques de performance"""
        if not self.results_history:
            return

        print(f"\n📈 MÉTRIQUES DE PERFORMANCE")
        print("-" * 60)

        # Calculer les moyennes
        recent_results = self.results_history[-20:]  # 20 derniers résultats
        if recent_results:
            avg_duration = sum(r['duration'] for r in recent_results) / len(recent_results)
            max_duration = max(r['duration'] for r in recent_results)
            min_duration = min(r['duration'] for r in recent_results)

            print(f"  ⏱️  Durée moyenne (20 derniers): {avg_duration:.2f}s")
            print(f"  🚀 Durée max: {max_duration:.2f}s")
            print(f"  ⚡ Durée min: {min_duration:.2f}s")

        # Taux de réussite récent
        recent_passed = sum(1 for r in recent_results if r['success'])
        if recent_results:
            recent_success_rate = (recent_passed / len(recent_results)) * 100
            print(f"  🎯 Taux de réussite récent: {recent_success_rate:.1f}%")

    def run_test_and_monitor(self, test_command: str, test_name: str):
        """Exécute un test et surveille son exécution"""
        start_time = time.time()
        self.current_session['current_test'] = test_name

        try:
            # Exécuter le test
            result = subprocess.run(
                test_command,
                shell=True,
                capture_output=True,
                text=True,
                timeout=300  # 5 minutes max par test
            )

            end_time = time.time()
            duration = end_time - start_time
            success = result.returncode == 0

            # Créer le résultat
            test_result = {
                'test_name': test_name,
                'command': test_command,
                'success': success,
                'duration': duration,
                'timestamp': datetime.now(),
                'stdout': result.stdout,
                'stderr': result.stderr,
                'return_code': result.returncode
            }

            # Mettre à jour la session
            self.current_session['tests_run'] += 1
            self.current_session['total_duration'] += duration
            self.current_session['last_update'] = datetime.now()

            if success:
                self.current_session['tests_passed'] += 1
            else:
                self.current_session['tests_failed'] += 1
                test_result['error'] = result.stderr

            # Ajouter à l'historique
            self.results_history.append(test_result)

            # Mettre le résultat dans la queue pour le thread de display
            self.test_results.put(test_result)

            return test_result

        except subprocess.TimeoutExpired:
            end_time = time.time()
            duration = end_time - start_time

            error_result = {
                'test_name': test_name,
                'command': test_command,
                'success': False,
                'duration': duration,
                'timestamp': datetime.now(),
                'error': 'Timeout after 300 seconds',
                'return_code': -1
            }

            self.current_session['tests_run'] += 1
            self.current_session['tests_failed'] += 1
            self.current_session['total_duration'] += duration
            self.results_history.append(error_result)
            self.test_results.put(error_result)

            return error_result

        except Exception as e:
            end_time = time.time()
            duration = end_time - start_time

            error_result = {
                'test_name': test_name,
                'command': test_command,
                'success': False,
                'duration': duration,
                'timestamp': datetime.now(),
                'error': str(e),
                'return_code': -2
            }

            self.current_session['tests_run'] += 1
            self.current_session['tests_failed'] += 1
            self.current_session['total_duration'] += duration
            self.results_history.append(error_result)
            self.test_results.put(error_result)

            return error_result
        finally:
            self.current_session['current_test'] = None

    def display_loop(self):
        """Boucle d'affichage du dashboard"""
        while self.monitoring_active:
            self.clear_screen()
            self.display_header()
            self.display_summary()
            self.display_recent_results()
            self.display_performance_metrics()

            # Afficher les commandes disponibles
            print(f"\n⌨️  Commandes: 'q' pour quitter, 'r' pour rapport détaillé")
            print("=" * 60)

            time.sleep(1)  # Rafraîchir chaque seconde

    def generate_report(self):
        """Génère un rapport détaillé de la session"""
        if not self.results_history:
            return "Aucun résultat à rapporter."

        report = {
            'session_summary': self.current_session,
            'detailed_results': self.results_history,
            'generated_at': datetime.now().isoformat()
        }

        # Calculer les statistiques supplémentaires
        if self.results_history:
            durations = [r['duration'] for r in self.results_history]
            report['statistics'] = {
                'total_tests': len(self.results_history),
                'avg_duration': sum(durations) / len(durations),
                'min_duration': min(durations),
                'max_duration': max(durations),
                'total_duration': sum(durations)
            }

        return report

    def run_monitoring_session(self, test_commands: List[tuple]):
        """Lance une session de monitoring avec des commandes de test"""
        print("🚀 Démarrage du monitoring des tests...")
        print("Appuyez sur Ctrl+C pour arrêter")

        # Démarrer le thread d'affichage
        display_thread = threading.Thread(target=self.display_loop)
        display_thread.daemon = True
        display_thread.start()

        try:
            # Exécuter les tests
            for test_command, test_name in test_commands:
                if not self.monitoring_active:
                    break

                print(f"\n🔄 Lancement du test: {test_name}")
                result = self.run_test_and_monitor(test_command, test_name)

                # Pause entre les tests pour éviter la surcharge
                time.sleep(2)

            # Attendre un peu avant la fin
            time.sleep(5)

        except KeyboardInterrupt:
            print("\n\n⏹️  Arrêt manuel du monitoring...")
            self.monitoring_active = False

        # Afficher le rapport final
        self.monitoring_active = False
        time.sleep(1)  # Laisser le temps au display thread de s'arrêter

        self.clear_screen()
        self.display_header()
        self.display_summary()

        print(f"\n📊 RAPPORT FINAL")
        print("=" * 60)

        report = self.generate_report()
        report_file = f"test_monitoring_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"

        with open(report_file, 'w', encoding='utf-8') as f:
            json.dump(report, f, indent=2, default=str, ensure_ascii=False)

        print(f"📄 Rapport détaillé sauvegardé: {report_file}")

        # Recommandations
        session = self.current_session
        if session['tests_run'] > 0:
            success_rate = (session['tests_passed'] / session['tests_run']) * 100

            if success_rate >= 95:
                print("🎉 EXCELLENT! La plateforme est très stable.")
            elif success_rate >= 90:
                print("✅ BON! La plateforme est globalement stable.")
            elif success_rate >= 80:
                print("⚠️  ATTENTION! Quelques problèmes à résoudre.")
            else:
                print("❌ CRITIQUE! De nombreux problèmes détectés.")

            if session['total_duration'] > 0:
                avg_test_time = session['total_duration'] / session['tests_run']
                if avg_test_time > 10:
                    print("🐌 Les tests sont lents, optimisation recommandée.")
                elif avg_test_time < 2:
                    print("⚡ Performance excellente des tests!")

        return report


def main():
    """Fonction principale"""
    # Liste des tests à monitorer
    test_commands = [
        ("python -m pytest test_course_manager.py -v --tb=short", "Tests CourseManager"),
        ("python -m pytest test_security.py -v --tb=short", "Tests de Sécurité"),
        ("python -m pytest test_db.py -v --tb=short", "Tests Base de Données"),
        ("python -m pytest test_exercises.py -v --tb=short", "Tests Exercices"),
        ("python -m pytest test_e2e_ui.py::TestE2EUserWorkflow::test_complete_learning_workflow -v --tb=short", "Tests E2E Workflow"),
        ("python -m pytest test_performance_monitoring.py::TestPerformanceMetrics::test_api_response_times -v --tb=short", "Tests Performance"),
    ]

    # Démarrer le monitoring
    dashboard = TestMonitoringDashboard()
    dashboard.run_monitoring_session(test_commands)


if __name__ == "__main__":
    main()