"""
Cortex Service - The gRPC Daemon for the Glass Terminal.

The Cortex is the living brain of K-Terrarium. It implements the Logos service
defined in logos.proto, handling all AGENTESE path resolution.

The CLI is a hollow shell - it parses arguments, makes gRPC calls to Cortex,
and formats output. All business logic lives here.

Components:
    CortexServicer - gRPC service implementation
    CortexDaemon - Background daemon runner

Principle: The CLI should be rewritable in 20 lines of Go.
All complexity lives in the Cortex daemon.
"""

from .daemon import (
    CortexDaemon,
    run_daemon,
)
from .service import (
    CortexServicer,
    InvokeResult,
    LogosServicer,
    StatusData,
    TitheResult,
    create_cortex_servicer,
)

__all__ = [
    "CortexServicer",
    "LogosServicer",
    "create_cortex_servicer",
    "StatusData",
    "InvokeResult",
    "TitheResult",
    "CortexDaemon",
    "run_daemon",
]
