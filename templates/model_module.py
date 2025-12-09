"""
数据模型 - ${ModuleName}
"""

from datetime import datetime
from typing import Any

from sqlalchemy import Column, DateTime, Integer, String, Text
from sqlalchemy.sql import func

# 重要：从项目的 Base 导入，确保模型注册到同一个元数据中
from app.initializer._db import Base


class ${ModuleName}(Base):
    """${ModuleName} 数据模型"""

    __tablename__ = "${module_name}"

    # 主键ID (使用雪花ID，字符串类型)
    id = Column(String(32), primary_key=True, comment="主键ID")

    # 业务字段 - 请根据实际需求修改
    name = Column(String(100), nullable=False, comment="名称")
    description = Column(Text, nullable=True, comment="描述")
    status = Column(Integer, default=1, comment="状态: 1-启用, 0-禁用")

    # 时间戳
    created_at = Column(
        DateTime, default=func.now(), server_default=func.now(), comment="创建时间"
    )
    updated_at = Column(
        DateTime,
        default=func.now(),
        onupdate=func.now(),
        server_default=func.now(),
        comment="更新时间",
    )

    def to_dict(self) -> dict[str, Any]:
        """转换为字典"""
        created = self.created_at
        updated = self.updated_at
        return {
            "id": self.id,
            "name": self.name,
            "description": self.description,
            "status": self.status,
            "created_at": created.isoformat() if isinstance(created, datetime) else None,
            "updated_at": updated.isoformat() if isinstance(updated, datetime) else None,
        }

    def __repr__(self) -> str:
        return f"<${ModuleName}(id={self.id}, name={self.name})>"
