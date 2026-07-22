from typing import Generic, TypeVar
from pydantic import BaseModel
import uuid

T = TypeVar("T")


class PaginatedResponse(BaseModel, Generic[T]):
    total: int
    page: int
    page_size: int
    items: list[T]

class BulkIdsRequest(BaseModel):
    ids: list[uuid.UUID]


class BulkAssignRequest(BaseModel):
    ids: list[uuid.UUID]
    assigned_to_id: uuid.UUID


class BulkStatusChangeRequest(BaseModel):
    ids: list[uuid.UUID]
    status: str


class BulkActionResult(BaseModel):
    success_count: int
    failed_ids: list[uuid.UUID] = []