"""
CORS 中间件
"""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware


def setup_cors(app: FastAPI) -> None:
    """
    设置 CORS 中间件

    Args:
        app: FastAPI应用实例
    """
    # 默认配置，可根据需要修改
    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],  # 生产环境应限制为具体域名
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )
