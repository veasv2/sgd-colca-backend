# app/services/auth_service.py

from typing import Optional, Dict, Any
from datetime import datetime, timedelta
from sqlalchemy.orm import Session
from fastapi import HTTPException, status

from app.models.seguridad.usuario_model import Usuario
from app.schemas.seguridad.auth_schemas import LoginRequest, LoginResponse, UserTokenInfo
from app.repositories.seguridad.usuario_repository import usuario_repository  # Esto debe ser la instancia
from app.core.security import verify_password
from app.core.jwt import create_access_token, create_refresh_token, verify_token
from app.core.config import settings

class AuthService:
    def __init__(self):
        self.usuario_repo = usuario_repository  # ✅ Instancia del repositorio

    def authenticate_user(self, db: Session, username_or_email: str, password: str) -> Optional[Usuario]:
        """
        Autenticar usuario con username/email y contraseña
        """
        # Obtener usuario por credenciales
        usuario = self.usuario_repo.get_by_credentials(db, username_or_email)
        
        if not usuario:
            return None
        
        # Verificar contraseña
        if not verify_password(password, usuario.password_hash):
            return None
        
        return usuario

    def login(self, db: Session, login_data: LoginRequest) -> LoginResponse:
        """
        Realizar login y generar tokens
        """
        # Autenticar usuario
        usuario = self.authenticate_user(
            db, 
            login_data.username_or_email, 
            login_data.password
        )
        
        if not usuario:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Credenciales incorrectas",
                headers={"WWW-Authenticate": "Bearer"},
            )
        
        # Verificar estado del usuario
        if usuario.estado != "ACTIVO":
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail=f"Usuario {usuario.estado.lower()}. Contacte al administrador.",
            )
        
        # Verificar si está bloqueado
        if usuario.bloqueado_hasta and usuario.bloqueado_hasta > datetime.utcnow():
            tiempo_restante = usuario.bloqueado_hasta - datetime.utcnow()
            minutos_restantes = int(tiempo_restante.total_seconds() / 60)
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail=f"Usuario bloqueado. Intente nuevamente en {minutos_restantes} minutos.",
            )
        
        # Actualizar último acceso (resetea intentos fallidos)
        usuario = self.usuario_repo.actualizar_ultimo_acceso(db, usuario)
        
        # Crear tokens
        token_data = {
            "user_id": usuario.id,
            "username": usuario.username,
            "tipo_usuario": usuario.tipo_usuario
        }
        
        access_token = create_access_token(token_data)
        refresh_token = create_refresh_token({"user_id": usuario.id})
        
        # Crear respuesta
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
        
        return LoginResponse(
            access_token=access_token,
            refresh_token=refresh_token,
            token_type="bearer",
            expires_in=settings.ACCESS_TOKEN_EXPIRE_MINUTES * 60,  # En segundos
            user=user_info
        )

    def get_current_user(self, db: Session, token: str) -> Usuario:
        """
        Obtener usuario actual desde token JWT
        """
        # Verificar y decodificar token
        payload = verify_token(token, "access")
        
        # Obtener user_id del payload
        user_id = payload.get("user_id")
        if not user_id:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Token inválido: falta user_id",
                headers={"WWW-Authenticate": "Bearer"},
            )
        
        # Obtener usuario de la base de datos
        usuario = self.usuario_repo.get(db, user_id)
        if not usuario:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Usuario no encontrado",
                headers={"WWW-Authenticate": "Bearer"},
            )
        
        # Verificar que el usuario siga activo
        if usuario.estado != "ACTIVO":
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Usuario inactivo",
                headers={"WWW-Authenticate": "Bearer"},
            )
        
        return usuario

    def refresh_access_token(self, db: Session, refresh_token: str) -> Dict[str, Any]:
        """
        Renovar access token usando refresh token
        """
        # Verificar refresh token
        payload = verify_token(refresh_token, "refresh")
        
        user_id = payload.get("user_id")
        if not user_id:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Refresh token inválido",
                headers={"WWW-Authenticate": "Bearer"},
            )
        
        # Obtener usuario
        usuario = self.usuario_repo.get(db, user_id)
        if not usuario or usuario.estado != "ACTIVO":
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Usuario no válido para renovar token",
                headers={"WWW-Authenticate": "Bearer"},
            )
        
        # Crear nuevo access token
        token_data = {
            "user_id": usuario.id,
            "username": usuario.username,
            "tipo_usuario": usuario.tipo_usuario
        }
        
        new_access_token = create_access_token(token_data)
        
        return {
            "access_token": new_access_token,
            "token_type": "bearer",
            "expires_in": settings.ACCESS_TOKEN_EXPIRE_MINUTES * 60
        }

    def handle_failed_login(self, db: Session, username_or_email: str):
        """
        Manejar intento de login fallido
        """
        usuario = self.usuario_repo.get_by_credentials(db, username_or_email)
        
        if usuario:
            # Incrementar intentos fallidos
            usuario = self.usuario_repo.incrementar_intentos_fallidos(db, usuario)
            
            # Bloquear si excede el máximo
            if usuario.intentos_fallidos >= settings.MAX_LOGIN_ATTEMPTS:
                lockout_until = datetime.utcnow() + timedelta(
                    minutes=settings.LOCKOUT_DURATION_MINUTES
                )
                self.usuario_repo.bloquear_usuario(db, usuario, lockout_until)
                
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail=f"Demasiados intentos fallidos. Usuario bloqueado por {settings.LOCKOUT_DURATION_MINUTES} minutos.",
                )
        
        # Siempre mostrar el mismo mensaje para no revelar si el usuario existe
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Credenciales incorrectas",
            headers={"WWW-Authenticate": "Bearer"},
        )

    def validate_token(self, token: str) -> Dict[str, Any]:
        """
        Validar token y retornar información básica
        """
        try:
            payload = verify_token(token, "access")
            return {
                "valid": True,
                "user_id": payload.get("user_id"),
                "username": payload.get("username"),
                "tipo_usuario": payload.get("tipo_usuario"),
                "expires_at": datetime.fromtimestamp(payload.get("exp"))
            }
        except HTTPException:
            return {"valid": False}

# Instancia del servicio
auth_service = AuthService()