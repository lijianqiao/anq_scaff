"""
Pytest 配置文件
定义测试 fixtures
"""

from collections.abc import AsyncGenerator, Generator

import pytest
from fastapi.testclient import TestClient
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine

from app.initializer._db import Base  # type: ignore
from app.main import app  # type: ignore

# 测试数据库URL（内存数据库）
TEST_DB_URL = "sqlite+aiosqlite:///:memory:"


@pytest.fixture(scope="function")
async def test_db_session() -> AsyncGenerator[AsyncSession, None]:
    """测试数据库会话"""
    # 创建测试数据库引擎
    engine = create_async_engine(TEST_DB_URL, echo=False)

    # 创建表
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
    # 创建测试客户端
    client = TestClient(app)
    yield client


@pytest.fixture
def auth_headers() -> dict[str, str]:
    """认证头部（JWT Token）"""
    # 这里可以生成测试用的JWT Token
    # 或者使用测试用户登录获取Token
    return {"Authorization": "Bearer test_token"}


@pytest.fixture
def api_key_headers() -> dict[str, str]:
    """API Key头部"""
    return {"X-API-Key": "test_api_key"}
