# 开发指南

## 项目结构

```
app/
├── api/                    # API 接口层
│   ├── v1/                # API 版本
│   ├── default/           # 默认路由（ping, health）
│   ├── dependencies.py    # 依赖注入
│   ├── exceptions.py      # 异常定义
│   ├── responses.py       # 响应封装
│   └── status.py          # 状态码
├── cache/                  # 缓存模块
│   ├── __init__.py        # 缓存装饰器
│   └── manager.py         # 缓存管理器
├── initializer/            # 初始化组件
│   ├── _db.py             # 数据库
│   ├── _log.py            # 日志
│   ├── _redis.py          # Redis
│   ├── _settings.py       # 配置
│   └── _snow.py           # 雪花ID
├── middleware/             # 中间件
├── models/                 # 数据模型层
├── schemas/                # 数据验证层
├── services/               # 业务逻辑层
├── utils/                  # 工具函数
└── main.py                 # 应用入口
```

## 添加新模块

### 方式一：使用脚手架命令（推荐）

```bash
anq-scaff add <module_name>
```

### 方式二：使用代码生成器

```bash
node generate_code.js
```

### 方式三：手动创建

1. 在 `app/models/` 下创建模型文件
2. 在 `app/schemas/` 下创建数据验证文件
3. 在 `app/services/` 下创建业务逻辑文件
4. 在 `app/api/v1/` 下创建 API 路由文件

## 数据库操作

### 使用异步会话

```python
from app.initializer import g

async def get_user(user_id: str):
    async with g.db_async_session() as session:
        # 执行数据库操作
        result = await session.execute(...)
        return result.scalar_one_or_none()
```

### 使用 CRUD 工具

```python
from app.utils import db_async_util

# 查询单条
item = await db_async_util.fetch_one(session, Model, filter_by={"id": id})

# 查询列表
items, total = await db_async_util.fetch_all(session, Model, page=1, size=10)

# 创建
new_id = await db_async_util.create(session, Model, data={...})

# 更新
success = await db_async_util.update_by_id(session, Model, id=id, data={...})

# 删除
success = await db_async_util.delete_by_id(session, Model, id=id)
```

## 缓存使用

### 使用缓存装饰器

```python
from app.cache import cached

@cached(expire=3600, key_prefix="user")
async def get_user_by_id(user_id: str):
    # 首次调用会执行函数，结果会被缓存
    # 后续调用直接从缓存返回
    ...
```

### 使用缓存管理器

```python
from app.initializer import g

# 设置缓存
g.cache_manager.set("key", value, expire=3600)

# 获取缓存
value = g.cache_manager.get("key")

# 删除缓存
g.cache_manager.delete("key")
```

## 日志记录

### 基本使用

```python
from loguru import logger

logger.debug("调试信息")
logger.info("普通信息")
logger.warning("警告信息")
logger.error("错误信息")
logger.exception("异常信息（包含堆栈）")
```

### 上下文日志

```python
from app.initializer.context import get_request_id, get_user_id

request_id = get_request_id()
user_id = get_user_id()
logger.info(f"[{request_id}] [{user_id}] 操作完成")
```

## 测试

### 运行测试

```bash
# 运行所有测试
pytest

# 运行特定测试文件
pytest tests/test_example.py

# 查看覆盖率
pytest --cov=app tests/
```

### 编写测试

```python
from fastapi.testclient import TestClient

def test_ping(test_client: TestClient):
    response = test_client.get("/api/ping")
    assert response.status_code == 200
    assert response.json()["code"] == 0
```

## 环境变量

所有配置项都可以通过环境变量覆盖，详见 `.env.example` 文件。

```bash
# 复制示例配置
cp .env.example .env

# 编辑配置
vim .env
```

