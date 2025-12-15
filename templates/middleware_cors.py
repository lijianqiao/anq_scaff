"""
CORS 中间件
"""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.initializer._settings import settings


def setup_cors(app: FastAPI) -> None:
    """
    设置 CORS 中间件

    Args:
        app: FastAPI应用实例
    """
    # 从配置读取
    app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.cors_allow_origins,
        allow_credentials=settings.cors_allow_credentials,
        allow_methods=settings.cors_allow_methods,
        allow_headers=settings.cors_allow_headers,
    )
