# app/schemas/common/filter_schemas.py

from typing import Optional, List, Union, Any, TypeVar, Generic
from pydantic import BaseModel, Field
from datetime import datetime

# Importar el sistema de ordenamiento
from app.schemas.common.sorting_schemas import SortConfig

# ----------------------------------------------------------------------
# Filtros genéricos por tipo de dato
# ----------------------------------------------------------------------

class StringFilter(BaseModel):
    equals: Optional[str] = None
    contains: Optional[str] = None
    startsWith: Optional[str] = None
    endsWith: Optional[str] = None
    in_: Optional[List[str]] = Field(default=None, alias="in")
    
    class Config:
        populate_by_name = True
        allow_population_by_field_name = True

class NumberFilter(BaseModel):
    equals: Optional[Union[int, float]] = None
    gt: Optional[Union[int, float]] = None
    gte: Optional[Union[int, float]] = None
    lt: Optional[Union[int, float]] = None
    lte: Optional[Union[int, float]] = None
    in_: Optional[List[Union[int, float]]] = Field(default=None, alias="in")
    
    class Config:
        populate_by_name = True
        allow_population_by_field_name = True

class DateFilter(BaseModel):
    equals: Optional[Union[datetime, str]] = None
    gt: Optional[Union[datetime, str]] = None
    gte: Optional[Union[datetime, str]] = None
    lt: Optional[Union[datetime, str]] = None
    lte: Optional[Union[datetime, str]] = None
    in_: Optional[List[Union[datetime, str]]] = Field(default=None, alias="in")
    
    class Config:
        populate_by_name = True
        allow_population_by_field_name = True

class EnumFilter(BaseModel):
    equals: Optional[str] = None
    in_: Optional[List[str]] = Field(default=None, alias="in")
    
    class Config:
        populate_by_name = True
        allow_population_by_field_name = True

class BooleanFilter(BaseModel):
    equals: Optional[bool] = None

# ----------------------------------------------------------------------
# Configuración de paginación
# ----------------------------------------------------------------------

class PaginationConfig(BaseModel):
    page: int = 1
    pageSize: int = 10

# ----------------------------------------------------------------------
# Resultado paginado genérico
# ----------------------------------------------------------------------

DataType = TypeVar('DataType')

class PaginatedResult(BaseModel, Generic[DataType]):
    data: List[DataType]        # datos de la página actual
    total: int                  # total de registros después de filtros
    inicio: int                 # índice del primer elemento (1-indexed)
    fin: int                   # índice del último elemento
    totalPages: int             # total de páginas
    hasNextPage: bool           # hay página siguiente
    hasPrevPage: bool           # hay página anterior
    currentPage: int            # página actual
    # Información adicional sobre el ordenamiento aplicado
    appliedSort: Optional[SortConfig] = None

# ----------------------------------------------------------------------
# Base para filtros con lógica AND/OR
# ----------------------------------------------------------------------

class BaseWhere(BaseModel):
    AND: Optional[List['BaseWhere']] = None
    OR: Optional[List['BaseWhere']] = None
    
    class Config:
        # Permitir referencias circulares
        arbitrary_types_allowed = True

# Actualizar referencias circulares
BaseWhere.model_rebuild()

# ----------------------------------------------------------------------
# Base para parámetros de consulta
# ----------------------------------------------------------------------

WhereType = TypeVar('WhereType')

class BaseListParams(BaseModel, Generic[WhereType]):
    where: Optional[WhereType] = None
    pagination: Optional[PaginationConfig] = None
    sort: Optional[SortConfig] = None