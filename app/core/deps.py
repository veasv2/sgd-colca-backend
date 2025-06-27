# app/core/deps.py
"""
Sistema de Dependencias para el Sistema de Gobernanza Digital (SGD)
Municipalidad Distrital de Colca

Implementa todas las dependencias de FastAPI para autenticación,
autorización y control de acceso basado en organigrama.
"""

from typing import Optional, List, Dict, Any, Callable
from fastapi import Depends, HTTPException, status, Request
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.orm import Session
import logging

# Importaciones locales
from app.core.database import get_database
from app.services.auth_service import AuthService, get_auth_service
from app.core.security import verify_token
from app.schemas.auth_schemas import TipoUsuarioEnum, EstadoUsuarioEnum
from app.models.auth_models import Usuario, Puesto, Area

# Configurar logging
logger = logging.getLogger(__name__)

# === CONFIGURACIÓN DE SEGURIDAD ===

# Esquema de seguridad HTTP Bearer para JWT
security = HTTPBearer(
    scheme_name="JWT",
    description="Token JWT de acceso al Sistema de Gobernanza Digital"
)

# === DEPENDENCIAS BÁSICAS ===

def get_db() -> Session:
    """
    Dependencia para obtener sesión de base de datos
    Alias para mayor claridad en los endpoints
    """
    return Depends(get_database)

def get_auth_service_dep(db: Session = Depends(get_database)) -> AuthService:
    """
    Dependencia para obtener el servicio de autenticación
    """
    return get_auth_service(db)

# === DEPENDENCIAS DE AUTENTICACIÓN ===

async def get_current_user_token(
    credentials: HTTPAuthorizationCredentials = Depends(security)
) -> Dict[str, Any]:
    """
    Extrae y valida el token JWT del header Authorization
    
    Returns:
        Dict con los datos del token decodificado
        
    Raises:
        HTTPException: Si el token es inválido o ha expirado
    """
    try:
        token = credentials.credentials
        payload = verify_token(token)
        
        if payload is None:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Token inválido o expirado",
                headers={"WWW-Authenticate": "Bearer"},
            )
        
        return payload
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error al procesar token: {e}")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Error al procesar token de autenticación",
            headers={"WWW-Authenticate": "Bearer"},
        )

async def get_current_user(
    token_data: Dict[str, Any] = Depends(get_current_user_token),
    auth_service: AuthService = Depends(get_auth_service_dep)
) -> Dict[str, Any]:
    """
    Obtiene el usuario actual basado en el token JWT
    
    Returns:
        Dict con información completa del usuario actual
        
    Raises:
        HTTPException: Si el usuario no existe o está inactivo
    """
    try:
        user_id = token_data.get("user_id")
        if not user_id:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Token inválido: falta información del usuario"
            )
        
        user_data = auth_service._load_user_with_relations(user_id)
        
        if not user_data:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Usuario no encontrado"
            )
        
        if user_data.get("estado") != EstadoUsuarioEnum.ACTIVO:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Usuario inactivo o suspendido"
            )
        
        return user_data
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error al obtener usuario actual: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error interno al verificar usuario"
        )

# === DEPENDENCIAS DE AUTORIZACIÓN POR TIPO DE USUARIO ===

def require_superadmin(
    current_user: Dict[str, Any] = Depends(get_current_user)
) -> Dict[str, Any]:
    """
    Requiere que el usuario actual sea SUPERADMIN
    
    Returns:
        Dict con información del usuario SUPERADMIN
        
    Raises:
        HTTPException: Si el usuario no es SUPERADMIN
    """
    if current_user.get("tipo_usuario") != TipoUsuarioEnum.SUPERADMIN:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Se requieren permisos de SUPERADMIN para esta operación"
        )
    
    logger.info(f"Acceso SUPERADMIN autorizado para usuario: {current_user.get('username')}")
    return current_user

def require_alcalde_or_above(
    current_user: Dict[str, Any] = Depends(get_current_user)
) -> Dict[str, Any]:
    """
    Requiere que el usuario sea ALCALDE o SUPERADMIN
    
    Returns:
        Dict con información del usuario autorizado
        
    Raises:
        HTTPException: Si el usuario no tiene permisos suficientes
    """
    allowed_types = [TipoUsuarioEnum.SUPERADMIN, TipoUsuarioEnum.ALCALDE]
    
    if current_user.get("tipo_usuario") not in allowed_types:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Se requieren permisos de ALCALDE o superiores para esta operación"
        )
    
    logger.info(f"Acceso ALCALDE+ autorizado para usuario: {current_user.get('username')}")
    return current_user

def require_admin_roles(
    current_user: Dict[str, Any] = Depends(get_current_user)
) -> Dict[str, Any]:
    """
    Requiere roles administrativos (SUPERADMIN o ALCALDE)
    Alias para require_alcalde_or_above para mayor claridad semántica
    """
    return require_alcalde_or_above(current_user)

# === DEPENDENCIAS DE AUTORIZACIÓN POR ÁREA ===

def require_area_access(area_codigo: str):
    """
    Factory para crear dependencia que requiere acceso a un área específica
    
    Args:
        area_codigo: Código del área requerida
        
    Returns:
        Función de dependencia
    """
    def check_area_access(
        current_user: Dict[str, Any] = Depends(get_current_user)
    ) -> Dict[str, Any]:
        """
        Verifica que el usuario tenga acceso al área especificada
        """
        # SUPERADMIN y ALCALDE tienen acceso a todas las áreas
        if current_user.get("tipo_usuario") in [TipoUsuarioEnum.SUPERADMIN, TipoUsuarioEnum.ALCALDE]:
            return current_user
        
        # Verificar área del usuario
        user_area_codigo = current_user.get("puesto", {}).get("area", {}).get("codigo")
        
        if user_area_codigo != area_codigo:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"Sin acceso al área {area_codigo}"
            )
        
        logger.info(f"Acceso autorizado al área {area_codigo} para usuario: {current_user.get('username')}")
        return current_user
    
    return check_area_access

def require_same_area_or_admin(target_user_id: int):
    """
    Factory para verificar acceso a usuarios de la misma área o permisos admin
    
    Args:
        target_user_id: ID del usuario objetivo
        
    Returns:
        Función de dependencia
    """
    def check_same_area_or_admin(
        current_user: Dict[str, Any] = Depends(get_current_user),
        auth_service: AuthService = Depends(get_auth_service_dep)
    ) -> Dict[str, Any]:
        """
        Verifica acceso al usuario objetivo
        """
        # Admins tienen acceso total
        if current_user.get("tipo_usuario") in [TipoUsuarioEnum.SUPERADMIN, TipoUsuarioEnum.ALCALDE]:
            return current_user
        
        # Acceso a sí mismo
        if current_user.get("id") == target_user_id:
            return current_user
        
        # Verificar misma área
        target_user = auth_service._load_user_with_relations(target_user_id)
        if not target_user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Usuario objetivo no encontrado"
            )
        
        current_area = current_user.get("puesto", {}).get("area", {}).get("id")
        target_area = target_user.get("puesto", {}).get("area", {}).get("id")
        
        if current_area != target_area:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Sin acceso a usuarios de otras áreas"
            )
        
        return current_user
    
    return check_same_area_or_admin

# === DEPENDENCIAS DE AUTORIZACIÓN POR MÓDULO ===

def require_module_permission(module_name: str, permission_type: str = "READ"):
    """
    Factory para crear dependencia que requiere permiso específico en un módulo
    
    Args:
        module_name: Nombre del módulo del SGD
        permission_type: Tipo de permiso (READ, WRITE, ADMIN)
        
    Returns:
        Función de dependencia
    """
    def check_module_permission(
        current_user: Dict[str, Any] = Depends(get_current_user),
        auth_service: AuthService = Depends(get_auth_service_dep)
    ) -> Dict[str, Any]:
        """
        Verifica permisos específicos del módulo
        """
        # SUPERADMIN tiene acceso total
        if current_user.get("tipo_usuario") == TipoUsuarioEnum.SUPERADMIN:
            return current_user
        
        # Obtener permisos del usuario
        user_permissions = auth_service.get_user_permissions(current_user.get("id"))
        
        # Verificar permiso específico
        required_permission = f"{module_name}_{permission_type}".lower()
        
        if required_permission not in user_permissions and f"{module_name}_admin" not in user_permissions:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"Sin permisos para {permission_type} en módulo {module_name}"
            )
        
        logger.info(f"Permiso {required_permission} autorizado para usuario: {current_user.get('username')}")
        return current_user
    
    return check_module_permission

# === DEPENDENCIAS ESPECÍFICAS DEL SGD ===

def require_organigrama_admin(
    current_user: Dict[str, Any] = Depends(get_current_user)
) -> Dict[str, Any]:
    """
    Requiere permisos para administrar el organigrama
    Solo SUPERADMIN y ALCALDE pueden modificar la estructura organizacional
    """
    if current_user.get("tipo_usuario") not in [TipoUsuarioEnum.SUPERADMIN, TipoUsuarioEnum.ALCALDE]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Solo SUPERADMIN y ALCALDE pueden administrar el organigrama"
        )
    
    logger.info(f"Acceso a administración de organigrama autorizado para: {current_user.get('username')}")
    return current_user

def require_document_creation(
    current_user: Dict[str, Any] = Depends(get_current_user)
) -> Dict[str, Any]:
    """
    Requiere permisos para crear documentos
    Todos los usuarios activos pueden crear documentos básicos
    """
    # Verificar que el usuario tenga un puesto asignado
    if not current_user.get("puesto_id"):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Debe tener un puesto asignado para crear documentos"
        )
    
    return current_user

def require_document_approval(document_type: str):
    """
    Factory para requerir permisos de aprobación según tipo de documento
    
    Args:
        document_type: Tipo de documento a aprobar
        
    Returns:
        Función de dependencia
    """
    def check_approval_permission(
        current_user: Dict[str, Any] = Depends(get_current_user)
    ) -> Dict[str, Any]:
        """
        Verifica permisos de aprobación según jerarquía
        """
        user_type = current_user.get("tipo_usuario")
        
        # Definir qué tipos de usuario pueden aprobar qué documentos
        approval_matrix = {
            "memorandum": [TipoUsuarioEnum.FUNCIONARIO, TipoUsuarioEnum.ALCALDE, TipoUsuarioEnum.SUPERADMIN],
            "resolucion": [TipoUsuarioEnum.ALCALDE, TipoUsuarioEnum.SUPERADMIN],
            "ordenanza": [TipoUsuarioEnum.ALCALDE, TipoUsuarioEnum.SUPERADMIN],
            "acuerdo": [TipoUsuarioEnum.ALCALDE, TipoUsuarioEnum.SUPERADMIN]
        }
        
        allowed_types = approval_matrix.get(document_type.lower(), [TipoUsuarioEnum.SUPERADMIN])
        
        if user_type not in allowed_types:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"Sin permisos para aprobar documentos de tipo {document_type}"
            )
        
        return current_user
    
    return check_approval_permission

# === DEPENDENCIAS DE AUDITORÍA ===

def require_audit_access(
    current_user: Dict[str, Any] = Depends(get_current_user)
) -> Dict[str, Any]:
    """
    Requiere acceso a funciones de auditoría
    Solo roles administrativos pueden acceder a logs y auditorías
    """
    if current_user.get("tipo_usuario") not in [TipoUsuarioEnum.SUPERADMIN, TipoUsuarioEnum.ALCALDE]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Se requieren permisos administrativos para acceso a auditoría"
        )
    
    logger.info(f"Acceso a auditoría autorizado para: {current_user.get('username')}")
    return current_user

# === UTILIDADES PARA DEPENDENCIAS ===

def get_user_context(
    current_user: Dict[str, Any] = Depends(get_current_user),
    request: Request = None
) -> Dict[str, Any]:
    """
    Obtiene contexto completo del usuario para operaciones complejas
    
    Returns:
        Dict con contexto expandido del usuario
    """
    context = current_user.copy()
    
    # Agregar información adicional del contexto
    if request:
        context.update({
            "ip_address": request.client.host,
            "user_agent": request.headers.get("user-agent", ""),
            "endpoint": request.url.path,
            "method": request.method
        })
    
    # Agregar flags de permisos comunes
    context.update({
        "is_admin": current_user.get("tipo_usuario") in [TipoUsuarioEnum.SUPERADMIN, TipoUsuarioEnum.ALCALDE],
        "is_superadmin": current_user.get("tipo_usuario") == TipoUsuarioEnum.SUPERADMIN,
        "is_alcalde": current_user.get("tipo_usuario") == TipoUsuarioEnum.ALCALDE,
        "has_puesto": bool(current_user.get("puesto_id")),
        "area_codigo": current_user.get("puesto", {}).get("area", {}).get("codigo")
    })
    
    return context

def optional_auth(
    credentials: Optional[HTTPAuthorizationCredentials] = Depends(HTTPBearer(auto_error=False)),
    auth_service: AuthService = Depends(get_auth_service_dep)
) -> Optional[Dict[str, Any]]:
    """
    Dependencia de autenticación opcional
    Útil para endpoints que pueden funcionar con o sin autenticación
    
    Returns:
        Dict con datos del usuario o None si no está autenticado
    """
    if not credentials:
        return None
    
    try:
        payload = verify_token(credentials.credentials)
        if not payload:
            return None
        
        user_id = payload.get("user_id")
        user_data = auth_service._load_user_with_relations(user_id)
        
        if user_data and user_data.get("estado") == EstadoUsuarioEnum.ACTIVO:
            return user_data
        
        return None
        
    except Exception as e:
        logger.warning(f"Error en autenticación opcional: {e}")
        return None

# === DEPENDENCIAS PERSONALIZADAS PARA ENDPOINTS ESPECÍFICOS ===

def require_user_management_access(
    current_user: Dict[str, Any] = Depends(get_current_user)
) -> Dict[str, Any]:
    """
    Requiere acceso para gestión de usuarios
    Combina verificaciones específicas del SGD
    """
    # Solo admins pueden gestionar usuarios
    if current_user.get("tipo_usuario") not in [TipoUsuarioEnum.SUPERADMIN, TipoUsuarioEnum.ALCALDE]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Se requieren permisos administrativos para gestión de usuarios"
        )
    
    # Verificar que el usuario tenga puesto asignado (excepción para SUPERADMIN)
    if (current_user.get("tipo_usuario") != TipoUsuarioEnum.SUPERADMIN and 
        not current_user.get("puesto_id")):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Debe tener un puesto asignado para gestionar usuarios"
        )
    
    logger.info(f"Acceso a gestión de usuarios autorizado para: {current_user.get('username')}")
    return current_user

# === MIDDLEWARE DE LOGGING PARA DEPENDENCIAS ===

def log_user_action(action: str):
    """
    Factory para crear dependencia que registra acciones del usuario
    
    Args:
        action: Descripción de la acción realizada
        
    Returns:
        Función de dependencia que registra la acción
    """
    def log_action(
        current_user: Dict[str, Any] = Depends(get_current_user)
    ) -> Dict[str, Any]:
        """
        Registra la acción del usuario para auditoría
        """
        logger.info(
            f"Acción: {action} | Usuario: {current_user.get('username')} | "
            f"Tipo: {current_user.get('tipo_usuario')} | "
            f"Área: {current_user.get('puesto', {}).get('area', {}).get('codigo', 'N/A')}"
        )
        return current_user
    
    return log_action