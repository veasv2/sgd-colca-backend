# app/services/seguridad/usuario_service.py

from sqlalchemy.ext.asyncio import AsyncSession
from fastapi import HTTPException, status

# Imports para filtros y ordenamiento
from app.models.seguridad.usuario_model import Usuario
from app.services.base_service import BaseService, BaseListService
from app.services.base_summary_service import BaseSummaryService
from app.schemas.seguridad.usuario.usuario_filter_schemas import (
    UsuarioListaRequest,
    UsuarioListaResponse,
    UsuarioWhere,
    UsuarioSortableColumns
)
from app.schemas.seguridad.usuario.usuario_summary_schemas import (
    UsuarioSummaryRequest,
    UsuarioSummaryResponse,
    UsuarioSummaryGroupableColumns
)
from app.schemas.seguridad.usuario.usuario_schemas import UsuarioCreate, UsuarioUpdate
from app.schemas.common.sorting_schemas import SortUtils

from app.repositories.seguridad.usuario_repository import UsuarioRepository, usuario_repository


class UsuarioService(
    BaseService[Usuario, UsuarioCreate, UsuarioUpdate],
    BaseListService[Usuario, UsuarioWhere, UsuarioListaResponse],
    BaseSummaryService[Usuario, UsuarioWhere]
):
    def __init__(self, repository: UsuarioRepository = usuario_repository):
        # Llamar al constructor de BaseService con el repositorio
        super(BaseService, self).__init__()  # Solo inicializar BaseListService y BaseSummaryService
        self.repository = repository

    # ===== OPERACIONES CRUD ASÍNCRONAS =====
    
    async def crear_usuario(self, db: AsyncSession, obj_in: UsuarioCreate) -> Usuario:
        """Crear un nuevo usuario con contraseña encriptada"""
        from app.core.security import hash_password
        
        # Verificar si el email ya existe
        existing_user = await self.repository.get_by_email(db, obj_in.email)
        if existing_user:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="El email ya está registrado"
            )
        
        # Verificar si el DNI ya existe (si se proporciona)
        if obj_in.dni:
            existing_dni = await self.repository.get_by_dni(db, obj_in.dni)
            if existing_dni:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="El DNI ya está registrado"
                )
        
        # Procesar datos y encriptar contraseña
        obj_in_data = obj_in.model_dump()
        password = obj_in_data.pop('password')
        obj_in_data['password_hash'] = hash_password(password)
        
        return await self.repository.create(db, obj_in_data)

    async def obtener_usuario(self, db: AsyncSession, uuid: str) -> Usuario:
        """Obtener usuario por UUID"""
        return await self.get_by_uuid(db, uuid)

    async def actualizar_usuario(self, db: AsyncSession, uuid: str, obj_in: UsuarioUpdate) -> Usuario:
        """Actualizar usuario por UUID"""
        return await self.update_by_uuid(db, uuid, obj_in)

    async def eliminar_usuario(self, db: AsyncSession, uuid: str) -> bool:
        """Eliminar usuario por UUID"""
        return await self.delete_by_uuid(db, uuid)

    # ===== OPERACIONES DE LISTADO Y RESUMEN =====

    async def lista_usuario(self, db: AsyncSession, request: UsuarioListaRequest) -> UsuarioListaResponse:
        """Obtiene la lista paginada de usuarios"""
        return await self.lista_entidades(
            db=db,
            model_class=Usuario,
            request=request,
            response_class=UsuarioListaResponse,
            allowed_sort_columns=UsuarioSortableColumns.get_all_columns(),
            excluded_columns=["password_hash"]  # ← EXCLUIR campo sensible
        )

    async def resumen_usuario(self, db: AsyncSession, request: UsuarioSummaryRequest) -> UsuarioSummaryResponse:
        """Genera resumen agrupado de usuarios"""
        summary_response = await self.generar_resumen(
            db=db,
            model_class=Usuario,
            request=request,
            allowed_group_columns=UsuarioSummaryGroupableColumns.get_all_columns()
        )
        # Convertir a response específico de usuarios si es necesario
        return UsuarioSummaryResponse(
            total=summary_response.total,
            groups=summary_response.groups
        )

# Factory function para crear servicio con dependencias
def create_usuario_service(repository: UsuarioRepository = None) -> UsuarioService:
    """Factory para crear UsuarioService con inyección de dependencias"""
    if repository is None:
        repository = usuario_repository
    return UsuarioService(repository)

# Instancia por defecto del servicio
usuario_service = create_usuario_service()