# app/repositories/usuario_repository.py

from typing import Optional
from sqlalchemy.orm import Session
from sqlalchemy import or_

from app.models import Usuario
from app.schemas import UsuarioCreate, UsuarioUpdate
from app.repositories.base_repository import BaseRepository

class UsuarioRepository(BaseRepository[Usuario, UsuarioCreate, UsuarioUpdate]):
    def __init__(self):
        super().__init__(Usuario)

    def get_by_username(self, db: Session, username: str) -> Optional[Usuario]:
        """Obtener usuario por username"""
        return db.query(Usuario).filter(Usuario.username == username).first()

    def get_by_email(self, db: Session, email: str) -> Optional[Usuario]:
        """Obtener usuario por email"""
        return db.query(Usuario).filter(Usuario.email == email).first()

    def get_by_dni(self, db: Session, dni: str) -> Optional[Usuario]:
        """Obtener usuario por DNI"""
        return db.query(Usuario).filter(Usuario.dni == dni).first()

    def get_by_credentials(self, db: Session, username_or_email: str) -> Optional[Usuario]:
        """Obtener usuario por username o email (para login)"""
        return db.query(Usuario).filter(
            or_(
                Usuario.username == username_or_email,
                Usuario.email == username_or_email
            )
        ).first()

    def is_username_taken(self, db: Session, username: str, exclude_id: Optional[int] = None) -> bool:
        """Verificar si el username ya está en uso"""
        query = db.query(Usuario).filter(Usuario.username == username)
        if exclude_id:
            query = query.filter(Usuario.id != exclude_id)
        return query.first() is not None

    def is_email_taken(self, db: Session, email: str, exclude_id: Optional[int] = None) -> bool:
        """Verificar si el email ya está en uso"""
        query = db.query(Usuario).filter(Usuario.email == email)
        if exclude_id:
            query = query.filter(Usuario.id != exclude_id)
        return query.first() is not None

    def is_dni_taken(self, db: Session, dni: str, exclude_id: Optional[int] = None) -> bool:
        """Verificar si el DNI ya está en uso"""
        query = db.query(Usuario).filter(Usuario.dni == dni)
        if exclude_id:
            query = query.filter(Usuario.id != exclude_id)
        return query.first() is not None

# Instancia del repositorio
usuario_repository = UsuarioRepository()