"""
A-gents Skeleton: The minimal structure every agent MUST implement.

This module formalizes what Agent[A, B] already IS:
- The skeleton is not a new class, but a recognition that Agent[A, B] in
  bootstrap.types IS the irreducible skeleton.

The key insight: Agent[A, B] provides:
    - name: str (identity)
    - invoke(input: A) -> B (behavior)
    - __rshift__ (composition)

That's it. That's the skeleton.

For agents that want to declare richer metadata (as per spec/a-gents/abstract/skeleton.md),
we provide AgentMeta as an OPTIONAL enhancement, not a requirement.

Philosophy: Composition, not duplication. We re-export Agent as AbstractAgent
for semantic clarity, but it's the same class.
"""

from dataclasses import dataclass, field
from typing import Any, TypeVar, Generic, Type

# Re-export the bootstrap Agent as AbstractAgent
# This is NOT a new class - it's the recognition that Agent IS the skeleton
from bootstrap.types import Agent

# Type alias for semantic clarity
AbstractAgent = Agent

# Type variables
A = TypeVar("A")
B = TypeVar("B")


@dataclass
class AgentIdentity:
    """
    Optional identity metadata for an agent.

    From spec/a-gents/abstract/skeleton.md:
    - name: Human-readable name
    - genus: Letter category (a, b, c, ...)
    - version: Semantic version
    - purpose: One-sentence "why this exists"
    """
    name: str
    genus: str
    version: str
    purpose: str


@dataclass
class AgentInterface:
    """
    Optional interface declaration.

    Describes what types the agent accepts and produces.
    In Python, this is already captured by Agent[A, B] generics,
    but this provides human-readable documentation.
    """
    input_type: Type[Any]
    input_description: str
    output_type: Type[Any]
    output_description: str
    error_codes: list[tuple[str, str]] = field(default_factory=list)  # (code, description)


@dataclass
class AgentBehavior:
    """
    Optional behavior specification.

    From spec/a-gents/abstract/skeleton.md:
    - description: What this agent does
    - guarantees: What the agent promises
    - constraints: What the agent will not do
    - side_effects: Effects beyond output
    """
    description: str
    guarantees: list[str] = field(default_factory=list)
    constraints: list[str] = field(default_factory=list)
    side_effects: list[str] = field(default_factory=list)


@dataclass
class AgentMeta:
    """
    Optional metadata for agents that want full spec compliance.

    This is NOT required to be a valid agent. Agent[A, B] is already
    the skeleton. AgentMeta provides additional documentation and
    introspection capabilities.

    Usage:
        class MyAgent(Agent[str, int]):
            meta = AgentMeta(
                identity=AgentIdentity(
                    name="Counter",
                    genus="a",
                    version="0.1.0",
                    purpose="Counts characters in input"
                ),
                interface=AgentInterface(
                    input_type=str,
                    input_description="Text to count",
                    output_type=int,
                    output_description="Character count"
                ),
                behavior=AgentBehavior(
                    description="Returns the length of input string",
                    guarantees=["Output >= 0", "Pure function"],
                    constraints=["Does not access network"],
                )
            )
    """
    identity: AgentIdentity
    interface: AgentInterface | None = None
    behavior: AgentBehavior | None = None

    @classmethod
    def minimal(cls, name: str, genus: str, purpose: str) -> "AgentMeta":
        """Create minimal metadata with just identity."""
        return cls(
            identity=AgentIdentity(
                name=name,
                genus=genus,
                version="0.1.0",
                purpose=purpose
            )
        )


def has_meta(agent: Agent) -> bool:
    """Check if an agent has AgentMeta defined."""
    return hasattr(agent, 'meta') and isinstance(agent.meta, AgentMeta)


def get_meta(agent: Agent) -> AgentMeta | None:
    """Get AgentMeta from an agent if present."""
    if has_meta(agent):
        return agent.meta  # type: ignore
    return None


# Note on the Identity Agent:
# The Identity agent (Id) from bootstrap is already spec-compliant.
# It satisfies the skeleton by providing:
#   - name: "Identity"
#   - invoke: returns input unchanged
#   - composition: works correctly with any other agent
#
# See: impl/claude-openrouter/bootstrap/id.py
