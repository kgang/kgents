# U-gent Dockerfile
#
# Builds the U-gent server image with:
# - Full kgents package for Soul library
# - FastAPI server for HTTP API
# - OpenAI SDK for Morpheus integration
#
# Usage:
#   docker build -t kgents/ugent:latest -f impl/claude/infra/k8s/images/ugent/Dockerfile .
#   kind load docker-image kgents/ugent:latest --name kgents-terrarium
#
# AGENTESE: world.ugent.container.define

FROM python:3.12-slim

LABEL org.opencontainers.image.title="U-gent Server"
LABEL org.opencontainers.image.description="Cluster-native tool execution with K-gent Soul integration"
LABEL org.opencontainers.image.vendor="kgents"

# Install system dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    curl \
    ca-certificates \
    && rm -rf /var/lib/apt/lists/*

# Create non-root user
RUN useradd -m -u 1000 -s /bin/bash agent
WORKDIR /app

# Install Python dependencies
RUN pip install --no-cache-dir \
    fastapi>=0.100.0 \
    uvicorn>=0.23.0 \
    httpx>=0.25.0 \
    pydantic>=2.0.0 \
    openai>=1.0.0

# Copy kgents package
COPY impl/claude /app/impl/claude
WORKDIR /app/impl/claude

# Set Python path
ENV PYTHONPATH=/app/impl/claude
ENV PYTHONUNBUFFERED=1

# U-gent specific configuration
ENV UGENT_PORT=8080
ENV UGENT_HOST=0.0.0.0

# Mount point for Claude auth (optional)
VOLUME /var/run/secrets/claude

# Expose port
EXPOSE 8080

# Health check
HEALTHCHECK --interval=30s --timeout=5s --start-period=10s --retries=3 \
    CMD curl -f http://localhost:8080/health || exit 1

# Switch to non-root user
USER agent

# Run U-gent server
CMD ["python", "-m", "agents.u.server"]
