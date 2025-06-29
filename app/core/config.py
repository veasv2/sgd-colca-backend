# app/core/config.py
"""
Configuración del Sistema de Gobernanza Digital (SGD)
Municipalidad Distrital de Colca
"""
from pydantic import Field
from pydantic_settings import BaseSettings
from typing import Optional
import secrets

class Settings(BaseSettings):
    """
    Configuración de la aplicación SGD
    Las variables se cargan desde archivo .env o variables de entorno
    """
    
    # === CONFIGURACIÓN DE APLICACIÓN ===
    PROJECT_NAME: str = "SGD - Sistema de Gobernanza Digital"
    PROJECT_DESCRIPTION: str = "Sistema de Gobernanza Digital - Municipalidad Distrital de Colca"
    VERSION: str = "1.0.0-MVP"
    DEBUG: bool = True
    ENVIRONMENT: str = "development"
    DESCRIPTION: str = "Sistema de gestión municipal"

    # === CONFIGURACIÓN DE BASE DE DATOS ===
    DATABASE_URL: str = "postgresql://sgd_user:sgd_password@localhost:5432/sgd_colca"
    DATABASE_HOST: str = "localhost"
    DATABASE_PORT: int = 5432
    DATABASE_NAME: str = "sgd_colca"
    DATABASE_USER: str = "sgd_user"
    DATABASE_PASSWORD: str = ""

    # === CONFIGURACIÓN DE GOOGLE CLOUD ===
    GOOGLE_CLOUD_PROJECT: str = ""
    GOOGLE_CLOUD_PROJECT_ID: str = ""
    GOOGLE_APPLICATION_CREDENTIALS: str = ""
    GOOGLE_DRIVE_FOLDER_ID: str = ""
    FIREBASE_PROJECT_ID: str = ""

    # === CONFIGURACIÓN DE LOGGING ===
    LOG_LEVEL: str = "INFO"
    LOG_FILE: str = "logs/sgd.log"

    # === CONFIGURACIÓN DE CORS ===
    BACKEND_CORS_ORIGINS: list = ["http://localhost:3000", "http://localhost:8080"]
    ALLOWED_ORIGINS: str = "http://localhost:3000,http://localhost:8080"

    # === CONFIGURACIÓN ESPECÍFICA DEL SGD ===
    MUNICIPALITY_NAME: str = "Municipalidad Distrital de Colca"
    MUNICIPALITY_RUC: str = "20486004421"  # RUC de ejemplo, verificar el real
    MUNICIPALITY_ADDRESS: str = "Plaza de Armas s/n, Colca, Huancayo, Junín"

    # === CONFIGURACIÓN DE ARCHIVOS ===
    MAX_FILE_SIZE: int = 10 * 1024 * 1024  # 10MB
    ALLOWED_FILE_TYPES: list = [".pdf", ".doc", ".docx", ".jpg", ".png"]

         # === CONFIGURACIÓN JWT ===
    SECRET_KEY: str = Field(
        default_factory=lambda: secrets.token_urlsafe(32),
        description="Clave secreta para JWT. Se genera automáticamente si no se especifica."
    )
    ALGORITHM: str = Field(
        default="HS256",
        description="Algoritmo para JWT"
    )
    ACCESS_TOKEN_EXPIRE_MINUTES: int = Field(
        default=30,
        description="Tiempo de expiración del token en minutos"
    )
    REFRESH_TOKEN_EXPIRE_DAYS: int = Field(
        default=7,
        description="Tiempo de expiración del refresh token en días"
    )
    
    # === CONFIGURACIÓN DE SEGURIDAD ===
    MAX_LOGIN_ATTEMPTS: int = Field(
        default=5,
        description="Máximo número de intentos de login fallidos"
    )
    LOCKOUT_DURATION_MINUTES: int = Field(
        default=15,
        description="Duración del bloqueo en minutos tras intentos fallidos"
    )

    class Config:
        env_file = ".env"
        case_sensitive = True

# Instancia global de configuración
settings = Settings()