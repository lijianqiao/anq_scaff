"""
缓存模块

提供统一的缓存接口和装饰器
"""

import hashlib
import json
from collections.abc import Callable
from functools import wraps
from typing import Any, ParamSpec, TypeVar

from loguru import logger

P = ParamSpec("P")
T = TypeVar("T")


def cached(
    expire: int = 3600,
    key_prefix: str = "",
    key_builder: Callable[..., str] | None = None,
) -> Callable[[Callable[P, T]], Callable[P, T]]:
    """
    缓存装饰器

    Args:
        expire: 过期时间（秒）
        key_prefix: 缓存键前缀
        key_builder: 自定义键构建函数

    Returns:
        装饰器函数
    """

    def decorator(func: Callable[P, T]) -> Callable[P, T]:
        @wraps(func)
        async def wrapper(*args: Any, **kwargs: Any) -> Any:
            # 构建缓存键
            if key_builder:
                cache_key = key_builder(*args, **kwargs)
            else:
                # 默认键构建
                key_data = {
                    "func": func.__name__,
                    "args": str(args),
                    "kwargs": str(sorted(kwargs.items())),
                }
                key_hash = hashlib.md5(json.dumps(key_data, sort_keys=True).encode()).hexdigest()[:16]
                cache_key = f"{key_prefix}:{func.__name__}:{key_hash}"

            # 尝试从缓存获取（延迟导入避免循环依赖）
            from app.initializer import g  # type: ignore
            cache_manager = getattr(g, "cache_manager", None)
            if cache_manager:
                cached_value = cache_manager.get(cache_key)
                if cached_value is not None:
                    logger.debug(f"缓存命中: {cache_key}")
                    return cached_value

            # 执行函数
            result = await func(*args, **kwargs)  # type: ignore

            # 存入缓存
            if cache_manager and result is not None:
                cache_manager.set(cache_key, result, expire=expire)
                logger.debug(f"缓存写入: {cache_key}")

            return result

        return wrapper  # type: ignore

    return decorator


__all__ = ["cached"]
