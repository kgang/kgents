"""
Tests for the Halo Capability Protocol.

Verifies:
1. Decorators add capabilities to __halo__
2. Multiple capabilities compose correctly
3. Capabilities are metadata only (no runtime effect)
4. Introspection functions work correctly
5. Halo inheritance works
"""

from __future__ import annotations

from dataclasses import dataclass

import pytest
from bootstrap.types import Agent

from ..halo import (
    HALO_ATTR,
    Capability,
    CapabilityBase,
    ObservableCapability,
    SoulfulCapability,
    StatefulCapability,
    StreamableCapability,
    TurnBasedCapability,
    get_capability,
    get_halo,
    has_capability,
    inherit_halo,
    merge_halos,
)

# --- Test Fixtures ---


@dataclass
class MockState:
    """Test state schema."""

    count: int = 0
    data: str = ""


class BaseAgent(Agent[str, str]):
    """Base test agent without any capabilities."""

    @property
    def name(self) -> str:
        return "base-agent"

    async def invoke(self, input: str) -> str:
        return f"echo: {input}"


# --- Test Capability Decorators ---


class TestCapabilityDecorators:
    """Tests for individual capability decorators."""

    def test_stateful_adds_to_halo(self) -> None:
        """@Stateful should add StatefulCapability to halo."""

        @Capability.Stateful(schema=MockState)
        class MyAgent(BaseAgent):
            pass

        halo = get_halo(MyAgent)
        assert len(halo) == 1
        assert has_capability(MyAgent, StatefulCapability)

    def test_stateful_stores_configuration(self) -> None:
        """@Stateful should preserve schema and backend config."""

        @Capability.Stateful(schema=MockState, backend="sqlite")
        class MyAgent(BaseAgent):
            pass

        cap = get_capability(MyAgent, StatefulCapability)
        assert cap is not None
        assert cap.schema is MockState
        assert cap.backend == "sqlite"

    def test_stateful_default_backend(self) -> None:
        """@Stateful should default to 'auto' backend."""

        @Capability.Stateful(schema=dict)
        class MyAgent(BaseAgent):
            pass

        cap = get_capability(MyAgent, StatefulCapability)
        assert cap is not None
        assert cap.backend == "auto"

    def test_soulful_adds_to_halo(self) -> None:
        """@Soulful should add SoulfulCapability to halo."""

        @Capability.Soulful(persona="Kent")
        class MyAgent(BaseAgent):
            pass

        halo = get_halo(MyAgent)
        assert len(halo) == 1
        assert has_capability(MyAgent, SoulfulCapability)

    def test_soulful_stores_configuration(self) -> None:
        """@Soulful should preserve persona and mode config."""

        @Capability.Soulful(persona="Kent", mode="strict")
        class MyAgent(BaseAgent):
            pass

        cap = get_capability(MyAgent, SoulfulCapability)
        assert cap is not None
        assert cap.persona == "Kent"
        assert cap.mode == "strict"

    def test_soulful_default_mode(self) -> None:
        """@Soulful should default to 'advisory' mode."""

        @Capability.Soulful(persona="Kent")
        class MyAgent(BaseAgent):
            pass

        cap = get_capability(MyAgent, SoulfulCapability)
        assert cap is not None
        assert cap.mode == "advisory"

    def test_observable_adds_to_halo(self) -> None:
        """@Observable should add ObservableCapability to halo."""

        @Capability.Observable()
        class MyAgent(BaseAgent):
            pass

        halo = get_halo(MyAgent)
        assert len(halo) == 1
        assert has_capability(MyAgent, ObservableCapability)

    def test_observable_stores_configuration(self) -> None:
        """@Observable should preserve mirror and metrics config."""

        @Capability.Observable(mirror=False, metrics=True)
        class MyAgent(BaseAgent):
            pass

        cap = get_capability(MyAgent, ObservableCapability)
        assert cap is not None
        assert cap.mirror is False
        assert cap.metrics is True

    def test_observable_defaults(self) -> None:
        """@Observable should default to mirror=True, metrics=True."""

        @Capability.Observable()
        class MyAgent(BaseAgent):
            pass

        cap = get_capability(MyAgent, ObservableCapability)
        assert cap is not None
        assert cap.mirror is True
        assert cap.metrics is True

    def test_streamable_adds_to_halo(self) -> None:
        """@Streamable should add StreamableCapability to halo."""

        @Capability.Streamable()
        class MyAgent(BaseAgent):
            pass

        halo = get_halo(MyAgent)
        assert len(halo) == 1
        assert has_capability(MyAgent, StreamableCapability)

    def test_streamable_stores_configuration(self) -> None:
        """@Streamable should preserve budget and feedback config."""

        @Capability.Streamable(budget=5.0, feedback=0.1)
        class MyAgent(BaseAgent):
            pass

        cap = get_capability(MyAgent, StreamableCapability)
        assert cap is not None
        assert cap.budget == 5.0
        assert cap.feedback == 0.1

    def test_streamable_defaults(self) -> None:
        """@Streamable should default to budget=10.0, feedback=0.0."""

        @Capability.Streamable()
        class MyAgent(BaseAgent):
            pass

        cap = get_capability(MyAgent, StreamableCapability)
        assert cap is not None
        assert cap.budget == 10.0
        assert cap.feedback == 0.0


# --- Test Capability Composition ---


class TestCapabilityComposition:
    """Tests for composing multiple capabilities."""

    def test_multiple_capabilities_compose(self) -> None:
        """Multiple decorators should add all capabilities to halo."""

        @Capability.Stateful(schema=dict)
        @Capability.Soulful(persona="Kent")
        @Capability.Observable()
        class MyAgent(BaseAgent):
            pass

        halo = get_halo(MyAgent)
        assert len(halo) == 3
        assert has_capability(MyAgent, StatefulCapability)
        assert has_capability(MyAgent, SoulfulCapability)
        assert has_capability(MyAgent, ObservableCapability)

    def test_all_four_capabilities(self) -> None:
        """All four standard capabilities should compose."""

        @Capability.Stateful(schema=MockState)
        @Capability.Soulful(persona="Kent", mode="strict")
        @Capability.Observable(mirror=True, metrics=True)
        @Capability.Streamable(budget=5.0, feedback=0.1)
        class MyAgent(BaseAgent):
            pass

        halo = get_halo(MyAgent)
        assert len(halo) == 4

        # Verify each capability is accessible
        stateful = get_capability(MyAgent, StatefulCapability)
        assert stateful is not None
        assert stateful.schema is MockState

        soulful = get_capability(MyAgent, SoulfulCapability)
        assert soulful is not None
        assert soulful.persona == "Kent"
        assert soulful.mode == "strict"

        observable = get_capability(MyAgent, ObservableCapability)
        assert observable is not None
        assert observable.mirror is True

        streamable = get_capability(MyAgent, StreamableCapability)
        assert streamable is not None
        assert streamable.budget == 5.0
        assert streamable.feedback == 0.1

    def test_duplicate_capability_type_replaces(self) -> None:
        """Same capability type applied twice keeps the last one (override semantics)."""

        @Capability.Stateful(schema=dict)  # Applied second (outermost) - this one wins
        @Capability.Stateful(schema=MockState)  # Applied first (innermost) - replaced
        class MyAgent(BaseAgent):
            pass

        halo = get_halo(MyAgent)
        # Override semantics: same type replaces, only ONE instance in halo
        stateful_caps = [c for c in halo if isinstance(c, StatefulCapability)]
        assert len(stateful_caps) == 1
        # The outermost decorator wins (applied last)
        assert stateful_caps[0].schema is dict

    def test_decoration_order_preserved(self) -> None:
        """Decorators are applied bottom-to-top."""

        @Capability.Stateful(schema=dict)  # Applied second
        @Capability.Soulful(persona="Kent")  # Applied first
        class MyAgent(BaseAgent):
            pass

        halo = get_halo(MyAgent)
        assert len(halo) == 2


# --- Test Metadata-Only Nature ---


class TestMetadataOnly:
    """Tests proving capabilities are metadata only (no runtime effect)."""

    @pytest.mark.anyio
    async def test_capability_does_not_change_invoke(self) -> None:
        """Decorated agent should behave identically to undecorated."""

        class PlainAgent(BaseAgent):
            async def invoke(self, input: str) -> str:
                return f"plain: {input}"

        @Capability.Stateful(schema=dict)
        @Capability.Soulful(persona="Kent")
        @Capability.Observable()
        @Capability.Streamable()
        class DecoratedAgent(BaseAgent):
            async def invoke(self, input: str) -> str:
                return f"plain: {input}"

        plain = PlainAgent()
        decorated = DecoratedAgent()

        # Both should produce identical output
        result_plain = await plain.invoke("test")
        result_decorated = await decorated.invoke("test")

        assert result_plain == result_decorated
        assert result_plain == "plain: test"

    def test_capability_does_not_change_name(self) -> None:
        """Decorated agent should have same name property."""

        @Capability.Stateful(schema=dict)
        class DecoratedAgent(BaseAgent):
            pass

        assert DecoratedAgent().name == "base-agent"

    def test_capability_does_not_wrap_class(self) -> None:
        """Decorator returns the same class, not a wrapper."""

        @Capability.Stateful(schema=dict)
        class DecoratedAgent(BaseAgent):
            pass

        # The decorator returns the same class object
        # (with __halo__ added)
        assert isinstance(DecoratedAgent(), BaseAgent)

    def test_halo_is_class_attribute(self) -> None:
        """Halo should be a class attribute, not instance attribute."""

        @Capability.Stateful(schema=dict)
        class MyAgent(BaseAgent):
            pass

        # Halo is on the class
        assert hasattr(MyAgent, HALO_ATTR)

        # Instances don't have their own halo
        instance = MyAgent()
        assert HALO_ATTR not in instance.__dict__


# --- Test Halo Introspection ---


class TestHaloIntrospection:
    """Tests for halo introspection functions."""

    def test_get_halo_empty(self) -> None:
        """get_halo on undecorated class returns empty set."""
        halo = get_halo(BaseAgent)
        assert halo == set()

    def test_get_halo_returns_copy(self) -> None:
        """get_halo should return a copy, not the original set."""

        @Capability.Stateful(schema=dict)
        class MyAgent(BaseAgent):
            pass

        halo1 = get_halo(MyAgent)
        halo2 = get_halo(MyAgent)

        # Should be equal
        assert halo1 == halo2

        # But not the same object
        assert halo1 is not halo2

        # Modifying one shouldn't affect the other
        halo1.add(SoulfulCapability(persona="test"))
        assert len(get_halo(MyAgent)) == 1  # Original unchanged

    def test_has_capability_true(self) -> None:
        """has_capability returns True when capability present."""

        @Capability.Stateful(schema=dict)
        class MyAgent(BaseAgent):
            pass

        assert has_capability(MyAgent, StatefulCapability) is True

    def test_has_capability_false(self) -> None:
        """has_capability returns False when capability absent."""

        @Capability.Stateful(schema=dict)
        class MyAgent(BaseAgent):
            pass

        assert has_capability(MyAgent, SoulfulCapability) is False

    def test_get_capability_found(self) -> None:
        """get_capability returns capability when present."""

        @Capability.Streamable(budget=42.0)
        class MyAgent(BaseAgent):
            pass

        cap = get_capability(MyAgent, StreamableCapability)
        assert cap is not None
        assert cap.budget == 42.0

    def test_get_capability_not_found(self) -> None:
        """get_capability returns None when not present."""

        @Capability.Stateful(schema=dict)
        class MyAgent(BaseAgent):
            pass

        cap = get_capability(MyAgent, SoulfulCapability)
        assert cap is None

    def test_get_capability_with_default(self) -> None:
        """get_capability returns default when not present."""

        @Capability.Stateful(schema=dict)
        class MyAgent(BaseAgent):
            pass

        default = StreamableCapability(budget=1.0)
        cap = get_capability(MyAgent, StreamableCapability, default)
        assert cap is default


# --- Test Halo Inheritance ---


class TestHaloInheritance:
    """Tests for halo inheritance between classes."""

    def test_child_inherits_parent_halo(self) -> None:
        """Child class should be able to inherit parent's halo."""

        @Capability.Stateful(schema=dict)
        class Parent(BaseAgent):
            pass

        class Child(Parent):
            pass

        # Child should have access to parent's halo via inheritance
        parent_halo = get_halo(Parent)
        child_halo = get_halo(Child)

        # By Python class attribute inheritance, child sees parent's halo
        assert child_halo == parent_halo

    def test_child_can_extend_halo(self) -> None:
        """Child can add capabilities while keeping parent's."""

        @Capability.Stateful(schema=dict)
        class Parent(BaseAgent):
            pass

        @Capability.Soulful(persona="Kent")
        class Child(Parent):
            pass

        child_halo = get_halo(Child)

        # Child has both capabilities
        assert has_capability(Child, StatefulCapability)
        assert has_capability(Child, SoulfulCapability)

    def test_inherit_halo_function(self) -> None:
        """inherit_halo should merge parent and child halos."""

        @Capability.Stateful(schema=dict)
        class Parent(BaseAgent):
            pass

        @Capability.Soulful(persona="Kent")
        class Child(Parent):
            pass

        merged = inherit_halo(Parent, Child)

        # Should have both
        assert len(merged) == 2
        assert any(isinstance(c, StatefulCapability) for c in merged)
        assert any(isinstance(c, SoulfulCapability) for c in merged)

    def test_child_override_parent_capability(self) -> None:
        """Child's capability should override parent's of same type in merge."""

        @Capability.Stateful(schema=dict, backend="sqlite")
        class Parent(BaseAgent):
            pass

        @Capability.Stateful(schema=MockState, backend="postgres")
        class Child(Parent):
            pass

        merged = inherit_halo(Parent, Child)

        # merge_halos keeps later (child) capability
        stateful_caps = [c for c in merged if isinstance(c, StatefulCapability)]
        assert len(stateful_caps) == 1
        assert stateful_caps[0].backend == "postgres"


# --- Test Merge Halos ---


class TestMergeHalos:
    """Tests for merge_halos function."""

    def test_merge_empty_halos(self) -> None:
        """Merging empty halos returns empty set."""
        result = merge_halos(set(), set())
        assert result == set()

    def test_merge_single_halo(self) -> None:
        """Merging single halo returns copy."""
        cap: CapabilityBase = StatefulCapability(schema=dict)
        halo: set[CapabilityBase] = {cap}
        result = merge_halos(halo)
        assert result == halo
        assert result is not halo

    def test_merge_disjoint_halos(self) -> None:
        """Merging halos with different capabilities combines them."""
        halo1: set[CapabilityBase] = {StatefulCapability(schema=dict)}
        halo2: set[CapabilityBase] = {SoulfulCapability(persona="Kent")}

        result = merge_halos(halo1, halo2)

        assert len(result) == 2
        assert any(isinstance(c, StatefulCapability) for c in result)
        assert any(isinstance(c, SoulfulCapability) for c in result)

    def test_merge_overlapping_halos(self) -> None:
        """Later halo's capability overrides earlier for same type."""
        halo1: set[CapabilityBase] = {StatefulCapability(schema=dict, backend="sqlite")}
        halo2: set[CapabilityBase] = {
            StatefulCapability(schema=MockState, backend="postgres")
        }

        result = merge_halos(halo1, halo2)

        assert len(result) == 1
        cap = list(result)[0]
        assert isinstance(cap, StatefulCapability)
        assert cap.backend == "postgres"  # halo2's value

    def test_merge_multiple_halos(self) -> None:
        """Can merge more than two halos."""
        halo1: set[CapabilityBase] = {StatefulCapability(schema=dict)}
        halo2: set[CapabilityBase] = {SoulfulCapability(persona="Kent")}
        halo3: set[CapabilityBase] = {ObservableCapability()}
        halo4: set[CapabilityBase] = {StreamableCapability(budget=5.0)}

        result = merge_halos(halo1, halo2, halo3, halo4)

        assert len(result) == 4


# --- Test Capability Equality and Hashing ---


class TestCapabilityEquality:
    """Tests for capability equality and hashing."""

    def test_same_config_equals(self) -> None:
        """Capabilities with same config should be equal."""
        cap1 = StatefulCapability(schema=dict, backend="auto")
        cap2 = StatefulCapability(schema=dict, backend="auto")

        assert cap1 == cap2
        assert hash(cap1) == hash(cap2)

    def test_different_config_not_equals(self) -> None:
        """Capabilities with different config should not be equal."""
        cap1 = StatefulCapability(schema=dict, backend="sqlite")
        cap2 = StatefulCapability(schema=dict, backend="postgres")

        assert cap1 != cap2

    def test_different_types_not_equals(self) -> None:
        """Different capability types should not be equal."""
        cap1: CapabilityBase = StatefulCapability(schema=dict)
        cap2: CapabilityBase = SoulfulCapability(persona="Kent")

        assert cap1 != cap2

    def test_capabilities_hashable_for_sets(self) -> None:
        """Capabilities should be usable in sets."""
        caps = {
            StatefulCapability(schema=dict),
            SoulfulCapability(persona="Kent"),
            ObservableCapability(),
            StreamableCapability(),
        }

        assert len(caps) == 4

    def test_duplicate_capabilities_dedupe_in_set(self) -> None:
        """Duplicate capabilities should be deduped in sets."""
        caps = {
            StatefulCapability(schema=dict, backend="auto"),
            StatefulCapability(schema=dict, backend="auto"),  # Duplicate
        }

        assert len(caps) == 1


# --- Test Edge Cases ---


class TestEdgeCases:
    """Tests for edge cases and error conditions."""

    def test_decorate_non_agent_class(self) -> None:
        """Capability can decorate any class (no enforcement)."""

        @Capability.Stateful(schema=dict)
        class NotAnAgent:
            pass

        # Works but caller should ensure it's meaningful
        assert has_capability(NotAnAgent, StatefulCapability)

    def test_decorate_function_works_but_meaningless(self) -> None:
        """Decorating a function works (Python allows setattr on functions)."""
        # Note: This works in Python but is meaningless since functions
        # aren't agents. We allow it for simplicity - it's the caller's
        # responsibility to use capabilities on agent classes.

        @Capability.Stateful(schema=dict)  # type: ignore
        def my_function() -> str:
            return "hello"

        # It works - function has halo attribute
        assert has_capability(my_function, StatefulCapability)  # type: ignore
        # But the function still works normally
        assert my_function() == "hello"

    def test_capability_base_is_decorator(self) -> None:
        """CapabilityBase instances can be used as decorators."""

        cap = StatefulCapability(schema=dict)

        @cap
        class MyAgent(BaseAgent):
            pass

        assert has_capability(MyAgent, StatefulCapability)

    def test_empty_schema_type(self) -> None:
        """Can use simple types as schema."""

        @Capability.Stateful(schema=dict)
        class Agent1(BaseAgent):
            pass

        @Capability.Stateful(schema=list)
        class Agent2(BaseAgent):
            pass

        cap1 = get_capability(Agent1, StatefulCapability)
        cap2 = get_capability(Agent2, StatefulCapability)

        assert cap1 is not None
        assert cap2 is not None
        assert cap1.schema is dict
        assert cap2.schema is list


# --- Test TurnBasedCapability ---


class TestTurnBasedCapability:
    """Tests for TurnBasedCapability (Turn-gents Protocol)."""

    def test_turnbased_adds_to_halo(self) -> None:
        """@TurnBased should add TurnBasedCapability to halo."""

        @Capability.TurnBased()
        class MyAgent(BaseAgent):
            pass

        halo = get_halo(MyAgent)
        assert len(halo) == 1
        assert has_capability(MyAgent, TurnBasedCapability)

    def test_turnbased_default_configuration(self) -> None:
        """@TurnBased should have sensible defaults."""

        @Capability.TurnBased()
        class MyAgent(BaseAgent):
            pass

        cap = get_capability(MyAgent, TurnBasedCapability)
        assert cap is not None
        assert cap.allowed_types is None  # All types allowed
        assert cap.dependency_policy == "causal_cone"
        assert cap.cone_depth is None  # Unlimited
        assert cap.thought_collapse is True
        assert cap.entropy_budget == 1.0
        assert cap.surplus_fraction == 0.1
        assert cap.yield_threshold == 0.3

    def test_turnbased_custom_configuration(self) -> None:
        """@TurnBased should store custom configuration."""

        @Capability.TurnBased(
            allowed_types={"SPEECH", "ACTION"},
            dependency_policy="thread_only",
            cone_depth=10,
            thought_collapse=False,
            entropy_budget=5.0,
            surplus_fraction=0.2,
            yield_threshold=0.5,
        )
        class MyAgent(BaseAgent):
            pass

        cap = get_capability(MyAgent, TurnBasedCapability)
        assert cap is not None
        assert cap.allowed_types == frozenset({"SPEECH", "ACTION"})
        assert cap.dependency_policy == "thread_only"
        assert cap.cone_depth == 10
        assert cap.thought_collapse is False
        assert cap.entropy_budget == 5.0
        assert cap.surplus_fraction == 0.2
        assert cap.yield_threshold == 0.5

    def test_turnbased_composes_with_other_capabilities(self) -> None:
        """@TurnBased should compose with other capabilities."""

        @Capability.Stateful(schema=MockState)
        @Capability.TurnBased(entropy_budget=10.0)
        @Capability.Observable()
        class MyAgent(BaseAgent):
            pass

        halo = get_halo(MyAgent)
        assert len(halo) == 3
        assert has_capability(MyAgent, StatefulCapability)
        assert has_capability(MyAgent, TurnBasedCapability)
        assert has_capability(MyAgent, ObservableCapability)

    def test_turnbased_override_in_subclass(self) -> None:
        """Child can override parent's TurnBased configuration."""

        @Capability.TurnBased(entropy_budget=1.0)
        class Parent(BaseAgent):
            pass

        @Capability.TurnBased(entropy_budget=10.0)
        class Child(Parent):
            pass

        parent_cap = get_capability(Parent, TurnBasedCapability)
        child_cap = get_capability(Child, TurnBasedCapability)

        assert parent_cap is not None
        assert child_cap is not None
        assert parent_cap.entropy_budget == 1.0
        assert child_cap.entropy_budget == 10.0

    def test_turnbased_allowed_types_converted_to_frozenset(self) -> None:
        """allowed_types should be converted to frozenset."""

        @Capability.TurnBased(allowed_types={"SPEECH"})
        class MyAgent(BaseAgent):
            pass

        cap = get_capability(MyAgent, TurnBasedCapability)
        assert cap is not None
        assert isinstance(cap.allowed_types, frozenset)

    def test_turnbased_is_hashable(self) -> None:
        """TurnBasedCapability should be hashable for set storage."""
        cap1 = TurnBasedCapability()
        cap2 = TurnBasedCapability(entropy_budget=5.0)
        cap3 = TurnBasedCapability()  # Same as cap1

        caps = {cap1, cap2, cap3}
        assert len(caps) == 2  # cap1 and cap3 are equal

    def test_turnbased_equality(self) -> None:
        """TurnBasedCapability equality should work correctly."""
        cap1 = TurnBasedCapability(entropy_budget=1.0)
        cap2 = TurnBasedCapability(entropy_budget=1.0)
        cap3 = TurnBasedCapability(entropy_budget=2.0)

        assert cap1 == cap2
        assert cap1 != cap3
