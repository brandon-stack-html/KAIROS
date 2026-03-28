"""Documents router — all routes require a valid JWT."""

from fastapi import APIRouter, Depends, File, Request, UploadFile, status
from fastapi.responses import FileResponse

from src.application.delete_document.command import DeleteDocumentCommand
from src.application.delete_document.handler import DeleteDocumentHandler
from src.application.download_document.command import DownloadDocumentCommand
from src.application.download_document.handler import DownloadDocumentHandler
from src.application.list_documents.command import ListDocumentsCommand
from src.application.list_documents.handler import ListDocumentsHandler
from src.application.upload_document.command import UploadDocumentCommand
from src.application.upload_document.handler import UploadDocumentHandler
from src.infrastructure.api.dependencies import get_current_user
from src.infrastructure.api.rate_limiter import limiter
from src.infrastructure.api.schemas.document_schemas import DocumentResponse
from src.infrastructure.config.container import (
    get_delete_document_handler,
    get_download_document_handler,
    get_list_documents_handler,
    get_upload_document_handler,
)

router = APIRouter(tags=["documents"])


def _document_response(doc) -> DocumentResponse:
    return DocumentResponse(
        id=doc.id.value,
        org_id=doc.org_id.value,
        project_id=doc.project_id.value if doc.project_id else None,
        uploaded_by=doc.uploaded_by.value,
        filename=doc.filename,
        file_type=doc.file_type,
        file_size_bytes=doc.file_size_bytes,
        storage_path=doc.storage_path,
        created_at=doc.created_at.isoformat(),
    )


@router.post(
    "/organizations/{org_id}/documents",
    response_model=DocumentResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Upload a document to an organization",
)
@limiter.limit("30/minute")
async def upload_org_document(
    org_id: str,
    request: Request,
    file: UploadFile = File(...),
    payload: dict = Depends(get_current_user),
    handler: UploadDocumentHandler = Depends(get_upload_document_handler),
) -> DocumentResponse:
    uploader_id: str = payload["sub"]
    content = await file.read()
    document = await handler.handle(
        UploadDocumentCommand(
            org_id=org_id,
            project_id=None,
            uploaded_by=uploader_id,
            filename=file.filename or "unknown",
            file_type=file.content_type or "application/octet-stream",
            file_content=content,
        )
    )
    return _document_response(document)


@router.get(
    "/organizations/{org_id}/documents",
    response_model=list[DocumentResponse],
    status_code=status.HTTP_200_OK,
    summary="List documents for an organization",
)
@limiter.limit("60/minute")
async def list_org_documents(
    org_id: str,
    request: Request,
    payload: dict = Depends(get_current_user),
    handler: ListDocumentsHandler = Depends(get_list_documents_handler),
) -> list[DocumentResponse]:
    documents = await handler.handle(ListDocumentsCommand(org_id=org_id))
    return [_document_response(d) for d in documents]


@router.post(
    "/projects/{project_id}/documents",
    response_model=DocumentResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Upload a document to a project",
)
@limiter.limit("30/minute")
async def upload_project_document(
    project_id: str,
    request: Request,
    file: UploadFile = File(...),
    payload: dict = Depends(get_current_user),
    handler: UploadDocumentHandler = Depends(get_upload_document_handler),
) -> DocumentResponse:
    from src.application.get_project.command import GetProjectCommand
    from src.application.get_project.handler import GetProjectHandler
    from src.infrastructure.config.container import get_get_project_handler

    uploader_id: str = payload["sub"]
    tenant_id: str = request.state.tenant_id
    project_handler: GetProjectHandler = get_get_project_handler()
    project = await project_handler.handle(
        GetProjectCommand(project_id=project_id, tenant_id=tenant_id)
    )

    content = await file.read()
    document = await handler.handle(
        UploadDocumentCommand(
            org_id=project.org_id.value,
            project_id=project_id,
            uploaded_by=uploader_id,
            filename=file.filename or "unknown",
            file_type=file.content_type or "application/octet-stream",
            file_content=content,
        )
    )
    return _document_response(document)


@router.get(
    "/projects/{project_id}/documents",
    response_model=list[DocumentResponse],
    status_code=status.HTTP_200_OK,
    summary="List documents for a project",
)
@limiter.limit("60/minute")
async def list_project_documents(
    project_id: str,
    request: Request,
    payload: dict = Depends(get_current_user),
    handler: ListDocumentsHandler = Depends(get_list_documents_handler),
) -> list[DocumentResponse]:
    documents = await handler.handle(ListDocumentsCommand(project_id=project_id))
    return [_document_response(d) for d in documents]


@router.delete(
    "/documents/{document_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Delete a document",
)
@limiter.limit("30/minute")
async def delete_document(
    document_id: str,
    request: Request,
    payload: dict = Depends(get_current_user),
    handler: DeleteDocumentHandler = Depends(get_delete_document_handler),
) -> None:
    requester_id: str = payload["sub"]
    tenant_id: str = request.state.tenant_id
    await handler.handle(
        DeleteDocumentCommand(
            document_id=document_id,
            requester_id=requester_id,
            tenant_id=tenant_id,
        )
    )


@router.get(
    "/documents/{document_id}/download",
    status_code=status.HTTP_200_OK,
    summary="Download a document file",
)
@limiter.limit("60/minute")
async def download_document(
    document_id: str,
    request: Request,
    payload: dict = Depends(get_current_user),
    handler: DownloadDocumentHandler = Depends(get_download_document_handler),
) -> FileResponse:
    document = await handler.handle(
        DownloadDocumentCommand(document_id=document_id)
    )
    return FileResponse(
        path=document.storage_path,
        filename=document.filename,
        media_type=document.file_type,
    )
