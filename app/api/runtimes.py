from fastapi import APIRouter, Depends, HTTPException

from app.api.dependencies import get_runtime_service
from app.models.portfolio import Runtime, RuntimeCreate, RuntimeUpdate
from app.services.runtime_service import RuntimeService

router = APIRouter()


@router.post("", response_model=Runtime)
def create_runtime(payload: RuntimeCreate, service: RuntimeService = Depends(get_runtime_service)) -> Runtime:
    try:
        return service.create_runtime(payload)
    except ValueError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc


@router.get("", response_model=list[Runtime])
def list_runtimes(user_id: str | None = None, service: RuntimeService = Depends(get_runtime_service)) -> list[Runtime]:
    if user_id:
        return service.list_user_runtimes(user_id)
    return service.list_all()


@router.get("/{runtime_id}", response_model=Runtime)
def get_runtime(runtime_id: str, service: RuntimeService = Depends(get_runtime_service)) -> Runtime:
    runtime = service.get_runtime(runtime_id)
    if runtime is None or not runtime.published:
        raise HTTPException(status_code=404, detail="Runtime not found")
    return runtime


@router.put("/{runtime_id}", response_model=Runtime)
def update_runtime(
    runtime_id: str,
    payload: RuntimeUpdate,
    service: RuntimeService = Depends(get_runtime_service),
) -> Runtime:
    runtime = service.update_runtime(runtime_id, payload)
    if runtime is None:
        raise HTTPException(status_code=404, detail="Runtime not found")
    return runtime


@router.delete("/{runtime_id}", status_code=204)
def delete_runtime(runtime_id: str, service: RuntimeService = Depends(get_runtime_service)) -> None:
    service.delete_runtime(runtime_id)
