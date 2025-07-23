# app/services/seguridad/usuario_service.py

from sqlalchemy.orm import Session

# Imports para filtros y ordenamiento
from app.models.seguridad.usuario_model import Usuario
from app.services.base_service import BaseListService
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
from app.schemas.common.sorting_schemas import SortUtils

from app.repositories.seguridad.usuario_repository import usuario_repository


class UsuarioService(
    BaseListService[Usuario, UsuarioWhere, UsuarioListaResponse],
    BaseSummaryService[Usuario, UsuarioWhere]
):
    #CRUD
    def crear_usuario(self, db: Session, obj_in):
        """Crear un nuevo usuario con contraseña encriptada"""
        from app.core.security import hash_password
        obj_in_data = obj_in.dict() if hasattr(obj_in, 'dict') else dict(obj_in)
        password = obj_in_data.pop('password')
        obj_in_data['password_hash'] = hash_password(password)
        return usuario_repository.create(db, obj_in_data)

    def obtener_usuario(self, db: Session, uuid: str):
        """Obtener usuario por UUID"""
        return usuario_repository.get_by_uuid(db, uuid)

    def actualizar_usuario(self, db: Session, uuid: str, obj_in):
        """Actualizar usuario por uuid"""
        db_obj = usuario_repository.get_by_uuid(db, uuid)
        if not db_obj:
            return None
        return usuario_repository.update(db, db_obj, obj_in)

    def eliminar_usuario(self, db: Session, uuid: str):
        """Eliminar usuario por uuid"""
        db_obj = usuario_repository.get_by_uuid(db, uuid)
        if not db_obj:
            return None
        return usuario_repository.delete(db, db_obj.id)

    # Listar usuarios
    def lista_usuario(self, db: Session, request: UsuarioListaRequest) -> UsuarioListaResponse:
        """Obtiene la lista paginada de usuarios"""
        return self.lista_entidades(
            db=db,
            model_class=Usuario,
            request=request,
            response_class=UsuarioListaResponse,
            allowed_sort_columns=UsuarioSortableColumns.get_all_columns(),
            excluded_columns=["password_hash"]  # ← EXCLUIR campo sensible
        )

    def resumen_usuario(self, db: Session, request: UsuarioSummaryRequest) -> UsuarioSummaryResponse:
        """Genera resumen agrupado de usuarios"""
        summary_response = self.generar_resumen(
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

# Instancia del servicio
usuario_service = UsuarioService()