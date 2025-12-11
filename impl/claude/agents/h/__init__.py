"""
H-gents: Dialectic Introspection Agents

System-facing agents for self-examination, synthesis, and shadow integration.

CRITICAL CONSTRAINT: H-gents are system-introspective, never human-therapeutic.
They examine the agent system itself, not users.

The three traditions:
- Hegelian (H-hegel): thesis + antithesis → synthesis
- Jungian (H-jung): Shadow integration
- Lacanian (H-lacan): Real / Symbolic / Imaginary triangulation
"""

# Hegel: Dialectic synthesis
# Composition: H-gent pipelines
from .composition import (
    FullIntrospection,
    HegelLacanPipeline,
    IntrospectionInput,
    IntrospectionOutput,
    JungHegelPipeline,
    LacanJungPipeline,
    full_introspection,
    hegel_to_lacan,
    jung_to_hegel,
    lacan_to_jung,
)
from .hegel import (
    BackgroundDialectic,
    ContinuousDialectic,
    DialecticInput,
    DialecticOutput,
    DialecticStep,
    HegelAgent,
    background_dialectic,
    continuous_dialectic,
    hegel,
)

# Jung: Shadow integration
from .jung import (
    Archetype,
    ArchetypeManifest,
    CollectiveShadow,
    CollectiveShadowAgent,
    CollectiveShadowInput,
    IntegrationDifficulty,
    IntegrationPath,
    JungAgent,
    JungInput,
    JungOutput,
    Projection,
    QuickShadow,
    ShadowContent,
    collective_shadow,
    jung,
    quick_shadow,
)

# Lacan: Register triangulation
from .lacan import (
    KnotStatus,
    LacanAgent,
    LacanError,
    LacanInput,
    LacanOutput,
    LacanResult,
    QuickRegister,
    Register,
    RegisterLocation,
    Slippage,
    lacan,
    quick_register,
)

# Persistent Dialectic (DGent-backed)
from .persistent_dialectic import (
    DialecticHistory,
    DialecticMemoryAgent,
    DialecticRecord,
    PersistentDialecticAgent,
    dialectic_memory_agent,
    persistent_dialectic_agent,
)

__all__ = [
    # Hegel
    "HegelAgent",
    "ContinuousDialectic",
    "BackgroundDialectic",
    "DialecticInput",
    "DialecticOutput",
    "DialecticStep",
    "hegel",
    "continuous_dialectic",
    "background_dialectic",
    # Persistent Dialectic (DGent-backed)
    "PersistentDialecticAgent",
    "DialecticMemoryAgent",
    "DialecticHistory",
    "DialecticRecord",
    "persistent_dialectic_agent",
    "dialectic_memory_agent",
    # Jung
    "JungAgent",
    "QuickShadow",
    "CollectiveShadowAgent",
    "JungInput",
    "JungOutput",
    "ShadowContent",
    "Projection",
    "IntegrationPath",
    "IntegrationDifficulty",
    "Archetype",
    "ArchetypeManifest",
    "CollectiveShadow",
    "CollectiveShadowInput",
    "jung",
    "quick_shadow",
    "collective_shadow",
    # Lacan
    "LacanAgent",
    "QuickRegister",
    "LacanInput",
    "LacanOutput",
    "LacanError",
    "LacanResult",
    "RegisterLocation",
    "Slippage",
    "Register",
    "KnotStatus",
    "lacan",
    "quick_register",
    # Composition
    "HegelLacanPipeline",
    "LacanJungPipeline",
    "JungHegelPipeline",
    "FullIntrospection",
    "IntrospectionInput",
    "IntrospectionOutput",
    "hegel_to_lacan",
    "lacan_to_jung",
    "jung_to_hegel",
    "full_introspection",
]
