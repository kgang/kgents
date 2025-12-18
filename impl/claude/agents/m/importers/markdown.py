"""
Markdown Importer: Parse Obsidian/Notion markdown into MemoryCrystal engrams.

This module provides:
- ObsidianVaultParser: Navigate vault structure (folders, files)
- extract_frontmatter: Parse YAML frontmatter metadata
- extract_wikilinks: Find [[wiki links]] and [[link|aliases]]
- extract_tags: Find #tags and nested #parent/child tags
- MarkdownEngram: Structured representation for Crystal storage
- MarkdownImporter: Batch import with progress tracking

Example:
    parser = ObsidianVaultParser("/path/to/vault")
    for engram in parser.parse_all():
        crystal.store(engram.concept_id, engram.content, engram.embedding)

CLI Usage:
    kg brain import --source obsidian --path /path/to/vault
"""

from __future__ import annotations

import hashlib
import re
import uuid
from dataclasses import dataclass, field
from datetime import datetime
from pathlib import Path
from typing import Any, Callable, Iterator, TypedDict

# YAML parsing - optional dependency
try:
    import yaml

    HAS_YAML = True
except ImportError:
    HAS_YAML = False
    yaml = None  # type: ignore


# =============================================================================
# Data Types
# =============================================================================


class FrontmatterData(TypedDict, total=False):
    """Typed dictionary for parsed frontmatter."""

    title: str
    date: str
    created: str
    modified: str
    tags: list[str]
    aliases: list[str]
    # Custom fields are allowed via total=False
    # Users can add any key: value pairs


@dataclass
class WikiLink:
    """A parsed wiki link from markdown."""

    target: str  # The linked note (without .md extension)
    alias: str | None  # Display text if [[target|alias]]
    raw: str  # Original match including brackets

    @property
    def display(self) -> str:
        """Text to display for this link."""
        return self.alias if self.alias else self.target


@dataclass
class MarkdownEngram:
    """
    A knowledge unit extracted from markdown, ready for Crystal storage.

    The engram captures:
    - content: The full text content
    - concept_id: Unique identifier (from filename or generated)
    - metadata: Frontmatter and structural metadata
    - links: Outgoing wikilinks
    - tags: All #tags found
    - source_path: Original file path (for provenance)

    This is the intermediate representation between raw markdown
    and MemoryCrystal patterns.
    """

    content: str
    concept_id: str
    title: str
    metadata: FrontmatterData
    links: list[WikiLink]
    tags: list[str]
    source_path: Path
    created_at: datetime = field(default_factory=datetime.now)
    vault_relative_path: str = ""

    @property
    def word_count(self) -> int:
        """Approximate word count of content."""
        return len(self.content.split())

    @property
    def link_count(self) -> int:
        """Number of outgoing wiki links."""
        return len(self.links)

    @property
    def tag_list(self) -> list[str]:
        """All tags, both from frontmatter and inline."""
        fm_tags = self.metadata.get("tags", [])
        all_tags = list(set(fm_tags + self.tags))
        return sorted(all_tags)

    def to_dict(self) -> dict[str, Any]:
        """Convert to dictionary for serialization."""
        return {
            "concept_id": self.concept_id,
            "title": self.title,
            "content": self.content,
            "tags": self.tag_list,
            "links": [link.target for link in self.links],
            "source_path": str(self.source_path),
            "vault_relative_path": self.vault_relative_path,
            "word_count": self.word_count,
            "created_at": self.created_at.isoformat(),
            "metadata": dict(self.metadata),
        }


@dataclass
class ImportProgress:
    """Track progress during batch import."""

    total_files: int
    processed_files: int = 0
    successful: int = 0
    failed: int = 0
    skipped: int = 0
    current_file: str = ""
    errors: list[tuple[str, str]] = field(default_factory=list)

    @property
    def percent_complete(self) -> float:
        """Percentage of files processed."""
        if self.total_files == 0:
            return 100.0
        return (self.processed_files / self.total_files) * 100

    @property
    def is_complete(self) -> bool:
        """Whether all files have been processed."""
        return self.processed_files >= self.total_files


# =============================================================================
# Extraction Functions
# =============================================================================

# Frontmatter pattern: starts with ---, ends with ---
_FRONTMATTER_PATTERN = re.compile(
    r"^---\s*\n(.*?)\n---\s*\n?",
    re.DOTALL,
)

# Wikilink patterns: [[target]] or [[target|alias]]
_WIKILINK_PATTERN = re.compile(
    r"\[\[([^\]|]+)(?:\|([^\]]+))?\]\]",
)

# Tag patterns: #tag or #parent/child (but not #123 which is a number)
_TAG_PATTERN = re.compile(
    r"(?<![&\w])#([a-zA-Z][a-zA-Z0-9_/-]*)",
)

# Block reference: ^blockid
_BLOCK_REF_PATTERN = re.compile(
    r"\^([a-zA-Z0-9-]+)$",
    re.MULTILINE,
)


def extract_frontmatter(content: str) -> tuple[FrontmatterData, str]:
    """
    Extract YAML frontmatter from markdown content.

    Args:
        content: Raw markdown text

    Returns:
        Tuple of (parsed frontmatter dict, remaining content)

    Example:
        >>> fm, body = extract_frontmatter('''---
        ... title: My Note
        ... tags: [python, coding]
        ... ---
        ... # Content here
        ... ''')
        >>> fm['title']
        'My Note'
    """
    match = _FRONTMATTER_PATTERN.match(content)
    if not match:
        return FrontmatterData(), content

    yaml_content = match.group(1)
    remaining_content = content[match.end() :]

    # Parse YAML if available
    if HAS_YAML and yaml is not None:
        try:
            parsed = yaml.safe_load(yaml_content)
            if isinstance(parsed, dict):
                # Ensure tags is a list
                if "tags" in parsed and isinstance(parsed["tags"], str):
                    parsed["tags"] = [t.strip() for t in parsed["tags"].split(",")]
                return FrontmatterData(**{str(k): v for k, v in parsed.items()}), remaining_content
        except yaml.YAMLError:
            pass

    # Fallback: simple key: value parsing
    frontmatter: FrontmatterData = FrontmatterData()
    for line in yaml_content.split("\n"):
        if ":" in line:
            key, _, value = line.partition(":")
            key = key.strip()
            value = value.strip()
            if key and value:
                # Handle simple lists: [item1, item2]
                if value.startswith("[") and value.endswith("]"):
                    items = value[1:-1].split(",")
                    value = [item.strip().strip("\"'") for item in items]
                frontmatter[key] = value  # type: ignore

    return frontmatter, remaining_content


def extract_wikilinks(content: str) -> list[WikiLink]:
    """
    Extract all wiki links from markdown content.

    Handles:
    - [[Simple Link]]
    - [[Link|Display Text]]
    - [[Folder/Nested Link]]
    - [[Link#Heading]]
    - [[Link#^blockref]]

    Args:
        content: Markdown text

    Returns:
        List of WikiLink objects

    Example:
        >>> links = extract_wikilinks("See [[Python]] and [[ML|Machine Learning]]")
        >>> [l.target for l in links]
        ['Python', 'ML']
    """
    links: list[WikiLink] = []
    for match in _WIKILINK_PATTERN.finditer(content):
        target = match.group(1).strip()
        alias = match.group(2)
        if alias:
            alias = alias.strip()

        links.append(
            WikiLink(
                target=target,
                alias=alias,
                raw=match.group(0),
            )
        )

    return links


def extract_tags(content: str) -> list[str]:
    """
    Extract all #tags from markdown content.

    Handles:
    - #simple
    - #nested/path/tag
    - #CamelCase
    - Excludes #123 (pure numbers)
    - Excludes HTML entities like &#123;

    Args:
        content: Markdown text

    Returns:
        List of tag strings (without # prefix)

    Example:
        >>> extract_tags("This is #python and #data/science")
        ['python', 'data/science']
    """
    tags: list[str] = []
    for match in _TAG_PATTERN.finditer(content):
        tag = match.group(1)
        # Skip if it's just numbers
        if not tag.isdigit():
            tags.append(tag)

    return list(set(tags))  # Deduplicate


def extract_headings(content: str) -> list[tuple[int, str]]:
    """
    Extract all headings from markdown content.

    Args:
        content: Markdown text

    Returns:
        List of (level, text) tuples

    Example:
        >>> extract_headings("# Title\\n## Subtitle")
        [(1, 'Title'), (2, 'Subtitle')]
    """
    headings: list[tuple[int, str]] = []
    for line in content.split("\n"):
        line = line.strip()
        if line.startswith("#"):
            level = 0
            while level < len(line) and line[level] == "#":
                level += 1
            text = line[level:].strip()
            if text:
                headings.append((level, text))
    return headings


def extract_code_blocks(content: str) -> list[tuple[str, str]]:
    """
    Extract fenced code blocks from markdown.

    Args:
        content: Markdown text

    Returns:
        List of (language, code) tuples

    Example:
        >>> blocks = extract_code_blocks("```python\\nprint('hi')\\n```")
        >>> blocks[0]
        ('python', "print('hi')")
    """
    pattern = re.compile(r"```(\w*)\n(.*?)\n```", re.DOTALL)
    return [(m.group(1) or "", m.group(2).strip()) for m in pattern.finditer(content)]


def strip_markdown_formatting(content: str) -> str:
    """
    Remove markdown formatting for plain text extraction.

    Removes:
    - Frontmatter
    - Code blocks
    - Wiki links (preserves display text)
    - Image/link syntax
    - Bold/italic markers

    Args:
        content: Markdown text

    Returns:
        Plain text content
    """
    # Remove frontmatter
    _, content = extract_frontmatter(content)

    # Remove code blocks
    content = re.sub(r"```.*?```", "", content, flags=re.DOTALL)
    content = re.sub(r"`[^`]+`", "", content)

    # Convert wikilinks to just the display text
    content = re.sub(r"\[\[([^\]|]+)\|([^\]]+)\]\]", r"\2", content)
    content = re.sub(r"\[\[([^\]]+)\]\]", r"\1", content)

    # Remove standard markdown links
    content = re.sub(r"\[([^\]]+)\]\([^)]+\)", r"\1", content)

    # Remove images
    content = re.sub(r"!\[([^\]]*)\]\([^)]+\)", r"\1", content)

    # Remove bold/italic
    content = re.sub(r"\*\*([^*]+)\*\*", r"\1", content)
    content = re.sub(r"\*([^*]+)\*", r"\1", content)
    content = re.sub(r"__([^_]+)__", r"\1", content)
    content = re.sub(r"_([^_]+)_", r"\1", content)

    # Remove headings markers
    content = re.sub(r"^#+\s*", "", content, flags=re.MULTILINE)

    # Collapse whitespace
    content = re.sub(r"\n{3,}", "\n\n", content)
    content = content.strip()

    return content


def parse_markdown(content: str, source_path: Path | None = None) -> MarkdownEngram:
    """
    Parse markdown content into a MarkdownEngram.

    This is the main parsing function that combines all extraction
    functions into a structured engram.

    Args:
        content: Raw markdown text
        source_path: Optional file path (for concept_id generation)

    Returns:
        MarkdownEngram ready for Crystal storage
    """
    # Extract components
    frontmatter, body = extract_frontmatter(content)
    links = extract_wikilinks(body)
    tags = extract_tags(body)

    # Get title: frontmatter > first heading > filename
    title = frontmatter.get("title", "")
    if not title:
        headings = extract_headings(body)
        if headings:
            title = headings[0][1]
        elif source_path:
            title = source_path.stem
        else:
            title = "Untitled"

    # Generate concept_id from path or content hash
    if source_path:
        concept_id = source_path.stem.lower().replace(" ", "-")
    else:
        content_hash = hashlib.md5(content.encode()).hexdigest()[:8]
        concept_id = f"engram-{content_hash}"

    return MarkdownEngram(
        content=body,
        concept_id=concept_id,
        title=title,
        metadata=frontmatter,
        links=links,
        tags=tags,
        source_path=source_path or Path("unknown"),
    )


# =============================================================================
# Vault Parser
# =============================================================================


class ObsidianVaultParser:
    """
    Parse an Obsidian vault into MarkdownEngrams.

    Handles:
    - Recursive folder traversal
    - .obsidian and other hidden folders (skipped)
    - Attachments folder (optionally skipped)
    - Daily notes detection
    - Template detection

    Example:
        parser = ObsidianVaultParser("/path/to/vault")

        # Get all engrams
        for engram in parser.parse_all():
            print(f"{engram.title}: {engram.word_count} words, {len(engram.links)} links")

        # Get specific folders
        for engram in parser.parse_folder("projects"):
            process(engram)
    """

    # Folders to skip by default
    DEFAULT_SKIP_FOLDERS = {
        ".obsidian",
        ".trash",
        ".git",
        "_attachments",
        "attachments",
        "_templates",
        "templates",
    }

    # File patterns to skip
    DEFAULT_SKIP_PATTERNS = {
        r"^\.",  # Hidden files
        r"^_",  # Underscore-prefixed files (often templates)
    }

    def __init__(
        self,
        vault_path: str | Path,
        skip_folders: set[str] | None = None,
        skip_patterns: set[str] | None = None,
        include_daily_notes: bool = True,
        include_templates: bool = False,
    ) -> None:
        """
        Initialize the vault parser.

        Args:
            vault_path: Path to Obsidian vault root
            skip_folders: Additional folders to skip (merged with defaults)
            skip_patterns: File patterns to skip (merged with defaults)
            include_daily_notes: Whether to include daily note files
            include_templates: Whether to include template files
        """
        self.vault_path = Path(vault_path).resolve()
        if not self.vault_path.exists():
            raise ValueError(f"Vault path does not exist: {vault_path}")
        if not self.vault_path.is_dir():
            raise ValueError(f"Vault path is not a directory: {vault_path}")

        # Merge skip sets
        self.skip_folders = self.DEFAULT_SKIP_FOLDERS.copy()
        if skip_folders:
            self.skip_folders.update(skip_folders)

        self.skip_patterns = self.DEFAULT_SKIP_PATTERNS.copy()
        if skip_patterns:
            self.skip_patterns.update(skip_patterns)

        self.include_daily_notes = include_daily_notes
        self.include_templates = include_templates

        # Compiled patterns for efficiency
        self._skip_patterns_compiled = [re.compile(p) for p in self.skip_patterns]

    def _should_skip_file(self, path: Path) -> bool:
        """Check if file should be skipped."""
        name = path.name

        # Check patterns
        for pattern in self._skip_patterns_compiled:
            if pattern.match(name):
                return True

        # Check daily notes pattern (YYYY-MM-DD.md)
        if not self.include_daily_notes:
            if re.match(r"^\d{4}-\d{2}-\d{2}\.md$", name):
                return True

        return False

    def _should_skip_folder(self, folder: Path) -> bool:
        """Check if folder should be skipped."""
        name = folder.name
        return name in self.skip_folders or name.startswith(".")

    def discover_files(self) -> list[Path]:
        """
        Discover all markdown files in the vault.

        Returns:
            List of Path objects for all eligible .md files
        """
        files: list[Path] = []

        def walk(folder: Path) -> None:
            try:
                for item in folder.iterdir():
                    if item.is_dir():
                        if not self._should_skip_folder(item):
                            walk(item)
                    elif item.is_file() and item.suffix.lower() == ".md":
                        if not self._should_skip_file(item):
                            files.append(item)
            except PermissionError:
                pass  # Skip folders we can't read

        walk(self.vault_path)
        return sorted(files)

    def parse_file(self, path: Path) -> MarkdownEngram:
        """
        Parse a single markdown file.

        Args:
            path: Path to markdown file

        Returns:
            MarkdownEngram for the file
        """
        content = path.read_text(encoding="utf-8")
        engram = parse_markdown(content, path)

        # Add vault-relative path
        try:
            engram.vault_relative_path = str(path.relative_to(self.vault_path))
        except ValueError:
            engram.vault_relative_path = str(path)

        return engram

    def parse_all(self) -> Iterator[MarkdownEngram]:
        """
        Parse all markdown files in the vault.

        Yields:
            MarkdownEngram for each file
        """
        for file_path in self.discover_files():
            try:
                yield self.parse_file(file_path)
            except Exception:
                # Skip files that can't be parsed
                continue

    def parse_folder(self, folder_name: str) -> Iterator[MarkdownEngram]:
        """
        Parse markdown files in a specific folder.

        Args:
            folder_name: Name of folder (relative to vault root)

        Yields:
            MarkdownEngram for each file in the folder
        """
        folder_path = self.vault_path / folder_name
        if not folder_path.exists():
            return

        for file_path in folder_path.rglob("*.md"):
            if not self._should_skip_file(file_path):
                try:
                    yield self.parse_file(file_path)
                except Exception:
                    continue

    def get_link_graph(self) -> dict[str, set[str]]:
        """
        Build a graph of links between notes.

        Returns:
            Dict mapping concept_id to set of linked concept_ids
        """
        graph: dict[str, set[str]] = {}

        for engram in self.parse_all():
            links = set()
            for link in engram.links:
                # Normalize link target to concept_id format
                target = link.target.lower().replace(" ", "-")
                # Remove heading/block references
                if "#" in target:
                    target = target.split("#")[0]
                links.add(target)
            graph[engram.concept_id] = links

        return graph

    def get_tag_index(self) -> dict[str, set[str]]:
        """
        Build an index of tags to concept_ids.

        Returns:
            Dict mapping tag to set of concept_ids with that tag
        """
        index: dict[str, set[str]] = {}

        for engram in self.parse_all():
            for tag in engram.tag_list:
                if tag not in index:
                    index[tag] = set()
                index[tag].add(engram.concept_id)

        return index

    def stats(self) -> dict[str, Any]:
        """
        Get vault statistics.

        Returns:
            Dict with vault metrics
        """
        files = self.discover_files()
        total_words = 0
        total_links = 0
        total_tags = 0
        all_tags: set[str] = set()

        for file_path in files:
            try:
                engram = self.parse_file(file_path)
                total_words += engram.word_count
                total_links += len(engram.links)
                total_tags += len(engram.tags)
                all_tags.update(engram.tag_list)
            except Exception:
                continue

        return {
            "vault_path": str(self.vault_path),
            "total_files": len(files),
            "total_words": total_words,
            "total_links": total_links,
            "unique_tags": len(all_tags),
            "avg_words_per_file": total_words // max(len(files), 1),
            "avg_links_per_file": total_links / max(len(files), 1),
        }


# =============================================================================
# Batch Importer
# =============================================================================


class MarkdownImporter:
    """
    Batch import markdown files into a MemoryCrystal.

    Provides:
    - Progress tracking callbacks
    - Error handling and reporting
    - Batch size control for memory management
    - Optional duplicate detection

    Example:
        from agents.m import MemoryCrystal
        from agents.m.importers import MarkdownImporter

        crystal = MemoryCrystal(dimension=384)
        importer = MarkdownImporter(crystal)

        progress = importer.import_vault("/path/to/vault")
        print(f"Imported {progress.successful} of {progress.total_files} files")
    """

    def __init__(
        self,
        crystal: Any,  # MemoryCrystal or similar
        embedder: Callable[[str], list[float]] | None = None,
        batch_size: int = 100,
        on_progress: Callable[[ImportProgress], None] | None = None,
    ) -> None:
        """
        Initialize the importer.

        Args:
            crystal: MemoryCrystal to store engrams in
            embedder: Function to generate embeddings (or None for hash-based)
            batch_size: Number of files to process before yielding
            on_progress: Callback for progress updates
        """
        self.crystal = crystal
        self.embedder = embedder or self._hash_embedding
        self.batch_size = batch_size
        self.on_progress = on_progress

    def _hash_embedding(self, text: str) -> list[float]:
        """Generate a simple hash-based embedding for testing."""
        # Create a deterministic but distributed embedding from hash
        h = hashlib.sha256(text.encode()).digest()
        # Use 64 dimensions (reasonable for testing)
        embedding = [float(b) / 255.0 - 0.5 for b in h[:32]]
        # Normalize
        magnitude = sum(x * x for x in embedding) ** 0.5
        if magnitude > 0:
            embedding = [x / magnitude for x in embedding]
        return embedding

    def import_vault(
        self,
        vault_path: str | Path,
        **parser_kwargs: Any,
    ) -> ImportProgress:
        """
        Import an entire Obsidian vault.

        Args:
            vault_path: Path to vault root
            **parser_kwargs: Passed to ObsidianVaultParser

        Returns:
            ImportProgress with final statistics
        """
        parser = ObsidianVaultParser(vault_path, **parser_kwargs)
        files = parser.discover_files()

        progress = ImportProgress(total_files=len(files))

        for file_path in files:
            progress.current_file = str(file_path)

            try:
                engram = parser.parse_file(file_path)
                self._store_engram(engram)
                progress.successful += 1
            except Exception as e:
                progress.failed += 1
                progress.errors.append((str(file_path), str(e)))

            progress.processed_files += 1

            # Callback for progress updates
            if self.on_progress:
                self.on_progress(progress)

        return progress

    def import_files(self, file_paths: list[Path]) -> ImportProgress:
        """
        Import a list of specific markdown files.

        Args:
            file_paths: List of paths to import

        Returns:
            ImportProgress with final statistics
        """
        progress = ImportProgress(total_files=len(file_paths))

        for file_path in file_paths:
            progress.current_file = str(file_path)

            try:
                content = file_path.read_text(encoding="utf-8")
                engram = parse_markdown(content, file_path)
                self._store_engram(engram)
                progress.successful += 1
            except Exception as e:
                progress.failed += 1
                progress.errors.append((str(file_path), str(e)))

            progress.processed_files += 1

            if self.on_progress:
                self.on_progress(progress)

        return progress

    def import_content(
        self,
        content: str,
        concept_id: str | None = None,
        source_path: Path | None = None,
    ) -> MarkdownEngram:
        """
        Import a single markdown string.

        Args:
            content: Markdown text
            concept_id: Optional custom ID
            source_path: Optional source path for metadata

        Returns:
            The created MarkdownEngram
        """
        engram = parse_markdown(content, source_path)
        if concept_id:
            engram.concept_id = concept_id
        self._store_engram(engram)
        return engram

    def _store_engram(self, engram: MarkdownEngram) -> None:
        """Store an engram in the crystal."""
        # Generate embedding from plain text content
        plain_text = strip_markdown_formatting(engram.content)
        embedding = self.embedder(plain_text)

        # Store with metadata in the content
        self.crystal.store(
            concept_id=engram.concept_id,
            content=engram,  # Store the full engram object
            embedding=embedding,
        )


# =============================================================================
# L-gent Integration
# =============================================================================


def create_lgent_embedder() -> Callable[[str], list[float]] | None:
    """
    Create an L-gent embedder if available.

    Returns the best available embedder from L-gent:
    - SentenceTransformerEmbedder if sentence-transformers is installed
    - OpenAIEmbedder if openai is installed and OPENAI_API_KEY set
    - None if no L-gent embedder is available (falls back to hash)

    Returns:
        Embedder function or None
    """
    try:
        from agents.l.embedders import (
            OPENAI_AVAILABLE,
            SENTENCE_TRANSFORMERS_AVAILABLE,
        )

        if SENTENCE_TRANSFORMERS_AVAILABLE:
            # Use sentence-transformers directly (sync API)
            try:
                from sentence_transformers import SentenceTransformer

                model = SentenceTransformer("all-MiniLM-L6-v2")

                def sync_embed(text: str) -> list[float]:
                    embedding = model.encode(
                        text, normalize_embeddings=True, show_progress_bar=False
                    )
                    return embedding.tolist()

                return sync_embed
            except Exception:
                pass

        if OPENAI_AVAILABLE:
            # OpenAI requires async, skip for now in sync context
            # Users can provide their own async wrapper if needed
            pass

    except ImportError:
        pass

    return None


def create_importer_with_best_embedder(
    crystal: Any,
    prefer: str = "sentence-transformers",
    batch_size: int = 100,
    on_progress: Callable[[ImportProgress], None] | None = None,
) -> MarkdownImporter:
    """
    Create a MarkdownImporter with the best available embedder.

    Tries L-gent embedders first, falls back to hash-based embedding
    if no ML embedders are available.

    Args:
        crystal: MemoryCrystal to store engrams in
        prefer: Preferred embedder ("sentence-transformers" or "openai")
        batch_size: Number of files per batch
        on_progress: Progress callback

    Returns:
        Configured MarkdownImporter
    """
    embedder = create_lgent_embedder()

    return MarkdownImporter(
        crystal=crystal,
        embedder=embedder,  # None uses default hash embedder
        batch_size=batch_size,
        on_progress=on_progress,
    )


# =============================================================================
# Utility Functions
# =============================================================================


def generate_concept_id(text: str | None = None, path: Path | None = None) -> str:
    """
    Generate a unique concept ID.

    Args:
        text: Optional text to hash for determinism
        path: Optional file path to derive ID from

    Returns:
        A slug-style concept ID
    """
    if path:
        return path.stem.lower().replace(" ", "-")
    elif text:
        h = hashlib.md5(text.encode()).hexdigest()[:8]
        return f"engram-{h}"
    else:
        return f"engram-{uuid.uuid4().hex[:8]}"
