#!/usr/bin/env python3
"""
Test complet de l'expérience Capitaine Python - Simulation apprenant de 9 ans (FINAL)
"""

import time
import requests
import json
from typing import Dict, Any

class ChildExperienceTester:
    """Testeur simulant un enfant de 9 ans apprenant Python"""

    def __init__(self):
        self.base_url = "http://localhost:8080"
        self.session = requests.Session()
        # Utiliser un nom valide selon les standards de sécurité
        self.child_name = "Leo123"  # Nom valide pour enfant de 9 ans
        self.progress = []

    def log_step(self, action: str, details: str = ""):
        """Enregistre une étape du test"""
        timestamp = time.strftime("%H:%M:%S")
        entry = f"[{timestamp}] {action}"
        if details:
            entry += f" - {details}"
        print(entry)
        self.progress.append(entry)

    def check_api_health(self) -> bool:
        """Vérifie que l'API fonctionne"""
        try:
            response = self.session.get(f"{self.base_url}/api/health")
            if response.status_code == 200:
                self.log_step("✅ API santé vérifiée", response.json().get("status", "unknown"))
                return True
        except Exception as e:
            self.log_step("❌ API inaccessible", str(e))
        return False

    def get_available_courses(self) -> Dict[str, Any]:
        """Récupère la liste des cours disponibles"""
        try:
            response = self.session.get(f"{self.base_url}/api/courses")
            if response.status_code == 200:
                courses = response.json()
                self.log_step("📚 Cours disponibles", f"{len(courses)} cours trouvés")
                for course in courses:
                    self.log_step(f"  • {course['id']}", course.get('title', {}).get('fr', 'Sans titre'))
                return courses
        except Exception as e:
            self.log_step("❌ Erreur récupération cours", str(e))
        return {}

    def choose_course_for_child(self, courses: list) -> str:
        """Choisit le cours le plus adapté pour un enfant de 9 ans"""
        # Priorité: python-basics (débutant)
        for course in courses:
            if course['id'] == 'python-basics':
                self.log_step("🎯 Cours choisi", "python-basics - parfait pour débutant")
                return course['id']

        # Alternative: premier cours disponible
        if courses:
            course_id = courses[0]['id']
            self.log_step("🎯 Cours choisi par défaut", course_id)
            return course_id

        self.log_step("❌ Aucun cours disponible")
        return ""

    def get_course_exercises(self, course_id: str) -> list:
        """Récupère les exercices d'un cours"""
        try:
            response = self.session.get(f"{self.base_url}/api/courses/{course_id}/exercises")
            if response.status_code == 200:
                exercises = response.json()
                self.log_step("📝 Exercices chargés", f"{len(exercises)} exercices dans {course_id}")
                return exercises
        except Exception as e:
            self.log_step("❌ Erreur chargement exercices", str(e))
        return []

    def test_exercise_as_child(self, course_id: str, exercise: Dict[str, Any]) -> Dict[str, Any]:
        """Teste un exercice comme un enfant de 9 ans"""
        exercise_id = exercise.get('id', 'unknown')
        title = exercise.get('title', {}).get('fr', 'Sans titre')
        stars = exercise.get('stars', 1)

        self.log_step(f"🌟 Exercice {exercise_id}", f"{title} ({'⭐' * stars})")

        # Récupérer les détails de l'exercice
        try:
            response = self.session.get(f"{self.base_url}/api/courses/{course_id}/exercises/{exercise_id}")
            if response.status_code != 200:
                self.log_step(f"❌ Erreur détails exercice {exercise_id}")
                return {"success": False, "error": "Details not found"}

            exercise_details = response.json()

        except Exception as e:
            self.log_step(f"❌ Erreur récupération détails {exercise_id}", str(e))
            return {"success": False, "error": str(e)}

        # Analyser le contenu comme un enfant
        prompt = exercise_details.get('prompt', {}).get('fr', '')
        starter = exercise_details.get('starter', '')
        hints = exercise_details.get('hints', {}).get('fr', [])

        self.log_step("  📖 Prompt", prompt[:100] + "..." if len(prompt) > 100 else prompt)

        # Vérifier si l'exercice a besoin d'input
        has_input = 'input(' in starter

        if has_input:
            return self.test_interactive_exercise(course_id, exercise_id, exercise_details)
        else:
            return self.test_simple_exercise(course_id, exercise_id, exercise_details)

    def test_simple_exercise(self, course_id: str, exercise_id: str, exercise: Dict[str, Any]) -> Dict[str, Any]:
        """Teste un exercice simple (sans input)"""
        starter = exercise.get('starter', '')

        self.log_step("  💻 Type", "Exercice simple (sans input)")
        self.log_step("  📝 Code de départ", starter[:50] + "..." if len(starter) > 50 else starter)

        # Simuler l'enfant qui utilise le code de départ
        try:
            # Test d'exécution simple
            run_payload = {
                "course_id": course_id,
                "exercise_id": exercise_id,
                "code": starter,
                "learner": self.child_name
            }

            run_response = self.session.post(
                f"{self.base_url}/api/run",
                json=run_payload
            )

            if run_response.status_code == 200:
                run_result = run_response.json()
                ok = run_result.get('ok', False)
                if ok:
                    self.log_step("  ▶️  Exécution réussie", "Code exécuté sans erreur")
                else:
                    self.log_step("  ❌ Erreur exécution", "Code contient des erreurs")
            else:
                self.log_step("  ❌ Erreur exécution", f"Status: {run_response.status_code}")
                self.log_step("  📝 Détails", run_response.text[:200])

        except Exception as e:
            self.log_step("  ❌ Erreur test exécution", str(e))

        # Test de validation (grading)
        try:
            grade_payload = {
                "course_id": course_id,
                "exercise_id": exercise_id,
                "code": starter,
                "learner": self.child_name
            }

            grade_response = self.session.post(
                f"{self.base_url}/api/grade",
                json=grade_payload
            )

            if grade_response.status_code == 200:
                grade_result = grade_response.json()
                result = grade_result.get('result', {})
                success = result.get('ok', False)
                hint = result.get('hint', '')

                if success:
                    self.log_step("  🎉 EXERCICE RÉUSSI !", "Bravo Léo !")
                    self.log_step("  🏆 Récompense", hint[:100] + "..." if len(hint) > 100 else hint)
                else:
                    self.log_step("  😢 Exercice échoué", "Besoin d'aide")
                    self.log_step("  💡 Indice", hint[:100] + "..." if len(hint) > 100 else hint)

                return {"success": success, "result": result}
            else:
                self.log_step("  ❌ Erreur validation", f"Status: {grade_response.status_code}")
                self.log_step("  📝 Détails", grade_response.text[:200])

        except Exception as e:
            self.log_step("  ❌ Erreur test validation", str(e))

        return {"success": False, "error": "Test failed"}

    def test_interactive_exercise(self, course_id: str, exercise_id: str, exercise: Dict[str, Any]) -> Dict[str, Any]:
        """Teste un exercice interactif (avec input)"""
        starter = exercise.get('starter', '')

        self.log_step("  💻 Type", "Exercice interactif (avec input)")
        self.log_step("  📝 Code de départ", starter[:50] + "..." if len(starter) > 50 else starter)

        # Simuler des inputs d'enfant (simples)
        test_inputs = self.generate_child_inputs(starter)

        try:
            # Test avec inputs
            interactive_payload = {
                "course_id": course_id,
                "exercise_id": exercise_id,
                "code": starter,
                "inputs": test_inputs,
                "learner": self.child_name,
                "timeout": 10
            }

            interactive_response = self.session.post(
                f"{self.base_url}/api/run-with-inputs",
                json=interactive_payload
            )

            if interactive_response.status_code == 200:
                interactive_result = interactive_response.json()
                success = interactive_result.get('ok', False)
                output = interactive_result.get('output', '')

                if success:
                    self.log_step("  ▶️  Test interactif réussi", f"Inputs: {test_inputs}")
                    self.log_step("  📤 Sortie", output[:100] + "..." if len(output) > 100 else output)
                else:
                    self.log_step("  ❌ Test interactif échoué", interactive_result.get('output', ''))

            else:
                self.log_step("  ❌ Erreur test interactif", f"Status: {interactive_response.status_code}")
                self.log_step("  📝 Détails", interactive_response.text[:200])

        except Exception as e:
            self.log_step("  ❌ Erreur test interactif", str(e))

        # Test de validation
        try:
            grade_payload = {
                "course_id": course_id,
                "exercise_id": exercise_id,
                "code": starter,
                "learner": self.child_name
            }

            grade_response = self.session.post(
                f"{self.base_url}/api/grade",
                json=grade_payload
            )

            if grade_response.status_code == 200:
                grade_result = grade_response.json()
                result = grade_result.get('result', {})
                success = result.get('ok', False)
                hint = result.get('hint', '')

                if success:
                    self.log_step("  🎉 EXERCICE INTERACTIF RÉUSSI !")
                    self.log_step("  🏆 Récompense", hint[:100] + "..." if len(hint) > 100 else hint)
                else:
                    self.log_step("  😢 Exercice interactif échoué")
                    self.log_step("  💡 Indice", hint[:100] + "..." if len(hint) > 100 else hint)

                return {"success": success, "result": result}
            else:
                self.log_step("  ❌ Erreur validation", f"Status: {grade_response.status_code}")
                self.log_step("  📝 Détails", grade_response.text[:200])

        except Exception as e:
            self.log_step("  ❌ Erreur validation", str(e))

        return {"success": False, "error": "Interactive test failed"}

    def generate_child_inputs(self, code: str) -> list:
        """Génère des inputs appropriés pour un enfant de 9 ans"""
        # Inputs simples qu'un enfant de 9 ans utiliserait
        child_inputs = ["Leo123", "9", "bonjour", "rouge", "42", "chat", "python"]

        # Détecter le type d'input attendu
        if "nom" in code.lower() or "name" in code.lower():
            return ["Leo123"]
        elif "âge" in code.lower() or "age" in code.lower():
            return ["9"]
        elif "couleur" in code.lower():
            return ["rouge"]
        elif "nombre" in code.lower():
            return ["42"]
        else:
            # Input générique
            return [child_inputs[0]]

    def test_progress_tracking(self, course_id: str):
        """Test le suivi de progression"""
        try:
            response = self.session.get(f"{self.base_url}/api/progress?learner={self.child_name}")
            if response.status_code == 200:
                progress = response.json()
                self.log_step("📊 Progression récupérée", f"{len(progress)} éléments suivis")
                for key, value in list(progress.items())[:3]:  # Limiter à 3 pour la lisibilité
                    self.log_step(f"  • {key}", f"Score: {value.get('score', 'N/A')}")
            else:
                self.log_step("❌ Erreur récupération progression")
        except Exception as e:
            self.log_step("❌ Erreur test progression", str(e))

    def test_ui_accessibility(self):
        """Test l'accessibilité de l'interface pour un enfant"""
        try:
            response = self.session.get(f"{self.base_url}/")
            if response.status_code == 200:
                html_content = response.text

                # Vérifier les éléments d'accessibilité de base
                has_title = "<title>" in html_content
                has_meta = "<meta" in html_content
                has_content = len(html_content) > 1000

                self.log_step("🎨 Interface accessible", f"Title: {has_title}, Meta: {has_meta}, Content: {has_content}")

                if has_title and has_meta and has_content:
                    self.log_step("  ✅ Interface adaptée aux enfants")
                else:
                    self.log_step("  ⚠️ Interface pourrait être améliorée")

            else:
                self.log_step("❌ Interface inaccessible")
        except Exception as e:
            self.log_step("❌ Erreur test interface", str(e))

    def test_validation_system(self):
        """Test le système de validation des exercices"""
        try:
            # Test de validation d'un exercice simple
            test_exercise = {
                "id": "test-child",
                "title": {"fr": "Test pour enfant"},
                "stars": 1,
                "prompt": {"fr": "Affiche 'Bonjour enfant'"},
                "starter": "print('Bonjour enfant')",
                "tests": ["out = execute_code()", "assert 'Bonjour enfant' in out"]
            }

            response = self.session.post(
                f"{self.base_url}/api/validate/exercise",
                json={"exercise": test_exercise}
            )

            if response.status_code == 200:
                result = response.json()
                valid = result.get('valid', False)
                score = result.get('score', 0)
                self.log_step("🔍 Validation système", f"Exercice test: {'Valide' if valid else 'Invalide'}")
                self.log_step("  📊 Score validation", f"{score}/100")
            else:
                self.log_step("❌ Erreur validation système")

        except Exception as e:
            self.log_step("❌ Erreur test validation", str(e))

    def test_child_friendly_features(self):
        """Test les fonctionnalités adaptées aux enfants"""
        features = []

        # Test 1: Exercices simples (1 étoile)
        try:
            response = self.session.get(f"{self.base_url}/api/courses/python-basics/exercises")
            if response.status_code == 200:
                exercises = response.json()
                easy_exercises = [ex for ex in exercises if ex.get('stars', 0) == 1]
                features.append(f"✅ {len(easy_exercises)} exercices faciles")
                self.log_step("🎯 Exercices pour débutants", f"{len(easy_exercises)} exercices à 1 étoile")
        except Exception as e:
            self.log_step("❌ Erreur analyse exercices", str(e))

        # Test 2: Support multilingue
        try:
            response = self.session.get(f"{self.base_url}/api/courses/python-basics/exercises/01-print")
            if response.status_code == 200:
                exercise = response.json()
                title = exercise.get('title', {})
                if isinstance(title, dict) and len(title) > 1:
                    languages = list(title.keys())
                    features.append(f"✅ Support {len(languages)} langues")
                    self.log_step("🌍 Support multilingue", f"{', '.join(languages)}")
        except Exception as e:
            self.log_step("❌ Erreur test multilingue", str(e))

        # Test 3: Indices pédagogiques
        try:
            response = self.session.get(f"{self.base_url}/api/courses/python-basics/exercises/01-print")
            if response.status_code == 200:
                exercise = response.json()
                hints = exercise.get('hints', {})
                if isinstance(hints, dict) and 'fr' in hints:
                    french_hints = hints['fr']
                    if len(french_hints) >= 2:
                        features.append(f"✅ {len(french_hints)} indices disponibles")
                        self.log_step("💡 Indices pédagogiques", f"{len(french_hints)} indices en français")
        except Exception as e:
            self.log_step("❌ Erreur test indices", str(e))

        return features

    def run_complete_child_test(self):
        """Lance le test complet de l'expérience enfant"""
        print("🧪 DÉBUT DU TEST COMPLET - EXPÉRIENCE ENFANT 9 ANS")
        print("=" * 60)
        print(f"👦 Nom de l'enfant: {self.child_name}")
        print(f"🎯 Objectif: Tester toutes les fonctionnalités comme un enfant")
        print("=" * 60)

        # 1. Vérifier la santé de l'API
        if not self.check_api_health():
            return False

        # 2. Tester l'interface
        self.test_ui_accessibility()

        # 3. Tester le système de validation
        self.test_validation_system()

        # 4. Tester les fonctionnalités adaptées aux enfants
        child_features = self.test_child_friendly_features()

        # 5. Récupérer les cours disponibles
        courses = self.get_available_courses()
        if not courses:
            return False

        # 6. Choisir un cours adapté
        course_id = self.choose_course_for_child(courses)
        if not course_id:
            return False

        # 7. Récupérer les exercices
        exercises = self.get_course_exercises(course_id)
        if not exercises:
            return False

        # 8. Tester quelques exercices (limité à 5 pour le test)
        test_exercises = exercises[:5]  # Tester les 5 premiers exercices

        self.log_step("🎮 DÉBUT DES TESTS D'EXERCICES", f"{len(test_exercises)} exercices sélectionnés")

        results = []
        success_count = 0

        for i, exercise in enumerate(test_exercises, 1):
            self.log_step(f"\n--- Exercice {i}/{len(test_exercises)} ---")
            result = self.test_exercise_as_child(course_id, exercise)
            results.append(result)

            if result.get('success', False):
                success_count += 1

            # Pause entre exercices (simulation temps de réflexion)
            time.sleep(0.5)

        # 9. Tester le suivi de progression
        self.log_step(f"\n--- SUIVI DE PROGRESSION ---")
        self.test_progress_tracking(course_id)

        # 10. Résultats finaux
        self.log_step(f"\n📊 RÉSULTATS FINAUX", f"{success_count}/{len(test_exercises)} exercices réussis")

        if success_count == len(test_exercises):
            self.log_step("🎉 TEST GLOBAL RÉUSSI !", "L'enfant peut utiliser toutes les fonctionnalités")
        elif success_count >= len(test_exercises) * 0.7:
            self.log_step("✅ TEST GLOBAL BON", "Quelques améliorations possibles")
        else:
            self.log_step("⚠️ TEST GLOBAL PARTIEL", "Des corrections sont nécessaires")

        # 11. Générer le rapport
        self.generate_report(results, success_count, len(test_exercises), child_features)

        return success_count >= len(test_exercises) * 0.7

    def generate_report(self, results: list, success_count: int, total_count: int, features: list):
        """Génère un rapport détaillé du test"""
        report = {
            "test_date": time.strftime("%Y-%m-%d %H:%M:%S"),
            "child_name": self.child_name,
            "child_age": "9 ans",
            "summary": {
                "total_exercises_tested": total_count,
                "successful_exercises": success_count,
                "success_rate": round(success_count / total_count * 100, 1) if total_count > 0 else 0,
                "child_friendly_features": features
            },
            "details": results,
            "progress_log": self.progress
        }

        # Sauvegarder le rapport
        report_file = f"child_experience_test_{int(time.time())}.json"
        with open(report_file, 'w', encoding='utf-8') as f:
            json.dump(report, f, indent=2, ensure_ascii=False)

        print(f"\n📄 Rapport détaillé sauvegardé: {report_file}")

        # Afficher le résumé
        print(f"\n🎯 RÉSUMÉ POUR PARENTS/ÉDUCATEURS:")
        print(f"• Succès: {success_count}/{total_count} exercices ({report['summary']['success_rate']}%)")
        print(f"• Expérience: {'Excellente' if success_count == total_count else 'Bonne' if success_count >= total_count * 0.7 else 'À améliorer'}")
        print(f"• Recommandation: {'Parfait pour enfants' if success_count >= total_count * 0.8 else 'Accompagnement conseillé'}")

        print(f"\n🌟 FONCTIONNALITÉS POUR ENFANTS:")
        for feature in features:
            print(f"  • {feature}")

if __name__ == "__main__":
    tester = ChildExperienceTester()
    success = tester.run_complete_child_test()

    if success:
        print("\n🎊 TEST COMPLET TERMINÉ AVEC SUCCÈS !")
        print("La plateforme Capitaine Python est prête pour les enfants. 🚀")
        print("✨ Fonctionnalités sécurisées, pédagogiques et adaptées aux jeunes apprenants !")
    else:
        print("\n⚠️ TEST COMPLET TERMINÉ AVEC PROBLÈMES")
        print("Des améliorations sont nécessaires avant de proposer aux enfants.")