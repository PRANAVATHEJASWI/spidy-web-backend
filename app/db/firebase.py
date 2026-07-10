"""
Firebase initialization, isolated from repository/query logic.

Only the FIREBASE_CREDENTIALS_JSON env var is supported — paste the full
service account JSON as a Render env var value. There is deliberately no
"local file path" credential option: that pattern invites someone to
commit a credentials file, or to depend on a path that won't exist on
Render's ephemeral filesystem.

If credentials are missing or invalid, initialization raises instead of
silently leaving db=None. Whether that's fatal is decided by the caller
(see app/db/repository.py) based on ENVIRONMENT — in production, no
Firebase means the app should not serve traffic pretending to persist data.
"""
import json
import logging

import firebase_admin
from firebase_admin import credentials, firestore

from app.core.config import settings

logger = logging.getLogger(__name__)

_db = None


class FirebaseInitError(RuntimeError):
    pass


def get_firestore_client():
    """Returns a cached Firestore client, initializing on first call.
    Raises FirebaseInitError if credentials are missing/invalid."""
    global _db
    if _db is not None:
        return _db

    if not settings.FIREBASE_CREDENTIALS_JSON:
        raise FirebaseInitError(
            "FIREBASE_CREDENTIALS_JSON is not set. "
            "Paste the full service account JSON into this env var on Render."
        )

    try:
        cred_dict = json.loads(settings.FIREBASE_CREDENTIALS_JSON)
    except json.JSONDecodeError as e:
        raise FirebaseInitError(f"FIREBASE_CREDENTIALS_JSON is not valid JSON: {e}") from e

    try:
        cred = credentials.Certificate(cred_dict)
        if not firebase_admin._apps:
            firebase_admin.initialize_app(cred)
        _db = firestore.client()
        logger.info("Firebase Firestore client initialized.")
        return _db
    except Exception as e:
        raise FirebaseInitError(f"Failed to initialize Firebase: {e}") from e
