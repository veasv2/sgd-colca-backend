# app/schemas/seguridad/usuario_filter_schemas.py

from typing import Optional, List
from pydantic import BaseModel
from app.schemas.common.filter_schemas import (
    StringFilter, 
    DateFilter, 
    EnumFilter,
    NumberFilter,
    BooleanFilter,
    PaginationConfig,
    BaseListParams
)
from app.schemas.common.sorting_schemas import SortConfig, SortUtils

# Importar el schema de usuario existente
from app.schemas.seguridad.usuario_schemas import UsuarioInDB

class UsuarioSortableColumns:
    ID = "id"
    UUID = "uuid"
    EMAIL = "email"
    NOMBRES = "nombres"
    APELLIDO_PATERNO = "apellido_paterno"
    APELLIDO_MATERNO = "apellido_materno"
    DNI = "dni"
    TELEFONO = "telefono"
    TIPO = "tipo"
    ESTADO = "estado"
    
    INTENTOS_FALLIDOS = "intentos_fallidos"
    BLOQUEADO_HASTA = "bloqueado_hasta"
    ULTIMO_ACCESO = "ultimo_acceso"
    
    FECHA_CREACION = "fecha_creacion"
    FECHA_ACTUALIZACION = "fecha_actualizacion"
    
    @classmethod
    def get_all_columns(cls) -> List[str]:
        """Retorna todas las columnas permitidas para ordenamiento"""
        return [
            cls.ID,
            cls.UUID,
            cls.EMAIL,
            cls.NOMBRES,
            cls.APELLIDO_PATERNO,
            cls.APELLIDO_MATERNO,
            cls.DNI,
            cls.TELEFONO,
            cls.TIPO,
            cls.ESTADO,
            cls.INTENTOS_FALLIDOS,
            cls.BLOQUEADO_HASTA,
            cls.ULTIMO_ACCESO,
            cls.FECHA_CREACION,
            cls.FECHA_ACTUALIZACION
        ]

# ✅ CORREGIDO: Definir UsuarioWhere sin herencia de BaseWhere
class UsuarioWhere(BaseModel):
    # Campos de identificación
    id: Optional[NumberFilter] = None
    uuid: Optional[StringFilter] = None
    email: Optional[StringFilter] = None
    dni: Optional[StringFilter] = None
    
    # Campos de nombre
    nombres: Optional[StringFilter] = None
    apellido_paterno: Optional[StringFilter] = None
    apellido_materno: Optional[StringFilter] = None
    telefono: Optional[StringFilter] = None
    
    # Campos enum/estado
    tipo: Optional[EnumFilter] = None
    estado: Optional[EnumFilter] = None
    
    # Campos de control de acceso
    intentos_fallidos: Optional[NumberFilter] = None
    bloqueado_hasta: Optional[DateFilter] = None
    ultimo_acceso: Optional[DateFilter] = None
    
    # Campos de auditoría
    fecha_creacion: Optional[DateFilter] = None
    fecha_actualizacion: Optional[DateFilter] = None
    
    # ✅ CORREGIDO: AND/OR con el tipo específico UsuarioWhere
    AND: Optional[List['UsuarioWhere']] = None
    OR: Optional[List['UsuarioWhere']] = None
    
    class Config:
        # Permitir referencias circulares
        arbitrary_types_allowed = True

# ✅ IMPORTANTE: Rebuild del modelo después de la definición
UsuarioWhere.model_rebuild()
        
class UsuarioListaRequest(BaseListParams[UsuarioWhere]):
    where: Optional[UsuarioWhere] = None
    pagination: Optional[PaginationConfig] = PaginationConfig()
    sort: Optional[SortConfig] = None
    
    def __init__(self, **data):
        super().__init__(**data)
        # Validar que las columnas de ordenamiento sean válidas
        if self.sort and not SortUtils.is_empty(self.sort):
            allowed_columns = UsuarioSortableColumns.get_all_columns()
            for sort_column in self.sort:
                if sort_column.column not in allowed_columns:
                    raise ValueError(f"Columna '{sort_column.column}' no permitida para ordenamiento. Columnas permitidas: {allowed_columns}")

class UsuarioListaResponse(BaseModel):
    data: List[UsuarioInDB]
    total: int
    inicio: int
    fin: int
    totalPages: int
    hasNextPage: bool
    hasPrevPage: bool
    currentPage: int
    # Información adicional sobre el ordenamiento aplicado
    appliedSort: Optional[SortConfig] = None