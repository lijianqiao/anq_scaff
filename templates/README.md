# ${project_name}

基于 FastAPI 构建的企业级应用。

## 快速开始

### 环境要求

- Python >= 3.10（推荐 3.12+）
- uv（推荐）或 pip

### 安装依赖

```bash
# 使用 uv（推荐）
uv pip install -r requirements.txt

# 或使用 pip
pip install -r requirements.txt
```

### 配置环境变量

```bash
# 复制环境变量示例文件
cp .env.example .env

# 编辑 .env 文件，设置数据库连接等配置
```

### 启动服务

```bash
# 开发模式
python runserver.py

# 或使用 uv
uv run python runserver.py
```

服务启动后访问：
- API 文档: http://localhost:8000/docs
- ReDoc 文档: http://localhost:8000/redoc

## 项目结构

```
${project_name}/
├── app/
│   ├── api/                    # API 接口层
│   │   ├── v1/                # API 版本
│   │   ├── dependencies.py   # 依赖注入
│   │   ├── exceptions.py      # 异常定义
│   │   ├── responses.py      # 响应封装
│   │   └── status.py         # 状态码
│   ├── initializer/           # 初始化组件
│   ├── middleware/            # 中间件
│   ├── models/                # 数据模型层
│   ├── schemas/               # 数据验证层
│   ├── services/              # 业务逻辑层
│   ├── utils/                 # 工具函数
│   └── main.py                # 应用入口
├── config/                     # 配置文件
├── tests/                      # 测试
├── logs/                       # 日志文件
├── .env                        # 环境变量
├── requirements.txt           # Python 依赖
└── runserver.py               # 启动脚本
```

## 开发指南

### 添加新的 API 模块

在 `app/api/v1/` 目录下创建新的 Python 文件，定义 `router = APIRouter()`，路由会自动注册。

### 统一路由接口

所有 CRUD 操作遵循统一接口：

```bash
POST /<资源>/actions
{
  "action": "list|get|create|update|delete",
  "params": {...}
}
```

### 运行测试

```bash
# 运行所有测试
pytest

# 查看覆盖率
pytest --cov=app tests/
```

## Docker 部署

```bash
# 构建镜像
docker build -t ${project_name} .

# 使用 docker-compose
docker-compose up -d
```

## License

MIT

