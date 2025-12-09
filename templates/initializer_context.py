"""
上下文变量
使用 contextvars 实现请求级别的上下文传递
"""

from contextvars import ContextVar

# 请求ID上下文变量
request_id_var: ContextVar[str] = ContextVar("request_id", default="N/A")

# 用户ID上下文变量
user_id_var: ContextVar[str | None] = ContextVar("user_id", default=None)

# 租户ID上下文变量（多租户支持）
tenant_id_var: ContextVar[str | None] = ContextVar("tenant_id", default=None)


def set_request_context(
    request_id: str,
    user_id: str | None = None,
    tenant_id: str | None = None,
) -> None:
    """
    设置请求上下文

    Args:
        request_id: 请求ID
        user_id: 用户ID
        tenant_id: 租户ID
    """
    _ = request_id_var.set(request_id)
    if user_id:
        _ = user_id_var.set(user_id)
    if tenant_id:
        _ = tenant_id_var.set(tenant_id)


def clear_request_context() -> None:
    """清除请求上下文"""
    _ = request_id_var.set("N/A")
    _ = user_id_var.set(None)
    _ = tenant_id_var.set(None)


def get_request_id() -> str:
    """获取当前请求ID"""
    return request_id_var.get()


def get_user_id() -> str | None:
    """获取当前用户ID"""
    return user_id_var.get()


def get_tenant_id() -> str | None:
    """获取当前租户ID"""
    return tenant_id_var.get()
