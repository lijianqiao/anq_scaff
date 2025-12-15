"""
API 路由注册
自动发现并注册 API 路由
"""

import importlib
import pkgutil
from pathlib import Path

from fastapi import APIRouter
from loguru import logger

# 主路由
api_router = APIRouter()


def _register_routers() -> None:
    """自动注册API路由"""
    # 获取当前目录
    api_dir = Path(__file__).parent

    # 注册默认路由
    default_dir = api_dir / "default"
    if default_dir.exists():
        _register_from_directory(default_dir, prefix="")

    # 注册版本化路由 (v1, v2, ...)
    for version_dir in api_dir.iterdir():
        if version_dir.is_dir() and version_dir.name.startswith("v"):
            _register_from_directory(version_dir, prefix=f"/{version_dir.name}")

    # 注册统一 RESTful 路由（可选）
    _register_unified_router()


def _register_from_directory(directory: Path, prefix: str) -> None:
    """
    从目录注册路由

    Args:
        directory: 目录路径
        prefix: 路由前缀
    """
    for module_info in pkgutil.iter_modules([str(directory)]):
        if module_info.name.startswith("_"):
            continue

        # 构建模块路径
        module_path = f"app.api.{directory.name}.{module_info.name}"

        try:
            module = importlib.import_module(module_path)

            # 获取路由器
            router = getattr(module, "router", None)
            if router and isinstance(router, APIRouter):
                # 检查是否激活
                is_active = getattr(module, "_active", True)
                if not is_active:
                    logger.debug(f"跳过未激活的路由: {module_path}")
                    continue

                # 获取标签
                tag = getattr(module, "_tag", module_info.name)

                # 注册路由
                api_router.include_router(router, prefix=prefix, tags=[tag])
                logger.debug(f"注册路由: {module_path} -> {prefix}")

        except Exception as e:
            logger.error(f"注册路由失败: {module_path}, 错误: {e}")


def _register_unified_router() -> None:
    """
    注册统一 RESTful 路由

    提供 /{resource} 的通用 RESTful 入口
    """
    try:
        from app.api.unified_router import router as unified_router  # type: ignore

        # 注册到 /v1 版本下
        api_router.include_router(
            unified_router,
            prefix="/v1",
            tags=["unified"],
        )
        logger.debug("注册统一 RESTful 路由: /v1/{resource}")
    except ImportError:
        logger.debug("统一动作路由未找到，跳过注册")
    except Exception as e:
        logger.warning(f"注册统一动作路由失败: {e}")


# 自动注册路由
_register_routers()
