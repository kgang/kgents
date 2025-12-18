"""
Tests for AGENTESE Prompt Context (concept.prompt.*).

Wave 6 of the Evergreen Prompt System.

Tests:
- PromptNode creation and properties
- concept.prompt.manifest
- concept.prompt.evolve
- concept.prompt.validate
- concept.prompt.compile
- concept.prompt.history
- concept.prompt.rollback
- concept.prompt.diff

See: plans/_continuations/evergreen-wave6-living-cli-continuation.md
"""

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime
from pathlib import Path
from typing import Any

import pytest

# Import the context module
from protocols.agentese.contexts.prompt import (
    PROMPT_ROLE_AFFORDANCES,
    CheckpointSummaryDTO,
    DiffResult,
    EvolutionResult,
    PromptContextResolver,
    PromptNode,
    ValidationResult,
    create_prompt_node,
    create_prompt_resolver,
)

# === Mock Umwelt for Testing ===


@dataclass
class MockDNA:
    """Mock DNA for testing."""

    name: str = "test-agent"


@dataclass
class MockUmwelt:
    """Mock Umwelt for testing."""

    dna: MockDNA
    archetype: str = "developer"

    def __init__(self, archetype: str = "developer") -> None:
        self.dna = MockDNA(name=f"test-{archetype}")
        self.archetype = archetype


class TestPromptRoleAffordances:
    """Tests for role-based affordances."""

    def test_developer_affordances(self) -> None:
        """Developer role has full affordances."""
        affordances = PROMPT_ROLE_AFFORDANCES["developer"]

        assert "manifest" in affordances
        assert "evolve" in affordances
        assert "compile" in affordances
        assert "history" in affordances
        assert "rollback" in affordances
        assert "diff" in affordances
        assert "validate" in affordances

    def test_architect_affordances(self) -> None:
        """Architect role has appropriate affordances."""
        affordances = PROMPT_ROLE_AFFORDANCES["architect"]

        assert "manifest" in affordances
        assert "evolve" in affordances
        assert "validate" in affordances

    def test_reviewer_affordances(self) -> None:
        """Reviewer role has limited affordances."""
        affordances = PROMPT_ROLE_AFFORDANCES["reviewer"]

        assert "manifest" in affordances
        assert "diff" in affordances
        assert "history" in affordances
        # Reviewer shouldn't have write operations
        assert "evolve" not in affordances
        assert "compile" not in affordances

    def test_default_affordances(self) -> None:
        """Default role has minimal affordances."""
        affordances = PROMPT_ROLE_AFFORDANCES["default"]

        assert "manifest" in affordances
        assert "history" in affordances


class TestResultTypes:
    """Tests for result data classes."""

    def test_evolution_result_creation(self) -> None:
        """EvolutionResult creates correctly."""
        result = EvolutionResult(
            success=True,
            original_content="original",
            improved_content="improved",
            sections_modified=("systems",),
            reasoning_trace=("step 1", "step 2"),
            checkpoint_id="abc123",
            message="Success",
        )

        assert result.success is True
        assert result.original_content == "original"
        assert result.improved_content == "improved"
        assert result.sections_modified == ("systems",)
        assert len(result.reasoning_trace) == 2
        assert result.checkpoint_id == "abc123"

    def test_validation_result_creation(self) -> None:
        """ValidationResult creates correctly."""
        result = ValidationResult(
            valid=True,
            law_checks=(("identity_law", True), ("determinism", True)),
            warnings=("minor warning",),
            errors=(),
        )

        assert result.valid is True
        assert len(result.law_checks) == 2
        assert result.law_checks[0] == ("identity_law", True)
        assert len(result.warnings) == 1
        assert len(result.errors) == 0

    def test_diff_result_creation(self) -> None:
        """DiffResult creates correctly."""
        result = DiffResult(
            id1="abc123",
            id2="def456",
            diff_content="+added\n-removed",
            lines_added=1,
            lines_removed=1,
        )

        assert result.id1 == "abc123"
        assert result.id2 == "def456"
        assert "+added" in result.diff_content
        assert result.lines_added == 1
        assert result.lines_removed == 1

    def test_checkpoint_summary_dto_creation(self) -> None:
        """CheckpointSummaryDTO creates correctly."""
        now = datetime.now()
        dto = CheckpointSummaryDTO(
            id="abc123",
            timestamp=now,
            reason="Test checkpoint",
            sections_before=("a", "b"),
            sections_after=("a", "b", "c"),
            content_length_before=100,
            content_length_after=150,
        )

        assert dto.id == "abc123"
        assert dto.timestamp == now
        assert dto.reason == "Test checkpoint"
        assert len(dto.sections_before) == 2
        assert len(dto.sections_after) == 3


class TestPromptNode:
    """Tests for PromptNode class."""

    def test_prompt_node_creation(self) -> None:
        """PromptNode creates with correct handle."""
        node = PromptNode()

        assert node.handle == "concept.prompt"

    def test_prompt_node_with_project_root(self) -> None:
        """PromptNode accepts project_root."""
        node = PromptNode(_project_root=Path("/test/path"))

        assert node._project_root == Path("/test/path")

    def test_prompt_node_affordances_developer(self) -> None:
        """Developer gets full affordances."""
        node = PromptNode()
        affordances = node._get_affordances_for_archetype("developer")

        assert "manifest" in affordances
        assert "evolve" in affordances
        assert "validate" in affordances

    def test_prompt_node_affordances_default(self) -> None:
        """Unknown role gets default affordances."""
        node = PromptNode()
        affordances = node._get_affordances_for_archetype("unknown_role")

        assert "manifest" in affordances
        assert "history" in affordances

    def test_content_to_sections_helper(self) -> None:
        """_content_to_sections parses markdown correctly."""
        node = PromptNode()

        content = """\
# Title

## Section A

Content A.

## Section B

Content B.
"""
        sections = node._content_to_sections(content)

        assert "Section A" in sections
        assert "Section B" in sections
        assert "Content A" in sections["Section A"]
        assert "Content B" in sections["Section B"]


class TestPromptContextResolver:
    """Tests for PromptContextResolver class."""

    def test_resolver_creation(self) -> None:
        """Resolver creates correctly."""
        resolver = PromptContextResolver()

        assert resolver is not None
        assert resolver._cache == {}

    def test_resolver_with_project_root(self) -> None:
        """Resolver accepts project_root."""
        resolver = PromptContextResolver(project_root=Path("/test"))

        assert resolver.project_root == Path("/test")

    def test_resolver_resolve_prompt(self) -> None:
        """Resolver resolves concept.prompt to PromptNode."""
        resolver = PromptContextResolver()
        node = resolver.resolve("prompt", [])

        assert isinstance(node, PromptNode)
        assert node.handle == "concept.prompt"

    def test_resolver_caching(self) -> None:
        """Resolver caches resolved nodes."""
        resolver = PromptContextResolver()

        node1 = resolver.resolve("prompt", [])
        node2 = resolver.resolve("prompt", [])

        # Should be same cached instance
        assert node1 is node2

    def test_resolver_unknown_path(self) -> None:
        """Resolver handles unknown paths gracefully."""
        resolver = PromptContextResolver()
        node = resolver.resolve("unknown", [])

        # Should return a PromptNode with modified handle
        assert isinstance(node, PromptNode)


class TestFactoryFunctions:
    """Tests for factory functions."""

    def test_create_prompt_node(self) -> None:
        """create_prompt_node creates correct node."""
        node = create_prompt_node()

        assert isinstance(node, PromptNode)
        assert node.handle == "concept.prompt"

    def test_create_prompt_node_with_root(self) -> None:
        """create_prompt_node accepts project_root."""
        node = create_prompt_node(project_root=Path("/custom"))

        assert node._project_root == Path("/custom")

    def test_create_prompt_resolver(self) -> None:
        """create_prompt_resolver creates correct resolver."""
        resolver = create_prompt_resolver()

        assert isinstance(resolver, PromptContextResolver)

    def test_create_prompt_resolver_with_root(self) -> None:
        """create_prompt_resolver accepts project_root."""
        resolver = create_prompt_resolver(project_root=Path("/custom"))

        assert resolver.project_root == Path("/custom")


class TestPromptNodeAspects:
    """Tests for PromptNode aspect invocation."""

    @pytest.fixture
    def node(self) -> PromptNode:
        """Create a PromptNode for testing."""
        return PromptNode()

    @pytest.fixture
    def observer(self) -> MockUmwelt:
        """Create a mock observer for testing."""
        return MockUmwelt(archetype="developer")

    @pytest.mark.asyncio
    async def test_evolve_no_feedback(self, node: PromptNode, observer: MockUmwelt) -> None:
        """Evolve without feedback returns error."""
        result = await node._evolve(observer, feedback="")

        assert isinstance(result, EvolutionResult)
        assert result.success is False
        assert "Feedback required" in result.message

    @pytest.mark.asyncio
    async def test_validate_returns_result(self, node: PromptNode, observer: MockUmwelt) -> None:
        """Validate returns ValidationResult."""
        result = await node._validate(observer)

        assert isinstance(result, ValidationResult)
        assert isinstance(result.valid, bool)
        assert isinstance(result.law_checks, tuple)

    @pytest.mark.asyncio
    async def test_history_returns_list(self, node: PromptNode, observer: MockUmwelt) -> None:
        """History returns list of summaries."""
        result = await node._history(observer, limit=5)

        assert isinstance(result, list)
        # May be empty if no history exists

    @pytest.mark.asyncio
    async def test_rollback_no_id(self, node: PromptNode, observer: MockUmwelt) -> None:
        """Rollback without ID returns error."""
        result = await node._rollback(observer, checkpoint_id="")

        assert isinstance(result, dict)
        assert result["success"] is False
        assert "required" in result["error"].lower()

    @pytest.mark.asyncio
    async def test_diff_no_ids(self, node: PromptNode, observer: MockUmwelt) -> None:
        """Diff without IDs returns error."""
        result = await node._diff(observer, id1="", id2="")

        assert isinstance(result, dict)
        assert "error" in result

    @pytest.mark.asyncio
    async def test_compile_returns_dict(self, node: PromptNode, observer: MockUmwelt) -> None:
        """Compile returns result dict."""
        result = await node._compile(
            observer,
            checkpoint=False,
            reason="Test compilation",
        )

        assert isinstance(result, dict)
        assert "success" in result

    @pytest.mark.asyncio
    async def test_invoke_aspect_unknown(self, node: PromptNode, observer: MockUmwelt) -> None:
        """Unknown aspect returns not implemented."""
        result = await node._invoke_aspect("unknown_aspect", observer)

        assert isinstance(result, dict)
        assert result["status"] == "not implemented"


class TestPromptNodeManifest:
    """Tests for manifest aspect."""

    @pytest.fixture
    def node(self) -> PromptNode:
        """Create a PromptNode for testing."""
        # Use actual project root for integration
        project_root = Path(__file__).parent.parent.parent.parent.parent.parent
        return PromptNode(_project_root=project_root)

    @pytest.mark.asyncio
    async def test_manifest_developer_view(self, node: PromptNode) -> None:
        """Developer manifest shows full content."""
        observer = MockUmwelt(archetype="developer")

        # Mock the _umwelt_to_meta method
        class MockMeta:
            archetype = "developer"

        node._umwelt_to_meta = lambda x: MockMeta()

        result = await node.manifest(observer)

        # Should return a Renderable
        assert hasattr(result, "summary") or hasattr(result, "content")

    @pytest.mark.asyncio
    async def test_manifest_architect_view(self, node: PromptNode) -> None:
        """Architect manifest shows structure."""
        observer = MockUmwelt(archetype="architect")

        class MockMeta:
            archetype = "architect"

        node._umwelt_to_meta = lambda x: MockMeta()

        result = await node.manifest(observer)

        assert hasattr(result, "summary") or hasattr(result, "content")


class TestEvolutionIntegration:
    """Integration tests for evolution workflow."""

    @pytest.fixture
    def node(self) -> PromptNode:
        """Create a PromptNode for testing."""
        project_root = Path(__file__).parent.parent.parent.parent.parent.parent
        return PromptNode(_project_root=project_root)

    @pytest.mark.asyncio
    async def test_evolution_with_feedback(self, node: PromptNode) -> None:
        """Evolution with feedback produces result."""
        observer = MockUmwelt(archetype="developer")

        result = await node._evolve(
            observer,
            feedback="be more concise",
            learning_rate=0.5,
        )

        assert isinstance(result, EvolutionResult)
        # May or may not succeed depending on CLAUDE.md presence
        assert isinstance(result.success, bool)
        assert isinstance(result.reasoning_trace, tuple)


class TestContextExports:
    """Tests for context module exports."""

    def test_all_exports_available(self) -> None:
        """All expected exports are available from contexts module."""
        from protocols.agentese.contexts import (
            PROMPT_ROLE_AFFORDANCES,
            CheckpointSummaryDTO,
            DiffResult,
            EvolutionResult,
            PromptContextResolver,
            PromptNode,
            ValidationResult,
            create_prompt_node,
            create_prompt_resolver,
        )

        # Verify all exports are the expected types
        assert isinstance(PROMPT_ROLE_AFFORDANCES, dict)
        assert callable(create_prompt_node)
        assert callable(create_prompt_resolver)
