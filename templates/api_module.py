"""
API接口 - ${ModuleName}
统一路由接口：POST /${module_name}/actions
"""

from typing import Any

from fastapi import APIRouter, Body, Depends

# type: ignore 用于模板文件
from app.api.dependencies import JWTUser, get_current_user  # type: ignore
from app.api.responses import Responses  # type: ignore
from app.api.status import Status  # type: ignore
from app.schemas.${module_name} import ${ModuleName}Create, ${ModuleName}Update  # type: ignore
from app.services.${module_name} import ${ModuleName}Service  # type: ignore

router = APIRouter()
_active = True
_tag = "${module_name}"


@router.post("/${module_name}/actions")
async def unified_action(
    request: dict[str, Any] = Body(...),
    current_user: JWTUser | None = Depends(get_current_user),
) -> dict[str, Any]:
    """
    统一动作接口
    action: list, get, create, update, delete
    """
    _ = current_user  # 可用于权限检查
    action = request.get("action")
    params = request.get("params", {})

    service = ${ModuleName}Service()

    try:
        if action == "list":
            page = params.get("page", 1)
            size = params.get("size", 10)
            items, total = await service.list(page=page, size=size)
            return Responses.success(data={"items": items, "total": total})

        elif action == "get":
            id = params.get("id")
            if not id:
                return Responses.failure(status=Status.PARAMS_ERROR, msg="缺少id参数")
            data = await service.get(id)
            if not data:
                return Responses.failure(status=Status.RECORD_NOT_EXIST_ERROR)
            return Responses.success(data=data)

        elif action == "create":
            create_data = ${ModuleName}Create(**params)
            id = await service.create(create_data)
            return Responses.success(data={"id": id})

        elif action == "update":
            id = params.get("id")
            if not id:
                return Responses.failure(status=Status.PARAMS_ERROR, msg="缺少id参数")
            update_data = ${ModuleName}Update(**params)
            success = await service.update(id, update_data)
            if not success:
                return Responses.failure(status=Status.RECORD_NOT_EXIST_ERROR)
            return Responses.success(data={"id": id})

        elif action == "delete":
            id = params.get("id")
            if not id:
                return Responses.failure(status=Status.PARAMS_ERROR, msg="缺少id参数")
            success = await service.delete(id)
            if not success:
                return Responses.failure(status=Status.RECORD_NOT_EXIST_ERROR)
            return Responses.success(data={"id": id})

        else:
            return Responses.failure(
                status=Status.PARAMS_ERROR, msg=f"不支持的动作: {action}"
            )

    except Exception as e:
        return Responses.failure(msg=f"操作失败: {e!s}", error=str(e))
