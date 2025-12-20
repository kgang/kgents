"""
Principle Loader: File loading and parsing for principles.

Handles loading principle files from spec/principles/ directory
with caching for performance (principles change rarely).

Pattern: Crown Jewel Pattern #15 (No Hollow Services)
- Requires base_path parameter, not optional
- Validates path exists on construction

See: spec/principles/node.md
"""

from __future__ import annotations

import logging
import re
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

from .types import (
    AD_TASK_MAPPING,
    PRINCIPLE_AD_MAPPING,
    THE_SEVEN_PRINCIPLES,
    ADRendering,
    ConstitutionRendering,
    MetaPrincipleRendering,
    OperationalRendering,
    Principle,
)

logger = logging.getLogger(__name__)


@dataclass
class PrincipleLoader:
    """
    Loads principle files from the spec/principles directory.

    Provides caching for frequently accessed files since principles
    change rarely. All methods are synchronous file reads.

    Attributes:
        base_path: Path to spec/principles/ directory
        cache: Whether to cache loaded files

    Example:
        loader = PrincipleLoader(Path("spec/principles"), cache=True)
        content = await loader.load("CONSTITUTION.md")
    """

    base_path: Path
    cache: bool = True
    _cache: dict[str, str] = field(default_factory=dict, repr=False)
    _ad_cache: dict[int, dict[str, Any]] = field(default_factory=dict, repr=False)

    def __post_init__(self) -> None:
        """Validate base_path exists."""
        if not self.base_path.exists():
            logger.warning(f"Principles path does not exist: {self.base_path}")

    async def load(self, filename: str) -> str:
        """
        Load a principle file by name.

        Args:
            filename: File to load (e.g., "CONSTITUTION.md")

        Returns:
            File content as string
        """
        # Check cache
        if self.cache and filename in self._cache:
            return self._cache[filename]

        # Load file
        filepath = self.base_path / filename
        if not filepath.exists():
            logger.warning(f"Principle file not found: {filepath}")
            return f"# {filename}\n\n*File not found*"

        try:
            content = filepath.read_text(encoding="utf-8")
            if self.cache:
                self._cache[filename] = content
            return content
        except Exception as e:
            logger.error(f"Error loading {filepath}: {e}")
            return f"# {filename}\n\n*Error loading file: {e}*"

    async def load_section(self, filename: str, section: str) -> str:
        """
        Load a specific section from a file.

        Sections are identified by markdown headings (## Section Name).

        Args:
            filename: File to load
            section: Section name (e.g., "The Accursed Share")

        Returns:
            Section content
        """
        content = await self.load(filename)

        # Find section by heading
        # Match ## Section or # Section
        pattern = rf"^##?\s*{re.escape(section)}\s*$"
        lines = content.split("\n")

        start_idx = None
        end_idx = None

        for i, line in enumerate(lines):
            if re.match(pattern, line, re.IGNORECASE):
                start_idx = i
            elif start_idx is not None and re.match(r"^##?\s+", line):
                # Next section starts
                end_idx = i
                break

        if start_idx is None:
            return f"*Section '{section}' not found in {filename}*"

        section_lines = lines[start_idx:end_idx] if end_idx else lines[start_idx:]
        return "\n".join(section_lines)

    async def load_slices(self, slices: tuple[str, ...]) -> str:
        """
        Load multiple files and combine them.

        Args:
            slices: Tuple of filenames to load

        Returns:
            Combined content with separators
        """
        contents = []
        for filename in slices:
            content = await self.load(filename)
            contents.append(content)

        return "\n\n---\n\n".join(contents)

    async def load_constitution(self) -> ConstitutionRendering:
        """
        Load and parse the constitution.

        Returns:
            ConstitutionRendering with content and parsed principles
        """
        content = await self.load("CONSTITUTION.md")

        # Parse principles from content to enrich THE_SEVEN_PRINCIPLES
        # For now, we use the static definitions with loaded content
        principles = list(THE_SEVEN_PRINCIPLES)

        return ConstitutionRendering(
            content=content,
            principles=tuple(principles),
        )

    async def load_meta(self, section: str | None = None) -> MetaPrincipleRendering:
        """
        Load meta-principles.

        Args:
            section: Optional section to load (e.g., "The Accursed Share")

        Returns:
            MetaPrincipleRendering
        """
        if section:
            content = await self.load_section("meta.md", section)
        else:
            content = await self.load("meta.md")

        return MetaPrincipleRendering(content=content, section=section)

    async def load_operational(self) -> OperationalRendering:
        """
        Load operational principles.

        Returns:
            OperationalRendering
        """
        content = await self.load("operational.md")
        return OperationalRendering(content=content)

    async def load_ad(self, ad_id: int) -> ADRendering:
        """
        Load a specific architectural decision.

        Args:
            ad_id: AD number (1-13)

        Returns:
            ADRendering
        """
        # Check cache
        if self.cache and ad_id in self._ad_cache:
            cached = self._ad_cache[ad_id]
            return ADRendering(
                ad_id=ad_id,
                category=cached.get("category"),
                content=cached.get("content", ""),
                ads=(cached,),
            )

        # Find the AD file
        decisions_path = self.base_path / "decisions"
        pattern = f"AD-{ad_id:03d}*.md"

        matching_files = list(decisions_path.glob(pattern))
        if not matching_files:
            return ADRendering(
                ad_id=ad_id,
                category=None,
                content=f"*AD-{ad_id:03d} not found*",
                ads=(),
            )

        filepath = matching_files[0]
        content = filepath.read_text(encoding="utf-8")

        # Parse AD metadata from filename
        name_match = re.match(r"AD-(\d+)-(.+)\.md", filepath.name)
        ad_name = name_match.group(2) if name_match else "unknown"

        ad_data = {
            "id": ad_id,
            "name": ad_name.replace("-", " ").title(),
            "filename": filepath.name,
            "content": content,
        }

        if self.cache:
            self._ad_cache[ad_id] = ad_data

        return ADRendering(
            ad_id=ad_id,
            category=None,
            content=content,
            ads=(ad_data,),
        )

    async def load_ads_by_category(self, category: str) -> ADRendering:
        """
        Load all ADs in a category.

        Categories from INDEX.md:
        - categorical: AD-001, AD-002, AD-006
        - design-philosophy: AD-003, AD-004, AD-008
        - architecture: AD-005, AD-009
        - protocol: AD-007, AD-010, AD-011, AD-012
        - ui: AD-013

        Args:
            category: Category name

        Returns:
            ADRendering with all ADs in category
        """
        # Map category names to AD numbers
        category_map: dict[str, tuple[int, ...]] = {
            "categorical": (1, 2, 6),
            "design-philosophy": (3, 4, 8),
            "architecture": (5, 9),
            "protocol": (7, 10, 11, 12),
            "ui": (13,),
        }

        normalized = category.lower().replace(" ", "-").replace("_", "-")
        ad_ids = category_map.get(normalized, ())

        if not ad_ids:
            return ADRendering(
                ad_id=None,
                category=category,
                content=f"*Category '{category}' not found*",
                ads=(),
            )

        all_ads: list[dict[str, Any]] = []
        contents: list[str] = []

        for ad_id in ad_ids:
            rendering = await self.load_ad(ad_id)
            if rendering.ads:
                all_ads.extend(rendering.ads)
                contents.append(rendering.content)

        return ADRendering(
            ad_id=None,
            category=category,
            content="\n\n---\n\n".join(contents),
            ads=tuple(all_ads),
        )

    async def load_ad_index(self) -> ADRendering:
        """
        Load the AD index.

        Returns:
            ADRendering with index content
        """
        content = await self.load("decisions/INDEX.md")

        # Parse ADs from index
        # Extract all AD references
        ad_pattern = r"AD-(\d+)"
        ad_ids = sorted(set(int(m) for m in re.findall(ad_pattern, content)))

        ads_data: list[dict[str, Any]] = []
        for ad_id in ad_ids:
            ads_data.append({"id": ad_id})

        return ADRendering(
            ad_id=None,
            category="index",
            content=content,
            ads=tuple(ads_data),
        )

    async def load_ads_for_task(self, task: str) -> tuple[int, ...]:
        """
        Get AD IDs relevant to a task pattern.

        Args:
            task: Task description (e.g., "adding-agent", "agentese")

        Returns:
            Tuple of relevant AD IDs
        """
        # Check for exact match
        if task in AD_TASK_MAPPING:
            return AD_TASK_MAPPING[task]

        # Check for partial match
        task_lower = task.lower()
        for pattern, ads in AD_TASK_MAPPING.items():
            if pattern in task_lower or task_lower in pattern:
                return ads

        return ()

    async def load_anti_patterns(self, principle: int) -> tuple[str, ...]:
        """
        Get anti-patterns for a principle.

        Args:
            principle: Principle number (1-7)

        Returns:
            Tuple of anti-pattern descriptions
        """
        if 1 <= principle <= 7:
            return THE_SEVEN_PRINCIPLES[principle - 1].anti_patterns
        return ()

    async def load_puppets_for_principle(self, principle: int) -> tuple[str, ...]:
        """
        Get relevant puppets for healing a principle violation.

        Puppets are isomorphic structures that make solutions obvious.

        Args:
            principle: Principle number (1-7)

        Returns:
            Tuple of puppet descriptions
        """
        # Load puppets.md and extract relevant examples
        content = await self.load("puppets.md")

        # Map principles to relevant puppet examples
        puppet_map: dict[int, tuple[str, ...]] = {
            1: ("kgents taxonomy: Agent <- Genus <- Specification <- Implementation",),
            2: ("Slack: Message <- Thread <- Channel <- Workspace",),
            3: ("Git: Changes <- Commits <- Branches <- Repository",),
            4: ("Git: Interactive history, time travel, experimentation",),
            5: ("Git: Branches and merges for distributed agent memory",),
            6: ("Holonic: Cell <- Organism <- Ecosystem",),
            7: ("Taxonomy: Species <- Genus <- Family <- Order <- Class",),
        }

        return puppet_map.get(principle, ())

    async def load_related_ads(self, principle: int) -> tuple[int, ...]:
        """
        Get ADs related to a principle.

        Args:
            principle: Principle number (1-7)

        Returns:
            Tuple of AD IDs
        """
        return PRINCIPLE_AD_MAPPING.get(principle, ())

    def clear_cache(self) -> None:
        """Clear all caches."""
        self._cache.clear()
        self._ad_cache.clear()


# === Factory Function ===


def create_principle_loader(
    base_path: Path | str | None = None, cache: bool = True
) -> PrincipleLoader:
    """
    Create a PrincipleLoader with default or specified path.

    Args:
        base_path: Path to principles directory. Defaults to spec/principles.
        cache: Whether to cache loaded files.

    Returns:
        Configured PrincipleLoader
    """
    if base_path is None:
        # Find spec/principles relative to this file
        # impl/claude/services/principles/loader.py -> spec/principles
        this_file = Path(__file__)
        impl_root = this_file.parents[3]  # Up to impl/claude
        base_path = impl_root.parent / "spec" / "principles"

    if isinstance(base_path, str):
        base_path = Path(base_path)

    return PrincipleLoader(base_path=base_path, cache=cache)


# === Exports ===

__all__ = [
    "PrincipleLoader",
    "create_principle_loader",
]
