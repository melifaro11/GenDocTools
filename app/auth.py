from __future__ import annotations

import hashlib
from dataclasses import dataclass

from fastapi import Header, HTTPException, status

from app.config import settings


@dataclass(frozen=True)
class UserContext:
    user_id: str
    user_hash: str
    source: str


def _hash_user_id(user_id: str) -> str:
    return hashlib.sha256(user_id.encode("utf-8")).hexdigest()[:32]


def _extract_bearer_token(authorization: str | None) -> str | None:
    if not authorization:
        return None

    prefix = "Bearer "
    if not authorization.startswith(prefix):
        return None

    token = authorization[len(prefix) :].strip()
    return token or None


async def get_user_context(
    authorization: str | None = Header(default=None, alias="Authorization"),
    x_openwebui_user_id: str | None = Header(default=None, alias="X-OpenWebUI-User-Id"),
    x_openwebui_user_email: str | None = Header(default=None, alias="X-OpenWebUI-User-Email"),
    x_user_id: str | None = Header(default=None, alias="X-User-Id"),
) -> UserContext:
    """
    Resolve the caller identity.

    Priority:
    1. Open WebUI user id header
    2. Open WebUI user email header
    3. Generic X-User-Id header
    4. API token fingerprint
    5. anonymous, only if allowed
    """

    token = _extract_bearer_token(authorization)

    if settings.enable_auth:
        if not token:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Missing Bearer token",
            )

        if settings.tool_api_keys and token not in settings.tool_api_keys:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Invalid API token",
            )

    if x_openwebui_user_id:
        user_id = x_openwebui_user_id.strip()
        return UserContext(user_id=user_id, user_hash=_hash_user_id(user_id), source="x-openwebui-user-id")

    if x_openwebui_user_email:
        user_id = x_openwebui_user_email.strip().lower()
        return UserContext(user_id=user_id, user_hash=_hash_user_id(user_id), source="x-openwebui-user-email")

    if x_user_id:
        user_id = x_user_id.strip()
        return UserContext(user_id=user_id, user_hash=_hash_user_id(user_id), source="x-user-id")

    if token:
        user_id = f"token:{hashlib.sha256(token.encode('utf-8')).hexdigest()[:16]}"
        return UserContext(user_id=user_id, user_hash=_hash_user_id(user_id), source="bearer-token")

    if settings.allow_anonymous:
        user_id = "anonymous"
        return UserContext(user_id=user_id, user_hash=_hash_user_id(user_id), source="anonymous")

    raise HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="User identity is required",
    )
