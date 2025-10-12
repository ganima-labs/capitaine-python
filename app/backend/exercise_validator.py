#!/usr/bin/env python3
"""
Validateur d'exercices automatisé pour Capitaine Python
Vérifie la qualité, cohérence et sécurité des exercices
"""

import re
import json
from typing import Dict, List, Any, Optional, Tuple
from dataclasses import dataclass
from enum import Enum

class ValidationLevel(Enum):
    """Niveaux de validation"""
    ERROR = "error"      # Bloquant - doit être corrigé
    WARNING = "warning"  # Important - devrait être corrigé
    INFO = "info"        # Suggestion - amélioration possible

@dataclass
class ValidationIssue:
    """Issue détectée lors de la validation"""
    level: ValidationLevel
    category: str
    message: str
    suggestion: Optional[str] = None
    line: Optional[int] = None
    exercise_id: Optional[str] = None

class ExerciseValidator:
    """Validateur complet pour les exercices Python"""

    def __init__(self):
        self.issues: List[ValidationIssue] = []

        # Patterns de code à valider
        self.dangerous_patterns = [
            (r'\bexec\s*\(', "Utilisation de exec() - dangereux"),
            (r'\beval\s*\(', "Utilisation de eval() - dangereux"),
            (r'\b__import__\s*\(', "Utilisation de __import__() - non recommandé"),
            (r'\bos\.system\s*\(', "Utilisation de os.system() - dangereux"),
            (r'\bsubprocess\.call\s*\(', "Utilisation de subprocess.call() - vérifier la sécurité"),
            (r'\bopen\s*\(["\']?[/\\]', "Accès au système de fichiers - vérifier la sécurité"),
        ]

        # Patterns de code suspects
        self.suspicious_patterns = [
            (r'\bglobals\s*\(\)', "Utilisation de globals() - vérifier l'usage"),
            (r'\blocals\s*\(\)', "Utilisation de locals() - vérifier l'usage"),
            (r'\bvars\s*\(\)', "Utilisation de vars() - vérifier l'usage"),
            (r'\bgetattr\s*\(', "Utilisation de getattr() - vérifier la sécurité"),
            (r'\bsetattr\s*\(', "Utilisation de setattr() - vérifier la sécurité"),
            (r'\bdelattr\s*\(', "Utilisation de delattr() - vérifier la sécurité"),
        ]

        # Modules interdits
        self.forbidden_modules = [
            'os', 'sys', 'subprocess', 'shutil', 'glob', 'pickle', 'marshal',
            'socket', 'urllib', 'requests', 'ftplib', 'smtplib', 'telnetlib',
            'threading', 'multiprocessing', 'ctypes', 'importlib'
        ]

        # Fonctions Python à surveiller
        self.input_functions = ['input', 'raw_input']
        self.output_functions = ['print', 'sys.stdout.write']
        self.file_functions = ['open', 'file', 'with open']

    def validate_exercise(self, exercise: Dict[str, Any], strict_mode: bool = False) -> Dict[str, Any]:
        """
        Valide un exercice complet

        Args:
            exercise: Dictionnaire représentant l'exercice
            strict_mode: Si True, les warnings sont traités comme des erreurs

        Returns:
            Dict avec résultat de validation
        """
        self.issues = []
        exercise_id = exercise.get('id', 'unknown')

        # Validation structurelle
        self._validate_structure(exercise, exercise_id)

        # Validation du code starter
        self._validate_starter_code(exercise, exercise_id)

        # Validation des tests
        self._validate_tests(exercise, exercise_id)

        # Validation de la cohérence
        self._validate_consistency(exercise, exercise_id)

        # Validation pédagogique
        self._validate_pedagogy(exercise, exercise_id)

        # Validation de sécurité
        self._validate_security(exercise, exercise_id)

        # Validation multilingue (si applicable)
        self._validate_multilingual(exercise, exercise_id)

        # Compter les issues par niveau
        error_count = sum(1 for issue in self.issues if issue.level == ValidationLevel.ERROR)
        warning_count = sum(1 for issue in self.issues if issue.level == ValidationLevel.WARNING)
        info_count = sum(1 for issue in self.issues if issue.level == ValidationLevel.INFO)

        # En mode strict, les warnings deviennent des erreurs
        if strict_mode:
            error_count += warning_count
            warning_count = 0

        is_valid = error_count == 0

        return {
            'valid': is_valid,
            'exercise_id': exercise_id,
            'score': self._calculate_quality_score(),
            'error_count': error_count,
            'warning_count': warning_count,
            'info_count': info_count,
            'issues': [self._serialize_issue(issue) for issue in self.issues],
            'summary': self._generate_summary(exercise_id),
            'recommendations': self._generate_recommendations(exercise_id)
        }

    def _validate_structure(self, exercise: Dict[str, Any], exercise_id: str):
        """Valide la structure de base d'un exercice"""
        required_fields = ['id', 'title', 'stars', 'prompt']

        for field in required_fields:
            if field not in exercise:
                self.issues.append(ValidationIssue(
                    level=ValidationLevel.ERROR,
                    category='structure',
                    message=f"Champ obligatoire manquant: '{field}'",
                    suggestion=f"Ajouter le champ '{field}' à l'exercice",
                    exercise_id=exercise_id
                ))

        # Validation des types
        if 'stars' in exercise and not isinstance(exercise['stars'], int):
            self.issues.append(ValidationIssue(
                level=ValidationLevel.ERROR,
                category='structure',
                message="Le champ 'stars' doit être un entier",
                suggestion="Changer la valeur de 'stars' en entier (1, 2 ou 3)",
                exercise_id=exercise_id
            ))

        if 'stars' in exercise and exercise['stars'] not in [1, 2, 3]:
            self.issues.append(ValidationIssue(
                level=ValidationLevel.WARNING,
                category='structure',
                message="La difficulté devrait être 1, 2 ou 3 étoiles",
                suggestion="Utiliser 1 (facile), 2 (moyen) ou 3 (difficile)",
                exercise_id=exercise_id
            ))

    def _validate_starter_code(self, exercise: Dict[str, Any], exercise_id: str):
        """Valide le code starter"""
        starter = exercise.get('starter')
        if not starter:
            self.issues.append(ValidationIssue(
                level=ValidationLevel.ERROR,
                category='code',
                message="Code starter manquant",
                suggestion="Ajouter un code starter pour guider l'apprenant",
                exercise_id=exercise_id
            ))
            return

        # Gérer le cas multilingue
        starter_codes = []
        if isinstance(starter, dict):
            starter_codes = [(lang, code) for lang, code in starter.items() if code]
        elif isinstance(starter, str):
            starter_codes = [('default', starter)]

        for lang, code in starter_codes:
            self._validate_code_content(code, exercise_id, f'starter[{lang}]')

            # Vérifier la longueur du code
            lines = code.splitlines()
            if len(lines) > 20:
                self.issues.append(ValidationIssue(
                    level=ValidationLevel.WARNING,
                    category='pedagogy',
                    message=f"Code starter trop long ({len(lines)} lignes)",
                    suggestion="Réduire le code starter à < 20 lignes pour rester accessible",
                    exercise_id=exercise_id
                ))

            # Vérifier la complexité cyclomatique
            complexity = self._calculate_complexity(code)
            if complexity > 10:
                self.issues.append(ValidationIssue(
                    level=ValidationLevel.WARNING,
                    category='pedagogy',
                    message=f"Code trop complexe (complexité: {complexity})",
                    suggestion="Simplifier le code ou le diviser en étapes",
                    exercise_id=exercise_id
                ))

    def _validate_tests(self, exercise: Dict[str, Any], exercise_id: str):
        """Valide les tests de l'exercice"""
        tests = exercise.get('tests', [])
        if not tests:
            self.issues.append(ValidationIssue(
                level=ValidationLevel.ERROR,
                category='tests',
                message="Aucun test défini",
                suggestion="Ajouter des tests pour valider la solution de l'apprenant",
                exercise_id=exercise_id
            ))
            return

        # Vérifier chaque test
        for i, test in enumerate(tests):
            if not isinstance(test, str):
                self.issues.append(ValidationIssue(
                    level=ValidationLevel.ERROR,
                    category='tests',
                    message=f"Test {i+1} invalide (doit être une chaîne)",
                    suggestion="Convertir le test en chaîne de caractères",
                    exercise_id=exercise_id
                ))
                continue

            self._validate_test_code(test, exercise_id, f'test[{i+1}]')

        # Vérifier la cohérence avec le starter
        self._validate_test_starter_consistency(exercise, exercise_id)

    def _validate_consistency(self, exercise: Dict[str, Any], exercise_id: str):
        """Valide la cohérence interne de l'exercice"""
        starter = exercise.get('starter')
        tests = exercise.get('tests', [])

        if not starter or not tests:
            return

        # Extraire le code starter (gestion multilingue)
        starter_code = None
        if isinstance(starter, dict):
            starter_code = starter.get('fr') or starter.get('en') or next(iter(starter.values()))
        elif isinstance(starter, str):
            starter_code = starter

        if not starter_code:
            return

        # Vérifier la cohérence input/run_with_input
        has_input = self._has_input_function(starter_code)
        uses_run_with_input = any('run_with_input' in test for test in tests)
        uses_execute_code = any('execute_code' in test for test in tests)

        if has_input and not uses_run_with_input:
            self.issues.append(ValidationIssue(
                level=ValidationLevel.WARNING,
                category='consistency',
                message="Le code utilise input() mais les tests n'utilisent pas run_with_input()",
                suggestion="Utiliser run_with_input() dans les tests ou utiliser execute_code()",
                exercise_id=exercise_id
            ))
        elif not has_input and uses_run_with_input:
            self.issues.append(ValidationIssue(
                level=ValidationLevel.ERROR,
                category='consistency',
                message="Les tests utilisent run_with_input() mais le code n'a pas de input()",
                suggestion="Remplacer run_with_input() par execute_code() dans les tests",
                exercise_id=exercise_id
            ))
        elif not has_input and not uses_execute_code and not uses_run_with_input:
            self.issues.append(ValidationIssue(
                level=ValidationLevel.WARNING,
                category='consistency',
                message="Tests sans fonction d'exécution claire (run_with_input ou execute_code)",
                suggestion="Ajouter execute_code() ou run_with_input() dans les tests",
                exercise_id=exercise_id
            ))

    def _validate_pedagogy(self, exercise: Dict[str, Any], exercise_id: str):
        """Valide les aspects pédagogiques de l'exercice"""
        # Vérifier la présence d'indices
        hints = exercise.get('hints', [])
        if not hints:
            self.issues.append(ValidationIssue(
                level=ValidationLevel.INFO,
                category='pedagogy',
                message="Aucun indice fourni",
                suggestion="Ajouter des indices pour aider les apprenants bloqués",
                exercise_id=exercise_id
            ))
        elif len(hints) < 2:
            self.issues.append(ValidationIssue(
                level=ValidationLevel.INFO,
                category='pedagogy',
                message="Peu d'indices disponibles",
                suggestion="Ajouter 2-3 indices pour un meilleur accompagnement",
                exercise_id=exercise_id
            ))

        # Vérifier la qualité du prompt
        prompt = exercise.get('prompt', '')
        if isinstance(prompt, dict):
            # Vérifier chaque langue
            for lang, text in prompt.items():
                self._validate_prompt_quality(text, exercise_id, f'prompt[{lang}]')
        elif isinstance(prompt, str):
            self._validate_prompt_quality(prompt, exercise_id, 'prompt')

        # Vérifier la présence de solution_explanation
        if 'solution_explanation' not in exercise:
            self.issues.append(ValidationIssue(
                level=ValidationLevel.INFO,
                category='pedagogy',
                message="Explication de solution manquante",
                suggestion="Ajouter 'solution_explanation' pour expliquer la solution",
                exercise_id=exercise_id
            ))

    def _validate_security(self, exercise: Dict[str, Any], exercise_id: str):
        """Valide la sécurité du code"""
        starter = exercise.get('starter')
        tests = exercise.get('tests', [])

        # Valider le starter
        if isinstance(starter, dict):
            for lang, code in starter.items():
                self._validate_code_security(code, exercise_id, f'starter[{lang}]')
        elif isinstance(starter, str):
            self._validate_code_security(starter, exercise_id, 'starter')

        # Valider les tests
        for i, test in enumerate(tests):
            self._validate_code_security(test, exercise_id, f'test[{i+1}]')

    def _validate_multilingual(self, exercise: Dict[str, Any], exercise_id: str):
        """Valide la cohérence multilingue"""
        fields_to_check = ['title', 'prompt', 'hints', 'starter', 'solution_explanation']

        for field in fields_to_check:
            value = exercise.get(field)
            if value and isinstance(value, dict):
                # Vérifier que le français est présent
                if 'fr' not in value:
                    self.issues.append(ValidationIssue(
                        level=ValidationLevel.WARNING,
                        category='multilingual',
                        message=f"Le champ '{field}' n'a pas de version française",
                        suggestion="Ajouter la version française ('fr')",
                        exercise_id=exercise_id
                    ))

                # Vérifier la cohérence des longueurs
                lengths = [len(str(v)) for v in value.values() if v]
                if len(lengths) > 1:
                    max_len = max(lengths)
                    min_len = min(lengths)
                    if max_len > min_len * 3:
                        self.issues.append(ValidationIssue(
                            level=ValidationLevel.INFO,
                            category='multilingual',
                            message=f"Grande différence de longueur dans '{field}' entre langues",
                            suggestion="Vérifier que toutes les langues ont un contenu équilibré",
                            exercise_id=exercise_id
                        ))

    def _validate_code_content(self, code: str, exercise_id: str, context: str):
        """Valide le contenu d'un code"""
        lines = code.splitlines()

        # Vérifier les lignes vides au début/fin
        if lines and not lines[0].strip():
            self.issues.append(ValidationIssue(
                level=ValidationLevel.INFO,
                category='style',
                message=f"Ligne vide au début du code dans {context}",
                suggestion="Supprimer les lignes vides au début",
                exercise_id=exercise_id
            ))

        if lines and not lines[-1].strip():
            self.issues.append(ValidationIssue(
                level=ValidationLevel.INFO,
                category='style',
                message=f"Ligne vide à la fin du code dans {context}",
                suggestion="Supprimer les lignes vides à la fin",
                exercise_id=exercise_id
            ))

        # Vérifier l'indentation
        self._validate_indentation(code, exercise_id, context)

    def _validate_test_code(self, test: str, exercise_id: str, context: str):
        """Valide le code d'un test"""
        # Vérifier que le test est exécutable
        if not any(keyword in test for keyword in ['assert', 'print', 'return', 'run_with_input', 'execute_code']):
            self.issues.append(ValidationIssue(
                level=ValidationLevel.WARNING,
                category='tests',
                message=f"Test sans assertion ou sortie dans {context}",
                suggestion="Ajouter assert(), print() ou une fonction d'exécution",
                exercise_id=exercise_id
            ))

        # Vérifier les assertions
        if 'assert' in test:
            # Compter les assertions
            assert_count = test.count('assert')
            if assert_count == 0:
                self.issues.append(ValidationIssue(
                    level=ValidationLevel.WARNING,
                    category='tests',
                    message=f"Pas d'assertion dans le test {context}",
                    suggestion="Ajouter des assertions pour valider le résultat",
                    exercise_id=exercise_id
                ))
            elif assert_count > 5:
                self.issues.append(ValidationIssue(
                    level=ValidationLevel.INFO,
                    category='tests',
                    message=f"Beaucoup d'assertions ({assert_count}) dans {context}",
                    suggestion="Considérer diviser en plusieurs tests ou simplifier",
                    exercise_id=exercise_id
                ))

    def _validate_test_starter_consistency(self, exercise: Dict[str, Any], exercise_id: str):
        """Valide la cohérence entre tests et starter"""
        # Vérifier que les tests référencent bien les fonctions définies dans le starter
        starter = exercise.get('starter')
        tests = exercise.get('tests', [])

        if not starter or not tests:
            return

        # Extraire les fonctions du starter
        starter_code = None
        if isinstance(starter, dict):
            starter_code = starter.get('fr') or starter.get('en') or next(iter(starter.values()))
        elif isinstance(starter, str):
            starter_code = starter

        if not starter_code:
            return

        # Trouver les fonctions définies
        function_pattern = r'def\s+([a-zA-Z_][a-zA-Z0-9_]*)\s*\('
        defined_functions = re.findall(function_pattern, starter_code)

        # Vérifier que les tests utilisent bien ces fonctions
        for test in tests:
            for func in defined_functions:
                if func in test and f"ns['{func}']" not in test:
                    self.issues.append(ValidationIssue(
                        level=ValidationLevel.WARNING,
                        category='consistency',
                        message=f"Fonction '{func}' utilisée dans les tests mais pas avec ns['{func}']",
                        suggestion=f"Utiliser ns['{func}']() pour accéder à la fonction",
                        exercise_id=exercise_id
                    ))

    def _validate_prompt_quality(self, prompt: str, exercise_id: str, context: str):
        """Valide la qualité d'un prompt"""
        if len(prompt) < 20:
            self.issues.append(ValidationIssue(
                level=ValidationLevel.WARNING,
                category='pedagogy',
                message=f"Prompt trop court dans {context} ({len(prompt)} caractères)",
                suggestion="Développer le prompt pour mieux guider l'apprenant",
                exercise_id=exercise_id
            ))
        elif len(prompt) > 500:
            self.issues.append(ValidationIssue(
                level=ValidationLevel.INFO,
                category='pedagogy',
                message=f"Prompt très long dans {context} ({len(prompt)} caractères)",
                suggestion="Considérer raccourcir le prompt pour rester accessible",
                exercise_id=exercise_id
            ))

        # Vérifier la présence d'instructions claires
        if not any(word in prompt.lower() for word in ['écris', 'crée', 'définis', 'implémente', 'affiche', 'calcule', 'retourne']):
            self.issues.append(ValidationIssue(
                level=ValidationLevel.INFO,
                category='pedagogy',
                message=f"Prompt sans verbe d'action clair dans {context}",
                suggestion="Ajouter un verbe d'action (écris, crée, affiche...)",
                exercise_id=exercise_id
            ))

    def _validate_code_security(self, code: str, exercise_id: str, context: str):
        """Valide la sécurité du code"""
        # Vérifier les patterns dangereux
        for pattern, message in self.dangerous_patterns:
            if re.search(pattern, code, re.IGNORECASE):
                self.issues.append(ValidationIssue(
                    level=ValidationLevel.ERROR,
                    category='security',
                    message=f"{message} dans {context}",
                    suggestion="Supprimer ou remplacer par une alternative plus sûre",
                    exercise_id=exercise_id
                ))

        # Vérifier les patterns suspects
        for pattern, message in self.suspicious_patterns:
            if re.search(pattern, code, re.IGNORECASE):
                self.issues.append(ValidationIssue(
                    level=ValidationLevel.WARNING,
                    category='security',
                    message=f"{message} dans {context}",
                    suggestion="Vérifier que l'usage est légitime et sécurisé",
                    exercise_id=exercise_id
                ))

        # Vérifier les imports interdits
        import_pattern = r'import\s+([a-zA-Z_][a-zA-Z0-9_]*)|from\s+([a-zA-Z_][a-zA-Z0-9_]*)\s+import'
        matches = re.finditer(import_pattern, code, re.IGNORECASE)
        for match in matches:
            module = match.group(1) or match.group(2)
            if module in self.forbidden_modules:
                self.issues.append(ValidationIssue(
                    level=ValidationLevel.ERROR,
                    category='security',
                    message=f"Import de module interdit '{module}' dans {context}",
                    suggestion=f"Supprimer l'import de {module} ou utiliser une alternative",
                    exercise_id=exercise_id
                ))

    def _validate_indentation(self, code: str, exercise_id: str, context: str):
        """Valide l'indentation du code"""
        lines = code.splitlines()
        for i, line in enumerate(lines, 1):
            if line.strip():  # Ignorer les lignes vides
                # Vérifier l'indentation cohérente
                if line.startswith(' ') and line.startswith('\t'):
                    self.issues.append(ValidationIssue(
                        level=ValidationLevel.WARNING,
                        category='style',
                        message=f"Mélange d'espaces et tabulations ligne {i} dans {context}",
                        suggestion="Utiliser uniquement des espaces ou uniquement des tabulations",
                        exercise_id=exercise_id,
                        line=i
                    ))
                    break

    def _has_input_function(self, code: str) -> bool:
        """Détecte si le code contient un appel à input()"""
        if not code or not isinstance(code, str):
            return False

        # Supprimer les commentaires pour éviter les faux positifs
        code_without_comments = re.sub(r'#.*$', '', code, flags=re.MULTILINE)

        # Rechercher les appels à input()
        return bool(re.search(r'\binput\s*\(', code_without_comments))

    def _calculate_complexity(self, code: str) -> int:
        """Calcule la complexité cyclomatique approximative"""
        # Compte les structures de contrôle
        patterns = [
            r'\bif\s+',
            r'\belif\s+',
            r'\bwhile\s+',
            r'\bfor\s+',
            r'\bexcept\s+',
            r'\belif\s+',
            r'\band\b',
            r'\bor\b'
        ]

        complexity = 1  # Base
        for pattern in patterns:
            complexity += len(re.findall(pattern, code))

        return complexity

    def _calculate_quality_score(self) -> int:
        """Calcule un score de qualité sur 100"""
        if not self.issues:
            return 100

        # Pondération des issues
        score = 100
        for issue in self.issues:
            if issue.level == ValidationLevel.ERROR:
                score -= 20
            elif issue.level == ValidationLevel.WARNING:
                score -= 10
            elif issue.level == ValidationLevel.INFO:
                score -= 5

        return max(0, score)

    def _serialize_issue(self, issue: ValidationIssue) -> Dict[str, Any]:
        """Sérialise une issue pour la sortie JSON"""
        return {
            'level': issue.level.value,
            'category': issue.category,
            'message': issue.message,
            'suggestion': issue.suggestion,
            'line': issue.line,
            'exercise_id': issue.exercise_id
        }

    def _generate_summary(self, exercise_id: str) -> str:
        """Génère un résumé de la validation"""
        if not self.issues:
            return f"✅ Exercice {exercise_id} est parfaitement valide !"

        error_count = sum(1 for issue in self.issues if issue.level == ValidationLevel.ERROR)
        warning_count = sum(1 for issue in self.issues if issue.level == ValidationLevel.WARNING)
        info_count = sum(1 for issue in self.issues if issue.level == ValidationLevel.INFO)

        summary_parts = []
        if error_count > 0:
            summary_parts.append(f"{error_count} erreur(s)")
        if warning_count > 0:
            summary_parts.append(f"{warning_count} avertissement(s)")
        if info_count > 0:
            summary_parts.append(f"{info_count} suggestion(s)")

        return f"📊 Exercice {exercise_id}: {', '.join(summary_parts)}"

    def _generate_recommendations(self, exercise_id: str) -> List[str]:
        """Génère des recommandations d'amélioration"""
        recommendations = []

        # Regrouper les issues par catégorie
        categories = {}
        for issue in self.issues:
            if issue.category not in categories:
                categories[issue.category] = []
            categories[issue.category].append(issue)

        # Générer des recommandations par catégorie
        if 'security' in categories:
            recommendations.append("🔒 **Sécurité**: Corriger les problèmes de sécurité avant de déployer l'exercice")

        if 'structure' in categories:
            recommendations.append("📋 **Structure**: Compléter les champs obligatoires de l'exercice")

        if 'tests' in categories:
            recommendations.append("🧪 **Tests**: Améliorer la couverture et la qualité des tests")

        if 'pedagogy' in categories:
            recommendations.append("📚 **Pédagogie**: Enrichir le contenu pédagogique pour mieux guider les apprenants")

        if 'consistency' in categories:
            recommendations.append("🔄 **Cohérence**: Assurer la cohérence entre le code et les tests")

        if 'style' in categories:
            recommendations.append("🎨 **Style**: Améliorer le style et la lisibilité du code")

        return recommendations

# Fonctions utilitaires pour usage externe
def validate_exercise(exercise: Dict[str, Any], strict_mode: bool = False) -> Dict[str, Any]:
    """Fonction pratique pour valider un exercice"""
    validator = ExerciseValidator()
    return validator.validate_exercise(exercise, strict_mode)

def validate_course(course_data: Dict[str, Any], strict_mode: bool = False) -> Dict[str, Any]:
    """Valide un cours complet avec tous ses exercices"""
    validator = ExerciseValidator()
    results = []

    exercises = course_data.get('exercises', [])
    if not exercises:
        return {
            'valid': False,
            'message': 'Aucun exercice dans le cours',
            'exercises': []
        }

    all_issues = []

    for exercise in exercises:
        result = validator.validate_exercise(exercise, strict_mode)
        results.append(result)
        all_issues.extend(result['issues'])

    # Statistiques globales
    error_count = sum(1 for issue in all_issues if issue['level'] == 'error')
    warning_count = sum(1 for issue in all_issues if issue['level'] == 'warning')
    info_count = sum(1 for issue in all_issues if issue['level'] == 'info')

    valid_exercises = sum(1 for result in results if result['valid'])
    avg_score = sum(result['score'] for result in results) / len(results) if results else 0

    return {
        'valid': error_count == 0,
        'course_id': course_data.get('meta', {}).get('id', 'unknown'),
        'total_exercises': len(exercises),
        'valid_exercises': valid_exercises,
        'average_score': round(avg_score, 1),
        'error_count': error_count,
        'warning_count': warning_count,
        'info_count': info_count,
        'exercises': results,
        'summary': f"📊 Cours: {valid_exercises}/{len(exercises)} exercices valides, score moyen: {avg_score:.1f}/100"
    }

if __name__ == "__main__":
    # Test rapide
    test_exercise = {
        "id": "test-exercise",
        "title": "Test Exercise",
        "stars": 2,
        "prompt": "Test exercise for validation",
        "starter": "print('Hello')",
        "tests": ["out = execute_code()", "assert 'Hello' in out"]
    }

    result = validate_exercise(test_exercise)
    print(json.dumps(result, indent=2, ensure_ascii=False))