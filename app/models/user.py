from datetime import datetime

from pydantic import BaseModel, EmailStr, Field


class User(BaseModel):
    id: str
    display_name: str
    email: EmailStr
    photo_url: str | None = None
    created_at: datetime = Field(default_factory=datetime.utcnow)


class UserCreate(BaseModel):
    display_name: str
    email: EmailStr
    password: str = Field(min_length=6)
    photo_url: str | None = None


class UserLogin(BaseModel):
    email: EmailStr
    password: str


class StoredUser(User):
    password_hash: str
