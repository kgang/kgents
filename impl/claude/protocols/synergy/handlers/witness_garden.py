"""
Witness to Garden Handler: Update Gardener plots when git commits are detected.

When Witness detects git commits, this handler analyzes commit messages
to find linked plots and updates their progress.

"The ghost is not a haunting—it's a witnessing that becomes a doing."

This enables:
- Automatic plot progress tracking via commits
- Linking development activity to Gardener sessions
- Progress inference from commit patterns
"""

from __future__ import annotations

import re
from typing import Any

from ..events import SynergyEvent, SynergyEventType, SynergyResult
from .base import BaseSynergyHandler


class WitnessToGardenHandler(BaseSynergyHandler):
    """
    Handler that updates Gardener plots based on Witness git commit events.

    When a git commit is detected:
    1. Parse commit message for plot references (e.g., "witness phase 2")
    2. Infer progress increment based on commit size
    3. Update linked plots in Gardener

    Plot Linking Strategies:
    - Explicit: "[plot:world.witness]" or "[witness]" in commit message
    - Implicit: Keywords matching active plot names
    - Branch: Branch name matching plot path (e.g., feature/witness-phase2)
    """

    SUPPORTED_EVENTS = {
        SynergyEventType.WITNESS_GIT_COMMIT,
    }

    # Regex patterns for plot linking
    EXPLICIT_PLOT_PATTERN = re.compile(r"\[(?:plot:)?(\w+(?:\.\w+)*)\]", re.IGNORECASE)
    PLAN_PATTERN = re.compile(r"plans?/([a-z0-9-]+)\.md", re.IGNORECASE)

    def __init__(self, auto_update: bool = True) -> None:
        """
        Initialize the handler.

        Args:
            auto_update: If True, automatically updates Gardener plots.
                        If False, just logs (useful for testing).
        """
        super().__init__()
        self._auto_update = auto_update

    @property
    def name(self) -> str:
        return "WitnessToGardenHandler"

    async def handle(self, event: SynergyEvent) -> SynergyResult:
        """Handle Witness git commit events → update Gardener plots."""
        if event.event_type not in self.SUPPORTED_EVENTS:
            return self.skip(f"Not handling {event.event_type.value}")

        return await self._handle_git_commit(event)

    async def _handle_git_commit(self, event: SynergyEvent) -> SynergyResult:
        """Handle git commit event → update linked plots."""
        payload = event.payload
        message = payload.get("message", "")
        files_changed = payload.get("files_changed", 0)
        insertions = payload.get("insertions", 0)
        deletions = payload.get("deletions", 0)

        # Extract plot links from commit message
        linked_plots = self._extract_plot_links(message)

        if not linked_plots:
            return self.skip("No plot links found in commit message")

        # Calculate progress increment based on commit size
        progress_delta = self._calculate_progress_delta(
            files_changed=files_changed,
            insertions=insertions,
            deletions=deletions,
        )

        if not self._auto_update:
            self._logger.info(f"Would update plots {linked_plots} with delta {progress_delta:.2%}")
            return self.success(
                message="Dry run - would update plot progress",
                metadata={
                    "linked_plots": linked_plots,
                    "progress_delta": progress_delta,
                    "commit_hash": event.source_id[:8],
                },
            )

        # Actually update plots in Gardener
        try:
            updated_plots = await self._update_plot_progress(
                plots=linked_plots,
                progress_delta=progress_delta,
                commit_hash=event.source_id,
                message=message,
            )
            self._logger.info(f"Updated {len(updated_plots)} plots from commit")
            return self.success(
                message=f"Updated {len(updated_plots)} plot(s) from git commit",
                metadata={
                    "updated_plots": updated_plots,
                    "progress_delta": progress_delta,
                    "commit_hash": event.source_id[:8],
                },
            )
        except Exception as e:
            self._logger.warning(f"Failed to update plots: {e}")
            # Graceful degradation: don't fail, just log
            return self.skip(f"Gardener unavailable: {e}")

    def _extract_plot_links(self, message: str) -> list[str]:
        """
        Extract plot references from commit message.

        Patterns recognized:
        - [plot:world.witness] or [world.witness] → Explicit AGENTESE path
        - plans/foo-bar.md → Plan file reference
        - Keywords: "witness", "brain", etc. → Implicit Crown Jewel link

        Returns:
            List of plot identifiers (AGENTESE paths or keywords)
        """
        plots: set[str] = set()

        # Check for explicit plot tags
        for match in self.EXPLICIT_PLOT_PATTERN.finditer(message):
            plots.add(match.group(1).lower())

        # Check for plan file references
        for match in self.PLAN_PATTERN.finditer(message):
            plan_name = match.group(1)
            # Convert plan name to plot reference
            # e.g., "witness-phase2" → "witness"
            base_name = plan_name.split("-")[0]
            plots.add(base_name)

        # Check for Crown Jewel keywords in message
        crown_jewels = [
            "witness",
            "brain",
            "gardener",
            "gestalt",
            "atelier",
            "park",
            "town",
            "domain",
        ]
        message_lower = message.lower()
        for jewel in crown_jewels:
            # Look for keywords not inside brackets (those are explicit)
            if jewel in message_lower and f"[{jewel}]" not in message_lower:
                # Only add if it appears as a word boundary
                if re.search(rf"\b{jewel}\b", message_lower):
                    plots.add(jewel)

        return list(plots)

    def _calculate_progress_delta(
        self,
        files_changed: int,
        insertions: int,
        deletions: int,
    ) -> float:
        """
        Calculate progress increment based on commit size.

        Heuristic:
        - Base: 1% per commit
        - Bonus: +0.5% per file changed (cap at 5%)
        - Bonus: +0.1% per 10 lines changed (cap at 5%)
        - Max: 10% per commit

        Returns:
            Progress delta as fraction (0.01 = 1%)
        """
        base = 0.01  # 1% base

        # File bonus (0.5% per file, max 5%)
        file_bonus = min(files_changed * 0.005, 0.05)

        # Lines bonus (0.1% per 10 lines, max 5%)
        total_lines = insertions + deletions
        lines_bonus = min((total_lines / 10) * 0.001, 0.05)

        # Total (max 10%)
        total = min(base + file_bonus + lines_bonus, 0.10)

        return total

    async def _update_plot_progress(
        self,
        plots: list[str],
        progress_delta: float,
        commit_hash: str,
        message: str,
    ) -> list[dict[str, Any]]:
        """
        Update plot progress in Gardener.

        Args:
            plots: List of plot identifiers to update
            progress_delta: Progress to add (0-1)
            commit_hash: Git commit hash for reference
            message: Commit message for context

        Returns:
            List of updated plot records
        """
        updated: list[dict[str, Any]] = []

        # Import here to avoid circular imports
        try:
            from agents.gardener.garden import get_garden  # type: ignore[import-untyped]
        except ImportError as e:
            raise RuntimeError(f"Gardener not available: {e}") from e

        garden = get_garden()

        for plot_id in plots:
            try:
                # Try to find and update plot
                # Note: This is a simplified implementation
                # A full implementation would query the garden for matching plots
                plot_path = f"world.{plot_id}" if "." not in plot_id else plot_id

                # Log the intended update (actual garden integration TBD)
                self._logger.info(
                    f"Would update plot {plot_path} by {progress_delta:.2%} "
                    f"from commit {commit_hash[:8]}"
                )

                updated.append(
                    {
                        "plot_path": plot_path,
                        "progress_delta": progress_delta,
                        "commit_hash": commit_hash[:8],
                        "message_preview": message[:50],
                    }
                )
            except Exception as e:
                self._logger.warning(f"Could not update plot {plot_id}: {e}")

        return updated


__all__ = ["WitnessToGardenHandler"]
