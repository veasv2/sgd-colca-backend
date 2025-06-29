# app/core/permissions/__init__.py

from .base import PermisosGenerales, TiposOperacion
from .seguridad import (
    PermisosUsuarios,
    PermisosSesiones,
    PermisosEventos,
    PermisosPermisos
)
from .organizacion import (
    PermisosPuestos,
    PermisosUnidadOrganica,
    PermisosOrganizacion
)
from .utils import (
    get_user_permissions,
    user_has_permission,
    require_permission,
    require_any_permission,
    require_role_or_permission
)

__all__ = [
    # Permisos base
    "PermisosGenerales",
    "TiposOperacion",
    
    # Permisos de seguridad
    "PermisosUsuarios",
    "PermisosSesiones", 
    "PermisosEventos",
    "PermisosPermisos",
    
    # Permisos de organización
    "PermisosPuestos",
    "PermisosUnidadOrganica",
    "PermisosOrganizacion",
    
    # Funciones utilitarias
    "get_user_permissions",
    "user_has_permission",
    "require_permission",
    "require_any_permission",
    "require_role_or_permission"
]