# RAGFlow Gateway
A simple RAGFlow platform

## 项目结构
```
ragflow-gateway/
├─ src/
│  └─ app/
│     ├─ api/                   # 业务接口层
│     │  ├─ v1/                 # API 版本
│     │  │  ├─ auth/
│     │  │  │  ├─ desp.py       # 模块依赖
│     │  │  │  ├─ routes.py     # 模块路由
│     │  │  │  ├─ schemas.py    # 模块DTO
│     │  │  ├─ iam/             # 身份与访问管理
│     │  │  ├─ ragflow/
│     ├─ cli/                   # 命令行脚本
│     ├─ conf/                  # 配置文件
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
> 没有指定运行目录的情况下，默认为项目根目录 `ragflow-gateway`。

### 2. 安装依赖
```shell
pip install uv
uv sync --python 3.13 --frozen

# 激活虚拟环境
.\.venv\Scripts\activate  #（Windows）
source ./.venv/
```

### 3. 配置环境变量文件
复制 `.env.example` 到 `.env`，并根据实际修改 `.env` 文件内容。

- secret key 可以通过下面办法生成 <br>
```python
import secrets
secret_key = secrets.token_urlsafe(32)
print(secret_key)
```

### 4. 运行路径

为了让项目正常运行，需要配置PythonPath。

- 命令行

```shell
$env:PYTHONPATH="src"  # Windows
export PYTHONPATH=src  # Linux
```
- PyCharm
  - 对于命令行，可在`Terminal`配置中添加上述环境变量。
  - 对于FastAPI，可以添加`Run Configuration`，并勾选`Add source roots to PYTHONPATH`。

### 4. 数据库迁移

- 执行迁移
```shell
# 生成迁移文件（首次或改动模型后）
alembic revision --autogenerate -m "initial"

# 执行迁移
alembic upgrade head
```
- 快速启动开发环境 PostgreSQL 和 Redis：<br>

> docker compose --env-file .env -f docker-compose.dev.yml up -d


### 5. 开发模式运行
```shell
uvicorn app.main:app --reload
```

### 6. 启动异步任务 worker（暂时无用）
```shell
taskiq worker app.tasks:broker
```

### 7. 初始化数据
初始化组和权限
```shell
cd src
python -m app.cli.init_perms
```

## 测试
打开浏览器输入 http://localhost:8000/docs

## 文档
- [开发手册](docs/development_guide.md)
- [生产环境](docs/deployment/production.md)
- [数据库迁移](docs/migration.md)
- [架构说明](docs/architecture/overview.md)
- [API 文档](docs/api.md)
