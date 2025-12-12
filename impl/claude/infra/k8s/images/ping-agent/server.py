"""
Minimal Ping Agent for K-Terrarium POC.

A simple health-check agent to verify deployment infrastructure.
"""

import asyncio
import os
import time
from datetime import datetime

from fastapi import FastAPI
from pydantic import BaseModel

app = FastAPI(title="Ping Agent", version="0.1.0")

# Track start time for uptime
START_TIME = time.time()


class HealthResponse(BaseModel):
    status: str
    agent: str
    pod_name: str
    namespace: str
    uptime_seconds: float
    timestamp: str


class PingRequest(BaseModel):
    message: str = "ping"


class PingResponse(BaseModel):
    message: str
    echo: str
    latency_ms: float


@app.get("/health")
async def health() -> HealthResponse:
    """Health check endpoint."""
    return HealthResponse(
        status="healthy",
        agent="ping-agent",
        pod_name=os.environ.get("POD_NAME", "unknown"),
        namespace=os.environ.get("POD_NAMESPACE", "unknown"),
        uptime_seconds=time.time() - START_TIME,
        timestamp=datetime.utcnow().isoformat(),
    )


@app.post("/invoke")
async def invoke(request: PingRequest) -> PingResponse:
    """Echo back the message with latency measurement."""
    start = time.perf_counter()

    # Simulate minimal work
    await asyncio.sleep(0.001)

    latency = (time.perf_counter() - start) * 1000

    return PingResponse(
        message="pong",
        echo=request.message,
        latency_ms=latency,
    )


@app.get("/")
async def root() -> dict[str, object]:
    """Root endpoint."""
    return {
        "agent": "ping-agent",
        "version": "0.1.0",
        "endpoints": ["/health", "/invoke"],
    }


if __name__ == "__main__":
    import uvicorn

    port = int(os.environ.get("PORT", "8080"))
    uvicorn.run(app, host="0.0.0.0", port=port)
