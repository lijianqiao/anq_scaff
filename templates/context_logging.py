"""
上下文感知日志系统
利用 contextvars 自动注入 request_id 和 user_id
"""

import sys
from pathlib import Path
from typing import Any

from loguru import logger

# type: ignore 用于模板文件
from app.initializer.context import request_id_var, user_id_var  # type: ignore


def _context_filter(record: Any) -> bool:
    """
    过滤器函数：为每条日志记录注入上下文信息
    """
    record["extra"]["request_id"] = request_id_var.get()
    record["extra"]["user_id"] = user_id_var.get() or "anonymous"
    return True


def setup_context_logging(
    level: str = "INFO",
    log_dir: str = "./logs",
    enable_console: bool = True,
    enable_file: bool = True,
) -> None:
    """
    设置上下文感知日志

    Args:
        level: 日志级别
        log_dir: 日志目录
        enable_console: 是否启用控制台输出
        enable_file: 是否启用文件输出
    """
    # 确保日志目录存在
    Path(log_dir).mkdir(parents=True, exist_ok=True)

    # 移除默认处理器
    logger.remove()

    # 控制台输出格式（包含 request_id 和 user_id）
    console_format = (
        "<green>{time:YYYY-MM-DD HH:mm:ss}</green> | "
        "<level>{level: <8}</level> | "
        "<cyan>req_id={extra[request_id]}</cyan> | "
        "<cyan>user_id={extra[user_id]}</cyan> | "
        "<cyan>{name}</cyan>:<cyan>{function}</cyan>:<cyan>{line}</cyan> | "
        "<level>{message}</level>"
    )

    file_format = (
        "{time:YYYY-MM-DD HH:mm:ss} | {level: <8} | "
        "req_id={extra[request_id]} | user_id={extra[user_id]} | "
        "{name}:{function}:{line} | {message}"
    )

    if enable_console:
        _ = logger.add(
            sys.stdout,
            format=console_format,
            level=level,
            colorize=True,
            filter=_context_filter,  # type: ignore[arg-type]
        )

    if enable_file:
        # 信息日志（INFO 及以下级别）
        _ = logger.add(
            f"{log_dir}/info.log",
            format=file_format,
            level="DEBUG",
            rotation="100 MB",
            retention="30 days",
            compression="zip",
            filter=lambda record: (
                _context_filter(record) and record["level"].no <= 20
            ),  # type: ignore[arg-type]
        )

        # 错误日志（WARNING 及以上级别）
        _ = logger.add(
            f"{log_dir}/error.log",
            format=file_format,
            level="WARNING",
            rotation="100 MB",
            retention="90 days",
            compression="zip",
            filter=_context_filter,  # type: ignore[arg-type]
        )

        # API 流量日志
        _ = logger.add(
            f"{log_dir}/api_traffic.log",
            format="{time:YYYY-MM-DD HH:mm:ss} | {message}",
            level="INFO",
            rotation="500 MB",
            retention="7 days",
            filter=lambda record: record.get("extra", {}).get(
                "api_traffic", False
            ),  # type: ignore[arg-type]
        )


def get_context_logger() -> Any:
    """
    获取带上下文的日志器

    使用示例:
        log = get_context_logger()
        log.info("用户操作")  # 自动包含 request_id 和 user_id
    """
    return logger.bind(
        request_id=request_id_var.get(),
        user_id=user_id_var.get() or "anonymous",
    )


def log_api_traffic(message: str) -> None:
    """记录 API 流量日志"""
    logger.bind(api_traffic=True).info(message)
