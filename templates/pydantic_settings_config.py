"""
应用配置管理 - 基于 pydantic-settings
唯一的配置入口，支持 .env 文件和环境变量
"""

from functools import lru_cache

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """应用配置类 - 使用 pydantic-settings"""

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore",
    )

    # ===== 应用基础配置 =====
    app_name: str = Field(default="FastAPI App", description="应用名称")
    app_version: str = Field(default="1.0.0", description="应用版本")
    app_description: str = Field(default="FastAPI Application", description="应用描述")
    app_debug: bool = Field(default=False, description="调试模式")
    app_env: str = Field(default="dev", description="环境：dev/test/prod")

    # ===== API 文档配置 =====
    app_disable_docs: bool = Field(default=False, description="禁用API文档")
    app_docs_url: str = Field(default="/docs", description="Swagger UI路径")
    app_redoc_url: str = Field(default="/redoc", description="ReDoc路径")

    # ===== 数据库配置 =====
    db_url: str = Field(default="${db_url}", description="数据库URL（同步）")
    db_async_url: str = Field(default="${db_async_url}", description="数据库URL（异步）")
    db_echo: bool = Field(default=False, description="SQL日志")
    db_pool_size: int = Field(default=10, description="连接池大小")
    db_max_overflow: int = Field(default=5, description="最大溢出连接数")
    db_pool_recycle: int = Field(default=3600, description="连接回收时间（秒）")

    # ===== Redis 配置 =====
    redis_host: str | None = Field(default=None, description="Redis主机")
    redis_port: int = Field(default=6379, description="Redis端口")
    redis_db: int = Field(default=0, description="Redis数据库")
    redis_password: str | None = Field(default=None, description="Redis密码")
    redis_max_connections: int = Field(default=10, description="Redis最大连接数")

    # ===== CORS 配置 =====
    cors_allow_origins: list[str] = Field(default=["*"], description="允许的来源")
    cors_allow_credentials: bool = Field(default=True, description="允许凭证")
    cors_allow_methods: list[str] = Field(default=["*"], description="允许的方法")
    cors_allow_headers: list[str] = Field(default=["*"], description="允许的头部")

    # ===== 日志配置 =====
    log_level: str = Field(default="INFO", description="日志级别")
    log_serialize: bool = Field(default=False, description="日志序列化为JSON")
    log_basedir: str = Field(default="./logs", description="日志目录")
    log_enable_console: bool = Field(default=True, description="启用控制台日志")
    log_enable_file: bool = Field(default=True, description="启用文件日志")

    # ===== JWT 配置 =====
    jwt_secret_key: str = Field(
        default="your-secret-key-change-in-production",
        description="JWT密钥（生产环境必须修改）",
    )
    jwt_algorithm: str = Field(default="HS256", description="JWT算法")
    jwt_expire_minutes: int = Field(default=1440, description="JWT过期时间（分钟）")

    # ===== API Key 配置 =====
    api_keys: list[str] = Field(default=["demo_api_key"], description="有效的API密钥列表")
    api_key_prefix: str = Field(default="anq_", description="API Key前缀")
    api_key_length: int = Field(default=32, description="API Key长度")

    # ===== 统一路由安全配置 =====
    api_allowed_resources: list[str] = Field(default=["user"], description="统一路由允许的资源白名单")
    unified_route_allow_all: bool = Field(default=False, description="统一路由是否允许所有资源")
    unified_route_require_auth: bool = Field(default=True, description="统一路由是否强制认证")

    # ===== 雪花ID配置 =====
    snow_datacenter_id: int = Field(default=1, description="数据中心ID (1-31)")
    snow_worker_id: int = Field(default=1, description="工作节点ID (1-31)")


@lru_cache
def get_settings() -> Settings:
    """
    获取配置单例（使用 lru_cache 缓存）

    Returns:
        Settings 实例
    """
    return Settings()


# 全局配置实例（便捷访问）
settings = get_settings()
