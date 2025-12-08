"""
Bridge to kgents implementation.

This module provides a clean import interface for zen-agents to access
the kgents agent ecosystem (kgents-runtime package).

The kgents-runtime package is linked via uv workspace from impl/claude-openrouter/.

Usage within zen-agents:
    from .kgents_bridge import ClaudeCLIRuntime, creativity_coach, robin
    from .kgents_bridge import compose, Judge, Fix
"""

# No path manipulation needed - kgents-runtime is a proper workspace dependency

# -----------------------------------------------------------------------------
# Runtime - LLM execution layer
# -----------------------------------------------------------------------------
from runtime import (
    ClaudeCLIRuntime,
    ClaudeRuntime,
    OpenRouterRuntime,
    LLMAgent,
    AgentContext,
    AgentResult,
    ParseError,
)

# -----------------------------------------------------------------------------
# Bootstrap - The 7 irreducible agents
# -----------------------------------------------------------------------------
from bootstrap import (
    # Types
    Agent,
    Verdict,
    VerdictType,
    Tension,
    TensionMode,
    Synthesis,
    ResolutionType,
    HoldTension,
    Facts,
    PersonaSeed,
    WorldSeed,
    Principle,
    Principles,
    # The 7 Bootstrap Agents
    Id,
    compose,
    ComposedAgent,
    Judge,
    JudgeInput,
    Ground,
    Contradict,
    ContradictInput,
    Sublate,
    Fix,
    fix,
    # Utilities
    FixConfig,
    FixResult,
    make_default_principles,
    # Specialized
    JudgeTaste,
    JudgeCurate,
    JudgeEthics,
    JudgeJoy,
    JudgeCompose,
    JudgeHetero,
    JudgeGenerate,
    NameCollisionChecker,
    ConfigConflictChecker,
    MergeConfigSublate,
    RetryFix,
    ConvergeFix,
)

# -----------------------------------------------------------------------------
# A-gents: Abstract Architectures + Art/Creativity
# -----------------------------------------------------------------------------
from agents.a import (
    # Core skeleton
    AbstractAgent,
    # Metadata (optional)
    AgentMeta,
    AgentIdentity,
    AgentInterface,
    AgentBehavior,
    has_meta,
    get_meta,
    # Creativity Coach
    CreativityMode,
    CreativityInput,
    CreativityResponse,
    Persona,
    CreativityCoach,
    creativity_coach,
    playful_coach,
    philosophical_coach,
    provocative_coach,
)

# -----------------------------------------------------------------------------
# B-gents: Scientific Discovery
# -----------------------------------------------------------------------------
from agents.b import (
    # HypothesisEngine
    HypothesisEngine,
    HypothesisInput,
    HypothesisOutput,
    Hypothesis,
    NoveltyLevel,
    hypothesis_engine,
    rigorous_engine,
    exploratory_engine,
    # Robin (scientific companion)
    RobinAgent,
    RobinInput,
    RobinOutput,
    robin,
    robin_with_persona,
    quick_robin,
)

# -----------------------------------------------------------------------------
# C-gents: Category Theory (Composability)
# -----------------------------------------------------------------------------
from agents.c import (
    # Maybe
    Maybe,
    Just,
    Nothing,
    MaybeAgent,
    maybe,
    # Either
    Either,
    Right,
    Left,
    EitherAgent,
    either,
    # Parallel
    ParallelAgent,
    FanOutAgent,
    CombineAgent,
    RaceAgent,
    parallel,
    fan_out,
    combine,
    race,
    # Conditional
    BranchAgent,
    SwitchAgent,
    GuardedAgent,
    FilterAgent,
    branch,
    switch,
    guarded,
    filter_by,
)

# -----------------------------------------------------------------------------
# H-gents: Dialectic Introspection
# -----------------------------------------------------------------------------
from agents.h import (
    # Hegel
    HegelAgent,
    ContinuousDialectic,
    DialecticInput,
    DialecticOutput,
    hegel,
    continuous_dialectic,
    # Jung
    JungAgent,
    QuickShadow,
    JungInput,
    JungOutput,
    ShadowContent,
    Projection,
    IntegrationPath,
    IntegrationDifficulty,
    jung,
    quick_shadow,
    # Lacan
    LacanAgent,
    QuickRegister,
    LacanInput,
    LacanOutput,
    RegisterLocation,
    Slippage,
    Register,
    KnotStatus,
    lacan,
    quick_register,
)

# -----------------------------------------------------------------------------
# K-gent: Kent Simulacra (Personalization)
# -----------------------------------------------------------------------------
from agents.k import (
    # Persona types
    PersonaSeed,  # Note: Also in bootstrap, same type
    PersonaState,
    PersonaQuery,
    PersonaResponse,
    DialogueMode,
    DialogueInput,
    DialogueOutput,
    # Agents
    KgentAgent,
    PersonaQueryAgent,
    EvolutionAgent,
    # Convenience functions
    kgent,
    query_persona,
    evolve_persona,
    # Evolution types
    EvolutionInput,
    EvolutionOutput,
    ConfidenceLevel,
    ChangeSource,
)

# -----------------------------------------------------------------------------
# Convenience: All exports
# -----------------------------------------------------------------------------
__all__ = [
    # Runtime
    "ClaudeCLIRuntime",
    "ClaudeRuntime",
    "OpenRouterRuntime",
    "LLMAgent",
    "AgentContext",
    "AgentResult",
    "ParseError",
    # Bootstrap types
    "Agent",
    "Verdict",
    "VerdictType",
    "Tension",
    "TensionMode",
    "Synthesis",
    "ResolutionType",
    "HoldTension",
    "Facts",
    "PersonaSeed",
    "WorldSeed",
    "Principle",
    "Principles",
    # Bootstrap agents
    "Id",
    "compose",
    "ComposedAgent",
    "Judge",
    "JudgeInput",
    "Ground",
    "Contradict",
    "ContradictInput",
    "Sublate",
    "Fix",
    "fix",
    "FixConfig",
    "FixResult",
    "make_default_principles",
    "RetryFix",
    "ConvergeFix",
    # A-gents
    "AbstractAgent",
    "CreativityMode",
    "CreativityInput",
    "CreativityResponse",
    "CreativityCoach",
    "creativity_coach",
    # B-gents
    "HypothesisEngine",
    "HypothesisInput",
    "HypothesisOutput",
    "Hypothesis",
    "hypothesis_engine",
    "rigorous_engine",
    "RobinAgent",
    "RobinInput",
    "RobinOutput",
    "robin",
    # C-gents
    "Maybe",
    "Either",
    "parallel",
    "branch",
    "switch",
    # H-gents
    "HegelAgent",
    "DialecticInput",
    "DialecticOutput",
    "hegel",
    "JungAgent",
    "jung",
    "LacanAgent",
    "lacan",
    # K-gent
    "DialogueMode",
    "DialogueInput",
    "DialogueOutput",
    "KgentAgent",
    "kgent",
    "PersonaQuery",
    "query_persona",
]
