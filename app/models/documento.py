from sqlalchemy import Column, String, Boolean, DateTime, ForeignKey, Text
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from .base import BaseModel

class Documento(BaseModel):
    __tablename__ = "documento" # La tabla se nombra en singular
    
    numero_correlativo = Column(String(50), unique=True, nullable=False)
    tipo_documento_id = Column(UUID(as_uuid=True), ForeignKey("tipo_documento.id"), nullable=False)
    unidad_emisora_id = Column(UUID(as_uuid=True), ForeignKey("unidad_organica.id"), nullable=False)
    usuario_emisor_id = Column(UUID(as_uuid=True), ForeignKey("usuario.id"), nullable=False)
    
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