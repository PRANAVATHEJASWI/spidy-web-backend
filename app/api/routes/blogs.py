import time

from fastapi import APIRouter, Depends, HTTPException, status

from app.core.security import require_editor
from app.db import repository
from app.db.repository import DataAccessError
from app.models.schemas import BlogCreateSchema, BlogSchema

router = APIRouter(prefix="/api/blogs", tags=["blogs"])


def _slugify(title: str) -> str:
    slug = title.lower().replace(" ", "-")
    return "".join(c for c in slug if c.isalnum() or c == "-")


@router.get("", response_model=list[BlogSchema])
def get_blogs():
    try:
        return repository.get_blogs()
    except DataAccessError as e:
        raise HTTPException(status.HTTP_503_SERVICE_UNAVAILABLE, str(e))
    except Exception as e:
        raise HTTPException(status.HTTP_500_INTERNAL_SERVER_ERROR, f"Failed to fetch blogs: {e}")


@router.get("/{blog_id}", response_model=BlogSchema)
def get_blog(blog_id: str):
    try:
        blog = repository.get_blog(blog_id)
    except DataAccessError as e:
        raise HTTPException(status.HTTP_503_SERVICE_UNAVAILABLE, str(e))
    if not blog:
        raise HTTPException(status.HTTP_404_NOT_FOUND, f"Blog with ID {blog_id} not found")
    return blog


@router.post("", response_model=BlogSchema)
def create_blog(blog_data: BlogCreateSchema, _auth=Depends(require_editor)):
    try:
        blog_id = _slugify(blog_data.title)
        if repository.get_blog(blog_id):
            blog_id = f"{blog_id}-{int(time.time())}"

        full_blog = blog_data.model_dump()
        full_blog["id"] = blog_id
        repository.save_blog(blog_id, full_blog)
        return full_blog
    except DataAccessError as e:
        raise HTTPException(status.HTTP_503_SERVICE_UNAVAILABLE, str(e))
    except Exception as e:
        raise HTTPException(status.HTTP_500_INTERNAL_SERVER_ERROR, f"Failed to create blog: {e}")


@router.put("/{blog_id}", response_model=BlogSchema)
def update_blog(blog_id: str, blog_data: BlogCreateSchema, _auth=Depends(require_editor)):
    try:
        existing = repository.get_blog(blog_id)
    except DataAccessError as e:
        raise HTTPException(status.HTTP_503_SERVICE_UNAVAILABLE, str(e))
    if not existing:
        raise HTTPException(status.HTTP_404_NOT_FOUND, f"Blog with ID {blog_id} not found")

    try:
        full_blog = blog_data.model_dump()
        full_blog["id"] = blog_id
        repository.save_blog(blog_id, full_blog)
        return full_blog
    except Exception as e:
        raise HTTPException(status.HTTP_500_INTERNAL_SERVER_ERROR, f"Failed to update blog: {e}")


@router.delete("/{blog_id}")
def delete_blog(blog_id: str, _auth=Depends(require_editor)):
    try:
        existing = repository.get_blog(blog_id)
    except DataAccessError as e:
        raise HTTPException(status.HTTP_503_SERVICE_UNAVAILABLE, str(e))
    if not existing:
        raise HTTPException(status.HTTP_404_NOT_FOUND, f"Blog with ID {blog_id} not found")

    try:
        repository.delete_blog(blog_id)
        return {"message": f"Blog with ID {blog_id} deleted successfully"}
    except Exception as e:
        raise HTTPException(status.HTTP_500_INTERNAL_SERVER_ERROR, f"Failed to delete blog: {e}")
