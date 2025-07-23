# app/core/deps.py
"""
Configuración de inyección de dependencias - 100% ASÍNCRONA
"""

from typing import AsyncGenerator
from sqlalchemy.ext.asyncio import AsyncSession
from fastapi import Depends

from app.core.database import get_db
from app.repositories.seguridad.usuario_repository import UsuarioRepository, usuario_repository
from app.services.seguridad.usuario_service import UsuarioService, create_usuario_service

# ===== DEPENDENCIAS DE BASE DE DATOS =====

async def get_async_db() -> AsyncGenerator[AsyncSession, None]:
    """
    Dependencia para obtener sesión de base de datos asíncrona
    """
    async for session in get_db():
        yield session

# ===== DEPENDENCIAS DE REPOSITORIOS =====

def get_usuario_repository() -> UsuarioRepository:
    """
    Dependencia para obtener repositorio de usuarios
    """
    return usuario_repository

# ===== DEPENDENCIAS DE SERVICIOS =====

def get_usuario_service(
    repository: UsuarioRepository = Depends(get_usuario_repository)
) -> UsuarioService:
    """
    Dependencia para obtener servicio de usuarios con inyección de repositorio
    """
    return create_usuario_service(repository)

# ===== DEPENDENCIAS DE AUTENTICACIÓN =====

async def get_current_user_dependency(
    db: AsyncSession = Depends(get_async_db),
    usuario_service: UsuarioService = Depends(get_usuario_service)
):
    """
    Dependencia para obtener usuario autenticado actual
    """
    # Esta función se implementaría con la lógica de autenticación JWT
    # Por ahora solo defino la estructura
    pass

# ===== DEPENDENCIAS DE PERMISOS =====

def require_permissions(*permissions: str):
    """
    Factory para crear dependencias que requieren permisos específicos
    """
    def permission_dependency(
        current_user = Depends(get_current_user_dependency)
    ):
        # Lógica de validación de permisos
        pass
    return permission_dependency
