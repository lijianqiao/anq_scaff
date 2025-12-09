# ANQ Scaff - 企业级FastAPI项目脚手架

## **ps**：该项目为 ai 主要开发，本人做一些修复错误以及开发部分，适用于大多数小项目。

## 🎯 项目简介

ANQ Scaff 是一个企业级 FastAPI 项目脚手架生成工具，集成了现代 Python Web 开发中的各项最佳实践。核心设计哲学是**模块化、高内聚、低耦合**。

## ✨ 核心特性

### 1. 现代化技术栈
- ✅ 基于 **FastAPI**、**Pydantic V2**、**SQLAlchemy 2.0 (Async)** 构建
- ✅ 保证高性能和优秀的开发体验

### 2. 统一的路由接口
- ✅ 所有 CRUD 操作均遵循 **POST /<资源>/actions** 模式
- ✅ 接口规范高度统一，便于客户端调用

### 3. 分层的异常处理
- ✅ 集中管理的 **错误码 -> 自定义异常 -> 全局异常处理器**
- ✅ 实现业务异常和未知错误的优雅、分层处理

### 4. 上下文感知日志
- ✅ 利用 **contextvars** 自动为每条日志注入 `request_id` 和 `user_id`
- ✅ 完美支持分布式系统下的链路追踪
- ✅ 日志按用途和级别分离到不同文件 (`info.log`, `error.log`, `api_traffic.log`)

### 5. 异步 CRUD 抽象层
- ✅ **LoggingFastCRUD** 封装了通用的数据库操作
- ✅ 自动处理日志、缓存失效和数据库错误翻译
- ✅ 业务代码更专注于逻辑本身

### 6. 专业的测试套件
- ✅ 使用 **pytest** 和 **Starlette TestClient**
- ✅ 为 API 提供稳定、可靠的自动化集成测试
- ✅ 使用独立的内存数据库保证测试的纯净与高速

### 7. 灵活的配置管理
- ✅ 通过 **pydantic-settings** 和 `.env` 文件实现配置与代码的完全分离
- ✅ 轻松适配开发、测试、生产等多种环境

### 8. 应用生命周期管理
- ✅ 使用 **lifespan** 管理器优雅地处理数据库、Redis 连接池等资源的初始化与释放
- ✅ 包含后台定时任务的最佳实践

### 9. 自动化代码生成
- ✅ 内置 **Node.js** 脚本，可通过命令行交互式地为新数据表快速生成全套符合项目规范的路由接口代码

## 🚀 快速开始

### 前置要求

- Python >= 3.11
- uv（推荐）或 pip

### 安装 uv（如果还没有安装）

```bash
# Windows
powershell -c "irm https://astral.sh/uv/install.ps1 | iex"

# Linux/Mac
curl -LsSf https://astral.sh/uv/install.sh | sh
```

### 安装脚手架工具（源码安装）

> **注意**：本项目为源码项目，需要从源码安装。

#### 使用 uv（推荐）

```bash
# 进入 anq_scaff 目录（注意：是包含 setup.py 的 anq_scaff 目录）
cd anq_scaff

# 安装脚手架工具（开发模式）
uv pip install -e .

# 验证安装
anq-scaff --help

# 如果验证失败，可以尝试重新安装
# uv pip uninstall anq-scaff
# uv pip install -e .
```

#### 使用 pip（备选）

```bash
# 进入 anq_scaff 目录（注意：是包含 setup.py 的 anq_scaff 目录）
cd anq_scaff

# 安装脚手架工具（开发模式）
pip install -e .

# 验证安装
anq-scaff --help

# 如果验证失败，可以尝试重新安装
# pip uninstall anq-scaff
# pip install -e .
```

> **提示**：
> 1. 如果系统没有安装 pip，请使用 uv。uv 是 pip 的现代替代品，速度更快，功能更强大。
> 2. 确保在包含 `setup.py` 的 `anq_scaff` 目录下执行安装命令。
> 3. 如果安装后仍然报错 `ModuleNotFoundError: No module named 'anq_scaff'`，请尝试：
>    - 重新安装：`uv pip uninstall anq-scaff && uv pip install -e .`
>    - 或使用直接运行方式：`uv run python -m anq_scaff.cli new myproject`

### 创建新项目

```bash
# 基础项目（SQLite）
anq-scaff new myproject

# 指定数据库类型
anq-scaff new myproject --db mysql
anq-scaff new myproject --db postgresql

# 启用Redis缓存
anq-scaff new myproject --redis

# 组合使用
anq-scaff new myproject --db postgresql --redis
```

### 启动项目

#### 使用 uv（推荐）

```bash
cd myproject

# 安装依赖
uv pip install -r requirements.txt

# 配置环境变量（创建 .env 文件）
cp .env.example .env
# 编辑 .env 文件设置数据库连接等

# 启动服务
uv run python runserver.py
```

#### 使用 pip（备选）

```bash
cd myproject

# 安装依赖
pip install -r requirements.txt

# 配置环境变量（创建 .env 文件）
cp .env.example .env
# 编辑 .env 文件设置数据库连接等

# 启动服务
python runserver.py
```

> **提示**：如果系统没有安装 pip，请使用 uv。

### 添加API模块

```bash
# 使用Node.js脚本生成（推荐）
cd myproject
npm install
npm run generate

# 或使用Python命令
anq-scaff add user --version v1
```

## 📁 项目结构

```
myproject/
├── app/
│   ├── api/                    # API接口层
│   │   ├── v1/                # API版本
│   │   ├── dependencies.py   # 依赖注入
│   │   ├── exceptions.py      # 异常定义
│   │   ├── responses.py      # 响应封装
│   │   └── status.py         # 状态码
│   ├── initializer/           # 初始化组件
│   │   ├── _conf.py          # 配置管理（pydantic-settings）
│   │   ├── _db.py            # 数据库初始化
│   │   ├── _log.py           # 日志初始化（上下文感知）
│   │   ├── _cache.py         # 缓存初始化
│   │   └── context.py        # 上下文变量（request_id, user_id）
│   ├── middleware/            # 中间件
│   │   ├── cors.py           # CORS
│   │   ├── exceptions.py     # 异常处理（分层）
│   │   └── http.py           # HTTP中间件
│   ├── models/                # 数据模型层
│   ├── schemas/               # 数据验证层（Pydantic V2）
│   ├── services/              # 业务逻辑层
│   │   └── base.py           # LoggingFastCRUD基类
│   ├── utils/                 # 工具函数
│   ├── cache/                 # 缓存模块
│   └── main.py                # 应用入口（lifespan管理）
├── config/                     # 配置文件（可选）
├── tests/                      # 测试套件
│   ├── test_base.py          # 测试基础类
│   └── test_*.py             # 测试用例
├── logs/                       # 日志文件
│   ├── info.log              # 信息日志
│   ├── error.log             # 错误日志
│   └── api_traffic.log       # API流量日志
├── .env                        # 环境变量配置
├── .env.example               # 环境变量示例
├── requirements.txt           # Python依赖
├── package.json               # Node.js依赖（代码生成器）
├── generate_code.js          # 代码生成脚本
└── pytest.ini                # pytest配置
```

## 💡 使用示例

### 统一路由接口

所有CRUD操作通过统一接口：

```bash
# 列表
POST /user/actions
{
  "action": "list",
  "params": {"page": 1, "size": 10}
}

# 详情
POST /user/actions
{
  "action": "get",
  "params": {"id": "123"}
}

# 创建
POST /user/actions
{
  "action": "create",
  "params": {"name": "test", "phone": "13800138000"}
}

# 更新
POST /user/actions
{
  "action": "update",
  "params": {"id": "123", "name": "new_name"}
}

# 删除
POST /user/actions
{
  "action": "delete",
  "params": {"id": "123"}
}
```

### 使用LoggingFastCRUD

```python
from app.utils.logging_fastcrud import LoggingFastCRUD
from app.models.user import User
from app.initializer import g

class UserService:
    def __init__(self):
        self.crud = LoggingFastCRUD(User)
    
    async def get_user(self, user_id: str):
        async with g.db_async_session() as session:
            return await self.crud.get(session, user_id)
```

### 上下文感知日志

日志自动包含 `request_id` 和 `user_id`：

```python
from loguru import logger

logger.info("用户操作")  # 自动包含 request_id 和 user_id
```

### 分层异常处理

```python
from app.api.exceptions import BusinessException, ErrorCode

# 抛出业务异常
raise BusinessException(
    error_code=ErrorCode.RESOURCE_NOT_FOUND,
    message="用户不存在",
    details={"user_id": "123"}
)
```

### 配置管理

使用 `.env` 文件：

```env
APP_NAME=MyApp
APP_DEBUG=true
DB_ASYNC_URL=postgresql+asyncpg://user:pass@localhost/db
REDIS_HOST=localhost
REDIS_PORT=6379
```

## 🧪 测试

#### 使用 uv（推荐）

```bash
# 运行所有测试
uv run pytest

# 运行特定测试
uv run pytest tests/test_user.py

# 查看覆盖率
uv run pytest --cov=app tests/
```

#### 使用 pip（备选）

```bash
# 运行所有测试
pytest

# 运行特定测试
pytest tests/test_user.py

# 查看覆盖率
pytest --cov=app tests/
```

> **提示**：如果系统没有安装 pip，请使用 uv。

## 📚 文档

- [使用指南](./使用指南.md) - 详细的使用说明和示例
- [API文档](http://localhost:8000/docs) - 启动服务后访问

## ❓ 常见问题

### Q: 为什么需要从源码安装？

A: ANQ Scaff 目前是源码项目，尚未发布到 PyPI，因此需要从源码安装。

### Q: 系统没有 pip 怎么办？

A: 使用 uv。uv 是 pip 的现代替代品，功能完全兼容，但速度更快。安装 uv 后，使用 `uv pip install -e .` 即可。

### Q: 可以不安装直接使用吗？

A: 可以，使用以下命令（需要在 `anq_scaff` 目录下）：

```bash
# 使用 uv（推荐）
cd anq_scaff
uv run python -m anq_scaff.cli new myproject

# 使用 pip（如果已安装）
cd anq_scaff
python -m anq_scaff.cli new myproject
```

### Q: 为什么使用 `-e` 参数？

A: `-e` 表示以"可编辑"模式安装，这样修改源码后无需重新安装即可生效，适合开发使用。

### Q: 安装后报错 `ModuleNotFoundError: No module named 'anq_scaff'` 怎么办？

A: 请尝试以下解决方案：

1. **确保在正确的目录下安装**：
   ```bash
   # 必须在包含 setup.py 的 anq_scaff 目录下
   cd anq_scaff
   uv pip install -e .
   ```

2. **重新安装**：
   ```bash
   uv pip uninstall anq-scaff
   uv pip install -e .
   ```

3. **使用直接运行方式**（无需安装）：
   ```bash
   cd anq_scaff
   uv run python -m anq_scaff.cli new myproject
   ```

4. **检查 Python 环境**：
   ```bash
   # 确保在正确的虚拟环境中
   python -c "import sys; print(sys.executable)"
   ```

## 🤝 贡献

欢迎提交 Issue 和 Pull Request！

## 📄 许可证

MIT License

## 🙏 致谢

everyone！
