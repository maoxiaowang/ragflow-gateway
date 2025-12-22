# Ragflow Gateway 开发指南

本文档为项目开发人员提供快速上手和开发流程参考。

---

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

### 4. 开发模式运行
```shell
uvicorn main:app --reload
```