from __future__ import annotations

from fastapi import Depends, FastAPI, Query
from fastapi.responses import FileResponse

from app.auth import UserContext, get_user_context
from app.config import settings
from app.models import (
    CleanupResponse,
    DeleteFileResponse,
    FileInfo,
    FileListResponse,
    GenerateDocxRequest,
    GenerateFileResponse,
    GenerateMarkdownRequest,
    GeneratePptxRequest,
    GenerateXlsxRequest,
    HealthResponse,
)
from app.service import document_service
from app.storage import StoredFile, storage
from app.urls import build_download_url, create_download_token, verify_download_token


def _file_info(stored: StoredFile) -> FileInfo:
    token = create_download_token(file_id=stored.file_id, user_hash=stored.user_hash)

    return FileInfo(
        file_id=stored.file_id,
        filename=stored.filename,
        mime_type=stored.mime_type,
        size_bytes=stored.size_bytes,
        created_at=stored.created_at,
        expires_at=stored.expires_at,
        owner=stored.user_hash,
        download_url=build_download_url(token),
        download_count=stored.download_count,
        last_downloaded_at=stored.last_downloaded_at,
    )


def create_app() -> FastAPI:
    app = FastAPI(
        title="GenDocTools OpenAPI Tool Server",
        version=settings.app_version,
        description=(
            "OpenAI/OpenAPI-compatible document generation tool server for Open WebUI. "
            "This interface is added next to the existing MCP server."
        ),
    )

    @app.get("/health", response_model=HealthResponse, tags=["system"])
    async def health() -> HealthResponse:
        return HealthResponse(version=settings.app_version)

    @app.post(
        "/tools/generate_markdown",
        response_model=GenerateFileResponse,
        tags=["tools"],
        operation_id="generate_markdown",
        summary="Generate a Markdown file",
    )
    async def generate_markdown(
        request: GenerateMarkdownRequest,
        user: UserContext = Depends(get_user_context),
    ) -> GenerateFileResponse:
        generated = document_service.generate_markdown(
            title=request.title,
            content=request.content,
            filename=request.filename,
        )

        stored = storage.save_bytes(
            user_hash=user.user_hash,
            filename=generated.filename,
            data=generated.data,
            mime_type=generated.mime_type,
        )

        return GenerateFileResponse(
            file=_file_info(stored),
            message="Markdown file generated successfully.",
        )

    @app.post(
        "/tools/generate_docx",
        response_model=GenerateFileResponse,
        tags=["tools"],
        operation_id="generate_docx",
        summary="Generate a DOCX file",
    )
    async def generate_docx(
        request: GenerateDocxRequest,
        user: UserContext = Depends(get_user_context),
    ) -> GenerateFileResponse:
        generated = document_service.generate_docx(
            title=request.title,
            content=request.content,
            filename=request.filename,
        )

        stored = storage.save_bytes(
            user_hash=user.user_hash,
            filename=generated.filename,
            data=generated.data,
            mime_type=generated.mime_type,
        )

        return GenerateFileResponse(
            file=_file_info(stored),
            message="DOCX file generated successfully.",
        )

    @app.post(
        "/tools/generate_xlsx",
        response_model=GenerateFileResponse,
        tags=["tools"],
        operation_id="generate_xlsx",
        summary="Generate an XLSX file",
    )
    async def generate_xlsx(
        request: GenerateXlsxRequest,
        user: UserContext = Depends(get_user_context),
    ) -> GenerateFileResponse:
        generated = document_service.generate_xlsx(
            title=request.title,
            rows=request.rows,
            filename=request.filename,
        )

        stored = storage.save_bytes(
            user_hash=user.user_hash,
            filename=generated.filename,
            data=generated.data,
            mime_type=generated.mime_type,
        )

        return GenerateFileResponse(
            file=_file_info(stored),
            message="XLSX file generated successfully.",
        )

    @app.post(
        "/tools/generate_pptx",
        response_model=GenerateFileResponse,
        tags=["tools"],
        operation_id="generate_pptx",
        summary="Generate a PPTX file",
    )
    async def generate_pptx(
        request: GeneratePptxRequest,
        user: UserContext = Depends(get_user_context),
    ) -> GenerateFileResponse:
        generated = document_service.generate_pptx(
            title=request.title,
            slides=request.slides,
            filename=request.filename,
        )

        stored = storage.save_bytes(
            user_hash=user.user_hash,
            filename=generated.filename,
            data=generated.data,
            mime_type=generated.mime_type,
        )

        return GenerateFileResponse(
            file=_file_info(stored),
            message="PPTX file generated successfully.",
        )

    @app.get(
        "/files",
        response_model=FileListResponse,
        tags=["files"],
        operation_id="list_generated_files",
        summary="List generated files for the current user",
    )
    async def list_files(
        limit: int = Query(default=50, ge=1, le=200),
        user: UserContext = Depends(get_user_context),
    ) -> FileListResponse:
        files = storage.list_files(user_hash=user.user_hash, limit=limit)
        return FileListResponse(files=[_file_info(item) for item in files])

    @app.delete(
        "/files/{file_id}",
        response_model=DeleteFileResponse,
        tags=["files"],
        operation_id="delete_generated_file",
        summary="Delete one generated file for the current user",
    )
    async def delete_file(
        file_id: str,
        user: UserContext = Depends(get_user_context),
    ) -> DeleteFileResponse:
        storage.delete_file(user_hash=user.user_hash, file_id=file_id)
        return DeleteFileResponse(ok=True, file_id=file_id)

    @app.post(
        "/maintenance/cleanup",
        response_model=CleanupResponse,
        tags=["maintenance"],
        operation_id="cleanup_expired_files",
        summary="Delete expired generated files",
    )
    async def cleanup_expired_files(
        current_user_only: bool = Query(default=True),
        user: UserContext = Depends(get_user_context),
    ) -> CleanupResponse:
        result = storage.cleanup_expired(user_hash=user.user_hash if current_user_only else None)

        return CleanupResponse(
            deleted_files=result.deleted_files,
            deleted_bytes=result.deleted_bytes,
        )

    @app.get(
        "/download/{token}",
        tags=["files"],
        include_in_schema=False,
    )
    async def download_file(token: str) -> FileResponse:
        payload = verify_download_token(token)

        stored = storage.get_file(
            user_hash=payload["user_hash"],
            file_id=payload["file_id"],
        )

        storage.mark_downloaded(
            user_hash=payload["user_hash"],
            file_id=payload["file_id"],
        )

        return FileResponse(
            path=stored.path,
            filename=stored.filename,
            media_type=stored.mime_type,
        )

    return app
