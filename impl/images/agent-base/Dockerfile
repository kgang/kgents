# Base image for kgents agents
# Minimal Python 3.12 with common agent dependencies
FROM python:3.12-slim

# Labels
LABEL org.opencontainers.image.title="kgents-agent-base"
LABEL org.opencontainers.image.description="Base image for kgents agents"
LABEL org.opencontainers.image.source="https://github.com/kgang/kgents"

# Create non-root user for security
RUN groupadd -r kgents && useradd -r -g kgents kgents

# Install minimal dependencies
RUN pip install --no-cache-dir \
    aiohttp>=3.9.0 \
    pydantic>=2.5.0

# Set up working directory
WORKDIR /app

# Copy agent code (placeholder - will be mounted or copied in derived images)
# COPY --chown=kgents:kgents . /app

# Switch to non-root user
USER kgents

# Health check endpoint
HEALTHCHECK --interval=30s --timeout=5s --start-period=10s \
    CMD python -c "print('healthy')" || exit 1

# Default command (override in derived images)
CMD ["python", "-c", "print('kgents agent base - override CMD in derived image')"]
