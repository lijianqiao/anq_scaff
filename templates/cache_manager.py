"""
缓存管理器
提供统一的缓存操作接口
"""

import json
from typing import Any

from loguru import logger


class CacheManager:
    """
    缓存管理器
    自动在内存缓存和Redis缓存之间切换
    """

    def __init__(self, redis_client: Any = None):
        """
        初始化缓存管理器

        Args:
            redis_client: Redis客户端实例，如果为None则使用内存缓存
        """
        self.redis_client: Any = redis_client
        self._memory_cache: dict[str, Any] = {}
        self._use_redis: bool = redis_client is not None

        if self._use_redis:
            logger.info("缓存管理器使用 Redis 后端")
        else:
            logger.info("缓存管理器使用内存后端")

    def get(self, key: str) -> Any | None:
        """
        获取缓存值

        Args:
            key: 缓存键

        Returns:
            缓存值，如果不存在返回None
        """
        if self._use_redis and self.redis_client is not None:
            try:
                with self.redis_client.connection() as r:
                    value = r.get(key)
                    if value:
                        return json.loads(value)
            except Exception as e:
                logger.warning(f"Redis获取缓存失败: {e}，回退到内存缓存")

        return self._memory_cache.get(key)

    def set(self, key: str, value: Any, expire: int = 3600) -> bool:
        """
        设置缓存值

        Args:
            key: 缓存键
            value: 缓存值
            expire: 过期时间（秒）

        Returns:
            是否设置成功
        """
        if self._use_redis and self.redis_client is not None:
            try:
                with self.redis_client.connection() as r:
                    r.setex(key, expire, json.dumps(value, ensure_ascii=False))
                    return True
            except Exception as e:
                logger.warning(f"Redis设置缓存失败: {e}，回退到内存缓存")

        self._memory_cache[key] = value
        return True

    def delete(self, key: str) -> bool:
        """
        删除缓存

        Args:
            key: 缓存键

        Returns:
            是否删除成功
        """
        if self._use_redis and self.redis_client is not None:
            try:
                with self.redis_client.connection() as r:
                    r.delete(key)
                    return True
            except Exception as e:
                logger.warning(f"Redis删除缓存失败: {e}")

        if key in self._memory_cache:
            del self._memory_cache[key]
        return True

    def exists(self, key: str) -> bool:
        """
        检查缓存是否存在

        Args:
            key: 缓存键

        Returns:
            是否存在
        """
        if self._use_redis and self.redis_client is not None:
            try:
                with self.redis_client.connection() as r:
                    return bool(r.exists(key))
            except Exception as e:
                logger.warning(f"Redis检查缓存失败: {e}")

        return key in self._memory_cache

    def clear(self) -> bool:
        """清除所有缓存

        Returns:
            是否清除成功
        """
        if self._use_redis and self.redis_client is not None:
            try:
                with self.redis_client.connection() as r:
                    r.flushdb()
                    return True
            except Exception as e:
                logger.warning(f"Redis清除缓存失败: {e}")

        self._memory_cache.clear()
        return True

    def delete_prefix(self, prefix: str) -> int:
        """按前缀批量删除缓存键
        Args:
            prefix: 键前缀
            Returns:
                删除的键数量
        """
        deleted = 0
        if self._use_redis and self.redis_client is not None:
            try:
                with self.redis_client.connection() as r:
                    cursor = 0
                    pattern = f"{prefix}*"
                    while True:
                        cursor, keys = r.scan(cursor=cursor, match=pattern, count=100)
                        if keys:
                            deleted += r.delete(*keys)
                        if cursor == 0:
                            break
            except Exception as e:
                logger.warning(f"Redis按前缀删除失败: {e}")

        # 内存缓存处理
        to_delete = [k for k in self._memory_cache if k.startswith(prefix)]
        for key in to_delete:
            del self._memory_cache[key]
            deleted += 1

        return deleted
