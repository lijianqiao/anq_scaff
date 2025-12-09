"""
业务逻辑层 - ${ModuleName}
"""

from typing import Any

from loguru import logger

# type: ignore 用于模板文件
from app.initializer import g  # type: ignore
from app.models.${module_name} import ${ModuleName}  # type: ignore
from app.schemas.${module_name} import ${ModuleName}Create, ${ModuleName}Update  # type: ignore
from app.utils import db_async_util  # type: ignore


class ${ModuleName}Service:
    """${ModuleName} 业务服务类"""

    async def list(
        self,
        page: int = 1,
        size: int = 10,
        filters: dict[str, Any] | None = None,
    ) -> tuple[list[dict[str, Any]], int]:
        """
        获取${ModuleName}列表

        Args:
            page: 页码
            size: 每页数量
            filters: 过滤条件

        Returns:
            (列表数据, 总数)
        """
        async with g.db_async_session() as session:  # type: ignore[attr-defined]
            items, total = await db_async_util.fetch_all(
                session=session,
                model=${ModuleName},
                page=page,
                size=size,
                filter_by=filters or {},
            )
            return [item.to_dict() for item in items], total

    async def get(self, id: str) -> dict[str, Any] | None:
        """
        获取单个${ModuleName}

        Args:
            id: 记录ID

        Returns:
            ${ModuleName}数据或None
        """
        async with g.db_async_session() as session:  # type: ignore[attr-defined]
            item = await db_async_util.fetch_one(
                session=session,
                model=${ModuleName},
                filter_by={"id": id},
            )
            return item.to_dict() if item else None

    async def create(self, data: ${ModuleName}Create) -> str:
        """
        创建${ModuleName}

        Args:
            data: 创建数据

        Returns:
            新创建记录的ID
        """
        async with g.db_async_session() as session:  # type: ignore[attr-defined]
            # 使用雪花ID生成唯一ID
            new_id = g.snow_client.generate_id_str()  # type: ignore[attr-defined]
            create_data = data.model_dump()
            create_data["id"] = new_id

            await db_async_util.create(
                session=session,
                model=${ModuleName},
                data=create_data,
            )
            logger.info(f"创建${ModuleName}成功: {new_id}")
            return new_id

    async def update(self, id: str, data: ${ModuleName}Update) -> bool:
        """
        更新${ModuleName}

        Args:
            id: 记录ID
            data: 更新数据

        Returns:
            是否更新成功
        """
        async with g.db_async_session() as session:  # type: ignore[attr-defined]
            # 检查记录是否存在
            item = await db_async_util.fetch_one(
                session=session,
                model=${ModuleName},
                filter_by={"id": id},
            )
            if not item:
                return False

            # 过滤掉None值
            update_data = {
                k: v for k, v in data.model_dump().items() if v is not None
            }
            if not update_data:
                return True  # 没有需要更新的数据

            await db_async_util.update_by_id(
                session=session,
                model=${ModuleName},
                id=id,
                data=update_data,
            )
            logger.info(f"更新${ModuleName}成功: {id}")
            return True

    async def delete(self, id: str) -> bool:
        """
        删除${ModuleName}

        Args:
            id: 记录ID

        Returns:
            是否删除成功
        """
        async with g.db_async_session() as session:  # type: ignore[attr-defined]
            # 检查记录是否存在
            item = await db_async_util.fetch_one(
                session=session,
                model=${ModuleName},
                filter_by={"id": id},
            )
            if not item:
                return False

            await db_async_util.delete_by_id(
                session=session,
                model=${ModuleName},
                id=id,
            )
            logger.info(f"删除${ModuleName}成功: {id}")
            return True
