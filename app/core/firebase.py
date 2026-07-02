from __future__ import annotations

from functools import lru_cache

from app.core.config import settings


@lru_cache
def get_firestore_client():
    try:
        import firebase_admin
        from firebase_admin import credentials, firestore
    except ImportError:
        return None

    credential_path = settings.firebase_credentials_file
    if not credential_path.exists():
        return None

    raw = credential_path.read_text(encoding="utf-8")
    if "replace-with-your-project-id" in raw:
        return None

    if not firebase_admin._apps:
        cred = credentials.Certificate(str(credential_path))
        firebase_admin.initialize_app(cred)

    return firestore.client()
