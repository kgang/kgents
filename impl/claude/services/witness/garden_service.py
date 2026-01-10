"""
GardenService: Aggregates specs, marks, and evidence into a living garden.

This service implements the WitnessGarden polynomial by:
1. Scanning spec files to create plants
2. Computing evidence ladders from marks/crystals
3. Detecting orphan artifacts
4. Building the complete GardenScene

The Core Insight:
    "The garden shows what *could* be witnessed, not just what *has* been."

See: spec/protocols/witness-assurance-surface.md
"""

from __future__ import annotations

import asyncio
import os
from collections import defaultdict
from datetime import datetime
from pathlib import Path
from typing import TYPE_CHECKING, AsyncIterator

from .garden import (
    AccountabilityLens,
    EvidenceLadder,
    GardenScene,
    OrphanWeed,
    SpecPath,
    SpecPlant,
)

if TYPE_CHECKING:
    from .crystal import Crystal
    from .crystal_store import CrystalStore
    from .mark import Mark
    from .trace_store import MarkStore


# =============================================================================
# Configuration
# =============================================================================

# Default spec directory relative to project root
DEFAULT_SPEC_PATTERNS = [
    "spec/**/*.md",
    "spec/*.md",
]

# Files to ignore in spec scanning
IGNORE_PATTERNS = {
    "_template.md",
    "_archive",
    "README.md",
}


# =============================================================================
# Garden Service
# =============================================================================


class GardenService:
    """
    Service for building and streaming WitnessGarden scenes.

    Usage:
        service = GardenService(
            spec_root="/path/to/spec",
            mark_store=mark_store,
            crystal_store=crystal_store,
        )

        # One-shot garden scene
        scene = await service.build_garden_scene(lens=AccountabilityLens.AUDIT)

        # Streaming updates
        async for scene in service.garden_stream(lens=AccountabilityLens.TRUST):
            yield scene
    """

    def __init__(
        self,
        spec_root: str | Path | None = None,
        mark_store: "MarkStore | None" = None,
        crystal_store: "CrystalStore | None" = None,
    ) -> None:
        """
        Initialize the garden service.

        Args:
            spec_root: Root directory for spec files. Defaults to project spec/.
            mark_store: Optional mark store for evidence computation.
            crystal_store: Optional crystal store for evidence computation.
        """
        self._spec_root = Path(spec_root) if spec_root else self._find_spec_root()
        self._mark_store = mark_store
        self._crystal_store = crystal_store

        # Cache for spec file metadata
        self._spec_cache: dict[str, dict[str, datetime]] = {}

    def _find_spec_root(self) -> Path:
        """Find the spec root directory."""
        # Walk up from current file to find project root
        current = Path(__file__).parent
        for _ in range(10):  # Max 10 levels up
            spec_dir = current / "spec"
            if spec_dir.exists():
                return spec_dir

            # Also check if we're in impl/claude
            if (current / "impl" / "claude").exists():
                return current / "spec"

            parent = current.parent
            if parent == current:
                break
            current = parent

        # Fallback: use current directory's spec folder
        return Path.cwd() / "spec"

    # =========================================================================
    # Spec Discovery
    # =========================================================================

    async def discover_specs(self) -> list[tuple[str, str, datetime | None]]:
        """
        Discover all spec files.

        Returns:
            List of (path, name, modified_at) tuples.
        """
        specs: list[tuple[str, str, datetime | None]] = []

        if not self._spec_root.exists():
            return specs

        # Walk the spec directory
        for md_file in self._spec_root.rglob("*.md"):
            # Skip ignored patterns
            if any(ignore in str(md_file) for ignore in IGNORE_PATTERNS):
                continue

            # Get relative path from spec root
            rel_path = str(md_file.relative_to(self._spec_root.parent))

            # Extract name from filename
            name = md_file.stem.replace("-", " ").replace("_", " ").title()

            # Get modification time
            try:
                mtime = datetime.fromtimestamp(md_file.stat().st_mtime)
            except OSError:
                mtime = None

            specs.append((rel_path, name, mtime))

        return specs

    # =========================================================================
    # Evidence Computation
    # =========================================================================

    async def compute_evidence_ladder(
        self,
        spec_path: str,
    ) -> EvidenceLadder:
        """
        Compute the evidence ladder for a spec.

        Aggregates evidence from:
        - Marks that reference this spec
        - Crystals that mention this spec
        - Tests that validate this spec

        Args:
            spec_path: Path to the spec file.

        Returns:
            EvidenceLadder with counts at each level.
        """
        ladder_data: dict[str, int] = defaultdict(int)

        # Count marks referencing this spec
        if self._mark_store:
            try:
                from .trace_store import MarkQuery

                # Note: query() is synchronous, returns Iterator[Mark]
                marks = list(self._mark_store.query(MarkQuery(limit=1000)))

                for mark in marks:
                    # Check if mark references this spec
                    if self._mark_references_spec(mark, spec_path):
                        # Classify by origin/type
                        if mark.origin == "prompt" or "prompt" in mark.tags:
                            ladder_data["prompt"] += 1
                        elif mark.origin == "trace" or "trace" in mark.tags:
                            ladder_data["trace"] += 1
                        elif mark.origin == "test" or "test" in mark.tags:
                            ladder_data["test"] += 1
                        elif mark.origin == "proof" or "proof" in mark.tags:
                            ladder_data["proof"] += 1
                        else:
                            # Default to human mark
                            ladder_data["mark"] += 1

            except Exception:
                pass  # Mark store not available

        # Count crystals mentioning this spec
        if self._crystal_store:
            try:
                from .crystal_store import CrystalQuery

                # Note: query() is synchronous, returns Iterator[Crystal]
                crystals = list(self._crystal_store.query(CrystalQuery(limit=1000)))

                for crystal in crystals:
                    if self._crystal_references_spec(crystal, spec_path):
                        # Crystals add to mark count (compressed marks)
                        ladder_data["mark"] += 1

            except Exception:
                pass  # Crystal store not available

        # Check for orphan status
        if ladder_data.get("prompt", 0) == 0 and sum(ladder_data.values()) > 0:
            # Has evidence but no prompt lineage = orphan
            ladder_data["orphan"] = 1

        return EvidenceLadder(
            orphan=ladder_data.get("orphan", 0),
            prompt=ladder_data.get("prompt", 0),
            trace=ladder_data.get("trace", 0),
            mark=ladder_data.get("mark", 0),
            test=ladder_data.get("test", 0),
            proof=ladder_data.get("proof", 0),
            bet=ladder_data.get("bet", 0),
        )

    def _mark_references_spec(self, mark: "Mark", spec_path: str) -> bool:
        """Check if a mark references a spec."""
        spec_stem = Path(spec_path).stem.lower()

        # Check metadata
        if mark.metadata:
            spec_ref = mark.metadata.get("spec") or mark.metadata.get("spec_path", "")
            if spec_stem in spec_ref.lower():
                return True

        # Check response content
        if spec_stem in mark.response.content.lower():
            return True

        # Check tags
        for tag in mark.tags:
            if spec_stem in tag.lower():
                return True

        return False

    def _crystal_references_spec(self, crystal: "Crystal", spec_path: str) -> bool:
        """Check if a crystal references a spec."""
        spec_stem = Path(spec_path).stem.lower()

        # Check insight/significance
        if spec_stem in crystal.insight.lower():
            return True
        if spec_stem in crystal.significance.lower():
            return True

        # Check topics
        for topic in crystal.topics:
            if spec_stem in topic.lower():
                return True

        return False

    # =========================================================================
    # Orphan Detection
    # =========================================================================

    async def detect_orphans(self) -> list[OrphanWeed]:
        """
        Detect artifacts without prompt lineage.

        An artifact is an orphan if:
        - It has no prompt ancestor in its lineage
        - It was created without clear attribution

        Returns:
            List of OrphanWeed instances.
        """
        orphans: list[OrphanWeed] = []

        if not self._mark_store:
            return orphans

        try:
            from .trace_store import MarkQuery

            # Note: query() is synchronous, returns Iterator[Mark]
            marks = list(self._mark_store.query(MarkQuery(limit=1000)))

            for mark in marks:
                # Check if mark has no lineage
                if not mark.links and mark.origin not in ("prompt", "user"):
                    # No links and not from prompt = orphan
                    orphans.append(
                        OrphanWeed(
                            path=str(mark.id),
                            artifact_type="mark",
                            created_at=mark.timestamp,
                            suggested_prompt=self._suggest_prompt(mark),
                        )
                    )

        except Exception:
            pass

        return orphans

    def _suggest_prompt(self, mark: "Mark") -> str | None:
        """Suggest a prompt that might have created this mark."""
        # Try to infer from content
        content = mark.response.content.lower()

        if "test" in content:
            return "Run tests for this module"
        elif "fix" in content or "bug" in content:
            return "Fix the bug in this code"
        elif "implement" in content:
            return "Implement this feature"
        elif "refactor" in content:
            return "Refactor this code"

        return None

    # =========================================================================
    # Garden Building
    # =========================================================================

    async def build_garden_scene(
        self,
        lens: AccountabilityLens = AccountabilityLens.AUDIT,
        density: str = "comfortable",
    ) -> GardenScene:
        """
        Build a complete garden scene.

        Args:
            lens: The accountability lens to apply.
            density: Display density (compact/comfortable/spacious).

        Returns:
            GardenScene with all specs and orphans.
        """
        # Discover specs
        spec_files = await self.discover_specs()

        # Build plants for each spec
        plants: list[SpecPlant] = []
        total_confidence = 0.0

        for spec_path, name, mtime in spec_files:
            # Compute evidence ladder
            ladder = await self.compute_evidence_ladder(spec_path)

            # Create plant
            plant = SpecPlant.from_spec_file(
                path=spec_path,
                name=name,
                ladder=ladder,
                last_evidence_at=mtime,
            )

            plants.append(plant)
            total_confidence += plant.confidence

        # Detect orphans
        orphans = await self.detect_orphans()

        # Compute overall health
        overall_health = total_confidence / len(plants) if plants else 0.0

        # Apply lens filtering
        filtered_plants = self._apply_lens(plants, lens)

        return GardenScene(
            specs=tuple(filtered_plants),
            orphans=tuple(orphans),
            overall_health=overall_health,
            lens=lens,
            density=density,  # type: ignore[arg-type]
        )

    def _apply_lens(
        self,
        plants: list[SpecPlant],
        lens: AccountabilityLens,
    ) -> list[SpecPlant]:
        """
        Apply accountability lens filtering.

        - AUDIT: Show everything
        - AUTHOR: Show only specs with my marks (TODO: user context)
        - TRUST: Show only summary (high-level health)
        """
        if lens == AccountabilityLens.AUDIT:
            # Show everything
            return plants

        elif lens == AccountabilityLens.AUTHOR:
            # Show only specs with evidence (TODO: filter by user)
            return [p for p in plants if p.evidence_levels.total_evidence > 0]

        elif lens == AccountabilityLens.TRUST:
            # Show everything but could simplify representation
            # (Frontend can use this lens to show simplified view)
            return plants

        return plants

    # =========================================================================
    # Streaming
    # =========================================================================

    async def garden_stream(
        self,
        lens: AccountabilityLens = AccountabilityLens.AUDIT,
        density: str = "comfortable",
        poll_interval: float = 5.0,
    ) -> AsyncIterator[GardenScene]:
        """
        Stream garden updates via polling.

        Yields a new GardenScene whenever the garden state changes.

        Args:
            lens: The accountability lens to apply.
            density: Display density.
            poll_interval: Seconds between polls.

        Yields:
            GardenScene instances.
        """
        last_scene: GardenScene | None = None

        while True:
            try:
                # Build current scene
                scene = await self.build_garden_scene(lens=lens, density=density)

                # Check if changed (simple comparison on overall_health + counts)
                if last_scene is None or self._scene_changed(last_scene, scene):
                    yield scene
                    last_scene = scene

                # Wait before next poll
                await asyncio.sleep(poll_interval)

            except asyncio.CancelledError:
                # Clean shutdown
                break
            except Exception as e:
                # Log error but continue streaming
                import logging

                logging.getLogger(__name__).warning(f"Garden stream error: {e}")
                await asyncio.sleep(poll_interval)

    def _scene_changed(self, old: GardenScene, new: GardenScene) -> bool:
        """Check if the scene has meaningfully changed."""
        # Quick checks
        if old.total_specs != new.total_specs:
            return True
        if old.witnessed_count != new.witnessed_count:
            return True
        if old.orphan_count != new.orphan_count:
            return True
        if abs(old.overall_health - new.overall_health) > 0.01:
            return True

        return False


# =============================================================================
# Factory Function
# =============================================================================


def get_garden_service(
    spec_root: str | Path | None = None,
    mark_store: "MarkStore | None" = None,
    crystal_store: "CrystalStore | None" = None,
) -> GardenService:
    """
    Get a garden service instance.

    This is the preferred way to create a GardenService, allowing for
    dependency injection in tests.
    """
    return GardenService(
        spec_root=spec_root,
        mark_store=mark_store,
        crystal_store=crystal_store,
    )


# =============================================================================
# Module Exports
# =============================================================================

__all__ = [
    "GardenService",
    "get_garden_service",
]
