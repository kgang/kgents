"""
N-gents: The Narrative Substrate.

N-gents separate recording (The Historian) from telling (The Bard).

Philosophy:
    The event is the stone. The story is the shadow.
    Collect stones. Cast shadows only when the sun is out.

The Correction:
    Story is a Read-Time projection, not a Write-Time artifact.
    The Historian is silent. The Bard speaks.

Phase 1 Components (Write-Time):
- SemanticTrace: The Crystal - pure data, no prose
- Historian: Invisible crystal collection
- CrystalStore: Crystal persistence
- HistorianTap: Wire protocol integration
- DgentCrystalStore: D-gent backed persistence

Phase 2 Components (Read-Time):
- NarrativeGenre: Genre determines voice and style
- Verbosity: How much detail to include
- NarrativeRequest: Request to the Bard
- Chapter: Coherent narrative unit
- Narrative: The Bard's output
- Bard: The storyteller agent
- ForensicBard: Crash diagnosis specialist

Future Phases:
- Phase 3: EchoChamber (replay simulation)
- Phase 4: Chronicle (multi-agent weaving)
- Phase 5: Integrations (D/L/M/I/B-gent)

Example (Phase 1 - Recording):
    >>> from agents.n import Historian, MemoryCrystalStore, SemanticTrace
    >>>
    >>> store = MemoryCrystalStore()
    >>> historian = Historian(store)
    >>>
    >>> # Begin recording (called by runtime, not agent)
    >>> ctx = historian.begin_trace(agent, input_data)
    >>>
    >>> # ... agent executes ...
    >>>
    >>> # End recording
    >>> crystal = historian.end_trace(ctx, "INVOKE", outputs)

Example (Phase 2 - Storytelling):
    >>> from agents.n import Bard, NarrativeRequest, NarrativeGenre
    >>>
    >>> bard = Bard(llm=my_llm_provider)
    >>> request = NarrativeRequest(
    ...     traces=crystals,
    ...     genre=NarrativeGenre.NOIR,
    ... )
    >>> narrative = await bard.invoke(request)
    >>> print(narrative.render("markdown"))

Wire Protocol Integration:
    >>> from agents.n import HistorianTap, WireIntegration
    >>>
    >>> tap = HistorianTap(historian)
    >>>
    >>> # On each wire frame:
    >>> frame = await tap.on_frame(incoming_frame)
"""

# Core Types
from .types import (
    Action,
    Determinism,
    SemanticTrace,
    TraceContext,
)

# Historian (Write-Time)
from .historian import (
    Historian,
    Traceable,
    TracingContext,
)

# Crystal Storage
from .store import (
    CrystalStore,
    CrystalStats,
    MemoryCrystalStore,
    compute_stats,
)

# Wire Protocol Integration
from .tap import (
    FrameType,
    HistorianTap,
    WireFrame,
    WireIntegration,
)

# D-gent Backed Storage
from .dgent_store import (
    DgentCrystalStore,
    SimpleDgentCrystalStore,
)

# Bard (Phase 2 - Read-Time Storytelling)
from .bard import (
    Bard,
    Chapter,
    Diagnosis,
    ForensicBard,
    LLMProvider,
    Narrative,
    NarrativeGenre,
    NarrativeRequest,
    Perspective,
    SimpleLLMProvider,
    Verbosity,
)

__all__ = [
    # Core Types
    "Action",
    "Determinism",
    "SemanticTrace",
    "TraceContext",
    # Historian
    "Historian",
    "Traceable",
    "TracingContext",
    # Storage
    "CrystalStore",
    "CrystalStats",
    "MemoryCrystalStore",
    "compute_stats",
    # Wire Integration
    "FrameType",
    "HistorianTap",
    "WireFrame",
    "WireIntegration",
    # D-gent Storage
    "DgentCrystalStore",
    "SimpleDgentCrystalStore",
    # Bard (Phase 2)
    "Bard",
    "Chapter",
    "Diagnosis",
    "ForensicBard",
    "LLMProvider",
    "Narrative",
    "NarrativeGenre",
    "NarrativeRequest",
    "Perspective",
    "SimpleLLMProvider",
    "Verbosity",
]
