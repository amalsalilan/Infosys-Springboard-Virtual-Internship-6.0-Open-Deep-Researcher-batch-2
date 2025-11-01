FROM python:3.11-slim

ENV PYTHONUNBUFFERED=1 \
    LANGGRAPH_PROJECT_FILE=langgraph.json \
    UV_LINK_MODE=copy

RUN apt-get update \
    && apt-get install -y --no-install-recommends curl build-essential \
    && rm -rf /var/lib/apt/lists/*

RUN curl -LsSf https://astral.sh/uv/install.sh | sh \
    && mv /root/.local/bin/uv /usr/local/bin/uv \
    && rm -rf /root/.local

WORKDIR /app

COPY . .

RUN uv sync --locked --group dev \
    && useradd --create-home --shell /bin/bash app \
    && chown -R app:app /app

ENV PATH="/app/.venv/bin:${PATH}"

USER app

EXPOSE 2024

CMD ["langgraph", "dev", "--host", "0.0.0.0", "--port", "2024", "--allow-blocking"]
