# Agent Town Service - Dockerfile
#
# Standalone microservice for Agent Town with LLM dialogue.
#
# Build:
#   docker build -t kgents/town:latest -f infra/k8s/images/town/Dockerfile .
#
# Run:
#   docker run -p 8001:8001 \
#     -e MORPHEUS_URL=http://morpheus:8080/v1 \
#     -e REDIS_URL=redis://redis:6379 \
#     kgents/town:latest
#
# See: plans/velvety-mapping-puddle.md Phase 4

FROM python:3.12-slim

LABEL org.opencontainers.image.title="kgents Town Service"
LABEL org.opencontainers.image.description="Agent Town orchestration with LLM dialogue"
LABEL org.opencontainers.image.version="1.0.0"
LABEL kgents.io/component="town"

# Install system dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    curl \
    ca-certificates \
    && rm -rf /var/lib/apt/lists/*

# Create non-root user
RUN useradd -m -u 1000 -s /bin/bash kgents
WORKDIR /app

# Install Python dependencies
# Note: We install a minimal set here; full deps come from the copied code
RUN pip install --no-cache-dir \
    fastapi>=0.115.0 \
    uvicorn[standard]>=0.32.0 \
    httpx>=0.27.0 \
    pydantic>=2.0.0 \
    redis>=5.0.0 \
    openai>=1.0.0 \
    nats-py>=2.7.0 \
    opentelemetry-api>=1.24.0 \
    opentelemetry-sdk>=1.24.0 \
    opentelemetry-exporter-otlp>=1.24.0 \
    prometheus-client>=0.20.0 \
    websockets>=12.0

# Copy application code
# Structure matches the impl/claude layout
COPY agents/ /app/agents/
COPY protocols/ /app/protocols/
COPY shared/ /app/shared/
COPY runtime/ /app/runtime/
COPY bootstrap/ /app/bootstrap/

# Set ownership
RUN chown -R kgents:kgents /app

# Environment
ENV PYTHONPATH=/app
ENV PYTHONUNBUFFERED=1
ENV PORT=8001

# Default Morpheus URL (override in k8s deployment)
ENV MORPHEUS_URL=http://morpheus-gateway.kgents.svc.cluster.local:8080/v1
ENV REDIS_URL=redis://triad-redis.kgents-triad.svc.cluster.local:6379

# Switch to non-root user
USER kgents

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD curl -f http://localhost:8001/health || exit 1

# Expose port
EXPOSE 8001

# Run the server
CMD ["python", "-m", "uvicorn", "agents.town.server:app", "--host", "0.0.0.0", "--port", "8001"]
