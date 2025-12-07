"""
H-gents: Dialectic Introspection Agents

System-facing agents for self-examination, synthesis, and shadow integration.

H-gents examine the agent system itself. They are NOT therapists for humans—
they are mechanisms by which an agent system can:
- Surface contradictions in its own outputs
- Synthesize opposing perspectives into higher-order understanding
- Integrate what it represses or ignores
- Navigate the gap between representation and reality

Critical constraint: H-gents are SYSTEM-INTROSPECTIVE, never human-therapeutic.

The Three Traditions:
- H-hegel: Dialectics (thesis + antithesis → synthesis)
- H-lacan: Representation (Real / Symbolic / Imaginary)
- H-jung: Shadow (integration of repressed/ignored content)
"""

# H-hegel: Dialectic Synthesis
from .hegel import (
    Hegel,
    hegel_agent,
    dialectic,
    hold_or_synthesize,
)

# H-lacan: Representational Triangulation
from .lacan import (
    Lacan,
    lacan_agent,
    analyze_registers,
    check_knot_status,
)

# H-jung: Shadow Integration
from .jung import (
    Jung,
    jung_agent,
    analyze_shadow,
    quick_shadow_check,
)

# Types
from ..types import (
    # Hegel types
    HegelInput,
    HegelOutput,

    # Lacan types
    LacanInput,
    LacanOutput,
    Register,
    RegisterLocation,
    Slippage,
    KnotStatus,

    # Jung types
    JungInput,
    JungOutput,
    ShadowContent,
    Projection,
    IntegrationPath,
    IntegrationDifficulty,
)

__all__ = [
    # H-hegel
    'Hegel',
    'hegel_agent',
    'dialectic',
    'hold_or_synthesize',
    'HegelInput',
    'HegelOutput',

    # H-lacan
    'Lacan',
    'lacan_agent',
    'analyze_registers',
    'check_knot_status',
    'LacanInput',
    'LacanOutput',
    'Register',
    'RegisterLocation',
    'Slippage',
    'KnotStatus',

    # H-jung
    'Jung',
    'jung_agent',
    'analyze_shadow',
    'quick_shadow_check',
    'JungInput',
    'JungOutput',
    'ShadowContent',
    'Projection',
    'IntegrationPath',
    'IntegrationDifficulty',
]

# H-gents genus marker
GENUS = 'h'
