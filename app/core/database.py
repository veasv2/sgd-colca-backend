# app/core/database.py
"""
Configuración de la base de datos PostgreSQL - 100% ASÍNCRONA
"""

from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker
from sqlalchemy.ext.declarative import declarative_base
from app.core.config import settings
import logging

# Configurar logging
logging.basicConfig(level=getattr(logging, settings.LOG_LEVEL))
logger = logging.getLogger(__name__)

# Crear engine asíncrono
async_database_url = settings.DATABASE_URL.replace("postgresql://", "postgresql+asyncpg://")
async_engine = create_async_engine(
    async_database_url,
    future=True,
    pool_pre_ping=True,
    echo=settings.DEBUG
)

# Crear AsyncSessionLocal
AsyncSessionLocal = async_sessionmaker(
    bind=async_engine,
    class_=AsyncSession,
    autoflush=False,
    autocommit=False,
    expire_on_commit=False
)

# Base para los modelos
Base = declarative_base()

async def get_db():
    """
    Dependencia para obtener la sesión de base de datos asíncrona
    """
    async with AsyncSessionLocal() as session:
        try:
            yield session
        except Exception as e:
            logger.error(f"Error en la sesión asíncrona de base de datos: {e}")
            await session.rollback()
            raise
        finally:
            await session.close()