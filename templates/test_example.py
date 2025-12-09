"""
测试示例 - API集成测试
"""

from typing import Any

import pytest
from fastapi.testclient import TestClient
from sqlalchemy.ext.asyncio import AsyncSession

# 注意：pytest fixture 通过函数参数自动注入，无需导入
# conftest.py 中的 fixture 会自动被发现


def test_ping(test_client: TestClient) -> None:
    """测试ping接口"""
    response = test_client.get("/api/ping")
    assert response.status_code == 200
    data: dict[str, Any] = response.json()
    assert data["code"] == 0


def test_health(test_client: TestClient) -> None:
    """测试health接口"""
    response = test_client.get("/api/health")
    assert response.status_code == 200
    data: dict[str, Any] = response.json()
    assert data["code"] == 0


def test_unified_action_list(
    test_client: TestClient,
    auth_headers: dict[str, str],
) -> None:
    """测试统一动作接口 - list"""
    response = test_client.post(
        "/api/v1/user/actions",  # 注意：v1 版本 API
        json={"action": "list", "params": {"page": 1, "size": 10}},
        headers=auth_headers,
    )
    assert response.status_code == 200
    data: dict[str, Any] = response.json()
    # 成功或资源不存在都是正常的
    assert data["code"] in [0, 4001, 2001]


def test_unified_action_get(
    test_client: TestClient,
    auth_headers: dict[str, str],
) -> None:
    """测试统一动作接口 - get"""
    response = test_client.post(
        "/api/v1/user/actions",  # 注意：v1 版本 API
        json={"action": "get", "params": {"id": "test_id"}},
        headers=auth_headers,
    )
    assert response.status_code == 200
    data: dict[str, Any] = response.json()
    # 成功或资源不存在都是正常的
    assert data["code"] in [0, 4001, 2001]


def test_unified_action_create(
    test_client: TestClient,
    auth_headers: dict[str, str],
) -> None:
    """测试统一动作接口 - create"""
    response = test_client.post(
        "/api/v1/user/actions",  # 注意：v1 版本 API
        json={
            "action": "create",
            "params": {"name": "test_user", "description": "test description"},
        },
        headers=auth_headers,
    )
    assert response.status_code == 200
    data: dict[str, Any] = response.json()
    # 成功或资源已存在都是正常的
    assert data["code"] in [0, 4002, 2001]


@pytest.mark.asyncio
async def test_database_operation(test_db_session: AsyncSession) -> None:
    """测试数据库操作"""
    from app.models.user import User  # type: ignore
    from app.utils import db_async_util  # type: ignore

    # 创建测试数据
    user_id = await db_async_util.create(
        session=test_db_session,
        model=User,
        data={"id": "test_id", "name": "test", "status": 1},
    )

    assert user_id is not None

    # 查询数据
    user = await db_async_util.fetch_one(
        session=test_db_session, model=User, filter_by={"id": user_id}
    )

    assert user is not None
    assert user.name == "test"
