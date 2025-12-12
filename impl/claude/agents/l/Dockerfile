# L-gent Container Image
# Semantic Registry with HTTP server for Kubernetes deployment.
#
# Build: docker build -t kgents/l-gent:latest -f impl/claude/agents/l/Dockerfile .
# Run:   docker run -p 8080:8080 kgents/l-gent:latest
#
# Environment variables:
#   LGENT_HOST      - Server host (default: 0.0.0.0)
#   LGENT_PORT      - Server port (default: 8080)
#   LGENT_MODE      - Operating mode (default: standalone)
#   DATABASE_URL    - PostgreSQL connection string (optional)
#
# Dependencies: Defined in __deps__.py, validated with:
#   python impl/claude/infra/scripts/build_agent_image.py agents.l --validate
#
# AGENTESE: world.library.container

FROM python:3.12-slim

LABEL maintainer="kgents"
LABEL description="L-gent Semantic Registry Server"

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    gcc \
    libpq-dev \
    && rm -rf /var/lib/apt/lists/*

# Install Python dependencies
# Core L-gent deps + PostgreSQL support
RUN pip install --no-cache-dir \
    aiosqlite>=0.20.0 \
    numpy>=1.24.0 \
    psycopg2-binary>=2.9.0

# Copy agents/l package (L-gent)
COPY impl/claude/agents/l/ /app/agents/l/

# Copy shared dependencies
# D-gent (for vector storage integration)
COPY impl/claude/agents/d/ /app/agents/d/
# A-gent base classes
COPY impl/claude/agents/a/ /app/agents/a/
# Bootstrap (core types required by D-gent)
COPY impl/claude/bootstrap/ /app/bootstrap/

# Create agents __init__.py
RUN echo '"""kgents agents package."""' > /app/agents/__init__.py

# Create minimal protocols stub (for CLI imports)
RUN mkdir -p /app/protocols/cli && \
    echo '"""protocols package."""' > /app/protocols/__init__.py && \
    echo '"""cli package."""' > /app/protocols/cli/__init__.py

# Create prism stub (minimal for CLICapable base class)
RUN echo '"""Minimal prism stub for container deployment."""' > /app/protocols/cli/prism.py && \
    echo 'from typing import Any, Callable' >> /app/protocols/cli/prism.py && \
    echo '' >> /app/protocols/cli/prism.py && \
    echo 'class CLICapable:' >> /app/protocols/cli/prism.py && \
    echo '    """Stub base class."""' >> /app/protocols/cli/prism.py && \
    echo '    pass' >> /app/protocols/cli/prism.py && \
    echo '' >> /app/protocols/cli/prism.py && \
    echo 'def expose(**kwargs: Any) -> Callable[[Any], Any]:' >> /app/protocols/cli/prism.py && \
    echo '    """Stub decorator."""' >> /app/protocols/cli/prism.py && \
    echo '    def decorator(fn: Any) -> Any:' >> /app/protocols/cli/prism.py && \
    echo '        return fn' >> /app/protocols/cli/prism.py && \
    echo '    return decorator' >> /app/protocols/cli/prism.py

# Set Python path for imports
ENV PYTHONPATH=/app
ENV PYTHONUNBUFFERED=1

# Expose HTTP port
EXPOSE 8080

# Health check
HEALTHCHECK --interval=30s --timeout=5s --start-period=10s --retries=3 \
    CMD python -c "import urllib.request; urllib.request.urlopen('http://localhost:8080/health')" || exit 1

# Run L-gent server
CMD ["python", "-m", "agents.l.server"]
