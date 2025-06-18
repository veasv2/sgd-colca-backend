"""
Modelos de SGD-Colca
Importa todos los modelos para que Alembic los detecte
"""
from .base import BaseModel
from .puesto import Puesto
from .unidad_organica import UnidadOrganica
from .usuario import  Usuario
from .documento import TipoDocumento, DocumentoTDI
from .mesa_partes import ExpedienteMesaPartes
from .auditoria import AuditLog

# Exportar todos los modelos
__all__ = [
    "BaseModel",
    "Puesto", 
    "UnidadOrganica", 
    "Usuario",
    "TipoDocumento", 
    "DocumentoTDI",
    "ExpedienteMesaPartes",
    "AuditLog"
]
