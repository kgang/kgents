"""
Tests for ProjectorArtisan.

Tests React component generation with both LLM-powered and template modes.
"""

from __future__ import annotations

import tempfile
from pathlib import Path
from unittest.mock import AsyncMock, MagicMock

import pytest

from ..artisans.architect import AgentDesign
from ..artisans.projector import (
    ProjectorArtisan,
    ProjectorOutput,
    _derive_component_name,
    _derive_hook_name,
    _generate_hooks_template,
    _generate_index_template,
    _generate_visualization_template,
)
from ..commission import Commission, CommissionStatus

# === ProjectorOutput Tests ===


class TestProjectorOutput:
    """Tests for the ProjectorOutput dataclass."""

    def test_to_dict_includes_file_list(self) -> None:
        """Test to_dict includes file information."""
        output = ProjectorOutput(
            artifact_path="/tmp/test/web",
            files={
                "index.ts": "export {}",
                "CounterVisualization.tsx": "// component",
                "useCounterQuery.ts": "// hooks",
            },
            summary="Generated 3 files",
        )

        data = output.to_dict()

        assert data["path"] == "/tmp/test/web"
        assert data["file_count"] == 3
        assert "index.ts" in data["files"]
        assert "CounterVisualization.tsx" in data["files"]
        assert "useCounterQuery.ts" in data["files"]


# === Name Derivation Tests ===


class TestNameDerivation:
    """Tests for component and hook name derivation."""

    @pytest.fixture
    def design(self) -> AgentDesign:
        """Create a test design."""
        return AgentDesign(
            name="CounterAgent",
            description="A counter",
            states=["IDLE"],
            initial_state="IDLE",
            transitions={},
            operations=[],
            laws=[],
            rationale="Test",
        )

    def test_derive_component_name(self, design: AgentDesign) -> None:
        """Test component name derivation."""
        name = _derive_component_name(design)
        assert name == "CounterVisualization"

    def test_derive_hook_name(self, design: AgentDesign) -> None:
        """Test hook name derivation."""
        name = _derive_hook_name(design)
        assert name == "useCounterQuery"

    def test_derive_names_without_agent_suffix(self) -> None:
        """Test names derivation without Agent suffix."""
        design = AgentDesign(
            name="Preferences",
            description="Prefs",
            states=["IDLE"],
            initial_state="IDLE",
            transitions={},
            operations=[],
            laws=[],
            rationale="Test",
        )

        comp_name = _derive_component_name(design)
        hook_name = _derive_hook_name(design)

        assert comp_name == "PreferencesVisualization"
        assert hook_name == "usePreferencesQuery"


# === Template Generation Tests ===


class TestIndexTemplateGeneration:
    """Tests for index.ts template generation."""

    @pytest.fixture
    def design(self) -> AgentDesign:
        """Create a test design."""
        return AgentDesign(
            name="CounterAgent",
            description="A counter",
            states=["IDLE"],
            initial_state="IDLE",
            transitions={},
            operations=[],
            laws=[],
            rationale="Test",
        )

    def test_index_exports_component(self, design: AgentDesign) -> None:
        """Test that index exports the visualization component."""
        template = _generate_index_template(design)

        assert "export { CounterVisualization }" in template

    def test_index_exports_hook(self, design: AgentDesign) -> None:
        """Test that index exports the query hook."""
        template = _generate_index_template(design)

        assert "export { useCounterQuery }" in template


class TestVisualizationTemplateGeneration:
    """Tests for visualization component template generation."""

    @pytest.fixture
    def design(self) -> AgentDesign:
        """Create a test design."""
        return AgentDesign(
            name="CounterAgent",
            description="A counter that counts",
            states=["IDLE", "COUNTING"],
            initial_state="IDLE",
            transitions={"IDLE": ["COUNTING"], "COUNTING": ["IDLE"]},
            operations=[
                {"name": "increment", "description": "Add one"},
                {"name": "decrement", "description": "Subtract one"},
            ],
            laws=[],
            rationale="Test",
        )

    def test_visualization_has_component_function(self, design: AgentDesign) -> None:
        """Test that template has React function component."""
        template = _generate_visualization_template(design, "world.counter")

        assert "export function CounterVisualization" in template

    def test_visualization_has_props_interface(self, design: AgentDesign) -> None:
        """Test that template has props interface."""
        template = _generate_visualization_template(design, "world.counter")

        assert "interface CounterVisualizationProps" in template
        assert "density: Density" in template

    def test_visualization_uses_hook(self, design: AgentDesign) -> None:
        """Test that visualization uses the query hook."""
        template = _generate_visualization_template(design, "world.counter")

        assert "useCounterQuery" in template

    def test_visualization_has_state_sections(self, design: AgentDesign) -> None:
        """Test that visualization has sections for each state."""
        template = _generate_visualization_template(design, "world.counter")

        assert "'idle'" in template.lower()
        assert "'counting'" in template.lower()

    def test_visualization_has_operation_buttons(self, design: AgentDesign) -> None:
        """Test that visualization has buttons for operations."""
        template = _generate_visualization_template(design, "world.counter")

        assert "Increment" in template
        assert "Decrement" in template


class TestHooksTemplateGeneration:
    """Tests for hooks template generation."""

    @pytest.fixture
    def design(self) -> AgentDesign:
        """Create a test design."""
        return AgentDesign(
            name="CounterAgent",
            description="A counter",
            states=["IDLE"],
            initial_state="IDLE",
            transitions={},
            operations=[
                {"name": "increment", "description": "Add one"},
                {"name": "get_count", "description": "Get current count"},
            ],
            laws=[],
            rationale="Test",
        )

    def test_hooks_has_manifest_hook(self, design: AgentDesign) -> None:
        """Test that hooks template has manifest query hook."""
        template = _generate_hooks_template(design, "world.counter")

        assert "export function useCounterQuery" in template

    def test_hooks_has_operation_hooks(self, design: AgentDesign) -> None:
        """Test that hooks template has hooks for operations."""
        template = _generate_hooks_template(design, "world.counter")

        assert "export function useIncrement" in template
        assert "export function useGetCount" in template

    def test_hooks_has_types(self, design: AgentDesign) -> None:
        """Test that hooks template has TypeScript types."""
        template = _generate_hooks_template(design, "world.counter")

        assert "interface IncrementRequest" in template
        assert "interface IncrementResponse" in template
        assert "interface CounterManifestResponse" in template

    def test_hooks_has_agentese_path(self, design: AgentDesign) -> None:
        """Test that hooks template references correct AGENTESE path."""
        template = _generate_hooks_template(design, "world.counter")

        assert "world.counter.manifest" in template
        assert "world.counter.increment" in template


# === ProjectorArtisan Tests ===


class TestProjectorArtisan:
    """Tests for the ProjectorArtisan."""

    @pytest.fixture
    def commission(self) -> Commission:
        """Create a test commission."""
        return Commission(
            id="test-projector-001",
            intent="Build a simple counter agent",
            name="CounterAgent",
            status=CommissionStatus.PROJECTING,
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
        }

    @pytest.fixture
    def herald_output(self) -> dict:
        """Create test herald output."""
        return {
            "files": ["node.py", "contracts_ext.py"],
            "registered_path": "world.counter",
            "summary": "Generated AGENTESE node",
        }

    @pytest.fixture
    def temp_output_dir(self) -> Path:
        """Create a temporary output directory."""
        with tempfile.TemporaryDirectory() as tmpdir:
            yield Path(tmpdir)

    def test_init_without_soul(self) -> None:
        """Test creating projector without K-gent soul."""
        projector = ProjectorArtisan(soul=None)
        assert projector.soul is None

    def test_init_with_custom_output_dir(self, temp_output_dir: Path) -> None:
        """Test creating projector with custom output directory."""
        projector = ProjectorArtisan(soul=None, output_dir=temp_output_dir)
        assert projector._output_dir == temp_output_dir

    @pytest.mark.asyncio
    async def test_project_template_mode(
        self,
        commission: Commission,
        design: AgentDesign,
        service_output: dict,
        herald_output: dict,
        temp_output_dir: Path,
    ) -> None:
        """Test project in template mode (no soul)."""
        projector = ProjectorArtisan(soul=None, output_dir=temp_output_dir)

        output = await projector.project(commission, design, service_output, herald_output)

        assert output.status == "complete"
        assert output.artisan.value == "projector"
        assert output.output is not None
        assert output.output["file_count"] == 3
        assert output.annotation is not None

    @pytest.mark.asyncio
    async def test_project_creates_files(
        self,
        commission: Commission,
        design: AgentDesign,
        service_output: dict,
        herald_output: dict,
        temp_output_dir: Path,
    ) -> None:
        """Test that project actually creates files on disk."""
        projector = ProjectorArtisan(soul=None, output_dir=temp_output_dir)

        output = await projector.project(commission, design, service_output, herald_output)

        # Check files were created
        artifact_path = Path(output.output["path"])
        assert artifact_path.exists()
        assert (artifact_path / "index.ts").exists()
        assert (artifact_path / "CounterVisualization.tsx").exists()
        assert (artifact_path / "useCounterQuery.ts").exists()

    @pytest.mark.asyncio
    async def test_project_files_contain_code(
        self,
        commission: Commission,
        design: AgentDesign,
        service_output: dict,
        herald_output: dict,
        temp_output_dir: Path,
    ) -> None:
        """Test that generated files contain valid TypeScript/React code."""
        projector = ProjectorArtisan(soul=None, output_dir=temp_output_dir)

        output = await projector.project(commission, design, service_output, herald_output)
        artifact_path = Path(output.output["path"])

        # Check index exports
        index_content = (artifact_path / "index.ts").read_text()
        assert "export" in index_content

        # Check visualization has component
        vis_content = (artifact_path / "CounterVisualization.tsx").read_text()
        assert "function CounterVisualization" in vis_content
        assert "useState" in vis_content or "useCallback" in vis_content

        # Check hooks has types and functions
        hooks_content = (artifact_path / "useCounterQuery.ts").read_text()
        assert "interface" in hooks_content
        assert "function" in hooks_content

    @pytest.mark.asyncio
    async def test_project_accepts_dict_design(
        self,
        commission: Commission,
        design: AgentDesign,
        service_output: dict,
        herald_output: dict,
        temp_output_dir: Path,
    ) -> None:
        """Test that project accepts design as dict."""
        projector = ProjectorArtisan(soul=None, output_dir=temp_output_dir)

        output = await projector.project(
            commission, design.to_dict(), service_output, herald_output
        )

        assert output.status == "complete"
        assert output.output["file_count"] == 3

    @pytest.mark.asyncio
    async def test_project_with_mock_soul(
        self,
        commission: Commission,
        design: AgentDesign,
        service_output: dict,
        herald_output: dict,
        temp_output_dir: Path,
    ) -> None:
        """Test project with mocked K-gent soul."""
        # Create mock soul with valid JSON response
        mock_soul = MagicMock()
        mock_response = MagicMock()
        mock_response.response = """
        {
            "files": {
                "index.ts": "export {}",
                "Visualization.tsx": "// component",
                "hooks.ts": "// hooks"
            },
            "summary": "Generated by LLM"
        }
        """
        mock_soul.dialogue = AsyncMock(return_value=mock_response)

        projector = ProjectorArtisan(soul=mock_soul, output_dir=temp_output_dir)
        output = await projector.project(commission, design, service_output, herald_output)

        assert output.status == "complete"
        mock_soul.dialogue.assert_called_once()

    @pytest.mark.asyncio
    async def test_project_fallback_on_bad_llm_response(
        self,
        commission: Commission,
        design: AgentDesign,
        service_output: dict,
        herald_output: dict,
        temp_output_dir: Path,
    ) -> None:
        """Test that project falls back to templates on bad LLM response."""
        # Create mock soul with invalid response
        mock_soul = MagicMock()
        mock_response = MagicMock()
        mock_response.response = "This is not valid JSON"
        mock_soul.dialogue = AsyncMock(return_value=mock_response)

        projector = ProjectorArtisan(soul=mock_soul, output_dir=temp_output_dir)
        output = await projector.project(commission, design, service_output, herald_output)

        # Should still succeed via template fallback
        assert output.status == "complete"
        assert output.output["file_count"] == 3


# === Integration Tests ===


class TestProjectorIntegration:
    """Integration tests for Projector in the commission pipeline."""

    @pytest.fixture
    def commission(self) -> Commission:
        """Create a test commission."""
        return Commission(
            id="test-projector-integration",
            intent="Build a preferences agent",
            name="PreferencesAgent",
            status=CommissionStatus.PROJECTING,
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
            laws=["Idempotence: set >> set = set"],
            rationale="User preferences management",
        )

    @pytest.fixture
    def temp_output_dir(self) -> Path:
        """Create a temporary output directory."""
        with tempfile.TemporaryDirectory() as tmpdir:
            yield Path(tmpdir)

    @pytest.mark.asyncio
    async def test_full_project_pipeline(
        self,
        commission: Commission,
        design: AgentDesign,
        temp_output_dir: Path,
    ) -> None:
        """Test the full project pipeline generates valid output."""
        projector = ProjectorArtisan(soul=None, output_dir=temp_output_dir)
        service_output = {"path": "/tmp/test", "files": ["service.py"]}
        herald_output = {
            "files": ["node.py", "contracts_ext.py"],
            "registered_path": "world.preferences",
            "summary": "Generated node",
        }

        output = await projector.project(commission, design, service_output, herald_output)

        assert output.status == "complete"
        assert output.artisan.value == "projector"

        # Output should have file info
        assert "PreferencesVisualization.tsx" in output.output["files"]
        assert "usePreferencesQuery.ts" in output.output["files"]
        assert "index.ts" in output.output["files"]
