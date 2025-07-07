# app/services/seguridad/usuario_service.py

from sqlalchemy.orm import Session

# Imports para filtros y ordenamiento
from app.models.seguridad.usuario_model import Usuario
from app.services.base_service import BaseListService
from app.schemas.seguridad.usuario_filter_schemas import (
    UsuarioListaRequest,
    UsuarioListaResponse,
    UsuarioWhere,
    UsuarioSortableColumns
)
from app.schemas.common.sorting_schemas import SortUtils

class UsuarioService(BaseListService[Usuario, UsuarioWhere, UsuarioListaResponse]):

    def lista_usuarios(self, db: Session, request: UsuarioListaRequest) -> UsuarioListaResponse:
        return self.lista_entidades(
            db=db,
            model_class=Usuario,
            request=request,
            response_class=UsuarioListaResponse,
            allowed_sort_columns=UsuarioSortableColumns.get_all_columns(),
            excluded_columns=["password_hash"]  # ← EXCLUIR campo sensible
        )
    
    def lista_usuarios_activos(self, db: Session, request: UsuarioListaRequest) -> UsuarioListaResponse:
        # Forzar filtro de usuarios activos
        if not request.where:
            from app.schemas.seguridad.usuario_filter_schemas import UsuarioWhere
            request.where = UsuarioWhere()
        
        # Aplicar filtro de estado activo
        from app.schemas.common.filter_schemas import EnumFilter
        request.where.estado = EnumFilter(equals="ACTIVO")
        
        return self.lista_usuarios(db=db, request=request)
    
    def lista_usuarios_publico(self, db: Session, request: UsuarioListaRequest) -> UsuarioListaResponse:
        # Validar que solo se usen columnas públicas para ordenamiento
        if request.sort and not SortUtils.is_empty(request.sort):
            from app.schemas.seguridad.usuario_filter_schemas import UsuarioColumnValidators
            UsuarioColumnValidators.validate_public_sorting(request.sort)
        
        return self.lista_entidades(
            db=db,
            model_class=Usuario,
            request=request,
            response_class=UsuarioListaResponse,
            allowed_sort_columns=UsuarioSortableColumns.get_public_columns(),
            excluded_columns=["password_hash", "intentos_fallidos", "bloqueado_hasta"]  # Más restricciones
        )

# Instancia del servicio
usuario_service = UsuarioService()