"""
中间件模块
"""

from fastapi import FastAPI

from app.middleware.cors import setup_cors
from app.middleware.http import HTTPMiddleware


def setup_middleware(app: FastAPI) -> None:
    """
    设置所有中间件

    Args:
        app: FastAPI应用实例
    """
    # 设置CORS
    setup_cors(app)

    # 添加HTTP中间件（请求ID、异常处理等）
    app.add_middleware(HTTPMiddleware)
