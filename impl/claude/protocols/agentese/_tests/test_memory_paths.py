"""
Tests for self.memory.* AGENTESE paths.

Tests the memory subsystem operations:
- crystallize: Create StateCrystal checkpoint
- resume: Restore from StateCrystal
- cherish: Pin crystal from reaping
- engram: Persist to Ghost cache

These operations wire the memory module to Crystal + Ghost infrastructure.
"""

from __future__ import annotations

import json
import tempfile
from collections.abc import Generator
from datetime import timedelta
from pathlib import Path
from typing import TYPE_CHECKING, Any, cast

import pytest
from agents.d.context_window import ContextWindow, TurnRole
from agents.d.crystal import (
    CrystallizationEngine,
    CrystalReaper,
    StateCrystal,
    TaskState,
    TaskStatus,
)
from agents.d.linearity import ResourceClass

from ..contexts.self_ import (
    SELF_AFFORDANCES,
    MemoryNode,
    SelfContextResolver,
    create_self_resolver,
)
from .conftest import MockUmwelt

if TYPE_CHECKING:
    from bootstrap.umwelt import Umwelt


def _cast_observer(mock: MockUmwelt) -> "Umwelt[Any, Any]":
    """Cast MockUmwelt to Umwelt for type checker satisfaction."""
    return cast("Umwelt[Any, Any]", mock)


# =============================================================================
# Test Fixtures
# =============================================================================


@pytest.fixture
def temp_storage() -> Generator[Path, None, None]:
    """Create a temporary storage path."""
    with tempfile.TemporaryDirectory() as tmpdir:
        yield Path(tmpdir)


@pytest.fixture
def crystal_reaper(temp_storage: Path) -> CrystalReaper:
    """Create a CrystalReaper with temp storage."""
    return CrystalReaper(storage_path=temp_storage / "crystals")


@pytest.fixture
def crystallization_engine(
    crystal_reaper: CrystalReaper, temp_storage: Path
) -> CrystallizationEngine:
    """Create a CrystallizationEngine."""
    return CrystallizationEngine(
        reaper=crystal_reaper,
        storage_path=temp_storage / "crystals",
    )


@pytest.fixture
def ghost_path(temp_storage: Path) -> Path:
    """Create a temporary Ghost cache path."""
    path = temp_storage / "ghost"
    path.mkdir(parents=True, exist_ok=True)
    return path


@pytest.fixture
def memory_node(
    crystallization_engine: CrystallizationEngine, ghost_path: Path
) -> MemoryNode:
    """Create a MemoryNode with crystal engine and ghost path."""
    return MemoryNode(
        _crystallization_engine=crystallization_engine,
        _ghost_path=ghost_path,
    )


@pytest.fixture
def self_resolver(
    crystallization_engine: CrystallizationEngine, ghost_path: Path
) -> SelfContextResolver:
    """Create a SelfContextResolver with integrations."""
    return create_self_resolver(
        crystallization_engine=crystallization_engine,
        ghost_path=ghost_path,
    )


@pytest.fixture
def mock_observer() -> "Umwelt[Any, Any]":
    """Create a mock observer (cast to Umwelt for type compatibility)."""
    return _cast_observer(MockUmwelt())


@pytest.fixture
def sample_context_window() -> ContextWindow:
    """Create a sample ContextWindow for testing."""
    window = ContextWindow(max_tokens=10000)

    # Add some turns
    window.append(TurnRole.SYSTEM, "System initialization")
    window.append(TurnRole.USER, "What is the weather?")
    window.append(TurnRole.ASSISTANT, "I don't have access to weather data.")

    # Mark one as PRESERVED
    preserved_turn = window.append(TurnRole.USER, "Remember this important fact!")
    window.promote_turn(preserved_turn, ResourceClass.PRESERVED, "user flagged")

    return window


# =============================================================================
# Affordances Tests
# =============================================================================


class TestMemoryAffordances:
    """Test that memory affordances include crystal and ghost operations."""

    def test_crystallize_in_affordances(self) -> None:
        """crystallize is in memory affordances."""
        assert "crystallize" in SELF_AFFORDANCES["memory"]

    def test_resume_in_affordances(self) -> None:
        """resume is in memory affordances."""
        assert "resume" in SELF_AFFORDANCES["memory"]

    def test_cherish_in_affordances(self) -> None:
        """cherish is in memory affordances."""
        assert "cherish" in SELF_AFFORDANCES["memory"]

    def test_engram_in_affordances(self) -> None:
        """engram is in memory affordances."""
        assert "engram" in SELF_AFFORDANCES["memory"]


# =============================================================================
# Crystallize Tests
# =============================================================================


class TestCrystallize:
    """Tests for self.memory.crystallize."""

    @pytest.mark.asyncio
    async def test_crystallize_requires_engine(
        self, mock_observer: "Umwelt[Any, Any]"
    ) -> None:
        """crystallize fails gracefully without engine."""
        node = MemoryNode()  # No engine configured
        result = await node._invoke_aspect("crystallize", mock_observer)

        assert "error" in result
        assert "CrystallizationEngine not configured" in result["error"]

    @pytest.mark.asyncio
    async def test_crystallize_requires_context_window(
        self,
        memory_node: MemoryNode,
        mock_observer: "Umwelt[Any, Any]",
    ) -> None:
        """crystallize requires context_window parameter."""
        result = await memory_node._invoke_aspect("crystallize", mock_observer)

        assert "error" in result
        assert "context_window required" in result["error"]

    @pytest.mark.asyncio
    async def test_crystallize_creates_crystal(
        self,
        memory_node: MemoryNode,
        mock_observer: "Umwelt[Any, Any]",
        sample_context_window: ContextWindow,
    ) -> None:
        """crystallize creates a StateCrystal."""
        result = await memory_node._invoke_aspect(
            "crystallize",
            mock_observer,
            context_window=sample_context_window,
            task_id="test-task-123",
            task_description="Test crystallization",
        )

        assert result["status"] == "crystallized"
        assert "crystal_id" in result
        assert result["crystal_id"].startswith("crystal_")
        assert result["preserved_count"] >= 1  # We marked one as PRESERVED
        assert result["pinned"] is False

    @pytest.mark.asyncio
    async def test_crystallize_with_working_memory(
        self,
        memory_node: MemoryNode,
        mock_observer: "Umwelt[Any, Any]",
        sample_context_window: ContextWindow,
    ) -> None:
        """crystallize preserves working memory."""
        working_memory = {"key1": "value1", "counter": 42}

        result = await memory_node._invoke_aspect(
            "crystallize",
            mock_observer,
            context_window=sample_context_window,
            task_id="test-task",
            task_description="Test with memory",
            working_memory=working_memory,
        )

        assert result["status"] == "crystallized"

    @pytest.mark.asyncio
    async def test_crystallize_with_custom_ttl(
        self,
        memory_node: MemoryNode,
        mock_observer: "Umwelt[Any, Any]",
        sample_context_window: ContextWindow,
    ) -> None:
        """crystallize respects custom TTL."""
        result = await memory_node._invoke_aspect(
            "crystallize",
            mock_observer,
            context_window=sample_context_window,
            task_id="test-task",
            task_description="Short-lived crystal",
            ttl_hours=1,  # 1 hour TTL
        )

        assert result["status"] == "crystallized"
        assert "expires_at" in result


# =============================================================================
# Resume Tests
# =============================================================================


class TestResume:
    """Tests for self.memory.resume."""

    @pytest.mark.asyncio
    async def test_resume_requires_engine(
        self, mock_observer: "Umwelt[Any, Any]"
    ) -> None:
        """resume fails gracefully without engine."""
        node = MemoryNode()
        result = await node._invoke_aspect("resume", mock_observer, crystal_id="test")

        assert "error" in result
        assert "CrystallizationEngine not configured" in result["error"]

    @pytest.mark.asyncio
    async def test_resume_requires_crystal_id(
        self,
        memory_node: MemoryNode,
        mock_observer: "Umwelt[Any, Any]",
    ) -> None:
        """resume requires crystal_id parameter."""
        result = await memory_node._invoke_aspect("resume", mock_observer)

        assert "error" in result
        assert "crystal_id required" in result["error"]

    @pytest.mark.asyncio
    async def test_resume_not_found(
        self,
        memory_node: MemoryNode,
        mock_observer: "Umwelt[Any, Any]",
    ) -> None:
        """resume returns error for non-existent crystal."""
        result = await memory_node._invoke_aspect(
            "resume",
            mock_observer,
            crystal_id="nonexistent_crystal",
        )

        assert "error" in result
        assert "not found" in result["error"].lower()

    @pytest.mark.asyncio
    async def test_resume_restores_crystal(
        self,
        memory_node: MemoryNode,
        mock_observer: "Umwelt[Any, Any]",
        sample_context_window: ContextWindow,
    ) -> None:
        """resume restores from a crystallized state."""
        # First crystallize
        crystallize_result = await memory_node._invoke_aspect(
            "crystallize",
            mock_observer,
            context_window=sample_context_window,
            task_id="resumable-task",
            task_description="Test resumption",
            working_memory={"state": "paused"},
        )
        crystal_id = crystallize_result["crystal_id"]

        # Then resume
        resume_result = await memory_node._invoke_aspect(
            "resume",
            mock_observer,
            crystal_id=crystal_id,
        )

        assert resume_result["status"] == "resumed"
        assert resume_result["crystal_id"] == crystal_id
        assert resume_result["task_id"] == "resumable-task"
        assert resume_result["task_description"] == "Test resumption"
        assert resume_result["working_memory"] == {"state": "paused"}
        assert resume_result["restored_fragments"] >= 1


# =============================================================================
# Cherish Tests
# =============================================================================


class TestCherish:
    """Tests for self.memory.cherish."""

    @pytest.mark.asyncio
    async def test_cherish_requires_engine(
        self, mock_observer: "Umwelt[Any, Any]"
    ) -> None:
        """cherish fails gracefully without engine."""
        node = MemoryNode()
        result = await node._invoke_aspect("cherish", mock_observer, crystal_id="test")

        assert "error" in result
        assert "CrystallizationEngine not configured" in result["error"]

    @pytest.mark.asyncio
    async def test_cherish_requires_crystal_id(
        self,
        memory_node: MemoryNode,
        mock_observer: "Umwelt[Any, Any]",
    ) -> None:
        """cherish requires crystal_id parameter."""
        result = await memory_node._invoke_aspect("cherish", mock_observer)

        assert "error" in result
        assert "crystal_id required" in result["error"]

    @pytest.mark.asyncio
    async def test_cherish_pins_crystal(
        self,
        memory_node: MemoryNode,
        mock_observer: "Umwelt[Any, Any]",
        sample_context_window: ContextWindow,
    ) -> None:
        """cherish pins a crystal from reaping."""
        # Create a crystal
        crystallize_result = await memory_node._invoke_aspect(
            "crystallize",
            mock_observer,
            context_window=sample_context_window,
            task_id="precious-task",
            task_description="Important work",
        )
        crystal_id = crystallize_result["crystal_id"]

        # Cherish it
        cherish_result = await memory_node._invoke_aspect(
            "cherish",
            mock_observer,
            crystal_id=crystal_id,
        )

        assert cherish_result["status"] == "cherished"
        assert cherish_result["crystal_id"] == crystal_id
        assert cherish_result["pinned"] is True

    @pytest.mark.asyncio
    async def test_uncherish_unpins_crystal(
        self,
        memory_node: MemoryNode,
        mock_observer: "Umwelt[Any, Any]",
        sample_context_window: ContextWindow,
    ) -> None:
        """uncherish unpins a crystal."""
        # Create and cherish
        crystallize_result = await memory_node._invoke_aspect(
            "crystallize",
            mock_observer,
            context_window=sample_context_window,
            task_id="temp-task",
            task_description="Temporary",
        )
        crystal_id = crystallize_result["crystal_id"]

        await memory_node._invoke_aspect(
            "cherish", mock_observer, crystal_id=crystal_id
        )

        # Uncherish
        uncherish_result = await memory_node._invoke_aspect(
            "cherish",
            mock_observer,
            crystal_id=crystal_id,
            uncherish=True,
        )

        assert uncherish_result["status"] == "uncherished"
        assert uncherish_result["pinned"] is False


# =============================================================================
# Engram Tests
# =============================================================================


class TestEngram:
    """Tests for self.memory.engram (Ghost cache)."""

    @pytest.mark.asyncio
    async def test_engram_requires_key(
        self,
        memory_node: MemoryNode,
        mock_observer: "Umwelt[Any, Any]",
    ) -> None:
        """engram requires key parameter."""
        result = await memory_node._invoke_aspect(
            "engram",
            mock_observer,
            data={"test": "data"},
        )

        assert "error" in result
        assert "key required" in result["error"]

    @pytest.mark.asyncio
    async def test_engram_requires_data(
        self,
        memory_node: MemoryNode,
        mock_observer: "Umwelt[Any, Any]",
    ) -> None:
        """engram requires data parameter."""
        result = await memory_node._invoke_aspect(
            "engram",
            mock_observer,
            key="test_key",
        )

        assert "error" in result
        assert "data required" in result["error"]

    @pytest.mark.asyncio
    async def test_engram_persists_data(
        self,
        memory_node: MemoryNode,
        mock_observer: "Umwelt[Any, Any]",
        ghost_path: Path,
    ) -> None:
        """engram persists data to Ghost cache."""
        test_data = {"status": "active", "count": 42}

        result = await memory_node._invoke_aspect(
            "engram",
            mock_observer,
            key="status",
            data=test_data,
        )

        assert result["status"] == "engrammed"
        assert result["key"] == "status"

        # Verify file exists
        engram_file = ghost_path / "status.json"
        assert engram_file.exists()

        # Verify content
        content = json.loads(engram_file.read_text())
        assert content["key"] == "status"
        assert content["data"] == test_data
        assert "timestamp" in content

    @pytest.mark.asyncio
    async def test_engram_with_subdirectory(
        self,
        memory_node: MemoryNode,
        mock_observer: "Umwelt[Any, Any]",
        ghost_path: Path,
    ) -> None:
        """engram supports subdirectories."""
        result = await memory_node._invoke_aspect(
            "engram",
            mock_observer,
            key="agent_state",
            data={"name": "test_agent"},
            subdirectory="agents",
        )

        assert result["status"] == "engrammed"

        # Verify file in subdirectory
        engram_file = ghost_path / "agents" / "agent_state.json"
        assert engram_file.exists()


# =============================================================================
# Integration Tests
# =============================================================================


class TestMemoryIntegration:
    """Integration tests for memory operations."""

    @pytest.mark.asyncio
    async def test_full_crystallize_resume_cycle(
        self,
        memory_node: MemoryNode,
        mock_observer: "Umwelt[Any, Any]",
        sample_context_window: ContextWindow,
    ) -> None:
        """Full cycle: crystallize → cherish → resume."""
        # Crystallize with state
        working_memory = {"counter": 1, "mode": "active"}

        crystallize_result = await memory_node._invoke_aspect(
            "crystallize",
            mock_observer,
            context_window=sample_context_window,
            task_id="cycle-test",
            task_description="Full cycle test",
            working_memory=working_memory,
        )
        crystal_id = crystallize_result["crystal_id"]

        # Cherish
        await memory_node._invoke_aspect(
            "cherish", mock_observer, crystal_id=crystal_id
        )

        # Resume
        resume_result = await memory_node._invoke_aspect(
            "resume",
            mock_observer,
            crystal_id=crystal_id,
        )

        assert resume_result["status"] == "resumed"
        assert resume_result["working_memory"] == working_memory

    @pytest.mark.asyncio
    async def test_resolver_wires_memory_correctly(
        self,
        self_resolver: SelfContextResolver,
        mock_observer: "Umwelt[Any, Any]",
        sample_context_window: ContextWindow,
    ) -> None:
        """SelfContextResolver correctly wires memory node."""
        # Get memory node from resolver
        resolved_node = self_resolver.resolve("memory", [])
        # Cast to MemoryNode to access private attributes
        memory_node = cast(MemoryNode, resolved_node)

        # Verify it has crystal engine
        assert memory_node._crystallization_engine is not None

        # Verify crystallize works
        result = await memory_node._invoke_aspect(
            "crystallize",
            mock_observer,
            context_window=sample_context_window,
            task_id="resolver-test",
            task_description="Test via resolver",
        )
        assert result["status"] == "crystallized"
