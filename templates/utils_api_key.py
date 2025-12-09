"""
API Key 工具模块
从配置读取前缀和长度，遵循配置与代码分离原则
"""

import hashlib
import secrets

# type: ignore 用于模板文件
from app.initializer._settings import settings  # type: ignore


def generate_api_key() -> str:
    """
    生成新的 API Key

    Returns:
        API Key 字符串
    """
    random_bytes = secrets.token_hex(settings.api_key_length // 2)
    return f"{settings.api_key_prefix}{random_bytes}"


def hash_api_key(api_key: str) -> str:
    """
    对 API Key 进行哈希

    Args:
        api_key: API Key 字符串

    Returns:
        哈希后的字符串
    """
    return hashlib.sha256(api_key.encode()).hexdigest()


def verify_api_key(api_key: str, hashed_key: str) -> bool:
    """
    验证 API Key（与哈希值比较）

    Args:
        api_key: 原始 API Key
        hashed_key: 存储的哈希值

    Returns:
        是否验证通过
    """
    return hash_api_key(api_key) == hashed_key


def is_valid_api_key(api_key: str) -> bool:
    """
    验证 API Key 是否在配置的有效列表中

    Args:
        api_key: API Key 字符串

    Returns:
        是否有效
    """
    if not api_key:
        return False

    # 检查是否在配置的有效 API Keys 列表中
    return api_key in settings.api_keys


def is_valid_api_key_format(api_key: str) -> bool:
    """
    检查 API Key 格式是否正确

    Args:
        api_key: API Key 字符串

    Returns:
        格式是否正确
    """
    if not api_key:
        return False

    if not api_key.startswith(settings.api_key_prefix):
        return False

    # 检查长度
    expected_length = len(settings.api_key_prefix) + settings.api_key_length
    if len(api_key) != expected_length:
        return False

    # 检查是否只包含合法字符
    key_part = api_key[len(settings.api_key_prefix) :]
    try:
        int(key_part, 16)
    except ValueError:
        return False
    return True
