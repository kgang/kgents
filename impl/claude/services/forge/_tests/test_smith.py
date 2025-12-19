"""
Tests for SmithArtisan.

Tests code generation with both LLM-powered and template modes.
"""

from __future__ import annotations

import os
import tempfile
from pathlib import Path
from unittest.mock import AsyncMock, MagicMock

import pytest

from ..artisans.architect import AgentDesign
from ..artisans.smith import SmithArtisan, SmithOutput
from ..commission import Commission, CommissionStatus

# === SmithOutput Tests ===


class TestSmithOutput:
    """Tests for the SmithOutput dataclass."""

    def test_to_dict_includes_file_list(self) -> None:
        """Test to_dict includes file information."""
        output = SmithOutput(
            artifact_path="/tmp/test",
            files={
                "__init__.py": "# init",
                "service.py": "# service",
                "polynomial.py": "# poly",
            },
            summary="Generated 3 files",
        )

        data = output.to_dict()

        assert data["path"] == "/tmp/test"
        assert data["file_count"] == 3
        assert "__init__.py" in data["files"]
        assert "service.py" in data["files"]
        assert "polynomial.py" in data["files"]


# === SmithArtisan Tests ===


class TestSmithArtisan:
    """Tests for the SmithArtisan."""

    @pytest.fixture
    def commission(self) -> Commission:
        """Create a test commission."""
        return Commission(
            id="test-smith-001",
            intent="Build a simple counter agent",
            name="CounterAgent",
            status=CommissionStatus.IMPLEMENTING,
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
            laws=[
                "Identity: counter >> identity = counter",
                "Commutativity: increment >> decrement = decrement >> increment",
            ],
            rationale="Simple state machine for counting operations",
        )

    @pytest.fixture
    def temp_output_dir(self) -> Path:
        """Create a temporary output directory."""
        with tempfile.TemporaryDirectory() as tmpdir:
            yield Path(tmpdir)

    def test_init_without_soul(self) -> None:
        """Test creating smith without K-gent soul."""
        smith = SmithArtisan(soul=None)
        assert smith.soul is None

    def test_init_with_custom_output_dir(self, temp_output_dir: Path) -> None:
        """Test creating smith with custom output directory."""
        smith = SmithArtisan(soul=None, output_dir=temp_output_dir)
        assert smith._output_dir == temp_output_dir

    @pytest.mark.asyncio
    async def test_implement_template_mode(
        self,
        commission: Commission,
        design: AgentDesign,
        temp_output_dir: Path,
    ) -> None:
        """Test implementation in template mode (no soul)."""
        smith = SmithArtisan(soul=None, output_dir=temp_output_dir)

        output = await smith.implement(commission, design)

        assert output.status == "complete"
        assert output.artisan.value == "smith"
        assert output.output is not None
        assert output.output["file_count"] == 3
        assert output.annotation is not None

    @pytest.mark.asyncio
    async def test_implement_creates_files(
        self,
        commission: Commission,
        design: AgentDesign,
        temp_output_dir: Path,
    ) -> None:
        """Test that implementation actually creates files on disk."""
        smith = SmithArtisan(soul=None, output_dir=temp_output_dir)

        output = await smith.implement(commission, design)

        # Check files were created
        artifact_path = Path(output.output["path"])
        assert artifact_path.exists()
        assert (artifact_path / "__init__.py").exists()
        assert (artifact_path / "service.py").exists()
        assert (artifact_path / "polynomial.py").exists()

    @pytest.mark.asyncio
    async def test_implement_files_contain_code(
        self,
        commission: Commission,
        design: AgentDesign,
        temp_output_dir: Path,
    ) -> None:
        """Test that generated files contain valid Python code."""
        smith = SmithArtisan(soul=None, output_dir=temp_output_dir)

        output = await smith.implement(commission, design)
        artifact_path = Path(output.output["path"])

        # Check init exports
        init_content = (artifact_path / "__init__.py").read_text()
        assert "CounterService" in init_content or "Counter" in init_content

        # Check polynomial has state enum
        poly_content = (artifact_path / "polynomial.py").read_text()
        assert "Enum" in poly_content
        assert "IDLE" in poly_content
        assert "COUNTING" in poly_content

        # Check service has class
        service_content = (artifact_path / "service.py").read_text()
        assert "class" in service_content
        assert "def" in service_content

    @pytest.mark.asyncio
    async def test_implement_accepts_dict_design(
        self,
        commission: Commission,
        design: AgentDesign,
        temp_output_dir: Path,
    ) -> None:
        """Test that implement accepts design as dict."""
        smith = SmithArtisan(soul=None, output_dir=temp_output_dir)

        # Pass design as dict (as it comes from architect output)
        output = await smith.implement(commission, design.to_dict())

        assert output.status == "complete"
        assert output.output["file_count"] == 3

    @pytest.mark.asyncio
    async def test_implement_with_mock_soul(
        self,
        commission: Commission,
        design: AgentDesign,
        temp_output_dir: Path,
    ) -> None:
        """Test implementation with mocked K-gent soul."""
        mock_soul = MagicMock()
        mock_dialogue_output = MagicMock()
        mock_dialogue_output.response = """{
            "files": {
                "__init__.py": "# LLM generated init\\nfrom .service import CounterService",
                "polynomial.py": "# LLM generated polynomial\\nfrom enum import Enum",
                "service.py": "# LLM generated service\\nclass CounterService:\\n    pass"
            },
            "summary": "Generated by LLM"
        }"""
        mock_soul.dialogue = AsyncMock(return_value=mock_dialogue_output)

        smith = SmithArtisan(soul=mock_soul, output_dir=temp_output_dir)
        output = await smith.implement(commission, design)

        assert output.status == "complete"
        assert output.output is not None

    @pytest.mark.asyncio
    async def test_implement_fallback_on_bad_llm_response(
        self,
        commission: Commission,
        design: AgentDesign,
        temp_output_dir: Path,
    ) -> None:
        """Test that bad LLM response falls back to templates."""
        mock_soul = MagicMock()
        mock_dialogue_output = MagicMock()
        mock_dialogue_output.response = "This is not valid JSON"
        mock_soul.dialogue = AsyncMock(return_value=mock_dialogue_output)

        smith = SmithArtisan(soul=mock_soul, output_dir=temp_output_dir)
        output = await smith.implement(commission, design)

        # Should fall back to templates and succeed
        assert output.status == "complete"
        assert output.output["file_count"] == 3

    @pytest.mark.asyncio
    async def test_implement_sets_timestamps(
        self,
        commission: Commission,
        design: AgentDesign,
        temp_output_dir: Path,
    ) -> None:
        """Test that implement sets started_at and completed_at."""
        smith = SmithArtisan(soul=None, output_dir=temp_output_dir)

        output = await smith.implement(commission, design)

        assert output.started_at is not None
        assert output.completed_at is not None
        assert output.completed_at >= output.started_at

    @pytest.mark.asyncio
    async def test_implement_uses_commission_id_for_path(
        self,
        commission: Commission,
        design: AgentDesign,
        temp_output_dir: Path,
    ) -> None:
        """Test that artifact path includes commission ID."""
        smith = SmithArtisan(soul=None, output_dir=temp_output_dir)

        output = await smith.implement(commission, design)

        assert commission.id in output.output["path"]


# === Template Generation Tests ===


class TestTemplateGeneration:
    """Tests for the code template generation functions."""

    @pytest.fixture
    def design(self) -> AgentDesign:
        """Create a test design."""
        return AgentDesign(
            name="TemplateTestAgent",
            description="Agent for template testing",
            states=["STATE_A", "STATE_B", "STATE_C"],
            initial_state="STATE_A",
            transitions={
                "STATE_A": ["STATE_B"],
                "STATE_B": ["STATE_A", "STATE_C"],
                "STATE_C": [],
            },
            operations=[
                {"name": "op1", "input": "str", "output": "bool", "description": "Op 1"},
                {"name": "op2", "input": "int", "output": "str", "description": "Op 2"},
            ],
            laws=["Identity law", "Composition law"],
            rationale="Testing templates",
        )

    def test_polynomial_template_has_enum(self, design: AgentDesign) -> None:
        """Test polynomial template generates state enum."""
        from ..artisans.smith import _generate_polynomial_template

        code = _generate_polynomial_template(design)

        assert "class TemplateTestAgentState" in code
        assert "STATE_A" in code
        assert "STATE_B" in code
        assert "STATE_C" in code
        assert "Enum" in code

    def test_polynomial_template_has_transitions(self, design: AgentDesign) -> None:
        """Test polynomial template includes transition map."""
        from ..artisans.smith import _generate_polynomial_template

        code = _generate_polynomial_template(design)

        assert "TEMPLATETESTAGENT_TRANSITIONS" in code
        assert "can_transition" in code
        assert "transition" in code

    def test_service_template_has_operations(self, design: AgentDesign) -> None:
        """Test service template includes operation methods."""
        from ..artisans.smith import _generate_service_template

        code = _generate_service_template(design)

        assert "class TemplateTestService" in code
        assert "def op1" in code
        assert "def op2" in code
        assert "async" in code  # Operations should be async

    def test_service_template_includes_rationale(self, design: AgentDesign) -> None:
        """Test service template includes design rationale."""
        from ..artisans.smith import _generate_service_template

        code = _generate_service_template(design)

        assert design.rationale in code

    def test_init_template_exports(self, design: AgentDesign) -> None:
        """Test init template exports service and polynomial."""
        from ..artisans.smith import _generate_init_template

        code = _generate_init_template(design)

        assert "from .service import" in code
        assert "from .polynomial import" in code
        assert "__all__" in code


# === Integration Tests ===


class TestSmithIntegration:
    """Integration tests for Smith in commission flow."""

    @pytest.mark.asyncio
    async def test_full_generation_pipeline(self) -> None:
        """Test complete generation from design to files."""
        with tempfile.TemporaryDirectory() as tmpdir:
            commission = Commission(
                id="integration-smith-001",
                intent="Manage todo items with add, complete, and delete operations",
                name="TodoManager",
                status=CommissionStatus.IMPLEMENTING,
            )

            design = AgentDesign(
                name="TodoManager",
                description="Manages a list of todo items",
                states=["EMPTY", "HAS_ITEMS", "ALL_COMPLETE"],
                initial_state="EMPTY",
                transitions={
                    "EMPTY": ["HAS_ITEMS"],
                    "HAS_ITEMS": ["EMPTY", "ALL_COMPLETE"],
                    "ALL_COMPLETE": ["HAS_ITEMS"],
                },
                operations=[
                    {"name": "add", "input": "str", "output": "TodoItem"},
                    {"name": "complete", "input": "str", "output": "bool"},
                    {"name": "delete", "input": "str", "output": "bool"},
                    {"name": "list_all", "input": "void", "output": "list[TodoItem]"},
                ],
                laws=[
                    "add >> delete(same_id) = identity",
                    "complete >> complete = complete",
                ],
                rationale="State tracks emptiness and completion status",
            )

            smith = SmithArtisan(soul=None, output_dir=Path(tmpdir))
            output = await smith.implement(commission, design)

            # Verify success
            assert output.status == "complete"
            assert output.output["file_count"] == 3

            # Verify files are syntactically valid Python
            artifact_path = Path(output.output["path"])

            for filename in ["__init__.py", "polynomial.py", "service.py"]:
                filepath = artifact_path / filename
                assert filepath.exists(), f"{filename} should exist"

                content = filepath.read_text()
                # Try to compile the Python code
                try:
                    compile(content, filename, "exec")
                except SyntaxError as e:
                    pytest.fail(f"{filename} has syntax error: {e}")
