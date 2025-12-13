"""Tests for agent scaffolding (kgents new agent)."""

from __future__ import annotations

import shutil
from collections.abc import Generator
from pathlib import Path

import pytest

# Skip all tests if jinja2 is not available
pytest.importorskip("jinja2")

from protocols.cli.intent.commands import IntentResult, _create_agent


class TestCreateAgent:
    """Tests for _create_agent function."""

    @pytest.fixture
    def cleanup_agent(self) -> Generator[None, None, None]:
        """Fixture to clean up generated agent after test."""
        yield
        # Clean up any test agents
        agents_dir = Path(__file__).parent.parent.parent.parent.parent / "agents"
        for test_dir in [
            "test_scaffolding_agent",
            "test_full_agent",
            "test_minimal_agent",
        ]:
            agent_dir = agents_dir / test_dir
            if agent_dir.exists():
                shutil.rmtree(agent_dir)

    def test_create_agent_basic(self, cleanup_agent: None) -> None:
        """_create_agent creates agent with default template."""
        result = _create_agent(
            name="test-scaffolding-agent",
            genus=None,
            template="default",
            path=Path("."),
        )

        assert result.success
        assert result.output is not None
        assert result.output["slug"] == "test_scaffolding_agent"
        assert result.output["class_name"] == "TestScaffoldingAgent"
        assert result.output["archetype"] == "Lambda"
        assert (
            len(result.output["files"]) == 4
        )  # __init__, agent, test __init__, test_agent

        # Verify files were created
        agents_dir = Path(__file__).parent.parent.parent.parent.parent / "agents"
        agent_dir = agents_dir / "test_scaffolding_agent"
        assert agent_dir.exists()
        assert (agent_dir / "__init__.py").exists()
        assert (agent_dir / "agent.py").exists()
        assert (agent_dir / "_tests" / "__init__.py").exists()
        assert (agent_dir / "_tests" / "test_agent.py").exists()

    def test_create_agent_full_template(self, cleanup_agent: None) -> None:
        """_create_agent with 'full' template creates Kappa archetype."""
        result = _create_agent(
            name="test-full-agent",
            genus=None,
            template="full",
            path=Path("."),
        )

        assert result.success
        assert result.output["archetype"] == "Kappa"

    def test_create_agent_minimal_template(self, cleanup_agent: None) -> None:
        """_create_agent with 'minimal' template creates Lambda archetype."""
        result = _create_agent(
            name="test-minimal-agent",
            genus=None,
            template="minimal",
            path=Path("."),
        )

        assert result.success
        assert result.output["archetype"] == "Lambda"

    def test_create_agent_directory_exists(self, cleanup_agent: None) -> None:
        """_create_agent fails if directory already exists."""
        # Create first
        result1 = _create_agent(
            name="test-scaffolding-agent",
            genus=None,
            template="default",
            path=Path("."),
        )
        assert result1.success

        # Try to create again
        result2 = _create_agent(
            name="test-scaffolding-agent",
            genus=None,
            template="default",
            path=Path("."),
        )
        assert not result2.success
        assert result2.error is not None
        assert "already exists" in result2.error.lower()

    def test_create_agent_name_normalization(self, cleanup_agent: None) -> None:
        """_create_agent normalizes kebab-case to snake_case."""
        result = _create_agent(
            name="test-scaffolding-agent",
            genus=None,
            template="default",
            path=Path("."),
        )

        assert result.success
        assert result.output["slug"] == "test_scaffolding_agent"
        assert result.output["class_name"] == "TestScaffoldingAgent"

    def test_create_agent_next_steps(self, cleanup_agent: None) -> None:
        """_create_agent provides helpful next steps."""
        result = _create_agent(
            name="test-scaffolding-agent",
            genus=None,
            template="default",
            path=Path("."),
        )

        assert result.success
        assert len(result.next_steps) >= 2
        # Should mention editing and testing
        steps_text = " ".join(result.next_steps).lower()
        assert "agent.py" in steps_text or "implement" in steps_text
        assert "pytest" in steps_text or "test" in steps_text


class TestGeneratedAgent:
    """Tests for generated agent structure."""

    @pytest.fixture
    def generated_agent(self) -> Generator[Path, None, None]:
        """Create a test agent and return its path."""
        result = _create_agent(
            name="test-generated-agent",
            genus=None,
            template="default",
            path=Path("."),
        )
        assert result.success

        agents_dir = Path(__file__).parent.parent.parent.parent.parent / "agents"
        agent_dir = agents_dir / "test_generated_agent"

        yield agent_dir

        # Cleanup
        if agent_dir.exists():
            shutil.rmtree(agent_dir)

    def test_generated_agent_imports(self, generated_agent: Path) -> None:
        """Generated agent can be imported."""
        # Read and check __init__.py
        init_content = (generated_agent / "__init__.py").read_text()
        assert "TestGeneratedAgent" in init_content
        assert "__all__" in init_content

    def test_generated_agent_structure(self, generated_agent: Path) -> None:
        """Generated agent has correct structure."""
        agent_content = (generated_agent / "agent.py").read_text()
        assert "class TestGeneratedAgent" in agent_content
        assert "Lambda" in agent_content
        assert "async def invoke" in agent_content
        assert "NotImplementedError" in agent_content

    def test_generated_tests_structure(self, generated_agent: Path) -> None:
        """Generated tests have correct structure."""
        test_content = (generated_agent / "_tests" / "test_agent.py").read_text()
        assert "TestTestGeneratedAgent" in test_content
        assert "@pytest.mark.asyncio" in test_content
        assert "test_agent_name" in test_content
        assert "test_invoke_raises_not_implemented" in test_content
