"""
Evidence Correlation: Link witness marks with git commits.

This module implements the hypothesis:
    "Systematic decision witnessing improves code quality and reduces rework."

It correlates witness marks with git history using four correlation types:
1. REFERENCES_COMMIT - Mark explicitly mentions a commit SHA
2. SAME_TIMESTAMP - Mark and commit within temporal window (±5min)
3. SAME_FILES - Mark mentions files changed in commit
4. DECISION_LED_TO - Decision mark temporally precedes implementation commits

Philosophy:
    "The proof IS the decision. The mark IS the witness."
    Evidence correlation validates that marks correlate with better outcomes.

Usage:
    correlator = EvidenceCorrelator(witness_persistence, repo_path)
    links = await correlator.correlate_marks_with_commits(since=datetime.now() - timedelta(days=30))
    chain = await correlator.trace_decision_to_commits(decision_mark_id="mark-123")
    gotchas = await correlator.correlate_gotchas_with_bugs()

See: spec/protocols/living-spec-evidence.md
See: spec/protocols/witness-primitives.md
See: docs/skills/crown-jewel-patterns.md (Pattern 7: Append-Only History)
"""

from __future__ import annotations

import re
from collections import Counter, defaultdict
from datetime import datetime, timedelta, timezone
from pathlib import Path
from typing import TYPE_CHECKING

from services.archaeology.mining import Commit, parse_git_log

from .models import (
    BugCorrelation,
    CommitPattern,
    CorrelationType,
    DecisionCommitChain,
    GotchaVsBugCorrelation,
    MarkCommitLink,
)

if TYPE_CHECKING:
    from services.witness.persistence import WitnessPersistence


# =============================================================================
# Constants
# =============================================================================

TEMPORAL_WINDOW_MINUTES = 5  # Marks/commits within ±5 min are correlated
DECISION_LOOKBACK_HOURS = 48  # Look 48h ahead for implementation commits
SHA_PATTERN = re.compile(r"\b[0-9a-f]{7,40}\b")  # Match git SHAs (7-40 chars)
FILE_PATH_PATTERN = re.compile(
    r"(?:^|[\s\"`'])([a-zA-Z0-9_/.-]+\.(?:py|ts|tsx|js|jsx|md|yaml|yml|json|toml))\b"
)


# =============================================================================
# EvidenceCorrelator
# =============================================================================


class EvidenceCorrelator:
    """
    Correlate witness marks with git history.

    This class validates the witness hypothesis by finding correlations between
    decision marks, gotcha annotations, and git commits. It measures whether
    systematic marking improves outcomes (fewer bugs, less rework, faster impl).

    Pattern: Container Owns Workflow (crown-jewel-patterns.md)
    - Owns the correlation logic and algorithms
    - Uses WitnessPersistence for marks (read-only)
    - Uses archaeology.parse_git_log for commits (read-only)
    - Returns frozen dataclass results
    """

    def __init__(
        self,
        witness_persistence: WitnessPersistence | None,
        repo_path: Path | str,
    ) -> None:
        """
        Initialize EvidenceCorrelator.

        Args:
            witness_persistence: Witness persistence layer (None = graceful degradation)
            repo_path: Path to git repository root

        Raises:
            ValueError: If repo_path is not a valid git repository
        """
        self.witness = witness_persistence
        self.repo_path = Path(repo_path)

        # Validate git repository
        git_dir = self.repo_path / ".git"
        if not git_dir.exists():
            raise ValueError(f"Not a git repository: {self.repo_path}")

    async def correlate_marks_with_commits(
        self,
        since: datetime | None = None,
        max_commits: int = 500,
    ) -> list[MarkCommitLink]:
        """
        Find correlations between witness marks and git commits.

        Correlation types:
        - REFERENCES_COMMIT: Mark explicitly references commit SHA in metadata
        - SAME_TIMESTAMP: Mark and commit within ±5 min temporal window
        - SAME_FILES: Mark mentions files that were changed in commit

        Args:
            since: Only correlate marks/commits after this timestamp
            max_commits: Maximum commits to analyze (default 500)

        Returns:
            List of MarkCommitLink correlations ordered by strength descending
        """
        # Graceful degradation if no witness persistence
        if self.witness is None:
            return []

        # Get marks
        marks = await self.witness.get_marks(
            limit=max_commits,
            since=since,
        )

        if not marks:
            return []

        # Get commits
        commits = parse_git_log(repo_path=self.repo_path, max_commits=max_commits)

        if not commits:
            return []

        # Filter commits by date if specified
        if since:
            # Ensure since is timezone-aware
            if since.tzinfo is None:
                since = since.replace(tzinfo=timezone.utc)
            commits = [c for c in commits if c.timestamp >= since]

        # Find correlations
        links: list[MarkCommitLink] = []

        for mark in marks:
            # Try to find correlations for this mark
            mark_links = self._find_correlations_for_mark(mark, commits)
            links.extend(mark_links)

        # Sort by correlation strength descending
        links.sort(key=lambda link: link.correlation_strength, reverse=True)

        return links

    async def trace_decision_to_commits(
        self,
        decision_mark_id: str,
        lookback_hours: int = DECISION_LOOKBACK_HOURS,
    ) -> DecisionCommitChain | None:
        """
        Trace from a decision mark to subsequent implementation commits.

        This validates: "Decision marks reduce rework and improve quality."

        Args:
            decision_mark_id: The decision mark ID to trace from
            lookback_hours: Hours to look ahead for implementation (default 48)

        Returns:
            DecisionCommitChain if correlations found, None otherwise
        """
        # Graceful degradation
        if self.witness is None:
            return None

        # Get the decision mark
        mark = await self.witness.get_mark(decision_mark_id)
        if not mark:
            return None

        # Extract decision context from mark
        # Decision marks have reasoning field with kent/claude/synthesis
        # For now, use action as decision summary
        decision_timestamp = mark.timestamp

        # Get commits after the decision
        end_timestamp = decision_timestamp + timedelta(hours=lookback_hours)
        commits = parse_git_log(repo_path=self.repo_path, max_commits=500)

        # Filter to commits after decision and before end
        relevant_commits = [
            c for c in commits if decision_timestamp <= c.timestamp <= end_timestamp
        ]

        if not relevant_commits:
            return None

        # Convert to CommitPattern
        patterns = [self._commit_to_pattern(c) for c in relevant_commits]

        # Calculate metrics
        time_to_first = (
            (relevant_commits[0].timestamp - decision_timestamp).total_seconds() / 3600
            if relevant_commits
            else 0.0
        )

        total_churn = sum(p.churn for p in patterns)

        # Detect reverts (commits with "revert" in message)
        reverts = sum(1 for p in patterns if p.is_revert)

        # Estimate rework ratio (rough heuristic: deletions / insertions)
        # High deletion ratio suggests rework
        total_insertions = sum(p.insertions for p in patterns)
        total_deletions = sum(p.deletions for p in patterns)
        rework_ratio = total_deletions / total_insertions if total_insertions > 0 else 0.0

        return DecisionCommitChain(
            decision_mark_id=decision_mark_id,
            decision_timestamp=decision_timestamp,
            decision_kent=mark.action,  # Simplified - real impl would parse reasoning
            decision_claude="",  # Simplified
            decision_synthesis=mark.reasoning or "",
            subsequent_commits=tuple(patterns),
            time_to_first_commit=time_to_first,
            total_commits=len(patterns),
            total_churn=total_churn,
            reverts=reverts,
            rework_ratio=min(rework_ratio, 1.0),  # Cap at 1.0
        )

    async def correlate_gotchas_with_bugs(
        self,
        max_commits: int = 500,
    ) -> GotchaVsBugCorrelation | None:
        """
        Compare gotcha annotations vs bug-fix commits.

        This validates: "Capturing gotchas reduces repeat mistakes."

        Args:
            max_commits: Maximum commits to analyze

        Returns:
            GotchaVsBugCorrelation if gotcha marks found, None otherwise
        """
        # Graceful degradation
        if self.witness is None:
            return None

        # Get gotcha marks (marks with "gotcha" or "evidence:gotcha" tags)
        marks = await self.witness.get_marks(limit=100)
        gotcha_marks = [
            m for m in marks if any(tag in ("gotcha", "evidence:gotcha") for tag in m.tags)
        ]

        if not gotcha_marks:
            return None

        # Use the first gotcha as example (real impl would aggregate)
        gotcha = gotcha_marks[0]

        # Extract file patterns from gotcha action/reasoning
        file_patterns = self._extract_file_paths(f"{gotcha.action} {gotcha.reasoning or ''}")

        # Get all commits
        commits = parse_git_log(repo_path=self.repo_path, max_commits=max_commits)

        # Find bug fixes in the same files
        bug_commits = [c for c in commits if c.commit_type == "fix"]
        related_bugs = []

        for bug_commit in bug_commits:
            # Check if bug touches any of the gotcha files
            bug_files = set(bug_commit.files_changed)
            gotcha_files = set(file_patterns)

            if bug_files & gotcha_files:
                # Related bug
                related_bugs.append(
                    BugCorrelation(
                        bug_fix_sha=bug_commit.sha,
                        bug_fix_timestamp=bug_commit.timestamp,
                        files_fixed=bug_commit.files_changed,
                        time_to_fix=None,  # Would need more analysis
                    )
                )

        # Split bugs into before/after gotcha
        gotcha_time = gotcha.timestamp
        bugs_before = [b for b in related_bugs if b.bug_fix_timestamp < gotcha_time]
        bugs_after = [b for b in related_bugs if b.bug_fix_timestamp >= gotcha_time]

        # Calculate reduction
        before_count = len(bugs_before)
        after_count = len(bugs_after)

        reduction = (before_count - after_count) / before_count if before_count > 0 else 0.0

        return GotchaVsBugCorrelation(
            gotcha_timestamp=gotcha_time,
            gotcha_section=gotcha.action,
            gotcha_note=gotcha.reasoning or "",
            gotcha_file_patterns=tuple(file_patterns),
            related_bugs=tuple(related_bugs[:10]),  # Top 10
            bugs_before_gotcha=before_count,
            bugs_after_gotcha=after_count,
            reduction_ratio=max(reduction, 0.0),  # Don't show negative reduction
        )

    # =========================================================================
    # Private Helpers
    # =========================================================================

    def _find_correlations_for_mark(
        self,
        mark: object,  # MarkResult from witness.persistence
        commits: list[Commit],
    ) -> list[MarkCommitLink]:
        """
        Find all correlations between a mark and commits.

        Returns list of MarkCommitLink (may be empty).
        """
        from services.witness.persistence import MarkResult

        if not isinstance(mark, MarkResult):
            return []

        links: list[MarkCommitLink] = []
        mark_content = f"{mark.action} {mark.reasoning or ''}"

        # 1. Check for explicit SHA references
        sha_refs = SHA_PATTERN.findall(mark_content)
        for commit in commits:
            if any(commit.sha.startswith(ref) for ref in sha_refs):
                links.append(
                    MarkCommitLink(
                        mark_id=mark.mark_id,
                        mark_timestamp=mark.timestamp,
                        mark_action=mark.action,
                        mark_metadata={
                            "reasoning": mark.reasoning,
                            "tags": mark.tags,
                            "principles": mark.principles,
                        },
                        commit_sha=commit.sha,
                        commit_timestamp=commit.timestamp,
                        correlation_type=CorrelationType.REFERENCES_COMMIT,
                        correlation_strength=1.0,  # Explicit reference = max strength
                        evidence=f"Mark explicitly references commit {commit.sha[:7]}",
                    )
                )

        # 2. Check for temporal proximity (±5 minutes)
        for commit in commits:
            time_delta = abs((mark.timestamp - commit.timestamp).total_seconds())
            if time_delta <= TEMPORAL_WINDOW_MINUTES * 60:
                # Within temporal window
                strength = 1.0 - (time_delta / (TEMPORAL_WINDOW_MINUTES * 60))
                links.append(
                    MarkCommitLink(
                        mark_id=mark.mark_id,
                        mark_timestamp=mark.timestamp,
                        mark_action=mark.action,
                        mark_metadata={
                            "reasoning": mark.reasoning,
                            "tags": mark.tags,
                            "principles": mark.principles,
                        },
                        commit_sha=commit.sha,
                        commit_timestamp=commit.timestamp,
                        correlation_type=CorrelationType.SAME_TIMESTAMP,
                        correlation_strength=strength * 0.8,  # Scale down vs explicit
                        evidence=f"Mark and commit within {int(time_delta / 60)}min",
                    )
                )

        # 3. Check for file path overlap
        mark_files = set(self._extract_file_paths(mark_content))
        if mark_files:
            for commit in commits:
                commit_files = set(commit.files_changed)
                overlap = mark_files & commit_files

                if overlap:
                    # Calculate strength based on overlap ratio
                    strength = len(overlap) / len(mark_files)
                    links.append(
                        MarkCommitLink(
                            mark_id=mark.mark_id,
                            mark_timestamp=mark.timestamp,
                            mark_action=mark.action,
                            mark_metadata={
                                "reasoning": mark.reasoning,
                                "tags": mark.tags,
                                "principles": mark.principles,
                            },
                            commit_sha=commit.sha,
                            commit_timestamp=commit.timestamp,
                            correlation_type=CorrelationType.SAME_FILES,
                            correlation_strength=strength * 0.7,  # Scale down
                            evidence=f"Mark mentions {len(overlap)} file(s) changed in commit: {', '.join(list(overlap)[:3])}",
                        )
                    )

        return links

    def _extract_file_paths(self, text: str) -> list[str]:
        """
        Extract file paths from text using regex.

        Matches paths like:
        - services/witness/persistence.py
        - impl/claude/web/src/App.tsx
        - spec/protocols/witness.md

        Returns list of file paths found.
        """
        matches = FILE_PATH_PATTERN.findall(text)
        # Deduplicate while preserving order
        seen = set()
        paths = []
        for match in matches:
            if match not in seen:
                seen.add(match)
                paths.append(match)
        return paths

    def _commit_to_pattern(self, commit: Commit) -> CommitPattern:
        """Convert archaeology Commit to evidence CommitPattern."""
        return CommitPattern(
            sha=commit.sha,
            timestamp=commit.timestamp,
            author=commit.author,
            message=commit.message,
            files_changed=len(commit.files_changed),
            insertions=commit.insertions,
            deletions=commit.deletions,
            commit_type=commit.commit_type,
            scope=commit.scope,
            is_merge=False,  # Would need to parse message for "Merge"
            is_revert="revert" in commit.message.lower(),
        )


# =============================================================================
# Exports
# =============================================================================

__all__ = [
    "EvidenceCorrelator",
    "TEMPORAL_WINDOW_MINUTES",
    "DECISION_LOOKBACK_HOURS",
]
