"""
健康检查接口
"""

from typing import Any

from fastapi import APIRouter

from app.api.responses import Responses

router = APIRouter()
_active = True
_tag = "健康检查"


@router.get("/ping")
async def ping() -> dict[str, Any]:
    """
    健康检查

    Returns:
        pong响应
    """
    return Responses.success(data={"message": "pong"})


@router.get("/health")
async def health() -> dict[str, Any]:
    """
    健康状态检查

    Returns:
        健康状态
    """
    return Responses.success(
        data={
            "status": "healthy",
            "version": "1.0.0",
        }
    )
