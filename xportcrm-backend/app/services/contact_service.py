import uuid

from sqlalchemy import select, update
from sqlalchemy.ext.asyncio import AsyncSession
from fastapi import HTTPException

from app.models.contact import Contact
from app.schemas.contact import ContactCreate, ContactUpdate
from sqlalchemy import select, update, func

# async def list_contacts(db: AsyncSession, tenant_id: uuid.UUID) -> list[Contact]:
#     result = await db.execute(
#         select(Contact).where(Contact.tenant_id == tenant_id, Contact.is_deleted == False)
#     )
#     return result.scalars().all()

async def list_contacts(
    db: AsyncSession,
    tenant_id: uuid.UUID,
    search: str | None = None,
    account_id: uuid.UUID | None = None,
    role_type: str | None = None,
    is_primary_contact: bool | None = None,
    do_not_contact: bool | None = None,
    page: int = 1,
    page_size: int = 25,
) -> tuple[list[Contact], int]:
    query = select(Contact).where(Contact.tenant_id == tenant_id, Contact.is_deleted == False)

    if search:
        pattern = f"%{search}%"
        query = query.where(Contact.contact_name.ilike(pattern))
    if account_id:
        query = query.where(Contact.account_id == account_id)
    if role_type:
        query = query.where(Contact.role_type == role_type)
    if is_primary_contact is not None:
        query = query.where(Contact.is_primary_contact == is_primary_contact)
    if do_not_contact is not None:
        query = query.where(Contact.do_not_contact == do_not_contact)

    count_query = select(func.count()).select_from(query.subquery())
    total = (await db.execute(count_query)).scalar_one()

    query = query.order_by(Contact.created_at.desc()).offset((page - 1) * page_size).limit(page_size)
    result = await db.execute(query)
    items = result.scalars().all()

    return items, total

async def get_contact(db: AsyncSession, tenant_id: uuid.UUID, contact_id: uuid.UUID) -> Contact | None:
    result = await db.execute(
        select(Contact).where(
            Contact.id == contact_id, Contact.tenant_id == tenant_id, Contact.is_deleted == False
        )
    )
    return result.scalar_one_or_none()


async def _check_duplicate_email(
    db: AsyncSession, tenant_id: uuid.UUID, account_id: uuid.UUID, email: str, exclude_id: uuid.UUID | None = None
):
    query = select(Contact).where(
        Contact.tenant_id == tenant_id,
        Contact.account_id == account_id,
        Contact.email == email,
        Contact.is_deleted == False,
    )
    if exclude_id is not None:
        query = query.where(Contact.id != exclude_id)
    result = await db.execute(query)
    if result.scalar_one_or_none() is not None:
        raise HTTPException(status_code=400, detail="Email already exists for this Account")


async def create_contact(db: AsyncSession, tenant_id: uuid.UUID, user_id: uuid.UUID, data: ContactCreate) -> Contact:
    await _check_duplicate_email(db, tenant_id, data.account_id, data.email)

    if data.is_primary_contact:
        await db.execute(
            update(Contact)
            .where(Contact.tenant_id == tenant_id, Contact.account_id == data.account_id, Contact.is_primary_contact == True)
            .values(is_primary_contact=False)
        )

    contact = Contact(tenant_id=tenant_id, created_by=user_id, **data.model_dump())
    db.add(contact)
    await db.commit()
    await db.refresh(contact)
    return contact


async def update_contact(
    db: AsyncSession, tenant_id: uuid.UUID, user_id: uuid.UUID, contact_id: uuid.UUID, data: ContactUpdate
) -> Contact | None:
    contact = await get_contact(db, tenant_id, contact_id)
    if contact is None:
        return None

    update_data = data.model_dump(exclude_unset=True)

    if "email" in update_data:
        await _check_duplicate_email(db, tenant_id, contact.account_id, update_data["email"], exclude_id=contact_id)

    if update_data.get("is_primary_contact") is True:
        await db.execute(
            update(Contact)
            .where(Contact.tenant_id == tenant_id, Contact.account_id == contact.account_id, Contact.is_primary_contact == True)
            .values(is_primary_contact=False)
        )

    for field, value in update_data.items():
        setattr(contact, field, value)
    contact.modified_by = user_id

    await db.commit()
    await db.refresh(contact)
    return contact


async def delete_contact(db: AsyncSession, tenant_id: uuid.UUID, user_id: uuid.UUID, contact_id: uuid.UUID) -> Contact | None:
    contact = await get_contact(db, tenant_id, contact_id)
    if contact is None:
        return None
    contact.is_deleted = True
    contact.modified_by = user_id
    await db.commit()
    await db.refresh(contact)
    return contact