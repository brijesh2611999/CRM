import uuid
from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, Form
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import get_current_tenant_id, get_current_user_id
from app.db.session import get_db
from app.schemas.document import DocumentRead, DocumentDownloadResponse
from app.services import document_service

router = APIRouter()


@router.post("/upload", response_model=DocumentRead, status_code=201)
async def upload_document(
    related_to: str = Form(...),
    related_record_id: uuid.UUID = Form(...),
    document_type: str | None = Form(None),
    file: UploadFile = File(...),
    tenant_id: uuid.UUID = Depends(get_current_tenant_id),
    user_id: uuid.UUID = Depends(get_current_user_id),
    db: AsyncSession = Depends(get_db),
):
    return await document_service.upload_document(
        db, tenant_id, user_id, related_to, related_record_id, document_type, file
    )


@router.get("/for/{related_to}/{related_record_id}", response_model=list[DocumentRead])
async def list_documents(
    related_to: str,
    related_record_id: uuid.UUID,
    tenant_id: uuid.UUID = Depends(get_current_tenant_id),
    db: AsyncSession = Depends(get_db),
):
    return await document_service.list_documents_for_record(db, tenant_id, related_to, related_record_id)


@router.get("/{document_id}/download", response_model=DocumentDownloadResponse)
async def download_document(
    document_id: uuid.UUID,
    tenant_id: uuid.UUID = Depends(get_current_tenant_id),
    db: AsyncSession = Depends(get_db),
):
    result = await document_service.get_download_url(db, tenant_id, document_id)
    if result is None:
        raise HTTPException(status_code=404, detail="Document not found")
    url, filename = result
    return DocumentDownloadResponse(download_url=url, filename=filename)


@router.delete("/{document_id}", status_code=204)
async def delete_document(
    document_id: uuid.UUID,
    tenant_id: uuid.UUID = Depends(get_current_tenant_id),
    db: AsyncSession = Depends(get_db),
):
    deleted = await document_service.delete_document(db, tenant_id, document_id)
    if not deleted:
        raise HTTPException(status_code=404, detail="Document not found")