#app/models/seguridad/usuario_model.py

from sqlalchemy import Column, Integer, String, Boolean, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
import uuid
from app.core.database import Base

class Usuario(Base):
    __tablename__ = "usuarios"
    __table_args__ = {'schema': 'seguridad'}

    id = Column(Integer, primary_key=True, index=True)
    uuid = Column(String(36), unique=True, default=lambda: str(uuid.uuid4()))
    username = Column(String(50), unique=True, nullable=False)
    email = Column(String(100), unique=True, nullable=False)
    password_hash = Column(String(255), nullable=False)
    nombres = Column(String(100), nullable=False)
    apellidos = Column(String(100), nullable=False)
    dni = Column(String(8), unique=True)
    telefono = Column(String(15))
    tipo_usuario = Column(String(20), nullable=False)
    estado = Column(String(20), default="ACTIVO")
    puesto_id = Column(Integer, ForeignKey('organizacion.puestos.id'))
    ultimo_acceso = Column(DateTime)
    intentos_fallidos = Column(Integer, default=0)
    bloqueado_hasta = Column(DateTime)
    fecha_creacion = Column(DateTime, default=func.now())
    fecha_actualizacion = Column(DateTime, default=func.now(), onupdate=func.now())

    sesiones = relationship("SesionUsuario", back_populates="usuario")
