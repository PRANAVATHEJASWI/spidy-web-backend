from typing import Optional

from pydantic import BaseModel, Field


class ContactSchema(BaseModel):
    phone: str
    email: str
    linkedin: str
    github: str
    portfolio: str
    extraUrls: list[dict[str, str]] = []


class EducationItem(BaseModel):
    institution: str
    degree: str
    cgpa: str
    duration: str
    link: Optional[str] = ""


class ExperienceItem(BaseModel):
    role: str
    company: str
    location: str
    duration: str
    highlights: list[str]
    link: Optional[str] = ""


class ProjectItem(BaseModel):
    title: str
    techStack: str
    highlights: list[str]
    link: Optional[str] = ""


class SkillsSchema(BaseModel):
    languages: list[str]
    automationTesting: list[str]
    aiLlm: list[str]
    toolsTechnologies: list[str]


class PublicationItem(BaseModel):
    title: str
    journal: str
    volumeInfo: str
    url: str


class CustomSectionItemSchema(BaseModel):
    text: str
    link: Optional[str] = ""


class CustomSectionSchema(BaseModel):
    title: str
    type: str = "list"
    items: list[CustomSectionItemSchema]


class AskMrNoobSchema(BaseModel):
    enabled: bool
    label: str
    disabledMessage: str


class ResumeSchema(BaseModel):
    name: str
    title: str
    subTitle: str
    description: str = ""
    contact: ContactSchema
    education: list[EducationItem]
    experience: list[ExperienceItem]
    projects: list[ProjectItem]
    skills: SkillsSchema
    certificates: list[str]
    publications: list[PublicationItem]
    customSections: list[CustomSectionSchema] = []
    askMrNoob: AskMrNoobSchema = Field(
        default_factory=lambda: AskMrNoobSchema(
            enabled=False,
            label="Ask MrNoob",
            disabledMessage="AI assistant is under construction.",
        )
    )


class BlogCreateSchema(BaseModel):
    title: str
    excerpt: str
    content: str
    date: str


class BlogSchema(BlogCreateSchema):
    id: str


class StatusSchema(BaseModel):
    status: str
    firebase_connected: bool
    auth_enabled: bool


class AuthVerifySchema(BaseModel):
    role: str
