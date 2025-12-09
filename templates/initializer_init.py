"""
全局初始化器
基于 pydantic-settings 的现代化配置系统
"""

import threading
from functools import cached_property

from loguru import logger
from loguru._logger import Logger
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker

from app.cache.manager import CacheManager
from app.initializer._db import init_db_async_session
from app.initializer._log import init_logger
from app.initializer._redis import RedisClient, init_redis_client
from app.initializer._settings import Settings, settings
from app.initializer._snow import SnowFlake, init_snow_client


class Singleton(type):
    """线程安全的单例元类"""

    _instances: dict[type, object] = {}
    _lock = threading.Lock()

    def __call__(cls, *args: object, **kwargs: object) -> object:
        if cls not in cls._instances:
            with cls._lock:
                if cls not in cls._instances:
                    cls._instances[cls] = super().__call__(*args, **kwargs)
        return cls._instances[cls]


class G(metaclass=Singleton):
    """
    全局对象容器

    使用 cached_property 实现延迟初始化，
    确保资源在首次访问时才创建。
    """

    _initialized: bool = False
    _init_lock: threading.Lock = threading.Lock()
    _init_properties: list[str] = [
        "settings",
        "logger",
        "snow_client",
        "db_async_session",
        "redis_client",
        "cache_manager",
    ]

    def __init__(self) -> None:
        self._initialized = False

    @cached_property
    def settings(self) -> Settings:
        """获取配置实例"""
        return settings

    # 向后兼容别名
    @property
    def config(self) -> Settings:
        """获取配置实例（别名，建议使用 settings）"""
        return self.settings

    @cached_property
    def logger(self) -> Logger:
        """获取日志实例"""
        return init_logger(
            level="DEBUG" if self.settings.app_debug else self.settings.log_level,
            serialize=self.settings.log_serialize,
            basedir=self.settings.log_basedir,
        )

    @cached_property
    def snow_client(self) -> SnowFlake:
        """获取雪花ID生成器"""
        return init_snow_client(
            datacenter_id=self.settings.snow_datacenter_id,
            worker_id=self.settings.snow_worker_id,
        )

    @cached_property
    def db_async_session(self) -> async_sessionmaker[AsyncSession]:
        """获取异步数据库会话工厂"""
        return init_db_async_session(
            db_url=self.settings.db_async_url,
            db_echo=self.settings.db_echo or self.settings.app_debug,
            is_create_tables=True,
        )

    @cached_property
    def redis_client(self) -> RedisClient | None:
        """
        获取 Redis 客户端（可选）

        如果未配置 redis_host，返回 None
        """
        if not self.settings.redis_host:
            logger.info("Redis 未配置，跳过初始化")
            return None
        return init_redis_client(
            host=self.settings.redis_host,
            port=self.settings.redis_port,
            db=self.settings.redis_db,
            password=self.settings.redis_password,
            max_connections=self.settings.redis_max_connections,
        )

    @cached_property
    def cache_manager(self) -> CacheManager:
        """
        获取缓存管理器

        自动降级：如果 Redis 不可用，使用内存缓存
        """

        return CacheManager(redis_client=self.redis_client)

    def setup(self) -> None:
        """
        初始化所有资源

        在应用启动时调用，确保所有资源被正确初始化。
        """
        with self._init_lock:
            if not self._initialized:
                for prop_name in self._init_properties:
                    if hasattr(self, prop_name):
                        try:
                            getattr(self, prop_name)
                        except Exception as e:
                            logger.warning(f"属性 {prop_name} 初始化失败: {e}")
                    else:
                        logger.warning(f"属性 {prop_name} 未找到")
                self._initialized = True
                logger.info("全局资源初始化完成")


# 全局对象实例
g = G()
