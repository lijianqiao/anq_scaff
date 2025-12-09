"""
数据模型层

所有模型类都应继承自 Base
模型会在此处被自动发现并导入，确保表能被自动创建
"""

import importlib
import pkgutil
from pathlib import Path

from loguru import logger

from app.initializer._db import Base

# 自动发现并导入所有模型
_models_dir = Path(__file__).parent


def _auto_import_models() -> list[str]:
    """
    自动导入 models 目录下的所有模型

    Returns:
        导入的模块名列表
    """
    imported: list[str] = []

    for module_info in pkgutil.iter_modules([str(_models_dir)]):
        # 跳过 __init__ 和私有模块
        if module_info.name.startswith("_"):
            continue

        module_name = f"app.models.{module_info.name}"
        try:
            importlib.import_module(module_name)
            imported.append(module_name)
            logger.debug(f"自动导入模型: {module_name}")
        except Exception as e:
            logger.warning(f"导入模型失败: {module_name}, 错误: {e}")

    return imported


# 执行自动导入
_imported_models = _auto_import_models()

# 导出
__all__ = ["Base"]
