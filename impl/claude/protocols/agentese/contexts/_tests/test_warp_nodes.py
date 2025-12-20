"""
Tests for WARP Phase 2 AGENTESE Nodes.

These tests verify:
1. VoiceGateNode (self.voice.gate.*)
2. TerraceNode (brain.terrace.*)

Both are "dark matter" primitives from Phase 1 that needed AGENTESE access.
"""

from __future__ import annotations

import uuid

import pytest

import protocols.agentese.contexts.brain_terrace as terrace_module
from protocols.agentese.contexts.brain_terrace import TerraceNode
from protocols.agentese.contexts.self_voice import VoiceGateNode
from protocols.agentese.node import BasicRendering


def _unique_topic(base: str = "topic") -> str:
    """Generate unique topic name to avoid parallel test collisions."""
    return f"{base}_{uuid.uuid4().hex[:8]}"


# =============================================================================
# VoiceGateNode Tests
# =============================================================================


class TestVoiceGateNode:
    """Tests for self.voice.gate.* AGENTESE node."""

    @pytest.fixture
    def node(self) -> VoiceGateNode:
        """Create VoiceGateNode instance."""
        return VoiceGateNode()

    def test_node_path(self, node: VoiceGateNode) -> None:
        """Node has correct AGENTESE path."""
        assert node.handle == "self.voice.gate"

    def test_node_affordances(self, node: VoiceGateNode) -> None:
        """Node has expected affordances."""
        from protocols.agentese.node import AgentMeta

        meta = AgentMeta(name="test", archetype="developer")
        affordances = node.affordances(meta)
        assert "manifest" in affordances
        assert "check" in affordances
        assert "report" in affordances

    def test_manifest_returns_rendering(self, node: VoiceGateNode) -> None:
        """Manifest aspect returns renderable."""
        import asyncio

        result = asyncio.get_event_loop().run_until_complete(node.manifest(None))  # type: ignore[arg-type]

        assert isinstance(result, BasicRendering)
        assert result.metadata is not None
        assert "anchors" in result.metadata
        assert "laws" in result.metadata

    def test_manifest_includes_anchors(self, node: VoiceGateNode) -> None:
        """Manifest includes voice anchors."""
        import asyncio

        result = asyncio.get_event_loop().run_until_complete(node.manifest(None))  # type: ignore[arg-type]

        anchors = result.metadata["anchors"]
        assert "Daring, bold, creative, opinionated but not gaudy" in anchors
        assert "The Mirror Test" in anchors

    def test_check_clean_text_passes(self, node: VoiceGateNode) -> None:
        """Clean text passes voice check."""
        result = node.check("This is a simple, clean statement.")

        assert isinstance(result, BasicRendering)
        assert result.metadata["passed"] is True
        assert result.metadata["blocking_count"] == 0

    def test_check_corporate_speak_warns(self, node: VoiceGateNode) -> None:
        """Corporate speak triggers warning in permissive mode."""
        result = node.check("We need to leverage synergies moving forward.")

        # In permissive mode, should pass but with warnings
        assert result.metadata["warning_count"] > 0
        # Check that specific violations were found
        violations = result.metadata["violations"]
        assert any("leverage" in str(v).lower() for v in violations)

    def test_check_strict_mode_blocks(self, node: VoiceGateNode) -> None:
        """Strict mode blocks corporate speak."""
        result = node.check("We need to leverage synergies.", strict=True)

        # In strict mode, should not pass
        assert result.metadata["passed"] is False
        assert result.metadata["blocking_count"] > 0

    def test_check_detects_anchors(self, node: VoiceGateNode) -> None:
        """Check detects voice anchor references."""
        result = node.check(
            "We follow the principle: Tasteful > feature-complete. Always apply The Mirror Test."
        )

        anchors = result.metadata["anchors_referenced"]
        assert len(anchors) >= 1

    def test_report_returns_detailed_analysis(self, node: VoiceGateNode) -> None:
        """Report provides detailed analysis."""
        result = node.report("We should leverage best practices to optimize synergies.")

        assert isinstance(result, BasicRendering)
        assert "anti_sausage_score" in result.metadata
        assert "summary" in result.metadata
        assert result.metadata["summary"]["blocking"] >= 0
        assert result.metadata["summary"]["warnings"] >= 0


# =============================================================================
# TerraceNode Tests
# =============================================================================


class TestTerraceNode:
    """Tests for brain.terrace.* AGENTESE node."""

    @pytest.fixture(autouse=True)
    def isolated_store(self, monkeypatch: pytest.MonkeyPatch) -> None:
        """Create isolated store per test using monkeypatch for true isolation."""
        from services.witness.terrace import TerraceStore

        # Use monkeypatch to ensure complete isolation even across parallel workers
        fresh_store = TerraceStore()
        monkeypatch.setattr(terrace_module, "_terrace_store", fresh_store)

    @pytest.fixture
    def node(self) -> TerraceNode:
        """Create TerraceNode instance."""
        return TerraceNode()

    def test_node_path(self, node: TerraceNode) -> None:
        """Node has correct AGENTESE path."""
        assert node.handle == "brain.terrace"

    def test_node_affordances(self, node: TerraceNode) -> None:
        """Node has expected affordances."""
        from protocols.agentese.node import AgentMeta

        meta = AgentMeta(name="test", archetype="developer")
        affordances = node.affordances(meta)
        assert "manifest" in affordances
        assert "create" in affordances
        assert "evolve" in affordances
        assert "search" in affordances
        assert "history" in affordances

    def test_manifest_empty_store(self, node: TerraceNode) -> None:
        """Manifest works with empty store."""
        import asyncio

        result = asyncio.get_event_loop().run_until_complete(node.manifest(None))  # type: ignore[arg-type]

        assert isinstance(result, BasicRendering)
        assert result.metadata["total_entries"] == 0
        assert result.metadata["topics"] == []

    def test_create_new_entry(self, node: TerraceNode) -> None:
        """Can create new knowledge entry."""
        result = node.create(
            topic="Testing patterns",
            content="DI > mocking: set_soul() injection pattern beats patch()",
            tags=["testing", "patterns"],
        )

        assert result.metadata["created"] is True
        assert result.metadata["terrace"]["topic"] == "Testing patterns"
        assert result.metadata["terrace"]["version"] == 1

    def test_create_duplicate_topic_fails(self, node: TerraceNode) -> None:
        """Creating duplicate topic returns error."""
        # Create first
        node.create(topic="Duplicate", content="First")

        # Try to create duplicate
        result = node.create(topic="Duplicate", content="Second")

        assert "error" in result.metadata
        assert result.metadata["error"] == "topic_exists"

    def test_evolve_updates_version(self, node: TerraceNode) -> None:
        """Evolving a topic creates new version."""
        # Create initial
        node.create(topic="Evolving", content="Version 1")

        # Evolve
        result = node.evolve(
            topic="Evolving",
            content="Version 2 with improvements",
            reason="Added improvements",
        )

        assert result.metadata["evolved"] is True
        assert result.metadata["old_version"] == 1
        assert result.metadata["new_version"] == 2

    def test_evolve_missing_topic_fails(self, node: TerraceNode) -> None:
        """Evolving non-existent topic returns error."""
        result = node.evolve(topic="Missing", content="New content")

        assert "error" in result.metadata
        assert result.metadata["error"] == "topic_not_found"

    def test_search_finds_matching(self, node: TerraceNode) -> None:
        """Search finds matching entries."""
        node.create(topic="AGENTESE patterns", content="Use @node decorator")
        node.create(topic="Testing basics", content="Use pytest")

        result = node.search("AGENTESE")

        assert result.metadata["count"] == 1
        assert result.metadata["results"][0]["topic"] == "AGENTESE patterns"

    def test_search_case_insensitive(self, node: TerraceNode) -> None:
        """Search is case-insensitive."""
        node.create(topic="Important", content="Test content")

        result = node.search("important")

        assert result.metadata["count"] == 1

    def test_history_shows_versions(self, node: TerraceNode) -> None:
        """History shows all versions of a topic."""
        # Create and evolve
        node.create(topic="Versioned", content="V1")
        node.evolve(topic="Versioned", content="V2", reason="Update 1")
        node.evolve(topic="Versioned", content="V3", reason="Update 2")

        result = node.history("Versioned")

        assert result.metadata["count"] == 3
        versions = [v["version"] for v in result.metadata["versions"]]
        assert versions == [1, 2, 3]

    def test_history_missing_topic(self, node: TerraceNode) -> None:
        """History for missing topic returns empty."""
        result = node.history("NonExistent")

        assert result.metadata["count"] == 0
        assert result.metadata["versions"] == []

    def test_manifest_after_creates(self, node: TerraceNode) -> None:
        """Manifest reflects created entries."""
        node.create(topic="Topic A", content="Content A")
        node.create(topic="Topic B", content="Content B")

        import asyncio

        result = asyncio.get_event_loop().run_until_complete(node.manifest(None))  # type: ignore[arg-type]

        assert result.metadata["total_entries"] == 2
        assert "Topic A" in result.metadata["topics"]
        assert "Topic B" in result.metadata["topics"]


# =============================================================================
# Integration Tests
# =============================================================================


class TestWarpNodesIntegration:
    """Integration tests for WARP nodes working together."""

    @pytest.fixture(autouse=True)
    def isolated_store(self, monkeypatch: pytest.MonkeyPatch) -> None:
        """Create isolated store per test using monkeypatch for true isolation."""
        from services.witness.terrace import TerraceStore

        # Use monkeypatch to ensure complete isolation even across parallel workers
        fresh_store = TerraceStore()
        monkeypatch.setattr(terrace_module, "_terrace_store", fresh_store)

    def test_voice_gate_can_check_terrace_content(self) -> None:
        """VoiceGate can validate Terrace content."""
        terrace_node = TerraceNode()
        voice_node = VoiceGateNode()

        # Create knowledge
        terrace_node.create(
            topic="Anti-Sausage Guidelines",
            content="Tasteful > feature-complete. Avoid corporate speak.",
        )

        # Check the content for voice
        result = voice_node.check("Tasteful > feature-complete. Avoid corporate speak.")

        assert result.metadata["passed"] is True
        # Should detect anchor
        assert len(result.metadata["anchors_referenced"]) > 0

    def test_nodes_are_stateless(self) -> None:
        """Nodes are stateless (Symbiont pattern)."""
        import asyncio

        # Create two node instances
        node1 = TerraceNode()
        node2 = TerraceNode()

        # Create via node1
        node1.create(topic="Shared", content="Test")

        # Should be visible via node2 (shared store)
        result = asyncio.get_event_loop().run_until_complete(node2.manifest(None))  # type: ignore[arg-type]
        assert result.metadata["total_entries"] == 1

    def test_cli_rendering_exists(self) -> None:
        """Nodes provide CLI rendering."""
        import asyncio

        voice_node = VoiceGateNode()
        terrace_node = TerraceNode()

        voice_result = asyncio.get_event_loop().run_until_complete(voice_node.manifest(None))  # type: ignore[arg-type]
        terrace_result = asyncio.get_event_loop().run_until_complete(terrace_node.manifest(None))  # type: ignore[arg-type]

        # Both should have content output
        assert voice_result.content is not None
        assert terrace_result.content is not None
        assert "Voice Gate" in voice_result.content
        assert "Terrace" in terrace_result.content


# =============================================================================
# Curate Aspect Tests (WARP Session 6)
# =============================================================================


class TestTerraceNodeCurate:
    """Tests for brain.terrace.curate aspect (human curation → trust L3)."""

    @pytest.fixture(autouse=True)
    def isolated_store(self, monkeypatch: pytest.MonkeyPatch) -> None:
        """Create isolated store per test."""
        from services.witness.terrace import TerraceStore

        fresh_store = TerraceStore()
        monkeypatch.setattr(terrace_module, "_terrace_store", fresh_store)

    @pytest.fixture
    def node(self) -> TerraceNode:
        """Create TerraceNode instance."""
        return TerraceNode()

    def test_curate_elevates_trust(self, node: TerraceNode) -> None:
        """Curating a topic elevates trust to L3."""
        # Create initial entry
        node.create(topic="Testing Pattern", content="DI > mocking")

        # Curate it
        result = node.curate(topic="Testing Pattern", curator="kent", notes="Verified in practice")

        assert result.metadata["curated"] is True
        assert result.metadata["trust_level"] == "L3"
        assert result.metadata["curator"] == "kent"
        assert result.metadata["old_version"] == 1
        assert result.metadata["new_version"] == 2

    def test_curate_adds_curated_tag(self, node: TerraceNode) -> None:
        """Curating adds 'curated' tag to the entry."""
        node.create(topic="Tagged", content="Content", tags=["original"])
        result = node.curate(topic="Tagged")

        terrace = result.metadata["terrace"]
        assert "curated" in terrace["tags"]
        assert "original" in terrace["tags"]

    def test_curate_preserves_content(self, node: TerraceNode) -> None:
        """Curating preserves the original content."""
        original_content = "Important learning about composition"
        node.create(topic="Preserved", content=original_content)

        result = node.curate(topic="Preserved")

        assert result.metadata["terrace"]["content"] == original_content

    def test_curate_missing_topic_returns_error(self, node: TerraceNode) -> None:
        """Curating non-existent topic returns error."""
        result = node.curate(topic="NonExistent")

        assert "error" in result.metadata
        assert result.metadata["error"] == "topic_not_found"

    def test_curate_sets_full_confidence(self, node: TerraceNode) -> None:
        """Curating sets confidence to 1.0 (full trust)."""
        # Create with lower confidence
        node.create(topic="LowConf", content="Test", confidence=0.5)

        result = node.curate(topic="LowConf")

        assert result.metadata["terrace"]["confidence"] == 1.0

    def test_curate_adds_metadata(self, node: TerraceNode) -> None:
        """Curating adds curation metadata."""
        node.create(topic="MetadataTest", content="Test")
        result = node.curate(topic="MetadataTest", curator="alice", notes="Looks good!")

        metadata = result.metadata["terrace"]["metadata"]
        assert metadata["curated"] is True
        assert metadata["curator"] == "alice"
        assert metadata["curation_notes"] == "Looks good!"
        assert metadata["trust_level"] == "L3"


# =============================================================================
# Crystallize Aspect Tests (WARP Session 6)
# =============================================================================


class TestTerraceNodeCrystallize:
    """Tests for brain.terrace.crystallize aspect (Brain → Terrace bridge)."""

    @pytest.fixture(autouse=True)
    def isolated_store(self, monkeypatch: pytest.MonkeyPatch) -> None:
        """Create isolated store per test."""
        from services.witness.terrace import TerraceStore

        fresh_store = TerraceStore()
        monkeypatch.setattr(terrace_module, "_terrace_store", fresh_store)

    @pytest.fixture
    def node(self) -> TerraceNode:
        """Create TerraceNode instance."""
        return TerraceNode()

    @pytest.mark.asyncio
    async def test_crystallize_missing_crystal_id_returns_error(self, node: TerraceNode) -> None:
        """Crystallize without crystal_id returns error."""
        result = await node.crystallize(crystal_id="", topic="Test")

        assert "error" in result.metadata
        assert result.metadata["error"] == "missing_crystal_id"

    @pytest.mark.asyncio
    async def test_crystallize_missing_topic_returns_error(self, node: TerraceNode) -> None:
        """Crystallize without topic returns error."""
        result = await node.crystallize(crystal_id="crystal-123", topic="")

        assert "error" in result.metadata
        assert result.metadata["error"] == "missing_topic"

    @pytest.mark.asyncio
    async def test_crystallize_handles_brain_not_found(self, node: TerraceNode) -> None:
        """Crystallize handles crystal not found gracefully."""
        # This will fail because the crystal doesn't exist
        result = await node.crystallize(crystal_id="nonexistent-123", topic="Test")

        # Should get an error (either crystal_not_found or brain_unavailable)
        assert "error" in result.metadata


# =============================================================================
# VoiceGate Integration Tests (WARP Session 6)
# =============================================================================


class TestTerraceVoiceGateIntegration:
    """Tests for VoiceGate integration in Terrace."""

    @pytest.fixture(autouse=True)
    def isolated_store(self, monkeypatch: pytest.MonkeyPatch) -> None:
        """Create isolated store per test."""
        from services.witness.terrace import TerraceStore

        fresh_store = TerraceStore()
        monkeypatch.setattr(terrace_module, "_terrace_store", fresh_store)

    @pytest.fixture
    def node(self) -> TerraceNode:
        """Create TerraceNode instance."""
        return TerraceNode()

    def test_create_includes_voice_check(self, node: TerraceNode) -> None:
        """Create includes voice check result in metadata."""
        result = node.create(
            topic="Voice Checked",
            content="Tasteful > feature-complete is our guiding principle.",
        )

        # Should include voice check
        assert "voice_check" in result.metadata
        assert result.metadata["voice_check"]["passed"] is True
        # Should detect the anchor
        assert len(result.metadata["voice_check"]["anchors"]) > 0

    def test_create_flags_corporate_speak(self, node: TerraceNode) -> None:
        """Create flags corporate speak in voice check."""
        result = node.create(
            topic="Corporate",
            content="We need to leverage synergies moving forward.",
        )

        # Still creates (permissive mode) but flags issues
        assert result.metadata["created"] is True
        assert "voice_check" in result.metadata
        assert result.metadata["voice_check"]["warnings"] > 0

    def test_curate_then_check_voice(self, node: TerraceNode) -> None:
        """Curated content can be voice-checked separately."""
        voice_node = VoiceGateNode()

        # Create and curate
        node.create(topic="Curated Content", content="The Mirror Test matters.")
        node.curate(topic="Curated Content")

        # Voice check the content
        result = voice_node.check("The Mirror Test matters.")

        assert result.metadata["passed"] is True
        assert len(result.metadata["anchors_referenced"]) > 0


# =============================================================================
# Affordance Tests (WARP Session 6)
# =============================================================================


class TestTerraceAffordances:
    """Tests for new affordances in TerraceNode."""

    @pytest.fixture
    def node(self) -> TerraceNode:
        """Create TerraceNode instance."""
        return TerraceNode()

    def test_curate_in_affordances(self, node: TerraceNode) -> None:
        """Curate is included in affordances."""
        from protocols.agentese.node import AgentMeta

        meta = AgentMeta(name="test", archetype="developer")
        affordances = node.affordances(meta)

        assert "curate" in affordances

    def test_crystallize_in_affordances(self, node: TerraceNode) -> None:
        """Crystallize is included in affordances."""
        from protocols.agentese.node import AgentMeta

        meta = AgentMeta(name="test", archetype="developer")
        affordances = node.affordances(meta)

        assert "crystallize" in affordances
