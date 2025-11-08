# Use Python 3.12 slim image as base
FROM python:3.12-slim as base

# Set working directory
WORKDIR /app

# Set environment variables
ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    UV_SYSTEM_PYTHON=1

# Install system dependencies
RUN apt-get update && apt-get install -y \
    gcc \
    g++ \
    bash \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Install uv
COPY --from=ghcr.io/astral-sh/uv:latest /uv /usr/local/bin/uv

# Copy dependency files
COPY pyproject.toml uv.lock ./

# Install dependencies using uv (faster and uses lock file)
RUN uv sync --frozen --no-dev

# Copy application code
COPY . .

# Copy and set up entrypoint script
COPY docker-entrypoint.sh /usr/local/bin/
RUN chmod +x /usr/local/bin/docker-entrypoint.sh

# Create necessary directories
RUN mkdir -p data images logs

# Expose port
EXPOSE 8000

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD uv run python -c "import urllib.request; urllib.request.urlopen('http://localhost:8000/')" || exit 1

# Use entrypoint script
ENTRYPOINT ["docker-entrypoint.sh"]

# Run the application using uv
CMD ["uv", "run", "uvicorn", "app:app", "--host", "0.0.0.0", "--port", "8000"]

