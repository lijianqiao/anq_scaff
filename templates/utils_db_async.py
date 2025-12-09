"""
异步数据库工具模块
"""

from typing import Any

from sqlalchemy import delete, func, select, update
from sqlalchemy.ext.asyncio import AsyncSession


async def fetch_one(
    session: AsyncSession,
    model: Any,
    filter_by: dict[str, Any] | None = None,
) -> Any | None:
    """
    查询单条记录

    Args:
        session: 数据库会话
        model: 模型类
        filter_by: 过滤条件

    Returns:
        模型实例或None
    """
    stmt = select(model)

    if filter_by:
        for key, value in filter_by.items():
            if hasattr(model, key):
                stmt = stmt.where(getattr(model, key) == value)

    result = await session.execute(stmt)
    return result.scalar_one_or_none()


async def fetch_all(
    session: AsyncSession,
    model: Any,
    page: int = 1,
    size: int = 10,
    filter_by: dict[str, Any] | None = None,
    order_by: str | None = None,
    order_desc: bool = False,
) -> tuple[list[Any], int]:
    """
    查询列表（分页）

    Args:
        session: 数据库会话
        model: 模型类
        page: 页码
        size: 每页数量
        filter_by: 过滤条件
        order_by: 排序字段
        order_desc: 是否降序

    Returns:
        (记录列表, 总数)
    """
    stmt = select(model)
    count_stmt = select(func.count()).select_from(model)

    # 应用过滤条件
    if filter_by:
        for key, value in filter_by.items():
            if hasattr(model, key):
                stmt = stmt.where(getattr(model, key) == value)
                count_stmt = count_stmt.where(getattr(model, key) == value)

    # 应用排序
    if order_by and hasattr(model, order_by):
        order_column = getattr(model, order_by)
        if order_desc:
            stmt = stmt.order_by(order_column.desc())
        else:
            stmt = stmt.order_by(order_column)

    # 获取总数
    total_result = await session.execute(count_stmt)
    total = total_result.scalar() or 0

    # 分页
    stmt = stmt.offset((page - 1) * size).limit(size)

    result = await session.execute(stmt)
    items = list(result.scalars().all())

    return items, total


async def create(
    session: AsyncSession,
    model: Any,
    data: dict[str, Any],
) -> Any:
    """
    创建记录

    Args:
        session: 数据库会话
        model: 模型类
        data: 数据字典

    Returns:
        新记录的ID
    """
    obj = model(**data)
    session.add(obj)
    await session.commit()
    await session.refresh(obj)
    return obj.id


async def update_by_id(
    session: AsyncSession,
    model: Any,
    id: Any,
    data: dict[str, Any],
) -> bool:
    """
    根据ID更新记录

    Args:
        session: 数据库会话
        model: 模型类
        id: 记录ID
        data: 更新数据

    Returns:
        是否更新成功
    """
    stmt = update(model).where(model.id == id).values(**data)
    result = await session.execute(stmt)
    await session.commit()
    return result.rowcount > 0  # type: ignore[union-attr]


async def delete_by_id(
    session: AsyncSession,
    model: Any,
    id: Any,
) -> bool:
    """
    根据ID删除记录

    Args:
        session: 数据库会话
        model: 模型类
        id: 记录ID

    Returns:
        是否删除成功
    """
    stmt = delete(model).where(model.id == id)
    result = await session.execute(stmt)
    await session.commit()
    return result.rowcount > 0  # type: ignore[union-attr]
