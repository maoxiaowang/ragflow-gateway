#!/bin/bash
set -e

[ -n "$LOG_DIR" ] && mkdir -p "$LOG_DIR"
[ -n "$UPLOAD_DIR" ] && mkdir -p "$UPLOAD_DIR"

# 执行数据库迁移
alembic upgrade head

exec "$@"