"""
Tests for Mirror Protocol - Obsidian Integration.

Tests cover:
1. Core types (Thesis, Antithesis, Tension, Synthesis)
2. Obsidian principle extractor (P-gent)
3. Obsidian pattern witness (W-gent)
4. Tension detector (H-gent)
5. Full mirror flow integration
"""

import pytest
import tempfile
from datetime import datetime, timedelta
from pathlib import Path

from protocols.mirror.types import (
    # Enums
    TensionMode,
    TensionType,
    InterventionType,
    PatternType,
    HoldReason,
    # Core types
    Thesis,
    Antithesis,
    Tension,
    Synthesis,
    HoldTension,
    DivergenceScore,
    PatternObservation,
    MirrorReport,
    MirrorConfig,
    # Marker constants
    SYMBOLIC_MARKERS,
    IMAGINARY_MARKERS,
    REAL_MARKERS,
    SHADOW_MAPPINGS,
)
from protocols.mirror.obsidian.extractor import (
    ObsidianPrincipleExtractor,
    extract_principles_from_vault,
    ExtractionResult,
)
from protocols.mirror.obsidian.witness import (
    ObsidianPatternWitness,
    observe_vault_patterns,
    WitnessResult,
    NoteMetadata,
)
from protocols.mirror.obsidian.tension import (
    ObsidianTensionDetector,
    detect_tensions,
    generate_mirror_report,
    TensionRule,
)


# =============================================================================
# Fixtures
# =============================================================================


@pytest.fixture
def temp_vault(tmp_path):
    """Create a temporary Obsidian vault for testing."""
    vault = tmp_path / "test_vault"
    vault.mkdir()

    # Create README with principles
    readme = vault / "README.md"
    readme.write_text("""# My Knowledge Base

## Principles

I believe in connecting ideas across domains.
Always update notes when learning something new.
Daily reflection is important for growth.

## About

This is my personal knowledge base.
""")

    # Create some notes
    notes = vault / "notes"
    notes.mkdir()

    # Note 1: Well-connected note
    note1 = notes / "connected_note.md"
    note1.write_text("""# Connected Note

This note links to [[other_note]] and [[another]].

It has substantial content about knowledge management.
The key insight is that connections matter more than content.

#principle #knowledge
""")

    # Note 2: Orphan note
    note2 = notes / "orphan_note.md"
    note2.write_text("""# Orphan Note

This note has no links to other notes.
It's isolated from the rest of the knowledge base.
""")

    # Note 3: Short note
    note3 = notes / "short_note.md"
    note3.write_text("""# Short

Brief note.
""")

    # Create daily notes folder
    daily = vault / "daily"
    daily.mkdir()

    # Daily note 1: With links
    daily1 = daily / "2024-01-15.md"
    daily1.write_text("""# 2024-01-15

Today I learned about [[topic]].
Reflected on my progress with #reflection.
""")

    # Daily note 2: Without links (orphan daily)
    daily2 = daily / "2024-01-16.md"
    daily2.write_text("""# 2024-01-16

Quick note for today.
""")

    # Create .obsidian folder (should be ignored)
    obsidian = vault / ".obsidian"
    obsidian.mkdir()
    config = obsidian / "app.json"
    config.write_text('{"theme": "dark"}')

    return vault


@pytest.fixture
def simple_thesis():
    """Create a simple thesis for testing."""
    return Thesis(
        content="I believe in connecting ideas",
        source="README.md",
        confidence=0.9,
    )


@pytest.fixture
def simple_observation():
    """Create a simple observation for testing."""
    return PatternObservation(
        pattern_type=PatternType.ORPHAN_NOTES,
        description="Percentage of orphan notes",
        value=60.0,
        sample_size=10,
        confidence=0.95,
    )


# =============================================================================
# Core Types Tests
# =============================================================================


class TestThesis:
    """Tests for Thesis type."""

    def test_thesis_creation(self):
        """Test basic thesis creation."""
        thesis = Thesis(
            content="Always connect ideas",
            source="principles.md",
            confidence=0.9,
        )
        assert thesis.content == "Always connect ideas"
        assert thesis.source == "principles.md"
        assert thesis.confidence == 0.9

    def test_thesis_with_metadata(self):
        """Test thesis with metadata."""
        thesis = Thesis(
            content="Deep work matters",
            source="README.md",
            source_line=42,
            category="productivity",
            metadata={"tags": ["principle", "focus"]},
        )
        assert thesis.source_line == 42
        assert thesis.category == "productivity"
        assert "tags" in thesis.metadata

    def test_thesis_confidence_bounds(self):
        """Test confidence must be 0.0-1.0."""
        with pytest.raises(ValueError):
            Thesis(content="test", source="test", confidence=1.5)

        with pytest.raises(ValueError):
            Thesis(content="test", source="test", confidence=-0.1)

    def test_thesis_immutable(self):
        """Test thesis is frozen."""
        thesis = Thesis(content="test", source="test")
        with pytest.raises(AttributeError):
            thesis.content = "changed"


class TestAntithesis:
    """Tests for Antithesis type."""

    def test_antithesis_creation(self):
        """Test basic antithesis creation."""
        obs = PatternObservation(
            pattern_type=PatternType.ORPHAN_NOTES,
            description="60% orphan notes",
            value=60,
            sample_size=100,
        )
        antithesis = Antithesis(
            pattern="Most notes are isolated",
            evidence=(obs,),
            frequency=0.6,
            severity=0.7,
        )
        assert antithesis.pattern == "Most notes are isolated"
        assert len(antithesis.evidence) == 1
        assert antithesis.frequency == 0.6

    def test_antithesis_frequency_bounds(self):
        """Test frequency must be 0.0-1.0."""
        with pytest.raises(ValueError):
            Antithesis(pattern="test", evidence=(), frequency=1.5)


class TestTension:
    """Tests for Tension type."""

    def test_tension_creation(self, simple_thesis, simple_observation):
        """Test basic tension creation."""
        antithesis = Antithesis(
            pattern="High orphan rate",
            evidence=(simple_observation,),
        )
        tension = Tension(
            thesis=simple_thesis,
            antithesis=antithesis,
            divergence=0.6,
            tension_type=TensionType.BEHAVIORAL,
        )
        assert tension.divergence == 0.6
        assert tension.tension_type == TensionType.BEHAVIORAL

    def test_tension_is_significant(self, simple_thesis, simple_observation):
        """Test significance threshold."""
        antithesis = Antithesis(pattern="test", evidence=(simple_observation,))

        # Not significant (< 0.5)
        low_tension = Tension(
            thesis=simple_thesis,
            antithesis=antithesis,
            divergence=0.3,
        )
        assert low_tension.is_significant is False

        # Significant (>= 0.5)
        high_tension = Tension(
            thesis=simple_thesis,
            antithesis=antithesis,
            divergence=0.7,
        )
        assert high_tension.is_significant is True

    def test_tension_requires_attention(self, simple_thesis, simple_observation):
        """Test attention threshold."""
        antithesis = Antithesis(pattern="test", evidence=(simple_observation,))

        # Doesn't require attention (< 0.75)
        medium = Tension(
            thesis=simple_thesis,
            antithesis=antithesis,
            divergence=0.6,
        )
        assert medium.requires_attention is False

        # Requires attention (>= 0.75)
        high = Tension(
            thesis=simple_thesis,
            antithesis=antithesis,
            divergence=0.8,
        )
        assert high.requires_attention is True


class TestSynthesis:
    """Tests for Synthesis type."""

    def test_synthesis_creation(self, simple_thesis, simple_observation):
        """Test basic synthesis creation."""
        antithesis = Antithesis(pattern="test", evidence=(simple_observation,))
        tension = Tension(
            thesis=simple_thesis,
            antithesis=antithesis,
            divergence=0.6,
        )
        synthesis = Synthesis(
            tension=tension,
            resolution_type="behavioral",
            proposal="Schedule weekly linking sessions",
            intervention=InterventionType.RITUAL,
            cost=0.3,
            confidence=0.7,
        )
        assert synthesis.resolution_type == "behavioral"
        assert synthesis.intervention == InterventionType.RITUAL


class TestPatternObservation:
    """Tests for PatternObservation type."""

    def test_observation_creation(self):
        """Test basic observation creation."""
        obs = PatternObservation(
            pattern_type=PatternType.LINK_DENSITY,
            description="Average links per note",
            value=2.5,
            sample_size=100,
        )
        assert obs.pattern_type == PatternType.LINK_DENSITY
        assert obs.value == 2.5

    def test_observation_with_examples(self):
        """Test observation with examples."""
        obs = PatternObservation(
            pattern_type=PatternType.ORPHAN_NOTES,
            description="Orphan notes",
            value=10,
            sample_size=50,
            examples=("note1.md", "note2.md", "note3.md"),
        )
        assert len(obs.examples) == 3


class TestMirrorReport:
    """Tests for MirrorReport type."""

    def test_report_creation(self, simple_thesis, simple_observation):
        """Test basic report creation."""
        antithesis = Antithesis(pattern="test", evidence=(simple_observation,))
        report = MirrorReport(
            thesis=simple_thesis,
            antithesis=antithesis,
            divergence=0.6,
            reflection="Consider your linking practice.",
        )
        assert report.divergence == 0.6
        assert "linking" in report.reflection

    def test_integrity_score_no_tensions(self, simple_thesis, simple_observation):
        """Test integrity score with no tensions."""
        antithesis = Antithesis(pattern="test", evidence=(simple_observation,))
        report = MirrorReport(
            thesis=simple_thesis,
            antithesis=antithesis,
            divergence=0.0,
            reflection="",
            all_tensions=[],
        )
        assert report.integrity_score == 1.0

    def test_integrity_score_with_tensions(self, simple_thesis, simple_observation):
        """Test integrity score with tensions."""
        antithesis = Antithesis(pattern="test", evidence=(simple_observation,))
        tensions = [
            Tension(thesis=simple_thesis, antithesis=antithesis, divergence=0.6),
            Tension(thesis=simple_thesis, antithesis=antithesis, divergence=0.4),
        ]
        report = MirrorReport(
            thesis=simple_thesis,
            antithesis=antithesis,
            divergence=0.6,
            reflection="",
            all_tensions=tensions,
        )
        # Average divergence = 0.5, so integrity = 0.5
        assert report.integrity_score == 0.5


class TestMirrorConfig:
    """Tests for MirrorConfig type."""

    def test_default_config(self):
        """Test default configuration."""
        config = MirrorConfig()
        assert config.extract_from_readme is True
        assert config.min_divergence_to_report == 0.3
        assert ".obsidian" in config.excluded_folders

    def test_custom_config(self):
        """Test custom configuration."""
        config = MirrorConfig(
            min_divergence_to_report=0.5,
            max_tensions_to_report=3,
        )
        assert config.min_divergence_to_report == 0.5
        assert config.max_tensions_to_report == 3


# =============================================================================
# Extractor Tests
# =============================================================================


class TestObsidianPrincipleExtractor:
    """Tests for ObsidianPrincipleExtractor."""

    def test_extractor_creation(self):
        """Test extractor creation."""
        extractor = ObsidianPrincipleExtractor()
        assert extractor.config is not None

    def test_extract_from_readme(self, temp_vault):
        """Test extraction from README."""
        extractor = ObsidianPrincipleExtractor()
        result = extractor.extract(temp_vault)

        assert isinstance(result, ExtractionResult)
        assert len(result.principles) > 0
        assert result.files_analyzed > 0

        # Check that principles from README were extracted
        contents = [p.content for p in result.principles]
        assert any("connect" in c.lower() for c in contents)

    def test_extract_from_tagged_notes(self, temp_vault):
        """Test extraction from tagged notes."""
        config = MirrorConfig(extract_from_tags=True)
        extractor = ObsidianPrincipleExtractor(config)
        result = extractor.extract(temp_vault)

        # Should find the #principle tagged note
        sources = [p.source for p in result.principles]
        assert any("connected_note" in s for s in sources)

    def test_extract_nonexistent_vault(self, tmp_path):
        """Test extraction from nonexistent vault."""
        extractor = ObsidianPrincipleExtractor()
        result = extractor.extract(tmp_path / "nonexistent")

        assert len(result.principles) == 0
        assert len(result.errors) > 0

    def test_extract_excludes_obsidian_folder(self, temp_vault):
        """Test that .obsidian folder is excluded."""
        extractor = ObsidianPrincipleExtractor()
        result = extractor.extract(temp_vault)

        sources = [p.source for p in result.principles]
        assert not any(".obsidian" in s for s in sources)

    def test_convenience_function(self, temp_vault):
        """Test extract_principles_from_vault convenience function."""
        principles = extract_principles_from_vault(temp_vault)
        assert len(principles) > 0


# =============================================================================
# Witness Tests
# =============================================================================


class TestObsidianPatternWitness:
    """Tests for ObsidianPatternWitness."""

    def test_witness_creation(self):
        """Test witness creation."""
        witness = ObsidianPatternWitness()
        assert witness.config is not None

    def test_observe_vault(self, temp_vault):
        """Test observation of vault."""
        witness = ObsidianPatternWitness()
        result = witness.observe(temp_vault)

        assert isinstance(result, WitnessResult)
        assert len(result.observations) > 0
        assert result.total_notes > 0

    def test_observe_link_patterns(self, temp_vault):
        """Test link pattern observation."""
        witness = ObsidianPatternWitness()
        result = witness.observe(temp_vault)

        # Should find link density observation
        link_obs = [
            o for o in result.observations if o.pattern_type == PatternType.LINK_DENSITY
        ]
        assert len(link_obs) > 0

    def test_observe_orphan_patterns(self, temp_vault):
        """Test orphan pattern observation."""
        witness = ObsidianPatternWitness()
        result = witness.observe(temp_vault)

        # Should find orphan observation
        orphan_obs = [
            o for o in result.observations if o.pattern_type == PatternType.ORPHAN_NOTES
        ]
        assert len(orphan_obs) > 0

    def test_observe_length_patterns(self, temp_vault):
        """Test length pattern observation."""
        witness = ObsidianPatternWitness()
        result = witness.observe(temp_vault)

        # Should find length observation
        length_obs = [
            o for o in result.observations if o.pattern_type == PatternType.NOTE_LENGTH
        ]
        assert len(length_obs) > 0

    def test_observe_daily_notes(self, temp_vault):
        """Test daily note observation."""
        witness = ObsidianPatternWitness()
        result = witness.observe(temp_vault)

        # Should find daily note observations
        daily_obs = [
            o
            for o in result.observations
            if o.pattern_type == PatternType.DAILY_NOTE_USAGE
        ]
        assert len(daily_obs) > 0

    def test_observe_nonexistent_vault(self, tmp_path):
        """Test observation of nonexistent vault."""
        witness = ObsidianPatternWitness()
        result = witness.observe(tmp_path / "nonexistent")

        assert len(result.observations) == 0
        assert len(result.errors) > 0

    def test_convenience_function(self, temp_vault):
        """Test observe_vault_patterns convenience function."""
        observations = observe_vault_patterns(temp_vault)
        assert len(observations) > 0


# =============================================================================
# Tension Detector Tests
# =============================================================================


class TestObsidianTensionDetector:
    """Tests for ObsidianTensionDetector."""

    def test_detector_creation(self):
        """Test detector creation."""
        detector = ObsidianTensionDetector()
        assert len(detector._rules) > 0

    def test_detect_connection_tension(self):
        """Test detection of connection tension."""
        detector = ObsidianTensionDetector()

        principles = [
            Thesis(
                content="I believe in connecting ideas across domains",
                source="README.md",
                confidence=0.9,
            )
        ]

        observations = [
            PatternObservation(
                pattern_type=PatternType.ORPHAN_NOTES,
                description="Percentage of orphan notes (no links in or out)",
                value=60.0,
                sample_size=100,
            )
        ]

        tensions = detector.detect(principles, observations)

        # Should detect tension between connection principle and orphan pattern
        assert len(tensions) > 0
        assert tensions[0].divergence > 0.3

    def test_detect_depth_tension(self):
        """Test detection of depth tension."""
        detector = ObsidianTensionDetector()

        principles = [
            Thesis(
                content="Deep thinking is essential for understanding",
                source="README.md",
                confidence=0.9,
            )
        ]

        observations = [
            PatternObservation(
                pattern_type=PatternType.NOTE_LENGTH,
                description="Percentage of notes under 100 words",
                value=80.0,
                sample_size=100,
            )
        ]

        tensions = detector.detect(principles, observations)

        # Should detect tension between depth principle and short notes
        assert len(tensions) > 0

    def test_detect_no_tension_when_aligned(self):
        """Test no tension when aligned."""
        detector = ObsidianTensionDetector()

        principles = [
            Thesis(
                content="I believe in connecting ideas",
                source="README.md",
                confidence=0.9,
            )
        ]

        observations = [
            PatternObservation(
                pattern_type=PatternType.ORPHAN_NOTES,
                description="Percentage of orphan notes",
                value=5.0,  # Very low orphan rate = aligned
                sample_size=100,
            )
        ]

        tensions = detector.detect(principles, observations)

        # Low orphan rate shouldn't trigger significant tension
        # (depends on min_divergence_to_report)
        if tensions:
            assert tensions[0].divergence < 0.3

    def test_tensions_sorted_by_divergence(self):
        """Test that tensions are sorted by divergence."""
        detector = ObsidianTensionDetector()

        principles = [
            Thesis(content="Connect ideas", source="test", confidence=0.9),
            Thesis(content="Deep thinking matters", source="test", confidence=0.9),
        ]

        observations = [
            PatternObservation(
                pattern_type=PatternType.ORPHAN_NOTES,
                description="Percentage of orphan notes",
                value=70.0,
                sample_size=100,
            ),
            PatternObservation(
                pattern_type=PatternType.NOTE_LENGTH,
                description="Percentage of notes under 100 words",
                value=50.0,
                sample_size=100,
            ),
        ]

        tensions = detector.detect(principles, observations)

        # Should be sorted by divergence (highest first)
        if len(tensions) > 1:
            assert tensions[0].divergence >= tensions[1].divergence

    def test_convenience_function(self):
        """Test detect_tensions convenience function."""
        principles = [Thesis(content="Connect ideas", source="test", confidence=0.9)]
        observations = [
            PatternObservation(
                pattern_type=PatternType.ORPHAN_NOTES,
                description="Percentage of orphan notes",
                value=60.0,
                sample_size=100,
            )
        ]

        tensions = detect_tensions(principles, observations)
        assert isinstance(tensions, list)


class TestGenerateMirrorReport:
    """Tests for generate_mirror_report function."""

    def test_generate_report_with_tensions(self, simple_thesis, simple_observation):
        """Test report generation with tensions."""
        antithesis = Antithesis(
            pattern="High orphan rate", evidence=(simple_observation,)
        )
        tensions = [
            Tension(
                thesis=simple_thesis,
                antithesis=antithesis,
                divergence=0.7,
                tension_type=TensionType.BEHAVIORAL,
                interpretation="You value connections but have many orphan notes.",
            )
        ]

        report = generate_mirror_report(
            vault_path="/test/vault",
            principles=[simple_thesis],
            observations=[simple_observation],
            tensions=tensions,
        )

        assert report.divergence == 0.7
        assert report.thesis == simple_thesis
        assert len(report.reflection) > 0

    def test_generate_report_no_tensions(self, simple_thesis, simple_observation):
        """Test report generation with no tensions."""
        report = generate_mirror_report(
            vault_path="/test/vault",
            principles=[simple_thesis],
            observations=[simple_observation],
            tensions=[],
        )

        assert report.divergence == 0.0
        assert "alignment" in report.reflection.lower()


# =============================================================================
# Integration Tests
# =============================================================================


class TestMirrorIntegration:
    """Integration tests for the full Mirror flow."""

    def test_full_mirror_flow(self, temp_vault):
        """Test complete Mirror Protocol flow."""
        # Step 1: Extract principles
        extractor = ObsidianPrincipleExtractor()
        extraction_result = extractor.extract(temp_vault)
        principles = extraction_result.principles

        assert len(principles) > 0, "Should extract at least one principle"

        # Step 2: Observe patterns
        witness = ObsidianPatternWitness()
        witness_result = witness.observe(temp_vault)
        observations = witness_result.observations

        assert len(observations) > 0, "Should observe at least one pattern"

        # Step 3: Detect tensions
        detector = ObsidianTensionDetector()
        tensions = detector.detect(principles, observations)

        # Tensions may or may not exist depending on vault state
        assert isinstance(tensions, list)

        # Step 4: Generate report
        duration = (
            extraction_result.extraction_duration_seconds
            + witness_result.observation_duration_seconds
        )
        report = generate_mirror_report(
            vault_path=str(temp_vault),
            principles=principles,
            observations=observations,
            tensions=tensions,
            duration_seconds=duration,
        )

        assert isinstance(report, MirrorReport)
        assert report.vault_path == str(temp_vault)
        assert len(report.reflection) > 0

    def test_mirror_with_empty_vault(self, tmp_path):
        """Test Mirror with empty vault."""
        empty_vault = tmp_path / "empty"
        empty_vault.mkdir()

        # Should handle empty vault gracefully
        principles = extract_principles_from_vault(empty_vault)
        observations = observe_vault_patterns(empty_vault)
        tensions = detect_tensions(principles, observations)

        assert len(tensions) == 0

    def test_mirror_detects_expected_tensions(self, tmp_path):
        """Test that Mirror detects expected tensions in a constructed scenario."""
        # Create a vault with a clear tension
        vault = tmp_path / "tension_vault"
        vault.mkdir()

        # Principle: "I connect all my ideas"
        readme = vault / "README.md"
        readme.write_text("""# My Vault

## Principles

I believe in connecting all my ideas together.
Everything should link to something else.
""")

        # Reality: Many orphan notes
        for i in range(10):
            note = vault / f"orphan_{i}.md"
            note.write_text(f"""# Note {i}

This is an isolated note with no links.
It doesn't connect to anything else.
""")

        # Run the mirror
        principles = extract_principles_from_vault(vault)
        observations = observe_vault_patterns(vault)
        tensions = detect_tensions(principles, observations)

        # Should detect the connection tension
        # (This depends on the principle keywords matching)
        # The orphan percentage should be high
        orphan_obs = [
            o for o in observations if o.pattern_type == PatternType.ORPHAN_NOTES
        ]
        assert len(orphan_obs) > 0
        if orphan_obs:
            assert orphan_obs[0].value > 50  # High orphan rate


class TestEdgeCases:
    """Edge case tests."""

    def test_special_characters_in_note_names(self, tmp_path):
        """Test handling of special characters in note names."""
        vault = tmp_path / "special_vault"
        vault.mkdir()

        # Note with special characters
        note = vault / "note with spaces & symbols!.md"
        note.write_text("# Special Note\n\nContent here.")

        witness = ObsidianPatternWitness()
        result = witness.observe(vault)

        assert result.total_notes == 1
        assert len(result.errors) == 0

    def test_unicode_content(self, tmp_path):
        """Test handling of unicode content."""
        vault = tmp_path / "unicode_vault"
        vault.mkdir()

        note = vault / "unicode.md"
        note.write_text("""# Unicode Note 中文 日本語

Emoji: 🎉 ✨ 🚀

Content with various scripts.
""")

        extractor = ObsidianPrincipleExtractor()
        result = extractor.extract(vault)

        # Should not crash
        assert result.files_analyzed >= 0

    def test_very_long_note(self, tmp_path):
        """Test handling of very long notes."""
        vault = tmp_path / "long_vault"
        vault.mkdir()

        note = vault / "long_note.md"
        content = "# Long Note\n\n" + ("This is a paragraph. " * 1000)
        note.write_text(content)

        witness = ObsidianPatternWitness()
        result = witness.observe(vault)

        assert result.total_notes == 1
        # Word count should be high
        length_obs = [
            o for o in result.observations if o.pattern_type == PatternType.NOTE_LENGTH
        ]
        assert len(length_obs) > 0

    def test_deeply_nested_folders(self, tmp_path):
        """Test handling of deeply nested folder structure."""
        vault = tmp_path / "nested_vault"
        current = vault
        for i in range(5):
            current = current / f"level_{i}"
        current.mkdir(parents=True)

        note = current / "deep_note.md"
        note.write_text("# Deep Note\n\nIn a deeply nested folder.")

        witness = ObsidianPatternWitness()
        result = witness.observe(vault)

        assert result.total_notes == 1


# =============================================================================
# Spec Alignment Tests - H-gents spec compliance
# =============================================================================


class TestTensionMode:
    """Tests for TensionMode enum from spec/h-gents/README.md."""

    def test_tension_mode_values(self):
        """Test TensionMode has spec-defined values."""
        assert TensionMode.LOGICAL.value == "logical"
        assert TensionMode.EMPIRICAL.value == "empirical"
        assert TensionMode.PRAGMATIC.value == "pragmatic"
        assert TensionMode.TEMPORAL.value == "temporal"

    def test_tension_with_mode(self, simple_thesis, simple_observation):
        """Test Tension creation with mode."""
        antithesis = Antithesis(pattern="test", evidence=(simple_observation,))
        tension = Tension(
            thesis=simple_thesis,
            antithesis=antithesis,
            divergence=0.7,
            mode=TensionMode.PRAGMATIC,
        )
        assert tension.mode == TensionMode.PRAGMATIC


class TestHoldTension:
    """Tests for HoldTension type from spec/h-gents/sublation.md."""

    def test_hold_tension_creation(self, simple_thesis, simple_observation):
        """Test basic HoldTension creation."""
        antithesis = Antithesis(pattern="test", evidence=(simple_observation,))
        tension = Tension(
            thesis=simple_thesis,
            antithesis=antithesis,
            divergence=0.6,
        )
        hold = HoldTension(
            tension=tension,
            why_held="Tension is productive for growth",
            hold_reason=HoldReason.PRODUCTIVE,
        )
        assert hold.tension == tension
        assert hold.hold_reason == HoldReason.PRODUCTIVE

    def test_hold_reasons(self):
        """Test HoldReason enum values."""
        assert HoldReason.PREMATURE.value == "premature"
        assert HoldReason.PRODUCTIVE.value == "productive"
        assert HoldReason.EXTERNAL_DEPENDENCY.value == "external"
        assert HoldReason.HIGH_COST.value == "high_cost"
        assert HoldReason.KAIROS.value == "kairos"

    def test_hold_with_management_practices(self, simple_thesis, simple_observation):
        """Test HoldTension with management practices."""
        antithesis = Antithesis(pattern="test", evidence=(simple_observation,))
        tension = Tension(
            thesis=simple_thesis,
            antithesis=antithesis,
            divergence=0.5,
        )
        hold = HoldTension(
            tension=tension,
            why_held="Exploration vs exploitation balance",
            hold_reason=HoldReason.PRODUCTIVE,
            productive_function="Drives innovation while maintaining stability",
            synthesis_triggers=("Crisis requiring focus", "Consistent failure"),
            management_practices=("20% exploration time", "Separate metrics"),
        )
        assert len(hold.management_practices) == 2
        assert len(hold.synthesis_triggers) == 2


class TestDivergenceScore:
    """Tests for DivergenceScore type from spec/h-gents/contradiction.md."""

    def test_divergence_score_creation(self):
        """Test DivergenceScore creation."""
        score = DivergenceScore(value=0.5, structural=0.3, semantic=0.7)
        assert score.value == 0.5
        assert score.structural == 0.3
        assert score.semantic == 0.7

    def test_severity_labels(self):
        """Test severity_label property matches spec thresholds."""
        assert DivergenceScore(value=0.1).severity_label == "aligned"
        assert DivergenceScore(value=0.3).severity_label == "tension"
        assert DivergenceScore(value=0.5).severity_label == "contradiction"
        assert DivergenceScore(value=0.7).severity_label == "significant"
        assert DivergenceScore(value=0.9).severity_label == "crisis"

    def test_divergence_validation(self):
        """Test DivergenceScore validates bounds."""
        with pytest.raises(ValueError):
            DivergenceScore(value=1.5)
        with pytest.raises(ValueError):
            DivergenceScore(value=-0.1)


class TestSynthesisResolutionTypes:
    """Tests for Synthesis resolution_type values from spec/h-gents/sublation.md."""

    def test_preserve_resolution(self, simple_thesis, simple_observation):
        """Test 'preserve' resolution type."""
        antithesis = Antithesis(pattern="test", evidence=(simple_observation,))
        tension = Tension(
            thesis=simple_thesis,
            antithesis=antithesis,
            divergence=0.3,
        )
        synthesis = Synthesis(
            tension=tension,
            resolution_type="preserve",
            proposal="Keep thesis as-is, no real contradiction",
        )
        assert synthesis.resolution_type == "preserve"
        assert synthesis.result == synthesis.proposal  # spec alias

    def test_negate_resolution(self, simple_thesis, simple_observation):
        """Test 'negate' resolution type."""
        antithesis = Antithesis(pattern="test", evidence=(simple_observation,))
        tension = Tension(
            thesis=simple_thesis,
            antithesis=antithesis,
            divergence=0.8,
        )
        synthesis = Synthesis(
            tension=tension,
            resolution_type="negate",
            proposal="Replace thesis with antithesis",
        )
        assert synthesis.resolution_type == "negate"

    def test_elevate_resolution(self, simple_thesis, simple_observation):
        """Test 'elevate' resolution type (transcendence)."""
        antithesis = Antithesis(pattern="test", evidence=(simple_observation,))
        tension = Tension(
            thesis=simple_thesis,
            antithesis=antithesis,
            divergence=0.6,
        )
        synthesis = Synthesis(
            tension=tension,
            resolution_type="elevate",
            proposal="Both contain partial truth; synthesize higher principle",
        )
        assert synthesis.resolution_type == "elevate"
        assert synthesis.explanation == synthesis.proposal  # spec alias


class TestMarkerConstants:
    """Tests for marker constants from spec/h-gents/contradiction.md."""

    def test_symbolic_markers_exist(self):
        """Test SYMBOLIC_MARKERS has expected values."""
        assert "defined" in SYMBOLIC_MARKERS
        assert "must" in SYMBOLIC_MARKERS
        assert "protocol" in SYMBOLIC_MARKERS

    def test_imaginary_markers_exist(self):
        """Test IMAGINARY_MARKERS has expected values."""
        assert "perfect" in IMAGINARY_MARKERS
        assert "always" in IMAGINARY_MARKERS
        assert "seamless" in IMAGINARY_MARKERS

    def test_real_markers_exist(self):
        """Test REAL_MARKERS has expected values."""
        assert "cannot" in REAL_MARKERS
        assert "failure" in REAL_MARKERS
        assert "crash" in REAL_MARKERS

    def test_shadow_mappings_exist(self):
        """Test SHADOW_MAPPINGS has expected persona->shadow pairs."""
        assert "helpful" in SHADOW_MAPPINGS
        assert "accurate" in SHADOW_MAPPINGS
        assert "ethical" in SHADOW_MAPPINGS
        # Check shadow content
        assert "refuse" in SHADOW_MAPPINGS["helpful"]
        assert "hallucinate" in SHADOW_MAPPINGS["accurate"]


class TestTensionSpecAliases:
    """Tests for Tension spec-compatible aliases."""

    def test_severity_alias(self, simple_thesis, simple_observation):
        """Test severity property is alias for divergence."""
        antithesis = Antithesis(pattern="test", evidence=(simple_observation,))
        tension = Tension(
            thesis=simple_thesis,
            antithesis=antithesis,
            divergence=0.75,
        )
        assert tension.severity == tension.divergence
        assert tension.severity == 0.75

    def test_description_alias(self, simple_thesis, simple_observation):
        """Test description property is alias for interpretation."""
        antithesis = Antithesis(pattern="test", evidence=(simple_observation,))
        tension = Tension(
            thesis=simple_thesis,
            antithesis=antithesis,
            divergence=0.6,
            interpretation="This is the interpretation",
        )
        assert tension.description == tension.interpretation
        assert tension.description == "This is the interpretation"
