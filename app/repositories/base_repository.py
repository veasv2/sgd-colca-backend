# app/repositories/base_repository.py

from typing import Generic, TypeVar, Type, Optional, List, Dict, Any
from sqlalchemy.orm import Session
from sqlalchemy import and_, or_, desc, asc
from app.core.database import Base

ModelType = TypeVar("ModelType", bound=Base)
CreateSchemaType = TypeVar("CreateSchemaType")
UpdateSchemaType = TypeVar("UpdateSchemaType")

class BaseRepository(Generic[ModelType, CreateSchemaType, UpdateSchemaType]):
    def __init__(self, model: Type[ModelType]):
        self.model = model

    def get(self, db: Session, id: int) -> Optional[ModelType]:
        """Obtener un registro por ID"""
        return db.query(self.model).filter(self.model.id == id).first()

    def get_by_uuid(self, db: Session, uuid: str) -> Optional[ModelType]:
        """Obtener un registro por UUID"""
        if hasattr(self.model, 'uuid'):
            return db.query(self.model).filter(self.model.uuid == uuid).first()
        return None

    def get_multi(
        self, 
        db: Session, 
        skip: int = 0, 
        limit: int = 100,
        filters: Optional[Dict[str, Any]] = None,
        order_by: Optional[str] = None,
        order_desc: bool = False
    ) -> List[ModelType]:
        """Obtener múltiples registros con filtros y paginación"""
        query = db.query(self.model)
        
        # Aplicar filtros
        if filters:
            for field, value in filters.items():
                if hasattr(self.model, field) and value is not None:
                    if isinstance(value, str):
                        # Búsqueda parcial para strings
                        query = query.filter(getattr(self.model, field).ilike(f"%{value}%"))
                    else:
                        query = query.filter(getattr(self.model, field) == value)
        
        # Aplicar ordenamiento
        if order_by and hasattr(self.model, order_by):
            if order_desc:
                query = query.order_by(desc(getattr(self.model, order_by)))
            else:
                query = query.order_by(asc(getattr(self.model, order_by)))
        
        return query.offset(skip).limit(limit).all()

    def count(self, db: Session, filters: Optional[Dict[str, Any]] = None) -> int:
        """Contar registros con filtros opcionales"""
        query = db.query(self.model)
        
        if filters:
            for field, value in filters.items():
                if hasattr(self.model, field) and value is not None:
                    if isinstance(value, str):
                        query = query.filter(getattr(self.model, field).ilike(f"%{value}%"))
                    else:
                        query = query.filter(getattr(self.model, field) == value)
        
        return query.count()

    def create(self, db: Session, obj_in: CreateSchemaType) -> ModelType:
        """Crear un nuevo registro"""
        obj_in_data = obj_in.dict() if hasattr(obj_in, 'dict') else obj_in
        db_obj = self.model(**obj_in_data)
        db.add(db_obj)
        db.commit()
        db.refresh(db_obj)
        return db_obj

    def update(
        self, 
        db: Session, 
        db_obj: ModelType, 
        obj_in: UpdateSchemaType
    ) -> ModelType:
        """Actualizar un registro existente"""
        obj_data = obj_in.dict(exclude_unset=True) if hasattr(obj_in, 'dict') else obj_in
        
        for field, value in obj_data.items():
            if hasattr(db_obj, field):
                setattr(db_obj, field, value)
        
        db.add(db_obj)
        db.commit()
        db.refresh(db_obj)
        return db_obj

    def delete(self, db: Session, id: int) -> ModelType:
        """Eliminar un registro por ID"""
        obj = db.query(self.model).get(id)
        if obj:
            db.delete(obj)
            db.commit()
        return obj

    def exists(self, db: Session, id: int) -> bool:
        """Verificar si existe un registro por ID"""
        return db.query(self.model).filter(self.model.id == id).first() is not None

    def get_by_field(self, db: Session, field: str, value: Any) -> Optional[ModelType]:
        """Obtener un registro por cualquier campo"""
        if hasattr(self.model, field):
            return db.query(self.model).filter(getattr(self.model, field) == value).first()
        return None

    def get_multi_by_field(self, db: Session, field: str, value: Any) -> List[ModelType]:
        """Obtener múltiples registros por cualquier campo"""
        if hasattr(self.model, field):
            return db.query(self.model).filter(getattr(self.model, field) == value).all()
        return []