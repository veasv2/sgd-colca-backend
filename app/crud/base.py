# En app/crud/base.py

from typing import Any, Dict, Generic, List, Optional, Type, TypeVar, Union
from uuid import UUID

from fastapi.encoders import jsonable_encoder
from pydantic import BaseModel
from sqlalchemy.orm import Session

from app.core.database import Base # Asumiendo que tu Base de SQLAlchemy está aquí

ModelType = TypeVar("ModelType", bound=Base)
CreateSchemaType = TypeVar("CreateSchemaType", bound=BaseModel)
UpdateSchemaType = TypeVar("UpdateSchemaType", bound=BaseModel)

class CRUDBase(Generic[ModelType, CreateSchemaType, UpdateSchemaType]):
    """
    Clase base para operaciones CRUD.
    Proporciona métodos genéricos para Crear, Leer, Actualizar, Eliminar.
    """
    def __init__(self, model: Type[ModelType]):
        """
        Objeto CRUD con métodos predeterminados para Crear, Leer, Actualizar, Eliminar (CRUD).

        Args:
            model: Una clase de modelo de SQLAlchemy
        """
        self.model = model

    def get(self, db: Session, id: UUID) -> Optional[ModelType]:
        """Obtener un único objeto por su ID."""
        return db.query(self.model).filter(self.model.id == id).first()

    def get_all(self, db: Session, skip: int = 0, limit: int = 100) -> List[ModelType]:
        """Obtener una lista de objetos con paginación."""
        return db.query(self.model).offset(skip).limit(limit).all()

    def create(self, db: Session, obj_in: CreateSchemaType) -> ModelType:
        """Crear un nuevo objeto."""
        obj_in_data = jsonable_encoder(obj_in)
        db_obj = self.model(**obj_in_data)
        db.add(db_obj)
        db.commit()
        db.refresh(db_obj)
        return db_obj

    def update(
        self,
        db: Session,
        db_obj: ModelType,
        obj_in: Union[UpdateSchemaType, Dict[str, Any]]
    ) -> ModelType:
        """Actualizar un objeto existente."""
        obj_data = jsonable_encoder(db_obj)
        if isinstance(obj_in, dict):
            update_data = obj_in
        else:
            update_data = obj_in.dict(exclude_unset=True) # exclude_unset=True es crucial para PATCH

        for field in obj_data:
            if field in update_data:
                setattr(db_obj, field, update_data[field])

        db.add(db_obj)
        db.commit()
        db.refresh(db_obj)
        return db_obj

    def remove(self, db: Session, id: UUID) -> Optional[ModelType]:
        """Eliminar (borrado duro) un objeto por su ID."""
        obj = db.query(self.model).filter(self.model.id == id).first()
        if obj:
            db.delete(obj)
            db.commit()
        return obj

    def count(self, db: Session) -> int:
        """Contar todos los objetos."""
        return db.query(self.model).count()