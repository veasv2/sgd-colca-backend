# app/core/permissions/usuarios.py

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