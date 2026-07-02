from fastapi import APIRouter, Depends, HTTPException

from app.api.dependencies import get_template_service
from app.models.portfolio import Template
from app.services.template_service import TemplateService

router = APIRouter()


@router.get("", response_model=list[Template])
def list_templates(service: TemplateService = Depends(get_template_service)) -> list[Template]:
    return service.list_templates()


@router.get("/{template_id}", response_model=Template)
def get_template(template_id: str, service: TemplateService = Depends(get_template_service)) -> Template:
    template = service.get_template(template_id)
    if template is None:
        raise HTTPException(status_code=404, detail="Template not found")
    return template
