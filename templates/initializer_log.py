"""
日志初始化
支持多级别日志分离：info.log, error.log, api_traffic.log
"""

import sys
from pathlib import Path

from loguru import logger


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

    # 控制台输出格式
    console_format = (
        "<green>{time:YYYY-MM-DD HH:mm:ss}</green> | "
        "<level>{level: <8}</level> | "
        "<cyan>{name}</cyan>:<cyan>{function}</cyan>:<cyan>{line}</cyan> | "
        "<level>{message}</level>"
    )

    # 文件输出格式
    file_format = (
        "{time:YYYY-MM-DD HH:mm:ss} | {level: <8} | "
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
        )

    if enable_file:
        # 添加信息日志文件处理器（DEBUG 和 INFO）
        logger.add(
            f"{basedir}/info.log",
            format=file_format,
            level="DEBUG",
            rotation="100 MB",
            retention="30 days",
            compression="zip",
            filter=lambda record: record["level"].no <= 20,  # INFO = 20
            serialize=serialize,
        )

        # 添加错误日志文件处理器（WARNING 及以上）
        logger.add(
            f"{basedir}/error.log",
            format=file_format,
            level="WARNING",
            rotation="100 MB",
            retention="90 days",
            compression="zip",
            serialize=serialize,
        )

        # 添加 API 流量日志文件处理器
        logger.add(
            f"{basedir}/api_traffic.log",
            format=api_format,
            level="INFO",
            rotation="100 MB",
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
