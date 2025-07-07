# app/models/__init__.py
"""
Modelos de la aplicación
Importar todos los modelos para que estén disponibles y Alembic los detecte
"""

# Importar todos los modelos de seguridad
# from .organizacion import (
#     UnidadOrganica,
#     Puesto
# )

# Importar todos los modelos de organización
from .seguridad import (
    Usuario,
    # Permiso,
    # SesionUsuario,
    # RegistroEventos    
)