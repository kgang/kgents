"""
C-gents: Category Theory Agents

The C-gents ARE the bootstrap agents. They provide the categorical foundation:
- Id: Identity morphism (composition unit)
- Compose: Agent-that-makes-agents
- Fix: Fixed-point operator
- pipeline: Multi-agent composition

These agents embody the three laws of composition:
1. Associativity: (f ∘ g) ∘ h ≡ f ∘ (g ∘ h)
2. Identity: Id ∘ f ≡ f, f ∘ Id ≡ f
3. Closure: composition of agents is an agent
"""

# C-gents are bootstrap agents - re-export them
from bootstrap import (
    # Agent classes
    Id,
    Compose,
    ComposedAgent,
    Fix,

    # Singleton instances
    id_agent,
    compose_agent,
    fix_agent,

    # Convenience functions
    compose,
    pipeline,
    fix,
    iterate_until_stable,

    # Types
    Agent,
    FixResult,
    FixConfig,
    FixInput,
)

__all__ = [
    # Classes
    'Id',
    'Compose',
    'ComposedAgent',
    'Fix',

    # Instances
    'id_agent',
    'compose_agent',
    'fix_agent',

    # Functions
    'compose',
    'pipeline',
    'fix',
    'iterate_until_stable',

    # Types
    'Agent',
    'FixResult',
    'FixConfig',
    'FixInput',
]

# C-gents genus marker
GENUS = 'c'
