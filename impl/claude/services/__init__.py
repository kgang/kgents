"""
Crown Jewel Services.

This directory contains the Crown Jewels - the flagship applications
that consume the categorical infrastructure in agents/.

Directory Structure:
- services/<jewel>/           # Crown Jewel service module
  - __init__.py               # Public API
  - persistence.py            # TableAdapter + D-gent integration
  - web/                      # Frontend components (if any)
  - _tests/                   # Service-specific tests

The Metaphysical Fullstack Pattern (AD-009):
- agents/ = categorical primitives (PolyAgent, Operad, Sheaf, Flux, D-gent)
- services/ = domain consumers (Brain, Witness, Foundry, Metabolism...)
- models/ = generic SQLAlchemy tables
- protocols/ = AGENTESE universal protocol (the API IS the protocol)

Key Rule: Adapters live in services/, not agents/ or handlers.
- Infrastructure doesn't know context (what tables are for, when to use them)
- Handlers are presentation (parsing only)
- Services own domain semantics (adapters, business logic, frontend components)

See: spec/principles.md AD-009, docs/skills/metaphysical-fullstack.md
"""

# Brain Crown Jewel
from .brain import (
    BrainManifestRendering,
    BrainNode,
    BrainPersistence,
    BrainStatus,
    CaptureRendering,
    CaptureResult,
    SearchRendering,
    SearchResult,
)

__all__ = [
    # Brain
    "BrainNode",
    "BrainManifestRendering",
    "CaptureRendering",
    "SearchRendering",
    "BrainPersistence",
    "BrainStatus",
    "CaptureResult",
    "SearchResult",
]
