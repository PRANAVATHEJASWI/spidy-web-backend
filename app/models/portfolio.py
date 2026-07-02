from __future__ import annotations

from datetime import datetime
from typing import Any, Literal

from pydantic import BaseModel, Field


SectionType = Literal[
    "hero",
    "cards",
    "skills",
    "timeline",
    "projects",
    "certificates",
    "publication",
    "contact",
    "custom",
]


class Theme(BaseModel):
    name: str = "Vibrant"
    primary: str = "#ef4444"
    secondary: str = "#2563eb"
    accent: str = "#f59e0b"
    background: str = "#fff7ed"
    surface: str = "#ffffff"
    text: str = "#111827"
    radius: int = 8
    font: str = "Inter"


class NavItem(BaseModel):
    label: str
    section_id: str
    visible: bool = True


class Section(BaseModel):
    id: str
    type: SectionType
    title: str
    subtitle: str | None = None
    visible: bool = True
    layout: str = "default"
    items: list[dict[str, Any]] = Field(default_factory=list)
    settings: dict[str, Any] = Field(default_factory=dict)


class PortfolioDocument(BaseModel):
    title: str
    owner_name: str
    role: str
    summary: str
    layout: str = "vibrant"
    contact: dict[str, str] = Field(default_factory=dict)
    theme: Theme = Field(default_factory=Theme)
    navbar: list[NavItem] = Field(default_factory=list)
    sections: list[Section] = Field(default_factory=list)


class Template(BaseModel):
    id: str
    name: str
    description: str
    category: str
    preview_tone: str
    document: PortfolioDocument


class Runtime(BaseModel):
    id: str
    user_id: str
    template_id: str
    slug: str
    document: PortfolioDocument
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)
    published: bool = True


class RuntimeCreate(BaseModel):
    user_id: str
    template_id: str
    document: PortfolioDocument | None = None


class RuntimeUpdate(BaseModel):
    document: PortfolioDocument
    published: bool = True
