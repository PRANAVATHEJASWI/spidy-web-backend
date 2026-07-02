from fastapi import APIRouter

from app.api import runtimes, templates, users

api_router = APIRouter()
api_router.include_router(templates.router, prefix="/templates", tags=["templates"])
api_router.include_router(users.router, prefix="/users", tags=["users"])
api_router.include_router(runtimes.router, prefix="/runtimes", tags=["runtimes"])
