# ============================================================================
# Multi-Stage Dockerfile for ML Model Serving
# ============================================================================
# Stage 1: Builder - Installs dependencies and trains model
# Stage 2: Production - Lightweight runtime image
# ============================================================================

# ============================================================================
# STAGE 1: BUILDER
# Purpose: Install dependencies, compile packages, train model
# This stage is LARGE but gets discarded!
# ============================================================================
FROM python:3.12-slim as builder

# Set working directory
WORKDIR /build

# Install system dependencies needed for building Python packages
RUN apt-get update && apt-get install -y --no-install-recommends \
    gcc \
    g++ \
    make \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements
COPY requirements-docker.txt .

# Install Python dependencies in a virtual environment
# Using venv allows us to copy just the packages to production
RUN python -m venv /opt/venv
ENV PATH="/opt/venv/bin:$PATH"

# Install dependencies
RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir -r requirements-docker.txt

# Copy source code
COPY . .

# Train the model (or use existing artifacts)
# This ensures we have a trained model in the image
RUN python -c "print('Model artifacts already included')" || \
    python main_pipeline.py

# ============================================================================
# STAGE 2: PRODUCTION
# Purpose: Lightweight runtime image
# Only includes what's needed to run the API
# ============================================================================
FROM python:3.12-slim

# Metadata labels
LABEL maintainer="your-email@example.com"
LABEL description="Housing Price Prediction ML API"
LABEL version="1.0.0"

# Create non-root user for security
RUN useradd -m -u 1000 -s /bin/bash mluser

# Set working directory
WORKDIR /app

# Copy virtual environment from builder
COPY --from=builder /opt/venv /opt/venv

# Copy only necessary files from builder
COPY --from=builder /build/app.py .
COPY --from=builder /build/src ./src
COPY --from=builder /build/models ./models
COPY --from=builder /build/config ./config

# Set environment variables
ENV PATH="/opt/venv/bin:$PATH" \
    PYTHONUNBUFFERED=1 \
    PORT=5000 \
    REDIS_HOST=redis \
    REDIS_PORT=6379

# Change ownership to non-root user
RUN chown -R mluser:mluser /app

# Switch to non-root user
USER mluser

# Expose port
EXPOSE 5000

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=40s --retries=3 \
    CMD python -c "import requests; requests.get('http://localhost:5000/health')" || exit 1

# Run with Gunicorn (production WSGI server)
# 4 workers = good for CPU-bound ML tasks
CMD ["gunicorn", "--bind", "0.0.0.0:5000", "--workers", "4", "--timeout", "120", "--access-logfile", "-", "--error-logfile", "-", "app:app"]

# For development, use Flask dev server instead:
# CMD ["python", "app.py"]