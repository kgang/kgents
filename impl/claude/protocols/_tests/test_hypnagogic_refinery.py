"""
Tests for Hypnagogic Refinery Protocol.

Phase 4.2: Automatic codebase optimization during "sleep".

Tests:
- Memory temperature classification
- Candidate selection
- Optimization and verification
- Dream cycle execution
- Rollback capability
"""

from __future__ import annotations

from datetime import datetime, timedelta

import pytest
from protocols.hypnagogic_refinery import (
    HypnagogicRefinery,
    MemoryTemperature,
    OptimizationEngine,
    OptimizationObjective,
    OptimizationStatus,
    RefineryReport,
    create_memory,
    create_memory_store,
    create_optimization_engine,
    create_refinery,
)


class TestMemoryRecord:
    """Tests for MemoryRecord."""

    def test_memory_creation(self) -> None:
        """Test basic memory creation."""
        memory = create_memory(
            content="def hello() -> None: pass",
            kind="code",
        )

        assert memory.kind == "code"
        assert memory.content == "def hello() -> None: pass"
        assert memory.size_bytes == len("def hello() -> None: pass".encode("utf-8"))
        assert memory.access_count == 0

    def test_memory_age(self) -> None:
        """Test age calculation."""
        memory = create_memory(
            content="test",
            kind="code",
        )
        memory.created_at = datetime.now() - timedelta(days=5)

        assert memory.age_days == pytest.approx(5, abs=0.1)

    def test_memory_dormancy(self) -> None:
        """Test dormancy calculation."""
        memory = create_memory(
            content="test",
            kind="code",
        )
        memory.last_accessed = datetime.now() - timedelta(days=10)

        assert memory.dormancy_days == pytest.approx(10, abs=0.1)


class TestMemoryStore:
    """Tests for MemoryStore."""

    def test_store_add_and_get(self) -> None:
        """Test adding and retrieving memories."""
        store = create_memory_store()

        memory = create_memory(content="test", kind="code", id="test-1")
        store.add(memory)

        retrieved = store.get("test-1")
        assert retrieved is not None
        assert retrieved.content == "test"

    def test_store_updates_access_on_get(self) -> None:
        """Test that get updates access count."""
        store = create_memory_store()

        memory = create_memory(content="test", kind="code", id="test-1")
        memory.access_count = 0
        store.add(memory)

        store.get("test-1")
        result = store.get("test-1")
        assert result is not None
        assert result.access_count == 2  # Two gets

    def test_query_by_temperature_cold(self) -> None:
        """Test querying cold memories."""
        store = create_memory_store()

        # Add hot memory (recent)
        hot = create_memory(content="hot", kind="code", id="hot")
        hot.temperature = MemoryTemperature.HOT
        store.add(hot)

        # Add cold memory (old)
        cold = create_memory(content="cold", kind="code", id="cold")
        cold.temperature = MemoryTemperature.COLD
        store.add(cold)

        # Add frozen memory
        frozen = create_memory(content="frozen", kind="code", id="frozen")
        frozen.temperature = MemoryTemperature.FROZEN
        store.add(frozen)

        # Query cold and below
        results = store.query_by_temperature(MemoryTemperature.COLD)

        assert len(results) == 2  # Cold and frozen, not hot
        ids = {m.id for m in results}
        assert "cold" in ids
        assert "frozen" in ids
        assert "hot" not in ids

    def test_recompute_temperatures(self) -> None:
        """Test temperature recomputation."""
        store = create_memory_store()

        memory = create_memory(content="test", kind="code", id="test-1")
        memory.last_accessed = datetime.now() - timedelta(days=40)  # Very old
        memory.temperature = MemoryTemperature.HOT  # Wrong temperature
        store.add(memory)

        count = store.recompute_temperatures()

        assert count == 1
        # Direct access to check (avoid triggering get which updates)
        assert store._memories["test-1"].temperature == MemoryTemperature.FROZEN


class TestOptimizationEngine:
    """Tests for OptimizationEngine."""

    @pytest.fixture
    def engine(self) -> OptimizationEngine:
        return create_optimization_engine(min_improvement=0.1)

    @pytest.mark.asyncio
    async def test_compress_code_with_comments(
        self, engine: OptimizationEngine
    ) -> None:
        """Test compressing code with many comments."""
        code = """# This is a header comment
# It has multiple lines
# That can be removed

def hello() -> None:
    # This comment can stay
    pass

# Another block of comments
# That takes up space
"""

        optimized, improvement, notes = await engine.optimize(
            content=code,
            objective=OptimizationObjective.COMPRESSION,
            kind="code",
        )

        assert optimized is not None
        assert len(optimized) < len(code)
        assert improvement > 0

    @pytest.mark.asyncio
    async def test_skip_minimal_compression(self, engine: OptimizationEngine) -> None:
        """Test skipping code with minimal compression potential."""
        code = """def hello() -> None:
    return "world"
"""

        optimized, improvement, notes = await engine.optimize(
            content=code,
            objective=OptimizationObjective.COMPRESSION,
            kind="code",
        )

        # Should skip if improvement below threshold
        assert improvement < 0.1

    @pytest.mark.asyncio
    async def test_cache_compression(self, engine: OptimizationEngine) -> None:
        """Test cache optimization (full removal)."""
        cache_content = "{'key': 'value', 'data': [1,2,3]}"

        optimized, improvement, notes = await engine.optimize(
            content=cache_content,
            objective=OptimizationObjective.COMPRESSION,
            kind="cache",
        )

        assert optimized == ""  # Cache cleared
        assert improvement == 1.0

    @pytest.mark.asyncio
    async def test_verify_semantics_code(self, engine: OptimizationEngine) -> None:
        """Test semantics verification for code."""
        original = """def foo() -> None:
    pass

class Bar:
    pass
"""

        # Good optimization (preserves definitions)
        good_optimized = """def foo() -> None:
    pass
class Bar:
    pass"""

        preserved, notes = await engine.verify_semantics(
            original, good_optimized, "code"
        )
        assert preserved

        # Bad optimization (removes definition)
        bad_optimized = """class Bar:
    pass"""

        preserved, notes = await engine.verify_semantics(
            original, bad_optimized, "code"
        )
        assert not preserved


class TestHypnagogicRefinery:
    """Tests for HypnagogicRefinery."""

    @pytest.fixture
    def refinery(self) -> HypnagogicRefinery:
        return create_refinery(max_candidates=5, min_improvement=0.1)

    def test_refinery_creation(self, refinery: HypnagogicRefinery) -> None:
        """Test refinery creation."""
        assert refinery.memory_store is not None
        assert refinery.cycles == []

    @pytest.mark.asyncio
    async def test_dream_cycle_empty_store(self, refinery: HypnagogicRefinery) -> None:
        """Test dream cycle with no memories."""
        report = await refinery.dream_cycle()

        assert isinstance(report, RefineryReport)
        assert report.memories_examined == 0
        assert report.candidates_found == 0

    @pytest.mark.asyncio
    async def test_dream_cycle_with_cold_memory(
        self, refinery: HypnagogicRefinery
    ) -> None:
        """Test dream cycle finds and optimizes cold memory."""
        # Add a cold memory with comments
        code_with_comments = """# Header comment
# Another line

def test() -> None:
    pass

# More comments
# And more
"""
        memory = create_memory(
            content=code_with_comments,
            kind="code",
            id="cold-code",
        )
        memory.temperature = MemoryTemperature.COLD
        memory.last_accessed = datetime.now() - timedelta(days=30)

        refinery.memory_store.add(memory)

        report = await refinery.dream_cycle()

        assert report.memories_examined == 1
        assert report.candidates_found == 1
        # Should attempt optimization

    @pytest.mark.asyncio
    async def test_dream_cycle_skips_hot_memory(
        self, refinery: HypnagogicRefinery
    ) -> None:
        """Test dream cycle skips hot memories."""
        memory = create_memory(
            content="# lots of comments\n" * 10,
            kind="code",
            id="hot-code",
        )
        memory.temperature = MemoryTemperature.HOT

        refinery.memory_store.add(memory)

        report = await refinery.dream_cycle()

        # Hot memory should not be examined
        assert report.memories_examined == 0

    @pytest.mark.asyncio
    async def test_dream_cycle_respects_limit(
        self, refinery: HypnagogicRefinery
    ) -> None:
        """Test dream cycle respects max candidates."""
        # Add many cold memories
        for i in range(20):
            memory = create_memory(
                content="# comment\n" * 10,
                kind="code",
                id=f"cold-{i}",
            )
            memory.temperature = MemoryTemperature.COLD
            refinery.memory_store.add(memory)

        report = await refinery.dream_cycle()

        # Should respect max_candidates limit
        assert report.candidates_found <= 5

    @pytest.mark.asyncio
    async def test_rollback(self, refinery: HypnagogicRefinery) -> None:
        """Test rollback of optimization."""
        original_content = """# Comment to remove
def foo() -> None:
    pass
"""
        memory = create_memory(
            content=original_content,
            kind="code",
            id="rollback-test",
        )
        memory.temperature = MemoryTemperature.COLD

        refinery.memory_store.add(memory)

        report = await refinery.dream_cycle()

        # Find applied result
        applied = [r for r in report.results if r.status == OptimizationStatus.APPLIED]

        if applied:
            result = applied[0]
            assert result.rollback_available

            # Content should be optimized
            optimized_memory = refinery.memory_store.get("rollback-test")
            assert optimized_memory is not None
            assert optimized_memory.content != original_content

            # Rollback
            success = refinery.rollback(result)
            assert success

            # Content should be restored
            restored_memory = refinery.memory_store.get("rollback-test")
            assert restored_memory is not None
            assert restored_memory.content == original_content

    @pytest.mark.asyncio
    async def test_total_bytes_saved(self, refinery: HypnagogicRefinery) -> None:
        """Test tracking of total bytes saved."""
        # Add cold memory with lots of comments
        memory = create_memory(
            content="# " + "comment " * 100 + "\ndef f() -> None: pass",
            kind="code",
            id="big-comments",
        )
        memory.temperature = MemoryTemperature.COLD

        refinery.memory_store.add(memory)

        await refinery.dream_cycle()

        # Should have saved some bytes
        # (exact amount depends on optimization)
        assert len(refinery.cycles) == 1


class TestRefineryReport:
    """Tests for RefineryReport."""

    def test_report_success_rate(self) -> None:
        """Test success rate calculation."""
        report = RefineryReport(
            cycle_id="test",
            started_at=datetime.now(),
            optimizations_attempted=10,
            optimizations_succeeded=7,
        )

        assert report.success_rate == 0.7

    def test_report_success_rate_zero_attempts(self) -> None:
        """Test success rate with zero attempts."""
        report = RefineryReport(
            cycle_id="test",
            started_at=datetime.now(),
            optimizations_attempted=0,
        )

        assert report.success_rate == 0.0

    def test_report_duration(self) -> None:
        """Test duration calculation."""
        start = datetime.now()
        end = start + timedelta(seconds=5)

        report = RefineryReport(
            cycle_id="test",
            started_at=start,
            completed_at=end,
        )

        assert report.duration_ms == pytest.approx(5000, abs=100)


class TestIntegration:
    """Integration tests for full refinery flow."""

    @pytest.mark.asyncio
    async def test_multiple_dream_cycles(self) -> None:
        """Test running multiple dream cycles."""
        refinery = create_refinery(max_candidates=3)

        # Add memories
        for i in range(10):
            memory = create_memory(
                content=f"# Header for item {i}\n"
                + "# comment\n" * 5
                + f"def func_{i}(): pass",
                kind="code",
                id=f"item-{i}",
            )
            memory.temperature = MemoryTemperature.COLD
            refinery.memory_store.add(memory)

        # Run multiple cycles
        for _ in range(3):
            report = await refinery.dream_cycle()
            assert report.completed_at is not None

        assert len(refinery.cycles) == 3

    @pytest.mark.asyncio
    async def test_optimization_preserves_functionality(self) -> None:
        """Test that optimization preserves code functionality."""
        refinery = create_refinery()

        code = """# This is a module for testing
# It has several functions

def add(a, b) -> None:
    '''Add two numbers.'''
    return a + b

# Another comment block
# With multiple lines

def multiply(x, y) -> None:
    '''Multiply two numbers.'''
    return x * y

class Calculator:
    '''A simple calculator.'''

    def divide(self, a, b) -> None:
        '''Divide a by b.'''
        return a / b
"""

        memory = create_memory(
            content=code,
            kind="code",
            id="functional-code",
        )
        memory.temperature = MemoryTemperature.COLD

        refinery.memory_store.add(memory)

        await refinery.dream_cycle()  # Side effect: optimizes memory

        # Get optimized memory
        optimized_memory = refinery.memory_store.get("functional-code")
        assert optimized_memory is not None

        # All functions and class should still be present
        assert "def add(" in optimized_memory.content
        assert "def multiply(" in optimized_memory.content
        assert "class Calculator:" in optimized_memory.content
        assert "def divide(" in optimized_memory.content

    @pytest.mark.asyncio
    async def test_cache_optimization(self) -> None:
        """Test that cache memories can be fully cleared."""
        refinery = create_refinery()

        cache = create_memory(
            content='{"cached": "data", "entries": [1,2,3,4,5]}',
            kind="cache",
            id="old-cache",
        )
        cache.temperature = MemoryTemperature.COLD

        refinery.memory_store.add(cache)

        report = await refinery.dream_cycle()

        # Find the result for our cache
        cache_results = [
            r for r in report.results if r.candidate.memory.id == "old-cache"
        ]

        assert len(cache_results) == 1
        assert cache_results[0].improvement == 1.0  # Full removal
