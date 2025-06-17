"""
Configuración de base de datos para SGD-Colca
"""
import os
from sqlalchemy import create_engine, MetaData
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from databases import Database
from .config import settings

# Para desarrollo sin Cloud SQL Proxy, usar configuración simplificada
DATABASE_URL = settings.DATABASE_URL

# Si estamos en desarrollo local sin proxy, usar una URL temporal
if "127.0.0.1:5432" in DATABASE_URL and os.getenv("SKIP_DB_CONNECTION") == "true":
    # URL temporal para que no falle al importar
    DATABASE_URL = "postgresql://user:pass@localhost:5432/temp"

try:
    # Configuración de SQLAlchemy
    engine = create_engine(DATABASE_URL)
    SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
    
    # Base para modelos
    Base = declarative_base()
    
    # Configuración de databases para async
    database = Database(DATABASE_URL)
    
except Exception as e:
    print(f"⚠️ Advertencia: No se pudo conectar a la base de datos: {e}")
    print("📝 Configurando modo sin base de datos para desarrollo")
    
    # Configuración temporal para desarrollo sin BD
    engine = None
    SessionLocal = None
    Base = declarative_base()
    database = None

# Dependency para obtener sesión de DB
def get_db():
    if SessionLocal is None:
        raise Exception("Base de datos no configurada")
    
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()