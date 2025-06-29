# app/schemas/auth_schemas.py

from pydantic import BaseModel, Field, EmailStr
from typing import Optional
from datetime import datetime

# =============================================================================
# SCHEMAS PARA LOGIN
# =============================================================================

class LoginRequest(BaseModel):
    """Schema para petición de login"""
    username_or_email: str = Field(
        ..., 
        min_length=3, 
        max_length=100,
        description="Username o email del usuario"
    )
    password: str = Field(
        ..., 
        min_length=1,
        description="Contraseña del usuario"
    )

class LoginResponse(BaseModel):
    """Schema para respuesta de login exitoso"""
    access_token: str = Field(..., description="Token JWT de acceso")
    refresh_token: str = Field(..., description="Token JWT de renovación")
    token_type: str = Field(default="bearer", description="Tipo de token")
    expires_in: int = Field(..., description="Tiempo de expiración en segundos")
    user: "UserTokenInfo" = Field(..., description="Información del usuario")

class UserTokenInfo(BaseModel):
    """Información del usuario incluida en el token"""
    id: int
    uuid: str
    username: str
    email: str
    nombres: str
    apellidos: str
    tipo_usuario: str
    estado: str
    puesto_id: Optional[int] = None

    class Config:
        from_attributes = True

# =============================================================================
# SCHEMAS PARA REFRESH TOKEN
# =============================================================================

class RefreshTokenRequest(BaseModel):
    """Schema para renovar token"""
    refresh_token: str = Field(..., description="Refresh token válido")

class RefreshTokenResponse(BaseModel):
    """Schema para respuesta de token renovado"""
    access_token: str = Field(..., description="Nuevo token JWT de acceso")
    token_type: str = Field(default="bearer", description="Tipo de token")
    expires_in: int = Field(..., description="Tiempo de expiración en segundos")

# =============================================================================
# SCHEMAS PARA VALIDACIÓN DE TOKEN
# =============================================================================

class TokenPayload(BaseModel):
    """Schema para payload del token JWT"""
    user_id: int = Field(..., description="ID del usuario")
    username: str = Field(..., description="Username del usuario")
    tipo_usuario: str = Field(..., description="Tipo de usuario")
    exp: datetime = Field(..., description="Fecha de expiración")
    iat: datetime = Field(..., description="Fecha de emisión")
    type: str = Field(..., description="Tipo de token")

# =============================================================================
# SCHEMAS PARA RESPUESTAS DE ERROR
# =============================================================================

class LoginError(BaseModel):
    """Schema para errores de login"""
    detail: str = Field(..., description="Descripción del error")
    error_code: str = Field(..., description="Código de error específico")
    remaining_attempts: Optional[int] = Field(None, description="Intentos restantes")
    lockout_until: Optional[datetime] = Field(None, description="Bloqueado hasta")

# =============================================================================
# SCHEMAS PARA CAMBIO DE CONTRASEÑA
# =============================================================================

class ChangePasswordRequest(BaseModel):
    """Schema para cambio de contraseña"""
    current_password: str = Field(..., description="Contraseña actual")
    new_password: str = Field(..., min_length=8, description="Nueva contraseña")

class PasswordResetRequest(BaseModel):
    """Schema para solicitud de reset de contraseña"""
    email: EmailStr = Field(..., description="Email del usuario")

class PasswordResetConfirm(BaseModel):
    """Schema para confirmar reset de contraseña"""
    token: str = Field(..., description="Token de reset")
    new_password: str = Field(..., min_length=8, description="Nueva contraseña")

# =============================================================================
# SCHEMAS PARA LOGOUT
# =============================================================================

class LogoutRequest(BaseModel):
    """Schema para logout"""
    refresh_token: Optional[str] = Field(None, description="Refresh token a invalidar")

class LogoutResponse(BaseModel):
    """Schema para respuesta de logout"""
    message: str = Field(default="Logout exitoso")
    
# =============================================================================
# SCHEMAS PARA INFORMACIÓN DE SESIÓN
# =============================================================================

class SessionInfo(BaseModel):
    """Información de la sesión actual"""
    user: UserTokenInfo
    token_expires_at: datetime
    session_created_at: datetime
    permissions: list[str] = Field(default_factory=list)
    last_activity: datetime

# Actualizar referencias forward
LoginResponse.model_rebuild()