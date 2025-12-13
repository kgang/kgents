# Synapse CDC Processor Image
#
# The morphism between Postgres and Qdrant:
# - Polls outbox for change events
# - Computes embeddings
# - Upserts to Qdrant
# - Reports metrics (Prometheus-compatible)
#
# Usage:
#   docker build -t kgents/synapse:latest -f impl/claude/infra/k8s/images/synapse/Dockerfile impl/claude
#   kind load docker-image kgents/synapse:latest --name kgents-triad
#
# AGENTESE: self.vitals.synapse

FROM python:3.12-slim

LABEL org.opencontainers.image.title="kgents Synapse"
LABEL org.opencontainers.image.description="CDC processor for Database Triad"
LABEL org.opencontainers.image.vendor="kgents"
LABEL kgents.io/triad-role="synapse"

# Install system dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    curl \
    ca-certificates \
    && rm -rf /var/lib/apt/lists/*

# Create non-root user
RUN useradd -m -u 1000 -s /bin/bash synapse
WORKDIR /app

# Install Python dependencies
RUN pip install --no-cache-dir \
    asyncpg>=0.29.0 \
    qdrant-client>=1.7.0 \
    openai>=1.0.0 \
    httpx>=0.25.0 \
    pydantic>=2.0.0

# Copy only what's needed for Synapse
# Minimal footprint for CronJob

# Create minimal directory structure
RUN mkdir -p /app/agents/flux /app/protocols/terrarium

# Copy Synapse modules
COPY agents/flux/synapse.py /app/agents/flux/synapse.py
COPY agents/flux/synapse_runner.py /app/agents/flux/synapse_runner.py
COPY agents/flux/dlq.py /app/agents/flux/dlq.py
COPY agents/flux/circuit_breaker.py /app/agents/flux/circuit_breaker.py

# Create minimal agents/__init__.py (avoid importing all modules)
RUN echo '"""Minimal agents package for Synapse."""' > /app/agents/__init__.py

# Create minimal agents/flux/__init__.py (empty - synapse_runner is self-contained)
RUN echo '"""Minimal flux package for Synapse CDC."""' > /app/agents/flux/__init__.py

# Also need protocols for semantic metrics (optional)
COPY protocols/terrarium/semantic_metrics.py /app/protocols/terrarium/semantic_metrics.py

# Create minimal protocols/__init__.py
RUN echo '"""Minimal protocols package for Synapse."""' > /app/protocols/__init__.py

# Create minimal protocols/terrarium/__init__.py
RUN echo '"""Minimal terrarium package for Synapse."""' > /app/protocols/terrarium/__init__.py

# Fix permissions for synapse user
RUN chown -R synapse:synapse /app

# Set PYTHONPATH
ENV PYTHONPATH=/app
ENV PYTHONUNBUFFERED=1

# Switch to non-root user
USER synapse

# Default: single batch mode (CronJob)
# Override with --continuous for Deployment mode
CMD ["python", "-m", "agents.flux.synapse_runner"]
