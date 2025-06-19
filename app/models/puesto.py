"""
Modelo de Puesto para SGD-Colca
"""
from sqlalchemy import Column, String, Boolean, Integer, ForeignKey
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from .base import BaseModel


class Puesto(BaseModel):
    __tablename__ = "puesto"
    
    codigo = Column(String(20), unique=True, nullable=False)
    nombre = Column(String(200), nullable=False)
    unidad_organica_id = Column(UUID(as_uuid=True), ForeignKey("unidad_organica.id"), nullable=False)
    nivel_jerarquico = Column(Integer, nullable=False)
    puede_firmar = Column(Boolean, default=False)
    puede_aprobar = Column(Boolean, default=False)
    
    # Relaciones
    unidad_organica = relationship("UnidadOrganica", back_populates="puestos")    
