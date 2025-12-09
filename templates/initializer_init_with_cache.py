"""
初始化（带缓存版）
"""

import threading
from functools import cached_property
from typing import Optional

from app.initializer._cache import CacheManager
from app.initializer._conf import Config, init_config
from app.initializer._db import init_db_async_session, init_db_session
from app.initializer._log import init_logger
from app.initializer._redis import RedisClient, init_redis_client
from app.initializer._snow import init_snow_client
from loguru import logger
from loguru._logger import Logger  # noqa
from sqlalchemy.orm import scoped_session, sessionmaker


class Singleton(type):
    """单例元类"""

    _instances = {}
    _lock = threading.Lock()

    def __call__(cls, *args, **kwargs):
        if cls not in cls._instances:
            with cls._lock:
                if cls not in cls._instances:
                    cls._instances[cls] = super().__call__(*args, **kwargs)
        return cls._instances[cls]


class G(metaclass=Singleton):
    _initialized = False
    _init_lock = threading.Lock()
    _init_properties = [
        "config",
        "logger",
        "snow_client",
        "db_async_session",
        "redis_client",
        "cache_manager",
    ]

    def __init__(self):
        self._initialized = False

    @cached_property
    def config(self) -> Config:
        return init_config()

    @cached_property
    def logger(self) -> Logger:
        return init_logger(
            level="DEBUG" if self.config.app_debug else "INFO",
            serialize=self.config.app_log_serialize,
            basedir=self.config.app_log_basedir,
        )

    @cached_property
    def snow_client(self):
        return init_snow_client(datacenter_id=self.config.snow_datacenter_id)

    @cached_property
    def db_session(self) -> scoped_session:
        return init_db_session(
            db_url=self.config.db_url,
            db_echo=self.config.app_debug,
            is_create_tables=True,
        )

    @cached_property
    def db_async_session(self) -> sessionmaker:
        return init_db_async_session(
            db_url=self.config.db_async_url,
            db_echo=self.config.app_debug,
            is_create_tables=True,
        )

    @cached_property
    def redis_client(self) -> Optional[RedisClient]:
        return init_redis_client(
            host=self.config.redis_host,
            port=self.config.redis_port,
            db=self.config.redis_db,
            password=self.config.redis_password,
            max_connections=self.config.redis_max_connections,
        )

    @cached_property
    def cache_manager(self) -> CacheManager:
        return CacheManager(redis_client=self.redis_client)

    def setup(self):
        with self._init_lock:
            if not self._initialized:
                for prop_name in self._init_properties:
                    if hasattr(self, prop_name):
                        getattr(self, prop_name)
                    else:
                        logger.warning(f"{prop_name} not found")
                self._initialized = True


g = G()
