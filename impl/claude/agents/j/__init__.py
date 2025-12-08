"""
J-gents: Just-in-Time Agent Intelligence

The letter J represents agents that embody JIT (Just-in-Time) intelligence:
the ability to classify reality, defer computation, compile ephemeral sub-agents,
and collapse safely when stability is threatened.

Philosophy:
> "Determine the nature of reality; compile the mind to match it; collapse to safety."

Core components:
- Promise[T]: Lazy computation with Ground fallback
- Reality: DETERMINISTIC | PROBABILISTIC | CHAOTIC classification
- RealityClassifier: Agent that classifies tasks
- Chaosmonger: AST-based stability analyzer (Phase 2)

See spec/j-gents/ for the full specification.
"""

from .chaosmonger import (
    Chaosmonger,
    StabilityConfig,
    StabilityInput,
    StabilityMetrics,
    StabilityResult,
    analyze_stability,
    check_stability,
    is_stable,
)
from .promise import (
    Promise,
    PromiseMetrics,
    PromiseState,
    child_promise,
    collect_metrics,
    promise,
)
from .reality import (
    ClassificationInput,
    ClassificationOutput,
    Reality,
    RealityClassifier,
    classify,
    classify_intent,
    classify_sync,
)

__all__ = [
    # Promise types
    "Promise",
    "PromiseState",
    "PromiseMetrics",
    # Promise helpers
    "promise",
    "child_promise",
    "collect_metrics",
    # Reality types
    "Reality",
    "ClassificationInput",
    "ClassificationOutput",
    # Reality agent
    "RealityClassifier",
    # Reality helpers
    "classify",
    "classify_intent",
    "classify_sync",
    # Stability types (Phase 2)
    "StabilityConfig",
    "StabilityInput",
    "StabilityMetrics",
    "StabilityResult",
    # Stability agent (Phase 2)
    "Chaosmonger",
    # Stability helpers (Phase 2)
    "analyze_stability",
    "check_stability",
    "is_stable",
]
