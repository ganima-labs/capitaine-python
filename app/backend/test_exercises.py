"""
Tests unitaires pour le module exercises.py
Valide la structure des exercices et leur cohérence
"""

import pytest
import exercises


class TestExercisesStructure:
    """Tests pour la structure des exercices"""

    def test_exercises_is_list(self):
        """Test que EXERCISES est une liste"""
        assert isinstance(exercises.EXERCISES, list)
        assert len(exercises.EXERCISES) > 0

    def test_exercises_count(self):
        """Test le nombre d'exercices"""
        expected_count = 8  # Basé sur le code actuel
        assert len(exercises.EXERCISES) == expected_count

    def test_each_exercise_is_dict(self):
        """Test que chaque exercice est un dictionnaire"""
        for exercise in exercises.EXERCISES:
            assert isinstance(exercise, dict)

    def test_exercise_required_fields(self):
        """Test que chaque exercice a les champs requis"""
        required_fields = [
            "id", "title", "stars", "prompt", "starter",
            "solution_explanation", "tests", "hints"
        ]

        for exercise in exercises.EXERCISES:
            for field in required_fields:
                assert field in exercise, f"Exercise missing field: {field}"
                assert exercise[field] is not None, f"Exercise field {field} is None"

    def test_exercise_ids_unique(self):
        """Test que les IDs d'exercices sont uniques"""
        ids = [exercise["id"] for exercise in exercises.EXERCISES]
        assert len(ids) == len(set(ids)), "Exercise IDs must be unique"

    def test_exercise_ids_format(self):
        """Test le format des IDs d'exercices"""
        for exercise in exercises.EXERCISES:
            exercise_id = exercise["id"]
            assert isinstance(exercise_id, str)
            assert len(exercise_id) > 0
            # Les IDs doivent être alphanumériques avec tirets
            assert all(c.isalnum() or c == '-' for c in exercise_id)

    def test_exercise_titles_valid(self):
        """Test que les titres d'exercices sont valides"""
        for exercise in exercises.EXERCISES:
            title = exercise["title"]
            assert isinstance(title, str)
            assert len(title.strip()) > 0
            assert len(title) <= 100  # Titre raisonnable

    def test_exercise_stars_range(self):
        """Test que le nombre d'étoiles est dans la plage valide"""
        for exercise in exercises.EXERCISES:
            stars = exercise["stars"]
            assert isinstance(stars, int)
            assert 1 <= stars <= 5, "Stars must be between 1 and 5"

    def test_exercise_prompts_valid(self):
        """Test que les prompts sont valides"""
        for exercise in exercises.EXERCISES:
            prompt = exercise["prompt"]
            assert isinstance(prompt, str)
            assert len(prompt.strip()) > 0
            assert len(prompt) <= 1000  # Prompt raisonnable

    def test_exercise_starters_valid(self):
        """Test que les codes de départ sont valides"""
        for exercise in exercises.EXERCISES:
            starter = exercise["starter"]
            assert isinstance(starter, str)
            assert len(starter) >= 0  # Peut être vide
            # Le starter doit être du code Python syntaxiquement valide
            # (on ne teste pas la syntaxe ici car certains peuvent être incomplets)

    def test_exercise_solution_explanations_valid(self):
        """Test que les explications de solution sont valides"""
        for exercise in exercises.EXERCISES:
            explanation = exercise["solution_explanation"]
            assert isinstance(explanation, str)
            assert len(explanation.strip()) > 0
            assert len(explanation) <= 2000  # Explication raisonnable

    def test_exercise_tests_is_list(self):
        """Test que les tests sont des listes"""
        for exercise in exercises.EXERCISES:
            tests = exercise["tests"]
            assert isinstance(tests, list)
            assert len(tests) > 0, "Each exercise must have at least one test"

    def test_exercise_hints_is_list(self):
        """Test que les indices sont des listes"""
        for exercise in exercises.EXERCISES:
            hints = exercise["hints"]
            assert isinstance(hints, list)
            assert len(hints) > 0, "Each exercise must have at least one hint"

    def test_exercise_hints_valid(self):
        """Test que les indices sont valides"""
        for exercise in exercises.EXERCISES:
            for hint in exercise["hints"]:
                assert isinstance(hint, str)
                assert len(hint.strip()) > 0
                assert len(hint) <= 200  # Indices concis


class TestExercisesContent:
    """Tests pour le contenu des exercices"""

    def test_exercise_01_print_content(self):
        """Test contenu spécifique de l'exercice 01-print"""
        exercise = exercises.EXERCISES[0]
        assert exercise["id"] == "01-print"
        assert exercise["title"] == "Fais parler l'ordi"
        assert exercise["stars"] == 1
        assert "Salut Capitaine Python !" in exercise["prompt"]
        assert "print" in exercise["starter"].lower()
        assert len(exercise["tests"]) == 2
        assert "Salut Capitaine Python !" in exercise["tests"][1]

    def test_exercise_02_variables_content(self):
        """Test contenu spécifique de l'exercice 02-variables"""
        exercise = exercises.EXERCISES[1]
        assert exercise["id"] == "02-variables"
        assert exercise["title"] == "Trésor dans une variable"
        assert exercise["stars"] == 1
        assert "variable" in exercise["prompt"].lower()
        assert "Bonjour Hugo" in exercise["starter"]
        assert len(exercise["tests"]) == 2
        assert "Bonjour Hugo" in exercise["tests"][1]

    def test_exercise_03_conditions_content(self):
        """Test contenu spécifique de l'exercice 03-conditions"""
        exercise = exercises.EXERCISES[2]
        assert exercise["id"] == "03-conditions"
        assert exercise["title"] == "Feu rouge/vert"
        assert exercise["stars"] == 2
        assert "rouge" in exercise["prompt"] and "vert" in exercise["prompt"]
        assert "if" in exercise["starter"]
        assert len(exercise["tests"]) == 4
        assert any("STOP" in test for test in exercise["tests"])
        assert any("GO" in test for test in exercise["tests"])

    def test_exercise_04_boucle_for_content(self):
        """Test contenu spécifique de l'exercice 04-boucle-for"""
        exercise = exercises.EXERCISES[3]
        assert exercise["id"] == "04-boucle-for"
        assert exercise["title"] == "Compte 1 à 5"
        assert exercise["stars"] == 1
        assert "boucle" in exercise["prompt"].lower() or "for" in exercise["prompt"]
        assert "for" in exercise["starter"]
        assert "range" in exercise["starter"]
        assert len(exercise["tests"]) == 2

    def test_exercise_05_fonction_bonjour_content(self):
        """Test contenu spécifique de l'exercice 05-fonction-bonjour"""
        exercise = exercises.EXERCISES[4]
        assert exercise["id"] == "05-fonction-bonjour"
        assert exercise["title"] == "Dis Bonjour"
        assert exercise["stars"] == 2
        assert "fonction" in exercise["prompt"].lower()
        assert "def bonjour" in exercise["starter"]
        assert "return" in exercise["starter"]
        assert len(exercise["tests"]) == 3

    def test_exercise_06_somme_1_a_n_content(self):
        """Test contenu spécifique de l'exercice 06-somme-1-a-n"""
        exercise = exercises.EXERCISES[5]
        assert exercise["id"] == "06-somme-1-a-n"
        assert exercise["title"] == "Addition magique"
        assert exercise["stars"] == 2
        assert "somme" in exercise["prompt"].lower()
        assert "def somme" in exercise["starter"]
        assert "for" in exercise["starter"]
        assert len(exercise["tests"]) == 4

    def test_exercise_07_fizzbuzz_content(self):
        """Test contenu spécifique de l'exercice 07-fizzbuzz"""
        exercise = exercises.EXERCISES[6]
        assert exercise["id"] == "07-fizzbuzz"
        assert exercise["title"] == "FizzBuzz rigolo"
        assert exercise["stars"] == 3
        assert "fizzbuzz" in exercise["prompt"].lower()
        assert "def fizzbuzz" in exercise["starter"]
        assert "%" in exercise["starter"]  # Modulo
        assert len(exercise["tests"]) == 5

    def test_exercise_08_max_de_trois_content(self):
        """Test contenu spécifique de l'exercice 08-max-de-trois"""
        exercise = exercises.EXERCISES[7]
        assert exercise["id"] == "08-max-de-trois"
        assert exercise["title"] == "Le plus grand"
        assert exercise["stars"] == 2
        assert "max" in exercise["prompt"].lower() or "plus grand" in exercise["prompt"]
        assert "def max_de_trois" in exercise["starter"]
        assert len(exercise["tests"]) == 3


class TestExerciseTests:
    """Tests pour la validité des tests d'exercices"""

    def test_tests_syntax_validity(self):
        """Test que les tests ont une syntaxe Python valide"""
        import ast

        for exercise in exercises.EXERCISES:
            for test in exercise["tests"]:
                try:
                    # Vérifier que le test peut être parsé comme du Python
                    ast.parse(test)
                except SyntaxError as e:
                    pytest.fail(f"Invalid Python syntax in test for exercise {exercise['id']}: {test}\nError: {e}")

    def test_tests_use_functions(self):
        """Test que les tests utilisent les fonctions attendues"""
        # Exercise 05 - fonction bonjour
        bonjour_exercise = next(e for e in exercises.EXERCISES if e["id"] == "05-fonction-bonjour")
        test_code = "\n".join(bonjour_exercise["tests"])
        assert "ns['bonjour']" in test_code
        assert "assert" in test_code

        # Exercise 06 - fonction somme
        somme_exercise = next(e for e in exercises.EXERCISES if e["id"] == "06-somme-1-a-n")
        test_code = "\n".join(somme_exercise["tests"])
        assert "ns['somme']" in test_code
        assert "assert" in test_code

    def test_tests_use_run_with_input(self):
        """Test que les tests d'I/O utilisent run_with_input"""
        io_exercises = ["01-print", "02-variables", "03-conditions", "04-boucle-for"]

        for exercise in exercises.EXERCISES:
            if exercise["id"] in io_exercises:
                test_code = "\n".join(exercise["tests"])
                assert "run_with_input" in test_code, f"Exercise {exercise['id']} should use run_with_input"

    def test_tests_have_assertions(self):
        """Test que les tests contiennent des assertions"""
        for exercise in exercises.EXERCISES:
            test_code = "\n".join(exercise["tests"])
            assert "assert" in test_code, f"Exercise {exercise['id']} tests must contain assertions"

    def test_function_tests_check_existence(self):
        """Test que les tests de fonctions vérifient l'existence de la fonction"""
        function_exercises = ["05-fonction-bonjour", "06-somme-1-a-n", "07-fizzbuzz", "08-max-de-trois"]

        for exercise in exercises.EXERCISES:
            if exercise["id"] in function_exercises:
                test_code = "\n".join(exercise["tests"])
                assert "ns.get(" in test_code, f"Exercise {exercise['id']} should check function existence"


class TestExerciseStars:
    """Tests pour la cohérence du système d'étoiles"""

    def test_ex_stars_creation(self):
        """Test création de EX_STARS"""
        assert hasattr(exercises, 'EX_STARS')
        assert isinstance(exercises.EX_STARS, dict)

    def test_ex_stars_content(self):
        """Test contenu de EX_STARS"""
        expected_stars = {
            "01-print": 1,
            "02-variables": 1,
            "03-conditions": 2,
            "04-boucle-for": 1,
            "05-fonction-bonjour": 2,
            "06-somme-1-a-n": 2,
            "07-fizzbuzz": 3,
            "08-max-de-trois": 2,
        }

        for exercise_id, expected_star_count in expected_stars.items():
            assert exercise_id in exercises.EX_STARS
            assert exercises.EX_STARS[exercise_id] == expected_star_count

    def test_ex_stars_completeness(self):
        """Test que tous les exercices sont dans EX_STARS"""
        exercise_ids = {exercise["id"] for exercise in exercises.EXERCISES}
        stars_ids = set(exercises.EX_STARS.keys())
        assert exercise_ids == stars_ids, "EX_STARS should contain all exercise IDs"

    def test_ex_stars_consistency(self):
        """Test cohérence entre EXERCISES et EX_STARS"""
        for exercise in exercises.EXERCISES:
            exercise_id = exercise["id"]
            assert exercise_id in exercises.EX_STARS
            assert exercise["stars"] == exercises.EX_STARS[exercise_id]


class TestExerciseDifficultyProgression:
    """Tests pour la progression de difficulté"""

    def test_star_distribution(self):
        """Test distribution raisonnable des étoiles"""
        star_counts = {}
        for exercise in exercises.EXERCISES:
            stars = exercise["stars"]
            star_counts[stars] = star_counts.get(stars, 0) + 1

        # Vérifier qu'on a une distribution raisonnable
        assert star_counts.get(1, 0) >= 2, "Should have at least 2 one-star exercises"
        assert star_counts.get(2, 0) >= 2, "Should have at least 2 two-star exercises"
        assert star_counts.get(3, 0) >= 1, "Should have at least 1 three-star exercise"

    def test_exercise_ordering_by_difficulty(self):
        """Test que les exercices sont globalement ordonnés par difficulté"""
        # Vérifier qu'on n'a pas d'exercice 3 étoiles au début
        first_three = exercises.EXERCISES[:3]
        for exercise in first_three:
            assert exercise["stars"] <= 2, "First exercises should be easier (1-2 stars)"

    def test_concept_progression(self):
        """Test progression logique des concepts"""
        exercise_ids = [exercise["id"] for exercise in exercises.EXERCISES]

        # Vérifier ordre logique: print -> variables -> conditions -> loops -> functions
        concept_order = [
            "01-print",  # Sortie de base
            "02-variables",  # Variables
            "03-conditions",  # Conditions
            "04-boucle-for",  # Boucles
            "05-fonction-bonjour",  # Fonctions simples
        ]

        for i, expected_id in enumerate(concept_order):
            assert exercise_ids[i] == expected_id, f"Exercise {expected_id} should be at position {i}"


class TestExerciseEdgeCases:
    """Tests des cas limites pour les exercices"""

    def test_no_duplicate_titles(self):
        """Test qu'il n'y a pas de titres dupliqués"""
        titles = [exercise["title"] for exercise in exercises.EXERCISES]
        assert len(titles) == len(set(titles)), "Exercise titles must be unique"

    def test_exercise_ids_no_spaces(self):
        """Test que les IDs n'ont pas d'espaces"""
        for exercise in exercises.EXERCISES:
            exercise_id = exercise["id"]
            assert " " not in exercise_id, f"Exercise ID {exercise_id} should not contain spaces"

    def test_prompts_not_too_long(self):
        """Test que les prompts ne sont pas trop longs"""
        for exercise in exercises.EXERCISES:
            prompt = exercise["prompt"]
            assert len(prompt) <= 1000, f"Prompt for {exercise['id']} is too long: {len(prompt)} characters"

    def test_hints_not_too_many(self):
        """Test qu'il n'y a pas trop d'indices"""
        for exercise in exercises.EXERCISES:
            hints = exercise["hints"]
            assert len(hints) <= 5, f"Too many hints for exercise {exercise['id']}: {len(hints)}"

    def test_solutions_not_too_long(self):
        """Test que les solutions de départ ne sont pas trop longues"""
        for exercise in exercises.EXERCISES:
            starter = exercise["starter"]
            assert len(starter) <= 500, f"Starter code for {exercise['id']} is too long: {len(starter)} characters"

    def test_explanations_meaningful(self):
        """Test que les explications ne sont pas vides ou triviales"""
        for exercise in exercises.EXERCISES:
            explanation = exercise["solution_explanation"]
            assert len(explanation.strip()) >= 50, f"Explanation for {exercise['id']} should be meaningful"
            # Vérifier que l'explication n'est pas juste une répétition du prompt
            assert explanation != exercise["prompt"], f"Explanation for {exercise['id']} should differ from prompt"


class TestExerciseCodeQuality:
    """Tests pour la qualité du code dans les exercices"""

    def test_starter_code_syntax(self):
        """Test que le code de départ a une syntaxe Python valide"""
        import ast

        for exercise in exercises.EXERCISES:
            starter = exercise["starter"]
            if starter.strip():  # Skip empty starters
                try:
                    ast.parse(starter)
                except SyntaxError as e:
                    pytest.fail(f"Invalid Python syntax in starter for exercise {exercise['id']}: {starter}\nError: {e}")

    def test_starter_code_no_complex_logic(self):
        """Test que le code de départ n'est pas trop complexe"""
        for exercise in exercises.EXERCISES:
            starter = exercise["starter"]
            lines = [line.strip() for line in starter.split('\n') if line.strip()]
            # Le code de départ ne devrait pas avoir plus de 10 lignes significatives
            assert len(lines) <= 10, f"Starter code for {exercise['id']} is too complex: {len(lines)} lines"

    def test_tests_code_quality(self):
        """Test qualité du code des tests"""
        for exercise in exercises.EXERCISES:
            for test in exercise["tests"]:
                # Les tests ne devraient pas être trop longs
                assert len(test) <= 200, f"Test for {exercise['id']} is too long: {len(test)} characters"
                # Les tests ne devraient pas avoir de lignes vides au début/fin
                assert test == test.strip(), f"Test for {exercise['id']} should not have leading/trailing whitespace"


class TestExercisePedagogicalAspects:
    """Tests pour les aspects pédagogiques des exercices"""

    def test_exercise_pedagogical_titles(self):
        """Test que les titres sont pédagogiques et engageants"""
        for exercise in exercises.EXERCISES:
            title = exercise["title"]
            # Les titres devraient être courts, mémorables et engaging
            assert len(title) <= 30, f"Title {title} should be concise"
            # Pas de jargon technique trop complexe dans les titres
            assert not any(word in title.lower() for word in ["algorithm", "complexity", "optimization"])

    def test_exercise_progressive_hints(self):
        """Test que les indices sont progressifs"""
        for exercise in exercises.EXERCISES:
            hints = exercise["hints"]
            if len(hints) > 1:
                # Les indices devraient devenir de plus en plus spécifiques
                # C'est subjectif, mais on vérifie au moins qu'ils sont différents
                for i in range(len(hints) - 1):
                    assert hints[i] != hints[i + 1], f"Hints {i} and {i+1} for {exercise['id']} should be different"

    def test_explanation_age_appropriate(self):
        """Test que les explications sont adaptées aux débutants"""
        complex_terms = ["polymorphism", "inheritance", "encapsulation", "abstraction", "paradigm"]

        for exercise in exercises.EXERCISES:
            explanation = exercise["solution_explanation"].lower()
            for term in complex_terms:
                assert term not in explanation, f"Explanation for {exercise['id']} should not use complex term '{term}'"

    def test_concrete_examples_in_explanations(self):
        """Test que les explications contiennent des exemples concrets"""
        for exercise in exercises.EXERCISES:
            explanation = exercise["solution_explanation"]
            # Les explications devraient contenir des exemples ou analogies
            assert ("comme" in explanation or
                   "exemple" in explanation or
                   "par exemple" in explanation or
                   "c'est comme" in explanation), \
                f"Explanation for {exercise['id']} should contain concrete examples"


@pytest.mark.integration
class TestExercisesIntegration:
    """Tests d'intégration pour les exercices"""

    def test_exercises_completeness(self):
        """Test que l'ensemble des exercices couvre les concepts de base"""
        concepts = {
            "print": False,
            "variables": False,
            "input": False,
            "conditions": False,
            "loops": False,
            "functions": False,
            "lists": False,
        }

        for exercise in exercises.EXERCISES:
            # Analyser le contenu pour détecter les concepts
            content = f"{exercise['prompt']} {exercise['starter']} {exercise['solution_explanation']}".lower()

            if "print" in content:
                concepts["print"] = True
            if "variable" in content:
                concepts["variables"] = True
            if "input" in content:
                concepts["input"] = True
            if "if" in content or "condition" in content:
                concepts["conditions"] = True
            if "for" in content or "while" in content or "boucle" in content:
                concepts["loops"] = True
            if "def" in content or "function" in content or "fonction" in content:
                concepts["functions"] = True
            if "list" in content or "liste" in content or "[]" in exercise["starter"]:
                concepts["lists"] = True

        # Vérifier que les concepts fondamentaux sont couverts
        assert concepts["print"], "Should cover print statements"
        assert concepts["variables"], "Should cover variables"
        assert concepts["conditions"], "Should cover conditions"
        assert concepts["loops"], "Should cover loops"
        assert concepts["functions"], "Should cover functions"

    def test_exercises_star_map_consistency(self):
        """Test cohérence de la carte d'étoiles avec les exercices"""
        # Vérifier que chaque exercice a une entrée dans EX_STARS
        for exercise in exercises.EXERCISES:
            assert exercise["id"] in exercises.EX_STARS
            assert exercises.EX_STARS[exercise["id"]] == exercise["stars"]

        # Vérifier qu'il n'y a pas d'entrées supplémentaires
        assert len(exercises.EX_STARS) == len(exercises.EXERCISES)

    def test_exercises_export_format(self):
        """Test que les exercices peuvent être exportés/serialisés"""
        import json

        # Vérifier que tout peut être sérialisé en JSON
        try:
            json.dumps(exercises.EXERCISES)
            json.dumps(exercises.EX_STARS)
        except (TypeError, ValueError) as e:
            pytest.fail(f"Exercises should be JSON serializable: {e}")


@pytest.mark.unit
class TestExercisesPerformance:
    """Tests de performance pour les exercices"""

    def test_load_exercises_performance(self):
        """Test performance du chargement des exercices"""
        import time

        start_time = time.time()

        # Simuler plusieurs accès aux exercices
        for _ in range(100):
            exercises.EXERCISES
            exercises.EX_STARS

        end_time = time.time()

        # Doit être très rapide (< 0.1 seconde pour 100 accès)
        assert (end_time - start_time) < 0.1

    def test_search_exercises_performance(self):
        """Test performance de recherche d'exercices"""
        import time

        # Test recherche par ID
        start_time = time.time()

        for _ in range(1000):
            next((e for e in exercises.EXERCISES if e["id"] == "05-fonction-bonjour"), None)

        end_time = time.time()

        # Doit être rapide (< 0.05 seconde pour 1000 recherches)
        assert (end_time - start_time) < 0.05