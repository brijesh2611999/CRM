import uuid

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.account import Account
from app.schemas.account import AccountCreate, AccountUpdate
from sqlalchemy import select, func


# async def list_accounts(db: AsyncSession, tenant_id: uuid.UUID) -> list[Account]:
#     result = await db.execute(
#         select(Account).where(Account.tenant_id == tenant_id, Account.is_deleted == False)
#     )
#     return result.scalars().all()

async def list_accounts(
    db: AsyncSession,
    tenant_id: uuid.UUID,
    search: str | None = None,
    account_type: str | None = None,
    status: str | None = None,
    kyc_status: str | None = None,
    page: int = 1,
    page_size: int = 25,
) -> tuple[list[Account], int]:
    query = select(Account).where(Account.tenant_id == tenant_id, Account.is_deleted == False)

    if search:
        pattern = f"%{search}%"
        query = query.where(
            (Account.name.ilike(pattern)) | (Account.code.ilike(pattern))
        )
    if account_type:
        query = query.where(Account.account_type == account_type)
    if status:
        query = query.where(Account.status == status)
    if kyc_status:
        query = query.where(Account.kyc_status == kyc_status)

    count_query = select(func.count()).select_from(query.subquery())
    total = (await db.execute(count_query)).scalar_one()

    query = query.order_by(Account.created_at.desc()).offset((page - 1) * page_size).limit(page_size)
    result = await db.execute(query)
    items = result.scalars().all()

    return items, total

async def get_account(db: AsyncSession, tenant_id: uuid.UUID, account_id: uuid.UUID) -> Account | None:
    result = await db.execute(
        select(Account).where(
            Account.id == account_id, Account.tenant_id == tenant_id, Account.is_deleted == False
        )
    )
    return result.scalar_one_or_none()


async def create_account(db: AsyncSession, tenant_id: uuid.UUID, user_id: uuid.UUID, data: AccountCreate) -> Account:
    account = Account(tenant_id=tenant_id, created_by=user_id, **data.model_dump())
    db.add(account)
    await db.commit()
    await db.refresh(account)
    return account


async def update_account(
    db: AsyncSession, tenant_id: uuid.UUID, user_id: uuid.UUID, account_id: uuid.UUID, data: AccountUpdate
) -> Account | None:
    account = await get_account(db, tenant_id, account_id)
    if account is None:
        return None
    for field, value in data.model_dump(exclude_unset=True).items():
        setattr(account, field, value)
    account.modified_by = user_id
    await db.commit()
    await db.refresh(account)
    return account


async def deactivate_account(db: AsyncSession, tenant_id: uuid.UUID, user_id: uuid.UUID, account_id: uuid.UUID) -> Account | None:
    account = await get_account(db, tenant_id, account_id)
    if account is None:
        return None
    account.is_deleted = True
    account.status = "Inactive"
    account.modified_by = user_id
    await db.commit()
    await db.refresh(account)
    return account


async def merge_accounts(
    db: AsyncSession, tenant_id: uuid.UUID, user_id: uuid.UUID, primary_id: uuid.UUID, duplicate_id: uuid.UUID
) -> Account | None:
    primary = await get_account(db, tenant_id, primary_id)
    duplicate = await get_account(db, tenant_id, duplicate_id)
    if primary is None or duplicate is None:
        return None
    duplicate.is_deleted = True
    duplicate.status = "Inactive"
    duplicate.modified_by = user_id
    await db.commit()
    await db.refresh(primary)
    return primary