"""
Obsidian Principle Extractor - P-gent for extracting principles from vaults.

This module extracts stated principles and values from an Obsidian vault
using a combination of structural analysis and content parsing.

Extraction Strategies:
1. README.md analysis - Look for explicit principle statements
2. Principles folder - Dedicated folder for principles (if exists)
3. Tag-based extraction - Notes tagged with #principle, #value, etc.
4. Content analysis - Sentences containing principle indicators

The extractor uses P-gent parsing strategies for robust extraction
from semi-structured markdown content.
"""

from __future__ import annotations

import re
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path
from typing import Iterator

from ..types import MirrorConfig, Thesis


@dataclass
class ExtractionResult:
    """Result of principle extraction."""

    principles: list[Thesis]
    files_analyzed: int
    extraction_duration_seconds: float
    errors: list[str]


class ObsidianPrincipleExtractor:
    """
    P-gent for extracting principles from Obsidian vaults.

    Implements multiple extraction strategies:
    1. Explicit extraction (README, principles folder)
    2. Tag-based extraction (#principle, #value)
    3. Content-based extraction (indicator phrases)

    Category Theory:
      Extract: Vault → List[Thesis]
      This is a functor from the Obsidian category to the Deontic category.
    """

    def __init__(self, config: MirrorConfig | None = None):
        """Initialize extractor with configuration."""
        self.config = config or MirrorConfig()

        # Compile regex patterns
        self._indicator_pattern = re.compile(
            r"\b(" + "|".join(self.config.principle_indicators) + r")\b",
            re.IGNORECASE,
        )
        self._heading_pattern = re.compile(r"^(#{1,6})\s+(.+)$", re.MULTILINE)
        self._list_item_pattern = re.compile(r"^[\s]*[-*]\s+(.+)$", re.MULTILINE)
        self._tag_pattern = re.compile(r"#(\w+)")

    def extract(self, vault_path: str | Path) -> ExtractionResult:
        """
        Extract all principles from an Obsidian vault.

        Args:
            vault_path: Path to the Obsidian vault root

        Returns:
            ExtractionResult with all extracted principles
        """
        start_time = datetime.now()
        vault_path = Path(vault_path)

        if not vault_path.exists():
            return ExtractionResult(
                principles=[],
                files_analyzed=0,
                extraction_duration_seconds=0.0,
                errors=[f"Vault path does not exist: {vault_path}"],
            )

        principles: list[Thesis] = []
        files_analyzed = 0
        errors: list[str] = []

        # Strategy 1: Extract from README.md
        readme_path = vault_path / "README.md"
        if readme_path.exists() and self.config.extract_from_readme:
            try:
                readme_principles = list(
                    self._extract_from_file(readme_path, is_readme=True)
                )
                principles.extend(readme_principles)
                files_analyzed += 1
            except Exception as e:
                errors.append(f"Error reading README.md: {e}")

        # Strategy 2: Extract from principles folder
        if self.config.extract_from_principles_folder:
            for folder_name in ["principles", "Principles", "values", "Values"]:
                folder_path = vault_path / folder_name
                if folder_path.exists() and folder_path.is_dir():
                    for file_path in folder_path.glob("**/*.md"):
                        try:
                            file_principles = list(
                                self._extract_from_file(
                                    file_path, is_principles_folder=True
                                )
                            )
                            principles.extend(file_principles)
                            files_analyzed += 1
                        except Exception as e:
                            errors.append(f"Error reading {file_path}: {e}")

        # Strategy 3: Extract from tagged notes
        if self.config.extract_from_tags:
            for md_file in self._iter_vault_files(vault_path):
                try:
                    content = md_file.read_text(encoding="utf-8")
                    if self._has_principle_tag(content):
                        file_principles = list(
                            self._extract_from_file(md_file, is_tagged=True)
                        )
                        principles.extend(file_principles)
                        files_analyzed += 1
                except Exception as e:
                    errors.append(f"Error reading {md_file}: {e}")

        # Deduplicate principles
        principles = self._deduplicate_principles(principles)

        duration = (datetime.now() - start_time).total_seconds()

        return ExtractionResult(
            principles=principles,
            files_analyzed=files_analyzed,
            extraction_duration_seconds=duration,
            errors=errors,
        )

    def _iter_vault_files(self, vault_path: Path) -> Iterator[Path]:
        """Iterate over all markdown files in the vault."""
        for ext in self.config.note_extensions:
            for md_file in vault_path.glob(f"**/*{ext}"):
                # Skip excluded folders
                if any(
                    excluded in md_file.parts
                    for excluded in self.config.excluded_folders
                ):
                    continue
                yield md_file

    def _has_principle_tag(self, content: str) -> bool:
        """Check if content has principle-related tags."""
        tags = self._tag_pattern.findall(content)
        principle_tags = {"principle", "principles", "value", "values", "belief"}
        return bool(set(t.lower() for t in tags) & principle_tags)

    def _extract_from_file(
        self,
        file_path: Path,
        is_readme: bool = False,
        is_principles_folder: bool = False,
        is_tagged: bool = False,
    ) -> Iterator[Thesis]:
        """
        Extract principles from a single file.

        Uses different confidence levels based on source:
        - README.md: High confidence (explicit documentation)
        - Principles folder: High confidence (dedicated location)
        - Tagged notes: Medium confidence (user-marked)
        - Indicator-based: Lower confidence (heuristic)
        """
        content = file_path.read_text(encoding="utf-8")
        source = str(file_path)

        # Base confidence by source type
        if is_readme or is_principles_folder:
            base_confidence = 0.9
        elif is_tagged:
            base_confidence = 0.8
        else:
            base_confidence = 0.6

        # Extract from headings (often principle statements)
        for match in self._heading_pattern.finditer(content):
            heading_level = len(match.group(1))
            heading_text = match.group(2).strip()

            # Skip very short headings or navigation headings
            if len(heading_text) < 10 or heading_text.lower() in (
                "contents",
                "table of contents",
                "toc",
                "index",
            ):
                continue

            # Check if heading contains principle indicators
            if self._indicator_pattern.search(heading_text):
                confidence = base_confidence * (1.0 - 0.05 * (heading_level - 1))
                yield Thesis(
                    content=heading_text,
                    source=source,
                    source_line=content[: match.start()].count("\n") + 1,
                    confidence=min(1.0, confidence),
                    category="heading",
                    metadata={"heading_level": heading_level},
                )

        # Extract from list items under principle-related headings
        in_principle_section = False
        current_line = 0

        for line in content.split("\n"):
            current_line += 1

            # Check if we're entering a principle section
            heading_match = re.match(r"^#{1,6}\s+(.+)$", line)
            if heading_match:
                heading = heading_match.group(1).lower()
                in_principle_section = any(
                    ind in heading for ind in ("principle", "value", "belief", "rule")
                )
                continue

            # Extract list items in principle sections
            if in_principle_section:
                list_match = re.match(r"^[\s]*[-*]\s+(.+)$", line)
                if list_match:
                    item_text = list_match.group(1).strip()
                    # Skip short items or links-only items
                    if len(item_text) > 15 and not item_text.startswith("[["):
                        yield Thesis(
                            content=item_text,
                            source=source,
                            source_line=current_line,
                            confidence=base_confidence * 0.95,
                            category="list_item",
                            metadata={"in_principle_section": True},
                        )

        # Extract standalone sentences with strong indicators
        sentences = self._split_into_sentences(content)
        found_strong_indicator = False
        for i, sentence in enumerate(sentences):
            sentence = sentence.strip()
            if len(sentence) < 20 or len(sentence) > 300:
                continue

            # Look for strong principle indicators
            strong_indicators = ("I believe", "We believe", "Our principle", "Always")
            if any(sentence.startswith(ind) for ind in strong_indicators):
                found_strong_indicator = True
                yield Thesis(
                    content=sentence,
                    source=source,
                    confidence=base_confidence * 0.85,
                    category="strong_indicator",
                    metadata={"indicator": "sentence_start"},
                )

        # For tagged notes: if no principles found yet, extract meaningful content
        # The tag itself indicates the note represents a principle
        if is_tagged and not found_strong_indicator:
            # Find first substantive paragraph (not a heading, not too short)
            for line in content.split("\n"):
                line = line.strip()
                # Skip headings, empty lines, and very short lines
                if not line or line.startswith("#") or len(line) < 30:
                    continue
                # Skip lines that are just links or tags
                if line.startswith("[[") or line.startswith("#"):
                    continue
                # Use this as the principle content
                yield Thesis(
                    content=line,
                    source=source,
                    confidence=base_confidence * 0.75,
                    category="tagged_content",
                    metadata={"from_tagged_note": True},
                )
                break  # Only take the first meaningful paragraph

    def _split_into_sentences(self, content: str) -> list[str]:
        """Split content into sentences."""
        # First split on newlines to separate paragraphs
        lines = content.split("\n")
        sentences = []
        for line in lines:
            line = line.strip()
            if not line:
                continue
            # Then split each line on sentence terminators
            line_sentences = re.split(r"(?<=[.!?])\s+", line)
            sentences.extend(s.strip() for s in line_sentences if s.strip())
        return sentences

    def _deduplicate_principles(self, principles: list[Thesis]) -> list[Thesis]:
        """Remove duplicate principles, keeping highest confidence version."""
        seen: dict[str, Thesis] = {}

        for principle in principles:
            # Normalize content for comparison
            normalized = principle.content.lower().strip()

            if (
                normalized not in seen
                or principle.confidence > seen[normalized].confidence
            ):
                seen[normalized] = principle

        return list(seen.values())


# =============================================================================
# Convenience Functions
# =============================================================================


def extract_principles_from_vault(
    vault_path: str | Path,
    config: MirrorConfig | None = None,
) -> list[Thesis]:
    """
    Extract principles from an Obsidian vault.

    This is the main entry point for principle extraction.

    Args:
        vault_path: Path to the Obsidian vault
        config: Optional configuration

    Returns:
        List of extracted Thesis objects
    """
    extractor = ObsidianPrincipleExtractor(config)
    result = extractor.extract(vault_path)
    return result.principles
