# Agent Base Image
#
# Base Dockerfile for kgents agent pods. Includes:
# - Python 3.12 runtime
# - kgents package installed
# - FastAPI/uvicorn for HTTP agents
# - Claude CLI support (optional, via mounted auth)
#
# Usage:
#   docker build -t kgents/agent-base:latest -f impl/claude/infra/k8s/images/agent-base/Dockerfile .
#   kind load docker-image kgents/agent-base:latest --name kgents-terrarium
#
# For agent-specific images, use multi-stage builds:
#   FROM kgents/agent-base:latest
#   COPY agents/u/server.py /app/agents/u/
#   CMD ["python", "-m", "agents.u.server"]
#
# AGENTESE: world.agents.container.base

FROM python:3.12-slim

LABEL org.opencontainers.image.title="kgents Agent Base"
LABEL org.opencontainers.image.description="Base image for kgents agent pods"
LABEL org.opencontainers.image.vendor="kgents"

# Install system dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    curl \
    ca-certificates \
    && rm -rf /var/lib/apt/lists/*

# Create non-root user
RUN useradd -m -u 1000 -s /bin/bash agent
WORKDIR /app

# Install Python dependencies (minimal set for agents)
# The full pyproject.toml can be mounted or built on top
RUN pip install --no-cache-dir \
    fastapi>=0.100.0 \
    uvicorn>=0.23.0 \
    httpx>=0.25.0 \
    pydantic>=2.0.0 \
    openai>=1.0.0

# Copy kgents package
# Note: In production, use pip install from PyPI or private registry
COPY impl/claude /app/impl/claude
WORKDIR /app/impl/claude

# Install kgents package in editable mode
# This makes agents importable as: from agents.k import KgentSoul
ENV PYTHONPATH=/app/impl/claude

# Set runtime environment
ENV PYTHONUNBUFFERED=1

# Mount point for Claude auth (optional)
VOLUME /var/run/secrets/claude

# Default port for agent HTTP servers
EXPOSE 8080

# Health check (agents must implement /health endpoint)
HEALTHCHECK --interval=30s --timeout=5s --start-period=10s --retries=3 \
    CMD curl -f http://localhost:8080/health || exit 1

# Switch to non-root user
USER agent

# No default CMD - agent-specific images provide this
# Example CMD: ["python", "-m", "agents.u.server"]
