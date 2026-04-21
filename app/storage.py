from __future__ import annotations

import json
import mimetypes
import re
import uuid
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path

from fastapi import HTTPException, status

from app.config import settings


_SAFE_FILENAME_RE = re.compile(r"[^A-Za-z0-9._ -]+")


@dataclass(frozen=True)
class StoredFile:
    file_id: str
    user_hash: str
    filename: str
    path: Path
    mime_type: str
    size_bytes: int
    created_at: datetime


def utc_now() -> datetime:
    return datetime.now(timezone.utc)


def sanitize_filename(filename: str, default: str) -> str:
    name = filename.strip() if filename else default
    name = name.replace("/", "_").replace("\\", "_")
    name = _SAFE_FILENAME_RE.sub("_", name)
    name = name.strip(" ._")

    if not name:
        name = default

    return name[:180]


class UserStorage:
    def __init__(self, data_dir: Path | None = None) -> None:
        self.data_dir = data_dir or settings.data_dir
        self.users_dir = self.data_dir / "users"
        self.tmp_dir = self.data_dir / "tmp"

        self.users_dir.mkdir(parents=True, exist_ok=True)
        self.tmp_dir.mkdir(parents=True, exist_ok=True)

    def _user_dir(self, user_hash: str) -> Path:
        path = self.users_dir / user_hash
        path.mkdir(parents=True, exist_ok=True)
        return path

    def _files_dir(self, user_hash: str) -> Path:
        path = self._user_dir(user_hash) / "files" / utc_now().strftime("%Y-%m-%d")
        path.mkdir(parents=True, exist_ok=True)
        return path

    def _registry_path(self, user_hash: str) -> Path:
        return self._user_dir(user_hash) / "registry.jsonl"

    def save_bytes(
        self,
        *,
        user_hash: str,
        filename: str,
        data: bytes,
        mime_type: str | None = None,
    ) -> StoredFile:
        max_size = settings.max_file_size_mb * 1024 * 1024
        if len(data) > max_size:
            raise HTTPException(
                status_code=status.HTTP_413_REQUEST_ENTITY_TOO_LARGE,
                detail=f"File exceeds MAX_FILE_SIZE_MB={settings.max_file_size_mb}",
            )

        file_id = uuid.uuid4().hex
        safe_name = sanitize_filename(filename, default=f"{file_id}.bin")

        guessed_mime = mime_type or mimetypes.guess_type(safe_name)[0] or "application/octet-stream"
        target_path = self._files_dir(user_hash) / f"{file_id}-{safe_name}"
        target_path.write_bytes(data)

        stored = StoredFile(
            file_id=file_id,
            user_hash=user_hash,
            filename=safe_name,
            path=target_path,
            mime_type=guessed_mime,
            size_bytes=len(data),
            created_at=utc_now(),
        )
        self._append_registry(stored)
        return stored

    def _append_registry(self, stored: StoredFile) -> None:
        record = {
            "file_id": stored.file_id,
            "user_hash": stored.user_hash,
            "filename": stored.filename,
            "path": str(stored.path),
            "mime_type": stored.mime_type,
            "size_bytes": stored.size_bytes,
            "created_at": stored.created_at.isoformat(),
        }

        registry = self._registry_path(stored.user_hash)
        with registry.open("a", encoding="utf-8") as fh:
            fh.write(json.dumps(record, ensure_ascii=False) + "\n")

    def list_files(self, user_hash: str, limit: int = 50) -> list[StoredFile]:
        registry = self._registry_path(user_hash)
        if not registry.exists():
            return []

        records: list[StoredFile] = []

        with registry.open("r", encoding="utf-8") as fh:
            for line in fh:
                if not line.strip():
                    continue

                raw = json.loads(line)
                path = Path(raw["path"])

                if not path.exists():
                    continue

                records.append(
                    StoredFile(
                        file_id=raw["file_id"],
                        user_hash=raw["user_hash"],
                        filename=raw["filename"],
                        path=path,
                        mime_type=raw["mime_type"],
                        size_bytes=int(raw["size_bytes"]),
                        created_at=datetime.fromisoformat(raw["created_at"]),
                    )
                )

        records.sort(key=lambda item: item.created_at, reverse=True)
        return records[:limit]

    def get_file(self, user_hash: str, file_id: str) -> StoredFile:
        for item in self.list_files(user_hash=user_hash, limit=10000):
            if item.file_id == file_id:
                return item

        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="File not found",
        )

    def delete_file(self, user_hash: str, file_id: str) -> bool:
        stored = self.get_file(user_hash=user_hash, file_id=file_id)

        try:
            stored.path.unlink(missing_ok=True)
        except OSError as exc:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Could not delete file: {exc}",
            ) from exc

        return True


storage = UserStorage()
