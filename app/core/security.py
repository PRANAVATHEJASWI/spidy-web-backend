"""
Bearer-token auth for a single-admin portfolio backend.

Design choice: a plain admin token (not Google OAuth) is intentional here.
There is exactly one writer (you). OAuth adds redirect handling, token
exchange, refresh tokens, and a client secret to manage for no real benefit
at this scale. If that ever changes (multiple editors, need to revoke access
without redeploying), OAuth becomes worth it — not before.

Security properties preserved from the original code, tightened:
- Missing EDITOR_ACCESS_TOKEN is impossible: config.py makes it required,
  so the app won't even boot without it. No "no tokens configured -> open
  access" branch exists anymore.
- Token comparison uses secrets.compare_digest to avoid timing attacks.
"""
import secrets
from enum import Enum

from fastapi import Header, HTTPException, status

from app.core.config import settings


class Role(str, Enum):
    NONE = "none"
    READONLY = "readonly"
    EDITOR = "editor"


def _extract_bearer_token(authorization: str | None) -> str | None:
    if not authorization:
        return None
    parts = authorization.split()
    if len(parts) != 2 or parts[0].lower() != "bearer":
        return None
    return parts[1]


def get_token_role(authorization: str | None = Header(None)) -> Role:
    """Dependency: resolves the caller's role. Never raises on its own —
    use require_editor / require_reader below to enforce access."""
    token = _extract_bearer_token(authorization)
    if token is None:
        return Role.NONE

    if secrets.compare_digest(token, settings.EDITOR_ACCESS_TOKEN):
        return Role.EDITOR

    if settings.READONLY_ACCESS_TOKEN and secrets.compare_digest(
        token, settings.READONLY_ACCESS_TOKEN
    ):
        return Role.READONLY

    return Role.NONE


def require_editor(authorization: str | None = Header(None)) -> None:
    """Use as a route dependency to gate write endpoints."""
    resolved = get_token_role(authorization)
    if resolved != Role.EDITOR:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Editor access token required",
        )


def require_reader(authorization: str | None = Header(None)) -> None:
    """Use if you ever want to gate read endpoints too (currently unused —
    resume/blog GET routes are public)."""
    resolved = get_token_role(authorization)
    if resolved == Role.NONE:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Valid access token required",
        )
