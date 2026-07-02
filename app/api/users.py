from fastapi import APIRouter, Depends, HTTPException

from app.api.dependencies import get_user_service
from app.models.user import User, UserCreate, UserLogin
from app.services.user_service import UserService

router = APIRouter()


@router.post("", response_model=User)
def create_user(payload: UserCreate, service: UserService = Depends(get_user_service)) -> User:
    try:
        return service.create_user(payload)
    except ValueError as exc:
        raise HTTPException(status_code=409, detail=str(exc)) from exc


@router.post("/login", response_model=User)
def login(payload: UserLogin, service: UserService = Depends(get_user_service)) -> User:
    user = service.login(payload)
    if user is None:
        raise HTTPException(status_code=401, detail="Invalid email or password")
    return user


@router.get("", response_model=list[User])
def list_users(service: UserService = Depends(get_user_service)) -> list[User]:
    return service.list_users()


@router.get("/{user_id}", response_model=User)
def get_user(user_id: str, service: UserService = Depends(get_user_service)) -> User:
    user = service.get_user(user_id)
    if user is None:
        raise HTTPException(status_code=404, detail="User not found")
    return user
