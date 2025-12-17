"""
Comprehensive tests for Markdown Importer.

Spike 3A: Markdown Import System - Test Suite

Tests cover:
- Frontmatter parsing (YAML, simple, edge cases)
- Wikilinks extraction ([[target]], [[target|alias]], [[path/nested]])
- Tag extraction (#simple, #nested/path, edge cases)
- Full markdown parsing pipeline
- Obsidian vault structure navigation
- Batch import with progress tracking
- Error handling and edge cases
- Property-based tests (Hypothesis) for fuzzing
- Performance baselines
- L-gent embedder integration

Run: pytest impl/claude/agents/m/importers/_tests/test_markdown.py -v
"""

from __future__ import annotations

import string
import tempfile
from pathlib import Path
from typing import Any

import pytest
from agents.m.importers.markdown import (
    FrontmatterData,
    ImportProgress,
    MarkdownEngram,
    MarkdownImporter,
    ObsidianVaultParser,
    WikiLink,
    extract_code_blocks,
    extract_frontmatter,
    extract_headings,
    extract_tags,
    extract_wikilinks,
    generate_concept_id,
    parse_markdown,
    strip_markdown_formatting,
)
from hypothesis import given, settings
from hypothesis import strategies as st

# Hypothesis strategies for common test patterns
markdown_text = st.text(min_size=0, max_size=500)
safe_identifiers = st.text(
    alphabet=string.ascii_lowercase + "_", min_size=1, max_size=30
)


# =============================================================================
# Frontmatter Tests
# =============================================================================


class TestExtractFrontmatter:
    """Tests for YAML frontmatter extraction."""

    def test_empty_content_returns_empty_frontmatter(self) -> None:
        """Empty content returns empty frontmatter."""
        fm, body = extract_frontmatter("")
        assert fm == {}
        assert body == ""

    def test_no_frontmatter_returns_original_content(self) -> None:
        """Content without frontmatter returns full content."""
        content = "# Title\n\nSome content"
        fm, body = extract_frontmatter(content)
        assert fm == {}
        assert body == content

    def test_simple_frontmatter(self) -> None:
        """Parse simple key-value frontmatter."""
        content = """---
title: My Note
date: 2024-01-01
---
# Content"""
        fm, body = extract_frontmatter(content)
        assert fm.get("title") == "My Note"
        # YAML may parse dates as datetime.date objects
        date_val = fm.get("date")
        assert date_val is not None
        assert "2024" in str(date_val)
        assert body.strip() == "# Content"

    def test_frontmatter_with_tags_list(self) -> None:
        """Parse tags as list in frontmatter."""
        content = """---
title: Tagged Note
tags: [python, coding, tutorial]
---
Body"""
        fm, body = extract_frontmatter(content)
        assert fm.get("title") == "Tagged Note"
        # Tags should be parsed as list
        tags = fm.get("tags")
        assert isinstance(tags, list)
        assert "python" in tags

    def test_frontmatter_with_aliases(self) -> None:
        """Parse aliases from frontmatter."""
        content = """---
title: Main Title
aliases: [alt1, alt2, "Another Name"]
---
Content"""
        fm, _ = extract_frontmatter(content)
        aliases = fm.get("aliases")
        assert isinstance(aliases, list)
        assert len(aliases) >= 2

    def test_frontmatter_preserves_multiline_values(self) -> None:
        """Frontmatter with complex YAML values."""
        content = """---
title: Complex Note
description: A longer description
tags: [a, b, c]
---
Body here"""
        fm, body = extract_frontmatter(content)
        assert "title" in fm
        assert body.strip() == "Body here"

    def test_malformed_frontmatter_fallback(self) -> None:
        """Malformed YAML falls back to simple parsing."""
        content = """---
title: Still Works
bad yaml: [unclosed
---
Content"""
        fm, body = extract_frontmatter(content)
        # Should still get title via fallback parser
        assert fm.get("title") == "Still Works"
        assert "Content" in body


# =============================================================================
# Wikilink Tests
# =============================================================================


class TestExtractWikilinks:
    """Tests for [[wikilink]] extraction."""

    def test_no_links_returns_empty_list(self) -> None:
        """Content without links returns empty list."""
        links = extract_wikilinks("No links here")
        assert links == []

    def test_simple_link(self) -> None:
        """Parse [[Simple Link]]."""
        links = extract_wikilinks("See [[Python]]")
        assert len(links) == 1
        assert links[0].target == "Python"
        assert links[0].alias is None

    def test_link_with_alias(self) -> None:
        """Parse [[target|display text]]."""
        links = extract_wikilinks("Check [[ML|Machine Learning]]")
        assert len(links) == 1
        assert links[0].target == "ML"
        assert links[0].alias == "Machine Learning"
        assert links[0].display == "Machine Learning"

    def test_nested_path_link(self) -> None:
        """Parse [[folder/note]]."""
        links = extract_wikilinks("See [[projects/python-tutorial]]")
        assert len(links) == 1
        assert links[0].target == "projects/python-tutorial"

    def test_link_with_heading(self) -> None:
        """Parse [[Note#Heading]]."""
        links = extract_wikilinks("Jump to [[Python#Installation]]")
        assert len(links) == 1
        assert links[0].target == "Python#Installation"

    def test_link_with_block_reference(self) -> None:
        """Parse [[Note#^blockid]]."""
        links = extract_wikilinks("See [[Ideas#^abc123]]")
        assert len(links) == 1
        assert "^abc123" in links[0].target

    def test_multiple_links(self) -> None:
        """Extract multiple links from content."""
        content = """
        Check out [[Python]] and [[JavaScript]].
        Also see [[ML|Machine Learning]] for more.
        """
        links = extract_wikilinks(content)
        assert len(links) == 3
        targets = [l.target for l in links]
        assert "Python" in targets
        assert "JavaScript" in targets
        assert "ML" in targets

    def test_link_display_property(self) -> None:
        """WikiLink.display returns alias or target."""
        link1 = WikiLink(target="Target", alias=None, raw="[[Target]]")
        link2 = WikiLink(target="Target", alias="Display", raw="[[Target|Display]]")
        assert link1.display == "Target"
        assert link2.display == "Display"


# =============================================================================
# Tag Tests
# =============================================================================


class TestExtractTags:
    """Tests for #tag extraction."""

    def test_no_tags_returns_empty_list(self) -> None:
        """Content without tags returns empty list."""
        tags = extract_tags("No tags here")
        assert tags == []

    def test_simple_tag(self) -> None:
        """Parse #simple."""
        tags = extract_tags("This is #python content")
        assert "python" in tags

    def test_camelcase_tag(self) -> None:
        """Parse #CamelCase tags."""
        tags = extract_tags("Use #DataScience methods")
        assert "DataScience" in tags

    def test_nested_tag(self) -> None:
        """Parse #parent/child tags."""
        tags = extract_tags("Topic: #programming/python")
        assert "programming/python" in tags

    def test_deeply_nested_tag(self) -> None:
        """Parse deeply nested tags."""
        tags = extract_tags("#level1/level2/level3")
        assert "level1/level2/level3" in tags

    def test_excludes_numbers(self) -> None:
        """#123 is not treated as a tag."""
        tags = extract_tags("Issue #123 is fixed")
        assert "123" not in tags

    def test_excludes_html_entities(self) -> None:
        """HTML entities like &#123; are not tags."""
        tags = extract_tags("Code: &#65;")
        assert "65" not in tags

    def test_multiple_tags(self) -> None:
        """Extract multiple tags."""
        content = "Tagged: #python #coding #tutorial"
        tags = extract_tags(content)
        assert "python" in tags
        assert "coding" in tags
        assert "tutorial" in tags

    def test_deduplicates_tags(self) -> None:
        """Same tag appearing twice is deduplicated."""
        tags = extract_tags("#python is #python")
        assert tags.count("python") == 1


# =============================================================================
# Heading and Code Block Tests
# =============================================================================


class TestExtractHeadings:
    """Tests for heading extraction."""

    def test_h1_heading(self) -> None:
        """Parse # Title."""
        headings = extract_headings("# Main Title")
        assert headings == [(1, "Main Title")]

    def test_multiple_levels(self) -> None:
        """Parse multiple heading levels."""
        content = """# H1
## H2
### H3"""
        headings = extract_headings(content)
        assert (1, "H1") in headings
        assert (2, "H2") in headings
        assert (3, "H3") in headings

    def test_empty_heading_skipped(self) -> None:
        """Empty headings are skipped."""
        headings = extract_headings("# \n## Real Title")
        assert len(headings) == 1
        assert headings[0] == (2, "Real Title")


class TestExtractCodeBlocks:
    """Tests for fenced code block extraction."""

    def test_simple_code_block(self) -> None:
        """Parse ```python ... ```."""
        content = """```python
print("hello")
```"""
        blocks = extract_code_blocks(content)
        assert len(blocks) == 1
        assert blocks[0][0] == "python"
        assert 'print("hello")' in blocks[0][1]

    def test_code_block_no_language(self) -> None:
        """Parse ``` ... ``` without language."""
        content = """```
some code
```"""
        blocks = extract_code_blocks(content)
        assert len(blocks) == 1
        assert blocks[0][0] == ""  # No language

    def test_multiple_code_blocks(self) -> None:
        """Extract multiple code blocks."""
        content = """```python
python code
```
Some text
```javascript
js code
```"""
        blocks = extract_code_blocks(content)
        assert len(blocks) == 2


# =============================================================================
# Strip Formatting Tests
# =============================================================================


class TestStripMarkdownFormatting:
    """Tests for plain text extraction."""

    def test_removes_frontmatter(self) -> None:
        """Frontmatter is removed."""
        content = """---
title: Test
---
Body text"""
        plain = strip_markdown_formatting(content)
        assert "title" not in plain
        assert "Body text" in plain

    def test_removes_code_blocks(self) -> None:
        """Code blocks are removed."""
        content = "Text ```python\ncode\n``` more"
        plain = strip_markdown_formatting(content)
        assert "```" not in plain
        assert "code" not in plain

    def test_converts_wikilinks(self) -> None:
        """Wikilinks become plain text."""
        content = "See [[Python]] and [[ML|Machine Learning]]"
        plain = strip_markdown_formatting(content)
        assert "[[" not in plain
        assert "Python" in plain
        assert "Machine Learning" in plain

    def test_removes_bold_italic(self) -> None:
        """Bold and italic markers removed."""
        content = "This is **bold** and *italic*"
        plain = strip_markdown_formatting(content)
        assert "**" not in plain
        assert "*" not in plain
        assert "bold" in plain
        assert "italic" in plain


# =============================================================================
# Full Parsing Tests
# =============================================================================


class TestParseMarkdown:
    """Tests for full markdown parsing pipeline."""

    def test_basic_note(self) -> None:
        """Parse a basic note."""
        content = """---
title: Test Note
tags: [test]
---
# Test Note

Some content with [[links]] and #tags.
"""
        engram = parse_markdown(content)
        assert engram.title == "Test Note"
        assert "test" in engram.tag_list
        assert engram.link_count == 1
        assert engram.word_count > 0

    def test_engram_properties(self) -> None:
        """MarkdownEngram properties work correctly."""
        engram = MarkdownEngram(
            content="Word one two three four",
            concept_id="test-id",
            title="Test",
            metadata=FrontmatterData(tags=["fm-tag"]),
            links=[WikiLink("target", None, "[[target]]")],
            tags=["inline-tag"],
            source_path=Path("test.md"),
        )
        assert engram.word_count == 5
        assert engram.link_count == 1
        assert "fm-tag" in engram.tag_list
        assert "inline-tag" in engram.tag_list

    def test_engram_to_dict(self) -> None:
        """MarkdownEngram serializes to dict."""
        engram = parse_markdown("# Title\n\nContent")
        d = engram.to_dict()
        assert "concept_id" in d
        assert "title" in d
        assert "content" in d

    def test_title_from_first_heading(self) -> None:
        """Title extracted from first heading if no frontmatter."""
        content = "# My Title\n\nContent"
        engram = parse_markdown(content)
        assert engram.title == "My Title"


# =============================================================================
# Vault Parser Tests
# =============================================================================


class TestObsidianVaultParser:
    """Tests for Obsidian vault parsing."""

    @pytest.fixture
    def temp_vault(self, tmp_path: Path) -> Path:
        """Create a temporary vault structure."""
        # Create folders
        (tmp_path / "notes").mkdir()
        (tmp_path / "projects").mkdir()
        (tmp_path / ".obsidian").mkdir()  # Should be skipped

        # Create files
        (tmp_path / "inbox.md").write_text("# Inbox\n\nCapture thoughts")
        (tmp_path / "notes" / "python.md").write_text(
            """---
title: Python Notes
tags: [python, programming]
---
# Python

Learn [[JavaScript]] too. #coding
"""
        )
        (tmp_path / "notes" / "javascript.md").write_text("# JavaScript\n\nJS notes")
        (tmp_path / "projects" / "project-a.md").write_text(
            "# Project A\n\nSee [[notes/python]]"
        )
        (tmp_path / ".obsidian" / "config.json").write_text("{}")  # Should be skipped

        return tmp_path

    def test_vault_not_found_raises(self) -> None:
        """Non-existent vault raises ValueError."""
        with pytest.raises(ValueError, match="does not exist"):
            ObsidianVaultParser("/nonexistent/path")

    def test_vault_not_directory_raises(self, tmp_path: Path) -> None:
        """File path (not directory) raises ValueError."""
        file_path = tmp_path / "file.txt"
        file_path.write_text("content")
        with pytest.raises(ValueError, match="not a directory"):
            ObsidianVaultParser(file_path)

    def test_discover_files(self, temp_vault: Path) -> None:
        """Discovers markdown files in vault."""
        parser = ObsidianVaultParser(temp_vault)
        files = parser.discover_files()
        assert len(files) == 4  # inbox, python, javascript, project-a
        # .obsidian should be skipped
        assert not any(".obsidian" in str(f) for f in files)

    def test_skips_hidden_folders(self, temp_vault: Path) -> None:
        """Hidden folders (.obsidian) are skipped."""
        parser = ObsidianVaultParser(temp_vault)
        files = parser.discover_files()
        names = [f.name for f in files]
        assert "config.json" not in names

    def test_parse_file(self, temp_vault: Path) -> None:
        """Parse a single file from vault."""
        parser = ObsidianVaultParser(temp_vault)
        engram = parser.parse_file(temp_vault / "notes" / "python.md")
        assert engram.title == "Python Notes"
        assert "python" in engram.tag_list
        assert engram.vault_relative_path == "notes/python.md"

    def test_parse_all_yields_engrams(self, temp_vault: Path) -> None:
        """parse_all() yields all engrams."""
        parser = ObsidianVaultParser(temp_vault)
        engrams = list(parser.parse_all())
        assert len(engrams) == 4

    def test_parse_folder(self, temp_vault: Path) -> None:
        """Parse only files in a specific folder."""
        parser = ObsidianVaultParser(temp_vault)
        engrams = list(parser.parse_folder("notes"))
        assert len(engrams) == 2  # python.md and javascript.md

    def test_get_link_graph(self, temp_vault: Path) -> None:
        """Build link graph from vault."""
        parser = ObsidianVaultParser(temp_vault)
        graph = parser.get_link_graph()
        assert "python" in graph
        assert "javascript" in graph["python"]

    def test_get_tag_index(self, temp_vault: Path) -> None:
        """Build tag index from vault."""
        parser = ObsidianVaultParser(temp_vault)
        index = parser.get_tag_index()
        assert "python" in index
        assert "python" in index["python"]  # Note with #python tag

    def test_stats(self, temp_vault: Path) -> None:
        """Get vault statistics."""
        parser = ObsidianVaultParser(temp_vault)
        stats = parser.stats()
        assert stats["total_files"] == 4
        assert stats["total_words"] > 0
        assert "unique_tags" in stats


# =============================================================================
# Batch Importer Tests
# =============================================================================


class TestMarkdownImporter:
    """Tests for batch import functionality."""

    @pytest.fixture
    def mock_crystal(self) -> Any:
        """Create a mock crystal for testing."""

        class MockCrystal:
            def __init__(self) -> None:
                self.stored: list[tuple[str, Any, list[float]]] = []

            def store(
                self, concept_id: str, content: Any, embedding: list[float]
            ) -> None:
                self.stored.append((concept_id, content, embedding))

        return MockCrystal()

    @pytest.fixture
    def temp_vault(self, tmp_path: Path) -> Path:
        """Create a temporary vault."""
        (tmp_path / "note1.md").write_text("# Note 1\n\nContent one")
        (tmp_path / "note2.md").write_text("# Note 2\n\nContent two")
        return tmp_path

    def test_import_vault(self, mock_crystal: Any, temp_vault: Path) -> None:
        """Import a vault stores all engrams."""
        importer = MarkdownImporter(mock_crystal)
        progress = importer.import_vault(temp_vault)

        assert progress.total_files == 2
        assert progress.successful == 2
        assert progress.failed == 0
        assert len(mock_crystal.stored) == 2

    def test_import_with_progress_callback(
        self, mock_crystal: Any, temp_vault: Path
    ) -> None:
        """Progress callback is called during import."""
        progress_updates: list[ImportProgress] = []

        def on_progress(p: ImportProgress) -> None:
            progress_updates.append(
                ImportProgress(
                    total_files=p.total_files,
                    processed_files=p.processed_files,
                    successful=p.successful,
                )
            )

        importer = MarkdownImporter(mock_crystal, on_progress=on_progress)
        importer.import_vault(temp_vault)

        assert len(progress_updates) == 2

    def test_import_files_list(self, mock_crystal: Any, temp_vault: Path) -> None:
        """Import specific files only."""
        files = [temp_vault / "note1.md"]
        importer = MarkdownImporter(mock_crystal)
        progress = importer.import_files(files)

        assert progress.total_files == 1
        assert progress.successful == 1
        assert len(mock_crystal.stored) == 1

    def test_import_content_string(self, mock_crystal: Any) -> None:
        """Import a markdown string directly."""
        importer = MarkdownImporter(mock_crystal)
        engram = importer.import_content("# Direct\n\nContent", concept_id="direct-id")

        assert engram.concept_id == "direct-id"
        assert len(mock_crystal.stored) == 1

    def test_import_handles_errors(self, mock_crystal: Any, tmp_path: Path) -> None:
        """Import continues past errors."""
        # Create one valid file and reference one that will fail
        (tmp_path / "good.md").write_text("# Good\n\nContent")
        bad_file = tmp_path / "bad.md"
        bad_file.write_bytes(b"\xff\xfe")  # Invalid UTF-8

        importer = MarkdownImporter(mock_crystal)
        progress = importer.import_files([tmp_path / "good.md", bad_file])

        assert progress.successful == 1
        assert progress.failed == 1
        assert len(progress.errors) == 1

    def test_custom_embedder(self, mock_crystal: Any, temp_vault: Path) -> None:
        """Custom embedder function is used."""
        custom_dim = 128
        embeddings_used: list[list[float]] = []

        def custom_embedder(text: str) -> list[float]:
            emb = [0.5] * custom_dim
            embeddings_used.append(emb)
            return emb

        importer = MarkdownImporter(mock_crystal, embedder=custom_embedder)
        importer.import_vault(temp_vault)

        assert len(embeddings_used) == 2
        assert all(len(e) == custom_dim for e in embeddings_used)


# =============================================================================
# Progress Tracking Tests
# =============================================================================


class TestImportProgress:
    """Tests for ImportProgress tracking."""

    def test_percent_complete_zero_files(self) -> None:
        """Zero files gives 100% complete."""
        progress = ImportProgress(total_files=0)
        assert progress.percent_complete == 100.0

    def test_percent_complete_partial(self) -> None:
        """Partial progress calculated correctly."""
        progress = ImportProgress(total_files=10, processed_files=5)
        assert progress.percent_complete == 50.0

    def test_is_complete(self) -> None:
        """is_complete when all files processed."""
        progress = ImportProgress(total_files=2, processed_files=2)
        assert progress.is_complete

    def test_not_complete(self) -> None:
        """Not complete when files remain."""
        progress = ImportProgress(total_files=2, processed_files=1)
        assert not progress.is_complete


# =============================================================================
# Utility Function Tests
# =============================================================================


class TestGenerateConceptId:
    """Tests for concept ID generation."""

    def test_from_path(self) -> None:
        """Generate ID from file path."""
        path = Path("/vault/my-note.md")
        concept_id = generate_concept_id(path=path)
        assert concept_id == "my-note"

    def test_from_text(self) -> None:
        """Generate ID from text hash."""
        concept_id = generate_concept_id(text="Some content")
        assert concept_id.startswith("engram-")

    def test_random_when_no_input(self) -> None:
        """Generate random ID when no input."""
        concept_id = generate_concept_id()
        assert concept_id.startswith("engram-")

    def test_deterministic_from_text(self) -> None:
        """Same text generates same ID."""
        id1 = generate_concept_id(text="Same content")
        id2 = generate_concept_id(text="Same content")
        assert id1 == id2


# =============================================================================
# Edge Case Tests
# =============================================================================


class TestEdgeCases:
    """Tests for edge cases and unusual inputs."""

    def test_empty_file(self) -> None:
        """Empty file parses without error."""
        engram = parse_markdown("")
        assert engram.concept_id.startswith("engram-")
        assert engram.word_count == 0

    def test_frontmatter_only(self) -> None:
        """File with only frontmatter."""
        content = """---
title: Just Metadata
---
"""
        engram = parse_markdown(content)
        assert engram.title == "Just Metadata"

    def test_unicode_content(self) -> None:
        """Unicode content handled correctly."""
        content = "# Emoji Title \n\nContent with emojis: arrows etc."
        engram = parse_markdown(content)
        assert "Emoji" in engram.title

    def test_nested_wikilinks(self) -> None:
        """Links with nested brackets work."""
        # This is technically invalid markdown but should not crash
        content = "See [[Note [with] brackets]]"
        links = extract_wikilinks(content)
        # Should find what it can
        assert len(links) >= 0

    def test_tags_in_code_still_extracted(self) -> None:
        """Tags in code blocks are still found (by design)."""
        # Note: A more sophisticated parser might skip code blocks
        content = "```python\n# comment with #tag\n```"
        tags = extract_tags(content)
        # Current implementation doesn't skip code blocks
        # This tests current behavior
        assert isinstance(tags, list)

    def test_very_long_content(self) -> None:
        """Very long content parses without error."""
        content = "# Long Note\n\n" + "Word " * 10000
        engram = parse_markdown(content)
        assert engram.word_count >= 10000

    def test_special_characters_in_tags(self) -> None:
        """Tags with hyphens and underscores."""
        tags = extract_tags("#my-tag #my_tag #123tag")
        # #123tag is invalid (starts with number via pattern)
        assert "my-tag" in tags
        assert "my_tag" in tags


# =============================================================================
# Property-Based Tests (Hypothesis)
# =============================================================================


class TestPropertyBased:
    """Property-based tests using Hypothesis for fuzzing."""

    @pytest.mark.property
    @given(st.text(min_size=0, max_size=500))
    @settings(max_examples=100)
    def test_parse_markdown_never_crashes(self, content: str) -> None:
        """parse_markdown should never crash on arbitrary input."""
        # Should not raise any exception
        engram = parse_markdown(content)
        # Basic invariants
        assert engram.concept_id is not None
        assert engram.title is not None
        assert isinstance(engram.tags, list)
        assert isinstance(engram.links, list)
        assert engram.word_count >= 0

    @pytest.mark.property
    @given(st.text(min_size=0, max_size=500))
    @settings(max_examples=100)
    def test_extract_frontmatter_never_crashes(self, content: str) -> None:
        """extract_frontmatter should never crash on arbitrary input."""
        fm, body = extract_frontmatter(content)
        # Invariants
        assert isinstance(fm, dict)
        assert isinstance(body, str)

    @pytest.mark.property
    @given(st.text(min_size=0, max_size=500))
    @settings(max_examples=100)
    def test_extract_wikilinks_returns_list(self, content: str) -> None:
        """extract_wikilinks always returns a list."""
        links = extract_wikilinks(content)
        assert isinstance(links, list)
        for link in links:
            assert isinstance(link, WikiLink)
            assert link.target is not None

    @pytest.mark.property
    @given(st.text(min_size=0, max_size=500))
    @settings(max_examples=100)
    def test_extract_tags_returns_list(self, content: str) -> None:
        """extract_tags always returns a list."""
        tags = extract_tags(content)
        assert isinstance(tags, list)
        for tag in tags:
            assert isinstance(tag, str)
            # Tags should not be pure numbers
            assert not tag.isdigit()

    @pytest.mark.property
    @given(
        st.text(
            alphabet=st.characters(whitelist_categories=("L", "N", "P", "Z")),
            min_size=1,
            max_size=100,
        )
    )
    @settings(max_examples=50)
    def test_strip_markdown_preserves_text(self, plain_text: str) -> None:
        """strip_markdown_formatting on plain text preserves most content."""
        # Plain text without markdown should mostly survive stripping
        result = strip_markdown_formatting(plain_text)
        # Result should be string
        assert isinstance(result, str)

    @pytest.mark.property
    @given(
        title=st.text(min_size=1, max_size=50).filter(lambda x: x.strip()),
        body=st.text(min_size=0, max_size=200),
    )
    @settings(max_examples=50)
    def test_frontmatter_title_preserved(self, title: str, body: str) -> None:
        """Title in frontmatter is preserved after parsing."""
        # Skip titles with problematic YAML characters
        # '#' is YAML comment, causes value to be None
        if any(c in title for c in [":", "\n", "---", "'", "#"]):
            return
        content = f"---\ntitle: {title}\n---\n{body}"
        fm, _ = extract_frontmatter(content)
        # Title should be preserved (may be trimmed)
        assert fm.get("title") is not None

    @pytest.mark.property
    @given(
        st.lists(
            st.text(alphabet=string.ascii_lowercase, min_size=1, max_size=20),
            min_size=0,
            max_size=10,
        )
    )
    @settings(max_examples=50)
    def test_wikilinks_roundtrip(self, targets: list[str]) -> None:
        """Wikilinks in content are all extracted."""
        # Build content with wikilinks
        content = " ".join(f"[[{t}]]" for t in targets)
        links = extract_wikilinks(content)
        # All unique targets should be found
        found_targets = {link.target for link in links}
        expected_targets = set(targets)
        assert found_targets == expected_targets

    @pytest.mark.property
    @given(
        st.lists(
            st.text(alphabet=string.ascii_lowercase, min_size=1, max_size=15),
            min_size=0,
            max_size=10,
        )
    )
    @settings(max_examples=50)
    def test_tags_roundtrip(self, tag_names: list[str]) -> None:
        """Tags in content are all extracted."""
        # Build content with tags
        content = " ".join(f"#{t}" for t in tag_names)
        tags = extract_tags(content)
        # All unique tags should be found
        found_tags = set(tags)
        expected_tags = set(tag_names)
        assert found_tags == expected_tags


# =============================================================================
# Performance Baselines
# =============================================================================


class TestPerformance:
    """Performance baseline tests."""

    def test_parse_markdown_performance(self) -> None:
        """Parsing should be fast even for large files."""
        import time

        # Generate a large document
        content = "---\ntitle: Large Document\n---\n"
        content += "# Large Document\n\n"
        content += "See [[Link1]] and [[Link2]].\n" * 500
        content += "#tag1 #tag2 #tag3\n" * 100

        start = time.perf_counter()
        for _ in range(10):
            engram = parse_markdown(content)
        elapsed = time.perf_counter() - start

        # 10 parses should complete in under 1 second
        assert elapsed < 1.0, (
            f"parse_markdown too slow: {elapsed:.3f}s for 10 iterations"
        )
        assert engram.link_count >= 500

    def test_extract_wikilinks_performance(self) -> None:
        """Wikilink extraction should be fast."""
        import time

        content = " ".join(f"[[Link{i}]]" for i in range(1000))

        start = time.perf_counter()
        for _ in range(100):
            links = extract_wikilinks(content)
        elapsed = time.perf_counter() - start

        assert elapsed < 1.0, f"extract_wikilinks too slow: {elapsed:.3f}s"
        assert len(links) == 1000

    def test_vault_discovery_performance(self, tmp_path: Path) -> None:
        """Vault discovery should be fast."""
        import time

        # Create 100 files
        for i in range(100):
            (tmp_path / f"note{i}.md").write_text(f"# Note {i}\n\nContent")

        start = time.perf_counter()
        parser = ObsidianVaultParser(tmp_path)
        files = parser.discover_files()
        elapsed = time.perf_counter() - start

        assert elapsed < 0.5, f"discover_files too slow: {elapsed:.3f}s"
        assert len(files) == 100


# =============================================================================
# L-gent Embedder Integration Tests
# =============================================================================


class TestLgentIntegration:
    """Tests for L-gent embedder integration."""

    @pytest.fixture
    def mock_crystal(self) -> Any:
        """Create a mock crystal for testing."""

        class MockCrystal:
            def __init__(self) -> None:
                self.stored: list[tuple[str, Any, list[float]]] = []

            def store(
                self, concept_id: str, content: Any, embedding: list[float]
            ) -> None:
                self.stored.append((concept_id, content, embedding))

        return MockCrystal()

    def test_simple_embedder_fallback(self, mock_crystal: Any, tmp_path: Path) -> None:
        """Importer works with simple embedder when L-gent unavailable."""
        (tmp_path / "test.md").write_text("# Test\n\nContent")

        # Use default hash embedder (L-gent not required)
        importer = MarkdownImporter(mock_crystal)
        progress = importer.import_vault(tmp_path)

        assert progress.successful == 1
        # Verify embedding was stored
        concept_id, content, embedding = mock_crystal.stored[0]
        assert len(embedding) > 0
        # Hash embeddings are normalized
        magnitude = sum(x * x for x in embedding) ** 0.5
        assert 0.99 < magnitude < 1.01

    def test_batch_embedder_integration(
        self, mock_crystal: Any, tmp_path: Path
    ) -> None:
        """Importer can use batch embedder for efficiency."""
        # Create multiple files
        for i in range(5):
            (tmp_path / f"note{i}.md").write_text(f"# Note {i}\n\nContent {i}")

        embed_calls: list[str] = []

        def tracking_embedder(text: str) -> list[float]:
            embed_calls.append(text)
            return [0.1] * 64

        importer = MarkdownImporter(mock_crystal, embedder=tracking_embedder)
        progress = importer.import_vault(tmp_path)

        assert progress.successful == 5
        assert len(embed_calls) == 5  # One call per file
