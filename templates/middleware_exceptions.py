"""
异常处理中间件
提供全局异常处理器，实现分层异常处理
"""

# type: ignore 用于模板文件
from fastapi import HTTPException, Request
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
from loguru import logger

from app.api.exceptions import BaseAppError
from app.api.responses import Responses
from app.api.status import Status
from app.initializer.context import request_id_var


async def exception_handler(request: Request, exc: Exception) -> JSONResponse:
    """
    全局异常处理器

    处理所有未被捕获的异常，包括：
    - BaseAppError: 业务异常，返回具体错误码
    - Exception: 未知异常，返回系统错误

    Args:
        request: 请求对象
        exc: 异常对象

    Returns:
        JSON响应
    """
    _ = request  # unused
    request_id = request_id_var.get("N/A")

    # 处理业务异常（BaseAppError）
    if isinstance(exc, BaseAppError):
        logger.warning(f"[{request_id}] 业务异常: {type(exc).__name__}: code={exc.status.value}, msg={exc.msg}")
        return JSONResponse(
            status_code=200,  # 业务异常返回200，错误码在响应体中
            content=Responses.failure(
                status=exc.status,
                msg=exc.msg,
                data=exc.data,
            ),
        )

    # 处理 HTTPException（保持原始状态码）
    if isinstance(exc, HTTPException):
        logger.warning(f"[{request_id}] HTTP异常: {type(exc).__name__}: status={exc.status_code}, detail={exc.detail}")
        return JSONResponse(
            status_code=exc.status_code,
            content=Responses.failure(status=Status.AUTH_ERROR, msg=str(exc.detail)),
        )

    # 处理未知异常
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
    exc: RequestValidationError,
) -> JSONResponse:
    """
    验证异常处理器

    处理 Pydantic 验证异常，返回友好的错误信息

    Args:
        request: 请求对象
        exc: 验证异常对象

    Returns:
        JSON响应
    """
    _ = request  # unused
    request_id = request_id_var.get("N/A")

    # 提取验证错误详情
    errors = exc.errors()
    error_details = []
    for error in errors:
        field = ".".join(str(loc) for loc in error.get("loc", []))
        msg = error.get("msg", "")
        error_details.append({"field": field, "message": msg})

    logger.warning(f"[{request_id}] 参数验证失败: {error_details}")

    return JSONResponse(
        status_code=422,
        content=Responses.failure(
            status=Status.PARAMS_ERROR,
            msg="参数验证失败",
            data={"errors": error_details},
        ),
    )
