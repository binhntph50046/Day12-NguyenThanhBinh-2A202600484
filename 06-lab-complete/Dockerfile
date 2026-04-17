# ============================================================
# Production Dockerfile — Multi-stage Build
# 
# Tại sao Multi-stage?
# - Stage 1 (builder): Compile dependencies (cần gcc, build tools)
# - Stage 2 (runtime): Chỉ copy kết quả, không cần build tools
# - Kết quả: Image nhỏ hơn 50-70% (< 500 MB)
# 
# Security:
# - Non-root user (agent:agent)
# - Minimal base image (python:3.11-slim)
# ============================================================

# ─────────────────────────────────────────────────────────
# Stage 1: Builder — Compile dependencies
# ─────────────────────────────────────────────────────────
FROM python:3.11-slim AS builder

WORKDIR /build

# Install build dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    gcc \
    libpq-dev \
    && rm -rf /var/lib/apt/lists/*

# Copy và install Python packages
COPY requirements.txt .
RUN pip install --no-cache-dir --user -r requirements.txt


# ─────────────────────────────────────────────────────────
# Stage 2: Runtime — Minimal production image
# ─────────────────────────────────────────────────────────
FROM python:3.11-slim AS runtime

# Tạo non-root user (security best practice)
RUN groupadd -r agent && useradd -r -g agent -d /app agent

WORKDIR /app

# Copy Python packages từ builder stage
COPY --from=builder /root/.local /home/agent/.local

# Copy application code
COPY app/ ./app/
COPY utils/ ./utils/

# Set ownership
RUN chown -R agent:agent /app

# Switch to non-root user
USER agent

# Environment variables
ENV PATH=/home/agent/.local/bin:$PATH
ENV PYTHONPATH=/app
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

EXPOSE 8000

# Health check — Platform sẽ restart nếu fail
HEALTHCHECK --interval=30s --timeout=10s --start-period=15s --retries=3 \
    CMD python -c \
    "import urllib.request; urllib.request.urlopen('http://localhost:8000/health')" \
    || exit 1

# Start application với 2 workers
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000", "--workers", "2"]
