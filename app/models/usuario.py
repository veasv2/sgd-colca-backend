"""
Modelo de Usuario para SGD-Colca
"""
from sqlalchemy import Column, String, Boolean, DateTime, ForeignKey
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from .base import BaseModel


class Usuario(BaseModel):
    __tablename__ = "usuario"
    
    firebase_uid = Column(String(128), unique=True, nullable=False)
    email = Column(String(255), unique=True, nullable=False)
    nombres = Column(String(100), nullable=False)
    apellidos = Column(String(100), nullable=False)
    dni = Column(String(8), unique=True)
    telefono = Column(String(20))
    puesto_id = Column(UUID(as_uuid=True), ForeignKey("puestos.id"))
    es_superadmin = Column(Boolean, default=False)
    ultimo_acceso = Column(DateTime)
    foto_perfil_url = Column(String(500), nullable=True)
    
    # Relaciones    
    puesto = relationship("Puesto", back_populates="usuarios")
