"""
异常处理中间件
"""

from typing import Any

from fastapi import Request
from fastapi.responses import JSONResponse
from loguru import logger

# type: ignore 用于模板文件
from app.api.responses import Responses  # type: ignore
from app.api.status import Status  # type: ignore
from app.initializer.context import request_id_var  # type: ignore


async def exception_handler(request: Request, exc: Exception) -> JSONResponse:
    """
    全局异常处理器

    Args:
        request: 请求对象
        exc: 异常对象

    Returns:
        JSON响应
    """
    _ = request  # unused
    request_id = request_id_var.get("N/A")

    # 记录异常日志
    logger.exception(f"[{request_id}] 未处理的异常: {type(exc).__name__}: {exc}")

    # 返回统一的错误响应
    return JSONResponse(
        status_code=500,
        content=Responses.failure(
            status=Status.SYSTEM_ERROR,
            msg="系统内部错误",
        ),
    )


async def validation_exception_handler(
    request: Request,
    exc: Any,
) -> JSONResponse:
    """
    验证异常处理器

    Args:
        request: 请求对象
        exc: 验证异常对象

    Returns:
        JSON响应
    """
    _ = request  # unused
    request_id = request_id_var.get("N/A")

    logger.warning(f"[{request_id}] 参数验证失败: {exc}")

    return JSONResponse(
        status_code=422,
        content=Responses.failure(
            status=Status.PARAMS_ERROR,
            msg="参数验证失败",
            data={"detail": str(exc)},
        ),
    )
