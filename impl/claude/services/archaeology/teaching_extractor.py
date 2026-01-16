"""
Commit Teaching Extractor: Extract TeachingMoments from git commits.

This module bridges the gap between git archaeology and the TeachingCrystal system:
    Commit → TeachingMoment → TeachingCrystal (via living_docs.crystallizer)

Teaching extraction is based on commit message patterns:
- fix: → gotcha (something was broken, now fixed)
- revert: → critical warning (approach failed)
- feat: + test → pattern (new capability with verification)
- refactor: → decision (architectural choice)
- BREAKING: → critical (migration needed)

See: spec/protocols/repo-archaeology.md, plans/git-archaeology-backfill.md
"""

from __future__ import annotations

import re
from dataclasses import dataclass
from typing import Literal, Sequence

from services.living_docs.types import TeachingMoment

from .mining import Commit
from .patterns import match_file_to_features


@dataclass(frozen=True)
class CommitTeaching:
    """
    A teaching moment extracted from a commit, enriched with context.

    Wraps TeachingMoment with additional metadata about the source commit
    and affected features.
    """

    teaching: TeachingMoment
    commit: Commit
    features: tuple[str, ...]  # Which features this teaching applies to
    category: str  # gotcha | pattern | decision | warning | critical


class CommitTeachingExtractor:
    """
    Extract TeachingMoments from git commits.

    The git log is a goldmine of "what went wrong" (fixes),
    "what we tried and reverted" (warnings), and "what we decided" (decisions).

    Each extraction strategy examines different commit patterns.
    """

    def extract_all(self, commits: Sequence[Commit]) -> list[CommitTeaching]:
        """
        Extract all teachings from a sequence of commits.

        Applies all extraction strategies in order:
        1. fix: commits → gotchas
        2. revert: commits → warnings
        3. BREAKING: commits → critical warnings
        4. refactor: commits → decisions
        5. feat: with test → patterns
        """
        teachings: list[CommitTeaching] = []

        for commit in commits:
            teaching = (
                self._extract_from_fix(commit)
                or self._extract_from_revert(commit)
                or self._extract_from_breaking(commit)
                or self._extract_from_refactor(commit)
                or self._extract_from_feat_with_test(commit)
            )

            if teaching:
                teachings.append(teaching)

        return teachings

    def _extract_from_fix(self, commit: Commit) -> CommitTeaching | None:
        """
        Extract gotchas from fix: commits.

        Fix commits encode "something was wrong, now it's fixed".
        The commit message often contains the insight.

        Example:
            "fix(brain): Handle empty capture list"
            → "Empty capture list caused crash in Brain - now handled"
        """
        if commit.commit_type != "fix":
            return None

        # Parse the fix message
        # Pattern: "fix[(scope)]: <description>"
        message = commit.message

        # Extract the actual fix description after the prefix
        if ": " in message:
            description = message.split(": ", 1)[1]
        else:
            description = message

        # Determine severity based on file count and churn
        severity: Literal["info", "warning", "critical"] = "warning"
        if commit.churn > 100 or len(commit.files_changed) > 5:
            severity = "critical"
        elif commit.churn < 20:
            severity = "info"

        # Build insight - emphasize what was learned
        scope = commit.scope or "system"
        insight = f"Bug fixed in {scope}: {description}"

        # Add evidence (the commit itself)
        evidence = f"commit:{commit.sha[:8]}"

        teaching = TeachingMoment(
            insight=insight,
            severity=severity,
            evidence=evidence,
            commit=commit.sha[:8],
        )

        features = tuple(
            feature for file in commit.files_changed for feature in match_file_to_features(file)
        )

        return CommitTeaching(
            teaching=teaching,
            commit=commit,
            features=features or ("general",),
            category="gotcha",
        )

    def _extract_from_revert(self, commit: Commit) -> CommitTeaching | None:
        """
        Extract warnings from revert: commits.

        Reverts are especially valuable - they encode "we tried this, it failed".
        Critical warnings that should prevent future attempts at the same mistake.
        """
        msg_lower = commit.message.lower()
        if not msg_lower.startswith("revert"):
            return None

        # Parse what was reverted
        # Pattern: "Revert \"<original message>\"" or "revert: <description>"
        if '"' in commit.message:
            # Git auto-generated revert
            original = commit.message.split('"')[1] if '"' in commit.message else commit.message
        elif ": " in commit.message:
            original = commit.message.split(": ", 1)[1]
        else:
            original = commit.message

        insight = f"Approach reverted: {original}. The implementation did not work as expected."

        teaching = TeachingMoment(
            insight=insight,
            severity="critical",
            evidence=f"revert:commit:{commit.sha[:8]}",
            commit=commit.sha[:8],
        )

        features = tuple(
            feature for file in commit.files_changed for feature in match_file_to_features(file)
        )

        return CommitTeaching(
            teaching=teaching,
            commit=commit,
            features=features or ("general",),
            category="warning",
        )

    def _extract_from_breaking(self, commit: Commit) -> CommitTeaching | None:
        """
        Extract critical warnings from BREAKING: commits.

        Breaking changes require migration - they're critical to know about.
        """
        if "BREAKING" not in commit.message.upper():
            return None

        # Extract the breaking change description
        # Pattern: "BREAKING: <description>" or "... BREAKING CHANGE: <description>"
        breaking_match = re.search(r"BREAKING[^:]*:\s*(.+)", commit.message, re.IGNORECASE)
        if breaking_match:
            description = breaking_match.group(1).strip()
        else:
            description = commit.message

        insight = f"Breaking change: {description}. Migration may be required."

        teaching = TeachingMoment(
            insight=insight,
            severity="critical",
            evidence=f"breaking:commit:{commit.sha[:8]}",
            commit=commit.sha[:8],
        )

        features = tuple(
            feature for file in commit.files_changed for feature in match_file_to_features(file)
        )

        return CommitTeaching(
            teaching=teaching,
            commit=commit,
            features=features or ("general",),
            category="critical",
        )

    def _extract_from_refactor(self, commit: Commit) -> CommitTeaching | None:
        """
        Extract decisions from refactor: commits.

        Refactors often encode architectural decisions worth remembering.
        """
        if commit.commit_type != "refactor":
            return None

        # Parse the refactor description
        if ": " in commit.message:
            description = commit.message.split(": ", 1)[1]
        else:
            description = commit.message

        scope = commit.scope or "architecture"

        # Only extract refactors that touch multiple files (likely significant)
        if len(commit.files_changed) < 3:
            return None

        insight = f"Architectural decision ({scope}): {description}"

        teaching = TeachingMoment(
            insight=insight,
            severity="info",
            evidence=f"refactor:commit:{commit.sha[:8]}",
            commit=commit.sha[:8],
        )

        features = tuple(
            feature for file in commit.files_changed for feature in match_file_to_features(file)
        )

        return CommitTeaching(
            teaching=teaching,
            commit=commit,
            features=features or ("general",),
            category="decision",
        )

    def _extract_from_feat_with_test(self, commit: Commit) -> CommitTeaching | None:
        """
        Extract patterns from feat: commits that include tests.

        Features with tests are verified patterns - worth crystallizing.
        """
        if commit.commit_type != "feat":
            return None

        # Check if commit includes tests
        has_tests = any("test" in f.lower() or "_tests" in f for f in commit.files_changed)

        if not has_tests:
            return None

        # Parse the feature description
        if ": " in commit.message:
            description = commit.message.split(": ", 1)[1]
        else:
            description = commit.message

        scope = commit.scope or "feature"

        insight = f"New pattern ({scope}): {description} - includes test coverage"

        teaching = TeachingMoment(
            insight=insight,
            severity="info",
            evidence=f"feat+test:commit:{commit.sha[:8]}",
            commit=commit.sha[:8],
        )

        features = tuple(
            feature for file in commit.files_changed for feature in match_file_to_features(file)
        )

        return CommitTeaching(
            teaching=teaching,
            commit=commit,
            features=features or ("general",),
            category="pattern",
        )


def extract_teachings_from_commits(
    commits: Sequence[Commit],
    min_churn: int = 0,
    max_age_days: int | None = None,
) -> list[CommitTeaching]:
    """
    Convenience function to extract teachings from commits.

    Args:
        commits: Sequence of commits to analyze
        min_churn: Minimum lines changed to consider (filters trivial fixes)
        max_age_days: Only consider commits within this many days (None = all)

    Returns:
        List of CommitTeaching objects ready for crystallization
    """
    from datetime import datetime, timedelta, timezone

    extractor = CommitTeachingExtractor()

    # Filter commits
    filtered = commits

    if min_churn > 0:
        filtered = [c for c in filtered if c.churn >= min_churn]

    if max_age_days is not None:
        cutoff = datetime.now(timezone.utc) - timedelta(days=max_age_days)
        filtered = [c for c in filtered if c.timestamp.replace(tzinfo=timezone.utc) >= cutoff]

    return extractor.extract_all(filtered)


def generate_teaching_report(teachings: Sequence[CommitTeaching]) -> str:
    """
    Generate a human-readable report of extracted teachings.

    Args:
        teachings: Teachings to report on

    Returns:
        Markdown-formatted report
    """
    from datetime import datetime

    lines = [
        "# Commit Teaching Extraction Report",
        f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M')}",
        f"Total teachings: {len(teachings)}",
        "",
        "## By Category",
        "",
    ]

    # Group by category
    by_category: dict[str, list[CommitTeaching]] = {}
    for t in teachings:
        by_category.setdefault(t.category, []).append(t)

    category_icons = {
        "gotcha": "🐛",
        "warning": "⚠️",
        "critical": "🚨",
        "decision": "🏗️",
        "pattern": "✨",
    }

    for category in ["critical", "warning", "gotcha", "decision", "pattern"]:
        items = by_category.get(category, [])
        if not items:
            continue

        icon = category_icons.get(category, "•")
        lines.append(f"### {icon} {category.upper()} ({len(items)})")
        lines.append("")

        for t in items[:10]:  # Limit to 10 per category
            lines.append(f"- **{t.teaching.insight[:80]}...**")
            lines.append(f"  - Features: {', '.join(t.features[:3])}")
            lines.append(f"  - Commit: `{t.commit.sha[:8]}`")
            lines.append("")

        if len(items) > 10:
            lines.append(f"  ... and {len(items) - 10} more")
            lines.append("")

    # By feature
    lines.extend(
        [
            "## By Feature",
            "",
        ]
    )

    by_feature: dict[str, list[CommitTeaching]] = {}
    for t in teachings:
        for feature in t.features:
            by_feature.setdefault(feature, []).append(t)

    for feature, items in sorted(by_feature.items(), key=lambda x: -len(x[1]))[:10]:
        lines.append(f"- **{feature}**: {len(items)} teachings")

    lines.append("")
    return "\n".join(lines)
