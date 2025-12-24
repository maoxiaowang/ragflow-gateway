# ===== Stage 1: Build =====
FROM python:3.13.11-slim-trixie AS builder

WORKDIR /app

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

RUN pip config set global.index-url https://pypi.mirrors.ustc.edu.cn/simple
RUN pip install uv

COPY pyproject.toml uv.lock ./
RUN uv sync --frozen


# ===== Stage 2: Runtime =====
FROM python:3.13.11-slim-bookworm AS runtime

RUN useradd -m -s /bin/bash app

WORKDIR /ragflow-gateway
ENV HOME=/ragflow-gateway

# 复制 Python 依赖
COPY --from=builder /usr/local/lib/python3.13/site-packages /usr/local/lib/python3.13/site-packages
COPY --from=builder /usr/local/bin /usr/local/bin

# 复制源码和 Alembic
COPY src src
COPY alembic alembic

COPY entrypoint.sh /entrypoint.sh
RUN chmod +x /entrypoint.sh \
    && chown -R app:app /ragflow-gateway /entrypoint.sh

EXPOSE 8000

ENTRYPOINT ["/entrypoint.sh"]

USER app

CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000", "--workers", "4"]