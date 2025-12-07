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
from .hegel import (
    HegelAgent,
    ContinuousDialectic,
    DialecticInput,
    DialecticOutput,
    hegel,
    continuous_dialectic,
)

# Jung: Shadow integration
from .jung import (
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
)

# Lacan: Register triangulation
from .lacan import (
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

__all__ = [
    # Hegel
    "HegelAgent",
    "ContinuousDialectic",
    "DialecticInput",
    "DialecticOutput",
    "hegel",
    "continuous_dialectic",
    # Jung
    "JungAgent",
    "QuickShadow",
    "JungInput",
    "JungOutput",
    "ShadowContent",
    "Projection",
    "IntegrationPath",
    "IntegrationDifficulty",
    "jung",
    "quick_shadow",
    # Lacan
    "LacanAgent",
    "QuickRegister",
    "LacanInput",
    "LacanOutput",
    "RegisterLocation",
    "Slippage",
    "Register",
    "KnotStatus",
    "lacan",
    "quick_register",
]
