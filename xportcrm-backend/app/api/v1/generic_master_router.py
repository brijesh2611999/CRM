import uuid
from typing import Type
from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import get_current_tenant_id, get_current_user_id, require_permission
from app.db.session import get_db
from app.services.generic_master_service import GenericMasterService


def build_master_router(
    model,
    create_schema: Type[BaseModel],
    update_schema: Type[BaseModel],
    read_schema: Type[BaseModel],
    module_name: str = "masters",
) -> APIRouter:
    router = APIRouter()
    service = GenericMasterService(model)

    @router.get("/", response_model=list[read_schema])
    async def list_records(
        tenant_id: uuid.UUID = Depends(get_current_tenant_id),
        db: AsyncSession = Depends(get_db),
    ):
        return await service.list_all(db, tenant_id)

    @router.post("/", response_model=read_schema, status_code=201)
    async def create_record(
        data: create_schema,
        tenant_id: uuid.UUID = Depends(get_current_tenant_id),
        user_id: uuid.UUID = Depends(get_current_user_id),
        db: AsyncSession = Depends(get_db),
        _current_user = Depends(require_permission(module_name, "create")),
    ):
        return await service.create(db, tenant_id, user_id, data.model_dump())

    @router.get("/{record_id}", response_model=read_schema)
    async def get_record(
        record_id: uuid.UUID,
        tenant_id: uuid.UUID = Depends(get_current_tenant_id),
        db: AsyncSession = Depends(get_db),
    ):
        obj = await service.get_one(db, tenant_id, record_id)
        if obj is None:
            raise HTTPException(status_code=404, detail="Record not found")
        return obj

    @router.put("/{record_id}", response_model=read_schema)
    async def update_record(
        record_id: uuid.UUID,
        data: update_schema,
        tenant_id: uuid.UUID = Depends(get_current_tenant_id),
        user_id: uuid.UUID = Depends(get_current_user_id),
        db: AsyncSession = Depends(get_db),
        _current_user = Depends(require_permission(module_name, "update")),
    ):
        obj = await service.update(db, tenant_id, user_id, record_id, data.model_dump(exclude_unset=True))
        if obj is None:
            raise HTTPException(status_code=404, detail="Record not found")
        return obj

    @router.delete("/{record_id}", response_model=read_schema)
    async def deactivate_record(
        record_id: uuid.UUID,
        tenant_id: uuid.UUID = Depends(get_current_tenant_id),
        user_id: uuid.UUID = Depends(get_current_user_id),
        db: AsyncSession = Depends(get_db),
        _current_user = Depends(require_permission(module_name, "delete")),
    ):
        obj = await service.deactivate(db, tenant_id, user_id, record_id)
        if obj is None:
            raise HTTPException(status_code=404, detail="Record not found")
        return obj

    return router