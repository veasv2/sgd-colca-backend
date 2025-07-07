# app/services/usuario_service.py

from typing import Optional, List
from sqlalchemy.orm import Session
from fastapi import HTTPException, status

from app.models import Usuario
from app.schemas import UsuarioCreate, UsuarioUpdate
from app.repositories import UsuarioRepository
from app.core.security import hash_password, verify_password, is_password_strong

class UsuarioService:
    def __init__(self):
        self.repository = UsuarioRepository()  # ✅ INSTANCIA, no clase

    def create_usuario(self, db: Session, usuario_data: UsuarioCreate) -> Usuario:
        """
        Crear un nuevo usuario con validaciones
        """
        # Validar que el username no esté en uso
        if self.repository.is_username_taken(db, usuario_data.username):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="El nombre de usuario ya está en uso"
            )
        
        # Validar que el email no esté en uso
        if self.repository.is_email_taken(db, usuario_data.email):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="El email ya está registrado"
            )
        
        # Validar DNI si se proporciona
        if usuario_data.dni and self.repository.is_dni_taken(db, usuario_data.dni):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="El DNI ya está registrado"
            )
        
        # Validar fortaleza de la contraseña
        is_valid, errors = is_password_strong(usuario_data.password)
        if not is_valid:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Contraseña no válida: {', '.join(errors)}"
            )
        
        # Crear el usuario con contraseña hasheada
        usuario_dict = usuario_data.dict()
        usuario_dict['password_hash'] = hash_password(usuario_data.password)
        del usuario_dict['password']  # Remover la contraseña plana
        
        # ✅ Usar el método create del repositorio
        return self.repository.create(db, usuario_data)

    def get_usuario(self, db: Session, usuario_id: int) -> Optional[Usuario]:
        """
        Obtener usuario por ID
        """
        usuario = self.repository.get(db, usuario_id)
        if not usuario:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Usuario no encontrado"
            )
        return usuario

    def get_usuario_by_username(self, db: Session, username: str) -> Optional[Usuario]:
        """
        Obtener usuario por username
        """
        return self.repository.get_by_username(db, username)

    def get_usuarios(self, db: Session, skip: int = 0, limit: int = 100) -> List[Usuario]:
        """
        Obtener lista de usuarios
        """
        return self.repository.get_multi(db, skip=skip, limit=limit)

    def update_usuario(self, db: Session, usuario_id: int, usuario_data: UsuarioUpdate) -> Usuario:
        """
        Actualizar usuario existente
        """
        # Obtener usuario actual
        db_usuario = self.repository.get(db, usuario_id)
        if not db_usuario:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Usuario no encontrado"
            )
        
        # Validar username único si se está actualizando
        if usuario_data.username and self.repository.is_username_taken(db, usuario_data.username, exclude_id=usuario_id):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="El nombre de usuario ya está en uso"
            )
        
        # Validar email único si se está actualizando
        if usuario_data.email and self.repository.is_email_taken(db, usuario_data.email, exclude_id=usuario_id):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="El email ya está registrado"
            )
        
        # Validar DNI único si se está actualizando
        if usuario_data.dni and self.repository.is_dni_taken(db, usuario_data.dni, exclude_id=usuario_id):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="El DNI ya está registrado"
            )
        
        # Validar contraseña si se está actualizando
        if usuario_data.password:
            is_valid, errors = is_password_strong(usuario_data.password)
            if not is_valid:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail=f"Contraseña no válida: {', '.join(errors)}"
                )
            # Hashear nueva contraseña
            usuario_data.password = hash_password(usuario_data.password)
        
        # Actualizar usando el repositorio
        return self.repository.update(db, db_usuario, usuario_data)

    def delete_usuario(self, db: Session, usuario_id: int) -> Usuario:
        """
        Eliminar usuario
        """
        db_usuario = self.repository.get(db, usuario_id)
        if not db_usuario:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Usuario no encontrado"
            )
        
        return self.repository.delete(db, usuario_id)

    def authenticate_usuario(self, db: Session, username_or_email: str, password: str) -> Optional[Usuario]:
        """
        Autenticar usuario con username/email y contraseña
        """
        usuario = self.repository.get_by_credentials(db, username_or_email)
        
        if not usuario:
            return None
        
        if not verify_password(password, usuario.password_hash):
            return None
        
        return usuario

    def change_password(self, db: Session, usuario_id: int, current_password: str, new_password: str) -> Usuario:
        """
        Cambiar contraseña de usuario
        """
        # Obtener usuario
        db_usuario = self.repository.get(db, usuario_id)
        if not db_usuario:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Usuario no encontrado"
            )
        
        # Verificar contraseña actual
        if not verify_password(current_password, db_usuario.password_hash):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Contraseña actual incorrecta"
            )
        
        # Validar nueva contraseña
        is_valid, errors = is_password_strong(new_password)
        if not is_valid:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Nueva contraseña no válida: {', '.join(errors)}"
            )
        
        # Actualizar contraseña
        db_usuario.password_hash = hash_password(new_password)
        db.commit()
        db.refresh(db_usuario)
        
        return db_usuario

# Instancia del servicio
usuario_service = UsuarioService()