# app/schemas/seguridad/permiso_schemas.py

from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime
from enum import Enum

class TipoPermiso(str, Enum):
    LECTURA = "LECTURA"
    ESCRITURA = "ESCRITURA"
    ADMINISTRACION = "ADMINISTRACION"
    CONFIGURACION = "CONFIGURACION"

class PermisoBase(BaseModel):
    codigo: str = Field(..., min_length=3, max_length=50)
    nombre: str = Field(..., min_length=3, max_length=100)
    descripcion: Optional[str] = Field(None, max_length=500)
    modulo: str = Field(..., min_length=3, max_length=50)
    tipo_permiso: TipoPermiso = Field(...)
    activo: bool = Field(default=True)

class PermisoCreate(PermisoBase):
    pass

class PermisoUpdate(BaseModel):
    nombre: Optional[str] = None
    descripcion: Optional[str] = None
    modulo: Optional[str] = None
    tipo_permiso: Optional[TipoPermiso] = None
    activo: Optional[bool] = None

class PermisoRead(PermisoBase):
    id: int
    fecha_creacion: datetime
