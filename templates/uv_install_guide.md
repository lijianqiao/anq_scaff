# uv 安装指南

## 什么是 uv？

`uv` 是一个极快的 Python 包安装器和解析器，用 Rust 编写。它是 `pip` 和 `pip-tools` 的现代替代品，速度更快，功能更强大。

## 安装 uv

### Windows

使用 PowerShell：

```powershell
powershell -c "irm https://astral.sh/uv/install.ps1 | iex"
```

### Linux / macOS

使用 curl：

```bash
curl -LsSf https://astral.sh/uv/install.sh | sh
```

或使用 pip：

```bash
pip install uv
```

## 验证安装

```bash
uv --version
```

## 基本使用

### 安装包

```bash
# 安装单个包
uv pip install fastapi

# 安装多个包
uv pip install fastapi uvicorn

# 从 requirements.txt 安装
uv pip install -r requirements.txt

# 安装开发模式
uv pip install -e .
```

### 运行 Python 脚本

```bash
# 运行脚本（自动管理虚拟环境）
uv run python script.py

# 运行模块
uv run python -m app.main
```

### 创建虚拟环境

```bash
# 创建虚拟环境
uv venv

# 激活虚拟环境
# Windows
.venv\Scripts\activate
# Linux/Mac
source .venv/bin/activate
```

## 为什么使用 uv？

1. **速度极快**：比 pip 快 10-100 倍
2. **功能强大**：集成了包管理、虚拟环境、依赖解析等功能
3. **兼容性好**：完全兼容 pip 和 requirements.txt
4. **现代化**：使用 Rust 编写，性能优异

## 更多信息

- 官方文档：https://github.com/astral-sh/uv
- GitHub：https://github.com/astral-sh/uv

