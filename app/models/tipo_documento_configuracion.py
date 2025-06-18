# app/models/tipo_documento_configuracion.py
"""
Modelo de TipoDocumentoConfiguracion para SGD-Colca
Configuraciones básicas para cada tipo de documento
"""
from sqlalchemy import Column, String, Boolean, Integer, ForeignKey
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from .base import BaseModel


class TipoDocumentoConfiguracion(BaseModel):
    __tablename__ = "tipo_documento_configuracion"
    
    # Relación con tipo de documento (1:1)
    tipo_documento_id = Column(
        UUID(as_uuid=True), 
        ForeignKey("tipos_documento.id"), 
        nullable=False, 
        unique=True,
        index=True
    )
    
    # Configuraciones básicas
    requiere_destinatario_interno = Column(Boolean, default=True)
    requiere_destinatario_externo = Column(Boolean, default=False)
    requiere_visto_bueno = Column(Boolean, default=False)
    
    # Numeración
    formato_numeracion = Column(String(100), default="{prefijo}-{año}-{correlativo:04d}")
    correlativo_por_unidad = Column(Boolean, default=False)
    
    # Visibilidad
    es_publico = Column(Boolean, default=False)
    
    # Adjuntos
    permite_adjuntos = Column(Boolean, default=True)
    max_adjuntos = Column(Integer, default=5)
    
    # Google Drive
    plantilla_gdoc_id = Column(String(200), nullable=True)
    
    # Relación
    tipo_documento = relationship("TipoDocumento", back_populates="configuracion")
    
    def __repr__(self):
        return f"<TipoDocumentoConfiguracion(tipo_documento_id={self.tipo_documento_id})>"