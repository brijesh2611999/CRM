import uuid
from typing import TypeVar, Generic, Type

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

ModelT = TypeVar("ModelT")


class GenericMasterService(Generic[ModelT]):
    def __init__(self, model: Type[ModelT]):
        self.model = model

    async def list_all(self, db: AsyncSession, tenant_id: uuid.UUID) -> list[ModelT]:
        result = await db.execute(
            select(self.model).where(
                self.model.tenant_id == tenant_id, self.model.is_deleted == False
            )
        )
        return result.scalars().all()

    async def get_one(self, db: AsyncSession, tenant_id: uuid.UUID, record_id: uuid.UUID) -> ModelT | None:
        result = await db.execute(
            select(self.model).where(
                self.model.id == record_id,
                self.model.tenant_id == tenant_id,
                self.model.is_deleted == False,
            )
        )
        return result.scalar_one_or_none()

    async def create(self, db: AsyncSession, tenant_id: uuid.UUID, user_id: uuid.UUID, data: dict) -> ModelT:
        obj = self.model(tenant_id=tenant_id, created_by=user_id, **data)
        db.add(obj)
        await db.commit()
        await db.refresh(obj)
        return obj

    async def update(
        self, db: AsyncSession, tenant_id: uuid.UUID, user_id: uuid.UUID, record_id: uuid.UUID, data: dict
    ) -> ModelT | None:
        obj = await self.get_one(db, tenant_id, record_id)
        if obj is None:
            return None
        for field, value in data.items():
            setattr(obj, field, value)
        obj.modified_by = user_id
        await db.commit()
        await db.refresh(obj)
        return obj

    async def deactivate(self, db: AsyncSession, tenant_id: uuid.UUID, user_id: uuid.UUID, record_id: uuid.UUID) -> ModelT | None:
        obj = await self.get_one(db, tenant_id, record_id)
        if obj is None:
            return None
        obj.is_deleted = True
        obj.status = "Inactive"
        obj.modified_by = user_id
        await db.commit()
        await db.refresh(obj)
        return obj