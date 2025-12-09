"""
业务逻辑层 - ${ModuleName}
"""

# 导入引发的报错在创建项目之后会自动消失
import json
from typing import Any

from loguru import logger

from app.initializer import g
from app.models.${module_name} import ${ModuleName}
from app.schemas.${module_name} import ${ModuleName}Create, ${ModuleName}Update
from app.utils.logging_fastcrud import LoggingFastCRUD


class ${ModuleName}Service:
    """${ModuleName} 业务服务类"""

    def __init__(self) -> None:
        self.crud = LoggingFastCRUD(${ModuleName})
        self.cache = getattr(g, "cache_manager", None)
        self.cache_prefix = f"${module_name}:"

    def _cache_key(self, suffix: str) -> str:
        return f"{self.cache_prefix}{suffix}"

    async def list(
        self,
        page: int = 1,
        size: int = 10,
        filters: dict[str, Any] | None = None,
    ) -> tuple[list[dict[str, Any]], int]:
        """获取${ModuleName}列表"""
        cache_key = self._cache_key(
            f"list:{page}:{size}:{json.dumps(filters or {}, sort_keys=True, ensure_ascii=False)}"
        )
        if self.cache:
            cached = self.cache.get(cache_key)
            if cached:
                return cached  # type: ignore[return-value]

        async with g.db_async_session() as session:  # type: ignore[attr-defined]
            items, total = await self.crud.list(
                session=session,
                page=page,
                size=size,
                filter_by=filters or {},
            )

        result = (items, total)
        if self.cache:
            self.cache.set(cache_key, result, expire=300)
        return result

    async def get(self, id: str) -> dict[str, Any] | None:
        """获取单个${ModuleName}"""
        cache_key = self._cache_key(f"get:{id}")
        if self.cache:
            cached = self.cache.get(cache_key)
            if cached:
                return cached  # type: ignore[return-value]

        async with g.db_async_session() as session:  # type: ignore[attr-defined]
            item = await self.crud.get(session=session, id=id)

        if item and self.cache:
            self.cache.set(cache_key, item, expire=300)
        return item

    async def create(self, data: ${ModuleName}Create) -> str:
        """创建${ModuleName}"""
        async with g.db_async_session() as session:  # type: ignore[attr-defined]
            new_id = g.snow_client.generate_id_str()  # type: ignore[attr-defined]
            create_data = data.model_dump()
            create_data["id"] = new_id

            await self.crud.create(session=session, data=create_data)
            logger.info(f"创建${ModuleName}成功: {new_id}")
            return new_id

    async def update(self, id: str, data: ${ModuleName}Update) -> bool:
        """更新${ModuleName}"""
        update_data = {k: v for k, v in data.model_dump().items() if v is not None}
        if not update_data:
            return True

        async with g.db_async_session() as session:  # type: ignore[attr-defined]
            updated = await self.crud.update(session=session, id=id, data=update_data)
            if updated:
                logger.info(f"更新${ModuleName}成功: {id}")
            return updated

    async def delete(self, id: str) -> bool:
        """删除${ModuleName}"""
        async with g.db_async_session() as session:  # type: ignore[attr-defined]
            deleted = await self.crud.delete(session=session, id=id)
            if deleted:
                logger.info(f"删除${ModuleName}成功: {id}")
            return deleted
