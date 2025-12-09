"""
统一响应封装
"""

from typing import Any

# type: ignore 用于模板文件，因为实际路径在生成后的项目中才存在
from app.api.status import Status  # type: ignore


class Responses:
    """统一响应类"""

    @staticmethod
    def success(data: Any = None, msg: str | None = None) -> dict[str, Any]:
        """成功响应"""
        return {
            "code": Status.SUCCESS.value,
            "msg": msg or Status.SUCCESS.message,
            "data": data,
        }

    @staticmethod
    def failure(
        status: Status = Status.PARAMS_ERROR,
        msg: str | None = None,
        data: Any = None,
        error: Any = None,
        code: int | None = None,
    ) -> dict[str, Any]:
        """失败响应"""
        return {
            "code": code if code is not None else status.value,
            "msg": msg or status.message,
            "data": data,
            "error": error,
        }
