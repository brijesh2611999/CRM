import uuid

from azure.storage.blob import BlobServiceClient
from fastapi import UploadFile

from app.core.config import settings


def _get_container_client():
    blob_service_client = BlobServiceClient.from_connection_string(settings.AZURE_STORAGE_CONNECTION_STRING)
    return blob_service_client.get_container_client(settings.AZURE_STORAGE_CONTAINER_NAME)


async def upload_file(tenant_id: uuid.UUID, related_to: str, file: UploadFile) -> tuple[str, int]:
    """Uploads a file to Azure Blob Storage under a tenant-scoped path
    (so tenants can never access each other's files even if a blob
    name were guessed). Returns (blob_name, file_size_bytes)."""
    container_client = _get_container_client()

    file_extension = file.filename.split(".")[-1] if "." in file.filename else ""
    unique_name = f"{uuid.uuid4()}.{file_extension}" if file_extension else str(uuid.uuid4())
    blob_name = f"{tenant_id}/{related_to.lower()}/{unique_name}"

    content = await file.read()
    file_size = len(content)

    blob_client = container_client.get_blob_client(blob_name)
    blob_client.upload_blob(content, overwrite=True)

    return blob_name, file_size


def get_download_url(blob_name: str) -> str:
    """Generates a time-limited download URL (SAS token) for a blob.
    Since the container is Private, direct URLs won't work without
    this - the SAS token grants temporary read access."""
    from azure.storage.blob import generate_blob_sas, BlobSasPermissions
    from datetime import datetime, timedelta, timezone

    blob_service_client = BlobServiceClient.from_connection_string(settings.AZURE_STORAGE_CONNECTION_STRING)
    account_name = blob_service_client.account_name
    account_key = blob_service_client.credential.account_key

    sas_token = generate_blob_sas(
        account_name=account_name,
        container_name=settings.AZURE_STORAGE_CONTAINER_NAME,
        blob_name=blob_name,
        account_key=account_key,
        permission=BlobSasPermissions(read=True),
        expiry=datetime.now(timezone.utc) + timedelta(hours=1),
    )

    return f"https://{account_name}.blob.core.windows.net/{settings.AZURE_STORAGE_CONTAINER_NAME}/{blob_name}?{sas_token}"


def delete_file(blob_name: str):
    container_client = _get_container_client()
    blob_client = container_client.get_blob_client(blob_name)
    blob_client.delete_blob()