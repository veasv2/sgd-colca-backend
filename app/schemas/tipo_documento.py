from datetime import datetime
from typing import Optional
from uuid import UUID

from pydantic import BaseModel, Field

# Esquema Base para TipoDocumento
class TipoDocumentoBase(BaseModel):
    """
    Esquema base para la creación o actualización de un Tipo de Documento.
    Define los campos comunes y obligatorios.
    """
    codigo: str = Field(..., max_length=20, description="Código único del tipo de documento (ej. 'OFICIO', 'MEMO').")
    nombre: str = Field(..., max_length=100, description="Nombre completo del tipo de documento.")
    prefijo_correlativo: str = Field(..., max_length=10, description="Prefijo usado para generar números correlativos (ej. 'OF', 'MEM').")
    requiere_cargo: bool = Field(True, description="Indica si el documento requiere acuse de recibo.")
    plantilla_gdoc_id: Optional[str] = Field(None, max_length=200, description="ID de la plantilla de Google Docs asociada (opcional).")

# Esquema para crear un TipoDocumento
class TipoDocumentoCreate(TipoDocumentoBase):
    """
    Esquema para crear un nuevo Tipo de Documento.
    No requiere el ID, ya que se generará en la base de datos.
    """
    pass

# Esquema para actualizar un TipoDocumento
class TipoDocumentoUpdate(TipoDocumentoBase):
    """
    Esquema para actualizar un Tipo de Documento.
    Todos los campos son opcionales para permitir actualizaciones parciales.
    """
    codigo: Optional[str] = Field(None, max_length=20, description="Código único del tipo de documento (ej. 'OFICIO', 'MEMO').")
    nombre: Optional[str] = Field(None, max_length=100, description="Nombre completo del tipo de documento.")
    prefijo_correlativo: Optional[str] = Field(None, max_length=10, description="Prefijo usado para generar números correlativos (ej. 'OF', 'MEM').")
    requiere_cargo: Optional[bool] = Field(None, description="Indica si el documento requiere acuse de recibo.")
    plantilla_gdoc_id: Optional[str] = Field(None, max_length=200, description="ID de la plantilla de Google Docs asociada (opcional).")


# Esquema para la respuesta de un TipoDocumento
class TipoDocumentoResponse(TipoDocumentoBase):
    """
    Esquema para representar un Tipo de Documento en las respuestas de la API.
    Incluye el ID y las marcas de tiempo.
    """
    id: UUID = Field(..., description="Identificador único del tipo de documento.")
    created_at: datetime = Field(..., description="Fecha y hora de creación del registro.")
    updated_at: datetime = Field(..., description="Fecha y hora de la última actualización del registro.")

    class Config:
        from_attributes = True # Permite mapear desde ORM objects