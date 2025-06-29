# app/core/permissions/base.py

from enum import Enum

class PermisosGenerales(str, Enum):
    """Permisos generales del sistema"""
    ADMIN_TOTAL = "ADMIN_TOTAL"
    CONFIGURACION_SISTEMA = "CONFIGURACION_SISTEMA"
    REPORTES_GLOBALES = "REPORTES_GLOBALES"
    AUDITORIA = "AUDITORIA"

class TiposOperacion(str, Enum):
    """Tipos básicos de operaciones CRUD"""
    CREAR = "CREAR"
    LEER = "LEER"
    ACTUALIZAR = "ACTUALIZAR"
    ELIMINAR = "ELIMINAR"
    EXPORTAR = "EXPORTAR"
    APROBAR = "APROBAR"