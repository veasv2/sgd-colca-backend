# app/data/__init__.py
"""
Paquete de datos iniciales y de testing para SGD Colca
"""

from .initial_data import (
    PERMISOS_INICIALES,
    MUNICIPALIDAD_PRINCIPAL,
    UNIDADES_ORGANICAS_INICIALES,
    PUESTOS_INICIALES, 
    USUARIO_ADMIN_INICIAL,
    CONFIGURACION_INICIAL
)

from .test_data import (
    USUARIOS_TEST,
    UNIDADES_TEST,
    PUESTOS_TEST,
    CONFIG_DESARROLLO,
    ESCENARIOS_TEST
)

__all__ = [
    # Datos iniciales del sistema
    "PERMISOS_INICIALES",
    "MUNICIPALIDAD_PRINCIPAL", 
    "UNIDADES_ORGANICAS_INICIALES",
    "PUESTOS_INICIALES",
    "USUARIO_ADMIN_INICIAL",
    "CONFIGURACION_INICIAL",
    
    # Datos de testing
    "USUARIOS_TEST",
    "UNIDADES_TEST", 
    "PUESTOS_TEST",
    "CONFIG_DESARROLLO",
    "ESCENARIOS_TEST"
]