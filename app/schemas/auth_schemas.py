# app/schemas/auth_schemas.py
"""
Esquemas Pydantic para Control de Acceso - Sistema de Gobernanza Digital (SGD)
Municipalidad Distrital de Colca

Estos esquemas definen la estructura de datos para validación de entrada y salida
"""

from pydantic import BaseModel, EmailStr, Field, validator
from typing import Optional, List
from datetime import datetime
from enum import Enum

# === ENUMS PARA VALIDACIÓN ===

class TipoUsuarioEnum(str, Enum):
    """Tipos de usuario según el diseño del sistema"""
    SUPERADMIN = "SUPERADMIN"
    ALCALDE = "ALCALDE"
    FUNCIONARIO = "FUNCIONARIO"

class EstadoUsuarioEnum(str, Enum):
    """Estados posibles de un usuario"""
    ACTIVO = "ACTIVO"
    INACTIVO = "INACTIVO"
    SUSPENDIDO = "SUSPENDIDO"

class TipoPermisoEnum(str, Enum):
    """Categorías de permisos del sistema"""
    LECTURA = "LECTURA"
    ESCRITURA = "ESCRITURA"
    ADMINISTRACION = "ADMINISTRACION"
    CONFIGURACION = "CONFIGURACION"

# === ESQUEMAS BASE ===

class BaseSchema(BaseModel):
    """Esquema base con configuración común"""
    
    class Config:
        from_attributes = True
        str_strip_whitespace = True
        validate_assignment = True

# === ESQUEMAS DE ÁREA ===

class AreaBase(BaseSchema):
    """Campos base para un área organizacional"""
    codigo: str = Field(..., min_length=2, max_length=10, description="Código único del área")
    nombre: str = Field(..., min_length=3, max_length=100, description="Nombre del área")
    descripcion: Optional[str] = Field(None, max_length=500, description="Descripción del área")
    nivel: int = Field(1, ge=1, le=10, description="Nivel jerárquico")
    activa: bool = Field(True, description="Estado del área")
    
    @validator('codigo')
    def validate_codigo(cls, v):
        if not v.isupper():
            raise ValueError('El código debe estar en mayúsculas')
        return v

class AreaCreate(AreaBase):
    """Esquema para crear un área"""
    area_padre_id: Optional[int] = Field(None, description="ID del área padre")

class AreaUpdate(BaseSchema):
    """Esquema para actualizar un área"""
    codigo: Optional[str] = Field(None, min_length=2, max_length=10)
    nombre: Optional[str] = Field(None, min_length=3, max_length=100)
    descripcion: Optional[str] = Field(None, max_length=500)
    area_padre_id: Optional[int] = None
    nivel: Optional[int] = Field(None, ge=1, le=10)
    activa: Optional[bool] = None

class AreaResponse(AreaBase):
    """Esquema de respuesta para un área"""
    id: int
    uuid: str
    fecha_creacion: datetime
    fecha_actualizacion: Optional[datetime] = None
    
    # Relaciones anidadas (opcional)
    sub_areas: Optional[List['AreaResponse']] = []

# === ESQUEMAS DE PUESTO ===

class PuestoBase(BaseSchema):
    """Campos base para un puesto del organigrama"""
    codigo: str = Field(..., min_length=3, max_length=20, description="Código único del puesto")
    nombre: str = Field(..., min_length=3, max_length=100, description="Nombre del puesto")
    descripcion: Optional[str] = Field(None, max_length=500, description="Descripción del puesto")
    nivel_jerarquico: int = Field(..., ge=1, le=20, description="Nivel jerárquico del puesto")
    activo: bool = Field(True, description="Estado del puesto")

class PuestoCreate(PuestoBase):
    """Esquema para crear un puesto"""
    area_id: int = Field(..., description="ID del área a la que pertenece")
    puesto_superior_id: Optional[int] = Field(None, description="ID del puesto superior")

class PuestoUpdate(BaseSchema):
    """Esquema para actualizar un puesto"""
    codigo: Optional[str] = Field(None, min_length=3, max_length=20)
    nombre: Optional[str] = Field(None, min_length=3, max_length=100)
    descripcion: Optional[str] = Field(None, max_length=500)
    area_id: Optional[int] = None
    puesto_superior_id: Optional[int] = None
    nivel_jerarquico: Optional[int] = Field(None, ge=1, le=20)
    activo: Optional[bool] = None

class PuestoResponse(PuestoBase):
    """Esquema de respuesta para un puesto"""
    id: int
    uuid: str
    area_id: int
    puesto_superior_id: Optional[int] = None
    fecha_creacion: datetime
    fecha_actualizacion: Optional[datetime] = None

# === ESQUEMAS DE USUARIO ===

class UsuarioBase(BaseSchema):
    """Campos base para un usuario"""
    username: str = Field(..., min_length=3, max_length=50, description="Nombre de usuario único")
    email: str = Field(..., description="Correo electrónico único")
    nombres: str = Field(..., min_length=2, max_length=100, description="Nombres del usuario")
    apellidos: str = Field(..., min_length=2, max_length=100, description="Apellidos del usuario")
    dni: Optional[str] = Field(None, min_length=8, max_length=8, description="DNI del usuario")
    telefono: Optional[str] = Field(None, max_length=15, description="Teléfono del usuario")
    tipo_usuario: TipoUsuarioEnum = Field(..., description="Tipo de usuario")
    estado: EstadoUsuarioEnum = Field(EstadoUsuarioEnum.ACTIVO, description="Estado del usuario")
    
    @validator('dni')
    def validate_dni(cls, v):
        if v and not v.isdigit():
            raise ValueError('El DNI debe contener solo números')
        return v
    
    @validator('username')
    def validate_username(cls, v):
        if not v.isalnum():
            raise ValueError('El username debe contener solo letras y números')
        return v.lower()

class UsuarioCreate(UsuarioBase):
    """Esquema para crear un usuario"""
    password: str = Field(..., min_length=8, description="Contraseña del usuario")
    puesto_id: Optional[int] = Field(None, description="ID del puesto asignado")
    
    @validator('password')
    def validate_password(cls, v):
        if len(v) < 8:
            raise ValueError('La contraseña debe tener al menos 8 caracteres')
        if not any(c.isupper() for c in v):
            raise ValueError('La contraseña debe tener al menos una mayúscula')
        if not any(c.islower() for c in v):
            raise ValueError('La contraseña debe tener al menos una minúscula')
        if not any(c.isdigit() for c in v):
            raise ValueError('La contraseña debe tener al menos un número')
        return v

class UsuarioUpdate(BaseSchema):
    """Esquema para actualizar un usuario"""
    email: Optional[str] = None
    nombres: Optional[str] = Field(None, min_length=2, max_length=100)
    apellidos: Optional[str] = Field(None, min_length=2, max_length=100)
    dni: Optional[str] = Field(None, min_length=8, max_length=8)
    telefono: Optional[str] = Field(None, max_length=15)
    tipo_usuario: Optional[TipoUsuarioEnum] = None
    estado: Optional[EstadoUsuarioEnum] = None
    puesto_id: Optional[int] = None

class UsuarioResponse(UsuarioBase):
    """Esquema de respuesta para un usuario (sin contraseña)"""
    id: int
    uuid: str
    puesto_id: Optional[int] = None
    ultimo_acceso: Optional[datetime] = None
    fecha_creacion: datetime
    fecha_actualizacion: Optional[datetime] = None
    
    # Relaciones anidadas (opcional)
    puesto: Optional[PuestoResponse] = None

# === ESQUEMAS DE PERMISO ===

class PermisoBase(BaseSchema):
    """Campos base para un permiso"""
    codigo: str = Field(..., min_length=3, max_length=50, description="Código único del permiso")
    nombre: str = Field(..., min_length=3, max_length=100, description="Nombre descriptivo")
    descripcion: Optional[str] = Field(None, max_length=500, description="Descripción del permiso")
    modulo: str = Field(..., min_length=3, max_length=50, description="Módulo del sistema")
    tipo_permiso: TipoPermisoEnum = Field(..., description="Tipo de permiso")
    activo: bool = Field(True, description="Estado del permiso")

class PermisoCreate(PermisoBase):
    """Esquema para crear un permiso"""
    pass

class PermisoResponse(PermisoBase):
    """Esquema de respuesta para un permiso"""
    id: int
    fecha_creacion: datetime

# === ESQUEMAS DE AUTENTICACIÓN ===

class LoginRequest(BaseSchema):
    """Esquema para solicitud de login"""
    username: str = Field(..., description="Nombre de usuario o email")
    password: str = Field(..., description="Contraseña")

class TokenResponse(BaseSchema):
    """Esquema de respuesta para token de autenticación"""
    access_token: str
    token_type: str = "bearer"
    expires_in: int
    user_info: UsuarioResponse

class ChangePasswordRequest(BaseSchema):
    """Esquema para cambio de contraseña"""
    current_password: str = Field(..., description="Contraseña actual")
    new_password: str = Field(..., min_length=8, description="Nueva contraseña")
    confirm_password: str = Field(..., description="Confirmación de nueva contraseña")
    
    @validator('confirm_password')
    def passwords_match(cls, v, values):
        if 'new_password' in values and v != values['new_password']:
            raise ValueError('Las contraseñas no coinciden')
        return v

# === ESQUEMAS DE RESPUESTA GENERAL ===

class MessageResponse(BaseSchema):
    """Esquema para respuestas de mensaje general"""
    message: str
    success: bool = True
    data: Optional[dict] = None

class PaginatedResponse(BaseSchema):
    """Esquema para respuestas paginadas"""
    items: List[dict]
    total: int
    page: int
    per_page: int
    pages: int

# === CONFIGURACIÓN PARA RELACIONES ANIDADAS ===

# Actualizar las referencias hacia adelante
AreaResponse.model_rebuild()
UsuarioResponse.model_rebuild()