"""
Modelo de Auditoría para SGD-Colca
"""
from sqlalchemy import Column, String, DateTime, ForeignKey, Text, Integer
from sqlalchemy.dialects.postgresql import UUID, JSONB, INET
from sqlalchemy.orm import relationship
from app.core.database import Base
import uuid
from datetime import datetime

class AuditLog(Base):
    __tablename__ = "audit_log"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    timestamp = Column(DateTime, default=datetime.utcnow, nullable=False)
    user_id = Column(UUID(as_uuid=True), ForeignKey("usuarios.id"))
    firebase_uid = Column(String(128))
    
    action_type = Column(String(100), nullable=False)
    target_table = Column(String(100))
    target_document_id = Column(UUID(as_uuid=True))
    
    details = Column(JSONB)
    ip_address = Column(INET)
    user_agent = Column(Text)
    
    # Para integridad de la cadena de auditoría
    hash_anterior = Column(String(256))
    hash_actual = Column(String(256))
    
    # Relaciones
    usuario = relationship("Usuario")
