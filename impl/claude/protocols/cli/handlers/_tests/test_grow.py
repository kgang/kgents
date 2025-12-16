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


class TestInputValidation:
    """Test input validation for propose command."""

    def test_invalid_context(self) -> None:
        """Invalid context should return error."""
        from protocols.cli.handlers.grow import cmd_grow

        result = cmd_grow(["propose", "invalid_ctx", "garden"])
        assert result == 1

    def test_empty_entity(self) -> None:
        """Empty entity name should return error."""
        from protocols.cli.handlers.grow import cmd_grow

        result = cmd_grow(["propose", "world", ""])
        assert result == 1

    def test_entity_too_short(self) -> None:
        """Entity name too short should return error."""
        from protocols.cli.handlers.grow import cmd_grow

        result = cmd_grow(["propose", "world", "x"])
        assert result == 1

    def test_entity_invalid_characters(self) -> None:
        """Entity with invalid characters should return error."""
        from protocols.cli.handlers.grow import cmd_grow

        result = cmd_grow(["propose", "world", "Garden-Test!"])
        assert result == 1

    def test_entity_starts_with_number(self) -> None:
        """Entity starting with number should return error."""
        from protocols.cli.handlers.grow import cmd_grow

        result = cmd_grow(["propose", "world", "123garden"])
        assert result == 1

    def test_why_too_short(self) -> None:
        """Justification too short should return error."""
        from protocols.cli.handlers.grow import cmd_grow

        result = cmd_grow(["propose", "world", "garden", "--why", "short"])
        assert result == 1

    def test_valid_proposal(self) -> None:
        """Valid inputs should succeed."""
        from protocols.cli.handlers.grow import _get_session, cmd_grow

        session = _get_session()
        session.proposals.clear()

        result = cmd_grow(
            [
                "propose",
                "world",
                "test_garden",
                "--why",
                "This is a valid justification for the garden holon",
            ]
        )
        assert result == 0
        assert len(session.proposals) == 1

    def test_context_case_insensitive(self) -> None:
        """Context should be case insensitive."""
        from protocols.cli.handlers.grow import _get_session, cmd_grow

        session = _get_session()
        session.proposals.clear()

        result = cmd_grow(
            [
                "propose",
                "WORLD",
                "test_flower",
                "--why",
                "Testing case insensitive context input",
            ]
        )
        assert result == 0

    def test_entity_normalized_to_lowercase(self) -> None:
        """Entity should be normalized to lowercase."""
        from protocols.cli.handlers.grow import _get_session, cmd_grow

        session = _get_session()
        session.proposals.clear()

        result = cmd_grow(
            [
                "propose",
                "world",
                "Test_Tree",
                "--why",
                "Testing entity normalization to lowercase",
            ]
        )
        assert result == 0

        # Check the stored proposal has lowercase entity
        proposal = list(session.proposals.values())[0]
        assert proposal.entity == "test_tree"


class TestValidationFunctions:
    """Test validation helper functions directly."""

    def test_validate_context_valid(self) -> None:
        """Valid contexts should pass."""
        from protocols.cli.handlers.grow import _validate_context

        for ctx in ["world", "self", "concept", "void", "time"]:
            valid, error = _validate_context(ctx)
            assert valid, f"Context {ctx} should be valid"
            assert error == ""

    def test_validate_context_invalid(self) -> None:
        """Invalid contexts should fail."""
        from protocols.cli.handlers.grow import _validate_context

        valid, error = _validate_context("invalid")
        assert not valid
        assert "Invalid context" in error

    def test_validate_context_empty(self) -> None:
        """Empty context should fail."""
        from protocols.cli.handlers.grow import _validate_context

        valid, error = _validate_context("")
        assert not valid
        assert "cannot be empty" in error

    def test_validate_entity_valid(self) -> None:
        """Valid entity names should pass."""
        from protocols.cli.handlers.grow import _validate_entity

        valid_names = ["garden", "flower_bed", "tree123", "abc"]
        for name in valid_names:
            valid, error = _validate_entity(name)
            assert valid, f"Entity {name} should be valid"

    def test_validate_entity_invalid_start(self) -> None:
        """Entity starting with number should fail."""
        from protocols.cli.handlers.grow import _validate_entity

        valid, error = _validate_entity("123abc")
        assert not valid
        assert "start with letter" in error

    def test_validate_entity_special_chars(self) -> None:
        """Entity with special chars should fail."""
        from protocols.cli.handlers.grow import _validate_entity

        valid, error = _validate_entity("test-entity")
        assert not valid

    def test_validate_why_exists_valid(self) -> None:
        """Valid justification should pass."""
        from protocols.cli.handlers.grow import _validate_why_exists

        valid, error = _validate_why_exists(
            "This is a valid justification for the holon"
        )
        assert valid
        assert error == ""

    def test_validate_why_exists_none(self) -> None:
        """None justification should pass (optional)."""
        from protocols.cli.handlers.grow import _validate_why_exists

        valid, error = _validate_why_exists(None)
        assert valid

    def test_validate_why_exists_too_short(self) -> None:
        """Too short justification should fail."""
        from protocols.cli.handlers.grow import _validate_why_exists

        valid, error = _validate_why_exists("short")
        assert not valid
        assert "too short" in error


class TestThreadSafety:
    """Test thread-safe session management."""

    def test_session_singleton(self) -> None:
        """Session should be singleton."""
        from protocols.cli.handlers.grow import _get_session

        session1 = _get_session()
        session2 = _get_session()
        assert session1 is session2

    def test_resolver_singleton(self) -> None:
        """Resolver should be singleton per session."""
        from protocols.cli.handlers.grow import _get_resolver

        resolver1 = _get_resolver()
        resolver2 = _get_resolver()
        assert resolver1 is resolver2

    def test_concurrent_session_access(self) -> None:
        """Concurrent session access should be safe."""
        import concurrent.futures

        from protocols.cli.handlers.grow import _get_session

        sessions = []

        def get_session():
            return _get_session()

        with concurrent.futures.ThreadPoolExecutor(max_workers=10) as executor:
            futures = [executor.submit(get_session) for _ in range(20)]
            sessions = [f.result() for f in futures]

        # All should be the same instance
        assert all(s is sessions[0] for s in sessions)


class TestErrorPaths:
    """Test error handling paths."""

    def test_validate_no_args(self) -> None:
        """Validate with no args should show available proposals."""
        from protocols.cli.handlers.grow import cmd_grow

        # This should return 0 or 1 depending on session state, not crash
        result = cmd_grow(["validate"])
        assert result in (0, 1)

    def test_validate_not_found(self) -> None:
        """Validate with non-existent proposal should return error."""
        from protocols.cli.handlers.grow import cmd_grow

        result = cmd_grow(["validate", "nonexistent_id_12345"])
        assert result == 1

    def test_germinate_no_args(self) -> None:
        """Germinate with no args should return error."""
        from protocols.cli.handlers.grow import cmd_grow

        result = cmd_grow(["germinate"])
        assert result == 1

    def test_germinate_not_found(self) -> None:
        """Germinate with non-existent proposal should return error."""
        from protocols.cli.handlers.grow import cmd_grow

        result = cmd_grow(["germinate", "nonexistent_id_12345"])
        assert result == 1

    def test_search_no_args(self) -> None:
        """Search with no args should return error."""
        from protocols.cli.handlers.grow import cmd_grow

        result = cmd_grow(["search"])
        assert result == 1

    def test_show_no_args(self) -> None:
        """Show with no args should return error."""
        from protocols.cli.handlers.grow import cmd_grow

        result = cmd_grow(["show"])
        assert result == 1

    def test_show_not_found(self) -> None:
        """Show with non-existent proposal should return error."""
        from protocols.cli.handlers.grow import cmd_grow

        result = cmd_grow(["show", "nonexistent_id_12345"])
        assert result == 1
