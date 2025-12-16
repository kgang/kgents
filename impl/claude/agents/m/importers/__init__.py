"""
M-gent Importers: Convert external knowledge sources to MemoryCrystal engrams.

Supported formats:
- Obsidian vaults (markdown with [[wikilinks]] and #tags)
- Notion exports (markdown with metadata)
- Plain markdown files

Integration:
- L-gent embedders (sentence-transformers, OpenAI) when available
- Falls back to hash-based embedding for zero-dependency operation

Example:
    from agents.m.importers import (
        ObsidianVaultParser,
        MarkdownImporter,
        create_importer_with_best_embedder,
    )

    # Basic usage (hash embeddings)
    crystal = create_crystal(dimension=64)
    importer = MarkdownImporter(crystal)
    progress = importer.import_vault("/path/to/vault")

    # With L-gent semantic embeddings
    importer = create_importer_with_best_embedder(crystal)
    progress = importer.import_vault("/path/to/vault")
"""

from __future__ import annotations

from agents.m.importers.markdown import (
    FrontmatterData,
    ImportProgress,
    MarkdownEngram,
    MarkdownImporter,
    ObsidianVaultParser,
    WikiLink,
    create_importer_with_best_embedder,
    create_lgent_embedder,
    extract_code_blocks,
    extract_frontmatter,
    extract_headings,
    extract_tags,
    extract_wikilinks,
    generate_concept_id,
    parse_markdown,
    strip_markdown_formatting,
)

__all__ = [
    # Core types
    "MarkdownEngram",
    "FrontmatterData",
    "WikiLink",
    "ImportProgress",
    # Parsers
    "ObsidianVaultParser",
    "MarkdownImporter",
    # Factory functions
    "create_importer_with_best_embedder",
    "create_lgent_embedder",
    # Parsing functions
    "parse_markdown",
    "extract_frontmatter",
    "extract_wikilinks",
    "extract_tags",
    "extract_headings",
    "extract_code_blocks",
    "strip_markdown_formatting",
    "generate_concept_id",
]
