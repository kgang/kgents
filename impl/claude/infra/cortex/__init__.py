"""
Cortex Service - The gRPC Daemon for the Glass Terminal.

The Cortex is the living brain of K-Terrarium. It implements the Logos service
defined in logos.proto, handling all AGENTESE path resolution.

The CLI is a hollow shell - it parses arguments, makes gRPC calls to Cortex,
and formats output. All business logic lives here.

Components:
    CortexServicer - gRPC service implementation (slimmed down in v2.0)
    LogosResolver - Stateless AGENTESE → K8s translation (new in v2.0)
    CortexDaemon - Background daemon runner
    CognitiveProbe - LLM health checks beyond HTTP 200
    Path Agents - LLM-backed AGENTESE path handlers

K8-Terrarium v2.0 Architectural Changes:
    - LogosResolver extracts K8s translation from CortexServicer
    - CortexServicer delegates world.cluster.* paths to LogosResolver
    - Pheromone intensity calculated on read (Passive Stigmergy)

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
from .logos_resolver import (
    ONTOLOGY_MAP,
    Handle,
    LogosResolver,
    create_logos_resolver,
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
    # LogosResolver (v2.0)
    "LogosResolver",
    "create_logos_resolver",
    "Handle",
    "ONTOLOGY_MAP",
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
