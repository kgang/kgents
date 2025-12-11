"""Tests for CLICapable protocol."""

from __future__ import annotations

from typing import Callable

import pytest
from protocols.cli.prism import CLICapable


class TestCLICapableProtocol:
    """Tests for CLICapable structural typing."""

    def test_isinstance_detection_valid(self) -> None:
        """CLICapable detection works via isinstance."""

        class ValidAgent:
            @property
            def genus_name(self) -> str:
                return "test"

            @property
            def cli_description(self) -> str:
                return "Test agent"

            def get_exposed_commands(self) -> dict[str, Callable]:
                return {}

        agent = ValidAgent()
        assert isinstance(agent, CLICapable)

    def test_isinstance_detection_missing_genus(self) -> None:
        """Missing genus_name fails isinstance check."""

        class InvalidAgent:
            @property
            def cli_description(self) -> str:
                return "Test agent"

            def get_exposed_commands(self) -> dict[str, Callable]:
                return {}

        agent = InvalidAgent()
        assert not isinstance(agent, CLICapable)

    def test_isinstance_detection_missing_description(self) -> None:
        """Missing cli_description fails isinstance check."""

        class InvalidAgent:
            @property
            def genus_name(self) -> str:
                return "test"

            def get_exposed_commands(self) -> dict[str, Callable]:
                return {}

        agent = InvalidAgent()
        assert not isinstance(agent, CLICapable)

    def test_isinstance_detection_missing_commands(self) -> None:
        """Missing get_exposed_commands fails isinstance check."""

        class InvalidAgent:
            @property
            def genus_name(self) -> str:
                return "test"

            @property
            def cli_description(self) -> str:
                return "Test agent"

        agent = InvalidAgent()
        assert not isinstance(agent, CLICapable)

    def test_genus_name_property(self) -> None:
        """genus_name returns the correct value."""

        class TestAgent:
            @property
            def genus_name(self) -> str:
                return "grammar"

            @property
            def cli_description(self) -> str:
                return "Test"

            def get_exposed_commands(self) -> dict[str, Callable]:
                return {}

        agent = TestAgent()
        assert agent.genus_name == "grammar"

    def test_cli_description_property(self) -> None:
        """cli_description returns the correct value."""

        class TestAgent:
            @property
            def genus_name(self) -> str:
                return "test"

            @property
            def cli_description(self) -> str:
                return "G-gent Grammar/DSL operations"

            def get_exposed_commands(self) -> dict[str, Callable]:
                return {}

        agent = TestAgent()
        assert agent.cli_description == "G-gent Grammar/DSL operations"

    def test_get_exposed_commands_returns_dict(self) -> None:
        """get_exposed_commands returns a command mapping."""

        def cmd_reify():
            pass

        def cmd_parse():
            pass

        class TestAgent:
            @property
            def genus_name(self) -> str:
                return "test"

            @property
            def cli_description(self) -> str:
                return "Test"

            def get_exposed_commands(self) -> dict[str, Callable]:
                return {"reify": cmd_reify, "parse": cmd_parse}

        agent = TestAgent()
        commands = agent.get_exposed_commands()

        assert isinstance(commands, dict)
        assert "reify" in commands
        assert "parse" in commands
        assert commands["reify"] is cmd_reify

    def test_protocol_is_runtime_checkable(self) -> None:
        """CLICapable can be used with isinstance at runtime."""
        # This test verifies the @runtime_checkable decorator is applied

        # If not runtime_checkable, isinstance would raise TypeError
        try:

            class TestClass:
                pass

            isinstance(TestClass(), CLICapable)
        except TypeError:
            pytest.fail("CLICapable should be @runtime_checkable")
