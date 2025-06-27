# app/routers/auth.py
from typing import List, Dict, Any
from datetime import datetime  # ← AGREGADO: Import faltante
from fastapi import APIRouter, Depends, HTTPException, status, Request
from fastapi.security import HTTPAuthorizationCredentials
from sqlalchemy.orm import Session
from pydantic import BaseModel  # ← AGREGADO: Import para BaseModel
import logging

# Importaciones locales
from app.core.database import get_database
from app.services.auth_service import AuthService, get_auth_service
from app.core.deps import (
    get_current_user,
    require_superadmin,
    require_alcalde_or_above,
    require_user_management_access,
    require_same_area_or_admin,
    log_user_action,
    get_user_context,
    optional_auth
)
from app.schemas.auth_schemas import (
    LoginRequest,
    TokenResponse,
    UsuarioCreate,
    UsuarioUpdate,
    UsuarioResponse,
    ChangePasswordRequest,
    MessageResponse,
    PaginatedResponse
)

# Esquema para refresh token
class RefreshTokenRequest(BaseModel):
    refresh_token: str

# Configurar logging
logger = logging.getLogger(__name__)

# Crear router
router = APIRouter(
    prefix="/auth",
    tags=["Autenticación"],
    responses={
        401: {"description": "No autorizado"},
        403: {"description": "Acceso prohibido"},
        500: {"description": "Error interno del servidor"}
    }
)

# === ENDPOINTS DE AUTENTICACIÓN ===

@router.post("/login", 
             response_model=TokenResponse,
             summary="Iniciar sesión",
             description="Autentica usuario y genera tokens de acceso")
async def login(
    login_data: LoginRequest,
    request: Request,
    db: Session = Depends(get_database)
):
    """
    Endpoint para iniciar sesión en el SGD
    
    - **username**: Nombre de usuario o email
    - **password**: Contraseña
    
    Retorna tokens JWT y información del usuario
    """
    try:
        # Crear servicio de autenticación
        auth_service = get_auth_service(db)
        
        # Obtener IP del cliente
        client_ip = request.client.host
        
        # Autenticar usuario
        auth_result = auth_service.authenticate_user(
            username=login_data.username,
            password=login_data.password,
            ip_address=client_ip
        )
        
        logger.info(f"Login exitoso para usuario: {login_data.username} desde IP: {client_ip}")
        
        return TokenResponse(**auth_result)
        
    except Exception as e:
        logger.warning(f"Intento de login fallido para: {login_data.username} desde IP: {request.client.host}")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Credenciales inválidas"
        )

@router.post("/refresh",
             response_model=Dict[str, Any],
             summary="Renovar token",
             description="Renueva el token de acceso usando refresh token")
async def refresh_token(
    request: RefreshTokenRequest,  # ← CORREGIDO: Usar schema específico
    db: Session = Depends(get_database)
):
    """
    Endpoint para renovar token de acceso
    
    - **refresh_token**: Token de renovación válido
    
    Retorna nuevo token de acceso
    """
    try:
        # Crear servicio de autenticación
        auth_service = get_auth_service(db)
        
        refresh_token = request.refresh_token
        if not refresh_token:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="refresh_token es requerido"
            )
            
        result = auth_service.refresh_access_token(refresh_token)
        return result
        
    except Exception as e:
        logger.warning(f"Error al renovar token: {e}")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Refresh token inválido"
        )

@router.post("/logout",
             response_model=MessageResponse,
             summary="Cerrar sesión",
             description="Cierra la sesión del usuario actual")
async def logout(
    current_user: Dict[str, Any] = Depends(get_current_user)
):
    """
    Endpoint para cerrar sesión
    
    Nota: En la implementación actual, el logout es del lado del cliente
    (eliminando tokens). En versiones futuras se implementará blacklist de tokens.
    """
    logger.info(f"Logout para usuario: {current_user.get('username')}")
    
    return MessageResponse(
        message="Sesión cerrada exitosamente",
        success=True
    )

@router.get("/me",
            response_model=UsuarioResponse,
            summary="Información del usuario actual",
            description="Obtiene información completa del usuario autenticado")
async def get_current_user_info(
    current_user: Dict[str, Any] = Depends(get_current_user)
):
    """
    Endpoint para obtener información del usuario actual
    Incluye datos del puesto y área asignada
    """
    return UsuarioResponse(**current_user)

@router.get("/profile",
            response_model=Dict[str, Any],
            summary="Perfil completo del usuario",
            description="Obtiene perfil expandido con permisos y contexto")
async def get_user_profile(
    user_context: Dict[str, Any] = Depends(get_user_context),
    db: Session = Depends(get_database)
):
    """
    Endpoint para obtener perfil completo del usuario
    Incluye permisos, área, puesto y flags de autorización
    """
    # Crear servicio de autenticación
    auth_service = get_auth_service(db)
    
    user_id = user_context.get("id")
    permissions = auth_service.get_user_permissions(user_id)
    
    profile = user_context.copy()
    profile["permissions"] = permissions
    
    return profile

# === ENDPOINTS DE GESTIÓN DE CONTRASEÑAS ===

@router.post("/change-password",
             response_model=MessageResponse,
             summary="Cambiar contraseña",
             description="Permite al usuario cambiar su contraseña")
async def change_password(
    password_data: ChangePasswordRequest,
    current_user: Dict[str, Any] = Depends(log_user_action("Cambio de contraseña")),
    db: Session = Depends(get_database)
):
    """
    Endpoint para cambiar contraseña del usuario actual
    
    - **current_password**: Contraseña actual
    - **new_password**: Nueva contraseña
    - **confirm_password**: Confirmación de nueva contraseña
    """
    try:
        # Crear servicio de autenticación
        auth_service = get_auth_service(db)
        
        success = auth_service.change_password(
            user_id=current_user.get("id"),
            password_change=password_data
        )
        
        if success:
            return MessageResponse(
                message="Contraseña cambiada exitosamente",
                success=True
            )
        else:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Error al cambiar contraseña"
            )
            
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error al cambiar contraseña para usuario {current_user.get('id')}: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error interno al cambiar contraseña"
        )

@router.post("/reset-password/{user_id}",
             response_model=MessageResponse,
             summary="Resetear contraseña de usuario",
             description="Permite a administradores resetear contraseñas")
async def reset_user_password(
    user_id: int,
    new_password: str,
    current_user: Dict[str, Any] = Depends(require_user_management_access),
    db: Session = Depends(get_database)
):
    """
    Endpoint para resetear contraseña de otro usuario (solo admins)
    
    - **user_id**: ID del usuario objetivo
    - **new_password**: Nueva contraseña
    """
    try:
        # Crear servicio de autenticación
        auth_service = get_auth_service(db)
        
        # Crear request de cambio de contraseña administrativo
        target_user = auth_service.get_user_by_id(user_id)
        if not target_user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Usuario no encontrado"
            )
        
        # Actualizar contraseña directamente (bypass de contraseña actual)
        from app.core.security import create_password_hash, validate_password_strength
        
        # Validar nueva contraseña
        validation = validate_password_strength(new_password)
        if not validation["valid"]:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Contraseña insegura: {', '.join(validation['errors'])}"
            )
        
        # Actualizar contraseña
        target_user.password_hash = create_password_hash(new_password)
        db.commit()  # ← CORREGIDO: Usar db en lugar de auth_service.db
        
        logger.info(f"Contraseña reseteada para usuario {target_user.username} por {current_user.get('username')}")
        
        return MessageResponse(
            message=f"Contraseña reseteada exitosamente para usuario {target_user.username}",
            success=True
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error al resetear contraseña: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error interno al resetear contraseña"
        )

# === ENDPOINTS DE GESTIÓN DE USUARIOS ===

@router.post("/users",
             response_model=UsuarioResponse,
             summary="Crear usuario",
             description="Crea un nuevo usuario en el sistema")
async def create_user(
    user_data: UsuarioCreate,
    current_user: Dict[str, Any] = Depends(require_user_management_access),
    db: Session = Depends(get_database)
):
    """
    Endpoint para crear un nuevo usuario
    
    Solo usuarios con permisos administrativos pueden crear usuarios.
    SUPERADMIN puede crear cualquier tipo, ALCALDE solo FUNCIONARIOS.
    """
    try:
        # Crear servicio de autenticación
        auth_service = get_auth_service(db)
        
        new_user = auth_service.create_user(
            user_data=user_data,
            created_by_user_id=current_user.get("id")
        )
        
        return UsuarioResponse(**new_user)
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error al crear usuario: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error interno al crear usuario"
        )

@router.get("/users",
            response_model=List[UsuarioResponse],
            summary="Listar usuarios",
            description="Obtiene lista de usuarios con filtros")
async def list_users(
    skip: int = 0,
    limit: int = 100,
    area_id: int = None,
    tipo_usuario: str = None,
    estado: str = None,
    current_user: Dict[str, Any] = Depends(require_user_management_access),
    db: Session = Depends(get_database)
):
    """
    Endpoint para listar usuarios con filtros opcionales
    
    - **skip**: Número de registros a omitir
    - **limit**: Número máximo de registros a retornar
    - **area_id**: Filtrar por área específica
    - **tipo_usuario**: Filtrar por tipo de usuario
    - **estado**: Filtrar por estado
    """
    try:
        # Crear servicio de autenticación
        auth_service = get_auth_service(db)
        
        # Construir query base
        from app.models.auth_models import Usuario, Puesto
        query = db.query(Usuario)
        
        # Aplicar filtros
        if area_id:
            query = query.join(Puesto).filter(Puesto.area_id == area_id)
        
        if tipo_usuario:
            query = query.filter(Usuario.tipo_usuario == tipo_usuario)
        
        if estado:
            query = query.filter(Usuario.estado == estado)
        
        # Si no es SUPERADMIN, limitar a usuarios de nivel inferior o igual
        if current_user.get("tipo_usuario") != "SUPERADMIN":
            # ALCALDE solo ve FUNCIONARIOS y su propio usuario
            if current_user.get("tipo_usuario") == "ALCALDE":
                query = query.filter(
                    (Usuario.tipo_usuario == "FUNCIONARIO") | 
                    (Usuario.id == current_user.get("id"))
                )
        
        # Ejecutar query con paginación
        users = query.offset(skip).limit(limit).all()
        
        # Convertir a respuesta
        users_data = []
        for user in users:
            user_data = auth_service._load_user_with_relations(user.id)
            users_data.append(UsuarioResponse(**user_data))
        
        return users_data
        
    except Exception as e:
        logger.error(f"Error al listar usuarios: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error interno al listar usuarios"
        )

@router.get("/users/{user_id}",
            response_model=UsuarioResponse,
            summary="Obtener usuario por ID",
            description="Obtiene información detallada de un usuario específico")
async def get_user_by_id(
    user_id: int,
    current_user: Dict[str, Any] = Depends(get_current_user),
    db: Session = Depends(get_database)
):
    """
    Endpoint para obtener un usuario específico por ID
    
    Requiere permisos administrativos o pertenecer a la misma área
    """
    try:
        # Crear servicio de autenticación
        auth_service = get_auth_service(db)
        
        # Verificar permisos manualmente (ya que no podemos usar la dependencia factory)
        # Admins tienen acceso total
        if current_user.get("tipo_usuario") not in ["SUPERADMIN", "ALCALDE"]:
            # Acceso a sí mismo
            if current_user.get("id") != user_id:
                # Verificar misma área
                target_user = auth_service._load_user_with_relations(user_id)
                if target_user:
                    current_area = current_user.get("puesto", {}).get("area", {}).get("id")
                    target_area = target_user.get("puesto", {}).get("area", {}).get("id")
                    
                    if current_area != target_area:
                        raise HTTPException(
                            status_code=status.HTTP_403_FORBIDDEN,
                            detail="Sin acceso a usuarios de otras áreas"
                        )
        
        user_data = auth_service._load_user_with_relations(user_id)
        
        if not user_data:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Usuario no encontrado"
            )
        
        return UsuarioResponse(**user_data)
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error al obtener usuario {user_id}: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error interno al obtener usuario"
        )

@router.put("/users/{user_id}",
            response_model=UsuarioResponse,
            summary="Actualizar usuario",
            description="Actualiza información de un usuario")
async def update_user(
    user_id: int,
    user_update: UsuarioUpdate,
    current_user: Dict[str, Any] = Depends(log_user_action("Actualizar usuario")),
    db: Session = Depends(get_database)
):
    """
    Endpoint para actualizar un usuario
    
    Los usuarios pueden actualizar sus propios datos básicos.
    Los administradores pueden actualizar cualquier usuario bajo su jurisdicción.
    """
    try:
        # Crear servicio de autenticación
        auth_service = get_auth_service(db)
        
        updated_user = auth_service.update_user(
            user_id=user_id,
            user_update=user_update,
            updated_by_user_id=current_user.get("id")
        )
        
        return UsuarioResponse(**updated_user)
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error al actualizar usuario {user_id}: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error interno al actualizar usuario"
        )

@router.delete("/users/{user_id}",
               response_model=MessageResponse,
               summary="Desactivar usuario",
               description="Desactiva un usuario (soft delete)")
async def deactivate_user(
    user_id: int,
    current_user: Dict[str, Any] = Depends(require_user_management_access),
    db: Session = Depends(get_database)
):
    """
    Endpoint para desactivar un usuario (no eliminar)
    
    Solo marca el usuario como INACTIVO, preservando datos para auditoría
    """
    try:
        # Crear servicio de autenticación
        auth_service = get_auth_service(db)
        
        user = auth_service.get_user_by_id(user_id)
        if not user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Usuario no encontrado"
            )
        
        # No permitir desactivar SUPERADMIN
        if user.tipo_usuario == "SUPERADMIN":
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="No se puede desactivar usuario SUPERADMIN"
            )
        
        # No permitir auto-desactivación
        if user.id == current_user.get("id"):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="No puede desactivar su propio usuario"
            )
        
        # Desactivar usuario
        user.estado = "INACTIVO"
        user.fecha_actualizacion = datetime.utcnow()
        db.commit()
        
        logger.info(f"Usuario {user.username} desactivado por {current_user.get('username')}")
        
        return MessageResponse(
            message=f"Usuario {user.username} desactivado exitosamente",
            success=True
        )
        
    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        logger.error(f"Error al desactivar usuario {user_id}: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error interno al desactivar usuario"
        )

# === ENDPOINTS DE INFORMACIÓN PÚBLICA ===

@router.get("/system-info",
            response_model=Dict[str, Any],
            summary="Información del sistema",
            description="Obtiene información básica del sistema SGD")
async def get_system_info(
    current_user: Dict[str, Any] = Depends(optional_auth)
):
    """
    Endpoint para obtener información básica del sistema
    Disponible sin autenticación para verificar estado del servicio
    """
    from app.core.config import settings
    
    info = {
        "name": "Sistema de Gobernanza Digital (SGD)",
        "municipality": "Municipalidad Distrital de Colca",
        "province": "Huancayo",
        "version": "1.0.0-MVP",
        "environment": settings.ENVIRONMENT,
        "authenticated": bool(current_user),
        "features": [
            "Gestión Documental",
            "Mesa de Partes Digital", 
            "Organigrama Digital",
            "Control de Acceso Basado en Roles",
            "Auditoría y Trazabilidad"
        ]
    }
    
    if current_user:
        info["user"] = {
            "username": current_user.get("username"),
            "tipo_usuario": current_user.get("tipo_usuario"),
            "area": current_user.get("puesto", {}).get("area", {}).get("nombre")
        }
    
    return info

# === ENDPOINTS DE VALIDACIÓN ===

@router.post("/validate-token",
             response_model=Dict[str, Any],
             summary="Validar token",
             description="Valida si un token JWT es válido")
async def validate_token(
    current_user: Dict[str, Any] = Depends(get_current_user)
):
    """
    Endpoint para validar un token JWT
    Útil para verificar validez sin obtener datos completos
    """
    return {
        "valid": True,
        "user_id": current_user.get("id"),
        "username": current_user.get("username"),
        "tipo_usuario": current_user.get("tipo_usuario"),
        "expires_in": "Verificar header del token"
    }

# === MANEJO DE ERRORES ===
# Nota: Los exception handlers deben registrarse en la aplicación principal (main.py)
# no en el router individual

# El siguiente código debe ir en app/main.py:
"""
from fastapi import Request
from fastapi.responses import JSONResponse
from app.core.config import settings

@app.exception_handler(Exception)
async def auth_exception_handler(request: Request, exc: Exception):
    logger.error(f"Error en endpoint de autenticación: {exc}")
    
    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content={
            "message": "Error interno en el sistema de autenticación",
            "success": False,
            "detail": str(exc) if settings.DEBUG else "Error interno del servidor"
        }
    )
"""