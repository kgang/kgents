"""
Categorical Reasoning Crown Jewel: Probing LLM Categorical Laws.

The Categorical service provides:
- MonadProbe: Test monad law satisfaction in LLM reasoning
- SheafDetector: Detect coherence violations (hallucinations)
- CorrelationRunner: Run statistical studies on law-accuracy correlation

Philosophy:
    "LLM reasoning failures are not random. They follow patterns
    that category theory predicts."

    - Monad law violations → Chain-of-thought breakdowns
    - Sheaf incoherence → Hallucinations

The Bet:
    If categorical laws correlate with reasoning correctness (r > 0.3),
    we have a new paradigm for LLM verification.

See: docs/theory/03-monadic-reasoning.md
See: docs/theory/05-sheaf-coherence.md
See: plans/categorical-reinvention-phase1-foundations.md
"""

from .probes import (
    AssociativityTestResult,
    # Unified probe runner
    CategoricalProbeRunner,
    Claim,
    ClaimPair,
    CoherenceResult,
    IdentityTestResult,
    # Monad probes
    MonadProbe,
    MonadResult,
    ProbeResults,
    # Sheaf probes
    SheafDetector,
    Violation,
)
from .study import (
    CorrelationResult,
    CorrelationStudy,
    Problem,
    ProblemSet,
    StudyConfig,
)

__all__ = [
    # Monad probes
    "MonadProbe",
    "MonadResult",
    "IdentityTestResult",
    "AssociativityTestResult",
    # Sheaf probes
    "SheafDetector",
    "CoherenceResult",
    "Claim",
    "ClaimPair",
    "Violation",
    # Unified runner
    "CategoricalProbeRunner",
    "ProbeResults",
    # Study
    "CorrelationStudy",
    "CorrelationResult",
    "Problem",
    "ProblemSet",
    "StudyConfig",
]
