# ===== Stage 1: Build =====
FROM python:3.12.12-slim AS builder

# 创建非 root 用户
RUN useradd -m -s /bin/bash app

WORKDIR /app

# 设置中科大 apt 源并安装系统依赖
RUN printf "Types: deb\n\
URIs: http://mirrors.ustc.edu.cn/debian\n\
Suites: trixie trixie-updates\n\
Components: main contrib non-free non-free-firmware\n\
Signed-By: /usr/share/keyrings/debian-archive-keyring.gpg\n\n\
Types: deb\n\
URIs: http://mirrors.ustc.edu.cn/debian-security\n\
Suites: trixie-security\n\
Components: main contrib non-free non-free-firmware\n\
Signed-By: /usr/share/keyrings/debian-archive-keyring.gpg\n" \
    > /etc/apt/sources.list.d/debian.sources

RUN apt-get update && \
    apt-get install -y --no-install-recommends build-essential libpq-dev && \
    rm -rf /var/lib/apt/lists/*

# 设置 pip 使用中科大源
RUN pip config set global.index-url https://pypi.mirrors.ustc.edu.cn/simple

# 复制依赖文件并安装 Python 包
COPY requirements.txt /app/
RUN pip install --upgrade pip && \
    pip install --no-cache-dir -r requirements.txt

# 复制源码和 Alembic
COPY src /app/src
COPY alembic /app/alembic

# ===== Stage 2: Runtime =====
FROM python:3.12.12-slim AS runtime

# 创建非 root 用户
RUN useradd -m -s /bin/bash app

WORKDIR /app/src

# 复制 Python 依赖
COPY --from=builder /usr/local/lib/python3.12/site-packages /usr/local/lib/python3.12/site-packages

# 复制源码和 Alembic
COPY --from=builder /app/src /app/src
COPY --from=builder /app/alembic /app/alembic

RUN mkdir -p /var/log/fastapi && chown -R app:app /var/log/fastapi

# 修改 /app 权限给 app 用户
RUN chown -R app:app /app

# 设置非 root 用户
USER app

EXPOSE 8000

# 默认启动 FastAPI
CMD ["python", "-m", "uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000", "--workers", "4"]