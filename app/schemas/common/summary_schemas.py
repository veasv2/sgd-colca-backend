# app/schemas/common/summary_schemas.py

from typing import Optional, List, Any, Dict, Generic, TypeVar
from pydantic import BaseModel, Field

# Type genérico para el where
WhereType = TypeVar('WhereType')

class SummaryItem(BaseModel):
    group: str = Field(..., description="Valor del grupo")
    count: int = Field(..., description="Cantidad de registros en este grupo")

class SummaryRequest(BaseModel, Generic[WhereType]):
    groupBy: str = Field(..., description="Campo por el cual agrupar")
    where: Optional[WhereType] = Field(None, description="Filtros a aplicar (mismo que en lista)")
    dateRange: Optional[Dict[str, Any]] = Field(None, description="Rango de fechas opcional")
    
    class Config:
        arbitrary_types_allowed = True

class SummaryResponse(BaseModel):
    total: int = Field(..., description="Total de registros")
    groups: List[SummaryItem] = Field(..., description="Grupos con sus conteos")
    
    class Config:
        from_attributes = True