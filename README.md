# FigureLabs AI

<p align="center">
  <strong>AI 驱动的图表生成平台</strong>
</p>

<p align="center">
  <img src="https://img.shields.io/badge/Python-3.11+-3776AB?logo=python&logoColor=white" />
  <img src="https://img.shields.io/badge/FastAPI-0.115-009688?logo=fastapi&logoColor=white" />
  <img src="https://img.shields.io/badge/React-18-61DAFB?logo=react&logoColor=white" />
  <img src="https://img.shields.io/badge/SQLite-PostgreSQL-003B57?logo=sqlite&logoColor=white" />
</p>

---

## 📋 目录

- [项目简介](#项目简介)
- [核心功能](#核心功能)
- [技术架构](#技术架构)
- [快速开始](#快速开始)
- [部署指南](#部署指南)
- [代码结构](#代码结构)
- [API 文档](#api-文档)
- [配置说明](#配置说明)
- [开发指南](#开发指南)

---

## 项目简介

FigureLabs AI 是一个基于 AI 的图表生成和管理平台，支持多账户管理、会话管理、图片生成与导出。项目采用现代化的前后端分离架构，提供完善的监控统计功能。

### 主要特性

✨ **多账户管理** - 支持 MailTM 和 DuckMail 自动注册  
📊 **实时监控** - Dashboard、Monitor、Logs 完整监控体系  
🎨 **图表生成** - AI 驱动的图表生成，支持多种格式导出  
🗄️ **双数据库** - SQLite/PostgreSQL 灵活切换  
📈 **统计分析** - 24h/7d/30d 多维度数据统计  
🔄 **模块化设计** - 清晰的代码分层，易于扩展  

---

## 核心功能

### 1. 账户管理
- 自动注册（MailTM / DuckMail）
- 账户标签管理
- 批量操作
- 账户状态监控

### 2. 图表生成
- AI 驱动的图表生成
- 会话管理
- 提示词扩展
- 实时状态查询

### 3. 导出功能
- PNG / JPG 格式导出
- SVG 矢量图导出
- PPTX 演示文稿导出
- 批量下载

### 4. 监控统计
- 实时系统监控
- 请求统计分析
- 日志查看
- 性能指标

---

## 技术架构

### 后端技术栈

```
FastAPI 0.115          # Web 框架
Python 3.11+           # 编程语言
SQLite / PostgreSQL    # 数据库
aiosqlite              # 异步 SQLite
asyncpg                # 异步 PostgreSQL (可选)
Pydantic               # 数据验证
python-multipart       # 文件上传
python-pptx            # PPTX 生成
lxml                   # XML 处理
```

### 前端技术栈

```
React 18               # UI 框架
Vite                   # 构建工具
Zustand                # 状态管理
Recharts               # 图表库
CSS Modules            # 样式方案
```

### 架构图

```
┌─────────────────────────────────────────────────┐
│                  Frontend (React)                │
│  Dashboard | Monitor | Accounts | Generate      │
│  Logs | Settings                                 │
└─────────────────┬───────────────────────────────┘
                  │ HTTP/REST API
┌─────────────────▼───────────────────────────────┐
│              Backend (FastAPI)                   │
│                                                  │
│  ┌──────────────┐  ┌──────────────┐            │
│  │   Routers    │  │   Schemas    │            │
│  │ - accounts   │  │ - validation │            │
│  │ - chat       │  │ - models     │            │
│  │ - stats      │  └──────────────┘            │
│  └──────────────┘                               │
│                                                  │
│  ┌──────────────┐  ┌──────────────┐            │
│  │    Core      │  │   Services   │            │
│  │ - storage    │  │ - register   │            │
│  │ - database   │  │ - chat       │            │
│  └──────────────┘  │ - export     │            │
│                    └──────────────┘             │
└─────────────────┬───────────────────────────────┘
                  │
┌─────────────────▼───────────────────────────────┐
│          Database (SQLite / PostgreSQL)         │
│  - accounts                                     │
│  - request_logs                                 │
│  - kv_settings                                  │
│  - kv_stats                                     │
└─────────────────────────────────────────────────┘
```

---

## 快速开始

### 环境要求

- Python 3.11+
- Node.js 18+
- Git

### 1. 克隆项目

```bash
git clone https://github.com/twj0/figurelabs.git
cd figurelabs
```

### 2. 后端设置

```bash
# 创建虚拟环境
python -m venv .venv

# 激活虚拟环境
# Windows
.venv\Scripts\activate
# Linux/Mac
source .venv/bin/activate

# 安装依赖
pip install -r requirements.txt

# 或使用 uv (更快)
uv pip install -r requirements.txt

# 创建配置文件
cp .env.example .env

# 编辑 .env 设置必要参数
```

### 3. 前端设置

```bash
cd frontend

# 安装依赖
npm install

# 开发模式
npm run dev

# 构建生产版本
npm run build
```

### 4. 启动服务

```bash
# 后端 (在项目根目录)
uvicorn src.api.app:app --port 7860 --reload

# 前端 (在 frontend 目录)
npm run dev
```

### 5. 访问应用

- 前端: http://localhost:5173
- 后端 API: http://localhost:7860
- 统计数据: http://localhost:7860/api/stats

---

## 部署指南

### Docker 部署（推荐）

#### 1. 使用 Docker Compose

```bash
# 构建并启动
docker-compose up -d

# 查看日志
docker-compose logs -f

# 停止服务
docker-compose down
```

#### 2. docker-compose.yml 配置

```yaml
version: '3.8'

services:
  app:
    build: .
    ports:
      - "7860:7860"
    volumes:
      - ./data:/app/data
    environment:
      - SQLITE_PATH=/app/data/data.db
    restart: unless-stopped

  # 可选：PostgreSQL 数据库
  postgres:
    image: postgres:15
    environment:
      POSTGRES_DB: figurelabs
      POSTGRES_USER: user
      POSTGRES_PASSWORD: password
    volumes:
      - postgres_data:/var/lib/postgresql/data
    restart: unless-stopped

volumes:
  postgres_data:
```

#### 3. Dockerfile

```dockerfile
FROM python:3.11-slim

WORKDIR /app

# 安装依赖
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# 复制代码
COPY src ./src
COPY frontend/dist ./frontend/dist

# 创建数据目录
RUN mkdir -p /app/data

# 暴露端口
EXPOSE 7860

# 启动命令
CMD ["uvicorn", "src.api.app:app", "--host", "0.0.0.0", "--port", "7860"]
```

### 传统部署

#### 1. 使用 systemd (Linux)

创建服务文件 `/etc/systemd/system/figurelabs.service`:

```ini
[Unit]
Description=FigureLabs AI Service
After=network.target

[Service]
Type=simple
User=www-data
WorkingDirectory=/var/www/figurelabs-ai
Environment="PATH=/var/www/figurelabs-ai/.venv/bin"
ExecStart=/var/www/figurelabs-ai/.venv/bin/uvicorn src.api.app:app --host 0.0.0.0 --port 7860
Restart=always

[Install]
WantedBy=multi-user.target
```

启动服务:

```bash
sudo systemctl daemon-reload
sudo systemctl enable figurelabs
sudo systemctl start figurelabs
sudo systemctl status figurelabs
```

#### 2. 使用 Nginx 反向代理

创建 Nginx 配置 `/etc/nginx/sites-available/figurelabs`:

```nginx
server {
    listen 80;
    server_name your-domain.com;

    location / {
        proxy_pass http://127.0.0.1:7860;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }

    location /api {
        proxy_pass http://127.0.0.1:7860;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
    }
}
```

启用配置:

```bash
sudo ln -s /etc/nginx/sites-available/figurelabs /etc/nginx/sites-enabled/
sudo nginx -t
sudo systemctl reload nginx
```

---

## 代码结构

### 项目目录树

```
figurelabs-ai/
├── src/                          # 后端源码
│   ├── core/                     # 核心模块
│   │   ├── storage.py           # 存储抽象层 (SQLite/PostgreSQL)
│   │   └── database.py          # 统计数据库
│   ├── api/                      # API 层
│   │   ├── routers/             # 路由模块
│   │   │   ├── accounts.py      # 账户管理路由
│   │   │   ├── chat.py          # 对话路由
│   │   │   └── stats.py         # 统计路由
│   │   ├── schemas/             # Pydantic 模型
│   │   ├── app.py               # FastAPI 主应用
│   │   └── factory.py           # 应用工厂
│   ├── chat/                     # 对话模块
│   ├── export/                   # 导出模块
│   ├── register/                 # 注册模块
│   ├── config.py                 # 配置管理
│   └── db.py                     # 数据库操作
│
├── frontend/                     # 前端源码
│   ├── src/
│   │   ├── components/
│   │   │   ├── DashboardPage.jsx        # 仪表盘
│   │   │   ├── MonitorPage.jsx          # 监控页面
│   │   │   ├── LogsPage.jsx             # 日志页面
│   │   │   └── ...
│   │   ├── store.js             # Zustand 状态管理
│   │   └── App.jsx              # 主应用
│   └── package.json
│
├── data/                         # 数据目录
├── docs/                         # 文档
├── .env.example                  # 环境变量示例
├── requirements.txt              # Python 依赖
└── README.md                    # 项目文档
```

### 核心模块说明

#### 1. 存储抽象层 (`src/core/storage.py`)

提供统一的数据库访问接口：

```python
# 账户管理
await load_accounts()           # 加载所有账户
await save_accounts(accounts)   # 保存账户列表

# 设置管理
await load_settings()           # 加载设置
await save_settings(settings)   # 保存设置
```

**设计模式**:
- 工厂模式：根据环境变量自动选择后端
- 连接池：自动管理数据库连接
- 事务支持：PostgreSQL 使用异步事务

#### 2. 统计数据库 (`src/core/database.py`)

管理请求日志和统计分析：

```python
from src.core.database import stats_db

# 插入日志
await stats_db.insert_request_log(
    timestamp=time.time(),
    model="gemini-pro",
    ttfb_ms=100,
    total_ms=500,
    status="success"
)

# 获取统计
stats = await stats_db.get_stats_by_time_range("24h")
```

#### 3. API 路由 (`src/api/routers/`)

模块化的路由结构：

```python
# accounts.py - 账户管理
@app.get("/api/accounts")           # 列出账户
@app.post("/api/accounts/register") # 注册账户

# chat.py - 对话管理
@app.post("/api/session")           # 创建会话
@app.post("/api/message")           # 发送消息

# stats.py - 统计数据
@app.get("/api/stats")              # 时间范围统计
```

---

## API 文档

### 账户管理

#### `GET /api/accounts`
获取所有账户列表

**Response**:
```json
[
  {
    "id": 1,
    "user_id": "abc123",
    "email": "user@example.com",
    "access_token": "token...",
    "mail_service": "mailtm",
    "created_at": 1718611200
  }
]
```

#### `POST /api/accounts/register`
注册新账户

**Request**:
```json
{
  "mail_service": "mailtm"
}
```

### 统计数据

#### `GET /api/stats?time_range=24h`
获取统计数据

**参数**:
- `time_range`: `24h` | `7d` | `30d`

**Response**:
```json
{
  "labels": ["00:00", "01:00", ...],
  "total_requests": [10, 15, ...],
  "failed_requests": [1, 0, ...]
}
```

---

## 配置说明

### 环境变量

创建 `.env` 文件：

```env
# 数据库配置
DATABASE_URL=                     # PostgreSQL URL (可选)
SQLITE_PATH=data/data.db          # SQLite 路径 (默认)

# 服务配置
PORT=7860                         # 服务端口
```

### 切换数据库

项目会自动检测配置：
1. 如果设置了 `DATABASE_URL`，使用 PostgreSQL
2. 否则使用 SQLite (默认路径: `data/data.db`)

---

## 开发指南

### 运行测试

```bash
# 测试存储层
python test_refactor.py

# 测试 API
python test_api_endpoints.py
```

### 添加新的 API 端点

1. 在 `src/api/routers/` 创建路由文件
2. 在 `src/api/app.py` 注册路由

### 添加新的前端页面

1. 在 `frontend/src/components/` 创建组件
2. 在 `frontend/src/App.jsx` 添加路由

---

## 常见问题

### Q: 如何切换数据库？
A: 设置 `DATABASE_URL` 环境变量即可。

### Q: 如何备份数据？
A: 复制 `data/data.db` 文件。

### Q: 前端如何代理 API？
A: Vite 会自动将 `/api` 请求代理到后端。

---

## 许可证

MIT License

---

**Made with ❤️ by FigureLabs Team**
