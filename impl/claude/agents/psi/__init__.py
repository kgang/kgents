"""
Psi-gent: The Universal Translator of Semantic Topologies.

Ψ-gent (Psychopomp) guides problems from Novel (unknown) to Archetype (known)
through metaphor projection and reification.

Core Components:
- MorphicFunctor: Φ (project) → Σ (solve) → Φ⁻¹ (reify)
- 4-Axis Tensor: Z (MHC), X (Shadow), Y (RSI), T (Value)
- HolographicMetaphorLibrary: M-gent fuzzy recall
- MetaphorHistorian: N-gent tracing
- MetaphorUmwelt: Agent-specific projection
- MetaphorEvolutionAgent: E-gent dialectical learning
- PsychopompAgent: Main orchestrator

Example:
    from impl.claude.agents.psi import PsychopompAgent, Novel

    problem = Novel(
        problem_id="test",
        description="Optimize team communication",
        domain="organization",
    )

    agent = PsychopompAgent()
    result = agent.solve(problem)

    if result.success:
        print(f"Solved via {result.metaphor_used.name}")
"""

# Core types
from .types import (
    # Enums
    MHCLevel,
    AxisType,
    StabilityStatus,
    AntiPattern,
    # Novel (input)
    Novel,
    # Metaphor types
    Metaphor,
    MetaphorOperation,
    # Projection types
    Projection,
    ConceptMapping,
    Distortion,
    # Solution types
    MetaphorSolution,
    ReifiedSolution,
    # Validation types
    TensorPosition,
    ValidationResult,
    TensorValidation,
    AntiPatternDetection,
)

# Metaphor library
from .metaphor_library import (
    MetaphorLibrary,
    StaticMetaphorLibrary,
    WeightedMetaphor,
    create_standard_library,
)

# Core functor
from .morphic_functor import MorphicFunctor

# 4-axis validators
from .resolution_scaler import (
    ResolutionScaler,
    ComplexityMetrics,
)
from .dialectical_rotator import (
    DialecticalRotator,
    ShadowGenerator,
    Shadow,
    ShadowType,
    ShadowTestResult,
)
from .topological_validator import (
    TopologicalValidator,
    KnotAnalyzer,
    KnotAnalysis,
    Register,
    RegisterState,
)
from .axiological_exchange import (
    AxiologicalExchange,
    ExchangeMatrix,
    ExchangeRate,
    ValueDimension,
    DimensionValue,
    MetaphorValueTensor,
    LossReport,
)

# M-gent integration (holographic memory)
from .holographic_library import (
    HolographicMetaphorLibrary,
    HolographicPattern,
    MetaphorEntry,
)

# N-gent integration (tracing)
from .metaphor_historian import (
    MetaphorHistorian,
    MetaphorTrace,
    MetaphorAction,
    MetaphorCrystalStore,
    TracingContext,
    ForensicBard,
    MetaphorDiagnosis,
)

# Umwelt integration
from .metaphor_umwelt import (
    MetaphorUmwelt,
    MetaphorLens,
    MetaphorDNA,
    MetaphorConstraint,
    # Factory functions
    create_k_gent_umwelt,
    create_b_gent_umwelt,
    create_e_gent_umwelt,
    create_neutral_umwelt,
    # Standard constraints
    NO_MILITARY,
    NO_RELIGIOUS,
    NO_VIOLENT,
    SCIENTIFIC_ONLY,
    NARRATIVE_ONLY,
    # Standard DNA profiles
    K_GENT_DNA,
    B_GENT_DNA,
    E_GENT_DNA,
)

# E-gent integration (evolution)
from .metaphor_evolution import (
    MetaphorEvolutionAgent,
    MetaphorEvolutionResult,
    MetaphorHypothesis,
    ExperimentResult,
    Verdict,
    HeldTension,
    MetaphorShadowAnalyzer,
    CollectiveShadow,
    EvolutionMemory,
)

# Main orchestrator
from .psychopomp_agent import (
    PsychopompAgent,
    PsychopompConfig,
    PsychopompResult,
    SearchPhase,
    SearchState,
    create_psychopomp,
    solve_problem,
)

__all__ = [
    # Types
    "MHCLevel",
    "AxisType",
    "StabilityStatus",
    "AntiPattern",
    "Novel",
    "Metaphor",
    "MetaphorOperation",
    "Projection",
    "ConceptMapping",
    "Distortion",
    "MetaphorSolution",
    "ReifiedSolution",
    "TensorPosition",
    "ValidationResult",
    "TensorValidation",
    "AntiPatternDetection",
    # Library
    "MetaphorLibrary",
    "StaticMetaphorLibrary",
    "WeightedMetaphor",
    "create_standard_library",
    # Functor
    "MorphicFunctor",
    # Z-axis
    "ResolutionScaler",
    "ComplexityMetrics",
    # X-axis
    "DialecticalRotator",
    "ShadowGenerator",
    "Shadow",
    "ShadowType",
    "ShadowTestResult",
    # Y-axis
    "TopologicalValidator",
    "KnotAnalyzer",
    "KnotAnalysis",
    "Register",
    "RegisterState",
    # T-axis
    "AxiologicalExchange",
    "ExchangeMatrix",
    "ExchangeRate",
    "ValueDimension",
    "DimensionValue",
    "MetaphorValueTensor",
    "LossReport",
    # M-gent
    "HolographicMetaphorLibrary",
    "HolographicPattern",
    "MetaphorEntry",
    # N-gent
    "MetaphorHistorian",
    "MetaphorTrace",
    "MetaphorAction",
    "MetaphorCrystalStore",
    "TracingContext",
    "ForensicBard",
    "MetaphorDiagnosis",
    # Umwelt
    "MetaphorUmwelt",
    "MetaphorLens",
    "MetaphorDNA",
    "MetaphorConstraint",
    "create_k_gent_umwelt",
    "create_b_gent_umwelt",
    "create_e_gent_umwelt",
    "create_neutral_umwelt",
    "NO_MILITARY",
    "NO_RELIGIOUS",
    "NO_VIOLENT",
    "SCIENTIFIC_ONLY",
    "NARRATIVE_ONLY",
    "K_GENT_DNA",
    "B_GENT_DNA",
    "E_GENT_DNA",
    # E-gent
    "MetaphorEvolutionAgent",
    "MetaphorEvolutionResult",
    "MetaphorHypothesis",
    "ExperimentResult",
    "Verdict",
    "HeldTension",
    "MetaphorShadowAnalyzer",
    "CollectiveShadow",
    "EvolutionMemory",
    # Psychopomp
    "PsychopompAgent",
    "PsychopompConfig",
    "PsychopompResult",
    "SearchPhase",
    "SearchState",
    "create_psychopomp",
    "solve_problem",
]
