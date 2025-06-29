# app/core/permissions/seguridad.py

from enum import Enum

class PermisosUsuarios(str, Enum):
    """Permisos específicos para el módulo de usuarios"""
    CREAR = "USUARIOS_CREAR"
    LEER = "USUARIOS_LEER"
    ACTUALIZAR = "USUARIOS_ACTUALIZAR"
    ELIMINAR = "USUARIOS_ELIMINAR"
    CAMBIAR_ESTADO = "USUARIOS_CAMBIAR_ESTADO"
    VER_TODOS = "USUARIOS_VER_TODOS"
    RESETEAR_PASSWORD = "USUARIOS_RESETEAR_PASSWORD"
    ASIGNAR_PERMISOS = "USUARIOS_ASIGNAR_PERMISOS"
    BLOQUEAR_DESBLOQUEAR = "USUARIOS_BLOQUEAR_DESBLOQUEAR"

class PermisosSesiones(str, Enum):
    """Permisos para gestión de sesiones de usuario"""
    VER_SESIONES = "SESIONES_VER"
    CERRAR_SESIONES = "SESIONES_CERRAR"
    VER_TODAS_SESIONES = "SESIONES_VER_TODAS"
    AUDITORIA_SESIONES = "SESIONES_AUDITORIA"

class PermisosEventos(str, Enum):
    """Permisos para registro de eventos y auditoría"""
    VER_EVENTOS = "EVENTOS_VER"
    VER_TODOS_EVENTOS = "EVENTOS_VER_TODOS"
    EXPORTAR_EVENTOS = "EVENTOS_EXPORTAR"
    CONFIGURAR_AUDITORIA = "EVENTOS_CONFIGURAR_AUDITORIA"

class PermisosPermisos(str, Enum):
    """Permisos para gestión de permisos del sistema"""
    CREAR = "PERMISOS_CREAR"
    LEER = "PERMISOS_LEER"
    ACTUALIZAR = "PERMISOS_ACTUALIZAR"
    ELIMINAR = "PERMISOS_ELIMINAR"
    ACTIVAR_DESACTIVAR = "PERMISOS_ACTIVAR_DESACTIVAR"
    ASIGNAR_A_PUESTOS = "PERMISOS_ASIGNAR_PUESTOS"
