"""
JWT 工具模块
从配置读取密钥和算法，遵循配置与代码分离原则
"""

from datetime import datetime, timedelta, timezone

import jwt
from loguru import logger

# type: ignore 用于模板文件
from app.initializer._settings import settings  # type: ignore


def create_access_token(
    data: dict[str, object],
    expires_delta: timedelta | None = None,
) -> str:
    """
    创建访问令牌

    Args:
        data: 要编码的数据
        expires_delta: 过期时间增量

    Returns:
        JWT令牌字符串
    """
    to_encode = data.copy()

    if expires_delta:
        expire = datetime.now(timezone.utc) + expires_delta
    else:
        expire = datetime.now(timezone.utc) + timedelta(
            minutes=settings.jwt_expire_minutes
        )

    to_encode.update({"exp": expire})

    encoded_jwt = jwt.encode(
        to_encode,
        settings.jwt_secret_key,
        algorithm=settings.jwt_algorithm,
    )
    return encoded_jwt


def verify_token(token: str) -> dict[str, object] | None:
    """
    验证JWT令牌

    Args:
        token: JWT令牌字符串

    Returns:
        解码后的数据，如果验证失败返回None
    """
    try:
        payload = jwt.decode(
            token,
            settings.jwt_secret_key,
            algorithms=[settings.jwt_algorithm],
        )
        return payload
    except jwt.ExpiredSignatureError:
        logger.warning("JWT令牌已过期")
        return None
    except jwt.InvalidTokenError as e:
        logger.warning(f"JWT令牌无效: {e}")
        return None


def decode_token(token: str) -> dict[str, object] | None:
    """
    解码JWT令牌（不验证过期时间）

    Args:
        token: JWT令牌字符串

    Returns:
        解码后的数据，如果解码失败返回None
    """
    try:
        payload = jwt.decode(
            token,
            settings.jwt_secret_key,
            algorithms=[settings.jwt_algorithm],
            options={"verify_exp": False},
        )
        return payload
    except jwt.InvalidTokenError as e:
        logger.warning(f"JWT令牌解码失败: {e}")
        return None
