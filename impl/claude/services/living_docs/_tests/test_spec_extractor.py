"""
Tests for SpecExtractor.

Validates markdown specification extraction:
- Header parsing
- Code block examples
- Anti-patterns as warnings
- Laws as critical teaching moments
"""

from pathlib import Path

import pytest

from services.living_docs.spec_extractor import SpecExtractor, SpecSection
from services.living_docs.types import Tier


class TestSpecExtractor:
    """Tests for SpecExtractor class."""

    @pytest.fixture
    def extractor(self) -> SpecExtractor:
        return SpecExtractor()

    def test_should_extract_md_files(self, extractor: SpecExtractor) -> None:
        """Should accept .md files."""
        assert extractor.should_extract(Path("spec/agents/d-gent.md"))
        assert extractor.should_extract(Path("spec/principles.md"))

    def test_should_exclude_non_md_files(self, extractor: SpecExtractor) -> None:
        """Should reject non-markdown files."""
        assert not extractor.should_extract(Path("spec/agents/d-gent.py"))
        assert not extractor.should_extract(Path("impl/claude/agents/d/__init__.py"))

    def test_should_exclude_archive(self, extractor: SpecExtractor) -> None:
        """Should exclude _archive directories."""
        assert not extractor.should_extract(Path("spec/protocols/_archive/old-spec.md"))

    def test_extract_basic_sections(self, extractor: SpecExtractor) -> None:
        """Extract ## headers as DocNodes."""
        content = """# Document Title

Some intro text.

---

## First Section

This is the first section content.

## Second Section

This is the second section.
"""
        nodes = extractor.extract_spec(content, "spec.test")

        assert len(nodes) == 2
        assert nodes[0].symbol == "first_section"
        assert nodes[0].summary == "This is the first section content."
        assert nodes[1].symbol == "second_section"
        assert nodes[1].summary == "This is the second section."

    def test_extract_signature_with_title(self, extractor: SpecExtractor) -> None:
        """Signature should include document title."""
        content = """# D-gent: The Data Agent

## Purpose

D-gent owns all persistence.
"""
        nodes = extractor.extract_spec(content, "spec.agents.d-gent")

        assert len(nodes) == 1
        assert "D-gent: The Data Agent" in nodes[0].signature
        assert "Purpose" in nodes[0].signature

    def test_extract_code_examples(self, extractor: SpecExtractor) -> None:
        """Extract code blocks as examples."""
        content = """# Test Spec

## Usage

Here's how to use it:

```python
x = 1 + 1
print(x)
```

And another example:

```python
def foo():
    return 42
```
"""
        nodes = extractor.extract_spec(content, "spec.test")

        assert len(nodes) == 1
        assert len(nodes[0].examples) == 2
        assert "x = 1 + 1" in nodes[0].examples[0]
        assert "def foo():" in nodes[0].examples[1]

    def test_extract_anti_patterns_as_warnings(self, extractor: SpecExtractor) -> None:
        """Anti-patterns section becomes warning teaching moments."""
        content = """# Test Spec

## Usage

Use it properly.

## Anti-Patterns

- Hardcoded paths
- Multiple databases per project
- Direct file I/O
"""
        nodes = extractor.extract_spec(content, "spec.test")

        # Find the teaching moments
        summary_node = extractor.extract_spec_summary(_make_temp_path(content, "test.md"))

        assert summary_node is not None
        assert len(summary_node.teaching) >= 3
        for t in summary_node.teaching:
            assert t.severity == "warning"
            assert "Anti-pattern:" in t.insight

    def test_extract_laws_as_critical(self, extractor: SpecExtractor) -> None:
        """Laws section becomes critical teaching moments."""
        content = """# Lens Spec

## Laws

| Law | Requirement |
|-----|-------------|
| **GetPut** | `lens.set(s, lens.get(s)) == s` |
| **PutGet** | `lens.get(lens.set(s, a)) == a` |
"""
        summary_node = extractor.extract_spec_summary(_make_temp_path(content, "lens.md"))

        assert summary_node is not None
        # Should have critical teaching moments for laws
        critical = [t for t in summary_node.teaching if t.severity == "critical"]
        assert len(critical) >= 2
        assert any("GetPut" in t.insight for t in critical)
        assert any("PutGet" in t.insight for t in critical)

    def test_tier_is_always_rich(self, extractor: SpecExtractor) -> None:
        """All spec nodes should be RICH tier."""
        content = """# Spec

## Section One

Content.

## Section Two

More content.
"""
        nodes = extractor.extract_spec(content, "spec.test")

        for node in nodes:
            assert node.tier == Tier.RICH

    def test_module_path_from_file(self, extractor: SpecExtractor) -> None:
        """Module path should be derived from file path."""
        # Test the path conversion
        path = Path("/Users/test/kgents/spec/agents/d-gent.md")
        module = extractor._path_to_module(path)

        assert "spec" in module
        assert "agents" in module
        assert "d-gent" in module

    def test_skip_meta_sections(self, extractor: SpecExtractor) -> None:
        """Should skip Anti-Patterns, Cross-References, Implementation Reference sections."""
        content = """# Test Spec

## Core Feature

This is the core.

## Anti-Patterns

- Bad thing 1
- Bad thing 2

## Cross-References

- See other file

## Implementation Reference

| File | Purpose |
"""
        nodes = extractor.extract_spec(content, "spec.test")

        # Should only have Core Feature
        assert len(nodes) == 1
        assert nodes[0].symbol == "core_feature"

    def test_normalize_symbol(self, extractor: SpecExtractor) -> None:
        """Symbol normalization should handle special characters."""
        assert extractor._normalize_symbol("Core: The Basics") == "core_the_basics"
        assert extractor._normalize_symbol("D-gent Spec") == "d_gent_spec"
        assert extractor._normalize_symbol("API (v2)") == "api_v2"

    def test_extract_blockquote_summary(self, extractor: SpecExtractor) -> None:
        """Document summary can come from blockquote."""
        content = """# D-gent: The Data Agent

> *"The cortex is singular. Memory is global. Context is local."*

**Status**: Canonical

---

## Purpose

D-gent owns all persistence.
"""
        summary_node = extractor.extract_spec_summary(_make_temp_path(content, "d-gent.md"))

        assert summary_node is not None
        assert "cortex is singular" in summary_node.summary

    def test_code_anti_patterns_with_emoji(self, extractor: SpecExtractor) -> None:
        """Extract anti-patterns from code blocks with ❌ emoji."""
        content = """# Test Spec

## Anti-Patterns

```python
# ❌ Hardcoded paths
Path.home() / ".kgents" / "state.json"

# ✅ XDG-compliant via DgentRouter
DgentRouter(namespace="state")
```
"""
        summary_node = extractor.extract_spec_summary(_make_temp_path(content, "test.md"))

        assert summary_node is not None
        # Should extract the ❌ comment as anti-pattern
        warnings = [t for t in summary_node.teaching if t.severity == "warning"]
        assert len(warnings) >= 1
        assert any("Hardcoded paths" in t.insight for t in warnings)

    def test_empty_file(self, extractor: SpecExtractor) -> None:
        """Should handle empty files gracefully."""
        nodes = extractor.extract_spec("", "spec.empty")
        assert nodes == []

    def test_file_with_only_title(self, extractor: SpecExtractor) -> None:
        """Should handle files with only a title."""
        content = """# Just a Title

No sections here.
"""
        nodes = extractor.extract_spec(content, "spec.minimal")
        assert nodes == []  # No ## sections to extract


class TestSpecSection:
    """Tests for SpecSection dataclass."""

    def test_frozen(self) -> None:
        """SpecSection should be immutable."""
        section = SpecSection(title="Test", level=2, content="Content", line_number=1)
        with pytest.raises(AttributeError):
            section.title = "Changed"  # type: ignore


def _make_temp_path(content: str, name: str) -> Path:
    """Create a mock path for testing extract_spec_summary."""
    import tempfile

    with tempfile.NamedTemporaryFile(mode="w", suffix=".md", delete=False, prefix="spec_") as f:
        f.write(content)
        return Path(f.name)
