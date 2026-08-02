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


async def create_user(
    db: AsyncSession, tenant_id: uuid.UUID, user_data
) -> User:
    from app.core.security import hash_password
    from fastapi import HTTPException
    from app.models.role import Role

    # Ensure email is not taken globally
    existing_query = select(User).where(User.email == user_data.email)
    existing = (await db.execute(existing_query)).scalars().first()
    if existing:
        raise HTTPException(status_code=400, detail="Email already registered")

    # Ensure role_id is valid and belongs to the same tenant
    role_query = select(Role).where(Role.id == user_data.role_id, Role.tenant_id == tenant_id)
    role = (await db.execute(role_query)).scalars().first()
    if not role:
        raise HTTPException(status_code=400, detail="Invalid role or role does not belong to your tenant")

    new_user = User(
        id=uuid.uuid4(),
        tenant_id=tenant_id,
        email=user_data.email,
        hashed_password=hash_password(user_data.password),
        full_name=user_data.full_name,
        is_active=True,
        role_id=user_data.role_id
    )
    db.add(new_user)
    await db.commit()
    await db.refresh(new_user)
    return new_user
