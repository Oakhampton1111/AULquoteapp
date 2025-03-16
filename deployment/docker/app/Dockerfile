# Build stage
FROM python:3.11-alpine AS builder

# Set build dependencies
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PIP_NO_CACHE_DIR=1 \
    PIP_DISABLE_PIP_VERSION_CHECK=1

# Install build dependencies
RUN apk add --no-cache \
    gcc \
    musl-dev \
    postgresql-dev \
    python3-dev \
    libffi-dev \
    openssl-dev

# Create virtual environment
RUN python -m venv /opt/venv
ENV PATH="/opt/venv/bin:$PATH"

# Install Python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Final stage
FROM python:3.11-alpine

# Copy virtual environment from builder
COPY --from=builder /opt/venv /opt/venv
ENV PATH="/opt/venv/bin:$PATH"

# Install runtime dependencies
RUN apk add --no-cache \
    postgresql-libs \
    redis \
    curl \
    && adduser -D appuser

# Set work directory and create necessary directories
WORKDIR /app
RUN mkdir -p /app/logs /app/static /app/templates \
    && chown -R appuser:appuser /app

# Copy wait-for-it script
COPY docker/wait-for-it.sh /usr/local/bin/
RUN chmod +x /usr/local/bin/wait-for-it.sh

# Copy only necessary files
COPY --chown=appuser:appuser alembic alembic/
COPY --chown=appuser:appuser alembic.ini .
COPY --chown=appuser:appuser app app/
COPY --chown=appuser:appuser prometheus.yml .

# Switch to non-root user
USER appuser

# Health check
HEALTHCHECK --interval=30s --timeout=30s --start-period=5s --retries=3 \
    CMD curl -f http://localhost:8000/health || exit 1

# Command to run the application
CMD ["wait-for-it.sh", "db", "redis", "uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
