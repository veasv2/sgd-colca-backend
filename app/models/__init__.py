"""
Modelos de SGD-Colca
Importa todos los modelos para que Alembic los detecte
"""
from .base import BaseModel
from .usuario import UnidadOrganica, Puesto, Usuario
from .documento import TipoDocumento, DocumentoTDI
from .mesa_partes import ExpedienteMesaPartes
from .auditoria import AuditLog

# Exportar todos los modelos
__all__ = [
    "BaseModel",
    "UnidadOrganica", 
    "Puesto", 
    "Usuario",
    "TipoDocumento", 
    "DocumentoTDI",
    "ExpedienteMesaPartes",
    "AuditLog"
]
