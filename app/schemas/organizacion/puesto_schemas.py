#app/schemas/organizacion/puesto_schemas.py

from pydantic import BaseModel, Field
from typing import Optional, Annotated
from datetime import datetime

from app.core.validators import (
    NombreType,
    CodigoPuestoType,
    DescripcionType,
    NivelPuestoType
)

class PuestoBase(BaseModel):
    nombre: Annotated[str, NombreType] = Field(...)
    codigo: Annotated[str, CodigoPuestoType] = Field(...)
    descripcion: Optional[Annotated[str, DescripcionType]] = Field(None)
    unidad_organica_id: int = Field(...)
    puesto_superior_id: Optional[int] = Field(None)
    nivel_jerarquico: Annotated[int, NivelPuestoType]
    activo: bool = Field(default=True)

class PuestoCreate(PuestoBase):
    pass

class PuestoUpdate(BaseModel):
    nombre: Optional[Annotated[str, NombreType]] = None
    codigo: Optional[Annotated[str, CodigoPuestoType]] = None
    descripcion: Optional[Annotated[str, DescripcionType]] = None
    unidad_organica_id: Optional[int] = None
    puesto_superior_id: Optional[int] = None
    nivel_jerarquico: Optional[Annotated[int, NivelPuestoType]] = None
    activo: Optional[bool] = None

class PuestoInDB(PuestoBase):
    id: int
    uuid: str
    creado_por: Optional[int]
    fecha_creacion: datetime
    fecha_actualizacion: datetime

    class Config:
        from_attributes = True

class PuestoRead(PuestoInDB):
    pass
