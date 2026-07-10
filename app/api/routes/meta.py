from fastapi import APIRouter, Header

from app.core.config import settings
from app.core.security import get_token_role
from app.db.repository import is_firebase_configured
from app.models.schemas import AuthVerifySchema, StatusSchema

router = APIRouter(prefix="/api", tags=["meta"])


@router.get("/status", response_model=StatusSchema)
def get_status():
    return StatusSchema(
        status="online",
        firebase_connected=is_firebase_configured(),
        auth_enabled=True,  # EDITOR_ACCESS_TOKEN is now a required setting
    )


@router.get("/auth/verify", response_model=AuthVerifySchema)
def verify_auth_token(authorization: str | None = Header(None)):
    role = get_token_role(authorization)
    return AuthVerifySchema(role=role.value)
