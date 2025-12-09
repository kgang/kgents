"""
B-gents: Scientific Discovery Agents

Agents for scientific reasoning, hypothesis generation, and empirical inquiry.

Core themes:
- Falsifiability (Popperian epistemology)
- Epistemic humility
- Transparent reasoning
- Composition with other agent genera

Currently implemented:
- HypothesisEngine: Transforms observations into testable hypotheses
- Robin: Personalized scientific companion (composes K-gent + Hypothesis + Hegel)
- PersistentHypothesisStorage: D-gent backed hypothesis persistence with lineage
- Catalog Integration: L-gent registration and discovery for hypotheses
"""

from .hypothesis import (
    HypothesisEngine,
    HypothesisInput,
    HypothesisOutput,
    Hypothesis,
    NoveltyLevel,
    hypothesis_engine,
    rigorous_engine,
    exploratory_engine,
)

from .robin import (
    RobinAgent,
    RobinInput,
    RobinOutput,
    robin,
    robin_with_persona,
    quick_robin,
    fallback_robin,
)

from .persistent_hypothesis import (
    HypothesisMemory,
    HypothesisLineageEdge,
    PersistentHypothesisStorage,
    persistent_hypothesis_storage,
)

from .catalog_integration import (
    # Types
    HypothesisCatalogEntry,
    TestResult,
    # Registration
    register_hypothesis,
    register_hypothesis_batch,
    # Discovery
    find_hypotheses,
    find_related_hypotheses,
    # Lineage
    record_hypothesis_evolution,
    record_hypothesis_fork,
    get_hypothesis_lineage,
    # Metrics
    update_hypothesis_metrics,
    mark_hypothesis_falsified,
)

__all__ = [
    # HypothesisEngine
    "HypothesisEngine",
    "HypothesisInput",
    "HypothesisOutput",
    "Hypothesis",
    "NoveltyLevel",
    "hypothesis_engine",
    "rigorous_engine",
    "exploratory_engine",
    # Robin (scientific companion)
    "RobinAgent",
    "RobinInput",
    "RobinOutput",
    "robin",
    "robin_with_persona",
    "quick_robin",
    "fallback_robin",
    # Persistent Storage (D-gent integration)
    "HypothesisMemory",
    "HypothesisLineageEdge",
    "PersistentHypothesisStorage",
    "persistent_hypothesis_storage",
    # Catalog Integration (L-gent integration)
    "HypothesisCatalogEntry",
    "TestResult",
    "register_hypothesis",
    "register_hypothesis_batch",
    "find_hypotheses",
    "find_related_hypotheses",
    "record_hypothesis_evolution",
    "record_hypothesis_fork",
    "get_hypothesis_lineage",
    "update_hypothesis_metrics",
    "mark_hypothesis_falsified",
]
