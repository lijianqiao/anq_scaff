"""
日志初始化
支持多级别日志分离：info.log, error.log, api_traffic.log
支持上下文感知：自动注入 request_id 和 user_id
"""

import sys
from pathlib import Path
from typing import Any

from loguru import logger

# 尝试导入上下文变量（可能还未初始化）
try:
    from app.initializer.context import request_id_var, user_id_var  # type: ignore
except ImportError:
    request_id_var = None
    user_id_var = None


def _context_filter(record: dict[str, Any]) -> bool:
    """
    上下文过滤器
    为日志记录添加 request_id 和 user_id

    Args:
        record: 日志记录

    Returns:
        始终返回 True（不过滤任何记录）
    """
    # 注入 request_id
    if request_id_var is not None:
        record["extra"]["request_id"] = request_id_var.get("-")
    else:
        record["extra"]["request_id"] = "-"

    # 注入 user_id
    if user_id_var is not None:
        record["extra"]["user_id"] = user_id_var.get("-")
    else:
        record["extra"]["user_id"] = "-"

    return True


def init_logger(
    level: str = "INFO",
    serialize: bool = False,
    basedir: str = "./logs",
    enable_console: bool = True,
    enable_file: bool = True,
) -> "logger":  # type: ignore[name-defined]
    """
    初始化日志系统

    Args:
        level: 日志级别
        serialize: 是否序列化为JSON格式
        basedir: 日志文件目录
        enable_console: 是否启用控制台日志
        enable_file: 是否启用文件日志

    Returns:
        配置好的logger实例
    """
    # 确保日志目录存在
    Path(basedir).mkdir(parents=True, exist_ok=True)

    # 移除默认处理器
    logger.remove()

    # 控制台输出格式（包含上下文）
    console_format = (
        "<green>{time:YYYY-MM-DD HH:mm:ss}</green> | "
        "<level>{level: <8}</level> | "
        "<cyan>[{extra[request_id]}]</cyan> | "
        "<cyan>{name}</cyan>:<cyan>{function}</cyan>:<cyan>{line}</cyan> | "
        "<level>{message}</level>"
    )

    # 文件输出格式（包含上下文）
    file_format = (
        "{time:YYYY-MM-DD HH:mm:ss} | {level: <8} | "
        "[{extra[request_id]}] [{extra[user_id]}] | "
        "{name}:{function}:{line} | {message}"
    )

    # API 流量日志格式（结构化）
    api_format = (
        "{time:YYYY-MM-DD HH:mm:ss} | {level: <8} | "
        "[{extra[request_id]}] | {extra[method]} {extra[path]} | "
        "{extra[status_code]} | {extra[process_time]}ms | {message}"
    )

    # 添加控制台处理器
    if enable_console:
        logger.add(
            sys.stdout,
            format=console_format,
            level=level,
            colorize=True,
            serialize=serialize,
            filter=_context_filter,  # type: ignore[arg-type]
        )

    if enable_file:
        # 添加信息日志文件处理器（DEBUG 和 INFO）
        logger.add(
            f"{basedir}/info_{{time:YYYYMMDD}}.log",
            format=file_format,
            level="DEBUG",
            rotation="00:00",
            retention="30 days",
            compression="zip",
            filter=lambda record: _context_filter(record) and record["level"].no <= 20,  # type: ignore[arg-type]
            serialize=serialize,
        )

        # 添加错误日志文件处理器（WARNING 及以上）
        logger.add(
            f"{basedir}/error_{{time:YYYYMMDD}}.log",
            format=file_format,
            level="WARNING",
            rotation="00:00",
            retention="90 days",
            compression="zip",
            filter=_context_filter,  # type: ignore[arg-type]
            serialize=serialize,
        )

        # 添加 API 流量日志文件处理器
        logger.add(
            f"{basedir}/api_traffic_{{time:YYYYMMDD}}.log",
            format=api_format,
            level="INFO",
            rotation="00:00",
            retention="7 days",
            compression="zip",
            filter=lambda record: record["extra"].get("log_type") == "api_traffic",
            serialize=serialize,
        )

    return logger


def log_api_traffic(
    request_id: str,
    method: str,
    path: str,
    status_code: int,
    process_time: float,
    message: str = "",
) -> None:
    """
    记录 API 流量日志

    Args:
        request_id: 请求ID
        method: HTTP 方法
        path: 请求路径
        status_code: 响应状态码
        process_time: 处理时间（毫秒）
        message: 附加消息
    """
    logger.bind(
        log_type="api_traffic",
        request_id=request_id,
        method=method,
        path=path,
        status_code=status_code,
        process_time=f"{process_time:.2f}",
    ).info(message or "API Request")
