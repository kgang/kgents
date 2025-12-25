"""
Categorical Reasoning Crown Jewel: Probing LLM Categorical Laws.

The Categorical service provides:
- MonadProbe: Test monad law satisfaction in LLM reasoning
- SheafDetector: Detect coherence violations (hallucinations)
- MiddleInvarianceProbe: Test middle-invariance hypothesis (Phase 1)
- MonadVariatorProbe: Test semantic-preserving transformations (Phase 1)
- CorrelationRunner: Run statistical studies on law-accuracy correlation
- DP Bridge: Formal isomorphism between Dynamic Programming and Agent composition

Philosophy:
    "LLM reasoning failures are not random. They follow patterns
    that category theory predicts."

    - Monad law violations → Chain-of-thought breakdowns
    - Sheaf incoherence → Hallucinations
    - Middle-invariance violations → Prompt brittleness
    - Variator failures → Non-monadic behavior

The Bet:
    If categorical laws correlate with reasoning correctness (r > 0.3),
    we have a new paradigm for LLM verification.

The DP-Agent Isomorphism:
    Dynamic Programming and Agent Composition are isomorphic:
    - DP states ↔ Agent positions
    - Bellman equations ↔ Composition laws
    - Value functions ↔ Principle satisfaction
    - Policy traces ↔ Witness marks

See: docs/theory/03-monadic-reasoning.md
See: docs/theory/05-sheaf-coherence.md
See: plans/categorical-reinvention-phase1-foundations.md
"""

from .constitution import (
    PRINCIPLE_WEIGHTS,
    Constitution,
    ConstitutionalEvaluation,
    Principle,
    PrincipleScore,
    ProbeRewards,
    compute_galois_loss,
)
from .dp_bridge import (
    # Core types
    TraceEntry,
    # Writer monad
    PolicyTrace,
    # Value function
    PrincipleScore as DPPrincipleScore,
    ValueScore,
    ValueFunction,
    ValueFunctionProtocol,
    # Bellman morphism (functor)
    DPState,
    DPAction,
    BellmanMorphism,
    # Optimal substructure (sheaf)
    SubproblemSolution,
    OptimalSubstructure,
    # Meta DP
    ProblemFormulation,
    MetaDP,
    # Solver
    DPSolver,
)
from .middle_invariance import MiddleInvarianceProbe, MiddleInvarianceResult
from .monad_variators import MonadVariatorProbe, MonadVariatorResult
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
    # Phase 1 enhancements
    StepExtractor,
    SymbolicContradictionChecker,
    Violation,
)
from .study import (
    BaselineResults,
    CorrelationResult,
    CorrelationStudy,
    Problem,
    ProblemResult,
    ProblemSet,
    StudyConfig,
    StudyResult,
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
    # Phase 1 new probes
    "MiddleInvarianceProbe",
    "MiddleInvarianceResult",
    "MonadVariatorProbe",
    "MonadVariatorResult",
    # Unified runner
    "CategoricalProbeRunner",
    "ProbeResults",
    # Phase 1 enhancements
    "StepExtractor",
    "SymbolicContradictionChecker",
    # Study
    "CorrelationStudy",
    "CorrelationResult",
    "BaselineResults",
    "Problem",
    "ProblemSet",
    "ProblemResult",
    "StudyConfig",
    "StudyResult",
    # Constitution - The Reward Function
    "Principle",
    "PRINCIPLE_WEIGHTS",
    "PrincipleScore",
    "ConstitutionalEvaluation",
    "Constitution",
    "ProbeRewards",
    "compute_galois_loss",
    # DP Bridge - Core types
    "TraceEntry",
    # DP Bridge - Writer monad
    "PolicyTrace",
    # DP Bridge - Value function
    "DPPrincipleScore",
    "ValueScore",
    "ValueFunction",
    "ValueFunctionProtocol",
    # DP Bridge - Bellman morphism (functor)
    "DPState",
    "DPAction",
    "BellmanMorphism",
    # DP Bridge - Optimal substructure (sheaf)
    "SubproblemSolution",
    "OptimalSubstructure",
    # DP Bridge - Meta DP
    "ProblemFormulation",
    "MetaDP",
    # DP Bridge - Solver
    "DPSolver",
]
