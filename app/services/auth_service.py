# app/services/auth_service.py
"""
Servicios de Autenticación para el Sistema de Gobernanza Digital (SGD)
Municipalidad Distrital de Colca

Implementa toda la lógica de negocio para autenticación, registro,
gestión de usuarios y permisos basados en organigrama.
"""

from datetime import datetime, timedelta
from typing import Optional, Dict, Any, List
from sqlalchemy.orm import Session, joinedload
from sqlalchemy import and_, or_
from fastapi import HTTPException, status
import logging

# Importaciones locales
from app.core.security import (
    create_password_hash, 
    verify_password, 
    create_access_token,
    create_refresh_token,
    verify_token,
    verify_refresh_token,
    validate_password_strength,
    create_session_data,
    MAX_LOGIN_ATTEMPTS,
    LOCKOUT_TIME_MINUTES
)
from app.models.auth_models import Usuario, Area, Puesto, Permiso
from app.schemas.auth_schemas import (
    UsuarioCreate, 
    UsuarioUpdate, 
    LoginRequest,
    ChangePasswordRequest,
    TipoUsuarioEnum,
    EstadoUsuarioEnum
)
from app.core.config import settings

# Configurar logging
logger = logging.getLogger(__name__)

# === EXCEPCIONES PERSONALIZADAS ===

class AuthenticationError(Exception):
    """Excepción para errores de autenticación"""
    pass

class AuthorizationError(Exception):
    """Excepción para errores de autorización"""
    pass

class UserLockedError(Exception):
    """Excepción para usuario bloqueado"""
    pass

# === SERVICIO PRINCIPAL DE AUTENTICACIÓN ===

class AuthService:
    """
    Servicio principal de autenticación y autorización
    Implementa la lógica de negocio del SGD
    """
    
    def __init__(self, db: Session):
        self.db = db
        self._login_attempts_cache = {}  # En producción usar Redis
    
    # === MÉTODOS DE AUTENTICACIÓN ===
    
    def authenticate_user(self, username: str, password: str, ip_address: str = None) -> Dict[str, Any]:
        """
        Autentica un usuario y genera tokens de acceso
        
        Args:
            username: Nombre de usuario o email
            password: Contraseña en texto plano
            ip_address: Dirección IP del cliente
            
        Returns:
            Dict con tokens y información del usuario
            
        Raises:
            AuthenticationError: Si las credenciales son inválidas
            UserLockedError: Si el usuario está bloqueado
        """
        try:
            # Verificar intentos de login fallidos
            self._check_login_attempts(username, ip_address)
            
            # Buscar usuario por username o email
            user = self._get_user_by_username_or_email(username)
            
            if not user:
                self._record_failed_attempt(username, ip_address)
                raise AuthenticationError("Credenciales inválidas")
            
            # Verificar estado del usuario
            if user.estado != EstadoUsuarioEnum.ACTIVO:
                raise AuthenticationError("Usuario inactivo o suspendido")
            
            # Verificar contraseña
            if not verify_password(password, user.password_hash):
                self._record_failed_attempt(username, ip_address)
                raise AuthenticationError("Credenciales inválidas")
            
            # Limpiar intentos fallidos exitosos
            self._clear_failed_attempts(username, ip_address)
            
            # Actualizar último acceso
            user.ultimo_acceso = datetime.utcnow()
            self.db.commit()
            
            # Cargar relaciones necesarias
            user_data = self._load_user_with_relations(user.id)
            
            # Generar tokens
            access_token = self._create_access_token_for_user(user_data)
            refresh_token = create_refresh_token(user.id)
            
            logger.info(f"Usuario autenticado exitosamente: {user.username}")
            
            return {
                "access_token": access_token,
                "refresh_token": refresh_token,
                "token_type": "bearer",
                "expires_in": settings.ACCESS_TOKEN_EXPIRE_MINUTES * 60,
                "user_info": user_data
            }
            
        except (AuthenticationError, UserLockedError):
            raise
        except Exception as e:
            logger.error(f"Error en autenticación: {e}")
            raise AuthenticationError("Error interno de autenticación")
    
    def refresh_access_token(self, refresh_token: str) -> Dict[str, Any]:
        """
        Renueva un token de acceso usando un refresh token
        
        Args:
            refresh_token: Token de renovación
            
        Returns:
            Dict con nuevo access token
        """
        try:
            # Verificar refresh token
            payload = verify_refresh_token(refresh_token)
            if not payload:
                raise AuthenticationError("Refresh token inválido")
            
            user_id = payload.get("user_id")
            user = self.get_user_by_id(user_id)
            
            if not user or user.estado != EstadoUsuarioEnum.ACTIVO:
                raise AuthenticationError("Usuario no válido")
            
            # Cargar datos del usuario y generar nuevo token
            user_data = self._load_user_with_relations(user_id)
            new_access_token = self._create_access_token_for_user(user_data)
            
            return {
                "access_token": new_access_token,
                "token_type": "bearer",
                "expires_in": settings.ACCESS_TOKEN_EXPIRE_MINUTES * 60
            }
            
        except Exception as e:
            logger.error(f"Error al renovar token: {e}")
            raise AuthenticationError("Error al renovar token")
    
    def validate_current_user(self, token: str) -> Dict[str, Any]:
        """
        Valida un token y retorna información del usuario actual
        
        Args:
            token: Token JWT de acceso
            
        Returns:
            Dict con información del usuario
        """
        try:
            payload = verify_token(token)
            if not payload:
                raise AuthenticationError("Token inválido")
            
            user_id = payload.get("user_id")
            user_data = self._load_user_with_relations(user_id)
            
            if not user_data or user_data.get("estado") != EstadoUsuarioEnum.ACTIVO:
                raise AuthenticationError("Usuario no válido")
            
            return user_data
            
        except Exception as e:
            logger.error(f"Error al validar usuario actual: {e}")
            raise AuthenticationError("Token inválido")
    
    # === MÉTODOS DE GESTIÓN DE USUARIOS ===
    
    def create_user(self, user_data: UsuarioCreate, created_by_user_id: int) -> Dict[str, Any]:
        """
        Crea un nuevo usuario en el sistema
        
        Args:
            user_data: Datos del usuario a crear
            created_by_user_id: ID del usuario que crea
            
        Returns:
            Dict con información del usuario creado
        """
        try:
            # Verificar permisos del usuario creador
            if not self._can_create_user(created_by_user_id, user_data.tipo_usuario):
                raise AuthorizationError("Sin permisos para crear este tipo de usuario")
            
            # Verificar unicidad de username y email
            if self._username_exists(user_data.username):
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="El nombre de usuario ya existe"
                )
            
            if self._email_exists(user_data.email):
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="El email ya está registrado"
                )
            
            # Validar fortaleza de contraseña
            password_validation = validate_password_strength(user_data.password)
            if not password_validation["valid"]:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail=f"Contraseña insegura: {', '.join(password_validation['errors'])}"
                )
            
            # Validar puesto si se especifica
            if user_data.puesto_id:
                puesto = self.db.query(Puesto).filter(Puesto.id == user_data.puesto_id).first()
                if not puesto or not puesto.activo:
                    raise HTTPException(
                        status_code=status.HTTP_400_BAD_REQUEST,
                        detail="Puesto inválido o inactivo"
                    )
            
            # Crear usuario
            password_hash = create_password_hash(user_data.password)
            
            new_user = Usuario(
                username=user_data.username.lower(),
                email=user_data.email.lower(),
                password_hash=password_hash,
                nombres=user_data.nombres,
                apellidos=user_data.apellidos,
                dni=user_data.dni,
                telefono=user_data.telefono,
                tipo_usuario=user_data.tipo_usuario,
                estado=user_data.estado,
                puesto_id=user_data.puesto_id
            )
            
            self.db.add(new_user)
            self.db.commit()
            self.db.refresh(new_user)
            
            logger.info(f"Usuario creado: {new_user.username} por usuario ID: {created_by_user_id}")
            
            return self._load_user_with_relations(new_user.id)
            
        except HTTPException:
            raise
        except Exception as e:
            self.db.rollback()
            logger.error(f"Error al crear usuario: {e}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Error interno al crear usuario"
            )
    
    def change_password(self, user_id: int, password_change: ChangePasswordRequest) -> bool:
        """
        Cambia la contraseña de un usuario
        
        Args:
            user_id: ID del usuario
            password_change: Datos del cambio de contraseña
            
        Returns:
            bool: True si el cambio fue exitoso
        """
        try:
            user = self.get_user_by_id(user_id)
            if not user:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail="Usuario no encontrado"
                )
            
            # Verificar contraseña actual
            if not verify_password(password_change.current_password, user.password_hash):
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Contraseña actual incorrecta"
                )
            
            # Validar nueva contraseña
            password_validation = validate_password_strength(password_change.new_password)
            if not password_validation["valid"]:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail=f"Nueva contraseña insegura: {', '.join(password_validation['errors'])}"
                )
            
            # Actualizar contraseña
            user.password_hash = create_password_hash(password_change.new_password)
            user.fecha_actualizacion = datetime.utcnow()
            
            self.db.commit()
            
            logger.info(f"Contraseña cambiada para usuario: {user.username}")
            return True
            
        except HTTPException:
            raise
        except Exception as e:
            self.db.rollback()
            logger.error(f"Error al cambiar contraseña: {e}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Error interno al cambiar contraseña"
            )
    
    def update_user(self, user_id: int, user_update: UsuarioUpdate, updated_by_user_id: int) -> Dict[str, Any]:
        """
        Actualiza los datos de un usuario
        
        Args:
            user_id: ID del usuario a actualizar
            user_update: Datos a actualizar
            updated_by_user_id: ID del usuario que realiza la actualización
            
        Returns:
            Dict con información del usuario actualizado
        """
        try:
            user = self.get_user_by_id(user_id)
            if not user:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail="Usuario no encontrado"
                )
            
            # Verificar permisos
            if not self._can_update_user(updated_by_user_id, user_id, user_update):
                raise AuthorizationError("Sin permisos para actualizar este usuario")
            
            # Actualizar campos si se proporcionan
            update_data = user_update.dict(exclude_unset=True)
            
            for field, value in update_data.items():
                if field == "email" and value:
                    # Verificar unicidad del email
                    if self._email_exists(value, exclude_user_id=user_id):
                        raise HTTPException(
                            status_code=status.HTTP_400_BAD_REQUEST,
                            detail="El email ya está registrado"
                        )
                    setattr(user, field, value.lower())
                elif field == "puesto_id" and value:
                    # Validar puesto
                    puesto = self.db.query(Puesto).filter(Puesto.id == value).first()
                    if not puesto or not puesto.activo:
                        raise HTTPException(
                            status_code=status.HTTP_400_BAD_REQUEST,
                            detail="Puesto inválido o inactivo"
                        )
                    setattr(user, field, value)
                else:
                    setattr(user, field, value)
            
            user.fecha_actualizacion = datetime.utcnow()
            self.db.commit()
            
            logger.info(f"Usuario actualizado: {user.username} por usuario ID: {updated_by_user_id}")
            
            return self._load_user_with_relations(user_id)
            
        except HTTPException:
            raise
        except Exception as e:
            self.db.rollback()
            logger.error(f"Error al actualizar usuario: {e}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Error interno al actualizar usuario"
            )
    
    # === MÉTODOS DE CONSULTA ===
    
    def get_user_by_id(self, user_id: int) -> Optional[Usuario]:
        """Obtiene un usuario por su ID"""
        return self.db.query(Usuario).filter(Usuario.id == user_id).first()
    
    def get_users_by_area(self, area_id: int) -> List[Dict[str, Any]]:
        """Obtiene todos los usuarios de un área específica"""
        users = self.db.query(Usuario).join(Puesto).filter(
            Puesto.area_id == area_id,
            Usuario.estado == EstadoUsuarioEnum.ACTIVO
        ).all()
        
        return [self._load_user_with_relations(user.id) for user in users]
    
    def get_user_permissions(self, user_id: int) -> List[str]:
        """
        Obtiene los permisos de un usuario basado en su puesto
        
        Args:
            user_id: ID del usuario
            
        Returns:
            Lista de códigos de permisos
        """
        try:
            user = self.get_user_by_id(user_id)
            if not user or not user.puesto_id:
                return []
            
            # Por ahora retornamos permisos básicos según tipo de usuario
            # TODO: Implementar sistema de permisos más granular
            base_permissions = ["lectura_documentos", "creacion_documentos"]
            
            if user.tipo_usuario in ["SUPERADMIN", "ALCALDE"]:
                base_permissions.extend([
                    "administracion_usuarios",
                    "configuracion_sistema",
                    "acceso_auditoria",
                    "gestion_organigrama"
                ])
            
            return base_permissions
            
        except Exception as e:
            logger.error(f"Error al obtener permisos: {e}")
            return []
    
    # === MÉTODOS PRIVADOS ===
    
    def _get_user_by_username_or_email(self, username: str) -> Optional[Usuario]:
        """Busca un usuario por username o email"""
        return self.db.query(Usuario).filter(
            or_(
                Usuario.username == username.lower(),
                Usuario.email == username.lower()
            )
        ).first()
    
    def _load_user_with_relations(self, user_id: int) -> Dict[str, Any]:
        """Carga un usuario con todas sus relaciones"""
        user = self.db.query(Usuario).options(
            joinedload(Usuario.puesto).joinedload(Puesto.area)
        ).filter(Usuario.id == user_id).first()
        
        if not user:
            return None
        
        user_dict = {
            "id": user.id,
            "uuid": str(user.uuid),
            "username": user.username,
            "email": user.email,
            "nombres": user.nombres,
            "apellidos": user.apellidos,
            "dni": user.dni,
            "telefono": user.telefono,
            "tipo_usuario": user.tipo_usuario,
            "estado": user.estado,
            "puesto_id": user.puesto_id,
            "ultimo_acceso": user.ultimo_acceso,
            "fecha_creacion": user.fecha_creacion,
            "fecha_actualizacion": user.fecha_actualizacion
        }
        
        # Agregar información del puesto y área si existe
        if user.puesto:
            user_dict["puesto"] = {
                "id": user.puesto.id,
                "codigo": user.puesto.codigo,
                "nombre": user.puesto.nombre,
                "area": {
                    "id": user.puesto.area.id,
                    "codigo": user.puesto.area.codigo,
                    "nombre": user.puesto.area.nombre
                } if user.puesto.area else None
            }
        
        return user_dict
    
    def _create_access_token_for_user(self, user_data: Dict[str, Any]) -> str:
        """Crea un token de acceso para un usuario específico"""
        token_data = {
            "user_id": user_data["id"],
            "username": user_data["username"],
            "tipo_usuario": user_data["tipo_usuario"],
            "puesto_id": user_data.get("puesto_id"),
            "area_codigo": user_data.get("puesto", {}).get("area", {}).get("codigo") if user_data.get("puesto") else None
        }
        
        return create_access_token(token_data)
    
    def _check_login_attempts(self, username: str, ip_address: str):
        """Verifica intentos de login fallidos"""
        key = f"{username}:{ip_address}"
        attempts = self._login_attempts_cache.get(key, {"count": 0, "locked_until": None})
        
        if attempts["locked_until"] and datetime.utcnow() < attempts["locked_until"]:
            raise UserLockedError("Usuario temporalmente bloqueado")
    
    def _record_failed_attempt(self, username: str, ip_address: str):
        """Registra un intento de login fallido"""
        key = f"{username}:{ip_address}"
        attempts = self._login_attempts_cache.get(key, {"count": 0, "locked_until": None})
        
        attempts["count"] += 1
        
        if attempts["count"] >= MAX_LOGIN_ATTEMPTS:
            attempts["locked_until"] = datetime.utcnow() + timedelta(minutes=LOCKOUT_TIME_MINUTES)
            logger.warning(f"Usuario bloqueado por intentos fallidos: {username} desde {ip_address}")
        
        self._login_attempts_cache[key] = attempts
    
    def _clear_failed_attempts(self, username: str, ip_address: str):
        """Limpia intentos fallidos después de login exitoso"""
        key = f"{username}:{ip_address}"
        if key in self._login_attempts_cache:
            del self._login_attempts_cache[key]
    
    def _username_exists(self, username: str, exclude_user_id: int = None) -> bool:
        """Verifica si un username ya existe"""
        query = self.db.query(Usuario).filter(Usuario.username == username.lower())
        if exclude_user_id:
            query = query.filter(Usuario.id != exclude_user_id)
        return query.first() is not None
    
    def _email_exists(self, email: str, exclude_user_id: int = None) -> bool:
        """Verifica si un email ya existe"""
        query = self.db.query(Usuario).filter(Usuario.email == email.lower())
        if exclude_user_id:
            query = query.filter(Usuario.id != exclude_user_id)
        return query.first() is not None
    
    def _can_create_user(self, creator_user_id: int, user_type: TipoUsuarioEnum) -> bool:
        """Verifica si un usuario puede crear otro tipo de usuario"""
        creator = self.get_user_by_id(creator_user_id)
        if not creator:
            return False
        
        # SUPERADMIN puede crear cualquier tipo
        if creator.tipo_usuario == TipoUsuarioEnum.SUPERADMIN:
            return True
        
        # ALCALDE puede crear FUNCIONARIOS
        if creator.tipo_usuario == TipoUsuarioEnum.ALCALDE and user_type == TipoUsuarioEnum.FUNCIONARIO:
            return True
        
        return False
    
    def _can_update_user(self, updater_user_id: int, target_user_id: int, update_data: UsuarioUpdate) -> bool:
        """Verifica si un usuario puede actualizar a otro"""
        updater = self.get_user_by_id(updater_user_id)
        target = self.get_user_by_id(target_user_id)
        
        if not updater or not target:
            return False
        
        # Los usuarios pueden actualizar sus propios datos (excepto tipo_usuario)
        if updater_user_id == target_user_id:
            return update_data.tipo_usuario is None
        
        # SUPERADMIN puede actualizar a cualquiera
        if updater.tipo_usuario == TipoUsuarioEnum.SUPERADMIN:
            return True
        
        # ALCALDE puede actualizar FUNCIONARIOS
        if (updater.tipo_usuario == TipoUsuarioEnum.ALCALDE and 
            target.tipo_usuario == TipoUsuarioEnum.FUNCIONARIO):
            return True
        
        return False

# === FUNCIONES DE UTILIDAD ===

def get_auth_service(db: Session) -> AuthService:
    """Factory function para crear instancia del servicio de autenticación"""
    return AuthService(db)