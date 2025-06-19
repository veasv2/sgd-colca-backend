# En app/crud/usuario.py

from typing import List, Optional, Type
from uuid import UUID
from sqlalchemy.orm import Session, joinedload
from sqlalchemy import and_, or_

# Importa tus modelos y esquemas
from app.models.puesto import Puesto
from app.models.unidad_organica import UnidadOrganica
from app.models.usuario import Usuario
from app.schemas.usuario import UsuarioCreate, UsuarioUpdate

# Importa la CRUDBase genérica
from app.crud.base import CRUDBase

class CRUDUsuario(CRUDBase[Usuario, UsuarioCreate, UsuarioUpdate]):
    """
    Operaciones CRUD para el modelo Usuario.
    Extiende CRUDBase y añade métodos específicos para Usuario.
    """
    def __init__(self, model: Type[Usuario]):
        super().__init__(model)
        # Puedes definir opciones predeterminadas para joinedload aquí si la mayoría de los métodos las usan
        self._default_options = [
            joinedload(Usuario.puesto).joinedload(Puesto.unidad_organica)
        ]

    def get_all(
        self,
        db: Session,
        skip: int = 0,
        limit: int = 100,
        activo: Optional[bool] = None
    ) -> List[Usuario]:
        """Obtener todos los usuarios con joins a puesto y unidad, con filtro opcional de activo."""
        query = db.query(self.model).options(*self._default_options)

        if activo is not None:
            query = query.filter(self.model.activo == activo)

        return query.offset(skip).limit(limit).all()

    def get(self, db: Session, id: UUID) -> Optional[Usuario]:
        """Obtener un único usuario por ID con joins a puesto y unidad."""
        return db.query(self.model).options(*self._default_options).filter(self.model.id == id).first()
    
    def get_by_firebase_uid(self, db: Session, firebase_uid: str) -> Optional[Usuario]:
        """Obtener usuario por Firebase UID."""
        return db.query(self.model).filter(self.model.firebase_uid == firebase_uid).first()
    
    def get_by_email(self, db: Session, email: str) -> Optional[Usuario]:
        """Obtener usuario por email."""
        return db.query(self.model).filter(self.model.email == email).first()
    
    # Sobreescribe el método base `remove` para realizar un borrado suave
    def remove(self, db: Session, id: UUID) -> bool:
        """Realiza un borrado suave (establece activo=False) para un usuario."""
        db_usuario = db.query(self.model).filter(self.model.id == id).first()
        if not db_usuario:
            return False
        
        db_usuario.activo = False # Realiza el borrado suave
        db.commit()
        db.refresh(db_usuario) # Refresca para reflejar el cambio
        return True
    
    def count(self, db: Session, activo: Optional[bool] = None) -> int:
        """Contar usuarios con un filtro opcional de activo."""
        query = db.query(self.model)
        if activo is not None:
            query = query.filter(self.model.activo == activo)
        return query.count()
    
    def search(self, db: Session, search_term: str, skip: int = 0, limit: int = 100) -> List[Usuario]:
        """Buscar usuarios por nombre, apellido o email con joins."""
        search_filter = or_(
            self.model.nombres.ilike(f"%{search_term}%"),
            self.model.apellidos.ilike(f"%{search_term}%"),
            self.model.email.ilike(f"%{search_term}%")
        )
        
        return db.query(self.model).options(*self._default_options).filter(search_filter).offset(skip).limit(limit).all()

# Instancia el objeto CRUD
usuario_crud = CRUDUsuario(Usuario)