"""
测试示例 - API 集成测试
覆盖健康检查、认证、异常处理、CRUD 等核心功能
"""

from typing import Any

import pytest
from fastapi.testclient import TestClient
from sqlalchemy.ext.asyncio import AsyncSession

# ==================== 健康检查测试 ====================


def test_ping(test_client: TestClient) -> None:
    """测试 ping 接口"""
    response = test_client.get("/api/ping")
    assert response.status_code == 200
    data: dict[str, Any] = response.json()
    assert data["code"] == 0


def test_health(test_client: TestClient) -> None:
    """测试 health 接口"""
    response = test_client.get("/api/health")
    assert response.status_code == 200
    data: dict[str, Any] = response.json()
    assert data["code"] == 0


# ==================== 认证测试 ====================


def test_auth_without_token(test_client: TestClient) -> None:
    """测试无 Token 访问（可选认证）"""
    response = test_client.post(
        "/api/v1/user/actions",
        json={"action": "list", "params": {"page": 1, "size": 10}},
    )
    assert response.status_code in (401, 403)


def test_auth_with_invalid_token(test_client: TestClient) -> None:
    """测试无效 Token"""
    response = test_client.post(
        "/api/v1/user/actions",
        json={"action": "list", "params": {}},
        headers={"Authorization": "Bearer invalid_token"},
    )
    assert response.status_code in (401, 403)


def test_auth_with_valid_token(
    test_client: TestClient,
    auth_headers: dict[str, str],
) -> None:
    """测试有效 Token"""
    response = test_client.post(
        "/api/v1/user/actions",
        json={"action": "list", "params": {"page": 1, "size": 10}},
        headers=auth_headers,
    )
    assert response.status_code == 200
    data: dict[str, Any] = response.json()
    assert data["code"] == 0


# ==================== 异常处理测试 ====================


def test_validation_error(test_client: TestClient) -> None:
    """测试参数验证失败 - 发送无效JSON"""
    response = test_client.post(
        "/api/v1/user/actions",
        content="invalid json",  # 发送非JSON内容
        headers={"Content-Type": "application/json"},
    )
    assert response.status_code == 422
    data: dict[str, Any] = response.json()
    assert data["code"] != 0  # 错误码不为0


def test_not_found(test_client: TestClient) -> None:
    """测试 404 错误"""
    response = test_client.get("/api/non_existent_endpoint")
    assert response.status_code == 404


# ==================== 统一动作接口测试 ====================


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
    # 成功或参数错误都是正常的（取决于模型是否存在）
    assert data["code"] in [0, 2001, 4001]


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
    assert data["code"] in [0, 2001, 4001]


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
    assert data["code"] in [0, 2001, 4002]


def test_unified_action_invalid(
    test_client: TestClient,
    auth_headers: dict[str, str],
) -> None:
    """测试统一动作接口 - 无效动作"""
    response = test_client.post(
        "/api/v1/user/actions",
        json={"action": "invalid_action", "params": {}},
        headers=auth_headers,
    )
    assert response.status_code == 200
    data: dict[str, Any] = response.json()
    # 应该返回参数错误
    assert data["code"] != 0


# ==================== 数据库操作测试 ====================


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
    user = await db_async_util.fetch_one(session=test_db_session, model=User, filter_by={"id": user_id})

    assert user is not None
    assert user.name == "test"

    # 更新数据
    updated = await db_async_util.update_by_id(
        session=test_db_session,
        model=User,
        id=user_id,
        data={"name": "updated_test"},
    )
    assert updated > 0

    # 验证更新
    user = await db_async_util.fetch_one(session=test_db_session, model=User, filter_by={"id": user_id})
    assert user is not None
    assert user.name == "updated_test"

    # 删除数据
    deleted = await db_async_util.delete_by_id(
        session=test_db_session,
        model=User,
        id=user_id,
    )
    assert deleted > 0

    # 验证删除
    user = await db_async_util.fetch_one(session=test_db_session, model=User, filter_by={"id": user_id})
    assert user is None
