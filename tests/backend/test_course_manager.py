"""
Tests unitaires pour le module course_manager.py
Valide la gestion des cours et des exercices pédagogiques
"""

import pytest
import tempfile
import json
import os
from pathlib import Path
from unittest.mock import patch, MagicMock
import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), '..', '..'))
from backend.course_manager import CourseManager


class TestCourseManagerInit:
    """Tests pour l'initialisation de CourseManager"""

    def test_init_default_directory(self):
        """Test initialisation avec répertoire par défaut"""
        import backend.course_manager as cm_mod
        manager = CourseManager()
        # Default dir is computed relative to course_manager.py, not this test file.
        expected_path = os.path.join(os.path.dirname(cm_mod.__file__), "courses")
        assert manager.courses_dir == expected_path
        assert isinstance(manager.courses, dict)
        assert manager.current_course_id is None

    def test_init_custom_directory(self):
        """Test initialisation avec répertoire personnalisé"""
        custom_dir = "/tmp/custom_courses"
        manager = CourseManager(custom_dir)
        assert manager.courses_dir == custom_dir

    def test_init_loads_courses(self):
        """Test que l'initialisation charge les cours"""
        with tempfile.TemporaryDirectory() as temp_dir:
            # Créer un fichier de cours test
            course_data = {
                "meta": {"id": "test-course", "title": "Test Course"},
                "exercises": []
            }
            course_file = Path(temp_dir) / "test_course.json"
            with open(course_file, 'w', encoding='utf-8') as f:
                json.dump(course_data, f)

            manager = CourseManager(temp_dir)
            assert "test-course" in manager.courses
            assert manager.courses["test-course"]["meta"]["title"] == "Test Course"


class TestLoadAllCourses:
    """Tests pour la méthode load_all_courses"""

    def test_load_all_courses_directory_not_exists(self):
        """Test chargement quand le répertoire n'existe pas"""
        non_existent_dir = "/tmp/definitely_does_not_exist_12345"
        manager = CourseManager(non_existent_dir)

        with patch('builtins.print') as mock_print:
            manager.load_all_courses()
            mock_print.assert_called_with(f"⚠️ Dossier des cours introuvable: {non_existent_dir}")

    def test_load_all_courses_empty_directory(self):
        """Test chargement d'un répertoire vide"""
        with tempfile.TemporaryDirectory() as temp_dir:
            manager = CourseManager(temp_dir)
            manager.load_all_courses()
            assert len(manager.courses) == 0

    def test_load_all_courses_with_valid_files(self):
        """Test chargement de fichiers de cours valides"""
        with tempfile.TemporaryDirectory() as temp_dir:
            # Créer plusieurs fichiers de cours
            courses_data = [
                {
                    "meta": {"id": "python-basics", "title": "Python Basics"},
                    "exercises": [{"id": "ex1", "stars": 1}]
                },
                {
                    "meta": {"id": "advanced-python", "title": "Advanced Python"},
                    "exercises": [{"id": "ex2", "stars": 2}, {"id": "ex3", "stars": 3}]
                }
            ]

            for i, course_data in enumerate(courses_data):
                course_file = Path(temp_dir) / f"course_{i}.json"
                with open(course_file, 'w', encoding='utf-8') as f:
                    json.dump(course_data, f)

            manager = CourseManager(temp_dir)
            manager.load_all_courses()

            assert len(manager.courses) == 2
            assert "python-basics" in manager.courses
            assert "advanced-python" in manager.courses
            assert len(manager.courses["python-basics"]["exercises"]) == 1
            assert len(manager.courses["advanced-python"]["exercises"]) == 2

    def test_load_all_courses_file_without_id(self):
        """Test gestion de fichier sans ID"""
        with tempfile.TemporaryDirectory() as temp_dir:
            # Créer un fichier sans ID
            invalid_course = {"meta": {"title": "No ID"}, "exercises": []}
            course_file = Path(temp_dir) / "invalid.json"
            with open(course_file, 'w', encoding='utf-8') as f:
                json.dump(invalid_course, f)

            manager = CourseManager(temp_dir)

            with patch('builtins.print') as mock_print:
                manager.load_all_courses()
                mock_print.assert_called()
                assert len(manager.courses) == 0

    def test_load_all_courses_malformed_json(self):
        """Test gestion de fichier JSON malformé"""
        with tempfile.TemporaryDirectory() as temp_dir:
            # Créer un fichier JSON invalide
            course_file = Path(temp_dir) / "malformed.json"
            with open(course_file, 'w', encoding='utf-8') as f:
                f.write("{ invalid json content")

            manager = CourseManager(temp_dir)

            with patch('builtins.print') as mock_print:
                manager.load_all_courses()
                mock_print.assert_called()
                assert len(manager.courses) == 0

    def test_load_all_courses_non_json_files(self):
        """Test ignorer les fichiers non-JSON"""
        with tempfile.TemporaryDirectory() as temp_dir:
            # Créer des fichiers non-JSON
            (Path(temp_dir) / "readme.txt").write_text("This is not JSON")
            (Path(temp_dir) / "config.yaml").write_text("key: value")

            manager = CourseManager(temp_dir)
            manager.load_all_courses()

            assert len(manager.courses) == 0

    def test_load_all_courses_unicode_content(self):
        """Test chargement de contenu Unicode"""
        with tempfile.TemporaryDirectory() as temp_dir:
            course_data = {
                "meta": {"id": "unicode-course", "title": "Cours en français 🐍"},
                "exercises": [{"id": "ex-unicode", "title": "Exercice avec accents éèç"}]
            }
            course_file = Path(temp_dir) / "unicode.json"
            with open(course_file, 'w', encoding='utf-8') as f:
                json.dump(course_data, f, ensure_ascii=False)

            manager = CourseManager(temp_dir)
            manager.load_all_courses()

            assert "unicode-course" in manager.courses
            assert "🐍" in manager.courses["unicode-course"]["meta"]["title"]
            assert "éèç" in manager.courses["unicode-course"]["exercises"][0]["title"]


class TestGetCourseList:
    """Tests pour la méthode get_course_list"""

    def setup_method(self):
        """Setup pour chaque test"""
        self.temp_dir = tempfile.mkdtemp()
        self.manager = CourseManager(self.temp_dir)

    def teardown_method(self):
        """Cleanup après chaque test"""
        import shutil
        shutil.rmtree(self.temp_dir, ignore_errors=True)

    def test_get_course_list_empty(self):
        """Test liste de cours vide"""
        self.manager.load_all_courses()
        course_list = self.manager.get_course_list()
        assert course_list == []

    def test_get_course_list_with_courses(self):
        """Test liste de cours avec des cours"""
        # Créer des cours de test
        courses_data = [
            {
                "meta": {
                    "id": "python-basics",
                    "title": "Python Basics",
                    "description": "Learn Python fundamentals",
                    "level": "Beginner",
                    "estimated_hours": 10,
                    "icon": "🐍"
                },
                "exercises": [
                    {"id": "ex1", "title": "Print", "stars": 1},
                    {"id": "ex2", "title": "Variables", "stars": 1}
                ]
            },
            {
                "meta": {
                    "id": "advanced-python",
                    "title": "Advanced Python",
                    "description": "Advanced Python concepts",
                    "level": "Advanced",
                    "estimated_hours": 20
                },
                "exercises": [
                    {"id": "ex3", "title": "Decorators", "stars": 3}
                ]
            }
        ]

        for course_data in courses_data:
            course_file = Path(self.temp_dir) / f"{course_data['meta']['id']}.json"
            with open(course_file, 'w', encoding='utf-8') as f:
                json.dump(course_data, f)

        self.manager.load_all_courses()
        course_list = self.manager.get_course_list()

        assert len(course_list) == 2

        # Vérifier que tous les cours attendus sont présents (indépendamment de l'ordre)
        course_ids = [course["id"] for course in course_list]
        expected_ids = ["python-basics", "advanced-python"]
        assert set(course_ids) == set(expected_ids)

        # Vérifier les métadonnées de chaque cours (indépendamment de l'ordre)
        courses_by_id = {course["id"]: course for course in course_list}

        # Vérifier python-basics
        python_basics = courses_by_id["python-basics"]
        assert python_basics["title"] == "Python Basics"
        assert python_basics["description"] == "Learn Python fundamentals"
        assert python_basics["level"] == "Beginner"
        assert python_basics["estimated_hours"] == 10
        assert python_basics["exercise_count"] == 2
        assert python_basics["total_stars"] == 2  # 1 + 1
        assert python_basics["icon"] == "🐍"

        # Vérifier advanced-python
        advanced_python = courses_by_id["advanced-python"]
        assert advanced_python["title"] == "Advanced Python"
        assert advanced_python["exercise_count"] == 1
        assert advanced_python["total_stars"] == 3
        assert advanced_python["icon"] is None

    def test_get_course_list_default_values(self):
        """Test liste de cours avec valeurs par défaut"""
        course_data = {
            "meta": {"id": "minimal-course"},
            "exercises": []
        }
        course_file = Path(self.temp_dir) / "minimal.json"
        with open(course_file, 'w', encoding='utf-8') as f:
            json.dump(course_data, f)

        self.manager.load_all_courses()
        course_list = self.manager.get_course_list()

        assert len(course_list) == 1
        course = course_list[0]
        assert course["id"] == "minimal-course"
        assert course["title"] == "Sans titre"
        assert course["description"] == ""
        assert course["level"] == "Non spécifié"
        assert course["estimated_hours"] == 0
        assert course["exercise_count"] == 0
        assert course["total_stars"] == 0
        assert course["theme_name"] == "default"
        assert course["icon"] is None


class TestGetCourse:
    """Tests pour la méthode get_course"""

    def setup_method(self):
        """Setup pour chaque test"""
        self.temp_dir = tempfile.mkdtemp()
        self.manager = CourseManager(self.temp_dir)

    def teardown_method(self):
        """Cleanup après chaque test"""
        import shutil
        shutil.rmtree(self.temp_dir, ignore_errors=True)

    def test_get_course_existing(self):
        """Test récupération d'un cours existant"""
        course_data = {
            "meta": {"id": "test-course", "title": "Test Course"},
            "exercises": [{"id": "ex1", "title": "Exercise 1"}]
        }
        course_file = Path(self.temp_dir) / "test.json"
        with open(course_file, 'w', encoding='utf-8') as f:
            json.dump(course_data, f)

        self.manager.load_all_courses()
        course = self.manager.get_course("test-course")

        assert course is not None
        assert course["meta"]["id"] == "test-course"
        assert course["meta"]["title"] == "Test Course"
        assert len(course["exercises"]) == 1

    def test_get_course_nonexistent(self):
        """Test récupération d'un cours inexistant"""
        self.manager.load_all_courses()
        course = self.manager.get_course("nonexistent-course")
        assert course is None

    def test_get_course_no_load(self):
        """Test récupération sans chargement préalable"""
        course = self.manager.get_course("any-course")
        assert course is None


class TestGetCourseExercises:
    """Tests pour la méthode get_course_exercises"""

    def setup_method(self):
        """Setup pour chaque test"""
        self.temp_dir = tempfile.mkdtemp()
        self.manager = CourseManager(self.temp_dir)

    def teardown_method(self):
        """Cleanup après chaque test"""
        import shutil
        shutil.rmtree(self.temp_dir, ignore_errors=True)

    def test_get_course_exercises_existing(self):
        """Test récupération des exercices d'un cours existant"""
        course_data = {
            "meta": {"id": "test-course"},
            "exercises": [
                {"id": "ex1", "title": "Print", "stars": 1},
                {"id": "ex2", "title": "Variables", "stars": 2},
                {"id": "ex3", "title": "Loops", "stars": 3}
            ]
        }
        course_file = Path(self.temp_dir) / "test.json"
        with open(course_file, 'w', encoding='utf-8') as f:
            json.dump(course_data, f)

        self.manager.load_all_courses()
        exercises = self.manager.get_course_exercises("test-course")

        assert len(exercises) == 3
        assert exercises[0]["id"] == "ex1"
        assert exercises[0]["title"] == "Print"
        assert exercises[0]["stars"] == 1
        assert exercises[1]["id"] == "ex2"
        assert exercises[1]["title"] == "Variables"
        assert exercises[1]["stars"] == 2

    def test_get_course_exercises_nonexistent_course(self):
        """Test récupération des exercices d'un cours inexistant"""
        self.manager.load_all_courses()
        exercises = self.manager.get_course_exercises("nonexistent-course")
        assert exercises == []

    def test_get_course_exercises_no_exercises(self):
        """Test récupération des exercices d'un cours sans exercices"""
        course_data = {"meta": {"id": "empty-course"}, "exercises": []}
        course_file = Path(self.temp_dir) / "empty.json"
        with open(course_file, 'w', encoding='utf-8') as f:
            json.dump(course_data, f)

        self.manager.load_all_courses()
        exercises = self.manager.get_course_exercises("empty-course")
        assert exercises == []

    def test_get_course_exercises_missing_fields(self):
        """Test récupération des exercices avec champs manquants"""
        course_data = {
            "meta": {"id": "test-course"},
            "exercises": [
                {"id": "ex1"},  # Pas de title ou stars
                {"title": "No ID"},  # Pas d'ID
                {"id": "ex2", "title": "Complete"}  # Sans stars (défaut 0)
            ]
        }
        course_file = Path(self.temp_dir) / "test.json"
        with open(course_file, 'w', encoding='utf-8') as f:
            json.dump(course_data, f)

        self.manager.load_all_courses()
        exercises = self.manager.get_course_exercises("test-course")

        assert len(exercises) == 3
        assert exercises[0]["id"] == "ex1"
        assert exercises[0]["title"] is None
        assert exercises[0]["stars"] == 0
        assert exercises[1]["id"] is None
        assert exercises[1]["title"] == "No ID"
        assert exercises[1]["stars"] == 0
        assert exercises[2]["id"] == "ex2"
        assert exercises[2]["title"] == "Complete"
        assert exercises[2]["stars"] == 0


class TestGetExercise:
    """Tests pour la méthode get_exercise"""

    def setup_method(self):
        """Setup pour chaque test"""
        self.temp_dir = tempfile.mkdtemp()
        self.manager = CourseManager(self.temp_dir)

    def teardown_method(self):
        """Cleanup après chaque test"""
        import shutil
        shutil.rmtree(self.temp_dir, ignore_errors=True)

    def test_get_exercise_existing(self):
        """Test récupération d'un exercice existant"""
        course_data = {
            "meta": {"id": "test-course"},
            "exercises": [
                {"id": "ex1", "title": "Print", "stars": 1},
                {"id": "ex2", "title": "Variables", "stars": 2}
            ]
        }
        course_file = Path(self.temp_dir) / "test.json"
        with open(course_file, 'w', encoding='utf-8') as f:
            json.dump(course_data, f)

        self.manager.load_all_courses()
        exercise = self.manager.get_exercise("test-course", "ex1")

        assert exercise is not None
        assert exercise["id"] == "ex1"
        assert exercise["title"] == "Print"
        assert exercise["stars"] == 1

    def test_get_exercise_nonexistent_course(self):
        """Test récupération d'un exercice d'un cours inexistant"""
        self.manager.load_all_courses()
        exercise = self.manager.get_exercise("nonexistent-course", "ex1")
        assert exercise is None

    def test_get_exercise_nonexistent_exercise(self):
        """Test récupération d'un exercice inexistant"""
        course_data = {
            "meta": {"id": "test-course"},
            "exercises": [{"id": "ex1", "title": "Print"}]
        }
        course_file = Path(self.temp_dir) / "test.json"
        with open(course_file, 'w', encoding='utf-8') as f:
            json.dump(course_data, f)

        self.manager.load_all_courses()
        exercise = self.manager.get_exercise("test-course", "nonexistent-ex")
        assert exercise is None

    def test_get_exercise_duplicate_ids(self):
        """Test récupération quand il y a des IDs dupliqués"""
        course_data = {
            "meta": {"id": "test-course"},
            "exercises": [
                {"id": "ex1", "title": "First"},
                {"id": "ex1", "title": "Second"}  # ID dupliqué
            ]
        }
        course_file = Path(self.temp_dir) / "test.json"
        with open(course_file, 'w', encoding='utf-8') as f:
            json.dump(course_data, f)

        self.manager.load_all_courses()
        exercise = self.manager.get_exercise("test-course", "ex1")

        # Doit retourner le premier trouvé
        assert exercise is not None
        assert exercise["title"] == "First"


class TestGetCourseTheme:
    """Tests pour la méthode get_course_theme"""

    def setup_method(self):
        """Setup pour chaque test"""
        self.temp_dir = tempfile.mkdtemp()
        self.manager = CourseManager(self.temp_dir)

    def teardown_method(self):
        """Cleanup après chaque test"""
        import shutil
        shutil.rmtree(self.temp_dir, ignore_errors=True)

    def test_get_course_theme_existing(self):
        """Test récupération du thème d'un cours existant"""
        course_data = {
            "meta": {"id": "test-course"},
            "theme": {
                "name": "custom",
                "primary_color": "#ff0000",
                "background_color": "#000000"
            }
        }
        course_file = Path(self.temp_dir) / "test.json"
        with open(course_file, 'w', encoding='utf-8') as f:
            json.dump(course_data, f)

        self.manager.load_all_courses()
        theme = self.manager.get_course_theme("test-course")

        assert theme["name"] == "custom"
        assert theme["primary_color"] == "#ff0000"
        assert theme["background_color"] == "#000000"

    def test_get_course_theme_no_theme(self):
        """Test récupération du thème quand le cours n'a pas de thème"""
        course_data = {"meta": {"id": "test-course"}}
        course_file = Path(self.temp_dir) / "test.json"
        with open(course_file, 'w', encoding='utf-8') as f:
            json.dump(course_data, f)

        self.manager.load_all_courses()
        theme = self.manager.get_course_theme("test-course")

        # Doit retourner le thème par défaut
        assert theme["name"] == "default"
        assert theme["primary_color"] == "#0077be"

    def test_get_course_theme_nonexistent_course(self):
        """Test récupération du thème d'un cours inexistant"""
        self.manager.load_all_courses()
        theme = self.manager.get_course_theme("nonexistent-course")

        # Doit retourner le thème par défaut
        assert theme["name"] == "default"
        assert theme["primary_color"] == "#0077be"


class TestGetDefaultTheme:
    """Tests pour la méthode get_default_theme"""

    def test_get_default_theme_structure(self):
        """Test structure du thème par défaut"""
        manager = CourseManager()
        theme = manager.get_default_theme()

        required_fields = [
            "name", "primary_color", "secondary_color", "background_color",
            "surface_color", "text_color", "accent_color",
            "gradient_start", "gradient_end", "font_family"
        ]

        for field in required_fields:
            assert field in theme

        assert theme["name"] == "default"
        assert theme["primary_color"] == "#0077be"
        assert theme["secondary_color"] == "#00a8cc"
        assert theme["background_color"] == "#0a1929"
        assert theme["surface_color"] == "#1e3a5f"
        assert theme["text_color"] == "#ffffff"
        assert theme["accent_color"] == "#00d4aa"
        assert theme["gradient_start"] == "#0a1929"
        assert theme["gradient_end"] == "#1e3a5f"
        assert theme["font_family"] == "system-ui, -apple-system, sans-serif"

    def test_get_default_theme_immutability(self):
        """Test que le thème par défaut peut être modifié sans affecter l'original"""
        manager = CourseManager()
        theme1 = manager.get_default_theme()
        theme1["primary_color"] = "#ff0000"

        theme2 = manager.get_default_theme()
        assert theme2["primary_color"] == "#0077be"  # Doit être inchangé


class TestSetCurrentCourse:
    """Tests pour la méthode set_current_course"""

    def setup_method(self):
        """Setup pour chaque test"""
        self.temp_dir = tempfile.mkdtemp()
        self.manager = CourseManager(self.temp_dir)

    def teardown_method(self):
        """Cleanup après chaque test"""
        import shutil
        shutil.rmtree(self.temp_dir, ignore_errors=True)

    def test_set_current_course_existing(self):
        """Test définition du cours actuel existant"""
        course_data = {"meta": {"id": "test-course"}}
        course_file = Path(self.temp_dir) / "test.json"
        with open(course_file, 'w', encoding='utf-8') as f:
            json.dump(course_data, f)

        self.manager.load_all_courses()
        result = self.manager.set_current_course("test-course")

        assert result is True
        assert self.manager.current_course_id == "test-course"

    def test_set_current_course_nonexistent(self):
        """Test définition du cours actuel inexistant"""
        self.manager.load_all_courses()
        result = self.manager.set_current_course("nonexistent-course")

        assert result is False
        assert self.manager.current_course_id is None

    def test_set_current_course_multiple(self):
        """Test changement multiple du cours actuel"""
        course_data = [
            {"meta": {"id": "course1"}},
            {"meta": {"id": "course2"}}
        ]

        for i, data in enumerate(course_data):
            course_file = Path(self.temp_dir) / f"course{i}.json"
            with open(course_file, 'w', encoding='utf-8') as f:
                json.dump(data, f)

        self.manager.load_all_courses()

        # Premier cours
        assert self.manager.set_current_course("course1") is True
        assert self.manager.current_course_id == "course1"

        # Changement vers deuxième cours
        assert self.manager.set_current_course("course2") is True
        assert self.manager.current_course_id == "course2"

        # Tentative de cours inexistant
        assert self.manager.set_current_course("nonexistent") is False
        assert self.manager.current_course_id == "course2"  # Doit rester inchangé


class TestGetCurrentCourse:
    """Tests pour la méthode get_current_course"""

    def test_get_current_course_none_initially(self):
        """Test getCurrentCourse retourne None initialement"""
        manager = CourseManager()
        assert manager.get_current_course() is None

    def test_get_current_course_after_set(self):
        """Test getCurrentCourse après set_current_course"""
        manager = CourseManager()
        # Simuler un cours existant
        manager.courses["test-course"] = {"meta": {"id": "test-course"}}

        manager.set_current_course("test-course")
        assert manager.get_current_course() == "test-course"


class TestGetStarMap:
    """Tests pour la méthode get_star_map"""

    def setup_method(self):
        """Setup pour chaque test"""
        self.temp_dir = tempfile.mkdtemp()
        self.manager = CourseManager(self.temp_dir)

    def teardown_method(self):
        """Cleanup après chaque test"""
        import shutil
        shutil.rmtree(self.temp_dir, ignore_errors=True)

    def test_get_star_map_existing(self):
        """Test récupération de la carte d'étoiles"""
        course_data = {
            "meta": {"id": "test-course"},
            "exercises": [
                {"id": "ex1", "stars": 1},
                {"id": "ex2", "stars": 2},
                {"id": "ex3", "stars": 1}
            ]
        }
        course_file = Path(self.temp_dir) / "test.json"
        with open(course_file, 'w', encoding='utf-8') as f:
            json.dump(course_data, f)

        self.manager.load_all_courses()
        star_map = self.manager.get_star_map("test-course")

        expected = {"ex1": 1, "ex2": 2, "ex3": 1}
        assert star_map == expected

    def test_get_star_map_nonexistent_course(self):
        """Test récupération de la carte d'étoiles pour cours inexistant"""
        self.manager.load_all_courses()
        star_map = self.manager.get_star_map("nonexistent-course")
        assert star_map == {}

    def test_get_star_map_no_exercises(self):
        """Test récupération de la carte d'étoiles pour cours sans exercices"""
        course_data = {"meta": {"id": "empty-course"}, "exercises": []}
        course_file = Path(self.temp_dir) / "empty.json"
        with open(course_file, 'w', encoding='utf-8') as f:
            json.dump(course_data, f)

        self.manager.load_all_courses()
        star_map = self.manager.get_star_map("empty-course")
        assert star_map == {}

    def test_get_star_map_missing_stars(self):
        """Test récupération de la carte d'étoiles avec valeurs manquantes"""
        course_data = {
            "meta": {"id": "test-course"},
            "exercises": [
                {"id": "ex1"},  # Pas de stars
                {"id": "ex2", "stars": 2},
                {"id": "ex3", "stars": 0}
            ]
        }
        course_file = Path(self.temp_dir) / "test.json"
        with open(course_file, 'w', encoding='utf-8') as f:
            json.dump(course_data, f)

        self.manager.load_all_courses()
        star_map = self.manager.get_star_map("test-course")

        expected = {"ex1": 0, "ex2": 2, "ex3": 0}
        assert star_map == expected


class TestCourseManagerEdgeCases:
    """Tests des cas limites pour CourseManager"""

    def test_load_courses_with_nested_directories(self):
        """Test chargement avec sous-répertoires (doit les ignorer)"""
        with tempfile.TemporaryDirectory() as temp_dir:
            # Créer un sous-répertoire
            subdir = Path(temp_dir) / "subdir"
            subdir.mkdir()

            # Mettre un fichier JSON dans le sous-répertoire
            nested_file = subdir / "nested.json"
            nested_file.write_text('{"meta": {"id": "nested"}}')

            # Mettre un fichier JSON à la racine
            root_file = Path(temp_dir) / "root.json"
            root_file.write_text('{"meta": {"id": "root"}}')

            manager = CourseManager(temp_dir)
            manager.load_all_courses()

            # Seul le fichier racine doit être chargé
            assert len(manager.courses) == 1
            assert "root" in manager.courses
            assert "nested" not in manager.courses

    def test_file_permissions_error(self):
        """Test gestion des erreurs de permissions"""
        with tempfile.TemporaryDirectory() as temp_dir:
            # Créer un fichier sans permissions de lecture
            course_file = Path(temp_dir) / "no_permission.json"
            course_data = {"meta": {"id": "no-permission"}}
            with open(course_file, 'w', encoding='utf-8') as f:
                json.dump(course_data, f)

            # Simuler une erreur de permission
            with patch('builtins.open', side_effect=PermissionError("Permission denied")):
                with patch('builtins.print') as mock_print:
                    manager = CourseManager(temp_dir)
                    manager.load_all_courses()

                    assert len(manager.courses) == 0
                    mock_print.assert_called()

    def test_concurrent_access(self):
        """Test accès concurrent aux données du cours"""
        import threading

        with tempfile.TemporaryDirectory() as temp_dir:
            course_data = {"meta": {"id": "test-course"}, "exercises": []}
            course_file = Path(temp_dir) / "test.json"
            with open(course_file, 'w', encoding='utf-8') as f:
                json.dump(course_data, f)

            manager = CourseManager(temp_dir)
            manager.load_all_courses()

            def access_course():
                for _ in range(100):
                    course = manager.get_course("test-course")
                    assert course is not None
                    exercises = manager.get_course_exercises("test-course")
                    assert isinstance(exercises, list)

            # Créer plusieurs threads qui accèdent aux données
            threads = [threading.Thread(target=access_course) for _ in range(5)]
            for thread in threads:
                thread.start()
            for thread in threads:
                thread.join()

            # Vérifier que les données sont toujours cohérentes
            assert manager.get_course("test-course") is not None


@pytest.mark.integration
class TestCourseManagerIntegration:
    """Tests d'intégration pour CourseManager"""

    def test_full_workflow(self):
        """Test workflow complet de gestion de cours"""
        with tempfile.TemporaryDirectory() as temp_dir:
            # Créer une structure de cours complète
            course_data = {
                "meta": {
                    "id": "python-complete",
                    "title": "Complete Python Course",
                    "description": "From basics to advanced",
                    "level": "Beginner to Advanced",
                    "estimated_hours": 40,
                    "icon": "🐍"
                },
                "theme": {
                    "name": "ocean",
                    "primary_color": "#006994",
                    "background_color": "#001f3f"
                },
                "exercises": [
                    {"id": "hello-world", "title": "Hello World", "stars": 1},
                    {"id": "variables", "title": "Variables", "stars": 1},
                    {"id": "functions", "title": "Functions", "stars": 2},
                    {"id": "classes", "title": "Classes", "stars": 3}
                ]
            }

            course_file = Path(temp_dir) / "python_complete.json"
            with open(course_file, 'w', encoding='utf-8') as f:
                json.dump(course_data, f)

            # Initialiser le gestionnaire
            manager = CourseManager(temp_dir)

            # Workflow complet
            assert len(manager.get_course_list()) == 1

            # Définir comme cours actuel
            assert manager.set_current_course("python-complete") is True
            assert manager.get_current_course() == "python-complete"

            # Obtenir les informations du cours
            course = manager.get_course("python-complete")
            assert course["meta"]["title"] == "Complete Python Course"

            # Obtenir les exercices
            exercises = manager.get_course_exercises("python-complete")
            assert len(exercises) == 4
            assert exercises[0]["stars"] == 1
            assert exercises[-1]["stars"] == 3

            # Obtenir un exercice spécifique
            exercise = manager.get_exercise("python-complete", "functions")
            assert exercise["title"] == "Functions"
            assert exercise["stars"] == 2

            # Obtenir le thème
            theme = manager.get_course_theme("python-complete")
            assert theme["name"] == "ocean"
            assert theme["primary_color"] == "#006994"

            # Obtenir la carte d'étoiles
            star_map = manager.get_star_map("python-complete")
            expected_stars = {
                "hello-world": 1,
                "variables": 1,
                "functions": 2,
                "classes": 3
            }
            assert star_map == expected_stars

    def test_multiple_courses_interaction(self):
        """Test interaction entre plusieurs cours"""
        with tempfile.TemporaryDirectory() as temp_dir:
            # Créer plusieurs cours
            courses_data = [
                {
                    "meta": {"id": "beginner", "title": "Beginner Course"},
                    "exercises": [{"id": "ex1", "stars": 1}, {"id": "ex2", "stars": 1}]
                },
                {
                    "meta": {"id": "intermediate", "title": "Intermediate Course"},
                    "exercises": [{"id": "ex1", "stars": 2}, {"id": "ex3", "stars": 3}]
                }
            ]

            for course_data in courses_data:
                course_file = Path(temp_dir) / f"{course_data['meta']['id']}.json"
                with open(course_file, 'w', encoding='utf-8') as f:
                    json.dump(course_data, f)

            manager = CourseManager(temp_dir)

            # Changer de cours actuel
            manager.set_current_course("beginner")
            assert manager.get_current_course() == "beginner"
            beginner_exercises = manager.get_course_exercises("beginner")
            assert len(beginner_exercises) == 2

            # Changer vers un autre cours
            manager.set_current_course("intermediate")
            assert manager.get_current_course() == "intermediate"
            intermediate_exercises = manager.get_course_exercises("intermediate")
            assert len(intermediate_exercises) == 2

            # Vérifier que les données du premier cours sont toujours accessibles
            assert len(manager.get_course_exercises("beginner")) == 2


@pytest.mark.unit
class TestCourseManagerPerformance:
    """Tests de performance pour CourseManager"""

    def test_load_many_courses_performance(self):
        """Test performance chargement de nombreux cours"""
        import time

        with tempfile.TemporaryDirectory() as temp_dir:
            # Créer 100 cours
            for i in range(100):
                course_data = {
                    "meta": {
                        "id": f"course-{i:03d}",
                        "title": f"Course {i}"
                    },
                    "exercises": [
                        {"id": f"ex-{i}-1", "stars": 1},
                        {"id": f"ex-{i}-2", "stars": 2}
                    ]
                }
                course_file = Path(temp_dir) / f"course_{i:03d}.json"
                with open(course_file, 'w', encoding='utf-8') as f:
                    json.dump(course_data, f)

            start_time = time.time()
            manager = CourseManager(temp_dir)
            manager.load_all_courses()
            end_time = time.time()

            # Doit charger 100 cours en moins d'une seconde
            assert (end_time - start_time) < 1.0
            assert len(manager.courses) == 100

    def test_get_operations_performance(self):
        """Test performance des opérations de lecture"""
        import time

        with tempfile.TemporaryDirectory() as temp_dir:
            # Créer 50 cours avec des exercices
            for i in range(50):
                course_data = {
                    "meta": {"id": f"course-{i}"},
                    "exercises": [{"id": f"ex-{j}", "stars": j % 3 + 1} for j in range(10)]
                }
                course_file = Path(temp_dir) / f"course_{i}.json"
                with open(course_file, 'w', encoding='utf-8') as f:
                    json.dump(course_data, f)

            manager = CourseManager(temp_dir)
            manager.load_all_courses()

            start_time = time.time()

            # Effectuer de nombreuses opérations de lecture
            for i in range(1000):
                course_id = f"course-{i % 50}"
                exercise_id = f"ex-{i % 10}"

                manager.get_course(course_id)
                manager.get_course_exercises(course_id)
                manager.get_exercise(course_id, exercise_id)
                manager.get_star_map(course_id)

            end_time = time.time()

            # 4000 opérations en moins d'une seconde
            assert (end_time - start_time) < 1.0


# Test pour l'instance globale
class TestGlobalCourseManager:
    """Tests pour l'instance globale course_manager"""

    def test_global_instance_exists(self):
        """Test que l'instance globale existe"""
        from backend.course_manager import course_manager
        assert course_manager is not None
        assert isinstance(course_manager, CourseManager)

    def test_global_instance_loaded(self):
        """Test que l'instance globale est chargée"""
        from backend.course_manager import course_manager
        # L'instance doit avoir tenté de charger les cours du répertoire par défaut
        assert isinstance(course_manager.courses, dict)