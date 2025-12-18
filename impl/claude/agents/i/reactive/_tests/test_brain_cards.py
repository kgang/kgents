"""
Tests for Brain Cards: Cartography and Ghost Notifier widgets.

Session 5: Crown Jewel Brain UI Layer
"""

from __future__ import annotations

import pytest

from agents.i.reactive.primitives.brain_cards import (
    BrainCartographyCard,
    CartographyState,
    GhostListState,
    GhostNotifierCard,
    GhostState,
    create_cartography_card,
    create_ghost_card,
)
from agents.i.reactive.widget import RenderTarget


class TestBrainCartographyCard:
    """Tests for BrainCartographyCard."""

    def test_create_default(self) -> None:
        """Default cartography card can be created."""
        card = BrainCartographyCard()
        assert card is not None
        assert card.state.value.landmarks == 0

    def test_create_with_state(self) -> None:
        """Cartography card with specific state."""
        card = BrainCartographyCard(
            CartographyState(
                landmarks=5,
                desire_lines=12,
                voids=3,
                resolution="high",
            )
        )
        state = card.state.value
        assert state.landmarks == 5
        assert state.desire_lines == 12
        assert state.voids == 3
        assert state.resolution == "high"

    def test_project_cli(self) -> None:
        """CLI projection produces readable text."""
        card = BrainCartographyCard(
            CartographyState(
                landmarks=3,
                desire_lines=7,
                voids=2,
            )
        )
        output = card.project(RenderTarget.CLI)
        assert "Memory Topology" in output
        assert "Landmarks: 3" in output
        assert "Paths: 7" in output
        assert "Voids: 2" in output

    def test_project_json(self) -> None:
        """JSON projection produces structured data."""
        card = BrainCartographyCard(
            CartographyState(
                landmarks=5,
                desire_lines=10,
                voids=1,
                resolution="medium",
            )
        )
        output = card.project(RenderTarget.JSON)
        assert output["type"] == "cartography"
        assert output["landmarks"] == 5
        assert output["desire_lines"] == 10
        assert output["voids"] == 1
        assert output["resolution"] == "medium"

    def test_from_manifest(self) -> None:
        """Create card from manifest result dict."""
        manifest = {
            "landmarks": 8,
            "desire_lines": 15,
            "voids": 4,
            "resolution": "high",
        }
        card = BrainCartographyCard.from_manifest(manifest)
        state = card.state.value
        assert state.landmarks == 8
        assert state.desire_lines == 15

    def test_create_cartography_card_helper(self) -> None:
        """Helper function creates card correctly."""
        card = create_cartography_card(
            landmarks=2,
            desire_lines=5,
            voids=0,
            resolution="low",
        )
        state = card.state.value
        assert state.landmarks == 2
        assert state.resolution == "low"


class TestGhostNotifierCard:
    """Tests for GhostNotifierCard."""

    def test_create_default(self) -> None:
        """Default ghost notifier can be created."""
        card = GhostNotifierCard()
        assert card is not None
        assert len(card.state.value.ghosts) == 0

    def test_create_with_ghosts(self) -> None:
        """Ghost notifier with specific ghosts."""
        card = GhostNotifierCard(
            GhostListState(
                ghosts=(
                    GhostState(content="Python tutorial", relevance=0.85),
                    GhostState(content="ML basics", relevance=0.62),
                ),
                context="programming",
                total_count=2,
            )
        )
        state = card.state.value
        assert len(state.ghosts) == 2
        assert state.ghosts[0].relevance == 0.85
        assert state.context == "programming"

    def test_project_cli_empty(self) -> None:
        """CLI projection for empty ghost list."""
        card = GhostNotifierCard()
        output = card.project(RenderTarget.CLI)
        assert "No memories surfaced" in output

    def test_project_cli_with_ghosts(self) -> None:
        """CLI projection shows ghost list."""
        card = GhostNotifierCard(
            GhostListState(
                ghosts=(
                    GhostState(content="Python tutorial", relevance=0.85),
                    GhostState(content="ML basics", relevance=0.62),
                ),
                total_count=2,
            )
        )
        output = card.project(RenderTarget.CLI)
        assert "Surfaced Memories (2)" in output
        assert "Python tutorial" in output
        assert "85%" in output

    def test_project_json(self) -> None:
        """JSON projection produces structured data."""
        card = GhostNotifierCard(
            GhostListState(
                ghosts=(
                    GhostState(
                        content="Test content",
                        relevance=0.75,
                        concept_id="test_123",
                    ),
                ),
                context="test query",
                total_count=1,
            )
        )
        output = card.project(RenderTarget.JSON)
        assert output["type"] == "ghost_notifier"
        assert output["context"] == "test query"
        assert len(output["ghosts"]) == 1
        assert output["ghosts"][0]["relevance"] == 0.75

    def test_from_surface_result(self) -> None:
        """Create card from ghost.surface result."""
        result = {
            "surfaced": [
                {"content": "Memory A", "relevance": 0.9, "concept_id": "a"},
                {"content": "Memory B", "similarity": 0.6, "concept_id": "b"},
            ],
            "context": "search query",
            "count": 2,
        }
        card = GhostNotifierCard.from_surface_result(result)
        state = card.state.value
        assert len(state.ghosts) == 2
        assert state.ghosts[0].content == "Memory A"
        assert state.ghosts[0].relevance == 0.9
        # 'similarity' should be mapped to relevance
        assert state.ghosts[1].relevance == 0.6

    def test_create_ghost_card_helper(self) -> None:
        """Helper function creates card correctly."""
        card = create_ghost_card(
            ghosts=[
                ("Content A", 0.8),
                ("Content B", 0.5),
            ],
            context="test",
        )
        state = card.state.value
        assert len(state.ghosts) == 2
        assert state.ghosts[0].content == "Content A"
        assert state.ghosts[0].relevance == 0.8
        assert state.context == "test"

    def test_truncates_long_content(self) -> None:
        """CLI projection truncates long content."""
        long_content = "This is a very long content string that should be truncated"
        card = GhostNotifierCard(
            GhostListState(
                ghosts=(GhostState(content=long_content, relevance=0.5),),
                total_count=1,
            )
        )
        output = card.project(RenderTarget.CLI)
        # Should contain truncated version with ellipsis
        assert "..." in output
        # Full content should not appear
        assert long_content not in output
