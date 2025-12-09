"""
统一异常出口（保持与 api_exceptions 一致）
"""

from fastapi import Request
from fastapi.responses import JSONResponse
from loguru import logger

from app.api.exceptions import BaseAppError
from app.api.responses import Responses
from app.api.status import Status
from app.initializer.context import request_id_var


async def global_exception_handler(request: Request, exc: Exception) -> JSONResponse:
    """全局异常处理器（与 middleware_exceptions 语义一致）"""
    request_id = request_id_var.get("N/A")
    logger.exception(f"[{request_id}] 异常: {type(exc).__name__}: {exc}")

    if isinstance(exc, BaseAppError):
        return JSONResponse(
            status_code=200,
            content=Responses.failure(status=exc.status, msg=exc.msg, data=exc.data),
        )

    return JSONResponse(
        status_code=500,
        content=Responses.failure(status=Status.SYSTEM_ERROR, msg="系统内部错误"),
    )
