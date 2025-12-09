"""
API 异常定义
"""

from enum import Enum
from typing import Any

# type: ignore 用于模板文件，因为实际路径在生成后的项目中才存在
from app.api.status import Status  # type: ignore


class ErrorCode(Enum):
    """错误码枚举"""

    # 系统错误
    SYSTEM_ERROR = "SYSTEM_ERROR"
    DATABASE_ERROR = "DATABASE_ERROR"
    CACHE_ERROR = "CACHE_ERROR"
    NETWORK_ERROR = "NETWORK_ERROR"

    # 参数错误
    PARAMS_ERROR = "PARAMS_ERROR"
    PARAMS_MISSING = "PARAMS_MISSING"
    PARAMS_INVALID = "PARAMS_INVALID"

    # 认证授权错误
    AUTH_ERROR = "AUTH_ERROR"
    TOKEN_EXPIRED = "TOKEN_EXPIRED"
    TOKEN_INVALID = "TOKEN_INVALID"
    PERMISSION_ERROR = "PERMISSION_ERROR"

    # 业务错误
    BUSINESS_ERROR = "BUSINESS_ERROR"
    RECORD_NOT_EXIST = "RECORD_NOT_EXIST"
    RECORD_EXIST = "RECORD_EXIST"
    OPERATION_FAILED = "OPERATION_FAILED"


class BaseAppError(Exception):
    """API异常基类"""

    status: Status
    msg: str
    data: Any

    def __init__(
        self,
        status: Status = Status.SYSTEM_ERROR,
        msg: str | None = None,
        data: Any = None,
    ):
        """
        初始化API异常

        Args:
            status: 状态码枚举
            msg: 错误消息
            data: 附加数据
        """
        self.status = status
        self.msg = msg or status.message
        self.data = data
        super().__init__(self.msg)


class DatabaseError(BaseAppError):
    """数据库异常"""

    error_code: ErrorCode
    message: str
    cause: Exception | None

    def __init__(
        self,
        error_code: ErrorCode = ErrorCode.DATABASE_ERROR,
        message: str = "数据库操作失败",
        cause: Exception | None = None,
    ):
        self.error_code = error_code
        self.message = message
        self.cause = cause
        super().__init__(status=Status.DATABASE_ERROR, msg=message, data=None)


class ParamsError(BaseAppError):
    """参数异常"""

    def __init__(self, msg: str = "参数错误", data: Any = None):
        super().__init__(status=Status.PARAMS_ERROR, msg=msg, data=data)


class AuthError(BaseAppError):
    """认证异常"""

    def __init__(self, msg: str = "认证失败", data: Any = None):
        super().__init__(status=Status.AUTH_ERROR, msg=msg, data=data)


class PermissionError(BaseAppError):
    """权限异常"""

    def __init__(self, msg: str = "权限不足", data: Any = None):
        super().__init__(status=Status.PERMISSION_ERROR, msg=msg, data=data)


class NotFoundError(BaseAppError):
    """资源不存在异常"""

    def __init__(self, msg: str = "资源不存在", data: Any = None):
        super().__init__(status=Status.RECORD_NOT_EXIST_ERROR, msg=msg, data=data)


class BusinessError(BaseAppError):
    """业务异常"""

    def __init__(self, msg: str = "业务错误", data: Any = None):
        super().__init__(status=Status.BUSINESS_ERROR, msg=msg, data=data)


# 向后兼容别名
APIException = BaseAppError
ParamsException = ParamsError
AuthException = AuthError
PermissionException = PermissionError
BusinessException = BusinessError
DatabaseException = DatabaseError
