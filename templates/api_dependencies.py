"""
API 依赖注入
提供 JWT 认证和 API Key 验证的依赖函数
"""

from fastapi import Depends, Header, HTTPException, status
from pydantic import BaseModel, ConfigDict

from app.utils.api_key_util import is_valid_api_key  # type: ignore
from app.utils.jwt_util import verify_token  # type: ignore


class JWTUser(BaseModel):
    """JWT用户信息"""

    model_config = ConfigDict(extra="allow")

    user_id: str
    username: str | None = None
    roles: list[str] = []


async def get_token(authorization: str | None = Header(None)) -> str | None:
    """
    从请求头获取Token

    Args:
        authorization: Authorization请求头

    Returns:
        Token字符串或None
    """
    if not authorization:
        return None

    # 支持 Bearer Token 格式
    if authorization.startswith("Bearer "):
        return authorization[7:]

    return authorization


async def get_current_user(token: str | None = Depends(get_token)) -> JWTUser | None:
    """
    获取当前用户（可选认证）

    Args:
        token: JWT Token

    Returns:
        JWTUser实例或None
    """
    if not token:
        return None

    payload = verify_token(token)
    if not payload:
        return None

    user_id = payload.get("sub")
    username = payload.get("username")
    roles = payload.get("roles")

    return JWTUser(
        user_id=str(user_id) if user_id else "",
        username=str(username) if username else None,
        roles=list(roles) if isinstance(roles, list) else [],
    )


async def get_current_user_required(
    current_user: JWTUser | None = Depends(get_current_user),
) -> JWTUser:
    """
    获取当前用户（必须认证）

    Args:
        current_user: 当前用户

    Returns:
        JWTUser实例

    Raises:
        HTTPException: 如果未认证
    """
    if not current_user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="未授权访问",
            headers={"WWW-Authenticate": "Bearer"},
        )
    return current_user


async def get_api_key(x_api_key: str | None = Header(None)) -> str | None:
    """
    从请求头获取API Key

    Args:
        x_api_key: X-API-Key请求头

    Returns:
        API Key字符串或None
    """
    return x_api_key


async def verify_api_key_required(api_key: str | None = Depends(get_api_key)) -> str:
    """
    验证API Key（必须）

    从配置中读取有效的 API Keys 列表进行验证。

    Args:
        api_key: API Key

    Returns:
        API Key字符串

    Raises:
        HTTPException: 如果API Key无效
    """
    if not api_key:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="缺少API Key",
        )

    # 验证 API Key 是否在配置的有效列表中
    if not is_valid_api_key(api_key):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="API Key无效",
        )

    return api_key


async def verify_api_key_optional(
    api_key: str | None = Depends(get_api_key),
) -> str | None:
    """
    验证API Key（可选）

    如果提供了 API Key，则验证其有效性。

    Args:
        api_key: API Key

    Returns:
        API Key字符串或None

    Raises:
        HTTPException: 如果提供的API Key无效
    """
    if not api_key:
        return None

    if not is_valid_api_key(api_key):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="API Key无效",
        )

    return api_key
