# FastAPIProject
A simple FastAPI project.

## 项目结构
```
FastAPIProject/
├─ src/
│  └─ app/
│     ├─ api/                   # 业务接口层
│     │  ├─ v1/                 # API 版本
│     │  │  ├─ auth/
│     │  │  ├─ author/
│     │  │  ├─ book/
│     │  │  └─ category/
│     ├─ core/                  # 核心配置与通用工具
│     ├─ models/                # 数据库模型
│     ├─ repositories/          # 通用数据访问层
│     ├─ schemas/               # 通用DTO
│     ├─ services/              # 通用业务逻辑
├─ alembic/                     # 数据库迁移工具
│  ├─ env.py
│  └─ versions/                 # 迁移文件目录
├─ docs/                        # 项目文档
├─ .env.example                 # 环境变量配置示例
├─ .gitignore
├─ pyproject.toml               # 项目依赖及工具配置
└─ README.md                    # 项目说明文件
```

## 项目环境

- Python 3.13+
- `uv`（虚拟环境管理工具）
- 数据库：PostgreSQL
- Alembic（数据库迁移）
- Git（版本管理）
- Docker

---

## 快速开始

### 1. 克隆项目：
```bash
git clone https://github.com/maoxiaowang/ragflow-gateway
cd ragflow-gateway
```
### 2. 安装依赖
```shell
pip install uv
uv sync --python 3.13 --frozen
```

### 3. 数据库迁移
```shell
alembic upgrade head
```
> 启动开发环境 PostgreSQL 和 Redis：<br>
> docker-compose --env-file .env -f docker-compose.dev.yml up -d

### 4. 开发模式运行
```shell
uvicorn main:app --reload
```

### 5. 启动异步任务 worker
```shell
taskiq worker app.tasks:broker
```

## 测试
打开浏览器输入 http://localhost:8000/docs

## 文档
- [开发手册](docs/development_guide.md)
- [生产环境](docs/deployment/production.md)
- [数据库迁移](docs/migration.md)
- [架构说明](docs/architecture/overview.md)
- [API 文档](docs/api.md)
