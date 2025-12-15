"""API接口 - ${ModuleName}

RESTful 风格接口：
- GET    /${module_name}
- GET    /${module_name}/{id}
- POST   /${module_name}
- PATCH  /${module_name}/{id}
- DELETE /${module_name}/{id}
"""

from fastapi import APIRouter, Depends

from app.api.dependencies import JWTUser, get_current_user_required
from app.api.responses import Responses
from app.api.status import Status
from app.schemas.${module_name} import ${ModuleName}Create, ${ModuleName}Update
from app.services.${module_name} import ${ModuleName}Service

router = APIRouter(prefix="/${module_name}")
_active = True
_tag = "${module_name}"


@router.get("")
async def list_${module_name}(
    page: int = 1,
    size: int = 10,
    current_user: JWTUser = Depends(get_current_user_required),
) -> dict:
    _ = current_user
    service = ${ModuleName}Service()
    items, total = await service.list(page=page, size=size)
    return Responses.success(data={"items": items, "total": total})


@router.get("/{id}")
async def get_${module_name}(
    id: str,
    current_user: JWTUser = Depends(get_current_user_required),
) -> dict:
    _ = current_user
    service = ${ModuleName}Service()
    data = await service.get(id)
    if not data:
        return Responses.failure(status=Status.RECORD_NOT_EXIST_ERROR)
    return Responses.success(data=data)


@router.post("")
async def create_${module_name}(
    payload: ${ModuleName}Create,
    current_user: JWTUser = Depends(get_current_user_required),
) -> dict:
    _ = current_user
    service = ${ModuleName}Service()
    new_id = await service.create(payload)
    return Responses.success(data={"id": new_id})


@router.patch("/{id}")
async def update_${module_name}(
    id: str,
    payload: ${ModuleName}Update,
    current_user: JWTUser = Depends(get_current_user_required),
) -> dict:
    _ = current_user
    service = ${ModuleName}Service()
    ok = await service.update(id, payload)
    if not ok:
        return Responses.failure(status=Status.RECORD_NOT_EXIST_ERROR)
    return Responses.success(data={"id": id})


@router.delete("/{id}")
async def delete_${module_name}(
    id: str,
    current_user: JWTUser = Depends(get_current_user_required),
) -> dict:
    _ = current_user
    service = ${ModuleName}Service()
    ok = await service.delete(id)
    if not ok:
        return Responses.failure(status=Status.RECORD_NOT_EXIST_ERROR)
    return Responses.success(data={"id": id})
