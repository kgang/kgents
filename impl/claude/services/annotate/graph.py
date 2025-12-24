"""
Annotation Graph: Build spec ↔ impl bidirectional mappings.

> *"Every spec section should trace to code. Every impl should trace to spec."*

This module builds bidirectional graphs from IMPL_LINK annotations:
- Spec → Impl: Find code that implements a spec section
- Impl → Spec: Find spec sections implemented by a file
- Coverage: Calculate % of spec sections with impl links

Graph Building Pattern:
    1. Extract spec sections (markdown headings)
    2. Query IMPL_LINK annotations
    3. Build edges with verification
    4. Calculate coverage metrics

Teaching:
    gotcha: Impl path verification checks file existence but doesn't parse code.
            Future: Use AST parsing to verify class/function existence.

    principle: Composable - Graph building composes annotation queries with
               file system checks to produce verified edges.

See: brainstorming/tool-use/CLAUDE_CODE_CLI_STRATEGY.md (Phase 2)
"""

from __future__ import annotations

import logging
import re
from pathlib import Path
from typing import TYPE_CHECKING

from .types import ImplEdge, ImplGraph

if TYPE_CHECKING:
    from .store import AnnotationStore

logger = logging.getLogger(__name__)


# =============================================================================
# Spec Section Extraction
# =============================================================================


def extract_spec_sections(spec_path: str | Path) -> list[str]:
    """
    Extract section headings from a markdown spec file.

    Sections are identified by markdown headings (# Heading).
    Returns list of section titles (without # prefix).

    Args:
        spec_path: Path to markdown spec file

    Returns:
        List of section titles

    Example:
        >>> sections = extract_spec_sections("spec/protocols/witness.md")
        >>> sections
        ['Overview', 'Mark Structure', 'MarkStore', 'Event Emission', ...]
    """
    path = Path(spec_path)
    if not path.exists():
        logger.warning(f"Spec file not found: {spec_path}")
        return []

    try:
        content = path.read_text(encoding="utf-8")
    except Exception as e:
        logger.error(f"Failed to read spec file {spec_path}: {e}")
        return []

    # Match markdown headings: # Heading, ## Heading, ### Heading, etc.
    # Capture the heading text without the # prefix
    heading_pattern = re.compile(r"^#{1,6}\s+(.+)$", re.MULTILINE)
    matches = heading_pattern.findall(content)

    # Clean up heading text (strip trailing #, whitespace, etc.)
    sections = [m.strip().rstrip("#").strip() for m in matches]

    logger.debug(f"Extracted {len(sections)} sections from {spec_path}")
    return sections


# =============================================================================
# Implementation Path Verification
# =============================================================================


def verify_impl_path(impl_path: str, repo_root: Path | None = None) -> bool:
    """
    Verify that an implementation path exists.

    Impl paths can be:
    - File path: "services/witness/store.py"
    - File + class: "services/witness/store.py:MarkStore"
    - File + function: "services/witness/store.py:save_mark"

    This function verifies the file exists (class/function verification is future work).

    Args:
        impl_path: Implementation path (with optional :ClassName suffix)
        repo_root: Repository root (defaults to current working directory)

    Returns:
        True if file exists, False otherwise

    Teaching:
        gotcha: We don't parse Python AST to verify class/function existence yet.
                This is a simple file existence check only.
    """
    if repo_root is None:
        repo_root = Path.cwd()

    # Split path from class/function name
    if ":" in impl_path:
        file_part, _ = impl_path.split(":", 1)
    else:
        file_part = impl_path

    # Check if file exists
    full_path = repo_root / file_part
    exists = full_path.exists() and full_path.is_file()

    if not exists:
        logger.debug(f"Implementation path not found: {impl_path}")

    return exists


# =============================================================================
# Graph Building
# =============================================================================


async def build_impl_graph(
    spec_path: str,
    store: AnnotationStore,
    repo_root: Path | None = None,
) -> ImplGraph:
    """
    Build bidirectional spec ↔ impl graph from IMPL_LINK annotations.

    Process:
    1. Extract all sections from spec file
    2. Query all IMPL_LINK annotations for this spec
    3. Build edges with verification
    4. Calculate coverage (% of sections with impl links)

    Args:
        spec_path: Path to spec file
        store: AnnotationStore instance
        repo_root: Repository root for path verification

    Returns:
        ImplGraph with edges, coverage, and uncovered sections

    Example:
        >>> graph = await build_impl_graph("spec/protocols/witness.md", store)
        >>> print(f"Coverage: {graph.coverage:.1%}")
        Coverage: 75.0%
        >>> print(f"Uncovered: {graph.uncovered_sections}")
        Uncovered: ['Future Work', 'Open Questions']
    """
    if repo_root is None:
        repo_root = Path.cwd()

    # Extract spec sections
    sections = extract_spec_sections(spec_path)
    if not sections:
        logger.warning(f"No sections found in {spec_path}")
        return ImplGraph(
            spec_path=spec_path,
            edges=[],
            coverage=0.0,
            uncovered_sections=[],
        )

    # Query IMPL_LINK annotations
    impl_links = await store.get_impl_links(spec_path)
    logger.info(f"Found {len(impl_links)} impl links for {spec_path}")

    # Build edges
    edges: list[ImplEdge] = []
    covered_sections: set[str] = set()

    for annotation in impl_links:
        if not annotation.impl_path:
            logger.warning(f"IMPL_LINK annotation {annotation.id} has no impl_path")
            continue

        # Verify impl path exists
        verified = verify_impl_path(annotation.impl_path, repo_root)

        edge = ImplEdge(
            spec_section=annotation.section,
            impl_path=annotation.impl_path,
            verified=verified,
            annotation_id=annotation.id,
        )
        edges.append(edge)
        covered_sections.add(annotation.section)

    # Calculate coverage
    coverage = len(covered_sections) / len(sections) if sections else 0.0
    uncovered = [s for s in sections if s not in covered_sections]

    graph = ImplGraph(
        spec_path=spec_path,
        edges=edges,
        coverage=coverage,
        uncovered_sections=uncovered,
    )

    logger.info(
        f"Built impl graph for {spec_path}: "
        f"{len(edges)} edges, {coverage:.1%} coverage, "
        f"{len(uncovered)} uncovered sections"
    )

    return graph


async def find_specs_for_impl(
    impl_path: str,
    store: AnnotationStore,
) -> dict[str, list[str]]:
    """
    Find all spec sections that link to a given implementation file.

    Reverse lookup: impl → spec sections.

    Args:
        impl_path: Implementation path (e.g., "services/witness/store.py")
        store: AnnotationStore instance

    Returns:
        Dict mapping spec_path to list of sections

    Example:
        >>> specs = await find_specs_for_impl("services/witness/store.py", store)
        >>> specs
        {
            "spec/protocols/witness.md": ["MarkStore", "Persistence"],
            "spec/agents/w-gent.md": ["Storage Backend"],
        }
    """
    # Query all IMPL_LINK annotations for this impl path
    result = await store.query_annotations(impl_path=impl_path)

    # Group by spec_path
    specs: dict[str, list[str]] = {}
    for annotation in result.annotations:
        if annotation.spec_path not in specs:
            specs[annotation.spec_path] = []
        specs[annotation.spec_path].append(annotation.section)

    logger.info(
        f"Found {len(specs)} specs linking to {impl_path} "
        f"({sum(len(v) for v in specs.values())} total sections)"
    )

    return specs


__all__ = [
    "extract_spec_sections",
    "verify_impl_path",
    "build_impl_graph",
    "find_specs_for_impl",
]
