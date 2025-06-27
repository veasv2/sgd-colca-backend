"""
Modelos de SGD-Colca
Importa todos los modelos para que Alembic los detecte
"""
from .base import BaseModel
from .unidad_organica import UnidadOrganica
from .puesto import Puesto

__all__ = [
    "BaseModel",
    "UnidadOrganica",
    "Puesto", 
]


# from .usuario import  Usuario
# from .tipo_documento import TipoDocumento
# from .documento import Documento
# from .mesa_partes import ExpedienteMesaPartes
# from .auditoria import AuditLog

# Exportar todos los modelos
# __all__ = [
#     "BaseModel",
#     "Puesto", 
#     "UnidadOrganica", 
#     "Usuario",
#     "TipoDocumento", 
#     "Documento",
#     "ExpedienteMesaPartes",
#     "AuditLog"
# ]
