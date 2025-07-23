# app/repositories/base_repository.py

from typing import Generic, TypeVar, Type, Optional, List, Dict, Any, Protocol
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, update, delete, func, and_, or_, desc, asc
from sqlalchemy.orm import selectinload
from abc import ABC, abstractmethod
import uuid

# Usar Any como bound para evitar error de Pylance
ModelType = TypeVar("ModelType", bound=Any)
CreateSchemaType = TypeVar("CreateSchemaType")
UpdateSchemaType = TypeVar("UpdateSchemaType")

class IBaseRepository(Protocol[ModelType, CreateSchemaType, UpdateSchemaType]):
    """Interfaz/Protocolo para repositorios base"""
    
    async def get_by_id(self, db: AsyncSession, id: int) -> Optional[ModelType]:
        """Obtener un registro por ID interno"""
        ...
    
    async def get_by_uuid(self, db: AsyncSession, uuid_str: str) -> Optional[ModelType]:
        """Obtener un registro por UUID externo"""
        ...
        
    async def get_multi(
        self, 
        db: AsyncSession, 
        skip: int = 0, 
        limit: int = 100,
        filters: Optional[Dict[str, Any]] = None,
        order_by: Optional[str] = None,
        order_desc: bool = False
    ) -> List[ModelType]:
        """Obtener múltiples registros con filtros y paginación"""
        ...
    
    async def count(self, db: AsyncSession, filters: Optional[Dict[str, Any]] = None) -> int:
        """Contar registros con filtros opcionales"""
        ...
    
    async def create(self, db: AsyncSession, obj_in: CreateSchemaType) -> ModelType:
        """Crear un nuevo registro"""
        ...
    
    async def update(
        self, 
        db: AsyncSession, 
        db_obj: ModelType, 
        obj_in: UpdateSchemaType
    ) -> ModelType:
        """Actualizar un registro existente"""
        ...
    
    async def delete_by_id(self, db: AsyncSession, id: int) -> Optional[ModelType]:
        """Eliminar un registro por ID interno"""
        ...
    
    async def delete_by_uuid(self, db: AsyncSession, uuid_str: str) -> Optional[ModelType]:
        """Eliminar un registro por UUID externo"""
        ...

class BaseRepository(Generic[ModelType, CreateSchemaType, UpdateSchemaType], ABC):
    """
    Repositorio base asíncrono con manejo de conversión UUID ↔ ID
    
    RESPONSABILIDADES:
    - Conversión UUID (externo) ↔ ID (interno de BD) SOLO en este layer
    - Operaciones CRUD asíncronas
    - Filtrado, ordenamiento y paginación
    """
    
    def __init__(self, model: Type[ModelType]):
        self.model = model

    async def get_by_id(self, db: AsyncSession, id: int) -> Optional[ModelType]:
        """Obtener un registro por ID interno (uso interno del repository)"""
        stmt = select(self.model).where(self.model.id == id)
        result = await db.execute(stmt)
        return result.scalar_one_or_none()

    async def get_by_uuid(self, db: AsyncSession, uuid_str: str) -> Optional[ModelType]:
        """Obtener un registro por UUID externo (conversión UUID → ID)"""
        if not hasattr(self.model, 'uuid'):
            return None
        
        stmt = select(self.model).where(self.model.uuid == uuid_str)
        result = await db.execute(stmt)
        return result.scalar_one_or_none()

    async def get_multi(
        self, 
        db: AsyncSession, 
        skip: int = 0, 
        limit: int = 100,
        filters: Optional[Dict[str, Any]] = None,
        order_by: Optional[str] = None,
        order_desc: bool = False
    ) -> List[ModelType]:
        """Obtener múltiples registros con filtros y paginación"""
        stmt = select(self.model)
        
        # Aplicar filtros
        if filters:
            conditions = []
            for field, value in filters.items():
                if hasattr(self.model, field) and value is not None:
                    if isinstance(value, str):
                        # Búsqueda parcial para strings  
                        conditions.append(getattr(self.model, field).ilike(f"%{value}%"))
                    else:
                        conditions.append(getattr(self.model, field) == value)
            
            if conditions:
                stmt = stmt.where(and_(*conditions))
        
        # Aplicar ordenamiento
        if order_by and hasattr(self.model, order_by):
            column = getattr(self.model, order_by)
            if order_desc:
                stmt = stmt.order_by(desc(column))
            else:
                stmt = stmt.order_by(asc(column))
        
        # Aplicar paginación
        stmt = stmt.offset(skip).limit(limit)
        
        result = await db.execute(stmt)
        return result.scalars().all()

    async def count(self, db: AsyncSession, filters: Optional[Dict[str, Any]] = None) -> int:
        """Contar registros con filtros opcionales"""
        stmt = select(func.count()).select_from(self.model)
        
        if filters:
            conditions = []
            for field, value in filters.items():
                if hasattr(self.model, field) and value is not None:
                    if isinstance(value, str):
                        conditions.append(getattr(self.model, field).ilike(f"%{value}%"))
                    else:
                        conditions.append(getattr(self.model, field) == value)
            
            if conditions:
                stmt = stmt.where(and_(*conditions))
        
        result = await db.execute(stmt)
        return result.scalar()

    async def create(self, db: AsyncSession, obj_in: CreateSchemaType) -> ModelType:
        """Crear un nuevo registro"""
        obj_in_data = obj_in.model_dump() if hasattr(obj_in, 'model_dump') else obj_in
        
        # Generar UUID si el modelo lo requiere y no viene en los datos
        if hasattr(self.model, 'uuid') and 'uuid' not in obj_in_data:
            obj_in_data['uuid'] = str(uuid.uuid4())
        
        db_obj = self.model(**obj_in_data)
        db.add(db_obj)
        await db.commit()
        await db.refresh(db_obj)
        return db_obj

    async def update(
        self, 
        db: AsyncSession, 
        db_obj: ModelType, 
        obj_in: UpdateSchemaType
    ) -> ModelType:
        """Actualizar un registro existente"""
        obj_data = obj_in.model_dump(exclude_unset=True) if hasattr(obj_in, 'model_dump') else obj_in
        
        for field, value in obj_data.items():
            if hasattr(db_obj, field):
                setattr(db_obj, field, value)
        
        db.add(db_obj)
        await db.commit()
        await db.refresh(db_obj)
        return db_obj

    async def delete_by_id(self, db: AsyncSession, id: int) -> Optional[ModelType]:
        """Eliminar un registro por ID interno"""
        obj = await self.get_by_id(db, id)
        if obj:
            await db.delete(obj)
            await db.commit()
        return obj

    async def delete_by_uuid(self, db: AsyncSession, uuid_str: str) -> Optional[ModelType]:
        """Eliminar un registro por UUID externo (conversión UUID → ID)"""
        obj = await self.get_by_uuid(db, uuid_str)
        if obj:
            await db.delete(obj)
            await db.commit()
        return obj

    async def exists_by_id(self, db: AsyncSession, id: int) -> bool:
        """Verificar si existe un registro por ID interno"""
        stmt = select(self.model.id).where(self.model.id == id)
        result = await db.execute(stmt)
        return result.scalar_one_or_none() is not None

    async def exists_by_uuid(self, db: AsyncSession, uuid_str: str) -> bool:
        """Verificar si existe un registro por UUID externo"""
        if not hasattr(self.model, 'uuid'):
            return False
        
        stmt = select(self.model.id).where(self.model.uuid == uuid_str)
        result = await db.execute(stmt)
        return result.scalar_one_or_none() is not None

    async def get_by_field(self, db: AsyncSession, field: str, value: Any) -> Optional[ModelType]:
        """Obtener un registro por cualquier campo"""
        if not hasattr(self.model, field):
            return None
        
        stmt = select(self.model).where(getattr(self.model, field) == value)
        result = await db.execute(stmt)
        return result.scalar_one_or_none()

    async def get_multi_by_field(self, db: AsyncSession, field: str, value: Any) -> List[ModelType]:
        """Obtener múltiples registros por cualquier campo"""
        if not hasattr(self.model, field):
            return []
        
        stmt = select(self.model).where(getattr(self.model, field) == value)
        result = await db.execute(stmt)
        return result.scalars().all()

    async def update_by_uuid(self, db: AsyncSession, uuid_str: str, obj_in: UpdateSchemaType) -> Optional[ModelType]:
        """Actualizar un registro por UUID externo (conversión UUID → ID)"""
        db_obj = await self.get_by_uuid(db, uuid_str)
        if not db_obj:
            return None
        return await self.update(db, db_obj, obj_in)