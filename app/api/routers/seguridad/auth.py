# app/api/routers/auth.py

from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import HTTPBearer
from sqlalchemy.orm import Session

from app.schemas.seguridad.auth_schemas import (
    LoginRequest, 
    LoginResponse,
    RefreshTokenRequest,
    RefreshTokenResponse,
    SessionInfo,
    UserTokenInfo
)
from app.services.seguridad.auth_service import auth_service
from app.core.database import get_database

router = APIRouter(
    prefix="/auth",
    tags=["autenticación"]
)

security = HTTPBearer()

@router.post("/login", response_model=LoginResponse)
def login(
    login_data: LoginRequest,
    db: Session = Depends(get_database)
):
    """
    Iniciar sesión con username/email y contraseña
    
    Returns:
        - access_token: Token JWT para autenticación
        - refresh_token: Token para renovar el access_token  
        - user: Información del usuario
        - expires_in: Tiempo de expiración en segundos
    """
    try:
        return auth_service.login(db, login_data)
    except HTTPException:
        # Manejar intento fallido si es necesario
        auth_service.handle_failed_login(db, login_data.username_or_email)

@router.post("/refresh", response_model=RefreshTokenResponse)
def refresh_token(
    refresh_data: RefreshTokenRequest,
    db: Session = Depends(get_database)
):
    """
    Renovar access token usando refresh token
    
    Returns:
        - access_token: Nuevo token JWT
        - expires_in: Tiempo de expiración en segundos
    """
    result = auth_service.refresh_access_token(db, refresh_data.refresh_token)
    return RefreshTokenResponse(**result)

@router.get("/me", response_model=UserTokenInfo)
def get_current_user_info(
    db: Session = Depends(get_database),
    token: str = Depends(security)
):
    """
    Obtener información del usuario autenticado actual
    
    Requires: Token JWT válido
    """
    usuario = auth_service.get_current_user(db, token.credentials)
    
    return UserTokenInfo(
        id=usuario.id,
        uuid=usuario.uuid,
        username=usuario.username,
        email=usuario.email,
        nombres=usuario.nombres,
        apellidos=usuario.apellidos,
        tipo_usuario=usuario.tipo_usuario,
        estado=usuario.estado,
        puesto_id=usuario.puesto_id
    )

@router.get("/session", response_model=SessionInfo)
def get_session_info(
    db: Session = Depends(get_database),
    token: str = Depends(security)
):
    """
    Obtener información completa de la sesión actual
    
    Includes:
        - User information
        - Token expiration
        - User permissions
    """
    from datetime import datetime
    from app.core.permissions.utils import get_user_permissions
    
    usuario = auth_service.get_current_user(db, token.credentials)
    
    # Obtener información del token
    token_info = auth_service.validate_token(token.credentials)
    
    # Obtener permisos del usuario
    user_permissions = get_user_permissions(db, usuario)
    
    user_info = UserTokenInfo(
        id=usuario.id,
        uuid=usuario.uuid,
        username=usuario.username,
        email=usuario.email,
        nombres=usuario.nombres,
        apellidos=usuario.apellidos,
        tipo_usuario=usuario.tipo_usuario,
        estado=usuario.estado,
        puesto_id=usuario.puesto_id
    )
    
    return SessionInfo(
        user=user_info,
        token_expires_at=token_info["expires_at"],
        session_created_at=datetime.utcnow(),  # Simplificado por ahora
        permissions=user_permissions,
        last_activity=usuario.ultimo_acceso or datetime.utcnow()
    )

@router.post("/validate")
def validate_token(
    token: str = Depends(security)
):
    """
    Validar si un token es válido
    
    Returns:
        - valid: Boolean indicating if token is valid
        - Additional token information if valid
    """
    return auth_service.validate_token(token.credentials)

@router.post("/logout")
def logout(
    token: str = Depends(security),
    db: Session = Depends(get_database)
):
    """
    Cerrar sesión (logout)
    
    Note: En esta implementación básica solo validamos que el token sea válido.
    Para una implementación completa, podrías:
    - Invalidar el token en una blacklist
    - Cerrar sesiones en la base de datos
    - Limpiar cookies del cliente
    """
    # Verificar que el token sea válido
    auth_service.get_current_user(db, token.credentials)
    
    return {
        "message": "Logout exitoso",
        "status": "success"
    }