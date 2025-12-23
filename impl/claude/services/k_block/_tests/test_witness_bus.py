"""
K-Block → Witness Integration Tests.

Tests that K-Block edits emit to WitnessSynergyBus.

"The proof IS the decision. The mark IS the witness."
"Editing IS witnessing."
"""

from __future__ import annotations

from services.witness.bus import WitnessTopics

from ..core import KBlock, WitnessedSheaf, generate_kblock_id
from ..views import ViewType

# =============================================================================
# Helpers
# =============================================================================


def make_kblock(
    content: str = "# Test", path: str = "test.md", activate_prose: bool = True
) -> KBlock:
    """Create a K-Block for testing."""
    block = KBlock(
        id=generate_kblock_id(),
        path=path,
        content=content,
        base_content=content,
    )
    if activate_prose:
        block.activate_view(ViewType.PROSE)
    return block


# =============================================================================
# Tests - Sync verification (async bus emit is tested by full K-Block suite)
# =============================================================================


class TestWitnessIntegration:
    """Tests for K-Block → Witness bus integration."""

    def test_kblock_topics_exist(self):
        """WitnessTopics should have K-Block topics defined."""
        assert hasattr(WitnessTopics, "KBLOCK_EDITED")
        assert hasattr(WitnessTopics, "KBLOCK_SAVED")
        assert hasattr(WitnessTopics, "KBLOCK_DISCARDED")
        assert hasattr(WitnessTopics, "KBLOCK_ALL")

        assert WitnessTopics.KBLOCK_EDITED == "witness.kblock.edited"
        assert WitnessTopics.KBLOCK_SAVED == "witness.kblock.saved"
        assert WitnessTopics.KBLOCK_DISCARDED == "witness.kblock.discarded"
        assert WitnessTopics.KBLOCK_ALL == "witness.kblock.*"

    def test_witnessed_sheaf_has_bus_emit_methods(self):
        """WitnessedSheaf should have bus emit methods."""
        kblock = make_kblock("# Test")
        sheaf = WitnessedSheaf(kblock, actor="Kent")

        assert hasattr(sheaf, "_schedule_bus_emit")
        assert hasattr(sheaf, "_emit_to_bus")

    def test_sync_context_does_not_crash(self):
        """
        In sync context (no event loop), bus emit should be skipped gracefully.

        When called without an event loop, _schedule_bus_emit should catch
        the RuntimeError and silently skip the bus emit.
        """
        # Create K-Block and sheaf
        kblock = make_kblock("# Sync test")
        sheaf = WitnessedSheaf(kblock, actor="Test")

        # This should not crash even though there's no event loop running
        # The _schedule_bus_emit will catch RuntimeError and skip
        sheaf.propagate(ViewType.PROSE, "# Updated")

        # If we got here without exception, test passes

    def test_propagate_returns_trace(self):
        """propagate() should return trace in changes dict."""
        kblock = make_kblock("# Test", path="test.md")
        sheaf = WitnessedSheaf(kblock, actor="Kent")
        changes = sheaf.propagate(ViewType.PROSE, "# Updated", reasoning="Test edit")

        # Verify trace was created
        assert ViewType.PROSE in changes
        assert "trace" in changes[ViewType.PROSE]
        trace = changes[ViewType.PROSE]["trace"]
        assert trace["actor"] == "Kent"
        assert trace["reasoning"] == "Test edit"
        assert trace["source_view"] == "prose"

    def test_edit_history_populated(self):
        """propagate() should add trace to edit_history."""
        kblock = make_kblock("# Test")
        sheaf = WitnessedSheaf(kblock, actor="Kent")

        assert len(sheaf.edit_history) == 0

        sheaf.propagate(ViewType.PROSE, "# Updated")

        assert len(sheaf.edit_history) == 1
        assert sheaf.edit_history[0].actor == "Kent"
        assert sheaf.edit_history[0].source_view == ViewType.PROSE
