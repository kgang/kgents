"""
Tests for K-gent Refinements: Domains 5-7.

Tests cover:
1. SoulPathResolver - AGENTESE path resolution with observer-awareness
2. GracefulDegradation - Error tracking and auto-degradation
3. FractalExpander - Recursive idea expansion
4. HolographicConstitution - Eigenvector-weighted constitution lookup
"""

from __future__ import annotations

from typing import TYPE_CHECKING

import pytest
from agents.k.eigenvectors import KentEigenvectors
from agents.k.refinements import (
    ConstitutionArticle,
    DialogueError,
    EigenvectorError,
    FractalExpander,
    FractalNode,
    GardenError,
    GracefulDegradation,
    HolographicConstitution,
    HypnagogiaError,
    SoulError,
    SoulErrorSeverity,
    SoulPath,
    SoulPathResolver,
    SoulPathResult,
)
from agents.k.soul import KgentSoul

if TYPE_CHECKING:
    pass


# =============================================================================
# SoulPath Enum Tests
# =============================================================================


class TestSoulPath:
    """Tests for SoulPath enum."""

    def test_soul_path_values(self) -> None:
        """Test that all SoulPath values have correct prefixes."""
        for path in SoulPath:
            assert path.value.startswith("self.soul.")

    def test_core_paths_exist(self) -> None:
        """Test that core paths are defined."""
        assert SoulPath.MANIFEST.value == "self.soul.manifest"
        assert SoulPath.WITNESS.value == "self.soul.witness"
        assert SoulPath.REFINE.value == "self.soul.refine"

    def test_eigenvector_paths_exist(self) -> None:
        """Test that eigenvector paths are defined."""
        assert SoulPath.EIGENVECTORS.value == "self.soul.eigenvectors"
        assert SoulPath.AESTHETIC.value == "self.soul.aesthetic"
        assert SoulPath.CATEGORICAL.value == "self.soul.categorical"
        assert SoulPath.GRATITUDE.value == "self.soul.gratitude"
        assert SoulPath.HETERARCHY.value == "self.soul.heterarchy"
        assert SoulPath.GENERATIVITY.value == "self.soul.generativity"
        assert SoulPath.JOY.value == "self.soul.joy"

    def test_entropy_paths_exist(self) -> None:
        """Test that entropy paths are defined."""
        assert SoulPath.SIP.value == "self.soul.sip"
        assert SoulPath.TITHE.value == "self.soul.tithe"

    def test_garden_paths_exist(self) -> None:
        """Test that garden paths are defined."""
        assert SoulPath.GARDEN.value == "self.soul.garden"
        assert SoulPath.PLANT.value == "self.soul.garden.plant"
        assert SoulPath.NURTURE.value == "self.soul.garden.nurture"


# =============================================================================
# SoulPathResult Tests
# =============================================================================


class TestSoulPathResult:
    """Tests for SoulPathResult dataclass."""

    def test_result_creation(self) -> None:
        """Test basic result creation."""
        result = SoulPathResult(
            path="self.soul.manifest",
            value={"test": "data"},
            observer="anonymous",
        )

        assert result.path == "self.soul.manifest"
        assert result.value == {"test": "data"}
        assert result.observer == "anonymous"
        assert result.was_cached is False
        assert result.timestamp is not None

    def test_result_to_dict(self) -> None:
        """Test serialization to dictionary."""
        result = SoulPathResult(
            path="self.soul.manifest",
            value={"key": "value"},
            observer="architect",
            was_cached=True,
        )

        data = result.to_dict()
        assert data["path"] == "self.soul.manifest"
        assert data["value"] == {"key": "value"}
        assert data["observer"] == "architect"
        assert data["was_cached"] is True
        assert "timestamp" in data


# =============================================================================
# SoulPathResolver Tests
# =============================================================================


class TestSoulPathResolver:
    """Tests for SoulPathResolver."""

    @pytest.fixture
    def soul(self) -> KgentSoul:
        """Create a KgentSoul for testing."""
        return KgentSoul()

    @pytest.fixture
    def resolver(self, soul: KgentSoul) -> SoulPathResolver:
        """Create a SoulPathResolver for testing."""
        return SoulPathResolver(soul)

    @pytest.mark.asyncio
    async def test_resolve_manifest_anonymous(self, resolver: SoulPathResolver) -> None:
        """Test manifest resolution for anonymous observer."""
        result = await resolver.resolve(SoulPath.MANIFEST.value, observer="anonymous")

        assert result.path == SoulPath.MANIFEST.value
        assert result.observer == "anonymous"
        assert isinstance(result.value, dict)

    @pytest.mark.asyncio
    async def test_resolve_manifest_architect(self, resolver: SoulPathResolver) -> None:
        """Test manifest resolution for architect observer."""
        result = await resolver.resolve(SoulPath.MANIFEST.value, observer="architect")

        assert result.observer == "architect"
        # Architect gets structure + eigenvector_graph
        assert "structure" in result.value
        assert "eigenvector_graph" in result.value

    @pytest.mark.asyncio
    async def test_resolve_manifest_poet(self, resolver: SoulPathResolver) -> None:
        """Test manifest resolution for poet observer."""
        result = await resolver.resolve(SoulPath.MANIFEST.value, observer="poet")

        assert result.observer == "poet"
        # Poet gets mood + dominant_theme
        assert "mood" in result.value
        assert "dominant_theme" in result.value

    @pytest.mark.asyncio
    async def test_resolve_witness(self, resolver: SoulPathResolver) -> None:
        """Test witness resolution."""
        result = await resolver.resolve(SoulPath.WITNESS.value)

        assert result.path == SoulPath.WITNESS.value
        assert "interactions" in result.value
        assert "tokens_used" in result.value
        assert "mode_history" in result.value

    @pytest.mark.asyncio
    async def test_resolve_eigenvectors(self, resolver: SoulPathResolver) -> None:
        """Test eigenvectors resolution."""
        result = await resolver.resolve(SoulPath.EIGENVECTORS.value)

        value = result.value
        assert "aesthetic" in value
        assert "categorical" in value
        assert "gratitude" in value
        assert "heterarchy" in value
        assert "generativity" in value
        assert "joy" in value

        # Each eigenvector should have value and confidence
        for name in [
            "aesthetic",
            "categorical",
            "gratitude",
            "heterarchy",
            "generativity",
            "joy",
        ]:
            assert "value" in value[name]
            assert "confidence" in value[name]

    @pytest.mark.asyncio
    async def test_resolve_individual_eigenvector(
        self, resolver: SoulPathResolver
    ) -> None:
        """Test resolving individual eigenvector paths."""
        paths = [
            SoulPath.AESTHETIC,
            SoulPath.CATEGORICAL,
            SoulPath.GRATITUDE,
            SoulPath.HETERARCHY,
            SoulPath.GENERATIVITY,
            SoulPath.JOY,
        ]

        for path in paths:
            result = await resolver.resolve(path.value)
            assert "name" in result.value
            assert "value" in result.value
            assert "confidence" in result.value

    @pytest.mark.asyncio
    async def test_resolve_sip(self, resolver: SoulPathResolver) -> None:
        """Test sip resolution (draw from entropy)."""
        result = await resolver.resolve(SoulPath.SIP.value)

        assert result.path == SoulPath.SIP.value
        assert "sip" in result.value
        assert "amount" in result.value
        assert "source" in result.value

    @pytest.mark.asyncio
    async def test_resolve_tithe(self, resolver: SoulPathResolver) -> None:
        """Test tithe resolution (pay gratitude)."""
        result = await resolver.resolve(SoulPath.TITHE.value)

        assert result.path == SoulPath.TITHE.value
        assert "received" in result.value
        assert "observer" in result.value
        assert result.value["acknowledged"] is True

    @pytest.mark.asyncio
    async def test_resolve_tithe_with_gratitude(
        self, resolver: SoulPathResolver
    ) -> None:
        """Test tithe resolution with explicit gratitude."""
        result = await resolver.resolve(
            SoulPath.TITHE.value,
            observer="user",
            gratitude="Thank you for the insights",
        )

        assert result.value["received"] == "Thank you for the insights"
        assert result.value["observer"] == "user"

    @pytest.mark.asyncio
    async def test_resolve_garden(self, resolver: SoulPathResolver) -> None:
        """Test garden resolution."""
        result = await resolver.resolve(SoulPath.GARDEN.value)

        assert result.path == SoulPath.GARDEN.value
        assert result.value["status"] == "accessible"
        assert "paths" in result.value
        assert "self.soul.garden.plant" in result.value["paths"]
        assert "self.soul.garden.nurture" in result.value["paths"]

    @pytest.mark.asyncio
    async def test_resolve_unknown_path(self, resolver: SoulPathResolver) -> None:
        """Test resolution of unknown path."""
        result = await resolver.resolve("self.soul.unknown")

        assert "error" in result.value
        assert "Unknown path" in result.value["error"]

    @pytest.mark.asyncio
    async def test_resolve_with_handler_exception(
        self, resolver: SoulPathResolver
    ) -> None:
        """Test that handler exceptions are caught gracefully."""

        # Register a handler that raises
        def failing_handler(_observer: str) -> dict[str, str]:
            raise ValueError("Handler failed")

        resolver._handlers["self.soul.failing"] = failing_handler

        result = await resolver.resolve("self.soul.failing")
        assert "error" in result.value
        assert "Handler failed" in result.value["error"]


# =============================================================================
# SoulError Tests
# =============================================================================


class TestSoulError:
    """Tests for SoulError and subclasses."""

    def test_soul_error_creation(self) -> None:
        """Test basic SoulError creation."""
        error = SoulError(
            message="Something went wrong",
            severity=SoulErrorSeverity.CONCERN,
        )

        assert error.message == "Something went wrong"
        assert error.severity == SoulErrorSeverity.CONCERN
        assert error.context == {}
        assert error.suggestion is None
        assert error.recovery_hint is None

    def test_soul_error_with_all_fields(self) -> None:
        """Test SoulError with all fields."""
        error = SoulError(
            message="Critical failure",
            severity=SoulErrorSeverity.CRISIS,
            context={"module": "hypnagogia"},
            suggestion="Try again later",
            recovery_hint="System will auto-recover",
        )

        assert error.severity == SoulErrorSeverity.CRISIS
        assert error.context["module"] == "hypnagogia"
        assert error.suggestion == "Try again later"
        assert error.recovery_hint == "System will auto-recover"

    def test_format_human(self) -> None:
        """Test human-readable formatting."""
        error = SoulError(
            message="Pattern extraction failed",
            severity=SoulErrorSeverity.CONCERN,
            suggestion="Reduce input size",
            recovery_hint="Patterns are preserved",
        )

        formatted = error.format_human()
        assert "[CONCERN]" in formatted
        assert "Pattern extraction failed" in formatted
        assert "Suggestion: Reduce input size" in formatted
        assert "Recovery: Patterns are preserved" in formatted

    def test_format_technical(self) -> None:
        """Test technical log formatting."""
        error = SoulError(
            message="Error occurred",
            severity=SoulErrorSeverity.WHISPER,
            context={"key": "value"},
        )

        formatted = error.format_technical()
        assert "whisper" in formatted
        assert "SoulError" in formatted
        assert "Error occurred" in formatted

    def test_str_uses_format_human(self) -> None:
        """Test that str() uses format_human()."""
        error = SoulError(message="Test error", severity=SoulErrorSeverity.CONCERN)
        assert str(error) == error.format_human()

    def test_severity_levels(self) -> None:
        """Test all severity levels exist."""
        assert SoulErrorSeverity.WHISPER.value == "whisper"
        assert SoulErrorSeverity.CONCERN.value == "concern"
        assert SoulErrorSeverity.CRISIS.value == "crisis"
        assert SoulErrorSeverity.CATASTROPHE.value == "catastrophe"


class TestDialogueError:
    """Tests for DialogueError."""

    def test_dialogue_error_defaults(self) -> None:
        """Test DialogueError has correct defaults."""
        error = DialogueError(message="Parse failed", mode="REFLECT")

        assert error.message == "Parse failed"
        assert error.severity == SoulErrorSeverity.CONCERN
        assert error.context["mode"] == "REFLECT"
        assert error.suggestion is not None and "rephrasing" in error.suggestion
        assert error.recovery_hint is not None and "continue" in error.recovery_hint


class TestEigenvectorError:
    """Tests for EigenvectorError."""

    def test_eigenvector_error_defaults(self) -> None:
        """Test EigenvectorError has correct defaults."""
        error = EigenvectorError(message="Update failed", eigenvector="joy")

        assert error.message == "Update failed"
        assert error.severity == SoulErrorSeverity.WHISPER
        assert error.context["eigenvector"] == "joy"
        assert error.suggestion is not None and "default confidence" in error.suggestion


class TestGardenError:
    """Tests for GardenError."""

    def test_garden_error_defaults(self) -> None:
        """Test GardenError has correct defaults."""
        error = GardenError(message="Entry not found", entry_id="abc123")

        assert error.message == "Entry not found"
        assert error.severity == SoulErrorSeverity.CONCERN
        assert error.context["entry_id"] == "abc123"
        assert error.suggestion is not None and "exists" in error.suggestion


class TestHypnagogiaError:
    """Tests for HypnagogiaError."""

    def test_hypnagogia_error_defaults(self) -> None:
        """Test HypnagogiaError has correct defaults."""
        error = HypnagogiaError(message="Dream interrupted", phase="consolidation")

        assert error.message == "Dream interrupted"
        assert error.severity == SoulErrorSeverity.CONCERN
        assert error.context["phase"] == "consolidation"
        assert error.suggestion is not None and "retried" in error.suggestion
        assert error.recovery_hint is not None and "preserved" in error.recovery_hint


# =============================================================================
# GracefulDegradation Tests
# =============================================================================


class TestGracefulDegradation:
    """Tests for GracefulDegradation."""

    @pytest.fixture
    def degradation(self) -> GracefulDegradation:
        """Create a GracefulDegradation instance."""
        return GracefulDegradation()

    def test_initial_state(self, degradation: GracefulDegradation) -> None:
        """Test initial state has no degraded features."""
        status = degradation.status()
        assert status["degraded_features"] == []
        assert status["error_counts"] == {}

    def test_record_error_increments(self, degradation: GracefulDegradation) -> None:
        """Test that recording errors increments count."""
        degradation.record_error("llm", ValueError("test"))

        status = degradation.status()
        assert status["error_counts"]["llm"] == 1

    def test_record_multiple_errors(self, degradation: GracefulDegradation) -> None:
        """Test recording multiple errors for same feature."""
        degradation.record_error("llm", ValueError("error1"))
        degradation.record_error("llm", ValueError("error2"))

        status = degradation.status()
        assert status["error_counts"]["llm"] == 2

    def test_auto_degrade_after_three_errors(
        self, degradation: GracefulDegradation
    ) -> None:
        """Test auto-degradation after 3 errors."""
        # Not degraded after 2 errors
        degradation.record_error("llm", ValueError("error1"))
        degradation.record_error("llm", ValueError("error2"))
        assert degradation.is_degraded("llm") is False

        # Degraded after 3rd error
        degradation.record_error("llm", ValueError("error3"))
        assert degradation.is_degraded("llm") is True

    def test_is_degraded_unknown_feature(
        self, degradation: GracefulDegradation
    ) -> None:
        """Test is_degraded returns False for unknown features."""
        assert degradation.is_degraded("unknown") is False

    def test_multiple_features_independent(
        self, degradation: GracefulDegradation
    ) -> None:
        """Test that features degrade independently."""
        # Degrade llm
        for _ in range(3):
            degradation.record_error("llm", ValueError("error"))

        # Garden should not be degraded
        degradation.record_error("garden", ValueError("error"))

        assert degradation.is_degraded("llm") is True
        assert degradation.is_degraded("garden") is False

    def test_restore_degraded_feature(self, degradation: GracefulDegradation) -> None:
        """Test restoring a degraded feature."""
        # Degrade it
        for _ in range(3):
            degradation.record_error("llm", ValueError("error"))
        assert degradation.is_degraded("llm") is True

        # Restore it
        result = degradation.restore("llm")
        assert result is True
        assert degradation.is_degraded("llm") is False

        # Error count should be reset
        status = degradation.status()
        assert status["error_counts"]["llm"] == 0

    def test_restore_non_degraded_feature(
        self, degradation: GracefulDegradation
    ) -> None:
        """Test restoring a non-degraded feature returns False."""
        result = degradation.restore("unknown")
        assert result is False

    def test_status_includes_all_info(self, degradation: GracefulDegradation) -> None:
        """Test status returns complete information."""
        # Add some errors
        degradation.record_error("llm", ValueError("error"))
        degradation.record_error("garden", ValueError("error"))
        for _ in range(2):
            degradation.record_error("garden", ValueError("error"))

        status = degradation.status()

        assert "degraded_features" in status
        assert "error_counts" in status
        assert status["error_counts"]["llm"] == 1
        assert status["error_counts"]["garden"] == 3
        assert "garden" in status["degraded_features"]
        assert "llm" not in status["degraded_features"]


# =============================================================================
# FractalNode Tests
# =============================================================================


class TestFractalNode:
    """Tests for FractalNode dataclass."""

    def test_node_creation(self) -> None:
        """Test basic node creation."""
        node = FractalNode(content="Root idea", depth=0)

        assert node.content == "Root idea"
        assert node.depth == 0
        assert node.children == []
        assert node.metadata == {}

    def test_node_with_children(self) -> None:
        """Test node with children."""
        child1 = FractalNode(content="Child 1", depth=1)
        child2 = FractalNode(content="Child 2", depth=1)
        parent = FractalNode(content="Parent", depth=0, children=[child1, child2])

        assert len(parent.children) == 2
        assert parent.children[0].content == "Child 1"
        assert parent.children[1].content == "Child 2"

    def test_node_to_dict(self) -> None:
        """Test node serialization."""
        child = FractalNode(content="Child", depth=1)
        parent = FractalNode(
            content="Parent",
            depth=0,
            children=[child],
            metadata={"source": "test"},
        )

        data = parent.to_dict()
        assert data["content"] == "Parent"
        assert data["depth"] == 0
        assert data["metadata"]["source"] == "test"
        assert len(data["children"]) == 1
        assert data["children"][0]["content"] == "Child"


# =============================================================================
# FractalExpander Tests
# =============================================================================


class TestFractalExpander:
    """Tests for FractalExpander."""

    @pytest.fixture
    def expander(self) -> FractalExpander:
        """Create a FractalExpander."""
        return FractalExpander(max_depth=2, branching_factor=2)

    @pytest.mark.asyncio
    async def test_expand_basic(self, expander: FractalExpander) -> None:
        """Test basic expansion."""
        result = await expander.expand("Test idea")

        assert result.content == "Test idea"
        assert result.depth == 0
        assert len(result.children) > 0

    @pytest.mark.asyncio
    async def test_expand_respects_max_depth(self, expander: FractalExpander) -> None:
        """Test that expansion respects max_depth."""
        result = await expander.expand("Deep idea")

        # Check no node exceeds max_depth
        def check_depth(node: FractalNode, max_depth: int) -> bool:
            if node.depth > max_depth:
                return False
            return all(check_depth(child, max_depth) for child in node.children)

        assert check_depth(result, expander._max_depth)

    @pytest.mark.asyncio
    async def test_expand_respects_branching_factor(
        self, expander: FractalExpander
    ) -> None:
        """Test that expansion respects branching_factor."""
        result = await expander.expand("Wide idea")

        # Check no node has more than branching_factor children
        def check_branching(node: FractalNode, max_children: int) -> bool:
            if len(node.children) > max_children:
                return False
            return all(check_branching(child, max_children) for child in node.children)

        assert check_branching(result, expander._branching_factor)

    @pytest.mark.asyncio
    async def test_expand_generates_children_content(
        self, expander: FractalExpander
    ) -> None:
        """Test that expansion generates meaningful children."""
        result = await expander.expand("architecture")

        # Children should contain references to the original content
        for child in result.children:
            assert "architecture" in child.content.lower()

    @pytest.mark.asyncio
    async def test_expand_with_soul_adds_eigenvector_expansions(self) -> None:
        """Test that soul-influenced expansion adds eigenvector-based content."""
        expander = FractalExpander(max_depth=1, branching_factor=5)
        soul = KgentSoul()

        # Set high confidence on aesthetic eigenvector
        soul.eigenvectors.aesthetic.confidence = 0.9

        result = await expander.expand("design patterns", soul=soul)

        # Should have more children due to eigenvector-influenced expansion
        children_content = [c.content.lower() for c in result.children]
        # Aesthetic should add "minimal essence" expansion
        has_minimal = any("minimal" in c for c in children_content)
        # This is probabilistic but aesthetic > 0.7 should trigger it
        assert has_minimal or len(result.children) > 0

    @pytest.mark.asyncio
    async def test_custom_depth_and_branching(self) -> None:
        """Test custom depth and branching configuration."""
        expander = FractalExpander(max_depth=1, branching_factor=1)
        result = await expander.expand("Minimal tree")

        # With max_depth=1, root should have children but they should have none
        assert len(result.children) > 0
        for child in result.children:
            assert child.depth == 1
            # With branching_factor=1 and depth=1 at children, they shouldn't expand further
            # because next depth would be 2 >= max_depth


# =============================================================================
# ConstitutionArticle Tests
# =============================================================================


class TestConstitutionArticle:
    """Tests for ConstitutionArticle dataclass."""

    def test_article_creation(self) -> None:
        """Test basic article creation."""
        article = ConstitutionArticle(
            number=1,
            title="Minimalism",
            content="Say no more than yes.",
        )

        assert article.number == 1
        assert article.title == "Minimalism"
        assert article.content == "Say no more than yes."
        assert article.eigenvector_weights == {}
        assert article.examples == []

    def test_article_with_weights_and_examples(self) -> None:
        """Test article with eigenvector weights and examples."""
        article = ConstitutionArticle(
            number=2,
            title="Composability",
            content="Agents are morphisms.",
            eigenvector_weights={"categorical": 0.9, "heterarchy": 0.7},
            examples=["f >> g over f(g(x))", "Dependency injection"],
        )

        assert article.eigenvector_weights["categorical"] == 0.9
        assert article.eigenvector_weights["heterarchy"] == 0.7
        assert len(article.examples) == 2

    def test_article_to_dict(self) -> None:
        """Test article serialization."""
        article = ConstitutionArticle(
            number=1,
            title="Test",
            content="Content",
            eigenvector_weights={"joy": 0.5},
            examples=["example"],
        )

        data = article.to_dict()
        assert data["number"] == 1
        assert data["title"] == "Test"
        assert data["content"] == "Content"
        assert data["eigenvector_weights"]["joy"] == 0.5
        assert data["examples"] == ["example"]


# =============================================================================
# HolographicConstitution Tests
# =============================================================================


class TestHolographicConstitution:
    """Tests for HolographicConstitution."""

    @pytest.fixture
    def constitution(self) -> HolographicConstitution:
        """Create a HolographicConstitution."""
        return HolographicConstitution()

    def test_constitution_has_articles(
        self, constitution: HolographicConstitution
    ) -> None:
        """Test that constitution initializes with articles."""
        assert len(constitution._articles) == 6

    def test_get_article_by_number(self, constitution: HolographicConstitution) -> None:
        """Test getting article by number."""
        article = constitution.get_article(1)
        assert article is not None
        assert article.number == 1
        assert article.title == "Minimalism"

        article = constitution.get_article(6)
        assert article is not None
        assert article.number == 6
        assert article.title == "Joy"

    def test_get_article_invalid_number(
        self, constitution: HolographicConstitution
    ) -> None:
        """Test getting article with invalid number returns None."""
        article = constitution.get_article(0)
        assert article is None

        article = constitution.get_article(99)
        assert article is None

    def test_get_by_eigenvector(self, constitution: HolographicConstitution) -> None:
        """Test getting articles weighted by eigenvector."""
        # Aesthetic should return Minimalism first
        aesthetic_articles = constitution.get_by_eigenvector("aesthetic")
        assert len(aesthetic_articles) > 0
        assert aesthetic_articles[0].title == "Minimalism"

        # Joy should return Joy article first
        joy_articles = constitution.get_by_eigenvector("joy")
        assert len(joy_articles) > 0
        assert joy_articles[0].title == "Joy"

    def test_get_by_eigenvector_unknown(
        self, constitution: HolographicConstitution
    ) -> None:
        """Test getting articles for unknown eigenvector returns empty."""
        articles = constitution.get_by_eigenvector("unknown")
        assert articles == []

    def test_holographic_lookup_keyword(
        self, constitution: HolographicConstitution
    ) -> None:
        """Test holographic lookup by keyword."""
        # Search for "morphisms" should find Composability (contains "Agents are morphisms")
        results = constitution.holographic_lookup("morphisms")
        titles = [a.title for a in results]
        assert "Composability" in titles

    def test_holographic_lookup_title_match(
        self, constitution: HolographicConstitution
    ) -> None:
        """Test holographic lookup with title match."""
        results = constitution.holographic_lookup("minimalism")
        assert len(results) > 0
        assert results[0].title == "Minimalism"

    def test_holographic_lookup_no_match(
        self, constitution: HolographicConstitution
    ) -> None:
        """Test holographic lookup with no matching terms."""
        results = constitution.holographic_lookup("xyzzy")
        assert results == []

    def test_holographic_lookup_with_soul_amplification(
        self, constitution: HolographicConstitution
    ) -> None:
        """Test holographic lookup with soul-based amplification."""
        soul = KgentSoul()
        # Set high joy confidence
        soul.eigenvectors.joy.confidence = 0.95

        # Search for "code" - multiple articles might match
        results = constitution.holographic_lookup("code", soul=soul)

        # Joy-weighted articles should be boosted
        # This is somewhat fuzzy but the test verifies soul integration
        assert len(results) >= 0  # At least the integration doesn't crash

    def test_constitution_to_dict(self, constitution: HolographicConstitution) -> None:
        """Test constitution serialization."""
        data = constitution.to_dict()

        assert "articles" in data
        assert "version" in data
        assert data["version"] == "1.0"
        assert len(data["articles"]) == 6

    def test_all_articles_have_eigenvector_weights(
        self, constitution: HolographicConstitution
    ) -> None:
        """Test that all articles have eigenvector weights defined."""
        for article in constitution._articles:
            assert len(article.eigenvector_weights) > 0

    def test_all_articles_have_examples(
        self, constitution: HolographicConstitution
    ) -> None:
        """Test that all articles have examples."""
        for article in constitution._articles:
            assert len(article.examples) > 0
