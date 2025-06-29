# app/schemas/seguridad/usuario_schemas.py

from pydantic import BaseModel, Field
from typing import Optional, Annotated
from datetime import datetime

from app.core.validators import (
    UsernameType,
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

class UsuarioBase(BaseModel):
    username: Annotated[str, UsernameType] = Field(...)
    email: Annotated[str, EmailInstitucionalType] = Field(...)
    nombres: Annotated[str, NombreType] = Field(...)
    apellidos: Annotated[str, NombreType] = Field(...)
    dni: Optional[Annotated[str, DNIPeruanoType]] = None
    telefono: Optional[Annotated[str, TelefonoType]] = None
    tipo_usuario: TipoUsuario = Field(...)
    estado: EstadoUsuario = Field(default=EstadoUsuario.ACTIVO)
    puesto_id: Optional[int] = Field(None)

class UsuarioCreate(UsuarioBase):
    password: Annotated[str, Field(min_length=8)] = Field(...)

class UsuarioUpdate(BaseModel):
    username: Optional[Annotated[str, UsernameType]] = None
    email: Optional[Annotated[str, EmailInstitucionalType]] = None
    nombres: Optional[Annotated[str, NombreType]] = None
    apellidos: Optional[Annotated[str, NombreType]] = None
    dni: Optional[Annotated[str, DNIPeruanoType]] = None
    telefono: Optional[Annotated[str, TelefonoType]] = None
    tipo_usuario: Optional[TipoUsuario] = None
    estado: Optional[EstadoUsuario] = None
    puesto_id: Optional[int] = None
    password: Optional[Annotated[str, Field(min_length=8)]] = None

class UsuarioInDB(UsuarioBase):
    id: int
    uuid: str
    intentos_fallidos: int
    bloqueado_hasta: Optional[datetime]
    ultimo_acceso: Optional[datetime]
    fecha_creacion: datetime
    fecha_actualizacion: datetime

    class Config:
        from_attributes = True

class UsuarioRead(UsuarioInDB):
    pass
