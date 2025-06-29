#app/models/seguridad/sesion_model.py

from sqlalchemy import Column, Integer, String, Boolean, DateTime, ForeignKey, Text
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.core.database import Base

class SesionUsuario(Base):
    __tablename__ = "sesiones_usuario"
    __table_args__ = {'schema': 'seguridad'}

    id = Column(Integer, primary_key=True, index=True)
    usuario_id = Column(Integer, ForeignKey('seguridad.usuarios.id'), nullable=False)
    token_sesion = Column(String(255), unique=True, nullable=False)
    ip_address = Column(String(45))
    user_agent = Column(Text)
    fecha_inicio = Column(DateTime, default=func.now())
    fecha_ultimo_acceso = Column(DateTime, default=func.now())
    fecha_cierre = Column(DateTime)
    activa = Column(Boolean, default=True)

    usuario = relationship("Usuario", back_populates="sesiones")
