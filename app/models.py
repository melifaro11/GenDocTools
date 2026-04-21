from __future__ import annotations

from datetime import datetime
from typing import Literal

from pydantic import BaseModel, Field


class GenerateMarkdownRequest(BaseModel):
    title: str = Field(..., min_length=1, max_length=200)
    content: str = Field(..., min_length=1)
    filename: str | None = Field(default=None, max_length=180)


class GenerateDocxRequest(BaseModel):
    title: str = Field(..., min_length=1, max_length=200)
    content: str = Field(..., min_length=1)
    filename: str | None = Field(default=None, max_length=180)


class GenerateXlsxRequest(BaseModel):
    title: str = Field(..., min_length=1, max_length=200)
    rows: list[list[str | int | float | bool | None]] = Field(
        default_factory=list,
        description="Rows to write into the first worksheet.",
    )
    filename: str | None = Field(default=None, max_length=180)


class GeneratePptxRequest(BaseModel):
    title: str = Field(..., min_length=1, max_length=200)
    slides: list[str] = Field(
        default_factory=list,
        description="Each string becomes one simple slide.",
    )
    filename: str | None = Field(default=None, max_length=180)


class FileInfo(BaseModel):
    file_id: str
    filename: str
    mime_type: str
    size_bytes: int
    created_at: datetime
    expires_at: datetime | None = None
    owner: str
    download_url: str
    download_count: int = 0
    last_downloaded_at: datetime | None = None


class GenerateFileResponse(BaseModel):
    ok: bool = True
    file: FileInfo
    message: str


class FileListResponse(BaseModel):
    files: list[FileInfo]


class DeleteFileResponse(BaseModel):
    ok: bool
    file_id: str


class CleanupResponse(BaseModel):
    ok: bool = True
    deleted_files: int
    deleted_bytes: int


class HealthResponse(BaseModel):
    status: Literal["ok"] = "ok"
    service: str = "GenDocTools"
    mode: Literal["openapi"] = "openapi"
    version: str
