from app.services.runtime_service import RuntimeService
from app.services.template_service import TemplateService
from app.services.user_service import UserService


def get_template_service() -> TemplateService:
    return TemplateService()


def get_user_service() -> UserService:
    return UserService()


def get_runtime_service() -> RuntimeService:
    return RuntimeService()
