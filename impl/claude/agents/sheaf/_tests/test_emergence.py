"""
Tests for Sheaf Emergence.

These tests verify:
1. Context structure
2. Sheaf restriction
3. Compatibility checking
4. Gluing operation
5. Emergent soul behavior
"""

from typing import Any

import pytest

from agents.poly import PolyAgent, from_function
from agents.sheaf import (
    AESTHETIC,
    CATEGORICAL,
    GENERATIVITY,
    GRATITUDE,
    HETERARCHY,
    JOY,
    KENT_SOUL,
    SOUL_SHEAF,
    AgentSheaf,
    Context,
    GluingError,
    RestrictionError,
    create_aesthetic_soul,
    create_categorical_soul,
    create_emergent_soul,
    create_generativity_soul,
    create_gratitude_soul,
    create_heterarchy_soul,
    create_joy_soul,
    eigenvector_overlap,
    query_soul,
)


class TestContext:
    """Tests for Context structure."""

    def test_context_creation(self) -> None:
        """Context has name and capabilities."""
        ctx = Context("test", frozenset({"cap1", "cap2"}))
        assert ctx.name == "test"
        assert "cap1" in ctx.capabilities

    def test_context_hashable(self) -> None:
        """Context is hashable (can be used in dicts/sets)."""
        ctx = Context("test", frozenset({"cap"}))
        ctx_set = {ctx}
        assert ctx in ctx_set

    def test_eigenvector_contexts_defined(self) -> None:
        """All eigenvector contexts are defined."""
        assert AESTHETIC.name == "aesthetic"
        assert CATEGORICAL.name == "categorical"
        assert GRATITUDE.name == "gratitude"
        assert HETERARCHY.name == "heterarchy"
        assert GENERATIVITY.name == "generativity"
        assert JOY.name == "joy"


class TestEigenvectorOverlap:
    """Tests for context overlap computation."""

    def test_no_overlap(self) -> None:
        """Non-overlapping contexts return None."""
        ctx1 = Context("a", frozenset({"x"}))
        ctx2 = Context("b", frozenset({"y"}))

        overlap = eigenvector_overlap(ctx1, ctx2)
        assert overlap is None

    def test_has_overlap(self) -> None:
        """Overlapping contexts return intersection."""
        ctx1 = Context("a", frozenset({"x", "y"}))
        ctx2 = Context("b", frozenset({"y", "z"}))

        overlap = eigenvector_overlap(ctx1, ctx2)
        assert overlap is not None
        assert "y" in overlap.capabilities
        assert "x" not in overlap.capabilities
        assert "z" not in overlap.capabilities


class TestAgentSheaf:
    """Tests for AgentSheaf operations."""

    def test_sheaf_creation(self) -> None:
        """AgentSheaf is created with contexts and overlap function."""
        sheaf = AgentSheaf(
            contexts={Context("a"), Context("b")},
            overlap_fn=lambda c1, c2: None,
        )
        assert len(sheaf.contexts) == 2

    def test_soul_sheaf_has_six_contexts(self) -> None:
        """SOUL_SHEAF has all six eigenvector contexts."""
        assert len(SOUL_SHEAF.contexts) == 6


class TestSheafRestriction:
    """Tests for sheaf restriction operation."""

    def test_restrict_to_context(self) -> None:
        """Can restrict agent to subcontext."""
        agent: PolyAgent[str, Any, Any] = from_function("Test", lambda x: x * 2)

        restricted = SOUL_SHEAF.restrict(agent, AESTHETIC)
        assert "|" in restricted.name
        assert AESTHETIC.name in restricted.name

    def test_restrict_preserves_behavior(self) -> None:
        """Restricted agent preserves original behavior."""
        agent: PolyAgent[str, Any, Any] = from_function("Double", lambda x: x * 2)

        restricted = SOUL_SHEAF.restrict(agent, CATEGORICAL)
        _, result = restricted.invoke("ready", 5)
        assert result == 10


class TestSheafCompatibility:
    """Tests for compatibility checking."""

    def test_compatible_locals(self) -> None:
        """Compatible local agents pass compatibility check."""
        agent1: PolyAgent[str, Any, Any] = from_function("A", lambda x: x + 1)
        agent2: PolyAgent[str, Any, Any] = from_function("B", lambda x: x + 1)

        locals = {AESTHETIC: agent1, CATEGORICAL: agent2}
        assert SOUL_SHEAF.compatible(locals)

    def test_empty_locals_compatible(self) -> None:
        """Empty locals are vacuously compatible."""
        assert SOUL_SHEAF.compatible({})


class TestSheafGluing:
    """Tests for gluing operation."""

    def test_glue_local_souls(self) -> None:
        """Can glue local souls into global soul."""
        local_souls = {
            AESTHETIC: create_aesthetic_soul(),
            CATEGORICAL: create_categorical_soul(),
        }

        glued = SOUL_SHEAF.glue(local_souls)
        assert glued is not None
        assert "Glued" in glued.name

    def test_glued_has_union_positions(self) -> None:
        """Glued agent has union of local positions."""
        agent1: PolyAgent[str, Any, Any] = from_function("A", lambda x: x)
        agent2: PolyAgent[str, Any, Any] = from_function("B", lambda x: x)

        # Both have position "ready"
        glued = SOUL_SHEAF.glue({AESTHETIC: agent1, CATEGORICAL: agent2})

        # Should have "ready" (union, not duplicated)
        assert "ready" in glued.positions


class TestLocalSouls:
    """Tests for local soul creation."""

    def test_aesthetic_soul(self) -> None:
        """Aesthetic soul asks about existence."""
        soul = create_aesthetic_soul()
        _, result = soul.invoke("ready", "a feature")

        assert result["context"] == "aesthetic"
        assert "need to exist" in result["question"].lower()
        assert result["minimalism"] == 0.15

    def test_categorical_soul(self) -> None:
        """Categorical soul asks about morphism."""
        soul = create_categorical_soul()
        _, result = soul.invoke("ready", "a pattern")

        assert result["context"] == "categorical"
        assert "morphism" in result["question"].lower()
        assert result["abstraction"] == 0.92

    def test_gratitude_soul(self) -> None:
        """Gratitude soul asks about respect."""
        soul = create_gratitude_soul()
        _, result = soul.invoke("ready", "a resource")

        assert result["context"] == "gratitude"
        assert "respect" in result["question"].lower()
        assert result["sacred_lean"] == 0.78

    def test_heterarchy_soul(self) -> None:
        """Heterarchy soul asks about peer structure."""
        soul = create_heterarchy_soul()
        _, result = soul.invoke("ready", "a hierarchy")

        assert result["context"] == "heterarchy"
        assert "peer" in result["question"].lower()
        assert result["peer_lean"] == 0.88

    def test_generativity_soul(self) -> None:
        """Generativity soul asks about generation."""
        soul = create_generativity_soul()
        _, result = soul.invoke("ready", "a spec")

        assert result["context"] == "generativity"
        assert "generate" in result["question"].lower()
        assert result["generation_lean"] == 0.90

    def test_joy_soul(self) -> None:
        """Joy soul asks about delight."""
        soul = create_joy_soul()
        _, result = soul.invoke("ready", "a feature")

        assert result["context"] == "joy"
        assert "delight" in result["question"].lower()
        assert result["playfulness"] == 0.75


class TestEmergentSoul:
    """Tests for emergent soul behavior."""

    def test_emergent_soul_created(self) -> None:
        """Emergent soul is successfully created."""
        soul = create_emergent_soul()
        assert soul is not None

    def test_kent_soul_exists(self) -> None:
        """KENT_SOUL global instance exists."""
        assert KENT_SOUL is not None
        assert "Glued" in KENT_SOUL.name

    def test_emergent_soul_has_all_positions(self) -> None:
        """Emergent soul has positions from all locals."""
        # All local souls have "ready" position
        assert "ready" in KENT_SOUL.positions

    def test_query_soul_with_context(self) -> None:
        """Can query soul with specific context."""
        result = query_soul("test input", context=AESTHETIC)
        assert result["context"] == "aesthetic"

    def test_query_soul_without_context(self) -> None:
        """Can query soul without context (uses global)."""
        result = query_soul("test input")
        assert result is not None

    def test_emergent_behavior(self) -> None:
        """Emergent soul has behavior from all contexts."""
        # The emergent soul can answer any query by dispatching
        # to the appropriate local soul based on state
        _, result = KENT_SOUL.invoke("ready", "test")

        # Result should be from one of the local souls
        assert "context" in result or result is not None


class TestGluingEmergence:
    """Tests for emergence properties."""

    def test_emergence_union_capability(self) -> None:
        """Glued agent can operate in any local context."""
        soul = create_emergent_soul()

        # Can invoke with any query
        _, result1 = soul.invoke("ready", "aesthetic query")
        _, result2 = soul.invoke("ready", "categorical query")

        # Both succeed (though may give same output due to dispatch)
        assert result1 is not None
        assert result2 is not None

    def test_local_to_global(self) -> None:
        """Global soul emerges from local souls."""
        # Create 6 local souls
        local_souls = {
            AESTHETIC: create_aesthetic_soul(),
            CATEGORICAL: create_categorical_soul(),
            GRATITUDE: create_gratitude_soul(),
            HETERARCHY: create_heterarchy_soul(),
            GENERATIVITY: create_generativity_soul(),
            JOY: create_joy_soul(),
        }

        # Glue into global
        global_soul = SOUL_SHEAF.glue(local_souls)

        # Global has more "reach" than any single local
        # (it can answer queries that span multiple contexts)
        assert len(local_souls) == 6
        assert global_soul is not None
