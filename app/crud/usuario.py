"""
CRUD operations para Usuario
"""
from typing import List, Optional
from uuid import UUID
from sqlalchemy.orm import Session, joinedload
from sqlalchemy import and_, or_

from app.models.usuario import Usuario, Puesto, UnidadOrganica
from app.schemas.usuario import UsuarioCreate, UsuarioUpdate

class UsuarioCRUD:
    
    @staticmethod
    def get_all(
        db: Session, 
        skip: int = 0, 
        limit: int = 100,
        activo: Optional[bool] = None
    ) -> List[Usuario]:
        """Obtener todos los usuarios con joins a puesto y unidad"""
        query = db.query(Usuario).options(
            joinedload(Usuario.puesto).joinedload(Puesto.unidad_organica)
        )
        
        if activo is not None:
            query = query.filter(Usuario.activo == activo)
        
        return query.offset(skip).limit(limit).all()
    
    @staticmethod
    def get_by_id(db: Session, usuario_id: UUID) -> Optional[Usuario]:
        """Obtener usuario por ID"""
        return db.query(Usuario).options(
            joinedload(Usuario.puesto).joinedload(Puesto.unidad_organica)
        ).filter(Usuario.id == usuario_id).first()
    
    @staticmethod
    def get_by_firebase_uid(db: Session, firebase_uid: str) -> Optional[Usuario]:
        """Obtener usuario por Firebase UID"""
        return db.query(Usuario).filter(Usuario.firebase_uid == firebase_uid).first()
    
    @staticmethod
    def get_by_email(db: Session, email: str) -> Optional[Usuario]:
        """Obtener usuario por email"""
        return db.query(Usuario).filter(Usuario.email == email).first()
    
    @staticmethod
    def create(db: Session, usuario: UsuarioCreate) -> Usuario:
        """Crear nuevo usuario"""
        db_usuario = Usuario(**usuario.dict())
        db.add(db_usuario)
        db.commit()
        db.refresh(db_usuario)
        return db_usuario
    
    @staticmethod
    def update(db: Session, usuario_id: UUID, usuario_update: UsuarioUpdate) -> Optional[Usuario]:
        """Actualizar usuario"""
        db_usuario = db.query(Usuario).filter(Usuario.id == usuario_id).first()
        if not db_usuario:
            return None
        
        # Actualizar solo los campos proporcionados
        update_data = usuario_update.dict(exclude_unset=True)
        for field, value in update_data.items():
            setattr(db_usuario, field, value)
        
        db.commit()
        db.refresh(db_usuario)
        return db_usuario
    
    @staticmethod
    def delete(db: Session, usuario_id: UUID) -> bool:
        """Eliminar usuario (soft delete)"""
        db_usuario = db.query(Usuario).filter(Usuario.id == usuario_id).first()
        if not db_usuario:
            return False
        
        db_usuario.activo = False
        db.commit()
        return True
    
    @staticmethod
    def count(db: Session, activo: Optional[bool] = None) -> int:
        """Contar usuarios"""
        query = db.query(Usuario)
        if activo is not None:
            query = query.filter(Usuario.activo == activo)
        return query.count()
    
    @staticmethod
    def search(db: Session, search_term: str, skip: int = 0, limit: int = 100) -> List[Usuario]:
        """Buscar usuarios por nombre, apellido o email"""
        search_filter = or_(
            Usuario.nombres.ilike(f"%{search_term}%"),
            Usuario.apellidos.ilike(f"%{search_term}%"),
            Usuario.email.ilike(f"%{search_term}%")
        )
        
        return db.query(Usuario).options(
            joinedload(Usuario.puesto).joinedload(Puesto.unidad_organica)
        ).filter(search_filter).offset(skip).limit(limit).all()

# Instancia global
usuario_crud = UsuarioCRUD()
