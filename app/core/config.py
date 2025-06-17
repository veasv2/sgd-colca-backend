"""
Configuración central de SGD-Colca Backend
"""
import os
from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    # Información del proyecto
    PROJECT_NAME: str = "SGD-Colca Backend"
    VERSION: str = "1.0.0-MVP"
    DESCRIPTION: str = "Sistema de Gobernanza Digital - Municipalidad de Colca"
    
    # Base de datos
    DATABASE_URL: str = os.getenv("DATABASE_URL", "postgresql://sgd_colca_user:SgdColca2025Seguro@127.0.0.1:5432/sgd_colca_municipal")
    
    # Google Cloud
    GOOGLE_CLOUD_PROJECT: str = os.getenv("GOOGLE_CLOUD_PROJECT", "")
    FIREBASE_PROJECT_ID: str = os.getenv("FIREBASE_PROJECT_ID", "")
    
    # Seguridad
    JWT_SECRET_KEY: str = os.getenv("JWT_SECRET_KEY", "")
    
    # Configuración de la aplicación
    ENVIRONMENT: str = os.getenv("ENVIRONMENT", "development")
    DEBUG: bool = ENVIRONMENT == "development"
    
    class Config:
        case_sensitive = True

settings = Settings()
