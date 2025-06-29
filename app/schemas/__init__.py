# app/schemas/__init__.py

from .seguridad import (
    UsuarioCreate, UsuarioUpdate, UsuarioRead, UsuarioInDB,
    PermisoCreate, PermisoUpdate, PermisoRead,
    SesionUsuarioRead, RegistroEventosRead
)

from .organizacion import (
    UnidadOrganicaCreate, UnidadOrganicaUpdate, UnidadOrganicaRead, UnidadOrganicaInDB,
    PuestoCreate, PuestoUpdate, PuestoRead, PuestoInDB
)
