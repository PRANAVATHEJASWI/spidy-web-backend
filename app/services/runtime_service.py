from __future__ import annotations

from datetime import datetime
from uuid import uuid4

from app.models.portfolio import Runtime, RuntimeCreate, RuntimeUpdate
from app.repositories.store import Store, get_store
from app.services.template_service import TemplateService


class RuntimeService:
    collection = "runtimes"

    def __init__(self, store: Store | None = None) -> None:
        self.store = store or get_store()
        self.template_service = TemplateService(self.store)

    def create_runtime(self, payload: RuntimeCreate) -> Runtime:
        template = self.template_service.get_template(payload.template_id)
        if template is None:
            raise ValueError("Template not found")

        runtime_id = str(uuid4())
        document = payload.document or template.document
        runtime = Runtime(
            id=runtime_id,
            user_id=payload.user_id,
            template_id=payload.template_id,
            slug=runtime_id,
            document=document,
        )
        self.store.set(self.collection, runtime.id, runtime.model_dump(mode="json"))
        return runtime

    def update_runtime(self, runtime_id: str, payload: RuntimeUpdate) -> Runtime | None:
        existing = self.get_runtime(runtime_id)
        if existing is None:
            return None
        updated = existing.model_copy(
            update={
                "document": payload.document,
                "published": payload.published,
                "updated_at": datetime.utcnow(),
            }
        )
        self.store.set(self.collection, runtime_id, updated.model_dump(mode="json"))
        return updated

    def get_runtime(self, runtime_id: str) -> Runtime | None:
        data = self.store.get(self.collection, runtime_id)
        return Runtime(**data) if data else None

    def list_user_runtimes(self, user_id: str) -> list[Runtime]:
        return [
            Runtime(**item)
            for item in self.store.list(self.collection)
            if item.get("user_id") == user_id
        ]

    def list_all(self) -> list[Runtime]:
        return [Runtime(**item) for item in self.store.list(self.collection)]

    def delete_runtime(self, runtime_id: str) -> None:
        self.store.delete(self.collection, runtime_id)
