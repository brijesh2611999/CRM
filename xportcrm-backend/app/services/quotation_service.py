import uuid

from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession
from fastapi import HTTPException

from app.models.quotation import Quotation
from app.models.quotation_charge_line import QuotationChargeLine
from app.models.opportunity import Opportunity
from app.schemas.quotation import QuotationCreate, QuotationUpdate, ChargeLineCreate, ChargeLineUpdate


async def _generate_quote_number(db: AsyncSession, tenant_id: uuid.UUID) -> str:
    result = await db.execute(
        select(func.count()).select_from(Quotation).where(Quotation.tenant_id == tenant_id)
    )
    count = result.scalar_one()
    return f"QT-{count + 1:06d}"


async def list_quotations(db: AsyncSession, tenant_id: uuid.UUID) -> list[Quotation]:
    result = await db.execute(
        select(Quotation).where(Quotation.tenant_id == tenant_id, Quotation.is_deleted == False)
    )
    return result.scalars().all()


async def get_quotation(db: AsyncSession, tenant_id: uuid.UUID, quotation_id: uuid.UUID) -> Quotation | None:
    result = await db.execute(
        select(Quotation).where(
            Quotation.id == quotation_id, Quotation.tenant_id == tenant_id, Quotation.is_deleted == False
        )
    )
    return result.scalar_one_or_none()


async def create_quotation(db: AsyncSession, tenant_id: uuid.UUID, user_id: uuid.UUID, data: QuotationCreate) -> Quotation:
    quote_number = await _generate_quote_number(db, tenant_id)

    quotation = Quotation(
        tenant_id=tenant_id,
        created_by=user_id,
        quote_number=quote_number,
        revision_number=1,
        status="Draft",
        **data.model_dump(),
    )
    db.add(quotation)
    await db.flush()

    opp_result = await db.execute(
        select(Opportunity).where(Opportunity.id == data.opportunity_id, Opportunity.tenant_id == tenant_id)
    )
    opportunity = opp_result.scalar_one_or_none()
    if opportunity:
        opportunity.quote_count = (opportunity.quote_count or 0) + 1

    await db.commit()
    await db.refresh(quotation)
    return quotation


async def update_quotation(
    db: AsyncSession, tenant_id: uuid.UUID, user_id: uuid.UUID, quotation_id: uuid.UUID, data: QuotationUpdate
) -> Quotation | None:
    quotation = await get_quotation(db, tenant_id, quotation_id)
    if quotation is None:
        return None
    for field, value in data.model_dump(exclude_unset=True).items():
        setattr(quotation, field, value)
    quotation.modified_by = user_id
    await db.commit()
    await db.refresh(quotation)
    return quotation


async def delete_quotation(db: AsyncSession, tenant_id: uuid.UUID, user_id: uuid.UUID, quotation_id: uuid.UUID) -> Quotation | None:
    quotation = await get_quotation(db, tenant_id, quotation_id)
    if quotation is None:
        return None
    quotation.is_deleted = True
    quotation.modified_by = user_id
    await db.commit()
    await db.refresh(quotation)
    return quotation


async def create_revision(db: AsyncSession, tenant_id: uuid.UUID, user_id: uuid.UUID, quotation_id: uuid.UUID) -> Quotation | None:
    original = await get_quotation(db, tenant_id, quotation_id)
    if original is None:
        return None

    new_quote_number = await _generate_quote_number(db, tenant_id)

    revision = Quotation(
        tenant_id=tenant_id,
        created_by=user_id,
        quote_number=new_quote_number,
        revision_number=original.revision_number + 1,
        previous_quote_id=original.id,
        opportunity_id=original.opportunity_id,
        account_id=original.account_id,
        service_type=original.service_type,
        origin=original.origin,
        destination=original.destination,
        commodity=original.commodity,
        hs_code=original.hs_code,
        weight=original.weight,
        volume=original.volume,
        container_type_id=original.container_type_id,
        incoterm_id=original.incoterm_id,
        currency_id=original.currency_id,
        valid_until=original.valid_until,
        status="Draft",
        payment_terms=original.payment_terms,
        terms_and_conditions=original.terms_and_conditions,
        notes=original.notes,
    )
    db.add(revision)
    await db.commit()
    await db.refresh(revision)
    return revision


async def _recalculate_quote_summary(db: AsyncSession, tenant_id: uuid.UUID, quotation_id: uuid.UUID):
    result = await db.execute(
        select(QuotationChargeLine).where(QuotationChargeLine.quotation_id == quotation_id)
    )
    lines = result.scalars().all()

    total_buy = float(sum(float(line.buy_amount) for line in lines))
    total_sell = float(sum(float(line.sell_amount) for line in lines))
    margin = total_sell - total_buy
    margin_pct = (margin / total_sell * 100) if total_sell else 0

    quotation = await get_quotation(db, tenant_id, quotation_id)
    if quotation:
        quotation.total_buy_amount = total_buy
        quotation.total_sell_amount = total_sell
        quotation.margin_amount = margin
        quotation.margin_pct = round(margin_pct, 2)
        quotation.grand_total = total_sell + float(quotation.taxes)


async def list_charge_lines(db: AsyncSession, tenant_id: uuid.UUID, quotation_id: uuid.UUID) -> list[QuotationChargeLine]:
    result = await db.execute(
        select(QuotationChargeLine).where(
            QuotationChargeLine.quotation_id == quotation_id, QuotationChargeLine.tenant_id == tenant_id
        ).order_by(QuotationChargeLine.sort_order)
    )
    return result.scalars().all()


async def add_charge_line(
    db: AsyncSession, tenant_id: uuid.UUID, user_id: uuid.UUID, quotation_id: uuid.UUID, data: ChargeLineCreate
) -> QuotationChargeLine:
    quotation = await get_quotation(db, tenant_id, quotation_id)
    if quotation is None:
        raise HTTPException(status_code=404, detail="Quotation not found")

    buy_amount = float(data.quantity) * float(data.buy_rate)
    sell_amount = float(data.quantity) * float(data.sell_rate)

    line = QuotationChargeLine(
        tenant_id=tenant_id,
        created_by=user_id,
        quotation_id=quotation_id,
        buy_amount=buy_amount,
        sell_amount=sell_amount,
        **data.model_dump(),
    )
    db.add(line)
    await db.flush()

    await _recalculate_quote_summary(db, tenant_id, quotation_id)
    await db.commit()
    await db.refresh(line)
    return line


async def update_charge_line(
    db: AsyncSession, tenant_id: uuid.UUID, user_id: uuid.UUID, quotation_id: uuid.UUID, line_id: uuid.UUID, data: ChargeLineUpdate
) -> QuotationChargeLine | None:
    result = await db.execute(
        select(QuotationChargeLine).where(
            QuotationChargeLine.id == line_id,
            QuotationChargeLine.quotation_id == quotation_id,
            QuotationChargeLine.tenant_id == tenant_id,
        )
    )
    line = result.scalar_one_or_none()
    if line is None:
        return None

    update_data = data.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(line, field, value)

    line.buy_amount = float(line.quantity) * float(line.buy_rate)
    line.sell_amount = float(line.quantity) * float(line.sell_rate)
    line.modified_by = user_id

    await db.flush()
    await _recalculate_quote_summary(db, tenant_id, quotation_id)
    await db.commit()
    await db.refresh(line)
    return line


async def delete_charge_line(db: AsyncSession, tenant_id: uuid.UUID, quotation_id: uuid.UUID, line_id: uuid.UUID) -> bool:
    result = await db.execute(
        select(QuotationChargeLine).where(
            QuotationChargeLine.id == line_id,
            QuotationChargeLine.quotation_id == quotation_id,
            QuotationChargeLine.tenant_id == tenant_id,
        )
    )
    line = result.scalar_one_or_none()
    if line is None:
        return False

    await db.delete(line)
    await db.flush()
    await _recalculate_quote_summary(db, tenant_id, quotation_id)
    await db.commit()
    return True