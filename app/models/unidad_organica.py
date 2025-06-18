"""
Modelo de Unidad Orgánica para SGD-Colca
"""
from sqlalchemy import Column, String, Integer, ForeignKey
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from .base import BaseModel


class UnidadOrganica(BaseModel):
    __tablename__ = "unidad_organica"
    
    codigo = Column(String(10), unique=True, nullable=False)
    nombre = Column(String(200), nullable=False)
    descripcion = Column(String)
    unidad_padre_id = Column(UUID(as_uuid=True), ForeignKey("unidad_organica.id"))
    nivel = Column(Integer, default=1, nullable=False)
    
    # Relaciones
    unidad_padre = relationship("UnidadOrganica", remote_side="UnidadOrganica.id")
    puestos = relationship("Puesto", back_populates="unidad_organica")
