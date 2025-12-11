"""Tests for Psi-gent metaphor corpus."""

import pytest

from ..corpus import (
    ECOSYSTEM,
    PLUMBING,
    STANDARD_CORPUS,
    create_standard_corpus,
    validate_generated_metaphor,
)
from ..types import Metaphor, Operation

# =============================================================================
# Standard Corpus Tests
# =============================================================================


class TestStandardCorpus:
    """Tests for the standard metaphor corpus."""

    def test_corpus_not_empty(self):
        """Standard corpus has metaphors."""
        assert len(STANDARD_CORPUS) >= 6

    def test_all_metaphors_have_operations(self):
        """Every metaphor has at least 2 operations."""
        for m in STANDARD_CORPUS:
            assert len(m.operations) >= 2, f"{m.name} has too few operations"

    def test_all_operations_have_effects(self):
        """Every operation has effects."""
        for m in STANDARD_CORPUS:
            for op in m.operations:
                assert op.effects, f"{m.name}.{op.name} has no effects"

    def test_plumbing_metaphor(self):
        """Plumbing metaphor is well-formed."""
        assert PLUMBING.id == "plumbing"
        assert PLUMBING.name == "Plumbing"
        assert "flow" in PLUMBING.description.lower()

        op_names = {op.name for op in PLUMBING.operations}
        assert "locate_constriction" in op_names
        assert "widen_pipe" in op_names

    def test_ecosystem_metaphor(self):
        """Ecosystem metaphor is well-formed."""
        assert ECOSYSTEM.id == "ecosystem"
        op_names = {op.name for op in ECOSYSTEM.operations}
        assert "strengthen_symbiosis" in op_names or "remove_invasive" in op_names

    def test_metaphors_have_examples(self):
        """At least some metaphors have examples."""
        with_examples = [m for m in STANDARD_CORPUS if m.examples]
        assert len(with_examples) >= 3


# =============================================================================
# MetaphorCorpus Tests
# =============================================================================


class TestMetaphorCorpus:
    """Tests for MetaphorCorpus management."""

    @pytest.fixture
    def corpus(self):
        """Create a test corpus."""
        return create_standard_corpus()

    def test_create_standard_corpus(self, corpus):
        """create_standard_corpus returns populated corpus."""
        assert len(corpus) == len(STANDARD_CORPUS)

    def test_iterate_corpus(self, corpus):
        """Can iterate over corpus."""
        metaphors = list(corpus)
        assert len(metaphors) == len(STANDARD_CORPUS)
        assert all(isinstance(m, Metaphor) for m in metaphors)

    def test_get_by_id(self, corpus):
        """Get metaphor by ID."""
        plumbing = corpus.get("plumbing")
        assert plumbing is not None
        assert plumbing.name == "Plumbing"

        missing = corpus.get("nonexistent")
        assert missing is None

    def test_all_ids(self, corpus):
        """all_ids returns set of IDs."""
        ids = corpus.all_ids
        assert "plumbing" in ids
        assert "ecosystem" in ids

    def test_add_valid_metaphor(self, corpus):
        """Can add a valid metaphor."""
        new_metaphor = Metaphor(
            id="chess",
            name="Chess",
            domain="games",
            description="Strategic board game with pieces and positions",
            operations=(
                Operation(
                    name="sacrifice",
                    description="Give up material for position",
                    effects=("position improves",),
                ),
                Operation(
                    name="develop",
                    description="Move pieces to active squares",
                    effects=("piece becomes active",),
                ),
            ),
        )

        initial_count = len(corpus)
        corpus.add(new_metaphor)
        assert len(corpus) == initial_count + 1
        assert corpus.get("chess") is not None

    def test_add_duplicate_fails(self, corpus):
        """Cannot add metaphor with existing ID."""
        with pytest.raises(ValueError, match="already exists"):
            corpus.add(PLUMBING)

    def test_add_invalid_fails(self, corpus):
        """Cannot add invalid metaphor."""
        invalid = Metaphor(
            id="bad",
            name="Bad",
            domain="test",
            description="Too short",  # < 10 chars after validation
            operations=(),  # No operations
        )
        with pytest.raises(ValueError, match="Invalid"):
            corpus.add(invalid)

    def test_remove_dynamic(self, corpus):
        """Can remove dynamic metaphors."""
        new_metaphor = Metaphor(
            id="temp",
            name="Temporary",
            domain="test",
            description="Temporary metaphor for testing removal",
            operations=(
                Operation(name="op1", description="Op 1", effects=("effect1",)),
                Operation(name="op2", description="Op 2", effects=("effect2",)),
            ),
        )
        corpus.add(new_metaphor)
        assert corpus.get("temp") is not None

        removed = corpus.remove("temp")
        assert removed
        assert corpus.get("temp") is None

    def test_remove_static_fails(self, corpus):
        """Cannot remove static metaphors."""
        removed = corpus.remove("plumbing")
        assert not removed
        assert corpus.get("plumbing") is not None


# =============================================================================
# Validation Tests
# =============================================================================


class TestValidation:
    """Tests for metaphor validation."""

    def test_validate_valid_metaphor(self):
        """Valid metaphor passes validation."""
        valid = Metaphor(
            id="valid",
            name="Valid",
            domain="test",
            description="A valid metaphor with enough description",
            operations=(
                Operation(name="op1", description="Operation 1", effects=("effect1",)),
                Operation(name="op2", description="Operation 2", effects=("effect2",)),
            ),
        )
        is_valid, issues = validate_generated_metaphor(valid)
        assert is_valid
        # May have minor issues (like no examples) but should be valid
        assert not any("Too few operations" in i for i in issues)

    def test_validate_too_few_operations(self):
        """Metaphor with < 2 operations fails."""
        invalid = Metaphor(
            id="invalid",
            name="Invalid",
            domain="test",
            description="Invalid metaphor with one operation",
            operations=(Operation(name="op1", description="Op", effects=("effect",)),),
        )
        is_valid, issues = validate_generated_metaphor(invalid)
        assert not is_valid
        assert any("Too few operations" in i for i in issues)

    def test_validate_operation_without_effects(self):
        """Operation without effects causes warning."""
        invalid = Metaphor(
            id="invalid",
            name="Invalid",
            domain="test",
            description="Invalid metaphor with effectless operation",
            operations=(
                Operation(name="op1", description="Op 1", effects=()),
                Operation(name="op2", description="Op 2", effects=("effect",)),
            ),
        )
        is_valid, issues = validate_generated_metaphor(invalid)
        assert not is_valid
        assert any("no effects" in i for i in issues)


# =============================================================================
# Integration Tests
# =============================================================================


class TestCorpusIntegration:
    """Integration tests for corpus with other components."""

    def test_corpus_metaphors_serialize(self):
        """All corpus metaphors can be serialized."""
        from ..types import to_dict

        for m in STANDARD_CORPUS:
            d = to_dict(m)
            assert d["id"] == m.id
            assert len(d["operations"]) == len(m.operations)

    def test_corpus_coverage_all_domains(self):
        """Corpus covers diverse domains."""
        domains = {m.domain for m in STANDARD_CORPUS}
        # Should have at least 4 different domains
        assert len(domains) >= 4
