FROM python:3.11-slim

WORKDIR /app

# Install system dependencies efficiently
RUN apt-get update && apt-get install -y \
    gcc \
    curl \
    && rm -rf /var/lib/apt/lists/* \
    && apt-get clean

# Create shared directory
RUN mkdir -p /app/shared

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY main.py .
COPY phase2_utils.py .
COPY http_client.py .

# Security: non-root user
RUN useradd --create-home --shell /bin/bash appuser \
    && chown -R appuser:appuser /app
USER appuser

EXPOSE 8080

# Optimized healthcheck
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=2 \
    CMD curl -f http://localhost:8080/health || exit 1

CMD ["python", "main.py"]
