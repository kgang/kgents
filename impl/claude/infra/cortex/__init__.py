"""
Cortex Service - The gRPC Daemon for the Glass Terminal.

The Cortex is the living brain of K-Terrarium. It implements the Logos service
defined in logos.proto, handling all AGENTESE path resolution.

The CLI is a hollow shell - it parses arguments, makes gRPC calls to Cortex,
and formats output. All business logic lives here.

Components:
    CortexServicer - gRPC service implementation
    CortexDaemon - Background daemon runner
    CognitiveProbe - LLM health checks beyond HTTP 200
    Path Agents - LLM-backed AGENTESE path handlers

Principle: The CLI should be rewritable in 20 lines of Go.
All complexity lives in the Cortex daemon.

Phase F additions:
    - Cognitive probes for LLM health validation
    - LLM runtime integration via ClaudeCLIRuntime
    - Path agents for concept.define, concept.blend.forge, concept.refine
"""

from .daemon import (
    CortexDaemon,
    run_daemon,
)
from .probes import (
    CognitiveProbe,
    PathProbe,
    ProbeResult,
    ProbeStatus,
    ReasoningProbe,
    full_probe_suite,
    probe_runtime,
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
    # Service
    "CortexServicer",
    "LogosServicer",
    "create_cortex_servicer",
    "StatusData",
    "InvokeResult",
    "TitheResult",
    # Daemon
    "CortexDaemon",
    "run_daemon",
    # Probes (Phase F)
    "CognitiveProbe",
    "ReasoningProbe",
    "PathProbe",
    "ProbeResult",
    "ProbeStatus",
    "probe_runtime",
    "full_probe_suite",
]
