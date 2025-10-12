"""
Tests unitaires pour le module de base de données (db.py)
Valide la persistance des données et la gestion de progression
"""

import pytest
import sqlite3
import tempfile
import os
import json
from unittest.mock import patch, MagicMock
import db


class TestDatabaseConnection:
    """Tests pour la gestion des connexions à la base de données"""

    def test_conn_returns_connection(self):
        """Test que _conn retourne une connexion SQLite valide"""
        conn = db._conn()
        assert isinstance(conn, sqlite3.Connection)
        conn.close()

    def test_conn_uses_custom_db_path(self):
        """Test que _conn utilise le chemin de base de données personnalisé"""
        test_db = "/tmp/test_custom.db"
        with patch.dict(os.environ, {'DB_PATH': test_db}):
            conn = db._conn()
            # Vérifier que la base est créée au bon endroit
            assert os.path.exists(test_db)
            conn.close()
            os.unlink(test_db)

    def test_conn_context_manager(self):
        """Test que _conn fonctionne comme context manager"""
        with db._conn() as conn:
            assert isinstance(conn, sqlite3.Connection)
            assert not conn.closed

    def test_default_db_path(self):
        """Test le chemin par défaut de la base de données"""
        assert db.DB == "./progress.db"


class TestDatabaseInitialization:
    """Tests pour l'initialisation de la base de données"""

    def test_init_db_creates_table(self):
        """Test que init_db crée la table progress"""
        with tempfile.NamedTemporaryFile(suffix='.db', delete=False) as f:
            test_db = f.name

        try:
            with patch.dict(os.environ, {'DB_PATH': test_db}):
                db.init_db()

                # Vérifier que la table existe
                conn = sqlite3.connect(test_db)
                cursor = conn.cursor()
                cursor.execute(
                    "SELECT name FROM sqlite_master WHERE type='table' AND name='progress'"
                )
                result = cursor.fetchone()
                assert result is not None
                assert result[0] == 'progress'

                # Vérifier la structure de la table
                cursor.execute("PRAGMA table_info(progress)")
                columns = cursor.fetchall()
                column_names = [col[1] for col in columns]
                expected_columns = ['user', 'exercise', 'ok', 'raw', 'ts']
                for expected_col in expected_columns:
                    assert expected_col in column_names

                conn.close()

        finally:
            if os.path.exists(test_db):
                os.unlink(test_db)

    def test_init_db_idempotent(self):
        """Test que init_db peut être appelé plusieurs fois sans erreur"""
        with tempfile.NamedTemporaryFile(suffix='.db', delete=False) as f:
            test_db = f.name

        try:
            with patch.dict(os.environ, {'DB_PATH': test_db}):
                # Premier appel
                db.init_db()

                # Deuxième appel (ne doit pas créer d'erreur)
                db.init_db()

                # Vérifier qu'il n'y a qu'une seule table
                conn = sqlite3.connect(test_db)
                cursor = conn.cursor()
                cursor.execute(
                    "SELECT COUNT(*) FROM sqlite_master WHERE type='table' AND name='progress'"
                )
                result = cursor.fetchone()
                assert result[0] == 1
                conn.close()

        finally:
            if os.path.exists(test_db):
                os.unlink(test_db)


class TestSaveResult:
    """Tests pour la fonction save_result"""

    def setup_method(self):
        """Setup pour chaque test"""
        self.temp_db = tempfile.NamedTemporaryFile(suffix='.db', delete=False)
        self.temp_db.close()
        self.original_db = db.DB
        db.DB = self.temp_db.name
        db.init_db()

    def teardown_method(self):
        """Cleanup après chaque test"""
        if os.path.exists(self.temp_db.name):
            os.unlink(self.temp_db.name)
        db.DB = self.original_db

    def test_save_result_success(self):
        """Test sauvegarde d'un résultat réussi"""
        user = "test_user"
        exercise = "test_exercise"
        result = {"ok": True, "output": "Hello World"}

        db.save_result(user, exercise, result)

        # Vérifier que le résultat a été sauvegardé
        conn = sqlite3.connect(self.temp_db.name)
        cursor = conn.cursor()
        cursor.execute(
            "SELECT user, exercise, ok, raw FROM progress WHERE user=? AND exercise=?",
            (user, exercise)
        )
        row = cursor.fetchone()
        conn.close()

        assert row is not None
        assert row[0] == user
        assert row[1] == exercise
        assert row[2] == 1  # ok=True
        assert json.loads(row[3]) == result

    def test_save_result_failure(self):
        """Test sauvegarde d'un résultat échoué"""
        user = "test_user"
        exercise = "test_exercise"
        result = {"ok": False, "error": "Syntax error"}

        db.save_result(user, exercise, result)

        # Vérifier que le résultat a été sauvegardé
        conn = sqlite3.connect(self.temp_db.name)
        cursor = conn.cursor()
        cursor.execute(
            "SELECT user, exercise, ok, raw FROM progress WHERE user=? AND exercise=?",
            (user, exercise)
        )
        row = cursor.fetchone()
        conn.close()

        assert row is not None
        assert row[0] == user
        assert row[1] == exercise
        assert row[2] == 0  # ok=False
        assert json.loads(row[3]) == result

    def test_save_result_multiple_attempts(self):
        """Test sauvegarde de plusieurs tentatives pour le même exercice"""
        user = "test_user"
        exercise = "test_exercise"

        # Première tentative échouée
        db.save_result(user, exercise, {"ok": False, "error": "Error 1"})

        # Deuxième tentative échouée
        db.save_result(user, exercise, {"ok": False, "error": "Error 2"})

        # Troisième tentative réussie
        db.save_result(user, exercise, {"ok": True, "output": "Success"})

        # Vérifier qu'on a bien 3 enregistrements
        conn = sqlite3.connect(self.temp_db.name)
        cursor = conn.cursor()
        cursor.execute(
            "SELECT COUNT(*) FROM progress WHERE user=? AND exercise=?",
            (user, exercise)
        )
        count = cursor.fetchone()[0]

        # Vérifier le dernier enregistrement
        cursor.execute(
            "SELECT ok, raw FROM progress WHERE user=? AND exercise=? ORDER BY rowid DESC LIMIT 1",
            (user, exercise)
        )
        last_row = cursor.fetchone()
        conn.close()

        assert count == 3
        assert last_row[0] == 1  # Le dernier est ok=True
        assert json.loads(last_row[1])["ok"] is True

    def test_save_result_with_complex_result(self):
        """Test sauvegarde d'un résultat complexe avec données imbriquées"""
        user = "test_user"
        exercise = "test_exercise"
        complex_result = {
            "ok": True,
            "output": "Success",
            "execution_time": 1.5,
            "memory_usage": 1024,
            "test_results": [
                {"test": "test1", "passed": True},
                {"test": "test2", "passed": True}
            ],
            "metadata": {
                "version": "1.0",
                "timestamp": "2023-01-01T00:00:00Z"
            }
        }

        db.save_result(user, exercise, complex_result)

        # Vérifier la sauvegarde
        conn = sqlite3.connect(self.temp_db.name)
        cursor = conn.cursor()
        cursor.execute(
            "SELECT raw FROM progress WHERE user=? AND exercise=?",
            (user, exercise)
        )
        row = cursor.fetchone()
        conn.close()

        saved_result = json.loads(row[0])
        assert saved_result == complex_result

    def test_save_result_special_characters(self):
        """Test sauvegarde avec des caractères spéciaux"""
        user = "user_éèç@#$%"
        exercise = "exercise-test_123"
        result = {"ok": True, "output": "Hello 世界 🌍"}

        db.save_result(user, exercise, result)

        # Vérifier la sauvegarde
        conn = sqlite3.connect(self.temp_db.name)
        cursor = conn.cursor()
        cursor.execute(
            "SELECT user, exercise, raw FROM progress WHERE user=? AND exercise=?",
            (user, exercise)
        )
        row = cursor.fetchone()
        conn.close()

        assert row is not None
        assert row[0] == user
        assert row[1] == exercise
        assert json.loads(row[3]) == result


class TestGetProgress:
    """Tests pour la fonction get_progress"""

    def setup_method(self):
        """Setup pour chaque test"""
        self.temp_db = tempfile.NamedTemporaryFile(suffix='.db', delete=False)
        self.temp_db.close()
        self.original_db = db.DB
        db.DB = self.temp_db.name
        db.init_db()

    def teardown_method(self):
        """Cleanup après chaque test"""
        if os.path.exists(self.temp_db.name):
            os.unlink(self.temp_db.name)
        db.DB = self.original_db

    def test_get_progress_empty_user(self):
        """Test récupération progression pour un utilisateur sans données"""
        result = db.get_progress("nonexistent_user")
        expected = {"completed": [], "stars": 0}
        assert result == expected

    def test_get_progress_user_with_successes(self):
        """Test récupération progression pour un utilisateur avec des succès"""
        user = "test_user"
        exercises = [
            ("course1_ex1", {"ok": True, "output": "Success 1"}),
            ("course1_ex2", {"ok": True, "output": "Success 2"}),
            ("course2_ex1", {"ok": False, "error": "Failed"}),
            ("course1_ex3", {"ok": True, "output": "Success 3"}),
        ]

        # Sauvegarder les résultats
        for exercise_id, result in exercises:
            db.save_result(user, exercise_id, result)

        result = db.get_progress(user)

        # Vérifier que seuls les exercices réussis sont comptés
        expected_completed = ["course1_ex1", "course1_ex2", "course1_ex3"]
        assert result["completed"] == expected_completed
        assert result["stars"] == 0  # Sans course_manager, stars = 0

    def test_get_progress_with_failed_attempts_only(self):
        """Test récupération progression pour un utilisateur avec uniquement des échecs"""
        user = "test_user"
        exercises = [
            ("course1_ex1", {"ok": False, "error": "Failed 1"}),
            ("course1_ex2", {"ok": False, "error": "Failed 2"}),
        ]

        for exercise_id, result in exercises:
            db.save_result(user, exercise_id, result)

        result = db.get_progress(user)
        expected = {"completed": [], "stars": 0}
        assert result == expected

    def test_get_progress_mixed_success_failure(self):
        """Test récupération progression avec succès et échecs"""
        user = "test_user"

        # Ajouter plusieurs tentatives pour le même exercice
        db.save_result(user, "course1_ex1", {"ok": False, "error": "Failed"})
        db.save_result(user, "course1_ex1", {"ok": True, "output": "Success"})  # Dernière = succès

        # Ajouter un exercice avec uniquement des échecs
        db.save_result(user, "course1_ex2", {"ok": False, "error": "Failed"})

        result = db.get_progress(user)
        expected_completed = ["course1_ex1"]  # Seul ex1 est considéré comme complété
        assert result["completed"] == expected_completed

    @patch('app.db.course_manager')
    def test_get_progress_with_course_manager(self, mock_course_manager):
        """Test récupération progression avec course_manager disponible"""
        # Mock du course_manager
        mock_course_manager.courses = {
            "python-basics": MagicMock(),
            "advanced-python": MagicMock()
        }

        # Mock de get_star_map
        def mock_get_star_map(course_id):
            if course_id == "python-basics":
                return {"hello-world": 1, "variables": 2}
            elif course_id == "advanced-python":
                return {"functions": 3}
            return {}

        mock_course_manager.get_star_map = mock_get_star_map

        user = "test_user"

        # Ajouter des exercices réussis
        db.save_result(user, "python-basics_hello-world", {"ok": True})
        db.save_result(user, "python-basics_variables", {"ok": True})
        db.save_result(user, "advanced-python_functions", {"ok": True})
        db.save_result(user, "python-basics_nonexistent", {"ok": True})  # Non dans star_map

        result = db.get_progress(user)

        # Vérifier les étoiles calculées
        expected_stars = 1 + 2 + 3  # hello-world + variables + functions
        assert result["stars"] == expected_stars
        assert len(result["completed"]) == 4

    @patch('app.db.course_manager', side_effect=ImportError("No module named"))
    def test_get_progress_course_manager_import_error(self, mock_course_manager):
        """Test récupération progression quand course_manager n'est pas disponible"""
        user = "test_user"
        db.save_result(user, "course1_ex1", {"ok": True})
        db.save_result(user, "course1_ex2", {"ok": False})

        result = db.get_progress(user)
        expected_completed = ["course1_ex1"]
        assert result["completed"] == expected_completed
        assert result["stars"] == 0


class TestDatabaseEdgeCases:
    """Tests des cas limites pour la base de données"""

    def test_database_permission_error(self):
        """Test gestion des erreurs de permissions de base de données"""
        # Utiliser un chemin inaccessible
        inaccessible_path = "/root/inaccessible.db"

        with patch.dict(os.environ, {'DB_PATH': inaccessible_path}):
            with pytest.raises(sqlite3.OperationalError):
                db.init_db()

    def test_save_result_database_locked(self):
        """Test sauvegarde quand la base de données est verrouillée"""
        with tempfile.NamedTemporaryFile(suffix='.db', delete=False) as f:
            test_db = f.name

        try:
            with patch.dict(os.environ, {'DB_PATH': test_db}):
                db.init_db()

                # Simuler une base de données verrouillée
                with patch('sqlite3.connect') as mock_connect:
                    mock_conn = MagicMock()
                    mock_cursor = MagicMock()
                    mock_cursor.execute.side_effect = sqlite3.OperationalError("database is locked")
                    mock_conn.cursor.return_value = mock_cursor
                    mock_connect.return_value.__enter__.return_value = mock_conn

                    with pytest.raises(sqlite3.OperationalError):
                        db.save_result("user", "exercise", {"ok": True})

        finally:
            if os.path.exists(test_db):
                os.unlink(test_db)

    def test_json_serialization_error(self):
        """Test gestion des erreurs de sérialisation JSON"""
        with tempfile.NamedTemporaryFile(suffix='.db', delete=False) as f:
            test_db = f.name

        try:
            with patch.dict(os.environ, {'DB_PATH': test_db}):
                db.init_db()

                # Créer un objet non sérialisable
                non_serializable_result = {
                    "ok": True,
                    "callback": lambda x: x  # Les fonctions ne sont pas sérialisables
                }

                with pytest.raises(TypeError):
                    db.save_result("user", "exercise", non_serializable_result)

        finally:
            if os.path.exists(test_db):
                os.unlink(test_db)


@pytest.mark.integration
class TestDatabaseIntegration:
    """Tests d'intégration pour la base de données"""

    def test_full_workflow_integration(self):
        """Test du workflow complet: init -> save -> get progress"""
        with tempfile.NamedTemporaryFile(suffix='.db', delete=False) as f:
            test_db = f.name

        try:
            with patch.dict(os.environ, {'DB_PATH': test_db}):
                # Initialiser la base
                db.init_db()

                # Sauvegarder plusieurs résultats pour plusieurs utilisateurs
                users_data = {
                    "alice": [
                        ("course1_ex1", {"ok": True}),
                        ("course1_ex2", {"ok": False}),
                        ("course1_ex2", {"ok": True}),  # Retentative réussie
                    ],
                    "bob": [
                        ("course1_ex1", {"ok": True}),
                        ("course2_ex1", {"ok": True}),
                    ]
                }

                for user, exercises in users_data.items():
                    for exercise_id, result in exercises:
                        db.save_result(user, exercise_id, result)

                # Vérifier la progression de chaque utilisateur
                alice_progress = db.get_progress("alice")
                bob_progress = db.get_progress("bob")
                charlie_progress = db.get_progress("charlie")  # Utilisateur inexistant

                # Assertions pour Alice
                assert set(alice_progress["completed"]) == {"course1_ex1", "course1_ex2"}
                assert alice_progress["stars"] == 0

                # Assertions pour Bob
                assert set(bob_progress["completed"]) == {"course1_ex1", "course2_ex1"}
                assert bob_progress["stars"] == 0

                # Assertions pour Charlie (aucune donnée)
                assert charlie_progress["completed"] == []
                assert charlie_progress["stars"] == 0

                # Vérifier qu'on a bien 5 enregistrements au total
                conn = sqlite3.connect(test_db)
                cursor = conn.cursor()
                cursor.execute("SELECT COUNT(*) FROM progress")
                total_records = cursor.fetchone()[0]
                conn.close()

                assert total_records == 5

        finally:
            if os.path.exists(test_db):
                os.unlink(test_db)


@pytest.mark.unit
class TestDatabasePerformance:
    """Tests de performance pour la base de données"""

    def test_performance_save_multiple_results(self):
        """Test performance sauvegarde de nombreux résultats"""
        import time

        with tempfile.NamedTemporaryFile(suffix='.db', delete=False) as f:
            test_db = f.name

        try:
            with patch.dict(os.environ, {'DB_PATH': test_db}):
                db.init_db()

                start_time = time.time()

                # Sauvegarder 1000 résultats
                for i in range(1000):
                    db.save_result(f"user_{i % 10}", f"exercise_{i}", {"ok": i % 2 == 0})

                end_time = time.time()

                # Doit prendre moins de 5 secondes
                assert (end_time - start_time) < 5.0

        finally:
            if os.path.exists(test_db):
                os.unlink(test_db)

    def test_performance_get_progress_large_dataset(self):
        """Test performance récupération progression avec beaucoup de données"""
        import time

        with tempfile.NamedTemporaryFile(suffix='.db', delete=False) as f:
            test_db = f.name

        try:
            with patch.dict(os.environ, {'DB_PATH': test_db}):
                db.init_db()

                # Créer beaucoup de données pour un utilisateur
                user = "test_user"
                for i in range(1000):
                    db.save_result(user, f"exercise_{i}", {"ok": i % 3 == 0})  # 1/3 réussis

                start_time = time.time()
                result = db.get_progress(user)
                end_time = time.time()

                # Doit prendre moins d'une seconde
                assert (end_time - start_time) < 1.0

                # Vérifier qu'on a bien le bon nombre d'exercices complétés
                assert len(result["completed"]) == 334  # 1000/3 arrondi

        finally:
            if os.path.exists(test_db):
                os.unlink(test_db)