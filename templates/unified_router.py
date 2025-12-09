"""
统一路由接口 - POST /<资源>/actions 模式
"""

# 导入引发的报错在创建项目之后会自动消失
import re
from typing import Any

from fastapi import APIRouter, Body, Depends, HTTPException
from fastapi import status as http_status
from loguru import logger
from pydantic import BaseModel

from app.api.dependencies import JWTUser, get_current_user_required
from app.api.exceptions import BaseAppError
from app.api.responses import Responses
from app.api.status import Status
from app.initializer._settings import settings


class ActionRequest(BaseModel):
    """统一动作请求模型"""

    action: str  # 动作名称：list, get, create, update, delete
    params: dict[str, Any] = {}  # 动作参数


router = APIRouter()


# 允许的资源白名单（安全机制）
# 从配置加载，留空则统一路由不可用
ALLOWED_RESOURCES: set[str] = set(settings.api_allowed_resources)
ALLOW_ALL: bool = settings.unified_route_allow_all
REQUIRE_AUTH: bool = True  # 始终强制认证

# 允许的动作白名单
ALLOWED_ACTIONS: set[str] = {"list", "get", "create", "update", "delete"}

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


@router.post("/{resource}/actions")
async def unified_action(
    resource: str,
    request: ActionRequest = Body(...),
    current_user: JWTUser | None = Depends(get_current_user_required),
) -> dict[str, Any]:
    """
    统一动作接口 - POST /<资源>/actions

    所有CRUD操作均通过此接口，遵循统一规范：
    - action: 动作名称（list, get, create, update, delete）
    - params: 动作参数
    """
    if current_user is None:
        # 双重保护，确保未认证时直接返回 401
        raise HTTPException(
            status_code=http_status.HTTP_401_UNAUTHORIZED,
            detail="未授权访问",
            headers={"WWW-Authenticate": "Bearer"},
        )

    if not ALLOW_ALL and not ALLOWED_RESOURCES:
        logger.warning("统一路由未配置允许的资源，已拒绝请求")
        return Responses.failure(status=Status.PARAMS_ERROR, msg="统一路由未启用或未配置白名单")

    # 验证资源名称（安全检查）
    if not _validate_resource(resource):
        logger.warning(f"非法资源访问尝试: resource={resource}")
        return Responses.failure(status=Status.PARAMS_ERROR, msg=f"不支持的资源: {resource}")

    # 验证动作名称
    if request.action not in ALLOWED_ACTIONS:
        return Responses.failure(status=Status.PARAMS_ERROR, msg=f"不支持的动作: {request.action}")

    try:
        # 根据资源名称和动作分发到对应的服务
        handler = _get_action_handler(resource, request.action)
        if not handler:
            return Responses.failure(
                status=Status.PARAMS_ERROR,
                msg=f"资源 '{resource}' 不支持动作 '{request.action}'",
            )

        # 执行动作
        result = await handler(request.params, current_user)
        return Responses.success(data=result)

    except BaseAppError as e:
        # 业务异常，返回具体错误码和消息
        logger.warning(f"业务异常: resource={resource}, action={request.action}, error={e.msg}")
        return Responses.failure(status=e.status, msg=e.msg, data=e.data)

    except Exception:
        # 未知异常，记录详细日志
        logger.exception(f"统一动作接口执行失败: resource={resource}, action={request.action}")
        return Responses.failure(msg="系统错误，请稍后重试")


def _get_action_handler(resource: str, action: str) -> Any:
    """
    获取动作处理器

    Args:
        resource: 资源名称（已通过验证）
        action: 动作名称

    Returns:
        处理器方法，如果不存在返回 None
    """
    try:
        module_name = f"app.services.{resource}"
        service_module = __import__(module_name, fromlist=[f"{resource.capitalize()}Service"])
        service_class = getattr(service_module, f"{resource.capitalize()}Service", None)

        if not service_class:
            return None

        service_instance = service_class()
        handler_method = getattr(service_instance, action, None)
        return handler_method

    except (ImportError, AttributeError):
        return None
