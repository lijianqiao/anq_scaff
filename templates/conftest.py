"""
Pytest 配置文件
定义测试 fixtures
"""

from collections.abc import AsyncGenerator, Generator

import pytest
from fastapi.testclient import TestClient
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine

# 导入所有模型以确保表被创建
# 这会触发 models/__init__.py 的自动导入
import app.models  # type: ignore # noqa: F401
from app.initializer._db import Base  # type: ignore

# 测试数据库URL（内存数据库）
TEST_DB_URL = "sqlite+aiosqlite:///:memory:"


@pytest.fixture(scope="function")
async def test_db_session() -> AsyncGenerator[AsyncSession, None]:
    """测试数据库会话"""
    # 创建测试数据库引擎
    engine = create_async_engine(TEST_DB_URL, echo=False)

    # 创建表（现在模型已导入，metadata 不为空）
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    # 创建会话
    async_session_factory = async_sessionmaker(
        bind=engine,
        expire_on_commit=False,
    )

    async with async_session_factory() as session:
        yield session

    # 清理
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)

    await engine.dispose()


@pytest.fixture(scope="function")
def test_client() -> Generator[TestClient, None, None]:
    """测试客户端"""
    # 确保导入的是 FastAPI 应用实例而不是模块
    from app.main import app as fastapi_app

    # 创建测试客户端
    client = TestClient(fastapi_app)
    yield client


@pytest.fixture
def auth_headers() -> dict[str, str]:
    """
    认证头部（JWT Token）

    生成有效的测试用 JWT Token
    """
    from app.utils.jwt_util import create_access_token  # type: ignore

    # 生成测试 Token
    test_payload = {
        "sub": "test_user_id",
        "username": "test_user",
        "roles": ["user"],
    }
    token = create_access_token(test_payload)

    return {"Authorization": f"Bearer {token}"}


@pytest.fixture
def api_key_headers() -> dict[str, str]:
    """
    API Key 头部

    使用配置中的有效 API Key
    """
    from app.initializer._settings import settings  # type: ignore

    # 获取配置中的第一个有效 API Key
    api_keys = settings.api_keys
    if api_keys:
        return {"X-API-Key": api_keys[0]}

    # 如果没有配置 API Key，返回测试 Key
    return {"X-API-Key": "test_api_key"}


@pytest.fixture
def test_user_data() -> dict:
    """测试用户数据"""
    return {
        "id": "test_id_001",
        "name": "测试用户",
        "email": "test@example.com",
        "status": 1,
    }
