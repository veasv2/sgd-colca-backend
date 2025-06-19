# In app/models/unidad_organica.py

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
    # Para la relación recursiva, es importante especificar remote_side
    # y si la relación va a cargar la unidad padre, o las hijas
    unidad_padre = relationship(
        "UnidadOrganica",
        remote_side="UnidadOrganica.id",
        backref="unidades_hijas", # This automatically creates a 'unidades_hijas' property on UnidadOrganica
        uselist=False # If a child only has one parent
    )
    # The 'unidades_hijas' relationship is implicitly created by backref="unidades_hijas"

    # THIS IS THE MISSING OR INCORRECT PART THAT NEEDS TO BE ADDED/FIXED
    # Define the relationship to Puesto, and specify back_populates to Puesto.unidad_organica
    puestos = relationship("Puesto", back_populates="unidad_organica") # <--- ADD/FIX THIS LINE