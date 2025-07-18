# app/schemas/common/pagination_schemas.py

from typing import Generic, List, Optional, TypeVar
from pydantic import BaseModel
from app.schemas.common.sorting_schemas import SortConfig

T = TypeVar("T")

class ListaResponse(BaseModel, Generic[T]):
    data: List[T]
    total: int
    inicio: int
    fin: int
    totalPages: int
    hasNextPage: bool
    hasPrevPage: bool
    currentPage: int
    appliedSort: Optional[SortConfig] = None
