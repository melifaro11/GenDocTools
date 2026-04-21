from __future__ import annotations

import os
from dataclasses import dataclass
from pathlib import Path


def _env_bool(name: str, default: bool) -> bool:
    value = os.getenv(name)
    if value is None:
        return default
    return value.strip().lower() in {"1", "true", "yes", "on"}


def _env_int(name: str, default: int) -> int:
    value = os.getenv(name)
    if value is None or not value.strip():
        return default
    return int(value)


def _env_list(name: str) -> list[str]:
    value = os.getenv(name, "")
    return [item.strip() for item in value.split(",") if item.strip()]


@dataclass(frozen=True)
class Settings:
    app_name: str = "GenDocTools"
    app_version: str = "0.1.0"

    host: str = os.getenv("HOST", "0.0.0.0")
    port: int = _env_int("PORT", 8017)

    data_dir: Path = Path(os.getenv("DATA_DIR", "/data")).resolve()
    public_base_url: str = os.getenv("PUBLIC_BASE_URL", "http://localhost:8017").rstrip("/")

    enable_auth: bool = _env_bool("ENABLE_AUTH", False)
    allow_anonymous: bool = _env_bool("ALLOW_ANONYMOUS", True)
    tool_api_keys: list[str] = None

    download_signing_secret: str = os.getenv(
        "DOWNLOAD_SIGNING_SECRET",
        "dev-only-change-me",
    )
    download_token_ttl_seconds: int = _env_int("DOWNLOAD_TOKEN_TTL_SECONDS", 86400)

    max_file_size_mb: int = _env_int("MAX_FILE_SIZE_MB", 100)
    retention_days: int = _env_int("RETENTION_DAYS", 30)

    def __post_init__(self) -> None:
        object.__setattr__(self, "tool_api_keys", _env_list("TOOL_API_KEYS"))

settings = Settings()
