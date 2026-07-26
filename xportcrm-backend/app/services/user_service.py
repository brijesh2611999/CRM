import uuid
from typing import Sequence
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.user import User


async def list_users(db: AsyncSession, tenant_id: uuid.UUID) -> Sequence[User]:
    """
    List all active users for a specific tenant.
    """
    query = select(User).where(User.tenant_id == tenant_id, User.is_active == True)
    result = await db.execute(query)
    return result.scalars().all()
