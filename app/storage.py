from __future__ import annotations

import json
import mimetypes
import os
import re
import tempfile
import uuid
from dataclasses import dataclass
from datetime import datetime, timedelta, timezone
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
    expires_at: datetime | None = None
    download_count: int = 0
    last_downloaded_at: datetime | None = None


@dataclass(frozen=True)
class CleanupResult:
    deleted_files: int
    deleted_bytes: int


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


def _parse_dt(value: str | None) -> datetime | None:
    if not value:
        return None
    return datetime.fromisoformat(value)


def _serialize_dt(value: datetime | None) -> str | None:
    if value is None:
        return None
    return value.isoformat()


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
        ttl_days: int | None = None,
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

        retention_days = ttl_days if ttl_days is not None else settings.retention_days
        expires_at = utc_now() + timedelta(days=retention_days) if retention_days > 0 else None

        stored = StoredFile(
            file_id=file_id,
            user_hash=user_hash,
            filename=safe_name,
            path=target_path,
            mime_type=guessed_mime,
            size_bytes=len(data),
            created_at=utc_now(),
            expires_at=expires_at,
            download_count=0,
            last_downloaded_at=None,
        )

        records = self._read_registry(user_hash)
        records.append(stored)
        self._write_registry(user_hash, records)

        return stored

    def list_files(self, user_hash: str, limit: int = 50, include_expired: bool = False) -> list[StoredFile]:
        records = self._read_registry(user_hash)
        now = utc_now()

        visible: list[StoredFile] = []

        for item in records:
            if not item.path.exists():
                continue

            if not include_expired and item.expires_at is not None and item.expires_at < now:
                continue

            visible.append(item)

        visible.sort(key=lambda item: item.created_at, reverse=True)
        return visible[:limit]

    def get_file(self, user_hash: str, file_id: str, allow_expired: bool = False) -> StoredFile:
        now = utc_now()

        for item in self._read_registry(user_hash):
            if item.file_id != file_id:
                continue

            if not item.path.exists():
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail="File content is missing",
                )

            if not allow_expired and item.expires_at is not None and item.expires_at < now:
                raise HTTPException(
                    status_code=status.HTTP_410_GONE,
                    detail="File expired",
                )

            return item

        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="File not found",
        )

    def mark_downloaded(self, user_hash: str, file_id: str) -> StoredFile:
        records = self._read_registry(user_hash)
        updated: list[StoredFile] = []
        found: StoredFile | None = None

        for item in records:
            if item.file_id == file_id:
                found = StoredFile(
                    file_id=item.file_id,
                    user_hash=item.user_hash,
                    filename=item.filename,
                    path=item.path,
                    mime_type=item.mime_type,
                    size_bytes=item.size_bytes,
                    created_at=item.created_at,
                    expires_at=item.expires_at,
                    download_count=item.download_count + 1,
                    last_downloaded_at=utc_now(),
                )
                updated.append(found)
            else:
                updated.append(item)

        if found is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="File not found",
            )

        self._write_registry(user_hash, updated)
        return found

    def delete_file(self, user_hash: str, file_id: str) -> bool:
        records = self._read_registry(user_hash)
        kept: list[StoredFile] = []
        deleted = False

        for item in records:
            if item.file_id == file_id:
                deleted = True
                try:
                    item.path.unlink(missing_ok=True)
                except OSError as exc:
                    raise HTTPException(
                        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                        detail=f"Could not delete file: {exc}",
                    ) from exc
            else:
                kept.append(item)

        if not deleted:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="File not found",
            )

        self._write_registry(user_hash, kept)
        return True

    def cleanup_expired(self, user_hash: str | None = None) -> CleanupResult:
        users = [user_hash] if user_hash else self._list_user_hashes()

        deleted_files = 0
        deleted_bytes = 0
        now = utc_now()

        for current_user_hash in users:
            records = self._read_registry(current_user_hash)
            kept: list[StoredFile] = []

            for item in records:
                should_delete = False

                if not item.path.exists():
                    should_delete = True
                elif item.expires_at is not None and item.expires_at < now:
                    should_delete = True

                if should_delete:
                    if item.path.exists():
                        try:
                            deleted_bytes += item.path.stat().st_size
                            item.path.unlink(missing_ok=True)
                        except OSError:
                            kept.append(item)
                            continue
                    deleted_files += 1
                else:
                    kept.append(item)

            self._write_registry(current_user_hash, kept)

        return CleanupResult(deleted_files=deleted_files, deleted_bytes=deleted_bytes)

    def _list_user_hashes(self) -> list[str]:
        if not self.users_dir.exists():
            return []

        return [
            item.name
            for item in self.users_dir.iterdir()
            if item.is_dir()
        ]

    def _read_registry(self, user_hash: str) -> list[StoredFile]:
        registry = self._registry_path(user_hash)
        if not registry.exists():
            return []

        records: list[StoredFile] = []

        with registry.open("r", encoding="utf-8") as fh:
            for line in fh:
                if not line.strip():
                    continue

                try:
                    raw = json.loads(line)
                except json.JSONDecodeError:
                    continue

                try:
                    records.append(self._record_to_stored_file(raw))
                except Exception:
                    continue

        return records

    def _write_registry(self, user_hash: str, records: list[StoredFile]) -> None:
        registry = self._registry_path(user_hash)
        registry.parent.mkdir(parents=True, exist_ok=True)

        fd, tmp_name = tempfile.mkstemp(
            prefix="registry.",
            suffix=".jsonl.tmp",
            dir=str(registry.parent),
            text=True,
        )

        try:
            with os.fdopen(fd, "w", encoding="utf-8") as fh:
                for item in records:
                    fh.write(json.dumps(self._stored_file_to_record(item), ensure_ascii=False) + "\n")

            os.replace(tmp_name, registry)
        finally:
            tmp_path = Path(tmp_name)
            if tmp_path.exists():
                tmp_path.unlink(missing_ok=True)

    def _stored_file_to_record(self, stored: StoredFile) -> dict:
        return {
            "file_id": stored.file_id,
            "user_hash": stored.user_hash,
            "filename": stored.filename,
            "path": str(stored.path),
            "mime_type": stored.mime_type,
            "size_bytes": stored.size_bytes,
            "created_at": _serialize_dt(stored.created_at),
            "expires_at": _serialize_dt(stored.expires_at),
            "download_count": stored.download_count,
            "last_downloaded_at": _serialize_dt(stored.last_downloaded_at),
        }

    def _record_to_stored_file(self, raw: dict) -> StoredFile:
        return StoredFile(
            file_id=raw["file_id"],
            user_hash=raw["user_hash"],
            filename=raw["filename"],
            path=Path(raw["path"]),
            mime_type=raw["mime_type"],
            size_bytes=int(raw["size_bytes"]),
            created_at=_parse_dt(raw.get("created_at")) or utc_now(),
            expires_at=_parse_dt(raw.get("expires_at")),
            download_count=int(raw.get("download_count", 0)),
            last_downloaded_at=_parse_dt(raw.get("last_downloaded_at")),
        )


storage = UserStorage()
