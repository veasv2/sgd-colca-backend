# app/services/base_service.py

from typing import Any, Type, TypeVar, Generic, List
from sqlalchemy.orm import Session
from sqlalchemy import text
from fastapi import HTTPException, status
from pydantic import BaseModel

from app.utils.filter_engine import FilterEngine
from app.utils.sort_engine import SortEngine
from app.schemas.common.filter_schemas import BaseListParams, PaginationConfig
from app.schemas.common.sorting_schemas import SortConfig, SortUtils

# Types genéricos
ModelType = TypeVar('ModelType')
WhereType = TypeVar('WhereType')
ResponseType = TypeVar('ResponseType', bound=BaseModel)

class BaseListService(Generic[ModelType, WhereType, ResponseType]):
    def lista_entidades(
        self,
        db: Session,
        model_class: Type[ModelType],
        request: BaseListParams[WhereType],
        response_class: Type[ResponseType],
        allowed_sort_columns: List[str] = None,
        excluded_columns: List[str] = None
    ) -> ResponseType:
        try:
            # Crear consulta base
            if excluded_columns:
                # Seleccionar solo las columnas que NO están excluidas
                columns_to_select = []
                for column in model_class.__table__.columns:
                    if column.name not in excluded_columns:
                        columns_to_select.append(column)
                
                query = db.query(*columns_to_select)
            else:
                query = db.query(model_class)
            
            # Aplicar filtros
            if request.where:
                query = FilterEngine.apply_filters(query, model_class, request.where)
            
            # Aplicar ordenamiento
            if request.sort and not SortUtils.is_empty(request.sort):
                # Validar columnas permitidas si se especifican
                if allowed_sort_columns:
                    SortEngine.validate_sortable_columns(model_class, request.sort, allowed_sort_columns)
                
                query = SortEngine.apply_sorting(query, model_class, request.sort)
            
            # Aplicar paginación
            pagination = request.pagination or PaginationConfig(page=1, pageSize=10)
            data, metadata = FilterEngine.apply_pagination(query, pagination)
            
            # Preparar respuesta
            response_data = {
                "data": data,
                **metadata
            }
            
            # Agregar información de ordenamiento si está disponible en el response
            if hasattr(response_class, '__fields__') and 'appliedSort' in response_class.__fields__:
                if request.sort and not SortUtils.is_empty(request.sort):
                    response_data["appliedSort"] = request.sort
            
            return response_class(**response_data)
            
        except Exception as e:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Error al obtener lista de entidades: {str(e)}"
            )
    
    def validate_pagination(self, pagination: PaginationConfig) -> PaginationConfig:
        """Valida y corrige parámetros de paginación"""
        if pagination.page < 1:
            pagination.page = 1
        
        if pagination.pageSize < 1:
            pagination.pageSize = 10
        elif pagination.pageSize > 1000:  # Límite máximo
            pagination.pageSize = 1000
            
        return pagination
    
    def build_search_conditions(self, model_class: Type[ModelType], search_term: str, search_fields: list[str]) -> list:
        """Construye condiciones de búsqueda para campos específicos"""
        from sqlalchemy import or_
        
        conditions = []
        for field_name in search_fields:
            if hasattr(model_class, field_name):
                field = getattr(model_class, field_name)
                conditions.append(field.ilike(f"%{search_term}%"))
        
        return [or_(*conditions)] if conditions else []

class CommonListService:
    """Servicios comunes para listados"""
    
    @staticmethod
    def build_quick_filters(where_obj: Any, search_term: str = None, active_only: bool = False):
        """Construye filtros rápidos comunes"""
        if search_term and hasattr(where_obj, 'nombres'):
            where_obj.nombres = {"contains": search_term}
        
        if active_only and hasattr(where_obj, 'estado'):
            where_obj.estado = {"equals": "ACTIVO"}
        
        return where_obj
    
    @staticmethod
    def validate_date_range(fecha_desde: str = None, fecha_hasta: str = None) -> dict:
        """Valida y construye filtros de rango de fechas"""
        date_filter = {}
        
        if fecha_desde:
            date_filter["gte"] = fecha_desde
        
        if fecha_hasta:
            date_filter["lte"] = fecha_hasta
            
        return date_filter if date_filter else None