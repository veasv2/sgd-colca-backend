#app/models/organizacion/unidad_organica_model.py

from sqlalchemy import Column, Integer, String, Boolean, DateTime, Text, ForeignKey
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
import uuid
from app.core.database import Base

class UnidadOrganica(Base):
    __tablename__ = "unidades_organicas"
    __table_args__ = {'schema': 'organizacion'}

    id = Column(Integer, primary_key=True, index=True)
    uuid = Column(String(36), unique=True, default=lambda: str(uuid.uuid4()))
    nombre = Column(String(100), nullable=False)
    sigla = Column(String(10), unique=True, nullable=False)
    tipo = Column(String(30), nullable=False)
    descripcion = Column(Text)
    unidad_padre_id = Column(Integer, ForeignKey('organizacion.unidades_organicas.id'), nullable=True)
    nivel = Column(Integer, default=1)
    activa = Column(Boolean, default=True)
    creado_por = Column(Integer, ForeignKey('seguridad.usuarios.id', use_alter=True, name='fk_unidad_creado_por', deferrable=True, initially='DEFERRED'))

    fecha_creacion = Column(DateTime, default=func.now())
    fecha_actualizacion = Column(DateTime, default=func.now(), onupdate=func.now())

    unidad_padre = relationship("UnidadOrganica", remote_side=[id])
    subunidades = relationship("UnidadOrganica", back_populates="unidad_padre")
    puestos = relationship("Puesto", back_populates="unidad_organica")
