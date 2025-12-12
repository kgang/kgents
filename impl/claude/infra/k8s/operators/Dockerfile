# K8gents Operator Image
# Runs all three operators (Agent, Pheromone, Proposal) in a single pod.
# kopf handles multiplexing across multiple handler files.
#
# Build: docker build -t kgents/operator:latest -f impl/claude/infra/k8s/operators/Dockerfile .
# Run:   docker run kgents/operator:latest

FROM python:3.12-slim

LABEL maintainer="kgents"
LABEL description="K8gents Kubernetes Operator"

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    gcc \
    && rm -rf /var/lib/apt/lists/*

# Install Python dependencies
# kopf: Kubernetes operator framework
# kubernetes: K8s Python client
RUN pip install --no-cache-dir \
    kopf>=1.36.0 \
    kubernetes>=28.1.0

# Copy operator code preserving package structure
# The key insight: operator.py conflicts with Python stdlib 'operator' module
# Solution: Create k8s_types package with the base classes, patch imports at runtime

# Create package structure that mirrors the original
RUN mkdir -p /app/k8s/operators

# Copy operator base as k8s_types (NOT operator.py - that conflicts with stdlib)
COPY impl/claude/infra/k8s/operator.py /app/k8s/k8s_types.py

# Copy exceptions module (required by k8s_types)
COPY impl/claude/infra/k8s/exceptions.py /app/k8s/exceptions.py

# Create __init__.py that exports from k8s_types
RUN echo 'from .k8s_types import AgentPhase, AgentSpec, DeployMode, ReconcileResult' > /app/k8s/__init__.py

# Copy operators
COPY impl/claude/infra/k8s/operators/*.py /app/k8s/operators/

# Patch agent_operator.py to use new import path
RUN sed -i 's/from \.\.operator import/from k8s import/g' /app/k8s/operators/agent_operator.py

# Create operators __init__.py
RUN echo '"""K8s Operators."""' > /app/k8s/operators/__init__.py

# Set Python path for imports
ENV PYTHONPATH=/app
ENV PYTHONUNBUFFERED=1

# Health check - kopf exposes health on /healthz
HEALTHCHECK --interval=30s --timeout=5s --start-period=10s --retries=3 \
    CMD python -c "import urllib.request; urllib.request.urlopen('http://localhost:8080/healthz')" || exit 1

# Run all operators with kopf
CMD ["kopf", "run", \
     "/app/k8s/operators/agent_operator.py", \
     "/app/k8s/operators/pheromone_operator.py", \
     "/app/k8s/operators/proposal_operator.py", \
     "--all-namespaces", \
     "--liveness=http://0.0.0.0:8080/healthz"]
