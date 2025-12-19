"""
Tests for HeraldArtisan.

Tests AGENTESE node generation with both LLM-powered and template modes.
"""

from __future__ import annotations

from unittest.mock import AsyncMock, MagicMock

import pytest

from ..artisans.architect import AgentDesign
from ..artisans.herald import (
    HeraldArtisan,
    HeraldOutput,
    _derive_agentese_path,
    _generate_contracts_template,
    _generate_node_template,
)
from ..commission import Commission, CommissionStatus

# === HeraldOutput Tests ===


class TestHeraldOutput:
    """Tests for the HeraldOutput dataclass."""

    def test_to_dict_includes_file_list(self) -> None:
        """Test to_dict includes file information."""
        output = HeraldOutput(
            files={
                "node.py": "# node",
                "contracts_ext.py": "# contracts",
            },
            registered_path="world.counter",
            summary="Generated 2 files",
        )

        data = output.to_dict()

        assert data["file_count"] == 2
        assert "node.py" in data["files"]
        assert "contracts_ext.py" in data["files"]
        assert data["registered_path"] == "world.counter"

    def test_to_dict_preserves_path(self) -> None:
        """Test that registered_path is preserved in to_dict."""
        output = HeraldOutput(
            files={},
            registered_path="world.myagent",
            summary="Test",
        )

        assert output.to_dict()["registered_path"] == "world.myagent"


# === Path Derivation Tests ===


class TestPathDerivation:
    """Tests for AGENTESE path derivation."""

    def test_derive_path_from_agent_name(self) -> None:
        """Test deriving path from agent name."""
        design = AgentDesign(
            name="CounterAgent",
            description="A counter",
            states=["IDLE"],
            initial_state="IDLE",
            transitions={},
            operations=[],
            laws=[],
            rationale="Test",
        )

        path = _derive_agentese_path(design)

        assert path == "world.counter"

    def test_derive_path_removes_agent_suffix(self) -> None:
        """Test that Agent suffix is removed."""
        design = AgentDesign(
            name="TodoManagerAgent",
            description="A todo manager",
            states=["IDLE"],
            initial_state="IDLE",
            transitions={},
            operations=[],
            laws=[],
            rationale="Test",
        )

        path = _derive_agentese_path(design)

        assert path == "world.todomanager"
        assert "agent" not in path.lower()

    def test_derive_path_handles_simple_name(self) -> None:
        """Test path derivation with simple name (no Agent suffix)."""
        design = AgentDesign(
            name="Preferences",
            description="Preferences manager",
            states=["IDLE"],
            initial_state="IDLE",
            transitions={},
            operations=[],
            laws=[],
            rationale="Test",
        )

        path = _derive_agentese_path(design)

        assert path == "world.preferences"


# === Template Generation Tests ===


class TestNodeTemplateGeneration:
    """Tests for node.py template generation."""

    @pytest.fixture
    def design(self) -> AgentDesign:
        """Create a test agent design."""
        return AgentDesign(
            name="CounterAgent",
            description="A counter that can increment and decrement",
            states=["IDLE", "COUNTING"],
            initial_state="IDLE",
            transitions={
                "IDLE": ["COUNTING"],
                "COUNTING": ["IDLE"],
            },
            operations=[
                {
                    "name": "increment",
                    "input": "void",
                    "output": "int",
                    "description": "Add one to the counter",
                },
                {
                    "name": "decrement",
                    "input": "void",
                    "output": "int",
                    "description": "Subtract one from the counter",
                },
            ],
            laws=["Identity: counter >> identity = counter"],
            rationale="Simple state machine for counting operations",
        )

    def test_node_template_has_decorator(self, design: AgentDesign) -> None:
        """Test that generated node has @node decorator."""
        template = _generate_node_template(design, "world.counter")

        assert "@node(" in template
        assert '"world.counter"' in template

    def test_node_template_has_contracts(self, design: AgentDesign) -> None:
        """Test that generated node has contracts dict."""
        template = _generate_node_template(design, "world.counter")

        assert "contracts={" in template
        assert '"manifest"' in template
        assert '"increment"' in template
        assert '"decrement"' in template

    def test_node_template_has_aspect_routing(self, design: AgentDesign) -> None:
        """Test that generated node has _invoke_aspect method."""
        template = _generate_node_template(design, "world.counter")

        assert "async def _invoke_aspect" in template
        assert 'aspect == "manifest"' in template
        assert 'aspect == "increment"' in template

    def test_node_template_has_rendering_class(self, design: AgentDesign) -> None:
        """Test that generated node has rendering class."""
        template = _generate_node_template(design, "world.counter")

        assert "class CounterManifestRendering" in template
        assert "def to_dict" in template
        assert "def to_text" in template

    def test_node_template_has_method_stubs(self, design: AgentDesign) -> None:
        """Test that generated node has method stubs for operations."""
        template = _generate_node_template(design, "world.counter")

        assert "async def _increment" in template
        assert "async def _decrement" in template
        assert "AGENTESE: world.counter.increment" in template


class TestContractsTemplateGeneration:
    """Tests for contracts_ext.py template generation."""

    @pytest.fixture
    def design(self) -> AgentDesign:
        """Create a test agent design."""
        return AgentDesign(
            name="CounterAgent",
            description="A counter",
            states=["IDLE"],
            initial_state="IDLE",
            transitions={},
            operations=[
                {
                    "name": "increment",
                    "input": "int",
                    "output": "int",
                    "description": "Add value",
                },
            ],
            laws=[],
            rationale="Test",
        )

    def test_contracts_template_has_manifest_response(self, design: AgentDesign) -> None:
        """Test that contracts has manifest response type."""
        template = _generate_contracts_template(design)

        assert "class CounterManifestResponse" in template
        assert "@dataclass" in template

    def test_contracts_template_has_operation_types(self, design: AgentDesign) -> None:
        """Test that contracts has request/response for operations."""
        template = _generate_contracts_template(design)

        assert "class IncrementRequest" in template
        assert "class IncrementResponse" in template


# === HeraldArtisan Tests ===


class TestHeraldArtisan:
    """Tests for the HeraldArtisan."""

    @pytest.fixture
    def commission(self) -> Commission:
        """Create a test commission."""
        return Commission(
            id="test-herald-001",
            intent="Build a simple counter agent",
            name="CounterAgent",
            status=CommissionStatus.EXPOSING,
        )

    @pytest.fixture
    def design(self) -> AgentDesign:
        """Create a test agent design."""
        return AgentDesign(
            name="CounterAgent",
            description="A counter that can increment and decrement",
            states=["IDLE", "COUNTING"],
            initial_state="IDLE",
            transitions={
                "IDLE": ["COUNTING"],
                "COUNTING": ["IDLE"],
            },
            operations=[
                {
                    "name": "increment",
                    "input": "void",
                    "output": "int",
                    "description": "Add one to the counter",
                },
                {
                    "name": "decrement",
                    "input": "void",
                    "output": "int",
                    "description": "Subtract one from the counter",
                },
            ],
            laws=["Identity: counter >> identity = counter"],
            rationale="Simple state machine for counting operations",
        )

    @pytest.fixture
    def service_output(self) -> dict:
        """Create test service output."""
        return {
            "path": "/tmp/test-service",
            "files": ["__init__.py", "service.py", "polynomial.py"],
            "file_count": 3,
        }

    def test_init_without_soul(self) -> None:
        """Test creating herald without K-gent soul."""
        herald = HeraldArtisan(soul=None)
        assert herald.soul is None

    @pytest.mark.asyncio
    async def test_expose_template_mode(
        self,
        commission: Commission,
        design: AgentDesign,
        service_output: dict,
    ) -> None:
        """Test expose in template mode (no soul)."""
        herald = HeraldArtisan(soul=None)

        output = await herald.expose(commission, design, service_output)

        assert output.status == "complete"
        assert output.artisan.value == "herald"
        assert output.output is not None
        assert output.output["file_count"] == 2
        assert output.output["registered_path"] == "world.counter"

    @pytest.mark.asyncio
    async def test_expose_accepts_dict_design(
        self,
        commission: Commission,
        design: AgentDesign,
        service_output: dict,
    ) -> None:
        """Test that expose accepts design as dict."""
        herald = HeraldArtisan(soul=None)

        output = await herald.expose(commission, design.to_dict(), service_output)

        assert output.status == "complete"
        assert output.output["file_count"] == 2

    @pytest.mark.asyncio
    async def test_expose_annotation_includes_path(
        self,
        commission: Commission,
        design: AgentDesign,
        service_output: dict,
    ) -> None:
        """Test that output annotation mentions the AGENTESE path."""
        herald = HeraldArtisan(soul=None)

        output = await herald.expose(commission, design, service_output)

        assert "world.counter" in output.annotation

    @pytest.mark.asyncio
    async def test_expose_with_mock_soul(
        self,
        commission: Commission,
        design: AgentDesign,
        service_output: dict,
    ) -> None:
        """Test expose with mocked K-gent soul."""
        # Create mock soul with valid JSON response
        mock_soul = MagicMock()
        mock_response = MagicMock()
        mock_response.response = """
        {
            "files": {
                "node.py": "# Generated node",
                "contracts_ext.py": "# Generated contracts"
            },
            "registered_path": "world.counter",
            "summary": "Generated by LLM"
        }
        """
        mock_soul.dialogue = AsyncMock(return_value=mock_response)

        herald = HeraldArtisan(soul=mock_soul)
        output = await herald.expose(commission, design, service_output)

        assert output.status == "complete"
        mock_soul.dialogue.assert_called_once()

    @pytest.mark.asyncio
    async def test_expose_fallback_on_bad_llm_response(
        self,
        commission: Commission,
        design: AgentDesign,
        service_output: dict,
    ) -> None:
        """Test that expose falls back to templates on bad LLM response."""
        # Create mock soul with invalid response
        mock_soul = MagicMock()
        mock_response = MagicMock()
        mock_response.response = "This is not valid JSON"
        mock_soul.dialogue = AsyncMock(return_value=mock_response)

        herald = HeraldArtisan(soul=mock_soul)
        output = await herald.expose(commission, design, service_output)

        # Should still succeed via template fallback
        assert output.status == "complete"
        assert output.output["file_count"] == 2


# === Integration Tests ===


class TestHeraldIntegration:
    """Integration tests for Herald in the commission pipeline."""

    @pytest.fixture
    def commission(self) -> Commission:
        """Create a test commission."""
        return Commission(
            id="test-herald-integration",
            intent="Build a preferences agent",
            name="PreferencesAgent",
            status=CommissionStatus.EXPOSING,
        )

    @pytest.fixture
    def design(self) -> AgentDesign:
        """Create a test agent design."""
        return AgentDesign(
            name="PreferencesAgent",
            description="Manages user preferences",
            states=["IDLE", "LOADING", "READY"],
            initial_state="IDLE",
            transitions={
                "IDLE": ["LOADING"],
                "LOADING": ["READY", "IDLE"],
                "READY": ["IDLE"],
            },
            operations=[
                {
                    "name": "get_preference",
                    "input": "str",
                    "output": "Any",
                    "description": "Get a preference value",
                },
                {
                    "name": "set_preference",
                    "input": "tuple[str, Any]",
                    "output": "bool",
                    "description": "Set a preference value",
                },
            ],
            laws=["Idempotence: set >> set = set", "Get after set: set >> get = value"],
            rationale="User preferences management with caching",
        )

    @pytest.mark.asyncio
    async def test_full_expose_pipeline(
        self,
        commission: Commission,
        design: AgentDesign,
    ) -> None:
        """Test the full expose pipeline generates valid output."""
        herald = HeraldArtisan(soul=None)
        service_output = {"path": "/tmp/test", "files": ["service.py"]}

        output = await herald.expose(commission, design, service_output)

        assert output.status == "complete"
        assert output.artisan.value == "herald"
        assert output.output["registered_path"] == "world.preferences"

        # Output should have file info
        assert "node.py" in output.output["files"]
        assert "contracts_ext.py" in output.output["files"]
