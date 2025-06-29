# app/core/validators/domain.py

from pydantic import BaseModel, Field
from typing import Optional, Annotated
from datetime import datetime

from app.core.validators.factory import (
    crear_tipo_texto,
    crear_tipo_numero,
    crear_validador_email_institucional,
    crear_validador_dni
)

# =============================================================================
# TIPOS DE TEXTO COMUNES EN EL DOMINIO ORGANIZACIONAL
# =============================================================================

NombreType = crear_tipo_texto(min_length=3, max_length=100, formato_titulo=True)
SiglaType = crear_tipo_texto(min_length=2, max_length=10, solo_mayusculas=True, sin_espacios=True)
CodigoPuestoType = crear_tipo_texto(min_length=4, max_length=20, patron_regex=r"^[A-Z0-9\-]+$", solo_mayusculas=True, sin_espacios=True)
DescripcionType = crear_tipo_texto(min_length=5, max_length=500, requerido=False)

# =============================================================================
# TIPOS NUMÉRICOS COMUNES EN EL DOMINIO ORGANIZACIONAL
# =============================================================================

NivelUnidadType = crear_tipo_numero(min_valor=1, max_valor=6, tipo_base=int, permitir_cero=False, permitir_negativos=False)
NivelPuestoType = crear_tipo_numero(min_valor=1, max_valor=10, tipo_base=int, permitir_cero=False, permitir_negativos=False)

# =============================================================================
# TIPOS DE TEXTO Y VALIDACIONES PARA EL DOMINIO DE SEGURIDAD
# =============================================================================

UsernameType = crear_tipo_texto(min_length=3, max_length=50, sin_espacios=True)
EmailInstitucionalType = crear_validador_email_institucional("munihuancayo.gob.pe")
TelefonoType = crear_tipo_texto(min_length=6, max_length=15, patron_regex=r"^\d{6,15}$", sin_espacios=True)
DNIPeruanoType = crear_validador_dni()
