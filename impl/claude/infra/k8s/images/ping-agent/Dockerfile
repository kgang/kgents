# Minimal Ping Agent for K-Terrarium POC
FROM python:3.12-slim

WORKDIR /app

# Create non-root user
RUN groupadd -r agent && useradd -r -g agent -u 1000 agent

# Install minimal dependencies
RUN pip install --no-cache-dir fastapi uvicorn pydantic

# Copy server code
COPY impl/claude/infra/k8s/images/ping-agent/server.py .

# Health check
HEALTHCHECK --interval=10s --timeout=3s --start-period=5s \
    CMD python -c "import urllib.request; urllib.request.urlopen('http://localhost:8080/health')" || exit 1

USER agent
EXPOSE 8080

CMD ["python", "server.py"]
