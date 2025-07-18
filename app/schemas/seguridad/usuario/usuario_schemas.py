# app/schemas/seguridad/usuario_schemas.py

from pydantic import BaseModel, Field
from typing import Optional, Annotated
from datetime import datetime

from app.core.validators import (
    EmailInstitucionalType,
    NombreType,
    DNIPeruanoType,
    TelefonoType,
)

from enum import Enum

class TipoUsuario(str, Enum):
    SUPERADMIN = "SUPERADMIN"
    ALCALDE = "ALCALDE"
    FUNCIONARIO = "FUNCIONARIO"

class EstadoUsuario(str, Enum):
    ACTIVO = "ACTIVO"
    INACTIVO = "INACTIVO"
    SUSPENDIDO = "SUSPENDIDO"
    BAJA = "BAJA"
    PENDIENTE = "PENDIENTE"

class UsuarioBase(BaseModel):
    email: Annotated[str, EmailInstitucionalType] = Field(...)
    nombres: Annotated[str, NombreType] = Field(...)
    apellido_paterno: Annotated[str, NombreType] = Field(...)
    apellido_materno: Annotated[str, NombreType] = Field(...)
    dni: Optional[Annotated[str, DNIPeruanoType]] = None
    telefono: Optional[Annotated[str, TelefonoType]] = None
    tipo: TipoUsuario = Field(...)
    estado: EstadoUsuario = Field(default=EstadoUsuario.ACTIVO)

class UsuarioCreate(UsuarioBase):
    password: Annotated[str, Field(min_length=8)] = Field(...)

class UsuarioUpdate(BaseModel):
    email: Optional[Annotated[str, EmailInstitucionalType]] = None
    nombres: Optional[Annotated[str, NombreType]] = None
    apellido_paterno: Optional[Annotated[str, NombreType]] = None
    apellido_materno: Optional[Annotated[str, NombreType]] = None
    dni: Optional[Annotated[str, DNIPeruanoType]] = None
    telefono: Optional[Annotated[str, TelefonoType]] = None
    tipo: Optional[TipoUsuario] = None
    estado: Optional[EstadoUsuario] = None
    password: Optional[Annotated[str, Field(min_length=8)]] = None

class UsuarioInDB(UsuarioBase):
    id: int
    uuid: str
    intentos_fallidos: int
    bloqueado_hasta: Optional[datetime] = None
    ultimo_acceso: Optional[datetime] = None
    fecha_creacion: datetime
    fecha_actualizacion: datetime
    # password_hash: str  # Normalmente no lo incluimos en respuestas

    class Config:
        from_attributes = True
