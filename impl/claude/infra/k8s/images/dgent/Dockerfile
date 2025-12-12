# D-gent Dockerfile
#
# Builds the D-gent server image for state management sidecar.
# Designed to run as a sidecar container in agent pods, providing:
# - Key-value state CRUD with versioning (optimistic concurrency)
# - Namespace isolation for multi-agent pods
# - Checkpoint/restore for durability
#
# Usage:
#   docker build -t kgents/dgent:latest -f impl/claude/infra/k8s/images/dgent/Dockerfile .
#   kind load docker-image kgents/dgent:latest --name kgents-terrarium
#
# As sidecar:
#   env: DGENT_CHECKPOINT_DIR=/data/state
#   volumeMount: agent-state:/data/state
#
# AGENTESE: self.dgent.container.define

FROM python:3.12-slim

LABEL org.opencontainers.image.title="D-gent Server"
LABEL org.opencontainers.image.description="Cluster-native state management sidecar"
LABEL org.opencontainers.image.vendor="kgents"

# Install system dependencies (minimal - no Claude CLI needed)
RUN apt-get update && apt-get install -y --no-install-recommends \
    curl \
    ca-certificates \
    && rm -rf /var/lib/apt/lists/*

# Create non-root user
RUN useradd -m -u 1000 -s /bin/bash agent
WORKDIR /app

# Install Python dependencies (minimal set for D-gent)
RUN pip install --no-cache-dir \
    fastapi>=0.100.0 \
    uvicorn>=0.23.0 \
    pydantic>=2.0.0

# Copy kgents package (D-gent only needs agents.d)
COPY impl/claude /app/impl/claude
WORKDIR /app/impl/claude

# Set Python path
ENV PYTHONPATH=/app/impl/claude
ENV PYTHONUNBUFFERED=1

# D-gent specific configuration
ENV DGENT_PORT=8081
ENV DGENT_HOST=0.0.0.0

# State checkpoint directory (mount a volume here for persistence)
# If not mounted, state is ephemeral (in-memory only)
ENV DGENT_CHECKPOINT_DIR=/data/state

# Create state directory (will be replaced by volume mount in K8s)
RUN mkdir -p /data/state && chown agent:agent /data/state

# Expose port (different from U-gent to allow sidecar pattern)
EXPOSE 8081

# Health check
HEALTHCHECK --interval=30s --timeout=5s --start-period=5s --retries=3 \
    CMD curl -f http://localhost:8081/health || exit 1

# Switch to non-root user
USER agent

# Run D-gent server
CMD ["python", "-m", "agents.d.server"]
