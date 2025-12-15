"""
FastAPI 应用入口
"""

from fastapi import FastAPI
from fastapi.exceptions import HTTPException, RequestValidationError

from app.api import api_router
from app.api.exceptions import BaseAppError
from app.core.lifespan import lifespan
from app.initializer._settings import settings
from app.middleware import setup_middleware
from app.middleware.exceptions import (
    exception_handler,
    validation_exception_handler,
)


# 创建 FastAPI 应用实例
app = FastAPI(
    title=settings.app_name,
    description=settings.app_description,
    version=settings.app_version,
    lifespan=lifespan,
)

# 注册全局异常处理器
app.add_exception_handler(BaseAppError, exception_handler)  # type: ignore[arg-type]
app.add_exception_handler(RequestValidationError, validation_exception_handler)  # type: ignore[arg-type]
app.add_exception_handler(HTTPException, exception_handler)  # 保持HTTP状态码
app.add_exception_handler(Exception, exception_handler)  # type: ignore[arg-type]

# 设置中间件
setup_middleware(app)

# 注册路由
app.include_router(api_router, prefix="/api")
