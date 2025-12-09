"""
HTTP 中间件
处理请求ID生成、上下文注入、请求日志等
"""

import time
import uuid
from collections.abc import Awaitable, Callable
from typing import override

from fastapi import Request, Response
from loguru import logger
from starlette.middleware.base import BaseHTTPMiddleware

from app.initializer._log import log_api_traffic  # type: ignore
from app.initializer.context import clear_request_context, set_request_context  # type: ignore


class HTTPMiddleware(BaseHTTPMiddleware):
    """HTTP中间件"""

    @override
    async def dispatch(
        self,
        request: Request,
        call_next: Callable[[Request], Awaitable[Response]],
    ) -> Response:
        """
        处理请求

        Args:
            request: 请求对象
            call_next: 下一个处理函数

        Returns:
            响应对象
        """
        # 生成或获取请求ID
        request_id = request.headers.get("X-Request-ID", str(uuid.uuid4()))

        # 设置请求上下文
        set_request_context(request_id=request_id)

        # 记录请求开始时间
        start_time = time.time()

        # 记录请求日志
        logger.info(f"[{request_id}] 请求开始: {request.method} {request.url.path}")

        try:
            # 处理请求
            response = await call_next(request)

            # 计算处理时间（毫秒）
            process_time = (time.time() - start_time) * 1000

            # 添加响应头
            response.headers["X-Request-ID"] = request_id
            response.headers["X-Process-Time"] = f"{process_time:.3f}"

            # 记录响应日志
            logger.info(
                f"[{request_id}] 请求完成: {request.method} {request.url.path} "
                f"- {response.status_code} - {process_time:.2f}ms"
            )

            # 记录 API 流量日志（单独文件）
            log_api_traffic(
                request_id=request_id,
                method=request.method,
                path=request.url.path,
                status_code=response.status_code,
                process_time=process_time,
            )

            return response

        except Exception as e:
            # 计算处理时间（毫秒）
            process_time = (time.time() - start_time) * 1000

            # 记录异常日志
            logger.exception(
                f"[{request_id}] 请求异常: {request.method} {request.url.path} "
                f"- {process_time:.2f}ms - {type(e).__name__}: {e}"
            )

            # 记录 API 流量日志（异常）
            log_api_traffic(
                request_id=request_id,
                method=request.method,
                path=request.url.path,
                status_code=500,
                process_time=process_time,
                message=f"Error: {type(e).__name__}",
            )

            raise

        finally:
            # 清除请求上下文
            clear_request_context()
