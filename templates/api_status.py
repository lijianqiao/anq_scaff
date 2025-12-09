"""
API 状态码定义
"""

from enum import Enum
from typing import override


class Status(Enum):
    """状态码枚举"""

    # 成功
    SUCCESS = (0, "操作成功")

    # 系统错误 (1xxx)
    SYSTEM_ERROR = (1000, "系统错误")
    DATABASE_ERROR = (1001, "数据库错误")
    CACHE_ERROR = (1002, "缓存错误")
    NETWORK_ERROR = (1003, "网络错误")

    # 参数错误 (2xxx)
    PARAMS_ERROR = (2000, "参数错误")
    PARAMS_MISSING = (2001, "缺少必要参数")
    PARAMS_INVALID = (2002, "参数格式无效")

    # 认证授权错误 (3xxx)
    AUTH_ERROR = (3000, "认证失败")
    TOKEN_EXPIRED = (3001, "Token已过期")
    TOKEN_INVALID = (3002, "Token无效")
    PERMISSION_ERROR = (3003, "权限不足")

    # 业务错误 (4xxx)
    BUSINESS_ERROR = (4000, "业务错误")
    RECORD_NOT_EXIST_ERROR = (4001, "记录不存在")
    RECORD_EXIST_ERROR = (4002, "记录已存在")
    OPERATION_FAILED = (4003, "操作失败")

    def __init__(self, code: int, message: str):
        self._code = code
        self._message = message

    @property
    @override
    def value(self) -> int:
        """获取状态码"""
        return self._code

    @property
    def message(self) -> str:
        """获取状态消息"""
        return self._message
