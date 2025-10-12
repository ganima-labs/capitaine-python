"""
Tests complets pour le module db.py
Couvre tous les aspects de la gestion de la base de données
"""

import pytest
import os
import tempfile
import sqlite3
import json
from unittest.mock import patch, mock_open, MagicMock
from contextlib import contextmanager

import db


class TestDatabaseConnection:
    """Tests pour la connexion à la base de données"""

    def test_conn_default_path(self):
        """Test _conn avec chemin par défaut"""
        with patch('sqlite3.connect') as mock_connect:
            mock_conn = MagicMock()
            mock_connect.return_value = mock_conn

            conn = db._conn()
            mock_connect.assert_called_once_with(db.DB_PATH)
            assert conn == mock_conn

    def test_conn_custom_path(self):
        """Test _conn avec chemin personnalisé via variable d'environnement"""
        custom_path = "/tmp/custom_test.db"

        with patch.dict(os.environ, {'DB_PATH': custom_path}):
            with patch('sqlite3.connect') as mock_connect:
                mock_conn = MagicMock()
                mock_connect.return_value = mock_conn

                conn = db._conn()
                mock_connect.assert_called_once_with(custom_path)
                assert conn == mock_conn

    def test_conn_context_manager_success(self):
        """Test _conn comme context manager - succès"""
        with patch('sqlite3.connect') as mock_connect:
            mock_conn = MagicMock()
            mock_connect.return_value.__enter__.return_value = mock_conn
            mock_connect.return_value.__exit__.return_value = None

            with db._conn() as conn:
                mock_connect.assert_called_once()
                assert conn == mock_conn

    def test_conn_context_manager_exception(self):
        """Test _conn comme context manager - avec exception"""
        with patch('sqlite3.connect') as mock_connect:
            mock_conn = MagicMock()
            mock_connect.return_value.__enter__.return_value = mock_conn
            mock_connect.return_value.__exit__.return_value = None

            try:
                with db._conn() as conn:
                    raise ValueError("Test exception")
            except ValueError:
                pass  # Expected

            mock_connect.assert_called_once()
            mock_conn.__exit__.assert_called_once()

    def test_conn_database_creation_on_first_use(self):
        """Test création de la base de données lors de la première utilisation"""
        with tempfile.NamedTemporaryFile(delete=False) as temp_file:
            db_path = temp_file.name

        # Supprimer le fichier pour simuler une création
        os.unlink(db_path)

        try:
            with patch.object(db, 'DB_PATH', db_path):
                conn = db._conn()

                # Vérifier que le fichier a été créé
                assert os.path.exists(db_path)

                # Nettoyer
                conn.close()
        finally:
            if os.path.exists(db_path):
                os.unlink(db_path)


class TestDatabaseInitialization:
    """Tests pour l'initialisation de la base de données"""

    def test_init_db_creates_table(self):
        """Test init_db crée la table progress"""
        with tempfile.NamedTemporaryFile(delete=False) as temp_file:
            db_path = temp_file.name

        try:
            with patch.object(db, 'DB_PATH', db_path):
                db.init_db()

                # Vérifier que la table a été créée
                conn = sqlite3.connect(db_path)
                cursor = conn.cursor()

                # Lister les tables
                cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
                tables = cursor.fetchall()

                assert len(tables) >= 1
                assert any('progress' in table[0] for table in tables)

                # Vérifier la structure de la table
                cursor.execute("PRAGMA table_info(progress)")
                columns = cursor.fetchall()
                column_names = [col[1] for col in columns]

                expected_columns = ['id', 'learner', 'exercise', 'result', 'created_at']
                for expected_col in expected_columns:
                    assert expected_col in column_names

                conn.close()
        finally:
            if os.path.exists(db_path):
                os.unlink(db_path)

    def test_init_db_idempotent(self):
        """Test init_db est idempotent (peut être appelé plusieurs fois)"""
        with tempfile.NamedTemporaryFile(delete=False) as temp_file:
            db_path = temp_file.name

        try:
            with patch.object(db, 'DB_PATH', db_path):
                # Appeler init_db deux fois
                db.init_db()
                db.init_db()

                # Ne devrait pas y avoir d'erreur
                conn = sqlite3.connect(db_path)
                cursor = conn.cursor()

                cursor.execute("SELECT COUNT(*) FROM progress")
                count = cursor.fetchone()[0]

                # La table devrait exister et être vide
                assert count == 0

                conn.close()
        finally:
            if os.path.exists(db_path):
                os.unlink(db_path)

    def test_init_db_handles_existing_data(self):
        """Test init_db préserve les données existantes"""
        with tempfile.NamedTemporaryFile(delete=False) as temp_file:
            db_path = temp_file.name

        try:
            with patch.object(db, 'DB_PATH', db_path):
                # Initialiser et ajouter des données
                db.init_db()

                test_result = {"ok": True, "stdout": "Hello"}
                db.save_result("test_user", "test_exercise", test_result)

                # Réinitialiser (ne devrait pas effacer les données)
                db.init_db()

                # Vérifier que les données sont toujours là
                progress = db.get_progress("test_user")
                assert "test_exercise" in progress

        finally:
            if os.path.exists(db_path):
                os.unlink(db_path)

    def test_init_db_with_database_error(self):
        """Test gestion des erreurs de base de données dans init_db"""
        with patch('sqlite3.connect') as mock_connect:
            mock_connect.side_effect = sqlite3.DatabaseError("Cannot create database")

            # Ne devrait pas lever d'exception non gérée
            with pytest.raises(sqlite3.DatabaseError):
                db.init_db()


class TestSaveResult:
    """Tests pour la fonction save_result"""

    def test_save_result_success(self):
        """Test save_result réussi"""
        with tempfile.NamedTemporaryFile(delete=False) as temp_file:
            db_path = temp_file.name

        try:
            with patch.object(db, 'DB_PATH', db_path):
                db.init_db()

                learner = "test_user"
                exercise = "test_exercise"
                result = {"ok": True, "stdout": "Hello World!", "score": 100}

                db.save_result(learner, exercise, result)

                # Vérifier que les données ont été sauvegardées
                conn = sqlite3.connect(db_path)
                cursor = conn.cursor()

                cursor.execute(
                    "SELECT learner, exercise, result FROM progress WHERE learner = ? AND exercise = ?",
                    (learner, exercise)
                )
                row = cursor.fetchone()

                assert row is not None
                assert row[0] == learner
                assert row[1] == exercise
                assert json.loads(row[2]) == result

                conn.close()
        finally:
            if os.path.exists(db_path):
                os.unlink(db_path)

    def test_save_result_update_existing(self):
        """Test save_result met à jour un enregistrement existant"""
        with tempfile.NamedTemporaryFile(delete=False) as temp_file:
            db_path = temp_file.name

        try:
            with patch.object(db, 'DB_PATH', db_path):
                db.init_db()

                learner = "test_user"
                exercise = "test_exercise"

                # Première sauvegarde
                result1 = {"ok": False, "stdout": "Error message", "score": 0}
                db.save_result(learner, exercise, result1)

                # Deuxième sauvegarde (mise à jour)
                result2 = {"ok": True, "stdout": "Success!", "score": 100}
                db.save_result(learner, exercise, result2)

                # Vérifier que seule la dernière version existe
                conn = sqlite3.connect(db_path)
                cursor = conn.cursor()

                cursor.execute(
                    "SELECT result FROM progress WHERE learner = ? AND exercise = ?",
                    (learner, exercise)
                )
                row = cursor.fetchone()

                assert row is not None
                saved_result = json.loads(row[0])
                assert saved_result == result2
                assert saved_result["ok"] is True

                conn.close()
        finally:
            if os.path.exists(db_path):
                os.unlink(db_path)

    def test_save_result_with_complex_result(self):
        """Test save_result avec un résultat complexe"""
        with tempfile.NamedTemporaryFile(delete=False) as temp_file:
            db_path = temp_file.name

        try:
            with patch.object(db, 'DB_PATH', db_path):
                db.init_db()

                complex_result = {
                    "ok": True,
                    "stdout": "Program output\nMultiple lines",
                    "stderr": "",
                    "score": 95,
                    "metadata": {
                        "execution_time": 1.23,
                        "memory_used": 1024,
                        "test_cases": [
                            {"name": "test1", "passed": True},
                            {"name": "test2", "passed": False, "error": "AssertionError"}
                        ]
                    },
                    "hints": ["Try using loops", "Check your variables"]
                }

                db.save_result("user", "exercise", complex_result)

                # Vérifier la récupération
                conn = sqlite3.connect(db_path)
                cursor = conn.cursor()

                cursor.execute("SELECT result FROM progress WHERE learner = 'user' AND exercise = 'exercise'")
                row = cursor.fetchone()

                assert row is not None
                saved_result = json.loads(row[0])
                assert saved_result == complex_result
                assert len(saved_result["metadata"]["test_cases"]) == 2

                conn.close()
        finally:
            if os.path.exists(db_path):
                os.unlink(db_path)

    def test_save_result_with_special_characters(self):
        """Test save_result avec des caractères spéciaux"""
        with tempfile.NamedTemporaryFile(delete=False) as temp_file:
            db_path = temp_file.name

        try:
            with patch.object(db, 'DB_PATH', db_path):
                db.init_db()

                special_result = {
                    "ok": True,
                    "stdout": "Output with émojis 🚀 and accents: éàüç",
                    "error": "Error message with quotes: 'single' and \"double\"",
                    "unicode": "测试中文 العربية русский"
                }

                db.save_result("unicode_user", "unicode_exercise", special_result)

                # Vérifier la récupération
                conn = sqlite3.connect(db_path)
                cursor = conn.cursor()

                cursor.execute(
                    "SELECT result FROM progress WHERE learner = 'unicode_user' AND exercise = 'unicode_exercise'"
                )
                row = cursor.fetchone()

                assert row is not None
                saved_result = json.loads(row[0])
                assert "🚀" in saved_result["stdout"]
                assert "测试中文" in saved_result["unicode"]

                conn.close()
        finally:
            if os.path.exists(db_path):
                os.unlink(db_path)

    def test_save_result_database_error(self):
        """Test save_result avec erreur de base de données"""
        with patch('sqlite3.connect') as mock_connect:
            mock_conn = MagicMock()
            mock_cursor = MagicMock()
            mock_conn.cursor.return_value = mock_cursor
            mock_connect.return_value = mock_conn

            # Simuler une erreur lors de l'exécution
            mock_cursor.execute.side_effect = sqlite3.DatabaseError("Disk full")

            with pytest.raises(sqlite3.DatabaseError):
                db.save_result("user", "exercise", {"ok": True})


class TestGetProgress:
    """Tests pour la fonction get_progress"""

    def test_get_progress_empty(self):
        """Test get_progress pour un utilisateur sans données"""
        with tempfile.NamedTemporaryFile(delete=False) as temp_file:
            db_path = temp_file.name

        try:
            with patch.object(db, 'DB_PATH', db_path):
                db.init_db()

                progress = db.get_progress("nonexistent_user")

                assert progress == {}

        finally:
            if os.path.exists(db_path):
                os.unlink(db_path)

    def test_get_progress_single_exercise(self):
        """Test get_progress pour un utilisateur avec un seul exercice"""
        with tempfile.NamedTemporaryFile(delete=False) as temp_file:
            db_path = temp_file.name

        try:
            with patch.object(db, 'DB_PATH', db_path):
                db.init_db()

                learner = "test_user"
                exercise = "test_exercise"
                result = {"ok": True, "score": 85}

                db.save_result(learner, exercise, result)

                progress = db.get_progress(learner)

                assert exercise in progress
                assert progress[exercise] == result

        finally:
            if os.path.exists(db_path):
                os.unlink(db_path)

    def test_get_progress_multiple_exercises(self):
        """Test get_progress pour un utilisateur avec plusieurs exercices"""
        with tempfile.NamedTemporaryFile(delete=False) as temp_file:
            db_path = temp_file.name

        try:
            with patch.object(db, 'DB_PATH', db_path):
                db.init_db()

                learner = "test_user"

                # Sauvegarder plusieurs exercices
                exercises = [
                    ("ex1", {"ok": True, "score": 100}),
                    ("ex2", {"ok": False, "score": 50}),
                    ("ex3", {"ok": True, "score": 75}),
                ]

                for exercise, result in exercises:
                    db.save_result(learner, exercise, result)

                progress = db.get_progress(learner)

                assert len(progress) == 3
                assert progress["ex1"]["score"] == 100
                assert progress["ex2"]["ok"] is False
                assert progress["ex3"]["score"] == 75

        finally:
            if os.path.exists(db_path):
                os.unlink(db_path)

    def test_get_progress_multiple_users(self):
        """Test get_progress ne retourne que les données de l'utilisateur spécifié"""
        with tempfile.NamedTemporaryFile(delete=False) as temp_file:
            db_path = temp_file.name

        try:
            with patch.object(db, 'DB_PATH', db_path):
                db.init_db()

                # Données pour deux utilisateurs différents
                db.save_result("user1", "ex1", {"ok": True, "score": 90})
                db.save_result("user2", "ex1", {"ok": False, "score": 60})
                db.save_result("user1", "ex2", {"ok": True, "score": 80})

                progress_user1 = db.get_progress("user1")
                progress_user2 = db.get_progress("user2")

                assert len(progress_user1) == 2
                assert len(progress_user2) == 1
                assert "ex1" in progress_user1
                assert "ex2" in progress_user1
                assert "ex1" in progress_user2
                assert progress_user1["ex1"]["score"] == 90
                assert progress_user2["ex1"]["score"] == 60

        finally:
            if os.path.exists(db_path):
                os.unlink(db_path)

    def test_get_progress_with_course_manager_integration(self):
        """Test get_progress avec intégration du course manager"""
        with tempfile.NamedTemporaryFile(delete=False) as temp_file:
            db_path = temp_file.name

        try:
            with patch.object(db, 'DB_PATH', db_path):
                db.init_db()

                # Simuler un exercice dans un cours
                exercise_key = "python-basics_hello-world"
                result = {"ok": True, "stars": 1, "completed_at": "2023-01-01T12:00:00Z"}

                db.save_result("student", exercise_key, result)

                progress = db.get_progress("student")

                assert exercise_key in progress
                assert progress[exercise_key]["ok"] is True
                assert progress[exercise_key]["stars"] == 1

        finally:
            if os.path.exists(db_path):
                os.unlink(db_path)

    def test_get_progress_course_manager_import_error(self):
        """Test get_progress gère les erreurs d'import du course manager"""
        with tempfile.NamedTemporaryFile(delete=False) as temp_file:
            db_path = temp_file.name

        try:
            with patch.object(db, 'DB_PATH', db_path):
                db.init_db()

                # Sauvegarder quelques résultats
                db.save_result("user", "test_exercise", {"ok": True})

                # Mock une erreur d'import du course manager
                with patch('course_manager.course_manager') as mock_cm:
                    mock_cm.get_exercise.side_effect = ImportError("Cannot import course_manager")

                    # La fonction devrait toujours fonctionner
                    progress = db.get_progress("user")
                    assert "test_exercise" in progress

        finally:
            if os.path.exists(db_path):
                os.unlink(db_path)


class TestDatabaseConstants:
    """Tests pour les constantes de la base de données"""

    def test_db_path_constant(self):
        """Test que DB_PATH est défini correctement"""
        assert hasattr(db, 'DB_PATH')
        assert isinstance(db.DB_PATH, str)
        assert len(db.DB_PATH) > 0

    def test_db_path_default_value(self):
        """Test la valeur par défaut de DB_PATH"""
        assert db.DB_PATH == "/data/progress.db"

    def test_db_path_environment_override(self):
        """Test que DB_PATH peut être surchargé par variable d'environnement"""
        custom_path = "/custom/path/test.db"

        with patch.dict(os.environ, {'DB_PATH': custom_path}):
            # Recharger le module pour tester
            import importlib
            importlib.reload(db)

            assert db.DB_PATH == custom_path


class TestDatabaseEdgeCases:
    """Tests pour les cas limites de la base de données"""

    def test_database_permission_error(self):
        """Test gestion des erreurs de permissions"""
        with patch('sqlite3.connect') as mock_connect:
            mock_connect.side_effect = sqlite3.OperationalError("Permission denied")

            with pytest.raises(sqlite3.OperationalError):
                conn = db._conn()

    def test_save_result_database_locked(self):
        """Test save_result quand la base de données est verrouillée"""
        with tempfile.NamedTemporaryFile(delete=False) as temp_file:
            db_path = temp_file.name

        try:
            with patch.object(db, 'DB_PATH', db_path):
                db.init_db()

                # Simuler une base de données verrouillée
                with patch('sqlite3.connect') as mock_connect:
                    mock_conn = MagicMock()
                    mock_cursor = MagicMock()
                    mock_conn.cursor.return_value = mock_cursor
                    mock_connect.return_value = mock_conn

                    mock_cursor.execute.side_effect = sqlite3.OperationalError("Database is locked")

                    with pytest.raises(sqlite3.OperationalError):
                        db.save_result("user", "exercise", {"ok": True})

        finally:
            if os.path.exists(db_path):
                os.unlink(db_path)

    def test_get_progress_corrupted_database(self):
        """Test get_progress avec base de données corrompue"""
        with tempfile.NamedTemporaryFile(delete=False) as temp_file:
            db_path = temp_file.name

        try:
            # Corrompre le fichier de base de données
            with open(db_path, 'w') as f:
                f.write("Corrupted database data")

            with patch.object(db, 'DB_PATH', db_path):
                with pytest.raises(sqlite3.DatabaseError):
                    progress = db.get_progress("user")

        finally:
            if os.path.exists(db_path):
                os.unlink(db_path)

    def test_concurrent_access(self):
        """Test accès concurrent à la base de données"""
        with tempfile.NamedTemporaryFile(delete=False) as temp_file:
            db_path = temp_file.name

        try:
            with patch.object(db, 'DB_PATH', db_path):
                db.init_db()

                # Simuler des accès concurrents
                import threading

                results = []
                errors = []

                def save_data(user_id):
                    try:
                        result = {"ok": True, "user_id": user_id}
                        db.save_result(f"user_{user_id}", f"exercise_{user_id}", result)
                        results.append(user_id)
                    except Exception as e:
                        errors.append((user_id, str(e)))

                # Créer plusieurs threads
                threads = []
                for i in range(5):
                    thread = threading.Thread(target=save_data, args=(i,))
                    threads.append(thread)

                # Démarrer tous les threads
                for thread in threads:
                    thread.start()

                # Attendre la fin de tous les threads
                for thread in threads:
                    thread.join()

                # Vérifier que les opérations ont réussi
                assert len(errors) == 0, f"Errors occurred: {errors}"
                assert len(results) == 5

        finally:
            if os.path.exists(db_path):
                os.unlink(db_path)


class TestDatabaseIntegration:
    """Tests d'intégration complets pour la base de données"""

    def test_full_workflow_integration(self):
        """Test workflow complet d'intégration"""
        with tempfile.NamedTemporaryFile(delete=False) as temp_file:
            db_path = temp_file.name

        try:
            with patch.object(db, 'DB_PATH', db_path):
                # Initialisation
                db.init_db()

                # Sauvegarder plusieurs résultats pour différents utilisateurs
                users_data = {
                    "alice": {
                        "python-basics_print": {"ok": True, "score": 100, "time": 0.5},
                        "python-basics_variables": {"ok": True, "score": 90, "time": 1.2},
                    },
                    "bob": {
                        "python-basics_print": {"ok": False, "score": 70, "error": "Syntax Error"},
                        "python-basics_variables": {"ok": True, "score": 85, "time": 0.8},
                        "python-basics_loops": {"ok": True, "score": 95, "time": 2.1},
                    }
                }

                # Sauvegarder toutes les données
                for user, exercises in users_data.items():
                    for exercise, result in exercises.items():
                        db.save_result(user, exercise, result)

                # Vérifier les données récupérées
                for user, expected_exercises in users_data.items():
                    progress = db.get_progress(user)

                    assert len(progress) == len(expected_exercises)

                    for exercise, expected_result in expected_exercises.items():
                        assert exercise in progress
                        saved_result = progress[exercise]
                        assert saved_result["ok"] == expected_result["ok"]
                        assert saved_result["score"] == expected_result["score"]

                # Mettre à jour un résultat existant
                improved_result = {"ok": True, "score": 100, "time": 0.4}
                db.save_result("bob", "python-basics_print", improved_result)

                # Vérifier la mise à jour
                bob_progress = db.get_progress("bob")
                assert bob_progress["python-basics_print"]["score"] == 100
                assert bob_progress["python-basics_print"]["time"] == 0.4

        finally:
            if os.path.exists(db_path):
                os.unlink(db_path)


class TestDatabasePerformance:
    """Tests de performance pour la base de données"""

    def test_performance_multiple_saves(self):
        """Test performance de sauvegardes multiples"""
        with tempfile.NamedTemporaryFile(delete=False) as temp_file:
            db_path = temp_file.name

        try:
            with patch.object(db, 'DB_PATH', db_path):
                db.init_db()

                import time

                # Mesurer le temps pour 100 sauvegardes
                start_time = time.time()

                for i in range(100):
                    result = {"ok": i % 2 == 0, "score": i, "iteration": i}
                    db.save_result(f"user_{i % 10}", f"exercise_{i}", result)

                end_time = time.time()
                elapsed_time = end_time - start_time

                # Devrait être raisonnablement rapide (< 5 secondes pour 100 opérations)
                assert elapsed_time < 5.0, f"Too slow: {elapsed_time:.2f} seconds for 100 operations"

        finally:
            if os.path.exists(db_path):
                os.unlink(db_path)

    def test_performance_large_dataset(self):
        """Test performance avec un grand jeu de données"""
        with tempfile.NamedTemporaryFile(delete=False) as temp_file:
            db_path = temp_file.name

        try:
            with patch.object(db, 'DB_PATH', db_path):
                db.init_db()

                # Créer un grand jeu de données
                user = "power_user"
                num_exercises = 50

                # Sauvegarder beaucoup de données
                for i in range(num_exercises):
                    large_result = {
                        "ok": True,
                        "score": 100,
                        "stdout": "Output " * 100,  # ~800 octets
                        "metadata": {"test": "data " * 50},  # ~400 octets
                        "array": list(range(1000))  # ~4000 octets
                    }
                    db.save_result(user, f"exercise_{i}", large_result)

                # Mesurer le temps de récupération
                import time
                start_time = time.time()

                progress = db.get_progress(user)

                end_time = time.time()
                elapsed_time = end_time - start_time

                # Vérifications
                assert len(progress) == num_exercises
                assert elapsed_time < 1.0, f"Too slow: {elapsed_time:.2f} seconds to retrieve {num_exercises} exercises"

                # Vérifier l'intégrité des données
                for i in range(num_exercises):
                    exercise_key = f"exercise_{i}"
                    assert exercise_key in progress
                    assert len(progress[exercise_key]["array"]) == 1000

        finally:
            if os.path.exists(db_path):
                os.unlink(db_path)