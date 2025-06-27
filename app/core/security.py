from datetime import datetime, timedelta
from typing import Optional, Dict, Any
import jwt
from passlib.context import CryptContext
from passlib.hash import bcrypt
from app.core.config import settings
import logging

# Configurar logging
logger = logging.getLogger(__name__)

# === CONFIGURACIÓN DE HASHING ===

# Contexto para hashing de contraseñas con bcrypt
pwd_context = CryptContext(
    schemes=["bcrypt"],
    deprecated="auto",
    bcrypt__rounds=12  # Nivel de seguridad alto para entorno gubernamental
)

# === FUNCIONES DE HASHING DE CONTRASEÑAS ===

def create_password_hash(password: str) -> str:
    """
    Genera un hash seguro de la contraseña
    
    Args:
        password: Contraseña en texto plano
        
    Returns:
        str: Hash de la contraseña
    """
    try:
        return pwd_context.hash(password)
    except Exception as e:
        logger.error(f"Error al generar hash de contraseña: {e}")
        raise ValueError("Error al procesar la contraseña")

def verify_password(plain_password: str, hashed_password: str) -> bool:
    """
    Verifica si una contraseña coincide con su hash
    
    Args:
        plain_password: Contraseña en texto plano
        hashed_password: Hash almacenado en base de datos
        
    Returns:
        bool: True si la contraseña es correcta
    """
    try:
        return pwd_context.verify(plain_password, hashed_password)
    except Exception as e:
        logger.error(f"Error al verificar contraseña: {e}")
        return False

def need_password_update(hashed_password: str) -> bool:
    """
    Verifica si una contraseña necesita ser actualizada
    (útil para migrar a algoritmos más seguros)
    
    Args:
        hashed_password: Hash actual de la contraseña
        
    Returns:
        bool: True si necesita actualización
    """
    return pwd_context.needs_update(hashed_password)

# === FUNCIONES DE JWT ===

def create_access_token(
    data: Dict[str, Any], 
    expires_delta: Optional[timedelta] = None
) -> str:
    """
    Genera un token JWT de acceso
    
    Args:
        data: Datos a incluir en el token (user_id, username, tipo_usuario, etc.)
        expires_delta: Tiempo de expiración personalizado
        
    Returns:
        str: Token JWT codificado
    """
    try:
        to_encode = data.copy()
        
        # Configurar tiempo de expiración
        if expires_delta:
            expire = datetime.utcnow() + expires_delta
        else:
            expire = datetime.utcnow() + timedelta(
                minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES
            )
        
        # Agregar campos estándar del JWT
        to_encode.update({
            "exp": expire,
            "iat": datetime.utcnow(),
            "iss": "SGD-Colca",  # Emisor: Sistema de Gobernanza Digital
            "aud": "sgd-users"   # Audiencia: usuarios del SGD
        })
        
        # Generar token
        encoded_jwt = jwt.encode(
            to_encode, 
            settings.SECRET_KEY, 
            algorithm=settings.ALGORITHM
        )
        
        logger.info(f"Token JWT generado para usuario: {data.get('username', 'unknown')}")
        return encoded_jwt
        
    except Exception as e:
        logger.error(f"Error al crear token JWT: {e}")
        raise ValueError("Error al generar token de acceso")

def create_refresh_token(user_id: int) -> str:
    """
    Genera un token JWT de renovación (refresh token)
    
    Args:
        user_id: ID del usuario
        
    Returns:
        str: Refresh token JWT
    """
    try:
        data = {
            "user_id": user_id,
            "type": "refresh",
            "exp": datetime.utcnow() + timedelta(days=settings.REFRESH_TOKEN_EXPIRE_DAYS),
            "iat": datetime.utcnow(),
            "iss": "SGD-Colca",
            "aud": "sgd-refresh"
        }
        
        return jwt.encode(data, settings.SECRET_KEY, algorithm=settings.ALGORITHM)
        
    except Exception as e:
        logger.error(f"Error al crear refresh token: {e}")
        raise ValueError("Error al generar token de renovación")

def verify_token(token: str) -> Optional[Dict[str, Any]]:
    """
    Verifica y decodifica un token JWT
    
    Args:
        token: Token JWT a verificar
        
    Returns:
        Dict con los datos del token o None si es inválido
    """
    try:
        payload = jwt.decode(
            token, 
            settings.SECRET_KEY, 
            algorithms=[settings.ALGORITHM],
            audience="sgd-users",
            issuer="SGD-Colca"
        )
        
        # Verificar que el token no haya expirado
        if datetime.utcnow() > datetime.fromtimestamp(payload.get("exp", 0)):
            logger.warning("Token JWT expirado")
            return None
        
        return payload
        
    except jwt.ExpiredSignatureError:
        logger.warning("Token JWT expirado")
        return None
    except jwt.InvalidTokenError as e:
        logger.warning(f"Token JWT inválido: {e}")
        return None
    except Exception as e:
        logger.error(f"Error al verificar token JWT: {e}")
        return None

def verify_refresh_token(token: str) -> Optional[Dict[str, Any]]:
    """
    Verifica un refresh token
    
    Args:
        token: Refresh token a verificar
        
    Returns:
        Dict con los datos del token o None si es inválido
    """
    try:
        payload = jwt.decode(
            token, 
            settings.SECRET_KEY, 
            algorithms=[settings.ALGORITHM],
            audience="sgd-refresh",
            issuer="SGD-Colca"
        )
        
        # Verificar que es un refresh token
        if payload.get("type") != "refresh":
            logger.warning("Token no es de tipo refresh")
            return None
        
        return payload
        
    except jwt.ExpiredSignatureError:
        logger.warning("Refresh token expirado")
        return None
    except jwt.InvalidTokenError as e:
        logger.warning(f"Refresh token inválido: {e}")
        return None
    except Exception as e:
        logger.error(f"Error al verificar refresh token: {e}")
        return None

# === UTILIDADES DE SEGURIDAD ===

def get_token_data(token: str) -> Optional[Dict[str, Any]]:
    """
    Extrae los datos de un token sin verificar su validez
    (útil para debugging o logs)
    
    Args:
        token: Token JWT
        
    Returns:
        Dict con los datos del token o None
    """
    try:
        # Decodificar sin verificar (solo para extraer datos)
        payload = jwt.decode(
            token, 
            options={"verify_signature": False, "verify_exp": False}
        )
        return payload
    except Exception as e:
        logger.error(f"Error al extraer datos del token: {e}")
        return None

def is_token_expired(token: str) -> bool:
    """
    Verifica si un token está expirado sin lanzar excepción
    
    Args:
        token: Token JWT a verificar
        
    Returns:
        bool: True si está expirado
    """
    try:
        payload = get_token_data(token)
        if not payload:
            return True
        
        exp_timestamp = payload.get("exp", 0)
        return datetime.utcnow() > datetime.fromtimestamp(exp_timestamp)
        
    except Exception:
        return True

def generate_api_key(user_id: int, description: str = "") -> str:
    """
    Genera una API key para acceso programático (futuro)
    
    Args:
        user_id: ID del usuario
        description: Descripción de la API key
        
    Returns:
        str: API key generada
    """
    try:
        data = {
            "user_id": user_id,
            "type": "api_key",
            "description": description,
            "created": datetime.utcnow().isoformat(),
            "iss": "SGD-Colca"
        }
        
        # API keys no expiran por defecto (se manejan manualmente)
        return jwt.encode(data, settings.SECRET_KEY, algorithm=settings.ALGORITHM)
        
    except Exception as e:
        logger.error(f"Error al generar API key: {e}")
        raise ValueError("Error al generar API key")

# === FUNCIONES DE VALIDACIÓN ===

def validate_password_strength(password: str) -> Dict[str, Any]:
    """
    Valida la fortaleza de una contraseña según las políticas del SGD
    
    Args:
        password: Contraseña a validar
        
    Returns:
        Dict con el resultado de la validación
    """
    result = {
        "valid": True,
        "errors": [],
        "score": 0,
        "suggestions": []
    }
    
    # Longitud mínima
    if len(password) < 8:
        result["valid"] = False
        result["errors"].append("La contraseña debe tener al menos 8 caracteres")
    else:
        result["score"] += 1
    
    # Al menos una mayúscula
    if not any(c.isupper() for c in password):
        result["valid"] = False
        result["errors"].append("La contraseña debe contener al menos una mayúscula")
    else:
        result["score"] += 1
    
    # Al menos una minúscula
    if not any(c.islower() for c in password):
        result["valid"] = False
        result["errors"].append("La contraseña debe contener al menos una minúscula")
    else:
        result["score"] += 1
    
    # Al menos un número
    if not any(c.isdigit() for c in password):
        result["valid"] = False
        result["errors"].append("La contraseña debe contener al menos un número")
    else:
        result["score"] += 1
    
    # Al menos un carácter especial (recomendado)
    special_chars = "!@#$%^&*()_+-=[]{}|;:,.<>?"
    if any(c in special_chars for c in password):
        result["score"] += 1
    else:
        result["suggestions"].append("Considere agregar caracteres especiales para mayor seguridad")
    
    # Longitud adicional
    if len(password) >= 12:
        result["score"] += 1
    else:
        result["suggestions"].append("Contraseñas de 12+ caracteres son más seguras")
    
    return result

# === CONFIGURACIÓN DE SESIONES ===

def create_session_data(user_id: int, ip_address: str, user_agent: str) -> Dict[str, Any]:
    """
    Crea datos de sesión para tracking de seguridad
    
    Args:
        user_id: ID del usuario
        ip_address: Dirección IP del usuario
        user_agent: User-Agent del navegador
        
    Returns:
        Dict con datos de la sesión
    """
    return {
        "user_id": user_id,
        "ip_address": ip_address,
        "user_agent": user_agent[:200],  # Limitar longitud
        "created_at": datetime.utcnow().isoformat(),
        "last_activity": datetime.utcnow().isoformat()
    }

# === CONSTANTES DE SEGURIDAD ===

# Tiempo de bloqueo después de intentos fallidos (en minutos)
LOCKOUT_TIME_MINUTES = 30

# Número máximo de intentos de login
MAX_LOGIN_ATTEMPTS = 5

# Tiempo de vida de tokens en minutos
DEFAULT_ACCESS_TOKEN_EXPIRE_MINUTES = 60 * 8  # 8 horas para jornada laboral

# Roles que pueden acceder a funciones administrativas
ADMIN_ROLES = ["SUPERADMIN", "ALCALDE"]

# Módulos del sistema que requieren permisos especiales
PROTECTED_MODULES = [
    "organigrama",
    "usuarios", 
    "configuracion",
    "auditoria",
    "normativa"
]