# kgents SaaS API Image
#
# FastAPI application serving K-gent Soul, AGENTESE, and Sessions APIs
# with multi-tenant support, metering, and SaaS infrastructure.
#
# Usage:
#   docker build -t kgents/api:latest -f impl/claude/infra/k8s/images/api/Dockerfile impl/claude
#   kind load docker-image kgents/api:latest --name kgents-triad
#
# AGENTESE: world.gateway.api

FROM python:3.12-slim

LABEL org.opencontainers.image.title="kgents API"
LABEL org.opencontainers.image.description="SaaS API for kgents platform"
LABEL org.opencontainers.image.vendor="kgents"
LABEL kgents.io/component="api"

# Install system dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    curl \
    ca-certificates \
    && rm -rf /var/lib/apt/lists/*

# Create non-root user
RUN useradd -m -u 1000 -s /bin/bash kgents
WORKDIR /app

# Install Python dependencies
# Core API dependencies
RUN pip install --no-cache-dir \
    fastapi>=0.115.0 \
    uvicorn>=0.32.0 \
    httpx>=0.27.0 \
    pydantic>=2.0.0 \
    aiosqlite>=0.20.0 \
    pyyaml>=6.0 \
    jinja2>=3.1.0 \
    # NATS client
    nats-py>=2.7.0 \
    # OpenTelemetry
    opentelemetry-api>=1.24.0 \
    opentelemetry-sdk>=1.24.0 \
    opentelemetry-exporter-otlp>=1.24.0 \
    opentelemetry-instrumentation-fastapi>=0.45b0 \
    # Prometheus metrics
    prometheus-client>=0.20.0 \
    # Stripe webhooks
    stripe>=8.0.0

# Copy application code
# Copy bootstrap (foundational types)
COPY bootstrap/ /app/bootstrap/

# Copy the entire protocols package (API, billing, config, etc.)
COPY protocols/ /app/protocols/

# Copy agents package (for K-gent Soul)
COPY agents/ /app/agents/

# Copy shared utilities
COPY shared/ /app/shared/

# Copy runtime (if needed)
COPY runtime/ /app/runtime/

# Create __init__.py files for proper module discovery
RUN echo '"""kgents application package."""' > /app/__init__.py

# Fix permissions
RUN chown -R kgents:kgents /app

# Set PYTHONPATH
ENV PYTHONPATH=/app
ENV PYTHONUNBUFFERED=1

# API configuration
ENV API_HOST=0.0.0.0
ENV API_PORT=8000

# SaaS configuration (override via K8s secrets/configmap)
ENV NATS_SERVERS=nats://nats.kgents-agents.svc.cluster.local:4222
ENV NATS_ENABLED=true
ENV REDIS_URL=redis://triad-redis.kgents-triad.svc.cluster.local:6379

# Switch to non-root user
USER kgents

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD curl -f http://localhost:8000/health || exit 1

# Expose API port
EXPOSE 8000

# Run API server
CMD ["python", "-m", "uvicorn", "protocols.api.app:create_app", "--factory", "--host", "0.0.0.0", "--port", "8000"]
