"""
Redis 初始化
"""

from typing import Any

from loguru import logger


class RedisClient:
    """Redis 客户端封装"""

    host: str
    port: int
    db: int
    password: str | None
    max_connections: int
    _pool: Any

    def __init__(
        self,
        host: str = "localhost",
        port: int = 6379,
        db: int = 0,
        password: str | None = None,
        max_connections: int = 10,
    ):
        """
        初始化 Redis 客户端

        Args:
            host: Redis主机地址
            port: Redis端口
            db: 数据库编号
            password: 密码
            max_connections: 最大连接数
        """
        self.host = host
        self.port = port
        self.db = db
        self.password = password
        self.max_connections = max_connections
        self._pool = None

    @property
    def pool(self) -> Any:
        """获取连接池"""
        if self._pool is None:
            import redis  # 项目创建需要启用Redis缓存，可以自行安装redis依赖，uv pip install reids

            self._pool = redis.ConnectionPool(
                host=self.host,
                port=self.port,
                db=self.db,
                password=self.password,
                max_connections=self.max_connections,
                decode_responses=True,
            )
        return self._pool

    def connection(self) -> Any:
        """获取 Redis 连接"""
        import redis  # 项目创建需要启用Redis缓存，可以自行安装redis依赖，uv pip install reids

        return redis.Redis(connection_pool=self.pool)

    def close(self) -> None:
        """关闭连接池"""
        if self._pool:
            self._pool.disconnect()
            self._pool = None


def init_redis_client(
    host: str = "localhost",
    port: int = 6379,
    db: int = 0,
    password: str | None = None,
    max_connections: int = 10,
) -> RedisClient | None:
    """
    初始化 Redis 客户端

    Args:
        host: Redis主机地址
        port: Redis端口
        db: 数据库编号
        password: 密码
        max_connections: 最大连接数

    Returns:
        RedisClient实例，如果连接失败则返回None
    """
    if not host:
        logger.warning("Redis未配置，跳过初始化")
        return None

    try:
        client = RedisClient(
            host=host,
            port=port,
            db=db,
            password=password,
            max_connections=max_connections,
        )
        # 测试连接
        with client.connection() as r:
            r.ping()
        logger.info(f"Redis连接成功: {host}:{port}/{db}")
        return client
    except Exception as e:
        logger.warning(f"Redis连接失败: {e}，将使用内存缓存")
        return None
