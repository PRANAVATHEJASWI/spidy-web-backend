from fastapi import APIRouter, Depends, HTTPException, status

from app.core.security import require_editor
from app.db import repository
from app.db.repository import DataAccessError
from app.models.schemas import ResumeSchema

router = APIRouter(prefix="/api/resume", tags=["resume"])


@router.get("", response_model=ResumeSchema)
def get_resume():
    try:
        return repository.get_resume()
    except DataAccessError as e:
        raise HTTPException(status.HTTP_503_SERVICE_UNAVAILABLE, str(e))
    except Exception as e:
        raise HTTPException(status.HTTP_500_INTERNAL_SERVER_ERROR, f"Failed to fetch resume: {e}")


@router.post("")
def update_resume(resume_data: ResumeSchema, _auth=Depends(require_editor)):
    try:
        repository.save_resume(resume_data.model_dump())
        return {"message": "Resume updated successfully"}
    except DataAccessError as e:
        raise HTTPException(status.HTTP_503_SERVICE_UNAVAILABLE, str(e))
    except Exception as e:
        raise HTTPException(status.HTTP_500_INTERNAL_SERVER_ERROR, f"Failed to update resume: {e}")
