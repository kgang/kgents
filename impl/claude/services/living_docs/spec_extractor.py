"""
Spec Extractor: Markdown Spec -> DocNode

Parses markdown specification files from spec/ and extracts structured documentation:
- ## headers as symbols with hierarchical organization
- Code blocks as examples
- Anti-patterns sections as teaching moments (warning severity)
- Laws tables as teaching moments (critical severity)
- Connection to Principles sections as cross-references

Teaching:
    gotcha: Spec files have different structure than Python docstrings.
            Use markdown-aware parsing, not AST.
            (Evidence: test_spec_extractor.py::test_markdown_structure)

    gotcha: Anti-patterns are warnings, Laws are critical.
            Severity mapping matters for proper prioritization.
            (Evidence: test_spec_extractor.py::test_severity_mapping)
"""

from __future__ import annotations

import re
from dataclasses import dataclass
from pathlib import Path
from typing import Iterator

from .types import DocNode, TeachingMoment, Tier


@dataclass(frozen=True)
class SpecSection:
    """A section from a markdown spec file."""

    title: str
    level: int  # 1 = #, 2 = ##, etc.
    content: str
    line_number: int


class SpecExtractor:
    """
    Extract DocNodes from markdown specification files.

    Handles the structure of kgents spec files:
    - Top-level # = document title
    - ## = major sections (become DocNodes)
    - ### = subsections (included in parent)
    - Code blocks = examples
    - Anti-patterns = warning teaching moments
    - Laws = critical teaching moments

    Teaching:
        gotcha: The extractor processes spec/ files, not impl/ Python files.
                Use DocstringExtractor for Python, SpecExtractor for markdown.
                (Evidence: test_spec_extractor.py::test_file_type_separation)
    """

    # Pattern to match markdown headers
    HEADER_PATTERN = re.compile(r"^(#{1,6})\s+(.+)$", re.MULTILINE)

    # Pattern to match code blocks (fenced)
    CODE_BLOCK_PATTERN = re.compile(
        r"```(\w+)?\n(.*?)```",
        re.DOTALL,
    )

    # Pattern to match Anti-patterns sections
    ANTI_PATTERN_SECTION = re.compile(
        r"##\s*Anti-[Pp]atterns?\s*\n((?:.*\n)*?)(?=\n##\s|\n---|\Z)",
        re.MULTILINE,
    )

    # Pattern to match Laws sections
    LAWS_SECTION = re.compile(
        r"##\s*Laws?\s*\n((?:.*\n)*?)(?=\n##\s|\n---|\Z)",
        re.MULTILINE,
    )

    # Pattern to match individual anti-pattern items (- or * bullets)
    ANTI_PATTERN_ITEM = re.compile(r"^[-*]\s+(.+)$", re.MULTILINE)

    # Pattern to match table rows (for laws)
    TABLE_ROW_PATTERN = re.compile(r"^\|\s*(.+?)\s*\|(.+?)\|(.+?)\|", re.MULTILINE)

    # Paths to exclude
    EXCLUDE_PATTERNS: tuple[str, ...] = (
        "_archive/",
        "node_modules/",
    )

    def should_extract(self, path: Path) -> bool:
        """Check if a file should be extracted (not excluded)."""
        path_str = str(path)
        return path.suffix == ".md" and not any(p in path_str for p in self.EXCLUDE_PATTERNS)

    def extract_file(self, path: Path) -> list[DocNode]:
        """
        Extract DocNodes from a markdown specification file.

        Args:
            path: Path to markdown file

        Returns:
            List of DocNodes for documented sections
        """
        if not self.should_extract(path):
            return []

        try:
            content = path.read_text()
        except (OSError, UnicodeDecodeError):
            return []

        return self.extract_spec(content, self._path_to_module(path))

    def extract_spec(self, content: str, module_name: str = "") -> list[DocNode]:
        """
        Extract DocNodes from markdown specification content.

        Args:
            content: Markdown source
            module_name: Module path (e.g., "spec.agents.d-gent")

        Returns:
            List of DocNodes for each ## section
        """
        nodes: list[DocNode] = []

        # Parse sections
        sections = list(self._parse_sections(content))

        # Extract document title (first # header)
        doc_title = ""
        for section in sections:
            if section.level == 1:
                doc_title = section.title
                break

        # Extract anti-patterns as teaching moments (apply to all nodes)
        anti_pattern_teaching = self._extract_anti_patterns(content)

        # Extract laws as teaching moments (apply to relevant section)
        laws_teaching = self._extract_laws(content)

        # Process each ## section as a DocNode
        for section in sections:
            if section.level != 2:
                continue

            # Skip certain sections that aren't documentation
            if section.title.lower() in (
                "anti-patterns",
                "cross-references",
                "implementation reference",
            ):
                continue

            # Get summary from first paragraph
            summary = self._extract_summary(section.content)

            # Get examples from code blocks
            examples = self._extract_examples(section.content)

            # Determine teaching moments for this section
            teaching: list[TeachingMoment] = []

            # Add laws if this section contains them
            if "law" in section.title.lower():
                teaching.extend(laws_teaching)
            # Add anti-patterns if this is the anti-patterns section
            elif "anti-pattern" in section.title.lower():
                teaching.extend(anti_pattern_teaching)

            # Create signature from header hierarchy
            signature = (
                f"spec {doc_title}: {section.title}" if doc_title else f"spec: {section.title}"
            )

            node = DocNode(
                symbol=self._normalize_symbol(section.title),
                signature=signature,
                summary=summary,
                examples=tuple(examples),
                teaching=tuple(teaching),
                tier=Tier.RICH,  # All spec sections are RICH tier
                module=module_name,
            )
            nodes.append(node)

        return nodes

    def extract_spec_summary(self, path: Path) -> DocNode | None:
        """
        Extract a top-level summary DocNode for the entire spec file.

        This captures the document-level teaching (anti-patterns, laws).
        """
        if not self.should_extract(path):
            return None

        try:
            content = path.read_text()
        except (OSError, UnicodeDecodeError):
            return None

        module_name = self._path_to_module(path)

        # Find document title
        sections = list(self._parse_sections(content))
        doc_title = ""
        for section in sections:
            if section.level == 1:
                doc_title = section.title
                break

        if not doc_title:
            doc_title = path.stem

        # Get summary from content after title, before first ##
        summary = self._extract_doc_summary(content)

        # Collect all teaching moments
        teaching = list(self._extract_anti_patterns(content))
        teaching.extend(self._extract_laws(content))

        # Get all examples from the file
        examples = list(self._extract_examples(content))

        return DocNode(
            symbol=self._normalize_symbol(doc_title),
            signature=f"spec {doc_title}",
            summary=summary,
            examples=tuple(examples[:5]),  # Limit to 5 top examples
            teaching=tuple(teaching),
            tier=Tier.RICH,
            module=module_name,
        )

    def _parse_sections(self, content: str) -> Iterator[SpecSection]:
        """Parse markdown content into sections."""
        lines = content.split("\n")
        current_section: SpecSection | None = None
        section_lines: list[str] = []
        section_start = 0

        for i, line in enumerate(lines):
            header_match = self.HEADER_PATTERN.match(line)
            if header_match:
                # Yield previous section if exists
                if current_section is not None:
                    yield SpecSection(
                        title=current_section.title,
                        level=current_section.level,
                        content="\n".join(section_lines),
                        line_number=section_start,
                    )

                # Start new section
                level = len(header_match.group(1))
                title = header_match.group(2).strip()
                current_section = SpecSection(
                    title=title,
                    level=level,
                    content="",
                    line_number=i + 1,
                )
                section_lines = []
                section_start = i + 1
            else:
                section_lines.append(line)

        # Yield final section
        if current_section is not None:
            yield SpecSection(
                title=current_section.title,
                level=current_section.level,
                content="\n".join(section_lines),
                line_number=section_start,
            )

    def _extract_summary(self, content: str) -> str:
        """Extract the first meaningful paragraph as summary."""
        lines = content.strip().split("\n")
        summary_lines: list[str] = []

        for line in lines:
            line = line.strip()
            # Skip empty lines at the start
            if not line and not summary_lines:
                continue
            # Stop at empty line after content, code block, or header
            if not line and summary_lines:
                break
            if line.startswith("```") or line.startswith("#"):
                break
            # Skip blockquotes for summary
            if line.startswith(">"):
                continue
            summary_lines.append(line)

        return " ".join(summary_lines)[:500]  # Limit length

    def _extract_doc_summary(self, content: str) -> str:
        """Extract summary from document level (between title and first ##)."""
        # Find content between first # and first ##
        title_match = re.search(r"^#\s+.+$", content, re.MULTILINE)
        section_match = re.search(r"^##\s+", content, re.MULTILINE)

        if title_match and section_match:
            start = title_match.end()
            end = section_match.start()
            between = content[start:end].strip()

            # Extract first meaningful content
            lines = between.split("\n")
            for line in lines:
                line = line.strip()
                if line.startswith(">"):
                    # Extract blockquote content
                    return line[1:].strip().strip('"*')
                elif line and not line.startswith("**") and not line.startswith("---"):
                    return line[:500]

        return ""

    def _extract_examples(self, content: str) -> list[str]:
        """Extract code block examples from content."""
        examples: list[str] = []

        for match in self.CODE_BLOCK_PATTERN.finditer(content):
            lang = match.group(1) or ""
            code = match.group(2).strip()

            # Only include Python examples for now
            if lang.lower() in ("python", "py", ""):
                examples.append(code)

        return examples

    def _extract_anti_patterns(self, content: str) -> list[TeachingMoment]:
        """Extract anti-patterns section as warning teaching moments."""
        teaching: list[TeachingMoment] = []

        match = self.ANTI_PATTERN_SECTION.search(content)
        if not match:
            return teaching

        anti_section = match.group(1)

        # Extract bullet points
        for item_match in self.ANTI_PATTERN_ITEM.finditer(anti_section):
            insight = item_match.group(1).strip()
            # Clean up the insight
            insight = re.sub(r"\*\*(.+?)\*\*", r"\1", insight)  # Remove bold
            insight = re.sub(r"`(.+?)`", r"\1", insight)  # Remove code markers

            if insight:
                teaching.append(
                    TeachingMoment(
                        insight=f"Anti-pattern: {insight}",
                        severity="warning",
                    )
                )

        # Also extract from code block examples with ❌
        for match in self.CODE_BLOCK_PATTERN.finditer(anti_section):
            code = match.group(2)
            # Look for ❌ lines
            for line in code.split("\n"):
                if "❌" in line:
                    comment_match = re.search(r"#\s*(.+)$", line)
                    if comment_match:
                        teaching.append(
                            TeachingMoment(
                                insight=f"Anti-pattern: {comment_match.group(1)}",
                                severity="warning",
                            )
                        )

        return teaching

    def _extract_laws(self, content: str) -> list[TeachingMoment]:
        """Extract laws as critical teaching moments."""
        teaching: list[TeachingMoment] = []

        # Look for laws tables
        match = self.LAWS_SECTION.search(content)
        if not match:
            # Also try looking for laws in other sections
            # Pattern: **Law Name**: Description
            law_pattern = re.compile(r"\*\*(\w+)\*\*:\s*`?(.+?)`?\s*(?:\||$)", re.MULTILINE)
            for law_match in law_pattern.finditer(content):
                name = law_match.group(1)
                statement = law_match.group(2).strip()
                if name.lower() in (
                    "law",
                    "identity",
                    "associativity",
                    "functor",
                    "getput",
                    "putget",
                    "putput",
                ):
                    teaching.append(
                        TeachingMoment(
                            insight=f"Law ({name}): {statement}",
                            severity="critical",
                        )
                    )
            return teaching

        laws_section = match.group(1)

        # Extract from tables
        table_started = False
        for line in laws_section.split("\n"):
            if "|" in line:
                if "---" in line:
                    table_started = True
                    continue
                if table_started:
                    # Parse table row
                    cols = [c.strip() for c in line.split("|") if c.strip()]
                    if len(cols) >= 2:
                        law_name = cols[0]
                        statement = cols[1] if len(cols) > 1 else ""
                        # Clean up
                        law_name = re.sub(r"\*\*(.+?)\*\*", r"\1", law_name)
                        statement = re.sub(r"`(.+?)`", r"\1", statement)

                        if law_name and statement:
                            teaching.append(
                                TeachingMoment(
                                    insight=f"Law ({law_name}): {statement}",
                                    severity="critical",
                                )
                            )

        return teaching

    def _normalize_symbol(self, title: str) -> str:
        """Normalize a markdown header into a symbol name."""
        # Remove special characters, convert to snake_case-like
        symbol = re.sub(r"[^\w\s-]", "", title)
        symbol = re.sub(r"[-\s]+", "_", symbol)
        return symbol.lower().strip("_")

    def _path_to_module(self, path: Path) -> str:
        """Convert a file path to a module-like name."""
        # Try to find 'spec' as the base
        parts = path.parts
        try:
            spec_idx = parts.index("spec")
            module_parts = list(parts[spec_idx:])
        except ValueError:
            module_parts = list(parts[-3:])

        # Remove .md extension from last part
        if module_parts and module_parts[-1].endswith(".md"):
            module_parts[-1] = module_parts[-1][:-3]

        return ".".join(module_parts)
