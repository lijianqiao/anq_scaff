"""
数据模型层

所有模型类都应继承自 Base

重要：新增模型后，请在此处导入以确保表能被自动创建
示例：
    from app.models.user import User
    from app.models.product import Product
"""

from app.initializer._db import Base

# 在此处导入所有模型
# from app.models.xxx import Xxx

# 导出
__all__ = ["Base"]
