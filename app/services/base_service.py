# app/services/base_service.py

from typing import Any, Type, TypeVar, Generic, List, Protocol
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func
from fastapi import HTTPException, status
from pydantic import BaseModel
from abc import ABC, abstractmethod

from app.utils.filter_engine import FilterEngine
from app.utils.sort_engine import SortEngine
from app.schemas.common.filter_schemas import BaseListParams, PaginationConfig
from app.schemas.common.sorting_schemas import SortConfig, SortUtils
from app.repositories.base_repository import IBaseRepository

# Types genéricos
ModelType = TypeVar('ModelType')
WhereType = TypeVar('WhereType')
ResponseType = TypeVar('ResponseType', bound=BaseModel)
CreateSchemaType = TypeVar('CreateSchemaType')
UpdateSchemaType = TypeVar('UpdateSchemaType')

class IBaseService(Protocol[ModelType, CreateSchemaType, UpdateSchemaType]):
    """Interfaz/Protocolo para servicios base"""
    
    async def create(self, db: AsyncSession, obj_in: CreateSchemaType) -> ModelType:
        """Crear nueva entidad"""
        ...
    
    async def get_by_uuid(self, db: AsyncSession, uuid: str) -> ModelType:
        """Obtener entidad por UUID"""
        ...
    
    async def update_by_uuid(self, db: AsyncSession, uuid: str, obj_in: UpdateSchemaType) -> ModelType:
        """Actualizar entidad por UUID"""
        ...
    
    async def delete_by_uuid(self, db: AsyncSession, uuid: str) -> bool:
        """Eliminar entidad por UUID"""
        ...

class BaseService(Generic[ModelType, CreateSchemaType, UpdateSchemaType], ABC):
    """
    Servicio base asíncrono que implementa patrón Repository + Service
    
    RESPONSABILIDADES:
    - Lógica de negocio
    - Validaciones
    - Orquestación de operaciones
    - Trabajo EXCLUSIVO con UUIDs (nunca con IDs internos)
    """
    
    def __init__(self, repository: IBaseRepository[ModelType, CreateSchemaType, UpdateSchemaType]):
        self.repository = repository

    async def create(self, db: AsyncSession, obj_in: CreateSchemaType) -> ModelType:
        """Crear nueva entidad (la lógica de negocio puede ser sobrescrita)"""
        return await self.repository.create(db, obj_in)

    async def get_by_uuid(self, db: AsyncSession, uuid: str) -> ModelType:
        """Obtener entidad por UUID"""
        entity = await self.repository.get_by_uuid(db, uuid)
        if not entity:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Entidad no encontrada"
            )
        return entity

    async def update_by_uuid(self, db: AsyncSession, uuid: str, obj_in: UpdateSchemaType) -> ModelType:
        """Actualizar entidad por UUID"""
        entity = await self.repository.update_by_uuid(db, uuid, obj_in)
        if not entity:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Entidad no encontrada"
            )
        return entity

    async def delete_by_uuid(self, db: AsyncSession, uuid: str) -> bool:
        """Eliminar entidad por UUID"""
        entity = await self.repository.delete_by_uuid(db, uuid)
        return entity is not None

    async def exists_by_uuid(self, db: AsyncSession, uuid: str) -> bool:
        """Verificar si existe entidad por UUID"""
        return await self.repository.exists_by_uuid(db, uuid)

class BaseListService(Generic[ModelType, WhereType, ResponseType]):
    """
    Servicio base asíncrono para operaciones de listado con filtros avanzados
    
    MANTIENE toda la funcionalidad de filtrado, ordenamiento y paginación existente
    """
    
    def __init__(self, repository: IBaseRepository[ModelType, Any, Any] = None):
        self.repository = repository

    async def lista_entidades(
        self,
        db: AsyncSession,
        model_class: Type[ModelType],
        request: BaseListParams[WhereType],
        response_class: Type[ResponseType],
        allowed_sort_columns: List[str] = None,
        excluded_columns: List[str] = None
    ) -> ResponseType:
        try:
            # Crear consulta base - siempre seleccionar el modelo completo
            stmt = select(model_class)
            
            # Aplicar filtros
            if request.where:
                stmt = FilterEngine.apply_filters(stmt, model_class, request.where)
            
            # Aplicar ordenamiento
            if request.sort and not SortUtils.is_empty(request.sort):
                # Validar columnas permitidas si se especifican
                if allowed_sort_columns:
                    SortEngine.validate_sortable_columns(model_class, request.sort, allowed_sort_columns)
                
                stmt = SortEngine.apply_sorting(stmt, model_class, request.sort)
            
            # Aplicar paginación
            pagination = request.pagination or PaginationConfig(page=1, pageSize=10)
            data, metadata = await FilterEngine.apply_pagination(db, stmt, pagination)
            
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
    
    async def build_search_conditions(self, model_class: Type[ModelType], search_term: str, search_fields: list[str]) -> list:
        """Construye condiciones de búsqueda para campos específicos"""
        from sqlalchemy import or_
        
        conditions = []
        for field_name in search_fields:
            if hasattr(model_class, field_name):
                field = getattr(model_class, field_name)
                conditions.append(field.ilike(f"%{search_term}%"))
        
        return [or_(*conditions)] if conditions else []

class CommonListService:
    """Servicios comunes para listados (mantenido sin cambios)"""
    
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