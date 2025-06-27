from sqlalchemy import Column, Integer, String, Boolean, DateTime, Text, ForeignKey, Table
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from datetime import datetime
from enum import Enum
import uuid
from app.core.database import Base

# Tabla de asociación many-to-many entre Puestos y Permisos
puesto_permisos = Table(
    'puesto_permisos',
    Base.metadata,
    Column('puesto_id', Integer, ForeignKey('puestos.id'), primary_key=True),
    Column('permiso_id', Integer, ForeignKey('permisos.id'), primary_key=True),
    Column('fecha_asignacion', DateTime, default=func.now()),
    Column('asignado_por', Integer, ForeignKey('usuarios.id'))
)

class TipoUsuario(str, Enum):
    """Tipos de usuario según el diseño del sistema"""
    SUPERADMIN = "SUPERADMIN"  # Rol técnico inicial
    ALCALDE = "ALCALDE"       # Máximos permisos funcionales
    FUNCIONARIO = "FUNCIONARIO"  # Usuario estándar del sistema

class EstadoUsuario(str, Enum):
    """Estados posibles de un usuario"""
    ACTIVO = "ACTIVO"
    INACTIVO = "INACTIVO" 
    SUSPENDIDO = "SUSPENDIDO"

class TipoPermiso(str, Enum):
    """Categorías de permisos del sistema"""
    LECTURA = "LECTURA"
    ESCRITURA = "ESCRITURA"
    ADMINISTRACION = "ADMINISTRACION"
    CONFIGURACION = "CONFIGURACION"

# Modelo: Areas Organizacionales
class Area(Base):
    __tablename__ = "areas"
    
    id = Column(Integer, primary_key=True, index=True)
    uuid = Column(String(36), unique=True, default=lambda: str(uuid.uuid4()))
    codigo = Column(String(10), unique=True, nullable=False)  # Ej: "GM", "OAJ", "UTI"
    nombre = Column(String(100), nullable=False)  # Ej: "Gerencia Municipal"
    descripcion = Column(Text)
    area_padre_id = Column(Integer, ForeignKey('areas.id'), nullable=True)  # Para jerarquía
    nivel = Column(Integer, default=1)  # Nivel jerárquico (1=más alto)
    activa = Column(Boolean, default=True)
    
    # Campos de auditoría
    fecha_creacion = Column(DateTime, default=func.now())
    fecha_actualizacion = Column(DateTime, default=func.now(), onupdate=func.now())
    creado_por = Column(Integer, ForeignKey('usuarios.id'))
    
    # Relaciones
    area_padre = relationship("Area", remote_side=[id])
    sub_areas = relationship("Area", back_populates="area_padre")
    puestos = relationship("Puesto", back_populates="area")

# Modelo: Puestos del Organigrama (CLAVE DEL SISTEMA)
class Puesto(Base):
    __tablename__ = "puestos"
    
    id = Column(Integer, primary_key=True, index=True)
    uuid = Column(String(36), unique=True, default=lambda: str(uuid.uuid4()))
    codigo = Column(String(20), unique=True, nullable=False)  # Ej: "ALC-001", "GM-001"
    nombre = Column(String(100), nullable=False)  # Ej: "Alcalde", "Gerente Municipal"
    descripcion = Column(Text)
    area_id = Column(Integer, ForeignKey('areas.id'), nullable=False)
    puesto_superior_id = Column(Integer, ForeignKey('puestos.id'))  # Jefe directo
    nivel_jerarquico = Column(Integer, nullable=False)  # 1=Alcalde, 2=Gerente, etc.
    activo = Column(Boolean, default=True)
    
    # Campos de auditoría
    fecha_creacion = Column(DateTime, default=func.now())
    fecha_actualizacion = Column(DateTime, default=func.now(), onupdate=func.now())
    creado_por = Column(Integer, ForeignKey('usuarios.id'))
    
    # Relaciones
    area = relationship("Area", back_populates="puestos")
    puesto_superior = relationship("Puesto", remote_side=[id])
    puestos_subordinados = relationship("Puesto", back_populates="puesto_superior")
    usuarios = relationship("Usuario", back_populates="puesto")
    permisos = relationship("Permiso", secondary=puesto_permisos, back_populates="puestos")

# Modelo: Usuarios del Sistema
class Usuario(Base):
    __tablename__ = "usuarios"
    
    id = Column(Integer, primary_key=True, index=True)
    uuid = Column(String(36), unique=True, default=lambda: str(uuid.uuid4()))
    
    # Datos de autenticación
    username = Column(String(50), unique=True, nullable=False)
    email = Column(String(100), unique=True, nullable=False)
    password_hash = Column(String(255), nullable=False)
    
    # Datos personales
    nombres = Column(String(100), nullable=False)
    apellidos = Column(String(100), nullable=False)
    dni = Column(String(8), unique=True)
    telefono = Column(String(15))
    
    # Configuración del sistema
    tipo_usuario = Column(String(20), nullable=False)  # TipoUsuario enum
    estado = Column(String(20), default=EstadoUsuario.ACTIVO)
    puesto_id = Column(Integer, ForeignKey('puestos.id'))  # Puesto asignado
    
    # Control de sesiones
    ultimo_acceso = Column(DateTime)
    intentos_fallidos = Column(Integer, default=0)
    bloqueado_hasta = Column(DateTime)
    
    # Campos de auditoría
    fecha_creacion = Column(DateTime, default=func.now())
    fecha_actualizacion = Column(DateTime, default=func.now(), onupdate=func.now())
    creado_por = Column(Integer, ForeignKey('usuarios.id'))
    
    # Relaciones
    puesto = relationship("Puesto", back_populates="usuarios")
    sesiones = relationship("SesionUsuario", back_populates="usuario")

# Modelo: Permisos del Sistema
class Permiso(Base):
    __tablename__ = "permisos"
    
    id = Column(Integer, primary_key=True, index=True)
    codigo = Column(String(50), unique=True, nullable=False)  # Ej: "MESA_PARTES_READ"
    nombre = Column(String(100), nullable=False)
    descripcion = Column(Text)
    modulo = Column(String(50), nullable=False)  # Módulo del sistema
    tipo_permiso = Column(String(20), nullable=False)  # TipoPermiso enum
    activo = Column(Boolean, default=True)
    
    # Campos de auditoría
    fecha_creacion = Column(DateTime, default=func.now())
    
    # Relaciones
    puestos = relationship("Puesto", secondary=puesto_permisos, back_populates="permisos")

# Modelo: Sesiones de Usuario (Control de acceso)
class SesionUsuario(Base):
    __tablename__ = "sesiones_usuario"
    
    id = Column(Integer, primary_key=True, index=True)
    usuario_id = Column(Integer, ForeignKey('usuarios.id'), nullable=False)
    token_sesion = Column(String(255), unique=True, nullable=False)
    ip_address = Column(String(45))  # IPv4 o IPv6
    user_agent = Column(Text)
    fecha_inicio = Column(DateTime, default=func.now())
    fecha_ultimo_acceso = Column(DateTime, default=func.now())
    fecha_cierre = Column(DateTime)
    activa = Column(Boolean, default=True)
    
    # Relaciones
    usuario = relationship("Usuario", back_populates="sesiones")

# Modelo: Bitácora de Auditoría (MVP - Versión Estándar)
class BitacoraAuditoria(Base):
    __tablename__ = "bitacora_auditoria"
    
    id = Column(Integer, primary_key=True, index=True)
    uuid = Column(String(36), unique=True, default=lambda: str(uuid.uuid4()))
    
    # Datos del evento
    usuario_id = Column(Integer, ForeignKey('usuarios.id'))
    accion = Column(String(100), nullable=False)  # CREATE, UPDATE, DELETE, LOGIN, etc.
    modulo = Column(String(50), nullable=False)   # Módulo afectado
    entidad = Column(String(50))                  # Tabla/Entidad afectada
    entidad_id = Column(String(50))               # ID del registro afectado
    
    # Contexto del evento
    datos_anteriores = Column(Text)  # JSON con estado anterior
    datos_nuevos = Column(Text)      # JSON con estado nuevo
    ip_address = Column(String(45))
    user_agent = Column(Text)
    
    # Timestamp del evento
    fecha_evento = Column(DateTime, default=func.now())
    
    # Para la versión futura con blockchain
    hash_bloque = Column(String(64))  # SHA-256 del bloque (reservado)
    hash_anterior = Column(String(64))  # Hash del bloque anterior (reservado)
    
    # Relaciones
    usuario = relationship("Usuario")