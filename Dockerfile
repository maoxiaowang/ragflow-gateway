# ===== Stage 1: Build =====
FROM python:3.13.11-slim-trixie AS builder

WORKDIR /ragflow-gateway

RUN pip config set global.index-url https://pypi.mirrors.ustc.edu.cn/simple
RUN pip install uv

COPY pyproject.toml uv.lock ./
RUN uv sync --frozen


# ===== Stage 2: Runtime =====
FROM python:3.13.11-slim-trixie AS runtime

RUN useradd -m -s /bin/bash app

ENV HOME=/ragflow-gateway
ENV PYTHONPATH=/ragflow-gateway/src

WORKDIR $HOME

ENV PATH="$HOME/.venv/bin:$PATH"

COPY --from=builder $HOME/.venv .venv

COPY src src
COPY alembic alembic
COPY alembic.ini .

COPY scripts/entrypoint.sh /entrypoint.sh
RUN chmod +x /entrypoint.sh \
    && chown -R app:app $HOME /entrypoint.sh

EXPOSE 8000

USER app

ENTRYPOINT ["/entrypoint.sh"]

WORKDIR $HOME/src

CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]