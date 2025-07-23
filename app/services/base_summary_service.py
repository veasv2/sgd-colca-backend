# app/services/base_summary_service.py

from typing import Type, TypeVar, Generic, List, Dict, Any
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import func, and_, select
from fastapi import HTTPException, status
from pydantic import BaseModel

from app.utils.filter_engine import FilterEngine
from app.schemas.common.summary_schemas import SummaryRequest, SummaryResponse, SummaryItem

# Types genéricos
ModelType = TypeVar('ModelType')
WhereType = TypeVar('WhereType')

class BaseSummaryService(Generic[ModelType, WhereType]):
    """
    Servicio base asíncrono para generar resúmenes agrupados
    
    MANTIENE toda la funcionalidad de resúmenes existente, ahora asíncrona
    """
    
    async def generar_resumen(
        self,
        db: AsyncSession,
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
            total_stmt = select(func.count(model_class.id))
            
            # Crear consulta para agrupación
            group_stmt = select(
                group_column.label('group'),
                func.count(model_class.id).label('count')
            ).group_by(group_column)
            
            # Aplicar filtros si existen
            if request.where:
                total_stmt = FilterEngine.apply_filters(total_stmt, model_class, request.where)
                group_stmt = FilterEngine.apply_filters(group_stmt, model_class, request.where)
            
            # Aplicar rango de fechas si existe
            if hasattr(request, 'dateRange') and request.dateRange:
                date_conditions = self._build_date_conditions(model_class, request.dateRange)
                if date_conditions:
                    total_stmt = total_stmt.where(and_(*date_conditions))
                    group_stmt = group_stmt.where(and_(*date_conditions))
            
            # Ejecutar consultas asíncronamente
            total_result = await db.execute(total_stmt)
            total = total_result.scalar() or 0
            
            group_result = await db.execute(group_stmt)
            groups_data = group_result.fetchall()
            
            # Preparar grupos para respuesta
            groups = []
            for row in groups_data:
                groups.append(SummaryItem(
                    group=str(row.group) if row.group is not None else "Sin clasificar",
                    count=row.count
                ))
            
            # Ordenar por conteo descendente por defecto
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

    async def generar_resumen_personalizado(
        self,
        db: AsyncSession,
        model_class: Type[ModelType],
        group_by_column: str,
        where_filters: WhereType = None,
        order_by_count: bool = True
    ) -> Dict[str, Any]:
        """
        Genera un resumen personalizado con más flexibilidad
        """
        try:
            if not hasattr(model_class, group_by_column):
                raise ValueError(f"Columna '{group_by_column}' no existe en el modelo")
            
            group_column = getattr(model_class, group_by_column)
            
            # Crear consulta
            stmt = select(
                group_column.label('group'),
                func.count(model_class.id).label('count')
            ).group_by(group_column)
            
            # Aplicar filtros
            if where_filters:
                stmt = FilterEngine.apply_filters(stmt, model_class, where_filters)
            
            # Ordenamiento
            if order_by_count:
                stmt = stmt.order_by(func.count(model_class.id).desc())
            
            result = await db.execute(stmt)
            data = result.fetchall()
            
            # Calcular total
            total = sum(row.count for row in data)
            
            return {
                "total": total,
                "groups": [
                    {
                        "group": str(row.group) if row.group is not None else "Sin definir",
                        "count": row.count,
                        "percentage": round((row.count / total) * 100, 2) if total > 0 else 0
                    }
                    for row in data
                ]
            }
            
        except Exception as e:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Error al generar resumen personalizado: {str(e)}"
            )

    def _build_date_conditions(self, model_class: Type[ModelType], date_range: Dict[str, Any]) -> List:
        """Construir condiciones de filtro por fechas"""
        conditions = []
        
        if not date_range:
            return conditions
        
        date_field_name = date_range.get('field', 'fecha_creacion')
        date_from = date_range.get('from')
        date_to = date_range.get('to')
        
        if not hasattr(model_class, date_field_name):
            return conditions
        
        date_field = getattr(model_class, date_field_name)
        
        if date_from:
            conditions.append(date_field >= date_from)
        
        if date_to:
            conditions.append(date_field <= date_to)
        
        return conditions
