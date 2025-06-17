"""
Schemas Pydantic para Usuario
"""
from typing import Optional
from datetime import datetime
from pydantic import BaseModel, EmailStr
from uuid import UUID

# Schema base
class UsuarioBase(BaseModel):
    email: EmailStr
    nombres: str
    apellidos: str
    dni: Optional[str] = None
    telefono: Optional[str] = None
    es_superadmin: bool = False
    activo: bool = True

# Schema para crear usuario
class UsuarioCreate(UsuarioBase):
    firebase_uid: str
    puesto_id: Optional[UUID] = None

# Schema para actualizar usuario
class UsuarioUpdate(BaseModel):
    nombres: Optional[str] = None
    apellidos: Optional[str] = None
    dni: Optional[str] = None
    telefono: Optional[str] = None
    puesto_id: Optional[UUID] = None
    activo: Optional[bool] = None

# Schema para respuesta (lo que devuelve la API)
class UsuarioResponse(UsuarioBase):
    id: UUID
    firebase_uid: str
    puesto_id: Optional[UUID] = None
    ultimo_acceso: Optional[datetime] = None
    created_at: datetime
    updated_at: datetime
    
    # Información del puesto (join)
    puesto_nombre: Optional[str] = None
    unidad_nombre: Optional[str] = None

    class Config:
        from_attributes = True  # Para SQLAlchemy ORM

# Schema para listado con paginación
class UsuarioList(BaseModel):
    success: bool
    data: list[UsuarioResponse]
    total: int
    page: int
    per_page: int
