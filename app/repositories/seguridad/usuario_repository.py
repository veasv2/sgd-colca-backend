# app/repositories/seguridad/usuario_repository.py

from app.models.seguridad.usuario_model import Usuario
from app.schemas.seguridad.usuario.usuario_schemas import UsuarioCreate, UsuarioUpdate
from app.repositories.base_repository import BaseRepository

class UsuarioRepository(BaseRepository[Usuario, UsuarioCreate, UsuarioUpdate]):
    def __init__(self):
        super().__init__(Usuario)

# Instancia del repositorio para inyección de dependencias
usuario_repository = UsuarioRepository()