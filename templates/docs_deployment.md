# 部署指南

## 环境要求

- Python >= 3.10
- Redis（可选，用于缓存）
- MySQL/PostgreSQL（生产环境推荐）

## 开发环境

### 使用 uv（推荐）

```bash
# 创建虚拟环境
uv venv

# 激活环境
source .venv/bin/activate  # Linux/macOS
.venv\Scripts\activate     # Windows

# 安装依赖
uv pip install -r requirements.txt

# 启动服务
python runserver.py
```

### 使用 pip

```bash
# 创建虚拟环境
python -m venv .venv

# 激活环境
source .venv/bin/activate  # Linux/macOS
.venv\Scripts\activate     # Windows

# 安装依赖
pip install -r requirements.txt

# 启动服务
python runserver.py
```

## 生产环境

### Docker 部署

```bash
# 构建镜像
docker build -t myapp .

# 运行容器
docker run -d \
  --name myapp \
  -p 8000:8000 \
  -e APP_ENV=prod \
  -e DB_ASYNC_URL=mysql+aiomysql://user:pass@host/db \
  myapp
```

### Docker Compose

```bash
# 启动所有服务
docker-compose up -d

# 查看日志
docker-compose logs -f

# 停止服务
docker-compose down
```

### 使用 Gunicorn + Uvicorn

```bash
# 安装 gunicorn
pip install gunicorn

# 启动（4 个 worker）
gunicorn app.main:app \
  --workers 4 \
  --worker-class uvicorn.workers.UvicornWorker \
  --bind 0.0.0.0:8000
```

### 使用 Supervisor

创建配置文件 `/etc/supervisor/conf.d/myapp.conf`：

```ini
[program:myapp]
directory=/opt/myapp
command=/opt/myapp/.venv/bin/gunicorn app.main:app --workers 4 --worker-class uvicorn.workers.UvicornWorker --bind 0.0.0.0:8000
user=www-data
autostart=true
autorestart=true
redirect_stderr=true
stdout_logfile=/var/log/myapp/app.log
```

启动服务：

```bash
supervisorctl reread
supervisorctl update
supervisorctl start myapp
```

## Nginx 配置

```nginx
upstream myapp {
    server 127.0.0.1:8000;
}

server {
    listen 80;
    server_name api.example.com;

    location / {
        proxy_pass http://myapp;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
        proxy_set_header X-Request-ID $request_id;
    }
}
```

## 健康检查

```bash
# 简单检查
curl http://localhost:8000/api/ping

# 深度检查（如果已实现）
curl http://localhost:8000/api/health
```

## 日志管理

日志文件位置：`./logs/`

- `info.log` - 普通日志（DEBUG/INFO）
- `error.log` - 错误日志（WARNING 及以上）
- `api_traffic.log` - API 流量日志

使用 logrotate 进行日志轮转（已内置支持）。

## 监控

### Prometheus 指标

可以通过 `prometheus-fastapi-instrumentator` 添加监控：

```python
# 在 main.py 中添加
from prometheus_fastapi_instrumentator import Instrumentator

Instrumentator().instrument(app).expose(app)
```

### 健康检查端点

- `GET /api/ping` - 简单存活检查
- `GET /api/health` - 服务健康状态

## 故障排查

### 常见问题

1. **数据库连接失败**
   - 检查 `DB_ASYNC_URL` 配置
   - 确认数据库服务正在运行
   - 检查防火墙规则

2. **Redis 连接失败**
   - 检查 `REDIS_HOST` 配置
   - 确认 Redis 服务正在运行
   - 系统会自动降级为内存缓存

3. **端口被占用**
   - 修改 `runserver.py` 中的端口配置
   - 或使用环境变量 `PORT=8001`

