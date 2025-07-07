# app/models/seguridad/usuario_model.py

from sqlalchemy import Column, Integer, String, Boolean, DateTime
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
import uuid
from app.core.database import Base

class Usuario(Base):
    __tablename__ = "usuario"
    __table_args__ = {'schema': 'seguridad'}

    id = Column(Integer, primary_key=True, index=True)
    uuid = Column(String(36), unique=True, default=lambda: str(uuid.uuid4()), nullable=False)
    email = Column(String(100), unique=True, nullable=False)
    nombres = Column(String(100), nullable=False)
    apellido_paterno = Column(String(100), nullable=False)
    apellido_materno = Column(String(100), nullable=False)
    dni = Column(String(8), unique=True, nullable=True)  # Opcional según schema
    telefono = Column(String(15), nullable=True)  # Opcional según schema
    tipo = Column(String(20), nullable=False)  # Corresponde a TipoUsuario enum (campo 'tipo' en schema)
    estado = Column(String(20), default="ACTIVO", nullable=False)  # Corresponde a EstadoUsuario enum
    intentos_fallidos = Column(Integer, default=0, nullable=False)
    bloqueado_hasta = Column(DateTime, nullable=True)
    ultimo_acceso = Column(DateTime, nullable=True)
    fecha_creacion = Column(DateTime, default=func.now(), nullable=False)
    fecha_actualizacion = Column(DateTime, default=func.now(), onupdate=func.now(), nullable=False)
    
    # Campo para almacenar la contraseña (no está en los schemas de respuesta por seguridad)
    password_hash = Column(String(255), nullable=False)