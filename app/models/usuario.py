"""
Modelo de Usuario para SGD-Colca
"""
from sqlalchemy import Column, String, Boolean, DateTime, ForeignKey, Integer
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from .base import BaseModel

class UnidadOrganica(BaseModel):
    __tablename__ = "unidades_organicas"
    
    codigo = Column(String(10), unique=True, nullable=False)
    nombre = Column(String(200), nullable=False)
    descripcion = Column(String)
    unidad_padre_id = Column(UUID(as_uuid=True), ForeignKey("unidades_organicas.id"))
    nivel = Column(Integer, default=1, nullable=False)
    
    # Relaciones
    unidad_padre = relationship("UnidadOrganica", remote_side="UnidadOrganica.id")
    puestos = relationship("Puesto", back_populates="unidad_organica")

class Puesto(BaseModel):
    __tablename__ = "puestos"
    
    codigo = Column(String(20), unique=True, nullable=False)
    nombre = Column(String(200), nullable=False)
    unidad_organica_id = Column(UUID(as_uuid=True), ForeignKey("unidades_organicas.id"), nullable=False)
    nivel_jerarquico = Column(Integer, nullable=False)
    puede_firmar = Column(Boolean, default=False)
    puede_aprobar = Column(Boolean, default=False)
    
    # Relaciones
    unidad_organica = relationship("UnidadOrganica", back_populates="puestos")
    usuarios = relationship("Usuario", back_populates="puesto")

class Usuario(BaseModel):
    __tablename__ = "usuarios"
    
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
