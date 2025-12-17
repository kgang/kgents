# Morpheus Gateway Dockerfile
#
# Builds the OpenAI-compatible LLM gateway with Claude CLI support.
#
# Usage:
#   docker build -t kgents/morpheus:latest -f impl/claude/infra/morpheus/Dockerfile .
#   kind load docker-image kgents/morpheus:latest --name kgents-terrarium
#
# AGENTESE: world.morpheus.container.define

FROM python:3.12-slim

LABEL org.opencontainers.image.title="Morpheus Gateway"
LABEL org.opencontainers.image.description="OpenAI-compatible LLM router for kgents"
LABEL org.opencontainers.image.vendor="kgents"

# Install system dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    curl \
    ca-certificates \
    && rm -rf /var/lib/apt/lists/*

# Install Claude CLI (if available in PATH at runtime)
# Note: In production, mount Claude auth via K8s Secret
# The CLI itself is expected to be available or the adapter falls back

# Create non-root user
RUN useradd -m -u 1000 -s /bin/bash morpheus
WORKDIR /app

# Install Python dependencies
COPY impl/claude/pyproject.toml /app/pyproject.toml

# Install minimal dependencies for Morpheus
RUN pip install --no-cache-dir \
    fastapi>=0.100.0 \
    uvicorn>=0.23.0 \
    httpx>=0.25.0 \
    pydantic>=2.0.0

# Copy application code
COPY impl/claude/infra/morpheus /app/infra/morpheus
COPY impl/claude/runtime /app/runtime
COPY impl/claude/bootstrap /app/bootstrap

# Set Python path
ENV PYTHONPATH=/app
ENV PYTHONUNBUFFERED=1

# Switch to non-root user
USER morpheus

# Expose ports
EXPOSE 8080 9090

# Health check
HEALTHCHECK --interval=30s --timeout=5s --start-period=10s --retries=3 \
    CMD curl -f http://localhost:8080/health || exit 1

# Run the server
CMD ["python", "-m", "infra.morpheus.server"]
