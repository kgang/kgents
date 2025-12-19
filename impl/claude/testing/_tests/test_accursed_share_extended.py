"""
Extended Accursed Share: Per-agent chaos tests.

Philosophy: Every agent genus gets chaotic exploration.
We cherish and express gratitude for slop.

Phase 6 of test evolution plan: Expand chaos tests to 50.
"""

from __future__ import annotations

import asyncio
import random
from dataclasses import dataclass
from typing import Any, cast

import pytest

# =============================================================================
# D-gent Chaos Tests
# =============================================================================


@pytest.mark.accursed_share
class TestDGentChaos:
    """Chaos tests for D-gent (Data agents)."""

    @pytest.mark.asyncio
    async def test_rapid_state_updates(self) -> None:
        """Rapid state updates."""
        from typing import Any

        from agents.d import VolatileAgent

        # VolatileAgent uses _state for storage
        store: VolatileAgent[dict[str, Any]] = VolatileAgent(_state={})

        for _ in range(100):
            key = f"key_{random.randint(0, 10)}"
            current = await store.load()
            if random.random() > 0.5:
                current[key] = random.randint(0, 1000)
            else:
                current.pop(key, None)
            await store.save(current)

        # Just verify no crashes
        final = await store.load()
        print(f"D-gent churn: {len(final)} keys surviving")

    @pytest.mark.asyncio
    async def test_large_value_storage(self) -> None:
        """Store very large values."""
        from agents.d import VolatileAgent

        # 1MB string
        large_value = "x" * (1024 * 1024)
        store: VolatileAgent[str] = VolatileAgent(_state=large_value)

        retrieved = await store.load()
        assert len(retrieved) == len(large_value)
        print(f"D-gent large: Stored and retrieved {len(large_value)} bytes")

    @pytest.mark.asyncio
    async def test_concurrent_reads_writes(self) -> None:
        """Concurrent reads and writes to same store."""
        from typing import Any

        from agents.d import VolatileAgent

        store: VolatileAgent[dict[str, Any]] = VolatileAgent(_state={})

        async def writer() -> None:
            for i in range(50):
                current = await store.load()
                current[f"key_{i % 10}"] = i
                await store.save(current)
                await asyncio.sleep(0.001)

        async def reader() -> list[Any]:
            results = []
            for _ in range(50):
                try:
                    current = await store.load()
                    key = f"key_{random.randint(0, 9)}"
                    if key in current:
                        results.append(current[key])
                except Exception:
                    pass  # Key might not exist yet
                await asyncio.sleep(0.001)
            return results

        # Run concurrently
        await asyncio.gather(writer(), reader(), reader())
        print("D-gent concurrent: No deadlocks detected")

    @pytest.mark.asyncio
    async def test_nested_dict_storage(self) -> None:
        """Store deeply nested dictionaries."""
        from agents.d import VolatileAgent

        # Create deeply nested structure
        def nest(depth: int) -> dict[str, Any]:
            if depth == 0:
                return {"leaf": random.random()}
            return {"level": depth, "child": nest(depth - 1)}

        nested = nest(50)
        store: VolatileAgent[dict[str, Any]] = VolatileAgent(_state=nested)

        retrieved = await store.load()
        assert retrieved["level"] == 50
        print("D-gent nested: 50-level nested structure handled")


# =============================================================================
# L-gent Chaos Tests
# =============================================================================


@pytest.mark.accursed_share
class TestLGentChaos:
    """Chaos tests for L-gent (Lattice/embeddings)."""

    @pytest.mark.asyncio
    async def test_near_duplicate_embeddings(self) -> None:
        """Store many near-identical embeddings."""
        from agents.l import CatalogEntry, EntityType, SemanticRegistry

        registry = SemanticRegistry()

        for i in range(100):
            entry = CatalogEntry(
                id=f"near_{i}",
                name=f"Near Duplicate {i}",
                entity_type=EntityType.AGENT,
                version="1.0.0",
                description=f"Near duplicate entry {i}",
            )
            await registry.register(entry)

        # Search should find entries
        await registry.fit()  # Build semantic index
        results = await registry.find_semantic("near duplicate", limit=50)
        print(f"L-gent near-dupes: Found {len(results)} results")

    @pytest.mark.asyncio
    async def test_unicode_entity_names(self) -> None:
        """Register entities with unicode names."""
        from agents.l import CatalogEntry, EntityType, SemanticRegistry

        registry = SemanticRegistry()

        names = [
            "普通话测试",  # Chinese
            "日本語テスト",  # Japanese
            "한국어 테스트",  # Korean
            "тест на русском",  # Russian
            "اختبار بالعربية",  # Arabic
            "🚀🔥💯",  # Emoji
        ]

        for i, name in enumerate(names):
            entry = CatalogEntry(
                id=f"unicode_{i}",
                name=name,
                entity_type=EntityType.AGENT,
                version="1.0.0",
                description=f"Unicode test: {name}",
            )
            await registry.register(entry)

        # Verify all registered
        entries = registry.catalog.entries
        assert len(entries) == len(names)
        print(f"L-gent unicode: Registered {len(names)} unicode names")

    @pytest.mark.asyncio
    async def test_empty_and_whitespace_queries(self) -> None:
        """Test handling of edge-case queries."""
        from agents.l import CatalogEntry, EntityType, SemanticRegistry

        registry = SemanticRegistry()

        # Register something first
        entry = CatalogEntry(
            id="test_1",
            name="Test Entity",
            entity_type=EntityType.AGENT,
            version="1.0.0",
            description="Test entity for chaos testing",
        )
        await registry.register(entry)

        edge_cases = ["", "   ", "\n\t", "\x00", "a" * 10000]

        await registry.fit()  # Build semantic index
        for query in edge_cases:
            try:
                results = await registry.find_semantic(query, limit=10)
                print(f"L-gent edge: Query '{query[:20]!r}' returned {len(results)} results")
            except Exception as e:
                print(f"L-gent edge: Query '{query[:20]!r}' raised {type(e).__name__}")


# =============================================================================
# N-gent Chaos Tests
# =============================================================================


@pytest.mark.accursed_share
class TestNGentChaos:
    """Chaos tests for N-gent (Narrative)."""

    @pytest.mark.asyncio
    async def test_rapid_event_stream(self) -> None:
        """Emit many events rapidly."""
        import hashlib
        import uuid
        from datetime import datetime, timezone

        from agents.n import MemoryCrystalStore, SemanticTrace

        store = MemoryCrystalStore()

        for i in range(1000):
            inputs = {"index": i, "random": random.random()}
            input_bytes = str(inputs).encode()
            trace = SemanticTrace(
                trace_id=str(uuid.uuid4()),
                parent_id=None,
                timestamp=datetime.now(timezone.utc),
                agent_id="chaos_agent",
                agent_genus="X",
                action="CHAOS",
                inputs=inputs,
                outputs={"result": i * 2},
                input_hash=hashlib.sha256(input_bytes).hexdigest(),
                input_snapshot=input_bytes,
                output_hash=None,
                gas_consumed=100,
                duration_ms=int(random.uniform(1, 100)),
            )
            store.store(trace)  # Sync method

        # Use count() instead of stats()
        count = store.count()
        print(f"N-gent rapid: Stored {count} traces")

    @pytest.mark.asyncio
    async def test_large_trace_data(self) -> None:
        """Store traces with large payloads."""
        import hashlib
        import uuid
        from datetime import datetime, timezone

        from agents.n import MemoryCrystalStore, SemanticTrace

        store = MemoryCrystalStore()

        large_input = {"data": "x" * 100000}  # 100KB payload
        input_bytes = str(large_input).encode()
        trace = SemanticTrace(
            trace_id=str(uuid.uuid4()),
            parent_id=None,
            timestamp=datetime.now(timezone.utc),
            agent_id="large_payload",
            agent_genus="X",
            action="LARGE",
            inputs=large_input,
            outputs={"echo": len(large_input["data"])},
            input_hash=hashlib.sha256(input_bytes).hexdigest(),
            input_snapshot=input_bytes,
            output_hash=None,
            gas_consumed=100,
            duration_ms=1,
        )
        store.store(trace)  # Sync method

        retrieved = store.get(trace.trace_id)  # Sync method
        assert retrieved is not None
        assert len(retrieved.inputs["data"]) == 100000
        print("N-gent large: 100KB trace stored and retrieved")


# =============================================================================
# Cross-Agent Chaos Tests
# =============================================================================


@pytest.mark.accursed_share
class TestCrossAgentChaos:
    """Chaos tests spanning multiple agent types."""

    @pytest.mark.asyncio
    async def test_d_to_l_pipeline(self) -> None:
        """Data flows from D-gent to L-gent."""
        from typing import Any

        from agents.d import VolatileAgent
        from agents.l import CatalogEntry, EntityType, SemanticRegistry

        store: VolatileAgent[dict[str, Any]] = VolatileAgent(_state={})
        registry = SemanticRegistry()

        # Store data in D-gent, register in L-gent
        for i in range(50):
            data = {"value": random.random(), "index": i}
            current = await store.load()
            current[f"item_{i}"] = data
            await store.save(current)

            entry = CatalogEntry(
                id=f"item_{i}",
                name=f"Data Item {i}",
                entity_type=EntityType.AGENT,
                version="1.0.0",
                description=f"Data item {i} with value {data['value']:.2f}",
            )
            await registry.register(entry)

        # Search L-gent
        await registry.fit()  # Build semantic index
        results = await registry.find_semantic("data item", limit=10)
        print(f"D→L pipeline: {len(results)} results from cross-agent query")

    @pytest.mark.asyncio
    async def test_concurrent_multi_agent(self) -> None:
        """Concurrent operations across multiple D-gent instances."""
        from typing import Any

        from agents.d import VolatileAgent

        stores = [VolatileAgent[dict[str, Any]](_state={}) for _ in range(5)]

        async def writer(store: Any, n: int) -> None:
            for i in range(n):
                current = await store.load()
                current[f"key_{i}"] = i
                await store.save(current)
                await asyncio.sleep(0.001)

        await asyncio.gather(*[writer(s, 100) for s in stores])

        total_keys = 0
        for s in stores:
            state = await s.load()
            total_keys += len(state)
        print(f"Concurrent multi-agent: {total_keys} total keys across {len(stores)} stores")
        assert total_keys == 500  # 5 stores * 100 keys

    @pytest.mark.asyncio
    async def test_composition_with_stateful_agents(self) -> None:
        """Compose stateful D-gents with pure transforms."""
        from agents.d import Symbiont, VolatileAgent
        from agents.poly import compose

        # Create a counter symbiont
        def counter_logic(inc: int, count: int) -> tuple[int, int]:
            new_count = count + inc
            return new_count, new_count

        memory: VolatileAgent[int] = VolatileAgent(_state=0)
        counter = Symbiont(logic=counter_logic, memory=memory)

        # Pure transform agent
        @dataclass
        class Double:
            name: str = "Double"

            async def invoke(self, x: int) -> int:
                return x * 2

        composed: Any = compose(cast(Any, counter), cast(Any, Double()))

        # Invoke several times
        results = []
        for i in range(1, 6):
            result = await composed.invoke(i)
            results.append(result)

        # Counter: 1, 3, 6, 10, 15
        # Doubled: 2, 6, 12, 20, 30
        print(f"Stateful composition: {results}")


# =============================================================================
# Composition Boundary Chaos
# =============================================================================


@pytest.mark.accursed_share
class TestCompositionBoundaryChaos:
    """Chaos tests for composition edge cases."""

    @pytest.mark.asyncio
    async def test_type_coercion_pipeline(self) -> None:
        """Pipeline with aggressive type coercions."""
        from typing import Any

        from agents.poly import compose

        @dataclass
        class IntToStr:
            name: str = "IntToStr"

            async def invoke(self, x: int) -> str:
                return str(x)

        @dataclass
        class StrToList:
            name: str = "StrToList"

            async def invoke(self, x: str) -> list[str]:
                return list(x)

        @dataclass
        class ListToDict:
            name: str = "ListToDict"

            async def invoke(self, x: list[str]) -> dict[str, str]:
                return {str(i): v for i, v in enumerate(x)}

        @dataclass
        class DictToTuple:
            name: str = "DictToTuple"

            async def invoke(self, x: dict[str, str]) -> tuple[tuple[str, str], ...]:
                return tuple(x.items())

        pipeline: Any = compose(
            compose(
                compose(cast(Any, IntToStr()), cast(Any, StrToList())),
                cast(Any, ListToDict()),
            ),
            cast(Any, DictToTuple()),
        )

        result = await pipeline.invoke(12345)
        print(f"Type coercion pipeline: 12345 -> {result}")

    @pytest.mark.asyncio
    async def test_exception_in_middle_of_chain(self) -> None:
        """Exception handling in the middle of a chain."""
        from agents.poly import compose

        @dataclass
        class Safe:
            name: str = "Safe"

            async def invoke(self, x: int) -> int:
                return x + 1

        @dataclass
        class Risky:
            name: str = "Risky"

            async def invoke(self, x: int) -> int:
                if x == 5:
                    raise ValueError("Don't like 5")
                return x * 2

        chain: Any = compose(cast(Any, Safe()), cast(Any, Risky()))

        # Should work for most inputs
        for i in range(10):
            if i == 4:  # 4 + 1 = 5, which Risky doesn't like
                with pytest.raises(ValueError):
                    await chain.invoke(i)
            else:
                result = await chain.invoke(i)
                print(f"Chain({i}) = {result}")

    @pytest.mark.asyncio
    async def test_none_propagation(self) -> None:
        """How None propagates through composition."""
        from agents.poly import compose

        @dataclass
        class MaybeReturn:
            name: str = "MaybeReturn"

            async def invoke(self, x: int) -> int | None:
                if x % 2 == 0:
                    return None
                return x * 2

        @dataclass
        class HandleNone:
            name: str = "HandleNone"

            async def invoke(self, x: int | None) -> str:
                if x is None:
                    return "got_none"
                return f"got_{x}"

        chain: Any = compose(cast(Any, MaybeReturn()), cast(Any, HandleNone()))

        results = [await chain.invoke(i) for i in range(6)]
        print(f"None propagation: {results}")


# =============================================================================
# Memory Pressure Chaos
# =============================================================================


@pytest.mark.accursed_share
@pytest.mark.slow
class TestMemoryPressureChaos:
    """Chaos tests for memory pressure scenarios."""

    @pytest.mark.asyncio
    async def test_many_small_agents(self) -> None:
        """Create many small agent instances."""
        from agents.d import VolatileAgent

        agents = []
        for i in range(1000):
            agent: VolatileAgent[int] = VolatileAgent(_state=i)
            agents.append(agent)

        # Verify they all work
        sample = random.sample(agents, 10)
        for agent in sample:
            val = await agent.load()
            assert val is not None

        print(f"Memory pressure: Created {len(agents)} agents")

    @pytest.mark.asyncio
    async def test_long_chain_composition(self) -> None:
        """Very long composition chains."""
        from functools import reduce

        from agents.poly import compose

        @dataclass
        class Increment:
            name: str = "Inc"

            async def invoke(self, x: int) -> int:
                return x + 1

        # Chain 500 increment agents
        agents = [Increment() for _ in range(500)]
        chain = reduce(lambda a, b: compose(a, b), agents)  # type: ignore[arg-type,return-value]

        result = await chain.invoke(0)
        assert result == 500
        print(f"Long chain: 500-deep composition returned {result}")


# Run with: pytest impl/claude/testing/_tests/test_accursed_share_extended.py -v -m accursed_share
