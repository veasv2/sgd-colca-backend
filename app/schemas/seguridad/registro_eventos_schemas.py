# app/schemas/seguridad/registro_eventos_schemas.py

from pydantic import BaseModel
from typing import Optional
from datetime import datetime

class RegistroEventosRead(BaseModel):
    id: int
    uuid: str
    usuario_id: Optional[int]
    accion: str
    modulo: str
    entidad: Optional[str]
    entidad_id: Optional[str]
    datos_anteriores: Optional[str]
    datos_nuevos: Optional[str]
    ip_address: Optional[str]
    user_agent: Optional[str]
    fecha_evento: datetime
    hash_bloque: Optional[str]
    hash_anterior: Optional[str]
