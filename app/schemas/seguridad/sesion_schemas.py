# app/schemas/seguridad/sesion_schemas.py

from pydantic import BaseModel
from typing import Optional
from datetime import datetime

class SesionUsuarioBase(BaseModel):
    ip_address: Optional[str] = None
    user_agent: Optional[str] = None

class SesionUsuarioRead(SesionUsuarioBase):
    id: int
    usuario_id: int
    token_sesion: str
    fecha_inicio: datetime
    fecha_ultimo_acceso: datetime
    fecha_cierre: Optional[datetime]
    activa: bool
