# app/schemas/unidad_organica.py
from pydantic import BaseModel, Field, UUID4
from typing import Optional, List
from datetime import datetime


class UnidadOrganicaBase(BaseModel):
    """Schema base - Define campos comunes UNA sola vez"""
    codigo: str = Field(..., min_length=1, max_length=10, description="Código único de la unidad orgánica")
    nombre: str = Field(..., min_length=1, max_length=200, description="Nombre de la unidad orgánica")
    descripcion: Optional[str] = Field(None, max_length=1000, description="Descripción de la unidad orgánica")
    unidad_padre_id: Optional[UUID4] = Field(None, description="ID de la unidad orgánica padre")
    nivel: int = Field(1, ge=1, le=5, description="Nivel en la jerarquía organizacional (1-5)")


class UnidadOrganicaCreate(UnidadOrganicaBase):
    """Para crear - hereda todo de Base con validaciones completas"""
    pass


class UnidadOrganicaUpdate(BaseModel):
    """Para updates parciales - todos los campos opcionales"""
    # NO hereda de Base para evitar campos obligatorios
    codigo: Optional[str] = Field(None, min_length=1, max_length=10)
    nombre: Optional[str] = Field(None, min_length=1, max_length=200) 
    descripcion: Optional[str] = Field(None, max_length=1000)
    unidad_padre_id: Optional[UUID4] = None
    nivel: Optional[int] = Field(None, ge=1, le=5)


class UnidadOrganicaResponse(UnidadOrganicaBase):
    """Para respuestas - hereda Base + campos de BD"""
    id: UUID4
    activo: bool
    created_at: datetime
    updated_at: Optional[datetime] = None
    
    class Config:
        from_attributes = True


class UnidadOrganicaList(BaseModel):
    """Para listas paginadas"""
    total: int
    items: List[UnidadOrganicaResponse]