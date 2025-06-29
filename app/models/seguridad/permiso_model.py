#app/models/seguridad/permiso_model.py

from sqlalchemy import Column, Integer, String, Boolean, DateTime, Text, ForeignKey, Table
from sqlalchemy.sql import func
from app.core.database import Base

puesto_permisos = Table(
    'puesto_permisos',
    Base.metadata,
    Column('puesto_id', Integer, ForeignKey('organizacion.puestos.id'), primary_key=True),
    Column('permiso_id', Integer, ForeignKey('seguridad.permisos.id'), primary_key=True),
    Column('fecha_asignacion', DateTime, default=func.now()),
    Column('asignado_por', Integer, ForeignKey('seguridad.usuarios.id', use_alter=True, name='fk_permiso_usuario', deferrable=True, initially='DEFERRED')),
    schema='seguridad'
)

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
