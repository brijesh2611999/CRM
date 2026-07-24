import uuid

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from fastapi import UploadFile, HTTPException

from app.models.document import Document
from app.services import blob_storage_service


async def upload_document(
    db: AsyncSession,
    tenant_id: uuid.UUID,
    user_id: uuid.UUID,
    related_to: str,
    related_record_id: uuid.UUID,
    document_type: str | None,
    file: UploadFile,
) -> Document:
    blob_name, file_size = await blob_storage_service.upload_file(tenant_id, related_to, file)

    document = Document(
        tenant_id=tenant_id,
        related_to=related_to,
        related_record_id=related_record_id,
        document_type=document_type,
        original_filename=file.filename,
        blob_name=blob_name,
        content_type=file.content_type,
        file_size_bytes=file_size,
        uploaded_by=user_id,
    )
    db.add(document)
    await db.commit()
    await db.refresh(document)
    return document


async def list_documents_for_record(
    db: AsyncSession, tenant_id: uuid.UUID, related_to: str, related_record_id: uuid.UUID
) -> list[Document]:
    result = await db.execute(
        select(Document).where(
            Document.tenant_id == tenant_id,
            Document.related_to == related_to,
            Document.related_record_id == related_record_id,
        ).order_by(Document.created_at.desc())
    )
    return result.scalars().all()


async def get_document(db: AsyncSession, tenant_id: uuid.UUID, document_id: uuid.UUID) -> Document | None:
    result = await db.execute(
        select(Document).where(Document.id == document_id, Document.tenant_id == tenant_id)
    )
    return result.scalar_one_or_none()


async def get_download_url(db: AsyncSession, tenant_id: uuid.UUID, document_id: uuid.UUID) -> tuple[str, str] | None:
    document = await get_document(db, tenant_id, document_id)
    if document is None:
        return None
    url = blob_storage_service.get_download_url(document.blob_name)
    return url, document.original_filename


async def delete_document(db: AsyncSession, tenant_id: uuid.UUID, document_id: uuid.UUID) -> bool:
    document = await get_document(db, tenant_id, document_id)
    if document is None:
        return False
    blob_storage_service.delete_file(document.blob_name)
    await db.delete(document)
    await db.commit()
    return True