# app/schemas/seguridad/usuario_summary_schemas.py

from typing import List
from app.schemas.common.summary_schemas import SummaryRequest, SummaryResponse
from app.schemas.seguridad.usuario.usuario_filter_schemas import UsuarioWhere

class UsuarioSummaryGroupableColumns:
    """Columnas permitidas para agrupar en resúmenes de usuarios"""
    ESTADO = "estado"
    TIPO = "tipo"
    FECHA_CREACION = "fecha_creacion"  # Para resúmenes por mes/año
    
    @classmethod
    def get_all_columns(cls) -> List[str]:
        """Retorna todas las columnas permitidas para agrupación"""
        return [
            cls.ESTADO,
            cls.TIPO,
            cls.FECHA_CREACION
        ]

# Request específico para resúmenes de usuarios
class UsuarioSummaryRequest(SummaryRequest[UsuarioWhere]):
    pass

# Response específico para resúmenes de usuarios  
class UsuarioSummaryResponse(SummaryResponse):
    pass