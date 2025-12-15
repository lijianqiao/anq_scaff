"""统一路由接口 - RESTful 模式

提供一组通用 RESTful 入口（可选启用，受白名单控制）：
- GET    /<resource>
- GET    /<resource>/{id}
- POST   /<resource>
- PATCH  /<resource>/{id}
- DELETE /<resource>/{id}

说明：
- 该路由通过资源名动态导入 service/schema 做分发。
- 若项目已为资源生成了显式模块路由（app.api.v1.<resource>），优先使用显式路由。
"""

import importlib
import re
from typing import Any

from fastapi import APIRouter, Body, Depends, HTTPException
from fastapi import status as http_status
from loguru import logger
from pydantic import ValidationError

from app.api.dependencies import JWTUser, get_current_user_required
from app.api.exceptions import BaseAppError
from app.api.responses import Responses
from app.api.status import Status
from app.initializer._settings import settings


router = APIRouter()


# 允许的资源白名单（安全机制）
# 从配置加载，留空则统一路由不可用
ALLOWED_RESOURCES: set[str] = set(settings.api_allowed_resources)
ALLOW_ALL: bool = settings.unified_route_allow_all
REQUIRE_AUTH: bool = True  # 始终强制认证

# 资源名称正则验证（只允许小写字母、数字和下划线）
RESOURCE_NAME_PATTERN = re.compile(r"^[a-z][a-z0-9_]*$")


def _validate_resource(resource: str) -> bool:
    """
    验证资源名称是否合法

    Args:
        resource: 资源名称

    Returns:
        是否合法
    """
    # 检查命名格式
    if not RESOURCE_NAME_PATTERN.match(resource):
        return False

    # 如果设置了白名单，检查是否在白名单中
    if not ALLOW_ALL and ALLOWED_RESOURCES and resource not in ALLOWED_RESOURCES:
        return False

    return True


def _snake_to_pascal(name: str) -> str:
    return "".join(part[:1].upper() + part[1:] for part in name.split("_") if part)


def _get_service_instance(resource: str) -> Any | None:
    try:
        module_name = f"app.services.{resource}"
        service_module = importlib.import_module(module_name)
        service_class = getattr(service_module, f"{_snake_to_pascal(resource)}Service", None)
        if not service_class:
            return None
        return service_class()
    except Exception:
        return None


def _get_schema_types(resource: str) -> tuple[type[Any] | None, type[Any] | None]:
    try:
        module_name = f"app.schemas.{resource}"
        schema_module = importlib.import_module(module_name)
        pascal = _snake_to_pascal(resource)
        create_type = getattr(schema_module, f"{pascal}Create", None)
        update_type = getattr(schema_module, f"{pascal}Update", None)
        return create_type, update_type
    except Exception:
        return None, None


def _ensure_allowed(resource: str, current_user: JWTUser | None) -> None:
    if current_user is None:
        raise HTTPException(
            status_code=http_status.HTTP_401_UNAUTHORIZED,
            detail="未授权访问",
            headers={"WWW-Authenticate": "Bearer"},
        )

    if not ALLOW_ALL and not ALLOWED_RESOURCES:
        logger.warning("统一路由未配置允许的资源，已拒绝请求")
        raise HTTPException(
            status_code=http_status.HTTP_404_NOT_FOUND,
            detail="统一路由未启用或未配置白名单",
        )

    if not _validate_resource(resource):
        logger.warning(f"非法资源访问尝试: resource={resource}")
        raise HTTPException(
            status_code=http_status.HTTP_404_NOT_FOUND,
            detail=f"不支持的资源: {resource}",
        )


@router.get("/{resource}")
async def list_resource(
    resource: str,
    page: int = 1,
    size: int = 10,
    current_user: JWTUser | None = Depends(get_current_user_required),
) -> dict[str, Any]:
    _ensure_allowed(resource, current_user)
    service = _get_service_instance(resource)
    if not service or not hasattr(service, "list"):
        return Responses.failure(status=Status.PARAMS_ERROR, msg=f"资源 '{resource}' 不支持 list")
    try:
        items, total = await service.list(page=page, size=size)
        return Responses.success(data={"items": items, "total": total})
    except BaseAppError as e:
        return Responses.failure(status=e.status, msg=e.msg, data=e.data)
    except Exception:
        logger.exception(f"统一RESTful接口执行失败: resource={resource}, action=list")
        return Responses.failure(msg="系统错误，请稍后重试")


@router.get("/{resource}/{id}")
async def get_resource(
    resource: str,
    id: str,
    current_user: JWTUser | None = Depends(get_current_user_required),
) -> dict[str, Any]:
    _ensure_allowed(resource, current_user)
    service = _get_service_instance(resource)
    if not service or not hasattr(service, "get"):
        return Responses.failure(status=Status.PARAMS_ERROR, msg=f"资源 '{resource}' 不支持 get")
    try:
        data = await service.get(id)
        if not data:
            return Responses.failure(status=Status.RECORD_NOT_EXIST_ERROR)
        return Responses.success(data=data)
    except BaseAppError as e:
        return Responses.failure(status=e.status, msg=e.msg, data=e.data)
    except Exception:
        logger.exception(f"统一RESTful接口执行失败: resource={resource}, action=get")
        return Responses.failure(msg="系统错误，请稍后重试")


@router.post("/{resource}")
async def create_resource(
    resource: str,
    payload: dict[str, Any] = Body(...),
    current_user: JWTUser | None = Depends(get_current_user_required),
) -> dict[str, Any]:
    _ensure_allowed(resource, current_user)
    service = _get_service_instance(resource)
    if not service or not hasattr(service, "create"):
        return Responses.failure(status=Status.PARAMS_ERROR, msg=f"资源 '{resource}' 不支持 create")
    create_type, _ = _get_schema_types(resource)
    if not create_type:
        return Responses.failure(status=Status.PARAMS_ERROR, msg=f"资源 '{resource}' 未找到 Create schema")
    try:
        create_obj = create_type(**payload)
        new_id = await service.create(create_obj)
        return Responses.success(data={"id": new_id})
    except ValidationError as e:
        return Responses.failure(status=Status.PARAMS_ERROR, msg="参数验证失败", data={"errors": e.errors()})
    except BaseAppError as e:
        return Responses.failure(status=e.status, msg=e.msg, data=e.data)
    except Exception:
        logger.exception(f"统一RESTful接口执行失败: resource={resource}, action=create")
        return Responses.failure(msg="系统错误，请稍后重试")


@router.patch("/{resource}/{id}")
async def update_resource(
    resource: str,
    id: str,
    payload: dict[str, Any] = Body(...),
    current_user: JWTUser | None = Depends(get_current_user_required),
) -> dict[str, Any]:
    _ensure_allowed(resource, current_user)
    service = _get_service_instance(resource)
    if not service or not hasattr(service, "update"):
        return Responses.failure(status=Status.PARAMS_ERROR, msg=f"资源 '{resource}' 不支持 update")
    _, update_type = _get_schema_types(resource)
    if not update_type:
        return Responses.failure(status=Status.PARAMS_ERROR, msg=f"资源 '{resource}' 未找到 Update schema")
    try:
        update_obj = update_type(**payload)
        ok = await service.update(id, update_obj)
        if not ok:
            return Responses.failure(status=Status.RECORD_NOT_EXIST_ERROR)
        return Responses.success(data={"id": id})
    except ValidationError as e:
        return Responses.failure(status=Status.PARAMS_ERROR, msg="参数验证失败", data={"errors": e.errors()})
    except BaseAppError as e:
        return Responses.failure(status=e.status, msg=e.msg, data=e.data)
    except Exception:
        logger.exception(f"统一RESTful接口执行失败: resource={resource}, action=update")
        return Responses.failure(msg="系统错误，请稍后重试")


@router.delete("/{resource}/{id}")
async def delete_resource(
    resource: str,
    id: str,
    current_user: JWTUser | None = Depends(get_current_user_required),
) -> dict[str, Any]:
    _ensure_allowed(resource, current_user)
    service = _get_service_instance(resource)
    if not service or not hasattr(service, "delete"):
        return Responses.failure(status=Status.PARAMS_ERROR, msg=f"资源 '{resource}' 不支持 delete")
    try:
        ok = await service.delete(id)
        if not ok:
            return Responses.failure(status=Status.RECORD_NOT_EXIST_ERROR)
        return Responses.success(data={"id": id})
    except BaseAppError as e:
        return Responses.failure(status=e.status, msg=e.msg, data=e.data)
    except Exception:
        logger.exception(f"统一RESTful接口执行失败: resource={resource}, action=delete")
        return Responses.failure(msg="系统错误，请稍后重试")
