from datetime import datetime
from typing import Optional
from uuid import UUID

from pydantic import BaseModel, Field

# Esquema Base para Documento
class DocumentoBase(BaseModel):
    """
    Esquema base para la creación o actualización de un Documento.
    Define los campos comunes y obligatorios.
    """
    numero_correlativo: str = Field(..., max_length=50, description="Número correlativo único del documento (ej. 'OFICIO-2025-001').")
    tipo_documento_id: UUID = Field(..., description="ID del tipo de documento al que pertenece.")
    usuario_emisor_id: UUID = Field(..., description="ID del usuario que emite el documento.")
    unidad_emisora_id: UUID = Field(..., description="ID de la unidad orgánica que emite el documento.")
    
    destinatario_interno: Optional[str] = Field(None, max_length=200, description="Destinatario(s) interno(s) del documento.")
    destinatario_externo: Optional[str] = Field(None, description="Destinatario(s) externo(s) del documento (puede ser un texto largo).")
    asunto: str = Field(..., description="Asunto o título del documento.")
    contenido: Optional[str] = Field(None, description="Contenido textual detallado del documento.")
    
    gdoc_id: Optional[str] = Field(None, max_length=200, description="ID del documento en Google Docs.")
    gdoc_url: Optional[str] = Field(None, description="URL de acceso al documento en Google Docs.")
    pdf_drive_id: Optional[str] = Field(None, max_length=200, description="ID del archivo PDF generado en Google Drive.")
    
    estado: str = Field("BORRADOR", max_length=50, description="Estado actual del documento (ej. 'BORRADOR', 'APROBADO', 'ENVIADO').")
    requiere_aprobacion: bool = Field(False, description="Indica si el documento necesita aprobación.")
    aprobado_por_id: Optional[UUID] = Field(None, description="ID del usuario que aprobó el documento (opcional).")
    fecha_aprobacion: Optional[datetime] = Field(None, description="Fecha y hora de la aprobación del documento (opcional).")
    prioridad: str = Field("NORMAL", max_length=20, description="Nivel de prioridad (ej. 'NORMAL', 'ALTA', 'URGENTE').")
    confidencial: bool = Field(False, description="Indica si el documento es confidencial.")

# Esquema para crear un Documento
class DocumentoCreate(DocumentoBase):
    """
    Esquema para crear un nuevo Documento.
    No requiere el ID, ni las fechas de aprobación, ya que se manejarán automáticamente.
    """
    pass

# Esquema para actualizar un Documento
class DocumentoUpdate(DocumentoBase):
    """
    Esquema para actualizar un Documento.
    Todos los campos son opcionales para permitir actualizaciones parciales.
    """
    numero_correlativo: Optional[str] = Field(None, max_length=50, description="Número correlativo único del documento (ej. 'OFICIO-2025-001').")
    tipo_documento_id: Optional[UUID] = Field(None, description="ID del tipo de documento al que pertenece.")
    usuario_emisor_id: Optional[UUID] = Field(None, description="ID del usuario que emite el documento.")
    unidad_emisora_id: Optional[UUID] = Field(None, description="ID de la unidad orgánica que emite el documento.")
    
    destinatario_interno: Optional[str] = Field(None, max_length=200, description="Destinatario(s) interno(s) del documento.")
    destinatario_externo: Optional[str] = Field(None, description="Destinatario(s) externo(s) del documento (puede ser un texto largo).")
    asunto: Optional[str] = Field(None, description="Asunto o título del documento.")
    contenido: Optional[str] = Field(None, description="Contenido textual detallado del documento.")
    
    gdoc_id: Optional[str] = Field(None, max_length=200, description="ID del documento en Google Docs.")
    gdoc_url: Optional[str] = Field(None, description="URL de acceso al documento en Google Docs.")
    pdf_drive_id: Optional[str] = Field(None, max_length=200, description="ID del archivo PDF generado en Google Drive.")
    
    estado: Optional[str] = Field(None, max_length=50, description="Estado actual del documento (ej. 'BORRADOR', 'APROBADO', 'ENVIADO').")
    requiere_aprobacion: Optional[bool] = Field(None, description="Indica si el documento necesita aprobación.")
    # `aprobado_por_id` y `fecha_aprobacion` se manejarían en lógica de negocio para cambios de estado a aprobado
    prioridad: Optional[str] = Field(None, max_length=20, description="Nivel de prioridad (ej. 'NORMAL', 'ALTA', 'URGENTE').")
    confidencial: Optional[bool] = Field(None, description="Indica si el documento es confidencial.")


# Esquema para la respuesta de un Documento
class DocumentoResponse(DocumentoBase):
    """
    Esquema para representar un Documento en las respuestas de la API.
    Incluye el ID y las marcas de tiempo.
    """
    id: UUID = Field(..., description="Identificador único del documento.")
    created_at: datetime = Field(..., description="Fecha y hora de creación del registro.")
    updated_at: datetime = Field(..., description="Fecha y hora de la última actualización del registro.")

    # Opcional: Incluir relaciones si se van a expandir en la respuesta
    # tipo_documento: Optional[TipoDocumentoResponse] = None
    # usuario_emisor: Optional[UsuarioResponse] = None # Necesitarías definir UsuarioResponse
    # unidad_emisora: Optional[UnidadOrganicaResponse] = None # Necesitarías definir UnidadOrganicaResponse
    # aprobado_por: Optional[UsuarioResponse] = None

    class Config:
        from_attributes = True # Permite mapear desde ORM objects
        # `populate_by_name = True` es útil si los campos ORM no coinciden exactamente con los campos Pydantic