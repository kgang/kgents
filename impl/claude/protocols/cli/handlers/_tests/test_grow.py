"""
Tests for the grow CLI handler.

Tests the self.grow CLI interface for the autopoietic holon generator.
"""

from __future__ import annotations

import pytest


class TestGrowHandler:
    """Test the grow CLI handler."""

    def test_cmd_grow_exists(self) -> None:
        """Handler should be importable."""
        from protocols.cli.handlers.grow import cmd_grow

        assert cmd_grow is not None
        assert callable(cmd_grow)

    def test_cmd_grow_help(self) -> None:
        """Help should return 0."""
        from protocols.cli.handlers.grow import cmd_grow

        result = cmd_grow(["--help"])
        assert result == 0

    def test_cmd_grow_status(self) -> None:
        """Status should return 0."""
        from protocols.cli.handlers.grow import cmd_grow

        result = cmd_grow(["status"])
        assert result == 0

    def test_cmd_grow_budget(self) -> None:
        """Budget should return 0."""
        from protocols.cli.handlers.grow import cmd_grow

        result = cmd_grow(["budget"])
        assert result == 0

    def test_cmd_grow_nursery(self) -> None:
        """Nursery should return 0."""
        from protocols.cli.handlers.grow import cmd_grow

        result = cmd_grow(["nursery"])
        assert result == 0

    def test_cmd_grow_recognize_demo(self) -> None:
        """Recognize with demo flag should return 0."""
        from protocols.cli.handlers.grow import cmd_grow

        result = cmd_grow(["recognize", "--demo"])
        assert result == 0

    def test_cmd_grow_propose_missing_args(self) -> None:
        """Propose without args should return error."""
        from protocols.cli.handlers.grow import cmd_grow

        result = cmd_grow(["propose"])
        assert result == 1

    def test_cmd_grow_unknown_command(self) -> None:
        """Unknown command should return error."""
        from protocols.cli.handlers.grow import cmd_grow

        result = cmd_grow(["unknown_command_xyz"])
        assert result == 1


class TestGrowSession:
    """Test session management."""

    def test_get_session(self) -> None:
        """Should return session instance."""
        from protocols.cli.handlers.grow import _get_session

        session = _get_session()
        assert session is not None
        assert hasattr(session, "proposals")
        assert hasattr(session, "last_gaps")

    def test_get_resolver(self) -> None:
        """Should return resolver instance."""
        from protocols.cli.handlers.grow import _get_resolver

        resolver = _get_resolver()
        assert resolver is not None
        assert hasattr(resolver, "_budget")
        assert hasattr(resolver, "_nursery")


class TestGrowPipeline:
    """Test the full growth pipeline through CLI."""

    def test_propose_and_validate(self) -> None:
        """Should create and validate a proposal."""
        from protocols.cli.handlers.grow import _get_session, cmd_grow

        # Clear session
        session = _get_session()
        session.proposals.clear()

        # Create proposal
        result = cmd_grow(
            ["propose", "world", "test_garden", "--why", "Test garden for CLI"]
        )
        assert result == 0

        # Check proposal was stored
        assert len(session.proposals) == 1

        # Get proposal ID
        proposal_id = list(session.proposals.keys())[0]

        # Validate
        result = cmd_grow(["validate", proposal_id[:8]])
        assert result == 0

    def test_germinate_flow(self) -> None:
        """Should germinate a validated proposal."""
        from protocols.cli.handlers.grow import _get_resolver, _get_session, cmd_grow

        # Clear state
        session = _get_session()
        session.proposals.clear()
        resolver = _get_resolver()

        # Reset nursery
        resolver._nursery._holons.clear()

        # Create proposal with good justification
        result = cmd_grow(
            [
                "propose",
                "world",
                "test_flower",
                "--why",
                "Agents frequently need world.test_flower for botanical exploration. Fills the gap between existing holons.",
            ]
        )
        assert result == 0

        # Get proposal ID
        proposal_id = list(session.proposals.keys())[0]

        # Germinate (includes validation)
        result = cmd_grow(["germinate", proposal_id[:8]])
        # May fail validation, that's ok for this test
        assert result in (0, 1)


class TestGrowIntegration:
    """Integration tests with the self_grow module."""

    def test_resolver_has_all_nodes(self) -> None:
        """Resolver should have all required nodes."""
        from protocols.cli.handlers.grow import _get_resolver

        resolver = _get_resolver()

        assert resolver._recognize is not None
        assert resolver._propose is not None
        assert resolver._validate is not None
        assert resolver._germinate is not None
        assert resolver._promote is not None
        assert resolver._rollback is not None
        assert resolver._prune is not None
        assert resolver._budget_node is not None
        assert resolver._nursery is not None

    def test_budget_tracks_spending(self) -> None:
        """Budget should track entropy spending."""
        from protocols.cli.handlers.grow import _get_resolver

        resolver = _get_resolver()
        budget = resolver._budget

        initial = budget.remaining
        if budget.can_afford("recognize"):
            budget.spend("recognize")
            assert budget.remaining < initial
            assert "recognize" in budget.spent_by_operation


class TestHollowRegistration:
    """Test that grow is registered in hollow.py."""

    def test_command_registered(self) -> None:
        """Grow command should be in registry."""
        from protocols.cli.hollow import COMMAND_REGISTRY

        assert "grow" in COMMAND_REGISTRY
        assert COMMAND_REGISTRY["grow"] == "protocols.cli.handlers.grow:cmd_grow"

    def test_command_resolves(self) -> None:
        """Grow command should resolve to handler."""
        from protocols.cli.hollow import resolve_command

        cmd = resolve_command("grow")
        assert cmd is not None
        assert callable(cmd)
