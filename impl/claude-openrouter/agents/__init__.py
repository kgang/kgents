"""
kgents Agent Genera

Implementation of the 5 agent genera using bootstrap primitives.

Genera:
- A-gents: Abstract patterns + Art (creativity support)
- B-gents: Bio/Scientific discovery (hypothesis generation)
- C-gents: Category Theory (composition, already in bootstrap)
- H-gents: Dialectic introspection (Hegel, Lacan, Jung)
- K-gent: Kent simulacra (interactive persona)

Generation rules from spec/bootstrap.md:
    A-gents = Compose(Ground, abstract_patterns) | Compose(Ground, creativity_support)
    B-gents = Compose(Ground, scientific_method)
    C-gents = {Id, Compose, Fix}  // C-gents ARE bootstrap agents
    H-gents = {Contradict, Sublate, introspection_targets}
    K-gent = Ground() projected through persona_schema

Usage:
    from agents import creativity_coach, hypothesis_engine, kgent
    from agents import dialectic, analyze_registers, analyze_shadow
    from agents import compose, pipeline, id_agent
"""

# A-gents: Abstract + Art
from .a import (
    # Abstract (from bootstrap)
    Id,
    id_agent,

    # Art
    CreativityCoach,
    creativity_coach,
    expand,
    connect,
    constrain,
    question,
    CreativityInput,
    CreativityOutput,
    CreativityMode,
    CreativityPersona,
)

# B-gents: Bio/Scientific
from .b import (
    HypothesisEngine,
    hypothesis_engine,
    generate_hypotheses,
    quick_hypothesis,
    HypothesisInput,
    HypothesisOutput,
    Hypothesis,
    Novelty,
)

# C-gents: Category Theory (re-export from bootstrap)
from .c import (
    Id,
    Compose,
    ComposedAgent,
    Fix,
    id_agent,
    compose_agent,
    fix_agent,
    compose,
    pipeline,
    fix,
    iterate_until_stable,
    Agent,
    FixResult,
    FixConfig,
    FixInput,
)

# H-gents: Dialectic Introspection
from .h import (
    # H-hegel
    Hegel,
    hegel_agent,
    dialectic,
    hold_or_synthesize,
    HegelInput,
    HegelOutput,

    # H-lacan
    Lacan,
    lacan_agent,
    analyze_registers,
    check_knot_status,
    LacanInput,
    LacanOutput,
    Register,
    RegisterLocation,
    Slippage,
    KnotStatus,

    # H-jung
    Jung,
    jung_agent,
    analyze_shadow,
    quick_shadow_check,
    JungInput,
    JungOutput,
    ShadowContent,
    Projection,
    IntegrationPath,
    IntegrationDifficulty,
)

# K-gent: Kent Simulacra
from .k import (
    Kgent,
    kgent,
    query_persona,
    dialogue,
    KgentInput,
    KgentOutput,
    PersonaQuery,
    PersonaUpdate,
    Dialogue,
    DialogueMode,
    QueryAspect,
    UpdateOperation,
    QueryResponse,
    UpdateConfirmation,
    DialogueResponse,
)

# All genera
GENERA = {
    'a': 'A-gents (Abstract + Art)',
    'b': 'B-gents (Bio/Scientific)',
    'c': 'C-gents (Category Theory)',
    'h': 'H-gents (Dialectic Introspection)',
    'k': 'K-gent (Kent Simulacra)',
}

__all__ = [
    # Genera info
    'GENERA',

    # A-gents
    'Id', 'id_agent',
    'CreativityCoach', 'creativity_coach',
    'expand', 'connect', 'constrain', 'question',
    'CreativityInput', 'CreativityOutput', 'CreativityMode', 'CreativityPersona',

    # B-gents
    'HypothesisEngine', 'hypothesis_engine',
    'generate_hypotheses', 'quick_hypothesis',
    'HypothesisInput', 'HypothesisOutput', 'Hypothesis', 'Novelty',

    # C-gents
    'Compose', 'ComposedAgent', 'Fix',
    'compose_agent', 'fix_agent',
    'compose', 'pipeline', 'fix', 'iterate_until_stable',
    'Agent', 'FixResult', 'FixConfig', 'FixInput',

    # H-gents
    'Hegel', 'hegel_agent', 'dialectic', 'hold_or_synthesize',
    'HegelInput', 'HegelOutput',
    'Lacan', 'lacan_agent', 'analyze_registers', 'check_knot_status',
    'LacanInput', 'LacanOutput', 'Register', 'RegisterLocation', 'Slippage', 'KnotStatus',
    'Jung', 'jung_agent', 'analyze_shadow', 'quick_shadow_check',
    'JungInput', 'JungOutput', 'ShadowContent', 'Projection', 'IntegrationPath', 'IntegrationDifficulty',

    # K-gent
    'Kgent', 'kgent', 'query_persona', 'dialogue',
    'KgentInput', 'KgentOutput',
    'PersonaQuery', 'PersonaUpdate', 'Dialogue', 'DialogueMode',
    'QueryAspect', 'UpdateOperation',
    'QueryResponse', 'UpdateConfirmation', 'DialogueResponse',
]
