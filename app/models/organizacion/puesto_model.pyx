#app/models/organizacion/unidad_organica_model.py

from sqlalchemy import Column, Integer, String, Boolean, DateTime, Text, ForeignKey
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
import uuid
from app.core.database import Base

class Puesto(Base):
    __tablename__ = "puestos"
    __table_args__ = {'schema': 'organizacion'}

    id = Column(Integer, primary_key=True, index=True)
    uuid = Column(String(36), unique=True, default=lambda: str(uuid.uuid4()))
    nombre = Column(String(100), nullable=False)
    codigo = Column(String(20), unique=True, nullable=False)
    descripcion = Column(Text)
    unidad_organica_id = Column(Integer, ForeignKey('organizacion.unidades_organicas.id'), nullable=False)
    puesto_superior_id = Column(Integer, ForeignKey('organizacion.puestos.id'), nullable=True)
    nivel_jerarquico = Column(Integer, nullable=False)
    activo = Column(Boolean, default=True)
    creado_por = Column(Integer, ForeignKey('seguridad.usuarios.id', use_alter=True, name='fk_puesto_creado_por', deferrable=True, initially='DEFERRED'))

    fecha_creacion = Column(DateTime, default=func.now())
    fecha_actualizacion = Column(DateTime, default=func.now(), onupdate=func.now())

    unidad_organica = relationship("UnidadOrganica", back_populates="puestos")
    puesto_superior = relationship("Puesto", remote_side=[id])
    puestos_subordinados = relationship("Puesto", back_populates="puesto_superior")
