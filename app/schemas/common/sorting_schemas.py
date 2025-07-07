# app/schemas/common/sorting_schemas.py
# VERSIÓN SIMPLE SIN RootModel

from typing import List, Optional
from pydantic import BaseModel, Field, field_validator
from enum import Enum

class SortDirection(str, Enum):
    """Direcciones de ordenamiento permitidas"""
    ASC = "asc"
    DESC = "desc"

class SortColumn(BaseModel):
    """
    Representa una columna de ordenamiento con su dirección
    """
    column: str = Field(..., description="Nombre de la columna a ordenar")
    direction: SortDirection = Field(default=SortDirection.ASC, description="Dirección del ordenamiento")
    
    @field_validator('column')
    @classmethod
    def validate_column_name(cls, v):
        if not v or not v.strip():
            raise ValueError('El nombre de la columna no puede estar vacío')
        return v.strip()

# Usar Optional[List[SortColumn]] directamente en lugar de RootModel
SortConfig = Optional[List[SortColumn]]

# Helper functions para trabajar con SortConfig
class SortUtils:
    @staticmethod
    def is_empty(sort_config: SortConfig) -> bool:
        """Verifica si no hay columnas configuradas"""
        return not sort_config or len(sort_config) == 0
    
    @staticmethod
    def get_columns_dict(sort_config: SortConfig) -> dict:
        """Retorna un diccionario con las columnas y sus direcciones"""
        if not sort_config:
            return {}
        return {col.column: col.direction.value for col in sort_config}
    
    @staticmethod
    def validate_columns(sort_config: SortConfig) -> bool:
        """Valida la configuración de ordenamiento"""
        if not sort_config:
            return True
            
        if len(sort_config) > 10:
            raise ValueError('No se pueden ordenar por más de 10 columnas')
        
        # Verificar que no haya columnas duplicadas
        column_names = [col.column for col in sort_config]
        if len(column_names) != len(set(column_names)):
            raise ValueError('No se pueden repetir columnas en el ordenamiento')
        
        return True