#!/usr/bin/env python3
"""
Minimal ping agent for K-Terrarium POC.

A simple HTTP server that:
- Responds to /health with 200 OK
- Responds to /ping with agent info
- Logs activity to stdout
"""

import json
import os
import socket
import sys
from datetime import datetime, timezone
from http.server import BaseHTTPRequestHandler, HTTPServer


class PingHandler(BaseHTTPRequestHandler):
    """Handle health check and ping requests."""

    def log_message(self, format: str, *args) -> None:
        """Log to stdout with timestamp."""
        timestamp = datetime.now(timezone.utc).isoformat()
        print(f"[{timestamp}] {format % args}", flush=True)

    def do_GET(self) -> None:
        if self.path == "/health":
            self._send_response(200, {"status": "healthy"})
        elif self.path == "/ping":
            self._send_response(
                200,
                {
                    "agent": "ping-agent",
                    "hostname": socket.gethostname(),
                    "pod_name": os.environ.get("POD_NAME", "unknown"),
                    "namespace": os.environ.get("POD_NAMESPACE", "unknown"),
                    "timestamp": datetime.now(timezone.utc).isoformat(),
                },
            )
        else:
            self._send_response(404, {"error": "not found"})

    def _send_response(self, status: int, body: dict) -> None:
        self.send_response(status)
        self.send_header("Content-Type", "application/json")
        self.end_headers()
        self.wfile.write(json.dumps(body).encode())


def main() -> None:
    port = int(os.environ.get("PORT", "8080"))
    server = HTTPServer(("0.0.0.0", port), PingHandler)
    print(
        f"[{datetime.now(timezone.utc).isoformat()}] Ping agent starting on port {port}",
        flush=True,
    )
    print(
        f"[{datetime.now(timezone.utc).isoformat()}] Hostname: {socket.gethostname()}",
        flush=True,
    )
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        print(
            f"\n[{datetime.now(timezone.utc).isoformat()}] Shutting down...", flush=True
        )
        server.shutdown()


if __name__ == "__main__":
    main()
