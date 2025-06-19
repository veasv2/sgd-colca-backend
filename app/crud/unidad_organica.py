# En app/crud/unidad_organica.py (crea este archivo si aún no existe)

from typing import List, Optional, Type
from uuid import UUID
from sqlalchemy.orm import Session, joinedload
from sqlalchemy import or_

# Importa tus modelos y esquemas
from app.models.unidad_organica import UnidadOrganica # Asegúrate de la ruta correcta a tu modelo
from app.schemas.unidad_organica import UnidadOrganicaCreate, UnidadOrganicaUpdate # Asegúrate de la ruta correcta a tus esquemas

# Importa la CRUDBase genérica
from app.crud.base import CRUDBase # Asegúrate de la ruta correcta a tu CRUDBase

class CRUDUnidadOrganica(CRUDBase[UnidadOrganica, UnidadOrganicaCreate, UnidadOrganicaUpdate]):
    """
    Operaciones CRUD para el modelo UnidadOrganica.
    Extiende CRUDBase y añade métodos específicos para UnidadOrganica.
    """
    def __init__(self, model: Type[UnidadOrganica]):
        super().__init__(model)
        # Puedes definir opciones predeterminadas para joinedload aquí si la mayoría de los métodos las usan
        # Por ejemplo, si siempre quieres cargar la unidad padre al obtener una unidad.
        # self._default_options = [
        #     joinedload(UnidadOrganica.unidad_padre)
        # ]

    def get_by_codigo(self, db: Session, codigo: str) -> Optional[UnidadOrganica]:
        """Obtiene una unidad orgánica por su código único."""
        # Se puede añadir options(*self._default_options) si es necesario cargar relaciones
        return db.query(self.model).filter(self.model.codigo == codigo).first()

    def get_by_nombre(self, db: Session, nombre: str) -> Optional[UnidadOrganica]:
        """Obtiene una unidad orgánica por su nombre."""
        # Se puede añadir options(*self._default_options) si es necesario cargar relaciones
        return db.query(self.model).filter(self.model.nombre == nombre).first()

    def search(self, db: Session, search_term: str, skip: int = 0, limit: int = 100) -> List[UnidadOrganica]:
        """Busca unidades orgánicas por nombre o código."""
        search_filter = or_(
            self.model.nombre.ilike(f"%{search_term}%"),
            self.model.codigo.ilike(f"%{search_term}%")
        )
        # Puedes añadir options(*self._default_options) si es necesario cargar relaciones
        return db.query(self.model).filter(search_filter).offset(skip).limit(limit).all()

    # Los métodos get (por ID), get_all (listado), create, update y remove
    # ya son proporcionados por CRUDBase.

    # Si necesitas un 'count' con filtros específicos para UnidadOrganica, lo añadirías aquí
    # def count_filtered(self, db: Session, some_filter: Any) -> int:
    #     query = db.query(self.model)
    #     # Add specific filters
    #     return query.count()


# Instancia el objeto CRUD para UnidadOrganica
unidad_organica_crud = CRUDUnidadOrganica(UnidadOrganica)