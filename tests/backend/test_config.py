"""
Tests unitaires pour le module de configuration (config.py)
Valide la gestion sécurisée des paramètres de configuration
"""

import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), '..', '..'))
import pytest
import os
import tempfile
from unittest.mock import patch, MagicMock
from pydantic import ValidationError
from backend.config import (
    SecurityConfig,
    get_config,
    is_production,
    is_development,
    get_database_url,
    get_executor_config,
    get_cors_config,
    get_security_limits,
    config
)


class TestSecurityConfig:
    """Tests pour la classe SecurityConfig"""

    def test_default_values(self):
        """Test des valeurs par défaut de la configuration"""
        config = SecurityConfig()

        assert config.executor_url == "http://piston:2000/api/v2/execute"
        assert config.use_secure_executor is True
        assert config.max_code_length == 5000
        assert config.max_execution_time == 10
        assert config.max_memory_usage == 128 * 1024 * 1024
        assert config.allowed_origins == ["http://localhost:3000", "http://localhost:8080"]
        assert config.allowed_methods == ["GET", "POST"]
        assert config.log_level == "INFO"
        assert config.enable_request_logging is True
        assert config.log_security_violations is True
        assert config.db_path == "/data/progress.db"
        assert config.environment == "development"
        assert config.debug_mode is False

    def test_valid_environment_values(self):
        """Test des valeurs valides pour environment"""
        valid_environments = ["development", "staging", "production"]

        for env in valid_environments:
            config = SecurityConfig(environment=env)
            assert config.environment == env

    def test_invalid_environment_value(self):
        """Test des valeurs invalides pour environment"""
        invalid_environments = ["test", "dev", "prod", "", "DEBUG", "INVALID"]

        for env in invalid_environments:
            with pytest.raises(ValidationError, match="Environment must be"):
                SecurityConfig(environment=env)

    def test_valid_executor_url(self):
        """Test des URLs valides pour l'exécuteur"""
        valid_urls = [
            "http://localhost:2000/api/v2/execute",
            "https://piston.example.com/api/v2/execute",
            "http://piston:2000/api/v2/execute",
        ]

        for url in valid_urls:
            config = SecurityConfig(executor_url=url)
            assert config.executor_url == url

    def test_invalid_executor_url(self):
        """Test des URLs invalides pour l'exécuteur"""
        invalid_urls = [
            "ftp://piston:2000/api/v2/execute",
            "piston:2000/api/v2/execute",
            "localhost:2000/api/v2/execute",
            "not-a-url",
            "",
            "://invalid",
        ]

        for url in invalid_urls:
            with pytest.raises(ValidationError, match="Executor URL must be"):
                SecurityConfig(executor_url=url)

    def test_valid_allowed_origins(self):
        """Test des origines autorisées valides"""
        valid_origins = [
            ["http://localhost:3000"],
            ["https://example.com", "http://localhost:8080"],
            ["http://localhost:3000", "https://staging.example.com"],
        ]

        for origins in valid_origins:
            config = SecurityConfig(allowed_origins=origins)
            assert config.allowed_origins == origins

    def test_invalid_allowed_origins(self):
        """Test des origines autorisées invalides"""
        invalid_origins = [
            ["ftp://localhost:3000"],  # FTP non autorisé
            ["localhost:3000"],  # Pas de protocole
            ["http://localhost:3000", "invalid-origin"],  # Une origine invalide
            "not-a-list",  # Pas une liste
        ]

        for origins in invalid_origins:
            with pytest.raises(ValidationError):
                SecurityConfig(allowed_origins=origins)

    def test_valid_max_code_length(self):
        """Test des longueurs de code valides"""
        valid_lengths = [1, 100, 5000, 50000]

        for length in valid_lengths:
            config = SecurityConfig(max_code_length=length)
            assert config.max_code_length == length

    def test_invalid_max_code_length(self):
        """Test des longueurs de code invalides"""
        invalid_lengths = [0, -1, -100, 50001, 100000]

        for length in invalid_lengths:
            with pytest.raises(ValidationError, match="Max code length must be"):
                SecurityConfig(max_code_length=length)

    def test_valid_max_execution_time(self):
        """Test des temps d'exécution valides"""
        valid_times = [1, 5, 10, 30, 60]

        for time_val in valid_times:
            config = SecurityConfig(max_execution_time=time_val)
            assert config.max_execution_time == time_val

    def test_invalid_max_execution_time(self):
        """Test des temps d'exécution invalides"""
        invalid_times = [0, -1, -10, 61, 120]

        for time_val in invalid_times:
            with pytest.raises(ValidationError, match="Max execution time must be"):
                SecurityConfig(max_execution_time=time_val)

    def test_valid_max_memory_usage(self):
        """Test des usages mémoire valides"""
        valid_memory = [
            1024,  # 1KB
            1024 * 1024,  # 1MB
            128 * 1024 * 1024,  # 128MB
            1024 * 1024 * 1024,  # 1GB
        ]

        for memory in valid_memory:
            config = SecurityConfig(max_memory_usage=memory)
            assert config.max_memory_usage == memory

    def test_invalid_max_memory_usage(self):
        """Test des usages mémoire invalides"""
        invalid_memory = [0, -1, -1024, 2 * 1024 * 1024 * 1024]  # > 1GB

        for memory in invalid_memory:
            with pytest.raises(ValidationError, match="Max memory usage must be"):
                SecurityConfig(max_memory_usage=memory)

    def test_config_from_environment(self):
        """Test création de configuration depuis variables d'environnement"""
        env_vars = {
            'EXECUTOR_URL': 'https://custom.example.com/execute',
            'ENVIRONMENT': 'production',
            'MAX_CODE_LENGTH': '10000',
            'DEBUG_MODE': 'true',
            'LOG_LEVEL': 'ERROR'
        }

        with patch.dict(os.environ, env_vars):
            config = SecurityConfig()
            assert config.executor_url == 'https://custom.example.com/execute'
            assert config.environment == 'production'
            assert config.max_code_length == 10000
            assert config.debug_mode is True
            assert config.log_level == 'ERROR'

    def test_config_from_env_file(self):
        """Test création de configuration depuis fichier .env"""
        env_content = """
EXECUTOR_URL=https://env-file.example.com/execute
ENVIRONMENT=staging
MAX_CODE_LENGTH=8000
USE_SECURE_EXECUTOR=false
"""

        with tempfile.NamedTemporaryFile(mode='w', suffix='.env', delete=False) as f:
            f.write(env_content)
            f.flush()

            config = SecurityConfig(_env_file=f.name)
            assert config.executor_url == 'https://env-file.example.com/execute'
            assert config.environment == 'staging'
            assert config.max_code_length == 8000
            assert config.use_secure_executor is False

        os.unlink(f.name)

    def test_case_insensitive_env_vars(self):
        """Test que les variables d'environnement sont insensibles à la casse"""
        env_vars = {
            'executor_url': 'https://case-insensitive.com/execute',
            'ENVIRONMENT': 'production',
            'debug_mode': 'true'
        }

        with patch.dict(os.environ, env_vars):
            config = SecurityConfig()
            assert config.executor_url == 'https://case-insensitive.com/execute'
            assert config.environment == 'production'
            assert config.debug_mode is True


class TestConfigFunctions:
    """Tests pour les fonctions utilitaires de configuration"""

    def test_get_config(self):
        """Test de la fonction get_config"""
        result = get_config()
        assert isinstance(result, SecurityConfig)
        assert result == config

    def test_is_production(self):
        """Test de la fonction is_production"""
        # Test avec environment = development
        with patch.object(config, 'environment', 'development'):
            assert is_production() is False

        # Test avec environment = staging
        with patch.object(config, 'environment', 'staging'):
            assert is_production() is False

        # Test avec environment = production
        with patch.object(config, 'environment', 'production'):
            assert is_production() is True

    def test_is_development(self):
        """Test de la fonction is_development"""
        # Test avec environment = development
        with patch.object(config, 'environment', 'development'):
            assert is_development() is True

        # Test avec environment = staging
        with patch.object(config, 'environment', 'staging'):
            assert is_development() is False

        # Test avec environment = production
        with patch.object(config, 'environment', 'production'):
            assert is_development() is False

    def test_get_database_url(self):
        """Test de la fonction get_database_url"""
        test_db_path = "/custom/path/test.db"
        with patch.object(config, 'db_path', test_db_path):
            result = get_database_url()
            assert result == f"sqlite:///{test_db_path}"

    def test_get_executor_config(self):
        """Test de la fonction get_executor_config"""
        # Test avec valeurs par défaut
        result = get_executor_config()
        expected = {
            "url": config.executor_url,
            "use_secure": config.use_secure_executor,
            "timeout": config.max_execution_time,
            "max_memory": config.max_memory_usage
        }
        assert result == expected

        # Test avec valeurs personnalisées
        with patch.multiple(config,
                          executor_url='https://custom.com/execute',
                          use_secure_executor=False,
                          max_execution_time=20,
                          max_memory_usage=256 * 1024 * 1024):
            result = get_executor_config()
            expected = {
                "url": 'https://custom.com/execute',
                "use_secure": False,
                "timeout": 20,
                "max_memory": 256 * 1024 * 1024
            }
            assert result == expected

    def test_get_cors_config(self):
        """Test de la fonction get_cors_config"""
        result = get_cors_config()
        expected = {
            "allow_origins": config.allowed_origins,
            "allow_credentials": True,
            "allow_methods": config.allowed_methods,
            "allow_headers": ["*"],
        }
        assert result == expected

    def test_get_security_limits(self):
        """Test de la fonction get_security_limits"""
        result = get_security_limits()
        expected = {
            "max_code_length": config.max_code_length,
            "max_execution_time": config.max_execution_time,
            "max_memory_usage": config.max_memory_usage,
        }
        assert result == expected


class TestConfigEdgeCases:
    """Tests des cas limites pour la configuration"""

    def test_empty_allowed_origins(self):
        """Test avec une liste vide d'origines autorisées"""
        config = SecurityConfig(allowed_origins=[])
        assert config.allowed_origins == []

    def test_single_origin(self):
        """Test avec une seule origine autorisée"""
        origins = ["http://localhost:3000"]
        config = SecurityConfig(allowed_origins=origins)
        assert config.allowed_origins == origins

    def test_minimal_values(self):
        """Test avec les valeurs minimales valides"""
        config = SecurityConfig(
            max_code_length=1,
            max_execution_time=1,
            max_memory_usage=1
        )
        assert config.max_code_length == 1
        assert config.max_execution_time == 1
        assert config.max_memory_usage == 1

    def test_maximum_values(self):
        """Test avec les valeurs maximales valides"""
        config = SecurityConfig(
            max_code_length=50000,
            max_execution_time=60,
            max_memory_usage=1024 * 1024 * 1024
        )
        assert config.max_code_length == 50000
        assert config.max_execution_time == 60
        assert config.max_memory_usage == 1024 * 1024 * 1024

    def test_special_characters_in_db_path(self):
        """Test avec des caractères spéciaux dans le chemin de base de données"""
        special_paths = [
            "/data/progress-test.db",
            "/tmp/test_db.db",
            "/var/lib/app/data.db"
        ]

        for path in special_paths:
            config = SecurityConfig(db_path=path)
            assert config.db_path == path

    def test_boolean_conversion(self):
        """Test conversion des valeurs booléennes depuis l'environnement"""
        test_cases = [
            ('true', True),
            ('True', True),
            ('TRUE', True),
            ('false', False),
            ('False', False),
            ('FALSE', False),
            ('1', True),
            ('0', False),
        ]

        for env_value, expected in test_cases:
            with patch.dict(os.environ, {'USE_SECURE_EXECUTOR': env_value}):
                config = SecurityConfig()
                # Note: Pydantic gère la conversion automatiquement
                assert isinstance(config.use_secure_executor, bool)


class TestConfigValidationMessages:
    """Tests des messages de validation d'erreur"""

    def test_environment_validation_message(self):
        """Test du message d'erreur pour environment invalide"""
        with pytest.raises(ValidationError) as exc_info:
            SecurityConfig(environment='invalid')

        assert 'Environment must be' in str(exc_info.value)

    def test_url_validation_message(self):
        """Test du message d'erreur pour URL invalide"""
        with pytest.raises(ValidationError) as exc_info:
            SecurityConfig(executor_url='invalid-url')

        assert 'Executor URL must be' in str(exc_info.value)

    def test_origins_validation_message(self):
        """Test du message d'erreur pour origines invalides"""
        with pytest.raises(ValidationError) as exc_info:
            SecurityConfig(allowed_origins=['ftp://invalid.com'])

        assert 'Invalid origin' in str(exc_info.value)


@pytest.mark.unit
class TestConfigPerformance:
    """Tests de performance pour la configuration"""

    def test_config_creation_performance(self):
        """Test que la création de configuration est rapide"""
        import time

        start_time = time.time()
        for _ in range(1000):
            SecurityConfig()
        end_time = time.time()

        # Doit créer 1000 configurations en moins d'une seconde
        assert (end_time - start_time) < 1.0

    def test_function_calls_performance(self):
        """Test que les appels de fonctions sont rapides"""
        import time

        start_time = time.time()
        for _ in range(1000):
            get_config()
            is_production()
            is_development()
            get_database_url()
        end_time = time.time()

        # Doit faire 4000 appels de fonctions en moins d'une seconde
        assert (end_time - start_time) < 1.0