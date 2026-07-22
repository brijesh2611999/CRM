import uuid
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import get_current_tenant_id, get_current_user_id
from app.db.session import get_db
from app.schemas.currency import CurrencyCreate, CurrencyUpdate, CurrencyRead
from app.services import currency_service

router = APIRouter()


@router.get("/", response_model=list[CurrencyRead])
async def list_currencies(
    tenant_id: uuid.UUID = Depends(get_current_tenant_id),
    db: AsyncSession = Depends(get_db),
):
    return await currency_service.list_currencies(db, tenant_id)


@router.post("/", response_model=CurrencyRead, status_code=201)
async def create_currency(
    data: CurrencyCreate,
    tenant_id: uuid.UUID = Depends(get_current_tenant_id),
    user_id: uuid.UUID = Depends(get_current_user_id),
    db: AsyncSession = Depends(get_db),
):
    return await currency_service.create_currency(db, tenant_id, user_id, data)


@router.get("/{currency_id}", response_model=CurrencyRead)
async def get_currency(
    currency_id: uuid.UUID,
    tenant_id: uuid.UUID = Depends(get_current_tenant_id),
    db: AsyncSession = Depends(get_db),
):
    currency = await currency_service.get_currency(db, tenant_id, currency_id)
    if currency is None:
        raise HTTPException(status_code=404, detail="Currency not found")
    return currency


@router.put("/{currency_id}", response_model=CurrencyRead)
async def update_currency(
    currency_id: uuid.UUID,
    data: CurrencyUpdate,
    tenant_id: uuid.UUID = Depends(get_current_tenant_id),
    user_id: uuid.UUID = Depends(get_current_user_id),
    db: AsyncSession = Depends(get_db),
):
    currency = await currency_service.update_currency(db, tenant_id, user_id, currency_id, data)
    if currency is None:
        raise HTTPException(status_code=404, detail="Currency not found")
    return currency


@router.delete("/{currency_id}", response_model=CurrencyRead)
async def deactivate_currency(
    currency_id: uuid.UUID,
    tenant_id: uuid.UUID = Depends(get_current_tenant_id),
    user_id: uuid.UUID = Depends(get_current_user_id),
    db: AsyncSession = Depends(get_db),
):
    currency = await currency_service.deactivate_currency(db, tenant_id, user_id, currency_id)
    if currency is None:
        raise HTTPException(status_code=404, detail="Currency not found")
    return currency