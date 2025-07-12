# app/services/seguridad/usuario_service.py

from sqlalchemy.orm import Session

# Imports para filtros y ordenamiento
from app.models.seguridad.usuario_model import Usuario
from app.services.base_service import BaseListService
from app.services.base_summary_service import BaseSummaryService
from app.schemas.seguridad.usuario_filter_schemas import (
    UsuarioListaRequest,
    UsuarioListaResponse,
    UsuarioWhere,
    UsuarioSortableColumns
)
from app.schemas.seguridad.usuario_summary_schemas import (
    UsuarioSummaryRequest,
    UsuarioSummaryResponse,
    UsuarioSummaryGroupableColumns
)
from app.schemas.common.sorting_schemas import SortUtils

class UsuarioService(
    BaseListService[Usuario, UsuarioWhere, UsuarioListaResponse],
    BaseSummaryService[Usuario, UsuarioWhere]
):

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