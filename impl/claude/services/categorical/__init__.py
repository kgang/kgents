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
    BellmanMorphism,
    DPAction,
    # Solver
    DPSolver,
    # Bellman morphism (functor)
    DPState,
    MetaDP,
    OptimalSubstructure,
    # Writer monad
    PolicyTrace,
    # Value function
    PrincipleScore as DPPrincipleScore,
    # Meta DP
    ProblemFormulation,
    # Optimal substructure (sheaf)
    SubproblemSolution,
    # Core types
    TraceEntry,
    ValueFunction,
    ValueFunctionProtocol,
    ValueScore,
)
from .middle_invariance import MiddleInvarianceProbe, MiddleInvarianceResult
from .monad_variators import MonadVariatorProbe, MonadVariatorResult

# Pilot Law Grammar (Amendment G)
from .pilot_laws import (
    PILOT_LAWS,
    LawSchema,
    LawVerificationReport,
    LawVerificationResult,
    PilotLaw,
    coherence_gate,
    compression_honesty,
    courage_preservation,
    drift_alert,
    get_all_pilots,
    get_law_by_name,
    get_laws_by_pilot,
    get_laws_by_schema,
    ghost_preservation,
    summarize_pilot_laws,
    verify_all_laws,
    verify_law,
    verify_pilot_laws,
    verify_schema_laws,
)
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
    # Pilot Law Grammar (Amendment G)
    "LawSchema",
    "PilotLaw",
    "LawVerificationResult",
    "LawVerificationReport",
    "coherence_gate",
    "drift_alert",
    "ghost_preservation",
    "courage_preservation",
    "compression_honesty",
    "PILOT_LAWS",
    "verify_law",
    "verify_all_laws",
    "verify_pilot_laws",
    "verify_schema_laws",
    "get_laws_by_pilot",
    "get_laws_by_schema",
    "get_all_pilots",
    "get_law_by_name",
    "summarize_pilot_laws",
]
