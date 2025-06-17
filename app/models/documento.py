"""
Modelos de Documentos para SGD-Colca
"""
from sqlalchemy import Column, String, Boolean, DateTime, ForeignKey, Text
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from .base import BaseModel

class TipoDocumento(BaseModel):
    __tablename__ = "tipos_documento"
    
    codigo = Column(String(20), unique=True, nullable=False)
    nombre = Column(String(100), nullable=False)
    prefijo_correlativo = Column(String(10), nullable=False)
    requiere_cargo = Column(Boolean, default=True)
    plantilla_gdoc_id = Column(String(200))
    
    # Relaciones
    documentos = relationship("DocumentoTDI", back_populates="tipo_documento")

class DocumentoTDI(BaseModel):
    __tablename__ = "documentos_tdi"
    
    numero_correlativo = Column(String(50), unique=True, nullable=False)
    tipo_documento_id = Column(UUID(as_uuid=True), ForeignKey("tipos_documento.id"), nullable=False)
    usuario_emisor_id = Column(UUID(as_uuid=True), ForeignKey("usuarios.id"), nullable=False)
    unidad_emisora_id = Column(UUID(as_uuid=True), ForeignKey("unidades_organicas.id"), nullable=False)
    
    destinatario_interno = Column(String(200))
    destinatario_externo = Column(Text)
    asunto = Column(Text, nullable=False)
    contenido = Column(Text)
    
    # Google Drive
    gdoc_id = Column(String(200))
    gdoc_url = Column(Text)
    pdf_drive_id = Column(String(200))
    
    # Control de flujo
    estado = Column(String(50), default='BORRADOR')
    requiere_aprobacion = Column(Boolean, default=False)
    aprobado_por_id = Column(UUID(as_uuid=True), ForeignKey("usuarios.id"))
    fecha_aprobacion = Column(DateTime)
    prioridad = Column(String(20), default='NORMAL')
    confidencial = Column(Boolean, default=False)
    
    # Relaciones
    tipo_documento = relationship("TipoDocumento", back_populates="documentos")
    usuario_emisor = relationship("Usuario", foreign_keys=[usuario_emisor_id])
    unidad_emisora = relationship("UnidadOrganica")
    aprobado_por = relationship("Usuario", foreign_keys=[aprobado_por_id])
