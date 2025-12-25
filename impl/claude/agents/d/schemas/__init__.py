"""
D-gent schemas - Versioned data contracts for the Crystal system.

Schemas define the shape of data independent of database models.
Each schema is a frozen dataclass with a version number.

Available schema domains:
- brain: Brain Crown Jewel schemas (crystals, settings)
- trail: Trail navigation and exploration schemas
- witness: Witness Crown Jewel schemas (marks, trust, thoughts, actions, escalations)
- code: Code artifact schemas (functions, tests, K-blocks, ghosts)
- proof: Galois witnessed proof schemas
- llm_trace: LLM invocation tracing (more granular than Datadog)
- axiom: Axiom and value crystals (Zero Seed L0-L1)
- prompt: Prompt templates and invocation crystals
- spec: Specification document crystals
- reflection: Reflection and interpretation crystals
- chat: Chat session, turn, and checkpoint crystals

The Crystal Taxonomy:
    L0 (Axioms): AxiomCrystal, ValueCrystal - foundational beliefs
    L1 (Prompts): PromptCrystal, InvocationCrystal - LLM interactions
    L2 (Specs): SpecCrystal - specification documents
    L3 (Code): FunctionCrystal, TestCrystal, KBlockCrystal - implementation
    L4 (Ghosts): GhostFunctionCrystal - implied/missing artifacts
    L5 (Proofs): GaloisWitnessedProof - self-justification
    L6 (Reflection): ReflectionCrystal, InterpretationCrystal - meta-analysis
    L7 (Witness): WitnessMark, LLMInvocationMark - execution traces
"""

from .brain import (
    BrainCrystal,
    BrainSetting,
    BRAIN_CRYSTAL_SCHEMA,
    BRAIN_SETTING_SCHEMA,
)
from .trail import (
    Trail,
    TRAIL_SCHEMA,
    TrailStep,
    TRAIL_STEP_SCHEMA,
    TrailCommitment,
    TRAIL_COMMITMENT_SCHEMA,
    TrailAnnotation,
    TRAIL_ANNOTATION_SCHEMA,
)
from .witness import (
    WitnessMark,
    WITNESS_MARK_SCHEMA,
    WitnessTrust,
    WITNESS_TRUST_SCHEMA,
    WitnessThought,
    WITNESS_THOUGHT_SCHEMA,
    WitnessAction,
    WITNESS_ACTION_SCHEMA,
    WitnessEscalation,
    WITNESS_ESCALATION_SCHEMA,
)
from .code import (
    ParamInfo,
    FunctionCrystal,
    FUNCTION_CRYSTAL_SCHEMA,
    TestCrystal,
    TEST_CRYSTAL_SCHEMA,
)
from .kblock import (
    KBLOCK_SIZE_HEURISTICS,
    KBlockCrystal,
    KBLOCK_CRYSTAL_SCHEMA,
)
from .ghost import (
    GhostFunctionCrystal,
    GHOST_FUNCTION_SCHEMA,
)
from .proof import (
    GaloisWitnessedProof,
    PROOF_SCHEMA,
)
try:
    from .llm_trace import (
        StateChange,
        LLMInvocationMark,
        LLM_INVOCATION_SCHEMA,
    )
    _LLM_TRACE_AVAILABLE = True
except ImportError:
    _LLM_TRACE_AVAILABLE = False

try:
    from .invocation import (
        StateChange,
        LLMInvocationMark,
        STATE_CHANGE_SCHEMA,
        LLM_INVOCATION_MARK_SCHEMA,
    )
    _INVOCATION_AVAILABLE = True
except ImportError:
    _INVOCATION_AVAILABLE = False
from .chat import (
    ChatSessionCrystal,
    ChatTurnCrystal,
    ChatCrystalCrystal,
    ChatCheckpointCrystal,
    CHAT_SESSION_SCHEMA,
    CHAT_TURN_SCHEMA,
    CHAT_CRYSTAL_SCHEMA,
    CHAT_CHECKPOINT_SCHEMA,
)

# New schema imports (conditional - will be available when files are created)
try:
    from .axiom import (
        AxiomCrystal,
        AXIOM_SCHEMA,
        ValueCrystal,
        VALUE_SCHEMA,
    )
    _AXIOM_AVAILABLE = True
except ImportError:
    _AXIOM_AVAILABLE = False

try:
    from .prompt import (
        PromptCrystal,
        PROMPT_CRYSTAL_SCHEMA,
        PromptParam,
        InvocationCrystal,
        INVOCATION_CRYSTAL_SCHEMA,
    )
    _PROMPT_AVAILABLE = True
except ImportError:
    _PROMPT_AVAILABLE = False

try:
    from .spec import (
        SpecCrystal,
        SPEC_CRYSTAL_SCHEMA,
    )
    _SPEC_AVAILABLE = True
except ImportError:
    _SPEC_AVAILABLE = False

try:
    from .reflection import (
        ReflectionCrystal,
        REFLECTION_CRYSTAL_SCHEMA,
        InterpretationCrystal,
        INTERPRETATION_CRYSTAL_SCHEMA,
    )
    _REFLECTION_AVAILABLE = True
except ImportError:
    _REFLECTION_AVAILABLE = False

__all__ = [
    # Brain schemas
    "BrainCrystal",
    "BrainSetting",
    "BRAIN_CRYSTAL_SCHEMA",
    "BRAIN_SETTING_SCHEMA",
    # Trail schemas
    "Trail",
    "TRAIL_SCHEMA",
    "TrailStep",
    "TRAIL_STEP_SCHEMA",
    "TrailCommitment",
    "TRAIL_COMMITMENT_SCHEMA",
    "TrailAnnotation",
    "TRAIL_ANNOTATION_SCHEMA",
    # Witness schemas
    "WitnessMark",
    "WITNESS_MARK_SCHEMA",
    "WitnessTrust",
    "WITNESS_TRUST_SCHEMA",
    "WitnessThought",
    "WITNESS_THOUGHT_SCHEMA",
    "WitnessAction",
    "WITNESS_ACTION_SCHEMA",
    "WitnessEscalation",
    "WITNESS_ESCALATION_SCHEMA",
    # Code schemas
    "ParamInfo",
    "FunctionCrystal",
    "FUNCTION_CRYSTAL_SCHEMA",
    "TestCrystal",
    "TEST_CRYSTAL_SCHEMA",
    "KBLOCK_SIZE_HEURISTICS",
    "KBlockCrystal",
    "KBLOCK_CRYSTAL_SCHEMA",
    "GhostFunctionCrystal",
    "GHOST_FUNCTION_SCHEMA",
    # Proof schemas
    "GaloisWitnessedProof",
    "PROOF_SCHEMA",
    # Chat schemas
    "ChatSessionCrystal",
    "ChatTurnCrystal",
    "ChatCrystalCrystal",
    "ChatCheckpointCrystal",
    "CHAT_SESSION_SCHEMA",
    "CHAT_TURN_SCHEMA",
    "CHAT_CRYSTAL_SCHEMA",
    "CHAT_CHECKPOINT_SCHEMA",
]

# Conditionally add new schemas to __all__
if _AXIOM_AVAILABLE:
    __all__.extend([
        "AxiomCrystal",
        "AXIOM_SCHEMA",
        "ValueCrystal",
        "VALUE_SCHEMA",
    ])

if _PROMPT_AVAILABLE:
    __all__.extend([
        "PromptCrystal",
        "PROMPT_CRYSTAL_SCHEMA",
        "PromptParam",
        "InvocationCrystal",
        "INVOCATION_CRYSTAL_SCHEMA",
    ])

if _SPEC_AVAILABLE:
    __all__.extend([
        "SpecCrystal",
        "SPEC_CRYSTAL_SCHEMA",
    ])

if _REFLECTION_AVAILABLE:
    __all__.extend([
        "ReflectionCrystal",
        "REFLECTION_CRYSTAL_SCHEMA",
        "InterpretationCrystal",
        "INTERPRETATION_CRYSTAL_SCHEMA",
    ])

if _LLM_TRACE_AVAILABLE:
    __all__.extend([
        "StateChange",
        "LLMInvocationMark",
        "LLM_INVOCATION_SCHEMA",
    ])

if _INVOCATION_AVAILABLE:
    __all__.extend([
        "StateChange",
        "LLMInvocationMark",
        "STATE_CHANGE_SCHEMA",
        "LLM_INVOCATION_MARK_SCHEMA",
    ])
