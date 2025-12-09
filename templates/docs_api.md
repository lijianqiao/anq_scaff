# API 文档

## 概述

本项目使用 **统一动作接口** 模式，所有 CRUD 操作通过统一的接口格式进行。

## 接口规范

### 统一请求格式

```
POST /<资源>/actions
Content-Type: application/json

{
    "action": "list|get|create|update|delete",
    "params": { ... }
}
```

### 统一响应格式

```json
{
    "code": 0,
    "msg": "操作成功",
    "data": { ... }
}
```

### 状态码说明

| 状态码 | 说明         |
| ------ | ------------ |
| 0      | 成功         |
| 1xxx   | 系统错误     |
| 2xxx   | 参数错误     |
| 3xxx   | 认证授权错误 |
| 4xxx   | 业务错误     |

## 认证方式

### JWT Token

在请求头中添加：

```
Authorization: Bearer <token>
```

### API Key

在请求头中添加：

```
X-API-Key: <api_key>
```

## 常用接口

### 健康检查

```bash
GET /api/ping
GET /api/health
```

### 资源操作示例

以 `user` 资源为例：

**列表查询**
```bash
POST /api/v1/user/actions
{
    "action": "list",
    "params": {
        "page": 1,
        "size": 10
    }
}
```

**获取详情**
```bash
POST /api/v1/user/actions
{
    "action": "get",
    "params": {
        "id": "123456"
    }
}
```

**创建**
```bash
POST /api/v1/user/actions
{
    "action": "create",
    "params": {
        "name": "张三",
        "description": "测试用户"
    }
}
```

**更新**
```bash
POST /api/v1/user/actions
{
    "action": "update",
    "params": {
        "id": "123456",
        "name": "李四"
    }
}
```

**删除**
```bash
POST /api/v1/user/actions
{
    "action": "delete",
    "params": {
        "id": "123456"
    }
}
```

## 在线文档

启动服务后访问：

- Swagger UI: http://localhost:8000/docs
- ReDoc: http://localhost:8000/redoc

