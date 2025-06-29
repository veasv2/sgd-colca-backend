#app/models/seguridad/registro_eventos_model.py

from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, Text
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
import uuid
from app.core.database import Base

class RegistroEventos(Base):
    __tablename__ = "registro_eventos"
    __table_args__ = {'schema': 'seguridad'}

    id = Column(Integer, primary_key=True, index=True)
    uuid = Column(String(36), unique=True, default=lambda: str(uuid.uuid4()))
    usuario_id = Column(Integer, ForeignKey('seguridad.usuarios.id', use_alter=True, name='fk_evento_usuario', deferrable=True, initially='DEFERRED'))
    accion = Column(String(100), nullable=False)
    modulo = Column(String(50), nullable=False)
    entidad = Column(String(50))
    entidad_id = Column(String(50))
    datos_anteriores = Column(Text)
    datos_nuevos = Column(Text)
    ip_address = Column(String(45))
    user_agent = Column(Text)
    fecha_evento = Column(DateTime, default=func.now())
    hash_bloque = Column(String(64))
    hash_anterior = Column(String(64))

    usuario = relationship("Usuario")
