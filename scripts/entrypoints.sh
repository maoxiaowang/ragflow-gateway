#!/bin/bash
# 执行数据库迁移
alembic upgrade head
# 启动 FastAPI
exec uvicorn src.app.main:app --host 0.0.0.0 --port 8000 --workers 4