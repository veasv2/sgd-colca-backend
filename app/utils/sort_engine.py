# app/utils/sort_engine.py

from typing import Type, List
from sqlalchemy.orm import Query
from sqlalchemy import desc, asc
from app.schemas.common.sorting_schemas import SortConfig, SortColumn, SortDirection, SortUtils

class SortEngine:
    @staticmethod
    def apply_sorting(query: Query, model_class: Type, sort_config: SortConfig) -> Query:
        if SortUtils.is_empty(sort_config):
            return query
        
        try:
            for sort_column in sort_config:
                column_attr = SortEngine._get_column_attribute(model_class, sort_column.column)
                
                if sort_column.direction == SortDirection.DESC:
                    query = query.order_by(desc(column_attr))
                else:
                    query = query.order_by(asc(column_attr))
            
            return query
            
        except Exception as e:
            raise ValueError(f"Error al aplicar ordenamiento: {str(e)}")
    
    @staticmethod
    def _get_column_attribute(model_class: Type, column_name: str):      
        if not hasattr(model_class, column_name):
            raise AttributeError(f"El modelo {model_class.__name__} no tiene la columna '{column_name}'")
        
        return getattr(model_class, column_name)
    
    @staticmethod
    def validate_sortable_columns(model_class: Type, sort_config: SortConfig, allowed_columns: List[str] = None) -> bool:        
        if SortUtils.is_empty(sort_config):
            return True
        
        for sort_column in sort_config:
            column_name = sort_column.column
            
            # Verificar si la columna existe en el modelo
            if not hasattr(model_class, column_name):
                raise ValueError(f"La columna '{column_name}' no existe en el modelo {model_class.__name__}")
            
            # Verificar si la columna está en la lista de columnas permitidas
            if allowed_columns and column_name not in allowed_columns:
                raise ValueError(f"La columna '{column_name}' no está permitida para ordenamiento")
        
        return True
    
    @staticmethod
    def create_default_sort(column: str, direction: SortDirection = SortDirection.ASC) -> SortConfig:       
        return [SortColumn(column=column, direction=direction)]
    
    @staticmethod
    def get_sql_order_by_string(sort_config: SortConfig) -> str:

        if SortUtils.is_empty(sort_config):
            return ""
        
        order_parts = []
        for sort_column in sort_config:
            direction = "DESC" if sort_column.direction == SortDirection.DESC else "ASC"
            order_parts.append(f"{sort_column.column} {direction}")
        
        return f"ORDER BY {', '.join(order_parts)}"