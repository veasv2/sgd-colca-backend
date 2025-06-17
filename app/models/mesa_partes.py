"""
Modelo de Mesa de Partes para SGD-Colca
"""
from sqlalchemy import Column, String, DateTime, ForeignKey, Text, Boolean
from sqlalchemy.dialects.postgresql import UUID, JSONB
from sqlalchemy.orm import relationship
from .base import BaseModel

class ExpedienteMesaPartes(BaseModel):
    __tablename__ = "expedientes_mesa_partes"
    
    numero_expediente = Column(String(50), unique=True, nullable=False)
    
    # Datos del solicitante
    solicitante_nombres = Column(String(200), nullable=False)
    solicitante_apellidos = Column(String(200))
    solicitante_dni = Column(String(8))
    solicitante_email = Column(String(255))
    solicitante_telefono = Column(String(20))
    solicitante_direccion = Column(Text)
    
    # Contenido del expediente
    asunto = Column(Text, nullable=False)
    tipo_tramite = Column(String(100))
    
    # Archivos (Google Drive)
    archivos_drive_folder_id = Column(String(200))
    
    # Estado y seguimiento
    estado = Column(String(50), default='RECIBIDO')
    unidad_destino_id = Column(UUID(as_uuid=True), ForeignKey("unidades_organicas.id"))
    usuario_asignado_id = Column(UUID(as_uuid=True), ForeignKey("usuarios.id"))
    
    # IA y OCR
    ocr_procesado = Column(Boolean, default=False)
    ocr_contenido = Column(Text)
    entidades_extraidas = Column(JSONB)
    
    # Fechas
    fecha_recepcion = Column(DateTime)
    fecha_limite = Column(DateTime)
    
    # Relaciones
    unidad_destino = relationship("UnidadOrganica")
    usuario_asignado = relationship("Usuario")
