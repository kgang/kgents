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

Phase 3 Components (Replay):
- EchoMode: STRICT vs LUCID replay modes
- Echo: Simulation of a past trace
- EchoChamber: Replay engine with navigation
- LucidDreamer: Counterfactual exploration
- DriftReport: Model drift detection

Phase 4 Components (Multi-Agent):
- Interaction: Point where agent timelines intersect
- Chronicle: Multi-agent crystal weaving
- ChronicleBuilder: Fluent API for chronicles
- TimelineView: Single agent's timeline view
- CorrelationDetector: Interaction detection

Phase 5 Components (Integrations):
- IndexedCrystalStore: L-gent semantic indexing
- ResonantCrystalStore: M-gent holographic memory
- VisualizableBard: I-gent visualization support
- BudgetedBard: B-gent token budgeting
- NarrativeOrchestrator: Unified integration layer

Phase 6 Components (Epistemic Features):
- ConfidenceLevel: Discrete confidence levels
- ReliabilityAnnotation: Confidence + corroboration tracking
- UnreliableTrace: Trace with reliability metadata
- HallucinationType: Types of potential hallucination
- HallucinationIndicator: Signs of potential hallucination
- HallucinationDetector: Detects hallucination patterns
- UnreliableNarrative: Narrative with epistemic annotations
- UnreliableNarrator: Narrator with epistemic humility
- PerspectiveSpec: Configuration for one perspective
- Contradiction: Where perspectives disagree
- RashomonNarrative: Multiple perspectives on same events
- RashomonNarrator: Multi-perspective story generation
- GroundTruth: Verified fact for reconciliation
- ReconciliationResult: Ground truth comparison result
- GroundTruthReconciler: Compare narratives against facts

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

# Echo Chamber (Phase 3 - Replay)
from .echo_chamber import (
    CounterfactualResult,
    DriftReport,
    Echo,
    EchoChamber,
    EchoMode,
    LucidDreamer,
    SimpleDriftMeasurer,
    quick_drift_check,
)

# Chronicle (Phase 4 - Multi-Agent)
from .chronicle import (
    Chronicle,
    ChronicleBuilder,
    CorrelationDetector,
    Interaction,
    TimelineView,
)

# Integrations (Phase 5 - D/L/M/I/B-gent)
from .integrations import (
    BudgetedBard,
    CrystalMemoryPattern,
    IndexedCrystalStore,
    InsufficientBudgetError,
    NarrationCost,
    NarrativeOrchestrator,
    NarrativeVisualization,
    ResonantCrystalStore,
    VisualizableBard,
)

# Epistemic Features (Phase 6)
from .epistemic import (
    ConfidenceLevel,
    Contradiction,
    GroundTruth,
    GroundTruthReconciler,
    HallucinationDetector,
    HallucinationIndicator,
    HallucinationType,
    PerspectiveSpec,
    RashomonNarrative,
    RashomonNarrator,
    ReconciliationResult,
    ReliabilityAnnotation,
    UnreliableNarrative,
    UnreliableNarrator,
    UnreliableTrace,
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
    # Echo Chamber (Phase 3)
    "CounterfactualResult",
    "DriftReport",
    "Echo",
    "EchoChamber",
    "EchoMode",
    "LucidDreamer",
    "SimpleDriftMeasurer",
    "quick_drift_check",
    # Chronicle (Phase 4)
    "Chronicle",
    "ChronicleBuilder",
    "CorrelationDetector",
    "Interaction",
    "TimelineView",
    # Integrations (Phase 5)
    "BudgetedBard",
    "CrystalMemoryPattern",
    "IndexedCrystalStore",
    "InsufficientBudgetError",
    "NarrationCost",
    "NarrativeOrchestrator",
    "NarrativeVisualization",
    "ResonantCrystalStore",
    "VisualizableBard",
    # Epistemic Features (Phase 6)
    "ConfidenceLevel",
    "Contradiction",
    "GroundTruth",
    "GroundTruthReconciler",
    "HallucinationDetector",
    "HallucinationIndicator",
    "HallucinationType",
    "PerspectiveSpec",
    "RashomonNarrative",
    "RashomonNarrator",
    "ReconciliationResult",
    "ReliabilityAnnotation",
    "UnreliableNarrative",
    "UnreliableNarrator",
    "UnreliableTrace",
]
