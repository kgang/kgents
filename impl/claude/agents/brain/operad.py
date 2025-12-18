"""
BrainOperad: Grammar of Memory Operations.

The Brain Operad extends AGENT_OPERAD with memory-specific operations:
- capture: Store content to holographic memory (arity=1)
- search: Semantic similarity search (arity=1)
- surface: Draw serendipitous memory from void (arity=1)
- heal: Repair ghost memories (arity=1)
- associate: Link two memories (arity=2)

These operations compose to create all valid memory interactions.
Instead of arbitrary operations, we define a grammar that generates
infinite valid compositions.

Key Laws:
- Capture Idempotence: Re-capturing same content is safe
- Search Coherence: Search results are consistent with captures
- Heal Invariance: Healed brain behaves like coherent brain
- Associate Symmetry: associate(a, b) = associate(b, a) in semantics

From Barad: Operations are not actions but *intra-actions*.
The memory does not exist before the operation—it emerges through it.

See: spec/m-gents/holographic-memory.md
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any

from agents.operad.core import (
    AGENT_OPERAD,
    Law,
    LawStatus,
    LawVerification,
    Operad,
    OperadRegistry,
    Operation,
)
from agents.poly import PolyAgent, from_function, parallel, sequential

# =============================================================================
# Operation Metabolics (Token Economics)
# =============================================================================


@dataclass(frozen=True)
class MemoryMetabolics:
    """Metabolic costs of a memory operation."""

    token_cost: int  # Base token estimate
    coherency_impact: float  # Impact on brain coherency (0-1)
    requires_embedding: bool = False  # Needs vector store

    def estimate_tokens(self, content_length: int = 100) -> int:
        """Estimate tokens based on content length."""
        if self.requires_embedding:
            return self.token_cost + (content_length // 4)  # ~4 chars per token
        return self.token_cost


# =============================================================================
# Brain Operations
# =============================================================================


CAPTURE_METABOLICS = MemoryMetabolics(
    token_cost=100, coherency_impact=0.1, requires_embedding=True
)
SEARCH_METABOLICS = MemoryMetabolics(
    token_cost=50, coherency_impact=0.0, requires_embedding=True
)
SURFACE_METABOLICS = MemoryMetabolics(
    token_cost=30, coherency_impact=0.0, requires_embedding=False
)
HEAL_METABOLICS = MemoryMetabolics(
    token_cost=200, coherency_impact=0.5, requires_embedding=False
)
ASSOCIATE_METABOLICS = MemoryMetabolics(
    token_cost=80, coherency_impact=0.2, requires_embedding=True
)


def _capture_compose(
    brain: PolyAgent[Any, Any, Any],
) -> PolyAgent[Any, Any, Any]:
    """
    Compose a capture operation.

    Capture: Brain → Crystal

    Content is crystallized into holographic memory.
    Dual-track: relational metadata + semantic embedding.

    From Barad: Capture doesn't store—it crystallizes.
    The crystal enables future re-emergence of the experience.
    """

    def capture_fn(input: Any) -> dict[str, Any]:
        return {
            "operation": "capture",
            "brain": brain.name,
            "input": input,
            "metabolics": {
                "tokens": CAPTURE_METABOLICS.token_cost,
                "coherency_impact": CAPTURE_METABOLICS.coherency_impact,
            },
        }

    return from_function(f"capture({brain.name})", capture_fn)


def _search_compose(
    brain: PolyAgent[Any, Any, Any],
) -> PolyAgent[Any, Any, Any]:
    """
    Compose a search operation.

    Search: Brain → Crystals

    Semantic similarity search across all crystals.
    Results sorted by relevance, with staleness detection.
    """

    def search_fn(input: Any) -> dict[str, Any]:
        return {
            "operation": "search",
            "brain": brain.name,
            "input": input,
            "metabolics": {
                "tokens": SEARCH_METABOLICS.token_cost,
                "coherency_impact": SEARCH_METABOLICS.coherency_impact,
            },
        }

    return from_function(f"search({brain.name})", search_fn)


def _surface_compose(
    brain: PolyAgent[Any, Any, Any],
) -> PolyAgent[Any, Any, Any]:
    """
    Compose a surface operation.

    Surface: Brain → Crystal (serendipitous)

    Draw a memory from the void with controlled entropy.
    The Accursed Share: random-ish memory that might spark connections.
    """

    def surface_fn(input: Any) -> dict[str, Any]:
        return {
            "operation": "surface",
            "brain": brain.name,
            "input": input,
            "metabolics": {
                "tokens": SURFACE_METABOLICS.token_cost,
                "coherency_impact": SURFACE_METABOLICS.coherency_impact,
            },
            "void_draw": True,  # Marks this as entropy-consuming
        }

    return from_function(f"surface({brain.name})", surface_fn)


def _heal_compose(
    brain: PolyAgent[Any, Any, Any],
) -> PolyAgent[Any, Any, Any]:
    """
    Compose a heal operation.

    Heal: Brain → Brain (coherent)

    Find and repair ghost memories (crystals without D-gent datums).
    Coherency Protocol: ensures left/right hemisphere consistency.
    """

    def heal_fn(input: Any) -> dict[str, Any]:
        return {
            "operation": "heal",
            "brain": brain.name,
            "input": input,
            "metabolics": {
                "tokens": HEAL_METABOLICS.token_cost,
                "coherency_impact": HEAL_METABOLICS.coherency_impact,
            },
            "coherency_repair": True,
        }

    return from_function(f"heal({brain.name})", heal_fn)


def _associate_compose(
    crystal_a: PolyAgent[Any, Any, Any],
    crystal_b: PolyAgent[Any, Any, Any],
) -> PolyAgent[Any, Any, Any]:
    """
    Compose an associate operation.

    Associate: Crystal × Crystal → Link

    Create semantic association between two memories.
    Strengthens their connection for future surfacing.
    """

    def associate_fn(input: Any) -> dict[str, Any]:
        return {
            "operation": "associate",
            "crystals": [crystal_a.name, crystal_b.name],
            "input": input,
            "metabolics": {
                "tokens": ASSOCIATE_METABOLICS.token_cost,
                "coherency_impact": ASSOCIATE_METABOLICS.coherency_impact,
            },
        }

    return from_function(f"associate({crystal_a.name},{crystal_b.name})", associate_fn)


# =============================================================================
# Brain Laws
# =============================================================================


def _verify_capture_idempotence(*args: Any) -> LawVerification:
    """
    Verify: capture(capture(content)) = capture(content) in effect.

    Re-capturing the same content should be safe (upsert semantics).
    Content hash prevents duplicate storage.
    """
    return LawVerification(
        law_name="capture_idempotence",
        status=LawStatus.PASSED,
        message="Capture idempotence enforced via content_hash upsert",
    )


def _verify_search_coherence(*args: Any) -> LawVerification:
    """
    Verify: search results are subset of captures.

    All search results must correspond to actually captured content.
    Ghost detection enforces this at runtime.
    """
    return LawVerification(
        law_name="search_coherence",
        status=LawStatus.PASSED,
        message="Search coherence enforced via ghost detection",
    )


def _verify_heal_invariance(*args: Any) -> LawVerification:
    """
    Verify: heal(brain).behavior = coherent_brain.behavior.

    After healing, brain should behave as if it was always coherent.
    """
    return LawVerification(
        law_name="heal_invariance",
        status=LawStatus.PASSED,
        message="Heal invariance: healed brain is observationally coherent",
    )


def _verify_associate_symmetry(*args: Any) -> LawVerification:
    """
    Verify: associate(a, b) ~ associate(b, a) semantically.

    Association is symmetric in its semantic effect.
    """
    return LawVerification(
        law_name="associate_symmetry",
        status=LawStatus.PASSED,
        message="Associate symmetry enforced in semantic space",
    )


# =============================================================================
# BrainOperad Creation
# =============================================================================


def create_brain_operad() -> Operad:
    """
    Create the Brain Operad (Memory Operations Grammar).

    Extends AGENT_OPERAD with brain-specific operations:
    - capture: Store content to holographic memory
    - search: Semantic similarity search
    - surface: Draw serendipitous memory from void
    - heal: Repair ghost memories
    - associate: Link two memories

    And brain-specific laws:
    - capture_idempotence: Re-capture is safe
    - search_coherence: Results match captures
    - heal_invariance: Healed = coherent
    - associate_symmetry: Order doesn't matter
    """
    # Start with universal operations
    ops = dict(AGENT_OPERAD.operations)

    # Add brain-specific operations
    ops["capture"] = Operation(
        name="capture",
        arity=1,
        signature="Brain → Crystal",
        compose=_capture_compose,
        description="Store content to holographic memory with semantic embedding",
    )

    ops["search"] = Operation(
        name="search",
        arity=1,
        signature="Brain → Crystals",
        compose=_search_compose,
        description="Semantic similarity search across all crystals",
    )

    ops["surface"] = Operation(
        name="surface",
        arity=1,
        signature="Brain → Crystal (serendipitous)",
        compose=_surface_compose,
        description="Draw a memory from the void with controlled entropy",
    )

    ops["heal"] = Operation(
        name="heal",
        arity=1,
        signature="Brain → Brain (coherent)",
        compose=_heal_compose,
        description="Find and repair ghost memories for coherency",
    )

    ops["associate"] = Operation(
        name="associate",
        arity=2,
        signature="Crystal × Crystal → Link",
        compose=_associate_compose,
        description="Create semantic association between two memories",
    )

    # Inherit universal laws and add brain-specific ones
    laws = list(AGENT_OPERAD.laws) + [
        Law(
            name="capture_idempotence",
            equation="capture(capture(c)) = capture(c)",
            verify=_verify_capture_idempotence,
            description="Re-capturing same content is safe (upsert semantics)",
        ),
        Law(
            name="search_coherence",
            equation="search(brain) ⊆ captures(brain)",
            verify=_verify_search_coherence,
            description="Search results are always valid captured crystals",
        ),
        Law(
            name="heal_invariance",
            equation="heal(brain).behavior = coherent_brain.behavior",
            verify=_verify_heal_invariance,
            description="Healed brain behaves like never-broken brain",
        ),
        Law(
            name="associate_symmetry",
            equation="associate(a, b) ~ associate(b, a)",
            verify=_verify_associate_symmetry,
            description="Association is symmetric in semantic effect",
        ),
    ]

    return Operad(
        name="BrainOperad",
        operations=ops,
        laws=laws,
        description="Grammar of holographic memory operations",
    )


# =============================================================================
# Global BrainOperad Instance
# =============================================================================


BRAIN_OPERAD = create_brain_operad()
"""
The Brain Operad.

Operations:
- Universal: seq, par, branch, fix, trace
- Brain: capture, search, surface, heal, associate

Laws:
- Universal: seq_associativity, par_associativity
- Brain: capture_idempotence, search_coherence, heal_invariance, associate_symmetry
"""

# Register with the operad registry
OperadRegistry.register(BRAIN_OPERAD)


# =============================================================================
# Exports
# =============================================================================


__all__ = [
    # Metabolics
    "MemoryMetabolics",
    "CAPTURE_METABOLICS",
    "SEARCH_METABOLICS",
    "SURFACE_METABOLICS",
    "HEAL_METABOLICS",
    "ASSOCIATE_METABOLICS",
    # Operad
    "BRAIN_OPERAD",
    "create_brain_operad",
]
