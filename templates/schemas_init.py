"""
数据验证层 (Pydantic Schemas)

所有Schema类都应继承自 BaseModel
"""

from typing import TypeVar

from pydantic import BaseModel, ConfigDict


class BaseSchema(BaseModel):
    """基础Schema"""

    model_config = ConfigDict(
        from_attributes=True,
        populate_by_name=True,
    )


DataT = TypeVar("DataT")


class PageRequest(BaseModel):
    """分页请求"""

    page: int = 1
    size: int = 10


class PageResponse[DataT](BaseModel):
    """分页响应"""

    items: list[DataT]
    total: int
    page: int
    size: int
    pages: int

    @classmethod
    def create(
        cls,
        items: list[DataT],
        total: int,
        page: int,
        size: int,
    ) -> "PageResponse[DataT]":
        """创建分页响应"""
        pages = (total + size - 1) // size if size > 0 else 0
        return cls(
            items=items,
            total=total,
            page=page,
            size=size,
            pages=pages,
        )


# 导出
__all__ = ["BaseSchema", "PageRequest", "PageResponse"]
