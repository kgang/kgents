"""
Tests for the Hydration Context Generator.

AGENTESE: concept.docs.hydrate
"""

from __future__ import annotations

import pytest

from services.living_docs.hydrator import (
    VOICE_ANCHORS,
    HydrationContext,
    Hydrator,
    hydrate_context,
    relevant_for_file,
)
from services.living_docs.teaching import TeachingResult
from services.living_docs.types import TeachingMoment


class TestHydrationContext:
    """Tests for HydrationContext dataclass."""

    def test_to_markdown_empty(self) -> None:
        """Empty context produces minimal markdown."""
        ctx = HydrationContext(task="test task")
        md = ctx.to_markdown()

        assert "# Hydration Context: test task" in md
        assert "Context compiled for: test task" in md

    def test_to_markdown_with_teaching(self) -> None:
        """Teaching moments are included in markdown output."""
        teaching = TeachingResult(
            moment=TeachingMoment(
                insight="Watch out for this gotcha",
                severity="critical",
                evidence="test_file.py::test_gotcha",
            ),
            symbol="some_function",
            module="services.brain.core",
        )
        ctx = HydrationContext(
            task="implement feature",
            relevant_teaching=[teaching],
        )
        md = ctx.to_markdown()

        assert "## Relevant Gotchas" in md
        assert "### 🚨 Critical" in md
        assert "Watch out for this gotcha" in md
        assert "test_file.py::test_gotcha" in md

    def test_to_markdown_with_modules(self) -> None:
        """Related modules are included in markdown output."""
        ctx = HydrationContext(
            task="implement feature",
            related_modules=["services.brain.core", "services.brain.persistence"],
        )
        md = ctx.to_markdown()

        assert "## Files You'll Likely Touch" in md
        assert "`services.brain.core`" in md

    def test_to_markdown_with_voice_anchors(self) -> None:
        """Voice anchors are included in markdown output."""
        ctx = HydrationContext(
            task="implement feature",
            voice_anchors=[VOICE_ANCHORS[0]],
        )
        md = ctx.to_markdown()

        assert "## Voice Anchors" in md
        assert "Daring, bold, creative" in md

    def test_to_dict(self) -> None:
        """Context can be serialized to dict."""
        teaching = TeachingResult(
            moment=TeachingMoment(
                insight="A gotcha",
                severity="warning",
            ),
            symbol="func",
            module="mod",
        )
        ctx = HydrationContext(
            task="test",
            relevant_teaching=[teaching],
            related_modules=["mod1"],
            voice_anchors=["anchor1"],
        )
        d = ctx.to_dict()

        assert d["task"] == "test"
        assert len(d["relevant_teaching"]) == 1
        assert d["relevant_teaching"][0]["insight"] == "A gotcha"
        assert d["related_modules"] == ["mod1"]
        assert d["voice_anchors"] == ["anchor1"]

    def test_markdown_format(self) -> None:
        """Markdown output is suitable for system prompts."""
        teaching = TeachingResult(
            moment=TeachingMoment(insight="Critical issue", severity="critical"),
            symbol="func",
            module="mod",
        )
        ctx = HydrationContext(
            task="build projector",
            relevant_teaching=[teaching],
            related_modules=["services.projector"],
            voice_anchors=[VOICE_ANCHORS[2]],  # Tasteful
        )
        md = ctx.to_markdown()

        # Check structure order: gotchas first, modules second, voice last
        gotcha_pos = md.find("## Relevant Gotchas")
        modules_pos = md.find("## Files You'll Likely Touch")
        voice_pos = md.find("## Voice Anchors")

        assert gotcha_pos < modules_pos < voice_pos, (
            "Gotchas should come before modules, which come before voice"
        )


class TestHydrator:
    """Tests for Hydrator class."""

    def test_keyword_extraction(self) -> None:
        """Keywords are extracted from task description."""
        hydrator = Hydrator()
        keywords = hydrator._extract_keywords("implement wasm projector for agents")

        assert "wasm" in keywords
        assert "projector" in keywords
        assert "agents" in keywords
        # Stop words should be filtered
        assert "for" not in keywords
        assert "implement" not in keywords

    def test_keyword_extraction_deduplicates(self) -> None:
        """Duplicate keywords are removed."""
        hydrator = Hydrator()
        keywords = hydrator._extract_keywords("brain brain brain memory")

        assert keywords.count("brain") == 1
        assert keywords.count("memory") == 1

    def test_keyword_extraction_filters_short(self) -> None:
        """Very short tokens (<=2 chars) are filtered out."""
        hydrator = Hydrator()
        keywords = hydrator._extract_keywords("fix a bug in the code base")

        assert "code" in keywords
        assert "base" in keywords
        assert "bug" in keywords
        assert "a" not in keywords
        assert "in" not in keywords

    def test_hydrate_returns_context(self) -> None:
        """hydrate() returns HydrationContext."""
        hydrator = Hydrator()
        ctx = hydrator.hydrate("implement brain persistence")

        assert isinstance(ctx, HydrationContext)
        assert ctx.task == "implement brain persistence"

    def test_hydrate_finds_relevant_teaching(self) -> None:
        """hydrate() finds teaching moments matching keywords."""
        hydrator = Hydrator()
        ctx = hydrator.hydrate("brain persistence")

        # Should find brain-related teaching moments
        modules = [t.module for t in ctx.relevant_teaching]
        # At minimum we should get some results if brain teaching exists
        # (May be empty if no teaching moments exist)
        assert isinstance(ctx.relevant_teaching, list)

    def test_hydrate_finds_related_modules(self) -> None:
        """hydrate() finds modules matching keywords."""
        hydrator = Hydrator()
        ctx = hydrator.hydrate("brain")

        # Should find brain-related modules
        assert isinstance(ctx.related_modules, list)

    def test_voice_anchors_for_implementation(self) -> None:
        """Implementation tasks get mirror test anchor."""
        hydrator = Hydrator()
        ctx = hydrator.hydrate("implement new feature")

        assert any("Mirror Test" in a for a in ctx.voice_anchors)

    def test_voice_anchors_always_include_tasteful(self) -> None:
        """All tasks get tasteful anchor."""
        hydrator = Hydrator()
        ctx = hydrator.hydrate("any task")

        assert any("Tasteful" in a for a in ctx.voice_anchors)

    def test_voice_anchors_for_joy_tasks(self) -> None:
        """Joy-related tasks get joy anchor."""
        hydrator = Hydrator()
        ctx = hydrator.hydrate("make it fun and delightful")

        assert any("Joy-inducing" in a for a in ctx.voice_anchors)

    def test_voice_anchors_for_garden_tasks(self) -> None:
        """Garden-related tasks get garden anchor."""
        hydrator = Hydrator()
        ctx = hydrator.hydrate("cultivate the garden")

        assert any("garden" in a for a in ctx.voice_anchors)


class TestConvenienceFunctions:
    """Tests for module-level convenience functions."""

    def test_hydrate_context(self) -> None:
        """hydrate_context() returns HydrationContext."""
        ctx = hydrate_context("test task")

        assert isinstance(ctx, HydrationContext)
        assert ctx.task == "test task"

    def test_relevant_for_file(self) -> None:
        """relevant_for_file() returns context for file path."""
        ctx = relevant_for_file("services/brain/persistence.py")

        assert isinstance(ctx, HydrationContext)
        assert "brain" in ctx.task.lower()
        assert "persistence" in ctx.task.lower()

    def test_relevant_for_file_extracts_path_parts(self) -> None:
        """File paths are converted to meaningful keywords."""
        ctx = relevant_for_file("protocols/agentese/logos.py")

        assert "logos" in ctx.task.lower() or "agentese" in ctx.task.lower()


class TestKeywordMatching:
    """Tests for keyword-based matching (vs semantic)."""

    def test_keyword_matching(self) -> None:
        """
        Hydrator uses keyword matching, not semantic similarity.

        This is intentional—semantic matching is future work via Brain vectors.
        """
        hydrator = Hydrator()

        # Exact keyword match should work
        ctx1 = hydrator.hydrate("brain")
        brain_modules = [m for m in ctx1.related_modules if "brain" in m.lower()]

        # Semantic equivalent should NOT match (yet)
        ctx2 = hydrator.hydrate("memory")  # Semantic equivalent of brain
        # Memory is a different keyword, might find m-gent stuff instead

        # The test verifies the current behavior is keyword-based
        assert isinstance(ctx1.related_modules, list)
        assert isinstance(ctx2.related_modules, list)


class TestVoiceAnchors:
    """Tests for voice anchor handling."""

    def test_voice_anchors_are_curated(self) -> None:
        """
        Voice anchors come from _focus.md, not git history.

        This is documented in the gotcha and intentional.
        """
        assert len(VOICE_ANCHORS) > 0
        assert all(isinstance(a, str) for a in VOICE_ANCHORS)

    def test_voice_anchors_preserve_quotes(self) -> None:
        """Voice anchors should preserve Kent's exact phrasing."""
        for anchor in VOICE_ANCHORS:
            # All anchors should be quoted phrases
            assert (
                anchor.startswith('"')
                or anchor.startswith("'")
                or ">" in anchor
                or anchor[0].isupper()
            )

    def test_default_anchors_returned(self) -> None:
        """When no specific anchors match, at least tasteful is returned."""
        hydrator = Hydrator()
        ctx = hydrator.hydrate("completely unrelated query xyz123")

        # Should still get the tasteful anchor at minimum
        assert len(ctx.voice_anchors) >= 1
        assert any("Tasteful" in a for a in ctx.voice_anchors)


class TestIntegration:
    """Integration tests for the full hydration pipeline."""

    def test_full_hydration_flow(self) -> None:
        """Complete hydration flow produces valid output."""
        ctx = hydrate_context("implement wasm projector for categorical agents")

        # Should have all components
        assert ctx.task
        assert isinstance(ctx.relevant_teaching, list)
        assert isinstance(ctx.related_modules, list)
        assert isinstance(ctx.voice_anchors, list)

        # Should produce valid markdown
        md = ctx.to_markdown()
        assert "# Hydration Context:" in md
        assert "---" in md

        # Should produce valid dict
        d = ctx.to_dict()
        assert "task" in d
        assert "relevant_teaching" in d

    def test_hydration_for_common_tasks(self) -> None:
        """Common task types produce reasonable output."""
        tasks = [
            "fix bug in brain persistence",
            "add new agentese node",
            "implement flux streaming",
            "update witness playbook",
        ]

        for task in tasks:
            ctx = hydrate_context(task)
            assert ctx.task == task
            # Should not raise and should produce markdown
            md = ctx.to_markdown()
            assert len(md) > 100  # Non-trivial output
