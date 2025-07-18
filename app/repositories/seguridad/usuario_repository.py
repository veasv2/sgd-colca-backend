# app/repositories/usuario_repository.py

from typing import Optional
from sqlalchemy.orm import Session
from sqlalchemy import or_
from datetime import datetime

from app.models import Usuario
from app.schemas import UsuarioCreate, UsuarioUpdate
from app.repositories.base_repository import BaseRepository

class UsuarioRepository(BaseRepository[Usuario, UsuarioCreate, UsuarioUpdate]):
    def __init__(self):
        super().__init__(Usuario)

# Instancia del repositorio
usuario_repository = UsuarioRepository()