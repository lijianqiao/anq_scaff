"""
数据模式 - ${ModuleName}
用于请求/响应数据验证
"""

from datetime import datetime

from pydantic import BaseModel, Field


class ${ModuleName}Base(BaseModel):
    """${ModuleName} 基础模式"""

    name: str = Field(..., min_length=1, max_length=100, description="名称")
    description: str | None = Field(None, max_length=500, description="描述")
    status: int | None = Field(1, ge=0, le=1, description="状态: 1-启用, 0-禁用")


class ${ModuleName}Create(${ModuleName}Base):
    """创建${ModuleName}请求模式"""

    pass


class ${ModuleName}Update(BaseModel):
    """更新${ModuleName}请求模式（所有字段可选）"""

    name: str | None = Field(None, min_length=1, max_length=100, description="名称")
    description: str | None = Field(None, max_length=500, description="描述")
    status: int | None = Field(None, ge=0, le=1, description="状态: 1-启用, 0-禁用")


class ${ModuleName}Response(${ModuleName}Base):
    """${ModuleName}响应模式"""

    id: str = Field(..., description="主键ID")
    created_at: datetime | None = Field(None, description="创建时间")
    updated_at: datetime | None = Field(None, description="更新时间")

    class Config:
        from_attributes: bool = True


class ${ModuleName}ListResponse(BaseModel):
    """${ModuleName}列表响应模式"""

    items: list[${ModuleName}Response] = Field(
        default_factory=list, description="数据列表"
    )
    total: int = Field(..., description="总数")
