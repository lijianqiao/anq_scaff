"""
分层异常处理系统
错误码 -> 自定义异常 -> 全局异常处理器
"""

from enum import Enum
from typing import Any

from fastapi import Request
from fastapi.responses import JSONResponse
from loguru import logger


class ErrorCode(Enum):
    """错误码枚举"""

    # 系统级错误 (1xxx)
    SYSTEM_ERROR = (1000, "系统错误")
    DATABASE_ERROR = (1001, "数据库错误")
    CACHE_ERROR = (1002, "缓存错误")
    NETWORK_ERROR = (1003, "网络错误")

    # 业务级错误 (2xxx)
    BUSINESS_ERROR = (2000, "业务错误")
    VALIDATION_ERROR = (2001, "验证错误")
    PERMISSION_DENIED = (2002, "权限不足")
    RESOURCE_NOT_FOUND = (2003, "资源不存在")
    RESOURCE_EXISTS = (2004, "资源已存在")

    # 认证授权错误 (3xxx)
    UNAUTHORIZED = (3000, "未授权")
    TOKEN_EXPIRED = (3001, "Token已过期")
    TOKEN_INVALID = (3002, "Token无效")

    @property
    def code(self) -> int:
        return self.value[0]

    @property
    def message(self) -> str:
        return self.value[1]


class BaseAppError(Exception):
    """基础应用异常"""

    def __init__(
        self,
        error_code: ErrorCode,
        message: str | None = None,
        details: dict[str, Any] | None = None,
        cause: Exception | None = None,
    ):
        self.error_code = error_code
        self.message = message or error_code.message
        self.details = details or {}
        self.cause = cause
        super().__init__(self.message)


class BusinessError(BaseAppError):
    """业务异常"""

    pass


class ValidationError(BaseAppError):
    """验证异常"""

    pass


class DatabaseError(BaseAppError):
    """数据库异常"""

    pass


class AuthenticationError(BaseAppError):
    """认证异常"""

    pass


# 向后兼容别名
BaseAppException = BaseAppError
BusinessException = BusinessError
ValidationException = ValidationError
DatabaseException = DatabaseError
AuthenticationException = AuthenticationError


async def global_exception_handler(request: Request, exc: Exception) -> JSONResponse:
    """全局异常处理器"""
    from app.api.responses import Responses
    from app.initializer.context import request_id_var

    # 记录异常
    request_id = request_id_var.get("N/A")
    logger.exception(f"[{request_id}] 异常: {type(exc).__name__}: {exc}", exc_info=exc)

    # 处理已知异常
    if isinstance(exc, BaseAppError):
        return JSONResponse(
            status_code=200,
            content=Responses.failure(
                code=exc.error_code.code,
                msg=exc.message,
                data=exc.details,
            ),
        )

    # 处理未知异常
    return JSONResponse(
        status_code=500,
        content=Responses.failure(
            code=ErrorCode.SYSTEM_ERROR.code,
            msg="系统内部错误",
            error=str(exc) if request.app.debug else None,
        ),
    )
