#app/schemas/organizacion/unidad_organica_schemas.py

from pydantic import BaseModel, Field
from typing import Optional, Annotated
from datetime import datetime

from app.core.validators import (
    NombreType,
    SiglaType,
    DescripcionType,
    NivelUnidadType
)

class UnidadOrganicaBase(BaseModel):
    nombre: Annotated[str, NombreType] = Field(...)
    sigla: Annotated[str, SiglaType] = Field(...)
    tipo: str = Field(...)
    descripcion: Optional[Annotated[str, DescripcionType]] = Field(None)
    unidad_padre_id: Optional[int] = Field(None)
    nivel: Optional[Annotated[int, NivelUnidadType]] = Field(1)
    activa: bool = Field(default=True)

class UnidadOrganicaCreate(UnidadOrganicaBase):
    pass

class UnidadOrganicaUpdate(BaseModel):
    nombre: Optional[Annotated[str, NombreType]] = None
    sigla: Optional[Annotated[str, SiglaType]] = None
    tipo: Optional[str] = None
    descripcion: Optional[Annotated[str, DescripcionType]] = None
    unidad_padre_id: Optional[int] = None
    nivel: Optional[Annotated[int, NivelUnidadType]] = None
    activa: Optional[bool] = None

class UnidadOrganicaInDB(UnidadOrganicaBase):
    id: int
    uuid: str
    creado_por: Optional[int]
    fecha_creacion: datetime
    fecha_actualizacion: datetime

    class Config:
        from_attributes = True

class UnidadOrganicaRead(UnidadOrganicaInDB):
    pass
