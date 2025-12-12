"""
AGENTESE Phase 2: Five Contexts Tests

Tests for the five strict contexts:
- world.*   - The External (Heterarchical)
- self.*    - The Internal (Ethical)
- concept.* - The Abstract (Generative)
- void.*    - The Accursed Share (Meta-Principle)
- time.*    - The Temporal (Heterarchical)
"""

from __future__ import annotations

from datetime import datetime, timedelta
from typing import TYPE_CHECKING, Any

import pytest
from shared.capital import EventSourcedLedger, InsufficientCapitalError
from testing.fixtures import as_umwelt

from ..contexts import (
    VALID_CONTEXTS,
    CapabilitiesNode,
    CapitalNode,
    ConceptNode,
    EntropyNode,
    FutureNode,
    GratitudeNode,
    IdentityNode,
    MemoryNode,
    PastNode,
    ScheduleNode,
    SerendipityNode,
    StateNode,
    # Time
    TraceNode,
    # World
    WorldNode,
    create_concept_node,
    create_concept_resolver,
    create_entropy_pool,
    create_self_resolver,
    create_time_resolver,
    create_void_resolver,
    create_world_node,
    create_world_resolver,
)
from ..contexts.concept import ConceptContextResolver
from ..contexts.self_ import SelfContextResolver
from ..contexts.time import TimeContextResolver
from ..contexts.void import EntropyPool, VoidContextResolver
from ..contexts.world import WorldContextResolver
from ..logos import Logos
from ..node import AgentMeta, BasicRendering, LogosNode
from .conftest import MockUmwelt

if TYPE_CHECKING:
    from bootstrap.umwelt import Umwelt

# ============================================================
# VALID CONTEXTS TESTS
# ============================================================


class TestValidContexts:
    """Test that only five contexts are allowed."""

    def test_exactly_five_contexts(self) -> None:
        """There are exactly five valid contexts."""
        assert len(VALID_CONTEXTS) == 5

    def test_context_names(self) -> None:
        """The five contexts have the correct names."""
        assert VALID_CONTEXTS == frozenset({"world", "self", "concept", "void", "time"})

    def test_contexts_immutable(self) -> None:
        """VALID_CONTEXTS is a frozenset (immutable)."""
        assert isinstance(VALID_CONTEXTS, frozenset)


# ============================================================
# WORLD CONTEXT TESTS
# ============================================================


class TestWorldNode:
    """Tests for WorldNode."""

    @pytest.fixture
    def world_node(self) -> WorldNode:
        return create_world_node(
            name="house",
            description="A beautiful house",
            entity_type="building",
            state={
                "dimensions": {"width": 10, "height": 8},
                "materials": ["wood", "stone"],
            },
        )

    @pytest.fixture
    def observer(self) -> MockUmwelt:
        return MockUmwelt(archetype="default")

    def test_handle(self, world_node: WorldNode) -> None:
        """Node has correct handle."""
        assert world_node.handle == "world.house"

    def test_base_affordances(
        self, world_node: WorldNode, observer: MockUmwelt
    ) -> None:
        """All nodes have base affordances."""
        meta = AgentMeta(name="test", archetype="default")
        affordances = world_node.affordances(meta)
        assert "manifest" in affordances
        assert "witness" in affordances
        assert "affordances" in affordances

    def test_architect_affordances(self, world_node: WorldNode) -> None:
        """Architect archetype has extra affordances."""
        meta = AgentMeta(name="test", archetype="architect")
        affordances = world_node.affordances(meta)
        assert "renovate" in affordances
        assert "blueprint" in affordances
        assert "demolish" in affordances

    def test_poet_affordances(self, world_node: WorldNode) -> None:
        """Poet archetype has different affordances."""
        meta = AgentMeta(name="test", archetype="poet")
        affordances = world_node.affordances(meta)
        assert "describe" in affordances
        assert "metaphorize" in affordances
        assert "inhabit" in affordances
        assert "renovate" not in affordances  # Not an architect

    @pytest.mark.asyncio
    async def test_manifest_default(
        self, world_node: WorldNode, observer: MockUmwelt
    ) -> None:
        """Default manifest returns BasicRendering."""
        result = await world_node.manifest(as_umwelt(observer))
        assert isinstance(result, BasicRendering)
        assert "house" in result.summary.lower()

    @pytest.mark.asyncio
    async def test_manifest_architect(self, world_node: WorldNode) -> None:
        """Architect sees BlueprintRendering."""
        observer = MockUmwelt(archetype="architect")
        result = await world_node.manifest(as_umwelt(observer))
        # Should be BlueprintRendering
        assert hasattr(result, "dimensions") or "blueprint" in str(type(result)).lower()

    @pytest.mark.asyncio
    async def test_invoke_witness(
        self, world_node: WorldNode, observer: MockUmwelt
    ) -> None:
        """Witness aspect returns history."""
        result = await world_node.invoke("witness", as_umwelt(observer))
        assert "handle" in result or "history" in result


class TestWorldContextResolver:
    """Tests for WorldContextResolver."""

    @pytest.fixture
    def resolver(self) -> WorldContextResolver:
        return create_world_resolver()

    def test_resolve_creates_node(self, resolver: WorldContextResolver) -> None:
        """Resolver creates a node for unknown holons."""
        node = resolver.resolve("house", [])
        assert node.handle == "world.house"
        assert isinstance(node, WorldNode)

    def test_resolve_caches_node(self, resolver: WorldContextResolver) -> None:
        """Resolved nodes are cached."""
        node1 = resolver.resolve("house", [])
        node2 = resolver.resolve("house", [])
        assert node1 is node2

    def test_list_handles(self, resolver: WorldContextResolver) -> None:
        """List handles returns cached handles."""
        resolver.resolve("house", [])
        resolver.resolve("server", [])
        handles = resolver.list_handles()
        assert "world.house" in handles
        assert "world.server" in handles


# ============================================================
# SELF CONTEXT TESTS
# ============================================================


class TestMemoryNode:
    """Tests for MemoryNode."""

    @pytest.fixture
    def memory_node(self) -> MemoryNode:
        return MemoryNode()

    @pytest.fixture
    def observer(self) -> MockUmwelt:
        return MockUmwelt(archetype="default")

    def test_handle(self, memory_node: MemoryNode) -> None:
        """Memory node has correct handle."""
        assert memory_node.handle == "self.memory"

    def test_affordances(self, memory_node: MemoryNode) -> None:
        """Memory node has memory affordances."""
        meta = AgentMeta(name="test", archetype="default")
        affordances = memory_node.affordances(meta)
        assert "consolidate" in affordances
        assert "prune" in affordances
        assert "checkpoint" in affordances
        assert "recall" in affordances

    @pytest.mark.asyncio
    async def test_checkpoint_creates_snapshot(
        self, memory_node: MemoryNode, observer: MockUmwelt
    ) -> None:
        """Checkpoint creates a memory snapshot."""
        result = await memory_node.invoke(
            "checkpoint",
            as_umwelt(observer),
            label="test_checkpoint",
        )
        assert result["label"] == "test_checkpoint"
        assert "timestamp" in result

    @pytest.mark.asyncio
    async def test_consolidate(
        self, memory_node: MemoryNode, observer: MockUmwelt
    ) -> None:
        """Consolidate processes temporary memories."""
        memory_node._memories["test"] = {"temporary": True, "data": "value"}
        result = await memory_node.invoke("consolidate", as_umwelt(observer))
        assert "consolidated" in result
        # Memory should no longer be temporary
        assert memory_node._memories["test"]["temporary"] is False


class TestCapabilitiesNode:
    """Tests for CapabilitiesNode."""

    @pytest.fixture
    def capabilities_node(self) -> CapabilitiesNode:
        return CapabilitiesNode()

    @pytest.fixture
    def observer(self) -> MockUmwelt:
        return MockUmwelt(archetype="default")

    @pytest.mark.asyncio
    async def test_acquire_capability(
        self, capabilities_node: CapabilitiesNode, observer: MockUmwelt
    ) -> None:
        """Can acquire new capabilities."""
        result = await capabilities_node.invoke(
            "acquire",
            as_umwelt(observer),
            capability="flying",
        )
        assert result["acquired"] == "flying"
        assert "flying" in capabilities_node._capabilities

    @pytest.mark.asyncio
    async def test_release_capability(
        self, capabilities_node: CapabilitiesNode, observer: MockUmwelt
    ) -> None:
        """Can release capabilities."""
        capabilities_node._capabilities.add("flying")
        result = await capabilities_node.invoke(
            "release",
            as_umwelt(observer),
            capability="flying",
        )
        assert result["released"] == "flying"
        assert "flying" not in capabilities_node._capabilities


class TestSelfContextResolver:
    """Tests for SelfContextResolver."""

    @pytest.fixture
    def resolver(self) -> SelfContextResolver:
        return create_self_resolver()

    def test_resolve_memory(self, resolver: WorldContextResolver) -> None:
        """Resolves self.memory."""
        node = resolver.resolve("memory", [])
        assert isinstance(node, MemoryNode)

    def test_resolve_capabilities(self, resolver: WorldContextResolver) -> None:
        """Resolves self.capabilities."""
        node = resolver.resolve("capabilities", [])
        assert isinstance(node, CapabilitiesNode)

    def test_resolve_state(self, resolver: WorldContextResolver) -> None:
        """Resolves self.state."""
        node = resolver.resolve("state", [])
        assert isinstance(node, StateNode)

    def test_resolve_identity(self, resolver: WorldContextResolver) -> None:
        """Resolves self.identity."""
        node = resolver.resolve("identity", [])
        assert isinstance(node, IdentityNode)


# ============================================================
# CONCEPT CONTEXT TESTS
# ============================================================


class TestConceptNode:
    """Tests for ConceptNode."""

    @pytest.fixture
    def concept_node(self) -> ConceptNode:
        return create_concept_node(
            name="justice",
            definition="The quality of being fair and reasonable",
            domain="philosophy",
            examples=["fair trial", "equal treatment"],
            related=["fairness", "equality"],
        )

    @pytest.fixture
    def observer(self) -> MockUmwelt:
        return MockUmwelt(archetype="default")

    def test_handle(self, concept_node: ConceptNode) -> None:
        """Concept has correct handle."""
        assert concept_node.handle == "concept.justice"

    def test_philosopher_affordances(self, concept_node: ConceptNode) -> None:
        """Philosopher has dialectical affordances."""
        meta = AgentMeta(name="test", archetype="philosopher")
        affordances = concept_node.affordances(meta)
        assert "refine" in affordances
        assert "dialectic" in affordances
        assert "synthesize" in affordances
        assert "critique" in affordances

    def test_scientist_affordances(self, concept_node: ConceptNode) -> None:
        """Scientist has empirical affordances."""
        meta = AgentMeta(name="test", archetype="scientist")
        affordances = concept_node.affordances(meta)
        assert "hypothesize" in affordances
        assert "validate" in affordances

    @pytest.mark.asyncio
    async def test_refine(
        self, concept_node: ConceptNode, observer: MockUmwelt
    ) -> None:
        """Refine challenges the concept definition."""
        result = await concept_node.invoke(
            "refine",
            as_umwelt(observer),
            challenge="What are the limits of justice?",
        )
        assert "refined" in result
        assert "challenge" in result

    @pytest.mark.asyncio
    async def test_dialectic(
        self, concept_node: ConceptNode, observer: MockUmwelt
    ) -> None:
        """Dialectic generates thesis/antithesis/synthesis."""
        result = await concept_node.invoke("dialectic", as_umwelt(observer))
        assert "thesis" in result
        assert "antithesis" in result
        assert "synthesis" in result

    @pytest.mark.asyncio
    async def test_relate(
        self, concept_node: ConceptNode, observer: MockUmwelt
    ) -> None:
        """Relate finds concept connections."""
        result = await concept_node.invoke(
            "relate", as_umwelt(observer), target="fairness"
        )
        assert result["target"] == "fairness"
        assert "fairness" in result["all_relations"]


class TestConceptContextResolver:
    """Tests for ConceptContextResolver."""

    @pytest.fixture
    def resolver(self) -> ConceptContextResolver:
        return create_concept_resolver()

    def test_resolve_creates_concept(self, resolver: WorldContextResolver) -> None:
        """Resolver creates concept for unknown names."""
        node = resolver.resolve("recursion", [])
        assert node.handle == "concept.recursion"
        assert isinstance(node, ConceptNode)

    def test_resolve_caches_concept(self, resolver: WorldContextResolver) -> None:
        """Resolved concepts are cached."""
        node1 = resolver.resolve("recursion", [])
        node2 = resolver.resolve("recursion", [])
        assert node1 is node2


# ============================================================
# VOID CONTEXT TESTS
# ============================================================


class TestEntropyPool:
    """Tests for EntropyPool (Accursed Share)."""

    @pytest.fixture
    def pool(self) -> EntropyPool:
        return create_entropy_pool(initial_budget=100.0)

    def test_initial_budget(self, pool: EntropyPool) -> None:
        """Pool starts with full budget."""
        assert pool.remaining == 100.0

    def test_sip_reduces_budget(self, pool: EntropyPool) -> None:
        """Sip reduces entropy budget."""
        pool.sip(10.0)
        assert pool.remaining == 90.0

    def test_sip_returns_seed(self, pool: EntropyPool) -> None:
        """Sip returns randomness."""
        result = pool.sip(1.0)
        assert "seed" in result
        assert 0.0 <= result["seed"] <= 1.0

    def test_sip_budget_exhausted(self, pool: EntropyPool) -> None:
        """Sip raises when budget exhausted."""
        from ..exceptions import BudgetExhaustedError

        pool.remaining = 5.0
        with pytest.raises(BudgetExhaustedError):
            pool.sip(10.0)

    def test_pour_recovers_partial(self, pool: EntropyPool) -> None:
        """Pour recovers partial entropy."""
        pool.remaining = 50.0
        result = pool.pour(20.0, recovery_rate=0.5)
        assert result["recovered"] == 10.0
        assert pool.remaining == 60.0

    def test_tithe_regenerates(self, pool: EntropyPool) -> None:
        """Tithe regenerates some entropy."""
        pool.remaining = 50.0
        result = pool.tithe()
        assert pool.remaining > 50.0
        assert "gratitude" in result


class TestVoidNodes:
    """Tests for void context nodes."""

    @pytest.fixture
    def observer(self) -> MockUmwelt:
        return MockUmwelt(archetype="default")

    @pytest.mark.asyncio
    async def test_entropy_sip(self, observer: MockUmwelt) -> None:
        """Entropy node can sip randomness."""
        node = EntropyNode()
        result = await node.invoke("sip", as_umwelt(observer), amount=1.0)
        assert "seed" in result
        assert "amount" in result

    @pytest.mark.asyncio
    async def test_serendipity_tangent(self, observer: MockUmwelt) -> None:
        """Serendipity generates tangents."""
        node = SerendipityNode()
        result = await node.invoke("sip", as_umwelt(observer), context="testing")
        assert "tangent" in result
        assert len(result["tangent"]) > 0

    @pytest.mark.asyncio
    async def test_gratitude_tithe(self, observer: MockUmwelt) -> None:
        """Gratitude accepts tithes."""
        node = GratitudeNode()
        result = await node.invoke("tithe", as_umwelt(observer))
        assert "gratitude" in result

    @pytest.mark.asyncio
    async def test_gratitude_thank(self, observer: MockUmwelt) -> None:
        """Gratitude accepts thanks."""
        node = GratitudeNode()
        result = await node.invoke("thank", as_umwelt(observer), target="the universe")
        assert result["target"] == "the universe"


class TestVoidContextResolver:
    """Tests for VoidContextResolver."""

    @pytest.fixture
    def resolver(self) -> VoidContextResolver:
        return create_void_resolver(initial_budget=100.0)

    def test_resolve_entropy(self, resolver: VoidContextResolver) -> None:
        """Resolves void.entropy."""
        node = resolver.resolve("entropy", [])
        assert isinstance(node, EntropyNode)

    def test_resolve_serendipity(self, resolver: VoidContextResolver) -> None:
        """Resolves void.serendipity."""
        node = resolver.resolve("serendipity", [])
        assert isinstance(node, SerendipityNode)

    def test_resolve_gratitude(self, resolver: VoidContextResolver) -> None:
        """Resolves void.gratitude."""
        node = resolver.resolve("gratitude", [])
        assert isinstance(node, GratitudeNode)

    def test_shared_entropy_pool(self, resolver: VoidContextResolver) -> None:
        """All void nodes share the same entropy pool."""
        entropy = resolver.resolve("entropy", [])
        serendipity = resolver.resolve("serendipity", [])
        gratitude = resolver.resolve("gratitude", [])
        assert entropy._pool is serendipity._pool  # type: ignore[attr-defined]
        assert serendipity._pool is gratitude._pool  # type: ignore[attr-defined]

    def test_resolve_capital(self, resolver: VoidContextResolver) -> None:
        """Resolves void.capital."""
        node = resolver.resolve("capital", [])
        assert isinstance(node, CapitalNode)

    def test_shared_capital_ledger(self) -> None:
        """VoidContextResolver with injected ledger shares it with capital node."""
        ledger = EventSourcedLedger()
        resolver = create_void_resolver(ledger=ledger)
        capital = resolver.resolve("capital", [])
        assert capital._ledger is ledger  # type: ignore[attr-defined]


class TestCapitalNode:
    """Tests for CapitalNode (void.capital.*)."""

    @pytest.fixture
    def ledger(self) -> EventSourcedLedger:
        """Fresh ledger per test."""
        return EventSourcedLedger()

    @pytest.fixture
    def capital_node(self, ledger: EventSourcedLedger) -> CapitalNode:
        """Capital node with injected ledger."""
        return CapitalNode(_ledger=ledger)

    @pytest.fixture
    def observer(self) -> MockUmwelt:
        return MockUmwelt(archetype="default")

    @pytest.fixture
    def named_observer(self) -> MockUmwelt:
        """Observer with a specific name for capital tracking."""
        from .conftest import MockDNA

        return MockUmwelt(dna=MockDNA(name="test-agent", archetype="default"))

    def test_handle(self, capital_node: CapitalNode) -> None:
        """Capital node has correct handle."""
        assert capital_node.handle == "void.capital"

    def test_affordances(self, capital_node: CapitalNode) -> None:
        """Capital node has capital affordances."""
        meta = AgentMeta(name="test", archetype="default")
        affordances = capital_node.affordances(meta)
        assert "balance" in affordances
        assert "history" in affordances
        assert "tithe" in affordances
        assert "bypass" in affordances

    @pytest.mark.asyncio
    async def test_manifest_shows_balance(
        self, capital_node: CapitalNode, named_observer: MockUmwelt
    ) -> None:
        """Manifest returns balance rendering."""
        result = await capital_node.manifest(as_umwelt(named_observer))
        assert isinstance(result, BasicRendering)
        assert "Capital Ledger" in result.summary
        assert "balance" in result.metadata

    @pytest.mark.asyncio
    async def test_balance_aspect(
        self, capital_node: CapitalNode, named_observer: MockUmwelt
    ) -> None:
        """Balance aspect returns agent balance."""
        result = await capital_node.invoke("balance", as_umwelt(named_observer))
        assert "agent" in result
        assert "balance" in result
        assert result["balance"] == 0.5  # initial_capital

    @pytest.mark.asyncio
    async def test_witness_aspect(
        self,
        capital_node: CapitalNode,
        ledger: EventSourcedLedger,
        named_observer: MockUmwelt,
    ) -> None:
        """Witness aspect returns event history."""
        # Add some history
        ledger.credit("test-agent", 0.1, "test_credit")
        ledger.debit("test-agent", 0.05, "test_debit")

        result = await capital_node.invoke("witness", as_umwelt(named_observer))
        assert "events" in result
        assert result["count"] == 2

    @pytest.mark.asyncio
    async def test_history_aspect_alias(
        self,
        capital_node: CapitalNode,
        ledger: EventSourcedLedger,
        named_observer: MockUmwelt,
    ) -> None:
        """History aspect is alias for witness."""
        ledger.credit("test-agent", 0.1, "test")

        result = await capital_node.invoke("history", as_umwelt(named_observer))
        assert "events" in result
        assert result["count"] == 1

    @pytest.mark.asyncio
    async def test_tithe_burns_capital(
        self,
        capital_node: CapitalNode,
        ledger: EventSourcedLedger,
        named_observer: MockUmwelt,
    ) -> None:
        """Tithe (potlatch) burns capital."""
        initial = ledger.balance("test-agent")

        result = await capital_node.invoke(
            "tithe", as_umwelt(named_observer), amount=0.1
        )

        assert result["ritual"] == "potlatch"
        assert result["amount"] == 0.1
        assert result["remaining"] < initial
        assert "gratitude" in result

    @pytest.mark.asyncio
    async def test_tithe_insufficient_raises(
        self,
        capital_node: CapitalNode,
        ledger: EventSourcedLedger,
        named_observer: MockUmwelt,
    ) -> None:
        """Tithe raises InsufficientCapitalError if insufficient balance."""
        with pytest.raises(InsufficientCapitalError):
            await capital_node.invoke("tithe", as_umwelt(named_observer), amount=10.0)

    @pytest.mark.asyncio
    async def test_bypass_mints_token(
        self,
        capital_node: CapitalNode,
        ledger: EventSourcedLedger,
        named_observer: MockUmwelt,
    ) -> None:
        """Bypass mints a BypassToken."""
        result = await capital_node.invoke(
            "bypass",
            as_umwelt(named_observer),
            check="trust_gate",
            cost=0.1,
        )

        assert "token" in result
        token = result["token"]
        assert token.check_name == "trust_gate"
        assert token.cost == 0.1
        assert token.agent == "test-agent"
        assert token.is_valid()

    @pytest.mark.asyncio
    async def test_bypass_insufficient_raises(
        self,
        capital_node: CapitalNode,
        ledger: EventSourcedLedger,
        named_observer: MockUmwelt,
    ) -> None:
        """Bypass raises InsufficientCapitalError if insufficient balance."""
        with pytest.raises(InsufficientCapitalError):
            await capital_node.invoke(
                "bypass",
                as_umwelt(named_observer),
                check="trust_gate",
                cost=10.0,
            )

    @pytest.mark.asyncio
    async def test_bypass_deducts_cost(
        self,
        capital_node: CapitalNode,
        ledger: EventSourcedLedger,
        named_observer: MockUmwelt,
    ) -> None:
        """Bypass deducts cost from agent's balance."""
        initial = ledger.balance("test-agent")

        await capital_node.invoke(
            "bypass",
            as_umwelt(named_observer),
            check="trust_gate",
            cost=0.1,
        )

        final = ledger.balance("test-agent")
        assert final == initial - 0.1


class TestCapitalLogosIntegration:
    """Test capital integration with Logos."""

    @pytest.fixture
    def ledger(self) -> EventSourcedLedger:
        return EventSourcedLedger()

    @pytest.fixture
    def logos_with_capital(self, ledger: EventSourcedLedger) -> Logos:
        from ..logos import create_logos

        return create_logos(capital_ledger=ledger)

    @pytest.fixture
    def named_observer(self) -> MockUmwelt:
        from .conftest import MockDNA

        return MockUmwelt(dna=MockDNA(name="test-agent", archetype="default"))

    def test_resolve_void_capital(self, logos_with_capital: Logos) -> None:
        """Logos resolves void.capital path."""
        node = logos_with_capital.resolve("void.capital")
        assert node.handle == "void.capital"
        assert isinstance(node, CapitalNode)

    @pytest.mark.asyncio
    async def test_invoke_void_capital_balance(
        self, logos_with_capital: Logos, named_observer: MockUmwelt
    ) -> None:
        """Invoke void.capital.balance through Logos."""
        result = await logos_with_capital.invoke(
            "void.capital.balance", as_umwelt(named_observer)
        )
        assert "balance" in result
        assert result["agent"] == "test-agent"

    @pytest.mark.asyncio
    async def test_invoke_void_capital_tithe(
        self, logos_with_capital: Logos, named_observer: MockUmwelt
    ) -> None:
        """Invoke void.capital.tithe through Logos."""
        result = await logos_with_capital.invoke(
            "void.capital.tithe",
            as_umwelt(named_observer),
            amount=0.1,
        )
        assert result["ritual"] == "potlatch"


# ============================================================
# TIME CONTEXT TESTS
# ============================================================


class TestTraceNode:
    """Tests for TraceNode."""

    @pytest.fixture
    def trace_node(self) -> TraceNode:
        node = TraceNode()
        # Add some test traces
        node.record({"event": "created", "data": "test1"})
        node.record({"event": "modified", "data": "test2"})
        return node

    @pytest.fixture
    def observer(self) -> MockUmwelt:
        return MockUmwelt(archetype="default")

    @pytest.mark.asyncio
    async def test_witness(self, trace_node: TraceNode, observer: MockUmwelt) -> None:
        """Witness returns traces."""
        result = await trace_node.invoke("witness", as_umwelt(observer), limit=10)
        assert "traces" in result
        assert len(result["traces"]) == 2

    @pytest.mark.asyncio
    async def test_query(self, trace_node: TraceNode, observer: MockUmwelt) -> None:
        """Query filters traces."""
        result = await trace_node.invoke("query", as_umwelt(observer), query="created")
        assert len(result["results"]) == 1
        assert result["results"][0]["event"] == "created"


class TestScheduleNode:
    """Tests for ScheduleNode."""

    @pytest.fixture
    def schedule_node(self) -> ScheduleNode:
        return ScheduleNode()

    @pytest.fixture
    def observer(self) -> MockUmwelt:
        return MockUmwelt(archetype="default")

    @pytest.mark.asyncio
    async def test_defer_with_delay(
        self, schedule_node: ScheduleNode, observer: MockUmwelt
    ) -> None:
        """Defer schedules action with delay."""
        result = await schedule_node.invoke(
            "defer",
            as_umwelt(observer),
            path="world.task.execute",
            delay=60,  # 60 seconds
        )
        assert "id" in result
        assert result["status"] == "scheduled"
        assert result["path"] == "world.task.execute"

    @pytest.mark.asyncio
    async def test_defer_with_at(
        self, schedule_node: ScheduleNode, observer: MockUmwelt
    ) -> None:
        """Defer schedules action at specific time."""
        future_time = datetime.now() + timedelta(hours=1)
        result = await schedule_node.invoke(
            "defer",
            as_umwelt(observer),
            path="world.task.execute",
            at=future_time,
        )
        assert "id" in result
        assert result["status"] == "scheduled"

    @pytest.mark.asyncio
    async def test_cancel(
        self, schedule_node: ScheduleNode, observer: MockUmwelt
    ) -> None:
        """Cancel removes scheduled action."""
        # First schedule
        defer_result = await schedule_node.invoke(
            "defer",
            as_umwelt(observer),
            path="world.task.execute",
            delay=60,
        )
        action_id = defer_result["id"]

        # Then cancel
        cancel_result = await schedule_node.invoke(
            "cancel",
            as_umwelt(observer),
            id=action_id,
        )
        assert cancel_result["status"] == "cancelled"

    @pytest.mark.asyncio
    async def test_list(
        self, schedule_node: ScheduleNode, observer: MockUmwelt
    ) -> None:
        """List returns scheduled actions."""
        # Schedule some actions
        await schedule_node.invoke("defer", as_umwelt(observer), path="task1", delay=60)
        await schedule_node.invoke(
            "defer", as_umwelt(observer), path="task2", delay=120
        )

        result = await schedule_node.invoke("list", as_umwelt(observer))
        assert result["count"] == 2


class TestFutureNode:
    """Tests for FutureNode."""

    @pytest.fixture
    def future_node(self) -> FutureNode:
        return FutureNode()

    @pytest.fixture
    def observer(self) -> MockUmwelt:
        return MockUmwelt(archetype="default")

    @pytest.mark.asyncio
    async def test_forecast(
        self, future_node: FutureNode, observer: MockUmwelt
    ) -> None:
        """Forecast returns probabilistic prediction."""
        result = await future_node.invoke(
            "forecast",
            as_umwelt(observer),
            target="market",
            horizon="1d",
        )
        assert "forecast" in result
        assert "scenarios" in result["forecast"]

    @pytest.mark.asyncio
    async def test_simulate(
        self, future_node: FutureNode, observer: MockUmwelt
    ) -> None:
        """Simulate returns simulation steps."""
        result = await future_node.invoke(
            "simulate",
            as_umwelt(observer),
            target="process",
            steps=5,
        )
        assert "simulation" in result
        assert len(result["simulation"]) == 5


class TestTimeContextResolver:
    """Tests for TimeContextResolver."""

    @pytest.fixture
    def resolver(self) -> TimeContextResolver:
        return create_time_resolver()

    def test_resolve_trace(self, resolver: WorldContextResolver) -> None:
        """Resolves time.trace."""
        node = resolver.resolve("trace", [])
        assert isinstance(node, TraceNode)

    def test_resolve_past(self, resolver: WorldContextResolver) -> None:
        """Resolves time.past."""
        node = resolver.resolve("past", [])
        assert isinstance(node, PastNode)

    def test_resolve_future(self, resolver: WorldContextResolver) -> None:
        """Resolves time.future."""
        node = resolver.resolve("future", [])
        assert isinstance(node, FutureNode)

    def test_resolve_schedule(self, resolver: WorldContextResolver) -> None:
        """Resolves time.schedule."""
        node = resolver.resolve("schedule", [])
        assert isinstance(node, ScheduleNode)


# ============================================================
# INTEGRATION WITH LOGOS TESTS
# ============================================================


class TestLogosContextIntegration:
    """Test context resolvers integrated with Logos."""

    @pytest.fixture
    def logos(self) -> Logos:
        from ..logos import create_logos

        return create_logos()

    @pytest.fixture
    def observer(self) -> MockUmwelt:
        return MockUmwelt(archetype="default")

    def test_logos_has_five_resolvers(self, logos: Logos) -> None:
        """Logos initializes with five context resolvers."""
        assert len(logos._context_resolvers) == 5
        assert "world" in logos._context_resolvers
        assert "self" in logos._context_resolvers
        assert "concept" in logos._context_resolvers
        assert "void" in logos._context_resolvers
        assert "time" in logos._context_resolvers

    def test_resolve_world_path(self, logos: Logos) -> None:
        """Logos resolves world.* paths."""
        node = logos.resolve("world.house")
        assert node.handle == "world.house"

    def test_resolve_self_path(self, logos: Logos) -> None:
        """Logos resolves self.* paths."""
        node = logos.resolve("self.memory")
        assert node.handle == "self.memory"

    def test_resolve_concept_path(self, logos: Logos) -> None:
        """Logos resolves concept.* paths."""
        node = logos.resolve("concept.justice")
        assert node.handle == "concept.justice"

    def test_resolve_void_path(self, logos: Logos) -> None:
        """Logos resolves void.* paths."""
        node = logos.resolve("void.entropy")
        assert node.handle == "void.entropy"

    def test_resolve_time_path(self, logos: Logos) -> None:
        """Logos resolves time.* paths."""
        node = logos.resolve("time.trace")
        assert node.handle == "time.trace"

    @pytest.mark.asyncio
    async def test_invoke_world_manifest(
        self, logos: Logos, observer: MockUmwelt
    ) -> None:
        """Invoke world.*.manifest through Logos."""
        result = await logos.invoke("world.house.manifest", as_umwelt(observer))
        assert result is not None

    @pytest.mark.asyncio
    async def test_invoke_void_sip(self, logos: Logos, observer: MockUmwelt) -> None:
        """Invoke void.entropy.sip through Logos."""
        result = await logos.invoke("void.entropy.sip", as_umwelt(observer), amount=1.0)
        assert "seed" in result
