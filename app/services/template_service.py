from app.models.portfolio import Template
from app.repositories.store import Store, get_store
from app.services.seed_data import default_templates


class TemplateService:
    collection = "templates"

    def __init__(self, store: Store | None = None) -> None:
        self.store = store or get_store()
        self.ensure_seeded()

    def ensure_seeded(self) -> None:
        if self.store.list(self.collection):
            return
        for template in default_templates():
            self.store.set(self.collection, template.id, template.model_dump(mode="json"))

    def list_templates(self) -> list[Template]:
        return [Template(**item) for item in self.store.list(self.collection)]

    def get_template(self, template_id: str) -> Template | None:
        data = self.store.get(self.collection, template_id)
        return Template(**data) if data else None
