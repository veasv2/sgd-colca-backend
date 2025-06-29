# app/models/seguridad_models.py

from sqlalchemy import Column, Integer, String, Boolean, DateTime, Text, ForeignKey, Table
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
import uuid
from enum import Enum
from app.core.database import Base

class TipoUsuario(str, Enum):
    SUPERADMIN = "SUPERADMIN"
    ALCALDE = "ALCALDE"
    FUNCIONARIO = "FUNCIONARIO"

class EstadoUsuario(str, Enum):
    ACTIVO = "ACTIVO"
    INACTIVO = "INACTIVO"
    SUSPENDIDO = "SUSPENDIDO"

class TipoPermiso(str, Enum):
    LECTURA = "LECTURA"
    ESCRITURA = "ESCRITURA"
    ADMINISTRACION = "ADMINISTRACION"
    CONFIGURACION = "CONFIGURACION"

puesto_permisos = Table(
    'puesto_permisos',
    Base.metadata,
    Column('puesto_id', Integer, ForeignKey('organizacion.puestos.id'), primary_key=True),
    Column('permiso_id', Integer, ForeignKey('seguridad.permisos.id'), primary_key=True),
    Column('fecha_asignacion', DateTime, default=func.now()),
    Column('asignado_por', Integer, ForeignKey('seguridad.usuarios.id', use_alter=True, name='fk_permiso_usuario', deferrable=True, initially='DEFERRED')),
    schema='seguridad'
)

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
    estado = Column(String(20), default=EstadoUsuario.ACTIVO)
    puesto_id = Column(Integer, ForeignKey('organizacion.puestos.id'))
    ultimo_acceso = Column(DateTime)
    intentos_fallidos = Column(Integer, default=0)
    bloqueado_hasta = Column(DateTime)
    fecha_creacion = Column(DateTime, default=func.now())
    fecha_actualizacion = Column(DateTime, default=func.now(), onupdate=func.now())

    sesiones = relationship("SesionUsuario", back_populates="usuario")

class Permiso(Base):
    __tablename__ = "permisos"
    __table_args__ = {'schema': 'seguridad'}

    id = Column(Integer, primary_key=True, index=True)
    codigo = Column(String(50), unique=True, nullable=False)
    nombre = Column(String(100), nullable=False)
    descripcion = Column(Text)
    modulo = Column(String(50), nullable=False)
    tipo_permiso = Column(String(20), nullable=False)
    activo = Column(Boolean, default=True)
    fecha_creacion = Column(DateTime, default=func.now())

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
