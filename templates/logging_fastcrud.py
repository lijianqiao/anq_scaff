"""
异步CRUD抽象层 - LoggingFastCRUD
自动处理日志、缓存失效和数据库错误翻译
"""

from typing import Any

from loguru import logger
from sqlalchemy import delete, func, select, update
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.exceptions import DatabaseError, ErrorCode  # type: ignore
from app.initializer import g  # type: ignore
from app.initializer.context import request_id_var, user_id_var  # type: ignore


class LoggingFastCRUD:
    """带日志的快速CRUD基类"""

    def __init__(self, model: Any):
        self.model = model
        self.model_name = model.__name__

    async def _execute_with_logging(
        self,
        operation: str,
        session: AsyncSession,
        func_call: Any,
        *args: Any,
        **kwargs: Any,
    ) -> Any:
        """执行操作并记录日志"""
        request_id = request_id_var.get("N/A")
        user_id = user_id_var.get() or "anonymous"

        try:
            logger.info(
                f"[{request_id}] [{user_id}] {self.model_name}.{operation} "
                f"args={args} kwargs={kwargs}"
            )

            result = await func_call(*args, **kwargs)

            logger.info(
                f"[{request_id}] [{user_id}] {self.model_name}.{operation} "
                f"success: {result}"
            )

            # 缓存失效
            await self._invalidate_cache(operation)

            return result

        except SQLAlchemyError as e:
            logger.error(
                f"[{request_id}] [{user_id}] {self.model_name}.{operation} "
                f"database error: {e}"
            )
            raise DatabaseError(
                error_code=ErrorCode.DATABASE_ERROR,
                message=f"数据库操作失败: {e!s}",
                cause=e,
            ) from e
        except Exception as e:
            logger.exception(
                f"[{request_id}] [{user_id}] {self.model_name}.{operation} "
                f"unexpected error: {e}"
            )
            raise

    async def _invalidate_cache(self, operation: str) -> None:
        """缓存失效"""
        cache_manager = getattr(g, "cache_manager", None)
        if cache_manager:
            # 清除相关缓存
            cache_key_pattern = f"{self.model_name.lower()}:*"
            # 这里需要根据实际缓存实现来清除
            logger.debug(f"Invalidating cache for {cache_key_pattern} ({operation})")

    async def get(
        self,
        session: AsyncSession,
        id: Any,
        fields: list[str] | None = None,
    ) -> dict[str, Any] | None:
        """获取单条记录"""

        async def _get() -> dict[str, Any] | None:
            stmt = select(self.model).where(self.model.id == id)
            result = await session.execute(stmt)
            obj = result.scalar_one_or_none()
            if not obj:
                return None

            if fields:
                return {
                    field: getattr(obj, field)
                    for field in fields
                    if hasattr(obj, field)
                }
            return {c.name: getattr(obj, c.name) for c in self.model.__table__.columns}

        return await self._execute_with_logging("get", session, _get)

    async def list(
        self,
        session: AsyncSession,
        page: int = 1,
        size: int = 10,
        filter_by: dict[str, Any] | None = None,
        fields: list[str] | None = None,
    ) -> tuple[list[dict[str, Any]], int]:
        """获取列表（分页）"""

        async def _list() -> tuple[list[dict[str, Any]], int]:
            stmt = select(self.model)

            # 应用过滤条件
            if filter_by:
                for key, value in filter_by.items():
                    if hasattr(self.model, key):
                        stmt = stmt.where(getattr(self.model, key) == value)

            # 获取总数
            count_stmt = select(func.count()).select_from(self.model)
            if filter_by:
                for key, value in filter_by.items():
                    if hasattr(self.model, key):
                        count_stmt = count_stmt.where(
                            getattr(self.model, key) == value
                        )

            total_result = await session.execute(count_stmt)
            total = total_result.scalar() or 0

            # 分页
            stmt = stmt.offset((page - 1) * size).limit(size)

            result = await session.execute(stmt)
            objs = result.scalars().all()

            if fields:
                items = [
                    {
                        field: getattr(obj, field)
                        for field in fields
                        if hasattr(obj, field)
                    }
                    for obj in objs
                ]
            else:
                # 对每个对象生成一个包含所有字段的字典
                items = [
                    {c.name: getattr(obj, c.name) for c in self.model.__table__.columns}
                    for obj in objs
                ]

            return items, total

        return await self._execute_with_logging("list", session, _list)

    async def create(self, session: AsyncSession, data: dict[str, Any]) -> Any:
        """创建记录"""

        async def _create() -> Any:
            obj = self.model(**data)
            session.add(obj)
            await session.commit()
            await session.refresh(obj)
            return obj.id

        return await self._execute_with_logging("create", session, _create)

    async def update(
        self,
        session: AsyncSession,
        id: Any,
        data: dict[str, Any],
    ) -> bool:
        """更新记录"""

        async def _update() -> bool:
            stmt = update(self.model).where(self.model.id == id).values(**data)
            result = await session.execute(stmt)
            await session.commit()
            return result.rowcount > 0  # type: ignore[union-attr]

        return await self._execute_with_logging("update", session, _update)

    async def delete(self, session: AsyncSession, id: Any) -> bool:
        """删除记录"""

        async def _delete() -> bool:
            stmt = delete(self.model).where(self.model.id == id)
            result = await session.execute(stmt)
            await session.commit()
            return result.rowcount > 0  # type: ignore[union-attr]

        return await self._execute_with_logging("delete", session, _delete)
