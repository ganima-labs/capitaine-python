import os
from typing import Optional
from pydantic import validator
from pydantic_settings import BaseSettings

class SecurityConfig(BaseSettings):
    """
    Configuration sécurisée pour l'application Capitaine Python
    """

    # Configuration de l'exécuteur
    executor_url: str = "http://piston:2000/api/v2/execute"
    use_secure_executor: bool = True

    # Limites de sécurité
    max_code_length: int = 5000
    max_execution_time: int = 10  # secondes
    max_memory_usage: int = 128 * 1024 * 1024  # 128MB

    # Configuration CORS
    allowed_origins: list = ["http://localhost:3000", "http://localhost:8080"]
    allowed_methods: list = ["GET", "POST"]

    # Logging et monitoring
    log_level: str = "INFO"
    enable_request_logging: bool = True
    log_security_violations: bool = True

    # Base de données
    db_path: str = "/data/progress.db"

    # Configuration de développement/production
    environment: str = "development"
    debug_mode: bool = False

    @validator('environment')
    def validate_environment(cls, v):
        if v not in ['development', 'staging', 'production']:
            raise ValueError('Environment must be development, staging, or production')
        return v

    @validator('executor_url')
    def validate_executor_url(cls, v):
        if not v.startswith(('http://', 'https://')):
            raise ValueError('Executor URL must be a valid HTTP/HTTPS URL')
        return v

    @validator('allowed_origins')
    def validate_origins(cls, v):
        if not isinstance(v, list):
            raise ValueError('Allowed origins must be a list')
        for origin in v:
            if not origin.startswith(('http://', 'https://')):
                raise ValueError(f'Invalid origin: {origin}')
        return v

    @validator('max_code_length')
    def validate_max_code_length(cls, v):
        if v <= 0 or v > 50000:
            raise ValueError('Max code length must be between 1 and 50000 characters')
        return v

    @validator('max_execution_time')
    def validate_max_execution_time(cls, v):
        if v <= 0 or v > 60:
            raise ValueError('Max execution time must be between 1 and 60 seconds')
        return v

    @validator('max_memory_usage')
    def validate_max_memory_usage(cls, v):
        if v <= 0 or v > 1024 * 1024 * 1024:  # 1GB max
            raise ValueError('Max memory usage must be between 1 and 1GB')
        return v

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"
        case_sensitive = False


# Instance globale de configuration
config = SecurityConfig()


def get_config() -> SecurityConfig:
    """Retourne la configuration de l'application"""
    return config


def is_production() -> bool:
    """Vérifie si l'application est en mode production"""
    return config.environment == "production"


def is_development() -> bool:
    """Vérifie si l'application est en mode développement"""
    return config.environment == "development"


def get_database_url() -> str:
    """Retourne l'URL de la base de données"""
    return f"sqlite:///{config.db_path}"


def get_executor_config() -> dict:
    """Retourne la configuration de l'exécuteur"""
    return {
        "url": config.executor_url,
        "use_secure": config.use_secure_executor,
        "timeout": config.max_execution_time,
        "max_memory": config.max_memory_usage
    }


def get_cors_config() -> dict:
    """Retourne la configuration CORS"""
    return {
        "allow_origins": config.allowed_origins,
        "allow_credentials": True,
        "allow_methods": config.allowed_methods,
        "allow_headers": ["*"],
    }


def get_security_limits() -> dict:
    """Retourne les limites de sécurité"""
    return {
        "max_code_length": config.max_code_length,
        "max_execution_time": config.max_execution_time,
        "max_memory_usage": config.max_memory_usage,
    }