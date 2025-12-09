#!/usr/bin/env node
/**
 * 自动化代码生成脚本
 * 通过命令行交互式地为新数据表快速生成全套符合项目规范的路由接口代码
 * 
 * 使用现代 Python 3.10+ 语法
 */

const readline = require('readline');
const fs = require('fs');
const path = require('path');

const rl = readline.createInterface({
    input: process.stdin,
    output: process.stdout
});

function question(query) {
    return new Promise(resolve => rl.question(query, resolve));
}

async function generateCode() {
    console.log('🚀 ANQ Scaff 代码生成器\n');
    
    // 收集信息
    const moduleName = await question('📝 模块名称（如：user）: ');
    const tableName = await question('📊 数据表名（如：user）: ');
    const fields = await question('📋 字段列表（用逗号分隔，如：name,phone,email）: ');
    
    const fieldList = fields.split(',').map(f => f.trim()).filter(f => f);
    
    // 生成文件路径
    const projectRoot = process.cwd();
    const apiPath = path.join(projectRoot, 'app', 'api', 'v1', `${moduleName}.py`);
    const servicePath = path.join(projectRoot, 'app', 'services', `${moduleName}.py`);
    const modelPath = path.join(projectRoot, 'app', 'models', `${moduleName}.py`);
    const schemaPath = path.join(projectRoot, 'app', 'schemas', `${moduleName}.py`);
    
    // 确保目录存在
    [apiPath, servicePath, modelPath, schemaPath].forEach(p => {
        const dir = path.dirname(p);
        if (!fs.existsSync(dir)) {
            fs.mkdirSync(dir, { recursive: true });
        }
    });
    
    // 生成Model
    const modelCode = generateModel(moduleName, tableName, fieldList);
    fs.writeFileSync(modelPath, modelCode);
    console.log(`✅ 生成 Model: ${modelPath}`);
    
    // 生成Schema
    const schemaCode = generateSchema(moduleName, fieldList);
    fs.writeFileSync(schemaPath, schemaCode);
    console.log(`✅ 生成 Schema: ${schemaPath}`);
    
    // 生成Service
    const serviceCode = generateService(moduleName, fieldList);
    fs.writeFileSync(servicePath, serviceCode);
    console.log(`✅ 生成 Service: ${servicePath}`);
    
    // 生成API
    const apiCode = generateAPI(moduleName);
    fs.writeFileSync(apiPath, apiCode);
    console.log(`✅ 生成 API: ${apiPath}`);
    
    console.log('\n🎉 代码生成完成！');
    console.log('\n📌 提示: 请在 app/models/__init__.py 中导入新模型以启用自动建表');
    rl.close();
}

function generateModel(moduleName, tableName, fields) {
    const className = moduleName.charAt(0).toUpperCase() + moduleName.slice(1);
    const fieldDefs = fields.map(f => {
        return `    ${f} = Column(String(255), nullable=True, comment="${f}")`;
    }).join('\n');
    
    return `"""
数据模型 - ${className}
"""

from datetime import datetime
from typing import Any

from sqlalchemy import Column, DateTime, Integer, String, Text
from sqlalchemy.sql import func

from app.initializer._db import Base


class ${className}(Base):
    """${className} 数据模型"""

    __tablename__ = "${tableName}"

    # 主键ID (使用雪花ID，字符串类型)
    id = Column(String(32), primary_key=True, comment="主键ID")

    # 业务字段
${fieldDefs}
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
${fields.map(f => `            "${f}": self.${f},`).join('\n')}
            "status": self.status,
            "created_at": created.isoformat() if isinstance(created, datetime) else None,
            "updated_at": updated.isoformat() if isinstance(updated, datetime) else None,
        }

    def __repr__(self) -> str:
        return f"<${className}(id={self.id})>"
`;
}

function generateSchema(moduleName, fields) {
    const className = moduleName.charAt(0).toUpperCase() + moduleName.slice(1);
    const fieldDefs = fields.map(f => {
        return `    ${f}: str | None = Field(None, description="${f}")`;
    }).join('\n');
    
    return `"""
数据结构 - ${className}
使用 Python 3.10+ 类型语法
"""

from pydantic import BaseModel, Field


class ${className}Create(BaseModel):
    """创建${className}请求"""

${fieldDefs}


class ${className}Update(BaseModel):
    """更新${className}请求"""

${fieldDefs}
    status: int | None = Field(None, description="状态")


class ${className}Detail(BaseModel):
    """${className}详情响应"""

    id: str
${fieldDefs}
    status: int | None = None
    created_at: str | None = None
    updated_at: str | None = None


class ${className}ListParams(BaseModel):
    """${className}列表参数"""

    page: int = Field(1, ge=1, description="页码")
    size: int = Field(10, ge=1, le=100, description="每页数量")
`;
}

function generateService(moduleName, fields) {
    const className = moduleName.charAt(0).toUpperCase() + moduleName.slice(1);
    
    return `"""
业务逻辑层 - ${className}
"""

from typing import Any

from loguru import logger

from app.initializer import g  # type: ignore
from app.models.${moduleName} import ${className}  # type: ignore
from app.schemas.${moduleName} import ${className}Create, ${className}Update  # type: ignore
from app.utils import db_async_util  # type: ignore


class ${className}Service:
    """${className} 业务服务类"""

    async def list(
        self,
        page: int = 1,
        size: int = 10,
        filters: dict[str, Any] | None = None,
    ) -> tuple[list[dict[str, Any]], int]:
        """
        获取${className}列表

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
                model=${className},
                page=page,
                size=size,
                filter_by=filters or {},
            )
            return [item.to_dict() for item in items], total

    async def get(self, id: str) -> dict[str, Any] | None:
        """
        获取单个${className}

        Args:
            id: 记录ID

        Returns:
            ${className}数据或None
        """
        async with g.db_async_session() as session:  # type: ignore[attr-defined]
            item = await db_async_util.fetch_one(
                session=session,
                model=${className},
                filter_by={"id": id},
            )
            return item.to_dict() if item else None

    async def create(self, data: ${className}Create) -> str:
        """
        创建${className}

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
                model=${className},
                data=create_data,
            )
            logger.info(f"创建${className}成功: {new_id}")
            return new_id

    async def update(self, id: str, data: ${className}Update) -> bool:
        """
        更新${className}

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
                model=${className},
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
                model=${className},
                id=id,
                data=update_data,
            )
            logger.info(f"更新${className}成功: {id}")
            return True

    async def delete(self, id: str) -> bool:
        """
        删除${className}

        Args:
            id: 记录ID

        Returns:
            是否删除成功
        """
        async with g.db_async_session() as session:  # type: ignore[attr-defined]
            # 检查记录是否存在
            item = await db_async_util.fetch_one(
                session=session,
                model=${className},
                filter_by={"id": id},
            )
            if not item:
                return False

            await db_async_util.delete_by_id(
                session=session,
                model=${className},
                id=id,
            )
            logger.info(f"删除${className}成功: {id}")
            return True
`;
}

function generateAPI(moduleName) {
    const className = moduleName.charAt(0).toUpperCase() + moduleName.slice(1);
    
    return `"""
API接口 - ${className}
统一路由接口：POST /${moduleName}/actions
"""

from typing import Any

from fastapi import APIRouter, Body, Depends

from app.api.dependencies import JWTUser, get_current_user  # type: ignore
from app.api.responses import Responses  # type: ignore
from app.api.status import Status  # type: ignore
from app.schemas.${moduleName} import ${className}Create, ${className}Update  # type: ignore
from app.services.${moduleName} import ${className}Service  # type: ignore

router = APIRouter()
_active = True
_tag = "${moduleName}"


@router.post("/${moduleName}/actions")
async def unified_action(
    request: dict[str, Any] = Body(...),
    current_user: JWTUser | None = Depends(get_current_user),
) -> dict[str, Any]:
    """
    统一动作接口
    action: list, get, create, update, delete
    """
    _ = current_user  # 可用于权限检查
    action = request.get("action")
    params = request.get("params", {})

    service = ${className}Service()

    try:
        if action == "list":
            page = params.get("page", 1)
            size = params.get("size", 10)
            items, total = await service.list(page=page, size=size)
            return Responses.success(data={"items": items, "total": total})

        elif action == "get":
            id = params.get("id")
            if not id:
                return Responses.failure(status=Status.PARAMS_ERROR, msg="缺少id参数")
            data = await service.get(id)
            if not data:
                return Responses.failure(status=Status.RECORD_NOT_EXIST_ERROR)
            return Responses.success(data=data)

        elif action == "create":
            create_data = ${className}Create(**params)
            id = await service.create(create_data)
            return Responses.success(data={"id": id})

        elif action == "update":
            id = params.get("id")
            if not id:
                return Responses.failure(status=Status.PARAMS_ERROR, msg="缺少id参数")
            update_data = ${className}Update(**params)
            success = await service.update(id, update_data)
            if not success:
                return Responses.failure(status=Status.RECORD_NOT_EXIST_ERROR)
            return Responses.success(data={"id": id})

        elif action == "delete":
            id = params.get("id")
            if not id:
                return Responses.failure(status=Status.PARAMS_ERROR, msg="缺少id参数")
            success = await service.delete(id)
            if not success:
                return Responses.failure(status=Status.RECORD_NOT_EXIST_ERROR)
            return Responses.success(data={"id": id})

        else:
            return Responses.failure(
                status=Status.PARAMS_ERROR, msg=f"不支持的动作: {action}"
            )

    except Exception as e:
        return Responses.failure(msg=f"操作失败: {e!s}", error=str(e))
`;
}

// 运行生成器
if (require.main === module) {
    generateCode().catch(console.error);
}

module.exports = { generateCode };
