# Terrarium Container Image
# The Agent Server Web Gateway for Kubernetes deployment.
#
# Build: docker build -t kgents/terrarium:latest -f impl/claude/protocols/terrarium/Dockerfile .
# Run:   docker run -p 8080:8080 -p 9090:9090 kgents/terrarium:latest
#
# Environment variables:
#   TERRARIUM_HOST              - Server host (default: 0.0.0.0)
#   TERRARIUM_PORT              - Server port (default: 8080)
#   TERRARIUM_METRICS_PORT      - Metrics port (default: 9090)
#   TERRARIUM_MIRROR_HISTORY    - Events in history (default: 100)
#   TERRARIUM_BROADCAST_TIMEOUT - Broadcast timeout in seconds (default: 0.1)
#   TERRARIUM_AUTO_DISCOVER     - Auto-discover agents (default: true)
#   TERRARIUM_SEMAPHORES_ENABLED - Enable semaphore handling (default: true)
#   TERRARIUM_PURGATORY_ENDPOINT - Expose /api/purgatory endpoints (default: true)
#   TERRARIUM_OBSERVE_AUTH      - Require auth for /observe (default: false)
#   TERRARIUM_PERTURB_AUTH      - Require auth for /perturb (default: true)
#
# K8s Integration:
#   The AgentServer CRD operator sets these environment variables from spec.
#   See: impl/claude/infra/k8s/crds/agentserver-crd.yaml
#
# AGENTESE: world.terrarium.container
# The Mirror Protocol: Observe Without Disturbing

FROM python:3.12-slim

LABEL maintainer="kgents"
LABEL description="Terrarium - Agent Server Web Gateway"
LABEL org.opencontainers.image.source="https://github.com/kgents/kgents"

# Create non-root user for security
RUN groupadd -r kgents && useradd -r -g kgents kgents

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    gcc \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Install Python dependencies
# FastAPI + uvicorn for web server
# httpx for async HTTP client
# numpy for metrics calculations
RUN pip install --no-cache-dir \
    fastapi>=0.115.0 \
    uvicorn>=0.32.0 \
    httpx>=0.27.0 \
    numpy>=1.24.0 \
    pydantic>=2.5.0

# Copy protocols package (terrarium + dependencies)
COPY impl/claude/protocols/terrarium/ /app/protocols/terrarium/
COPY impl/claude/protocols/__init__.py /app/protocols/

# Copy agents package (FluxAgent for registration)
COPY impl/claude/agents/flux/ /app/agents/flux/
COPY impl/claude/agents/a/ /app/agents/a/
COPY impl/claude/agents/__init__.py /app/agents/

# Copy bootstrap (core types)
COPY impl/claude/bootstrap/ /app/bootstrap/

# Create packages __init__.py files
RUN echo '"""kgents protocols package."""' > /app/protocols/__init__.py

# Set Python path for imports
ENV PYTHONPATH=/app
ENV PYTHONUNBUFFERED=1

# Default environment (can be overridden by K8s/CRD)
ENV TERRARIUM_HOST=0.0.0.0
ENV TERRARIUM_PORT=8080
ENV TERRARIUM_METRICS_PORT=9090
ENV TERRARIUM_SEMAPHORES_ENABLED=true
ENV TERRARIUM_PURGATORY_ENDPOINT=true

# Expose ports
# 8080: Main gateway (WebSocket + REST)
# 9090: Prometheus metrics
EXPOSE 8080 9090

# Health check (used by K8s liveness probe)
HEALTHCHECK --interval=30s --timeout=5s --start-period=15s --retries=3 \
    CMD curl --fail --silent http://localhost:8080/health || exit 1

# Switch to non-root user
USER kgents

# Run terrarium server
CMD ["python", "-m", "protocols.terrarium.server"]
