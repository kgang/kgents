"""
Tests for Brain AGENTESE Node.

Verifies that BrainNode:
1. Registers with @node("self.memory")
2. Provides correct affordances by archetype
3. Routes aspects to BrainPersistence methods
4. Integrates with AGENTESE gateway
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any
from unittest.mock import AsyncMock, MagicMock

import pytest

from protocols.agentese.node import AgentMeta, Observer
from protocols.agentese.registry import get_registry, repopulate_registry, reset_registry

# === Fixtures ===


@pytest.fixture(autouse=True)
def clean_registry():
    """
    Reset registry before each test, repopulate after.

    CRITICAL for pytest-xdist: Without repopulation, tests on the same
    worker that run after this test will see an empty registry, breaking
    canary tests and any test that relies on global node registration.

    See: protocols/agentese/_tests/test_xdist_node_registry_canary.py
    """
    reset_registry()
    yield
    # Repopulate registry for subsequent tests on this worker
    # NOTE: repopulate_registry() scans sys.modules for @node classes
    # _import_node_modules() won't work because imports are cached
    repopulate_registry()


@pytest.fixture
def mock_persistence():
    """Create a mock BrainPersistence."""
    from services.brain import BrainStatus, CaptureResult, SearchResult

    persistence = MagicMock()

    # Mock manifest
    persistence.manifest = AsyncMock(
        return_value=BrainStatus(
            total_crystals=42,
            vector_count=10,
            has_semantic=True,
            coherency_rate=0.95,
            ghosts_healed=2,
            storage_path="~/.local/share/kgents/brain",
            storage_backend="sqlite",
        )
    )

    # Mock capture
    persistence.capture = AsyncMock(
        return_value=CaptureResult(
            crystal_id="crystal-abc123",
            content="Test content",
            summary="Test content...",
            captured_at="2025-01-01T00:00:00",
            has_embedding=True,
            storage="sqlite",
            datum_id="brain-crystal-abc123",
            tags=["test"],
        )
    )

    # Mock search
    persistence.search = AsyncMock(
        return_value=[
            SearchResult(
                crystal_id="crystal-abc123",
                content="Test content",
                summary="Test content...",
                similarity=0.95,
                captured_at="2025-01-01T00:00:00",
                is_stale=False,
            )
        ]
    )

    # Mock surface
    persistence.surface = AsyncMock(
        return_value=SearchResult(
            crystal_id="crystal-xyz789",
            content="Surfaced memory",
            summary="Surfaced memory...",
            similarity=0.7,
            captured_at="2025-01-01T00:00:00",
            is_stale=False,
        )
    )

    # Mock get_by_id
    persistence.get_by_id = AsyncMock(
        return_value=SearchResult(
            crystal_id="crystal-abc123",
            content="Retrieved content",
            summary="Retrieved...",
            similarity=1.0,
            captured_at="2025-01-01T00:00:00",
            is_stale=False,
        )
    )

    # Mock list_recent
    persistence.list_recent = AsyncMock(return_value=[])

    # Mock list_by_tag
    persistence.list_by_tag = AsyncMock(return_value=[])

    # Mock delete
    persistence.delete = AsyncMock(return_value=True)

    # Mock heal_ghosts
    persistence.heal_ghosts = AsyncMock(return_value=3)

    return persistence


@pytest.fixture
def brain_node(mock_persistence):
    """Create a BrainNode with mock persistence."""
    from services.brain.node import BrainNode

    return BrainNode(brain_persistence=mock_persistence)


# === Test Registration ===


class TestBrainNodeRegistration:
    """
    Tests for BrainNode AGENTESE registration.

    NOTE: @node decorator registration happens at import time.
    Since we reset_registry() before each test (autouse fixture),
    we need to manually re-register for tests that check global registry state.
    """

    def test_node_has_metadata_marker(self):
        """BrainNode has @node metadata marker."""
        from protocols.agentese.registry import NODE_MARKER, get_node_metadata
        from services.brain.node import BrainNode

        # Check marker is present on class
        assert hasattr(BrainNode, NODE_MARKER)

        # Check metadata via helper
        meta = get_node_metadata(BrainNode)
        assert meta is not None
        assert meta.path == "self.memory"
        assert "brain_persistence" in meta.dependencies

    def test_node_class_can_be_registered(self):
        """BrainNode can be manually registered with registry."""
        from protocols.agentese.registry import get_node_metadata
        from services.brain.node import BrainNode

        # Get metadata and manually register (simulating import-time behavior)
        registry = get_registry()
        meta = get_node_metadata(BrainNode)
        assert meta is not None

        registry._register_class("self.memory", BrainNode, meta)

        # Verify registration
        assert registry.has("self.memory")
        cls = registry.get("self.memory")
        assert cls is BrainNode

    def test_node_handle_matches_path(self, mock_persistence):
        """BrainNode.handle matches @node path."""
        from protocols.agentese.registry import get_node_metadata
        from services.brain.node import BrainNode

        node = BrainNode(brain_persistence=mock_persistence)
        meta = get_node_metadata(BrainNode)

        assert node.handle == "self.memory"
        assert meta is not None
        assert meta.path == node.handle

    def test_node_requires_persistence(self):
        """BrainNode requires brain_persistence argument (for proper DI fallback)."""
        from services.brain.node import BrainNode

        # Without persistence, instantiation should fail
        # This enables Logos to fall back to SelfMemoryContext
        with pytest.raises(TypeError):
            BrainNode()


# === Test Handle ===


class TestBrainNodeHandle:
    """Tests for BrainNode.handle property."""

    def test_handle_is_self_memory(self, brain_node):
        """Handle returns 'self.memory'."""
        assert brain_node.handle == "self.memory"


# === Test Affordances ===


class TestBrainNodeAffordances:
    """Tests for BrainNode affordances by archetype."""

    def test_developer_affordances(self, brain_node):
        """Developer gets full affordances including mutations."""
        meta = AgentMeta(name="test", archetype="developer")
        affordances = brain_node.affordances(meta)

        assert "capture" in affordances
        assert "search" in affordances
        assert "surface" in affordances
        assert "delete" in affordances
        assert "heal" in affordances
        assert "topology" in affordances

    def test_guest_affordances(self, brain_node):
        """Guest gets read-only affordances (no mutation)."""
        meta = AgentMeta(name="test", archetype="guest")
        affordances = brain_node.affordances(meta)

        # Read operations available to guests
        assert "search" in affordances
        assert "surface" in affordances
        # Mutation operations restricted (including capture)
        assert "capture" not in affordances  # Guests cannot write
        assert "delete" not in affordances
        assert "heal" not in affordances

    def test_base_affordances_included(self, brain_node):
        """All archetypes get base affordances."""
        meta = AgentMeta(name="test", archetype="guest")
        affordances = brain_node.affordances(meta)

        # Base affordances from BaseLogosNode
        assert "manifest" in affordances
        assert "witness" in affordances
        assert "affordances" in affordances
        assert "help" in affordances


# === Test Manifest ===


class TestBrainNodeManifest:
    """Tests for BrainNode.manifest() aspect."""

    @pytest.mark.asyncio
    async def test_manifest_returns_rendering(self, brain_node, mock_persistence):
        """Manifest returns BrainManifestRendering."""
        from services.brain.node import BrainManifestRendering

        observer = Observer.test()
        result = await brain_node.manifest(observer)

        assert isinstance(result, BrainManifestRendering)
        mock_persistence.manifest.assert_awaited_once()

    @pytest.mark.asyncio
    async def test_manifest_to_dict(self, brain_node):
        """Manifest rendering converts to dict."""
        observer = Observer.test()
        result = await brain_node.manifest(observer)

        data = result.to_dict()
        assert data["type"] == "brain_manifest"
        assert data["total_crystals"] == 42
        assert data["coherency_rate"] == 0.95

    @pytest.mark.asyncio
    async def test_manifest_to_text(self, brain_node):
        """Manifest rendering converts to text."""
        observer = Observer.test()
        result = await brain_node.manifest(observer)

        text = result.to_text()
        assert "Brain Status" in text
        assert "Total Crystals: 42" in text

    # Note: BrainNode now requires persistence (no test for None case)
    # This enables proper fallback to SelfMemoryContext when DI not configured


# === Test Aspects ===


class TestBrainNodeCapture:
    """Tests for self.memory.capture aspect."""

    @pytest.mark.asyncio
    async def test_capture_calls_persistence(self, brain_node, mock_persistence):
        """Capture invokes persistence.capture()."""
        observer = Observer.test()
        result = await brain_node.invoke(
            "capture",
            observer,
            content="Test content",
            tags=["test"],
        )

        mock_persistence.capture.assert_awaited_once_with(
            content="Test content",
            tags=["test"],
            source_type="capture",
            source_ref=None,
            metadata=None,
        )

    @pytest.mark.asyncio
    async def test_capture_returns_result(self, brain_node):
        """Capture returns structured result."""
        observer = Observer.test()
        result = await brain_node.invoke("capture", observer, content="Test")

        assert result["crystal_id"] == "crystal-abc123"
        assert "captured_at" in result


class TestBrainNodeSearch:
    """Tests for self.memory.search aspect."""

    @pytest.mark.asyncio
    async def test_search_calls_persistence(self, brain_node, mock_persistence):
        """Search invokes persistence.search()."""
        observer = Observer.test()
        await brain_node.invoke("search", observer, query="test query", limit=5)

        mock_persistence.search.assert_awaited_once_with(
            query="test query",
            limit=5,
            tags=None,
        )

    @pytest.mark.asyncio
    async def test_search_returns_results(self, brain_node):
        """Search returns structured results."""
        observer = Observer.test()
        result = await brain_node.invoke("search", observer, query="test")

        assert result["type"] == "search_results"
        assert result["query"] == "test"
        assert len(result["results"]) == 1


class TestBrainNodeSurface:
    """Tests for self.memory.surface aspect."""

    @pytest.mark.asyncio
    async def test_surface_calls_persistence(self, brain_node, mock_persistence):
        """Surface invokes persistence.surface()."""
        observer = Observer.test()
        await brain_node.invoke("surface", observer, context="inspiration", entropy=0.8)

        mock_persistence.surface.assert_awaited_once_with(
            context="inspiration",
            entropy=0.8,
        )

    @pytest.mark.asyncio
    async def test_surface_returns_memory(self, brain_node):
        """Surface returns surfaced memory."""
        observer = Observer.test()
        result = await brain_node.invoke("surface", observer)

        assert "surface" in result
        assert result["surface"]["crystal_id"] == "crystal-xyz789"


class TestBrainNodeGet:
    """Tests for self.memory.get aspect."""

    @pytest.mark.asyncio
    async def test_get_calls_persistence(self, brain_node, mock_persistence):
        """Get invokes persistence.get_by_id()."""
        observer = Observer.test()
        await brain_node.invoke("get", observer, crystal_id="crystal-abc123")

        mock_persistence.get_by_id.assert_awaited_once_with("crystal-abc123")

    @pytest.mark.asyncio
    async def test_get_without_id_returns_error(self, brain_node):
        """Get without crystal_id returns error."""
        observer = Observer.test()
        result = await brain_node.invoke("get", observer)

        assert "error" in result


class TestBrainNodeDelete:
    """Tests for self.memory.delete aspect."""

    @pytest.mark.asyncio
    async def test_delete_calls_persistence(self, brain_node, mock_persistence):
        """Delete invokes persistence.delete()."""
        observer = Observer.test()
        await brain_node.invoke("delete", observer, crystal_id="crystal-abc123")

        mock_persistence.delete.assert_awaited_once_with("crystal-abc123")

    @pytest.mark.asyncio
    async def test_delete_returns_result(self, brain_node):
        """Delete returns success status."""
        observer = Observer.test()
        result = await brain_node.invoke("delete", observer, crystal_id="crystal-abc123")

        assert result["deleted"] is True
        assert result["crystal_id"] == "crystal-abc123"


class TestBrainNodeHeal:
    """Tests for self.memory.heal aspect."""

    @pytest.mark.asyncio
    async def test_heal_calls_persistence(self, brain_node, mock_persistence):
        """Heal invokes persistence.heal_ghosts()."""
        observer = Observer.test()
        await brain_node.invoke("heal", observer)

        mock_persistence.heal_ghosts.assert_awaited_once()

    @pytest.mark.asyncio
    async def test_heal_returns_count(self, brain_node):
        """Heal returns healed count."""
        observer = Observer.test()
        result = await brain_node.invoke("heal", observer)

        assert result["healed"] == 3


# === Test Unknown Aspects ===


class TestBrainNodeUnknownAspect:
    """Tests for unknown aspect handling."""

    @pytest.mark.asyncio
    async def test_unknown_aspect_returns_error(self, brain_node):
        """Unknown aspects return error dict."""
        observer = Observer.test()
        result = await brain_node.invoke("unknown_aspect", observer)

        assert "error" in result
        assert "unknown_aspect" in result["error"].lower()


# === WARP Integration: Mark Emission (Law 3) ===


@pytest.fixture
def clean_trace_store():
    """Reset trace store before and after each test."""
    from services.witness.trace_store import reset_mark_store

    reset_mark_store()
    yield
    reset_mark_store()


class TestBrainWARPIntegration:
    """
    Tests for WARP integration: Law 3 Mark emission.

    These tests verify that Brain operations emit Marks when
    invoked through the AGENTESE gateway, per WARP Law 3:
    "Every AGENTESE invocation emits exactly one Mark."

    See: spec/protocols/warp-primitives.md
    See: plans/continuation-warp-servo-session4.md
    """

    @pytest.mark.asyncio
    async def test_brain_terrace_manifest_emits_trace_node(self, clean_trace_store):
        """
        Brain Lesson manifest operation emits a Mark.

        Law 3: Every AGENTESE invocation emits exactly one Mark.
        This test verifies that brain.terrace.manifest is traced.

        NOTE: Uses brain.terrace (not self.memory) because it doesn't
        require external persistence, making the test self-contained.

        NOTE: Does not use clean_registry fixture because we need
        brain.terrace to remain registered from module import.
        """
        from protocols.agentese.gateway import _import_node_modules, create_gateway
        from services.witness.trace_store import get_mark_store

        # Import all nodes (including brain.terrace)
        # This triggers @node registration if not already done
        _import_node_modules()
        # Re-populate registry in case it was reset by another test
        repopulate_registry()

        # Create gateway
        gateway = create_gateway(prefix="/agentese")

        observer = Observer.test()

        # Invoke manifest through gateway
        await gateway._invoke_path("brain.terrace", "manifest", observer)

        # Verify Mark was emitted (Law 3)
        store = get_mark_store()
        assert len(store) >= 1, "Law 3 violation: No Mark emitted for manifest"

        # Verify trace content
        trace = list(store.all())[-1]
        assert trace.origin == "gateway"
        assert trace.stimulus.kind == "agentese"
        assert "brain.terrace" in trace.stimulus.content
        assert "manifest" in trace.stimulus.content
        assert trace.response.success is True

    @pytest.mark.asyncio
    async def test_brain_terrace_create_emits_trace_node(self, clean_trace_store):
        """
        Brain Lesson create operation emits a Mark.

        Law 3: Every AGENTESE invocation emits exactly one Mark.
        This test verifies that brain.terrace.create is traced.
        """
        from protocols.agentese.gateway import _import_node_modules, create_gateway
        from services.witness.trace_store import get_mark_store

        _import_node_modules()
        repopulate_registry()
        gateway = create_gateway(prefix="/agentese")
        observer = Observer.test()

        # Invoke create through gateway
        await gateway._invoke_path(
            "brain.terrace",
            "create",
            observer,
            topic="warp-test",
            content="Test knowledge for WARP integration",
        )

        # Verify Mark was emitted
        store = get_mark_store()
        assert len(store) >= 1, "Law 3 violation: No Mark emitted for create"

        trace = list(store.all())[-1]
        assert "brain.terrace" in trace.stimulus.content
        assert "create" in trace.stimulus.content

    @pytest.mark.asyncio
    async def test_brain_terrace_search_emits_trace_node(self, clean_trace_store):
        """
        Brain Lesson search operation emits a Mark.

        Law 3: Every AGENTESE invocation emits exactly one Mark.
        This test verifies that brain.terrace.search is traced.
        """
        from protocols.agentese.gateway import _import_node_modules, create_gateway
        from services.witness.trace_store import get_mark_store

        _import_node_modules()
        repopulate_registry()
        gateway = create_gateway(prefix="/agentese")
        observer = Observer.test()

        # Invoke search through gateway
        await gateway._invoke_path("brain.terrace", "search", observer, query="test")

        # Verify Mark was emitted
        store = get_mark_store()
        assert len(store) >= 1, "Law 3 violation: No Mark emitted for search"

        trace = list(store.all())[-1]
        assert "brain.terrace" in trace.stimulus.content
        assert "search" in trace.stimulus.content

    @pytest.mark.asyncio
    async def test_multiple_operations_emit_multiple_traces(self, clean_trace_store):
        """
        Multiple Brain operations emit distinct Marks.

        Law 3: Every AGENTESE invocation emits exactly one Mark.
        This test verifies that N invocations produce N traces.
        """
        from protocols.agentese.gateway import _import_node_modules, create_gateway
        from services.witness.trace_store import get_mark_store

        _import_node_modules()
        repopulate_registry()
        gateway = create_gateway(prefix="/agentese")
        observer = Observer.test()

        # Invoke multiple operations
        await gateway._invoke_path("brain.terrace", "manifest", observer)
        await gateway._invoke_path(
            "brain.terrace", "create", observer, topic="test1", content="Content 1"
        )
        await gateway._invoke_path("brain.terrace", "search", observer, query="test")

        # Verify 3 Marks were emitted
        store = get_mark_store()
        assert len(store) >= 3, f"Expected 3+ traces, got {len(store)}"

        # Verify all traces are unique
        trace_ids = [t.id for t in store.all()]
        assert len(set(trace_ids)) == len(trace_ids), "Trace IDs should be unique"
