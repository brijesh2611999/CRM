import uuid

from sqlalchemy import select, update
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.currency import Currency
from app.schemas.currency import CurrencyCreate, CurrencyUpdate


async def list_currencies(db: AsyncSession, tenant_id: uuid.UUID) -> list[Currency]:
    result = await db.execute(
        select(Currency).where(Currency.tenant_id == tenant_id, Currency.is_deleted == False)
    )
    return result.scalars().all()


async def get_currency(db: AsyncSession, tenant_id: uuid.UUID, currency_id: uuid.UUID) -> Currency | None:
    result = await db.execute(
        select(Currency).where(
            Currency.id == currency_id, Currency.tenant_id == tenant_id, Currency.is_deleted == False
        )
    )
    return result.scalar_one_or_none()


async def create_currency(db: AsyncSession, tenant_id: uuid.UUID, user_id: uuid.UUID, data: CurrencyCreate) -> Currency:
    if data.is_base_currency:
        await db.execute(
            update(Currency)
            .where(Currency.tenant_id == tenant_id, Currency.is_base_currency == True)
            .values(is_base_currency=False)
        )

    currency = Currency(tenant_id=tenant_id, created_by=user_id, **data.model_dump())
    db.add(currency)
    await db.commit()
    await db.refresh(currency)
    return currency


async def update_currency(
    db: AsyncSession, tenant_id: uuid.UUID, user_id: uuid.UUID, currency_id: uuid.UUID, data: CurrencyUpdate
) -> Currency | None:
    currency = await get_currency(db, tenant_id, currency_id)
    if currency is None:
        return None

    update_data = data.model_dump(exclude_unset=True)

    if update_data.get("is_base_currency") is True:
        await db.execute(
            update(Currency)
            .where(Currency.tenant_id == tenant_id, Currency.is_base_currency == True)
            .values(is_base_currency=False)
        )

    for field, value in update_data.items():
        setattr(currency, field, value)
    currency.modified_by = user_id

    await db.commit()
    await db.refresh(currency)
    return currency


async def deactivate_currency(db: AsyncSession, tenant_id: uuid.UUID, user_id: uuid.UUID, currency_id: uuid.UUID) -> Currency | None:
    currency = await get_currency(db, tenant_id, currency_id)
    if currency is None:
        return None
    currency.is_deleted = True
    currency.status = "Inactive"
    currency.modified_by = user_id
    await db.commit()
    await db.refresh(currency)
    return currency