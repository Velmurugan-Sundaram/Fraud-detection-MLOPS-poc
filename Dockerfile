# Multi-stage Dockerfile for MLOps Fraud Detection POC
# Optimized for EC2 deployment with minimal image size

# Stage 1: Builder
FROM python:3.11-slim as builder

# Set working directory
WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    git \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements
COPY requirements.txt .

# Create virtual environment and install packages
RUN python -m venv /opt/venv
ENV PATH="/opt/venv/bin:$PATH"
RUN pip install --upgrade pip setuptools wheel && \
    pip install --no-cache-dir -r requirements.txt

# Stage 2: Runtime (minimal image)
FROM python:3.11-slim

# Set environment variables
ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    PATH="/opt/venv/bin:$PATH" \
    HOME=/app

# Create app user (security best practice)
RUN useradd -m -u 1000 appuser && \
    mkdir -p /app /data /logs && \
    chown -R appuser:appuser /app /data /logs

# Set working directory
WORKDIR /app

# Copy virtual environment from builder
COPY --from=builder --chown=appuser:appuser /opt/venv /opt/venv

# Copy project files
COPY --chown=appuser:appuser . .

# Create necessary directories for data and logs
RUN mkdir -p data/raw data/validated data/processed && \
    mkdir -p logs && \
    chown -R appuser:appuser data logs

# Switch to non-root user
USER appuser

# Expose ports (optional, for monitoring/API)
EXPOSE 8000 8501 9090

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD python -c "from src.ingestion.loader import DataLoader; print('Health check: OK')" || exit 1

# Default entrypoint - Run the data ingestion pipeline
ENTRYPOINT ["python"]
CMD ["-c", "from src.ingestion.pipeline import DataIngestionPipeline; import logging; logging.basicConfig(level=logging.INFO); p = DataIngestionPipeline(); p.run()"]
