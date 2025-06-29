# app/models/__init__.py
"""
Modelos de la aplicación
Importar todos los modelos para que estén disponibles y Alembic los detecte
"""

# Importar todos los modelos de seguridad
from .seguridad_models import (
    Usuario,
    Permiso,
    SesionUsuario,
    RegistroEventos,
    TipoUsuario,
    EstadoUsuario,
    TipoPermiso,
    puesto_permisos
)

# Importar todos los modelos de organización
from .organizacion_models import (
    UnidadOrganica,
    Puesto
)

# Hacer que todos los modelos estén disponibles cuando se importe el paquete
__all__ = [
    # Modelos de seguridad
    "Usuario",
    "Permiso", 
    "SesionUsuario",
    "RegistroEventos",
    "TipoUsuario",
    "EstadoUsuario",
    "TipoPermiso",
    "puesto_permisos",
    
    # Modelos de organización
    "UnidadOrganica",
    "Puesto"
]