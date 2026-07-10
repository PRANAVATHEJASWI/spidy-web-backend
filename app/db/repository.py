"""
Data access for resume + blog content.

Behavior change from the original database.py:
  - In production (ENVIRONMENT != "local"), Firebase is required. If it's
    unreachable or misconfigured, calls raise a 500 instead of silently
    writing to the ephemeral local filesystem and losing data on next
    deploy.
  - The local JSON file fallback still exists, but only runs when
    ENVIRONMENT=local, for offline dev without a Firebase project.
  - Seed content is loaded lazily from app/data/seed.json, only when
    Firestore/local storage has no data yet (first-run bootstrap). Once
    real data exists, seed.json is never read again and can be deleted.
"""
import json
import logging
from pathlib import Path
from typing import Any

from app.core.config import settings
from app.db.firebase import FirebaseInitError, get_firestore_client

logger = logging.getLogger(__name__)

APP_DIR = Path(__file__).resolve().parent.parent
SEED_FILE = APP_DIR / "data" / "seed.json"
LOCAL_DATA_DIR = APP_DIR / "data" / "local"
RESUME_FILE = LOCAL_DATA_DIR / "resume.json"
BLOGS_FILE = LOCAL_DATA_DIR / "blogs.json"


class DataAccessError(RuntimeError):
    pass


def _load_seed() -> dict[str, Any]:
    """Loads seed.json lazily, only when actually needed (first-run
    bootstrap of an empty Firestore, or local fallback with no local files
    yet). Safe to delete seed.json once Firestore already holds real data —
    this will simply never be called again."""
    if not SEED_FILE.exists():
        raise DataAccessError(
            "No data found in Firestore/local storage and app/data/seed.json "
            "does not exist to bootstrap from. If Firestore already has your "
            "resume/blogs, this shouldn't happen — check your Firebase project "
            "and collection names ('resume', 'blogs')."
        )
    return json.loads(SEED_FILE.read_text(encoding="utf-8"))


def _default_resume() -> dict[str, Any]:
    return _load_seed()["resume"]


def _default_blogs() -> list[dict[str, Any]]:
    return _load_seed()["blogs"]


def _local_mode() -> bool:
    return settings.ENVIRONMENT == "local"


def _ensure_local_files() -> None:
    LOCAL_DATA_DIR.mkdir(parents=True, exist_ok=True)
    if not RESUME_FILE.exists():
        RESUME_FILE.write_text(json.dumps(_default_resume(), indent=2), encoding="utf-8")
    if not BLOGS_FILE.exists():
        BLOGS_FILE.write_text(json.dumps(_default_blogs(), indent=2), encoding="utf-8")


def _require_db():
    try:
        return get_firestore_client()
    except FirebaseInitError as e:
        if _local_mode():
            return None
        # Production with no working Firebase: fail loudly, don't fall
        # back to a filesystem that gets wiped on the next deploy.
        raise DataAccessError(str(e)) from e


# --- RESUME ---

def get_resume() -> dict[str, Any]:
    db = _require_db()
    if db is not None:
        doc_ref = db.collection("resume").document("default")
        doc = doc_ref.get()
        if doc.exists:
            return doc.to_dict()
        default_resume = _default_resume()
        doc_ref.set(default_resume)
        return default_resume

    _ensure_local_files()
    return json.loads(RESUME_FILE.read_text(encoding="utf-8"))


def save_resume(data: dict[str, Any]) -> None:
    db = _require_db()
    if db is not None:
        db.collection("resume").document("default").set(data)
        return

    _ensure_local_files()
    RESUME_FILE.write_text(json.dumps(data, indent=2), encoding="utf-8")


# --- BLOGS ---

def get_blogs() -> list[dict[str, Any]]:
    db = _require_db()
    if db is not None:
        docs = db.collection("blogs").stream()
        blogs = []
        for doc in docs:
            b = doc.to_dict()
            b["id"] = doc.id
            blogs.append(b)

        if not blogs:
            for b in _default_blogs():
                b_copy = {k: v for k, v in b.items() if k != "id"}
                db.collection("blogs").document(b["id"]).set(b_copy)
                b_copy["id"] = b["id"]
                blogs.append(b_copy)

        return sorted(blogs, key=lambda x: x.get("date", ""), reverse=True)

    _ensure_local_files()
    blogs = json.loads(BLOGS_FILE.read_text(encoding="utf-8"))
    return sorted(blogs, key=lambda x: x.get("date", ""), reverse=True)


def get_blog(blog_id: str) -> dict[str, Any] | None:
    db = _require_db()
    if db is not None:
        doc = db.collection("blogs").document(blog_id).get()
        if doc.exists:
            b = doc.to_dict()
            b["id"] = doc.id
            return b
        return None

    for b in get_blogs():
        if b.get("id") == blog_id:
            return b
    return None


def save_blog(blog_id: str, data: dict[str, Any]) -> None:
    data_to_save = {k: v for k, v in data.items() if k != "id"}

    db = _require_db()
    if db is not None:
        db.collection("blogs").document(blog_id).set(data_to_save)
        return

    blogs = get_blogs()
    updated = []
    found = False
    for b in blogs:
        if b.get("id") == blog_id:
            merged = {**b, **data, "id": blog_id}
            updated.append(merged)
            found = True
        else:
            updated.append(b)
    if not found:
        new_blog = {**data, "id": blog_id}
        updated.append(new_blog)

    BLOGS_FILE.write_text(json.dumps(updated, indent=2), encoding="utf-8")


def delete_blog(blog_id: str) -> None:
    db = _require_db()
    if db is not None:
        db.collection("blogs").document(blog_id).delete()
        return

    blogs = [b for b in get_blogs() if b.get("id") != blog_id]
    BLOGS_FILE.write_text(json.dumps(blogs, indent=2), encoding="utf-8")


def is_firebase_configured() -> bool:
    try:
        get_firestore_client()
        return True
    except FirebaseInitError:
        return False