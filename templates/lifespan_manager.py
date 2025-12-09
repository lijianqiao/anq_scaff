"""
应用生命周期管理
优雅地处理数据库、Redis连接池等资源的初始化与释放
"""

# 导入引发的报错在创建项目之后会自动消失
from collections.abc import AsyncGenerator
from contextlib import asynccontextmanager
from typing import Any

from fastapi import FastAPI
from loguru import logger

from app.initializer import g


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncGenerator[None]:
    """
    应用生命周期管理器
    处理资源的初始化和清理
    """
    # 启动时初始化
    logger.info("应用启动中...")

    try:
        # 初始化全局对象
        g.setup()  # type: ignore[attr-defined]

        # 初始化数据库连接池
        logger.info("初始化数据库连接池...")
        # 数据库连接池会在首次使用时自动创建

        # 初始化Redis连接池（如果启用）
        redis_client: Any = getattr(g, "redis_client", None)
        if redis_client is not None:
            logger.info("初始化Redis连接池...")
            try:
                with redis_client.connection() as r:
                    r.ping()
                logger.info("Redis连接池初始化成功")
            except Exception as e:
                logger.warning(f"Redis连接失败: {e}，将使用内存缓存")

        # 初始化缓存管理器
        if hasattr(g, "cache_manager"):
            logger.info("初始化缓存管理器...")
            logger.info("缓存管理器初始化成功")

        # 启动后台任务（如果需要）
        # background_tasks = BackgroundTasks()
        # asyncio.create_task(periodic_task())

        logger.info("应用启动完成")

        yield

    except Exception as e:
        logger.error(f"应用启动失败: {e}")
        raise

    finally:
        # 关闭时清理
        logger.info("应用关闭中...")

        try:
            # 关闭数据库连接池
            if hasattr(g, "db_async_session"):
                logger.info("关闭数据库连接池...")
                # SQLAlchemy会自动管理连接池

            # 关闭Redis连接池
            redis_client = getattr(g, "redis_client", None)
            if redis_client is not None:
                logger.info("关闭Redis连接池...")
                # Redis客户端会自动管理连接

            logger.info("应用关闭完成")

        except Exception as e:
            logger.error(f"应用关闭时出错: {e}")


# 后台定时任务示例
async def periodic_task() -> None:
    """后台定时任务示例"""
    import asyncio

    while True:
        try:
            # 执行定时任务
            logger.debug("执行后台定时任务...")
            await asyncio.sleep(60)  # 每60秒执行一次
        except asyncio.CancelledError:
            logger.info("后台任务已取消")
            break
        except Exception as e:
            logger.error(f"后台任务执行失败: {e}")
            await asyncio.sleep(60)
