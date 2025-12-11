# Minimal ping agent for K-Terrarium POC
# Stays alive and responds to health checks
FROM python:3.12-slim

LABEL org.opencontainers.image.title="kgents-ping-agent"
LABEL org.opencontainers.image.description="Minimal ping agent for K-Terrarium POC"

# Create non-root user with UID 1000 (matches K8s runAsUser)
RUN groupadd -g 1000 kgents && useradd -u 1000 -g kgents kgents

WORKDIR /app

# Copy the agent script with correct ownership
COPY --chown=1000:1000 ping_agent.py /app/

# Ensure file is readable
RUN chmod 644 /app/ping_agent.py

USER 1000

HEALTHCHECK --interval=10s --timeout=3s --start-period=5s \
    CMD python -c "import urllib.request; urllib.request.urlopen('http://localhost:8080/health')" || exit 1

EXPOSE 8080

CMD ["python", "ping_agent.py"]
