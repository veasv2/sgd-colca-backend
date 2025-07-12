# app/services/base_summary_service.py

from typing import Type, TypeVar, Generic, List, Dict, Any
from sqlalchemy.orm import Session
from sqlalchemy import func, and_
from fastapi import HTTPException, status
from pydantic import BaseModel

from app.utils.filter_engine import FilterEngine
from app.schemas.common.summary_schemas import SummaryRequest, SummaryResponse, SummaryItem

# Types genéricos
ModelType = TypeVar('ModelType')
WhereType = TypeVar('WhereType')

class BaseSummaryService(Generic[ModelType, WhereType]):
    
    def generar_resumen(
        self,
        db: Session,
        model_class: Type[ModelType],
        request: SummaryRequest[WhereType],
        allowed_group_columns: List[str] = None
    ) -> SummaryResponse:
        try:
            # Validar columna de agrupación
            if allowed_group_columns and request.groupBy not in allowed_group_columns:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail=f"Columna '{request.groupBy}' no permitida para agrupación. "
                           f"Columnas permitidas: {allowed_group_columns}"
                )
            
            # Verificar que la columna existe en el modelo
            if not hasattr(model_class, request.groupBy):
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail=f"Columna '{request.groupBy}' no existe en el modelo"
                )
            
            # Obtener la columna para agrupar
            group_column = getattr(model_class, request.groupBy)
            
            # Crear consulta base para el conteo total
            total_query = db.query(func.count(model_class.id))
            
            # Crear consulta para agrupación
            group_query = db.query(
                group_column.label('group'),
                func.count(model_class.id).label('count')
            )
            
            # Aplicar filtros si existen
            if request.where:
                total_query = FilterEngine.apply_filters(total_query, model_class, request.where)
                group_query = FilterEngine.apply_filters(group_query, model_class, request.where)
            
            # Aplicar rango de fechas si existe
            if request.dateRange:
                date_conditions = self._build_date_conditions(model_class, request.dateRange)
                if date_conditions:
                    total_query = total_query.filter(and_(*date_conditions))
                    group_query = group_query.filter(and_(*date_conditions))
            
            # Ejecutar consulta de total
            total = total_query.scalar() or 0
            
            # Ejecutar consulta de agrupación
            group_results = group_query.group_by(group_column).all()
            
            # Convertir resultados a SummaryItem
            groups = []
            for result in group_results:
                groups.append(SummaryItem(
                    group=str(result.group) if result.group is not None else "Sin clasificar",
                    count=result.count
                ))
            
            # Ordenar grupos por count descendente
            groups.sort(key=lambda x: x.count, reverse=True)
            
            return SummaryResponse(
                total=total,
                groups=groups
            )
            
        except HTTPException:
            raise
        except Exception as e:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Error al generar resumen: {str(e)}"
            )
    
    def _build_date_conditions(self, model_class: Type[ModelType], date_range: Dict[str, Any]) -> List:
        conditions = []
        
        if not date_range:
            return conditions
        
        date_field_name = date_range.get('field', 'fecha_creacion')
        date_from = date_range.get('from')
        date_to = date_range.get('to')
        
        # Verificar que el campo existe
        if not hasattr(model_class, date_field_name):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Campo de fecha '{date_field_name}' no existe en el modelo"
            )
        
        date_field = getattr(model_class, date_field_name)
        
        if date_from:
            conditions.append(date_field >= date_from)
        
        if date_to:
            conditions.append(date_field <= date_to)
        
        return conditions
    
    def validate_group_column(self, model_class: Type[ModelType], column_name: str, allowed_columns: List[str] = None):
        """Valida que una columna sea válida para agrupación"""
        if allowed_columns and column_name not in allowed_columns:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Columna '{column_name}' no permitida para agrupación"
            )
        
        if not hasattr(model_class, column_name):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Columna '{column_name}' no existe en el modelo"
            )