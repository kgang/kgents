"""
Session Pattern Analyzer: Extract patterns from Claude Code session history.

Part of Wave 4 of the Evergreen Prompt System.

Reads from ~/.claude/ to analyze:
- Command frequency and patterns
- Time-of-day usage patterns
- Project focus areas
- Tool usage patterns
"""

from __future__ import annotations

import json
import logging
from collections import Counter
from dataclasses import dataclass
from datetime import datetime, timedelta
from pathlib import Path
from typing import Literal

from .git_analyzer import GitPattern

logger = logging.getLogger(__name__)


class SessionAnalyzerError(Exception):
    """Error during session analysis."""

    pass


@dataclass(frozen=True)
class SessionPattern:
    """A detected pattern from session history."""

    pattern_type: Literal[
        "command_frequency", "time_usage", "project_focus", "tool_usage"
    ]
    description: str
    confidence: float  # 0.0-1.0
    evidence: tuple[str, ...]
    details: dict[str, float]

    def __str__(self) -> str:
        return f"[{self.pattern_type}] {self.description} (confidence: {self.confidence:.0%})"

    def to_git_pattern(self) -> GitPattern:
        """Convert to GitPattern for unified handling."""
        # Map session pattern types to git pattern types
        type_map = {
            "command_frequency": "commit_style",  # Style indicator
            "time_usage": "timing",
            "project_focus": "file_focus",
            "tool_usage": "commit_style",
        }
        return GitPattern(
            pattern_type=type_map.get(self.pattern_type, "commit_style"),
            description=self.description,
            confidence=self.confidence,
            evidence=self.evidence,
            details=self.details,
        )


@dataclass
class SessionPatternAnalyzer:
    """
    Analyze Claude Code session history for developer patterns.

    Reads from ~/.claude/ directory structure:
    - history.jsonl: Command history
    - stats-cache.json: Usage statistics
    - projects/{path}/*.jsonl: Full transcripts

    Thread-safe: all operations are stateless file reads.
    """

    claude_dir: Path = Path.home() / ".claude"
    lookback_days: int = 30
    current_project: Path | None = None

    def analyze(self) -> list[SessionPattern]:
        """
        Extract patterns from session history.

        Returns list of detected patterns, highest confidence first.
        """
        if not self.claude_dir.exists():
            logger.info(f"Claude directory not found: {self.claude_dir}")
            return []

        patterns: list[SessionPattern] = []

        try:
            patterns.append(self._analyze_command_frequency())
        except Exception as e:
            logger.warning(f"Failed to analyze command frequency: {e}")

        try:
            patterns.append(self._analyze_time_usage())
        except Exception as e:
            logger.warning(f"Failed to analyze time usage: {e}")

        try:
            patterns.append(self._analyze_project_focus())
        except Exception as e:
            logger.warning(f"Failed to analyze project focus: {e}")

        try:
            patterns.append(self._analyze_tool_usage())
        except Exception as e:
            logger.warning(f"Failed to analyze tool usage: {e}")

        # Filter out None and sort by confidence
        patterns = [p for p in patterns if p is not None]
        patterns.sort(key=lambda p: p.confidence, reverse=True)

        return patterns

    def _analyze_command_frequency(self) -> SessionPattern | None:
        """
        Analyze command/prompt patterns from history.jsonl.

        Detects:
        - Common command prefixes (/, imperative verbs)
        - Message length preferences
        - Question vs statement style
        """
        history_file = self.claude_dir / "history.jsonl"
        if not history_file.exists():
            return None

        entries = self._read_jsonl(history_file)
        if not entries:
            return None

        # Filter to recent entries
        cutoff = datetime.now() - timedelta(days=self.lookback_days)
        recent = [
            e for e in entries if self._parse_timestamp(e.get("timestamp")) > cutoff
        ]

        if len(recent) < 10:
            return None

        # Analyze message patterns
        messages = [e.get("display", "") for e in recent if e.get("display")]

        # Count prefixes
        prefix_counts: Counter[str] = Counter()
        for msg in messages:
            first_word = msg.split()[0].lower() if msg.split() else ""
            if first_word:
                prefix_counts[first_word] += 1

        # Count message lengths
        lengths = [len(m) for m in messages]
        avg_length = sum(lengths) / len(lengths) if lengths else 0

        # Count slash commands
        slash_count = sum(1 for m in messages if m.startswith("/"))
        slash_ratio = slash_count / len(messages) if messages else 0

        # Count questions
        question_count = sum(1 for m in messages if m.strip().endswith("?"))
        question_ratio = question_count / len(messages) if messages else 0

        # Determine primary style
        details = {
            "avg_length": avg_length,
            "slash_ratio": slash_ratio,
            "question_ratio": question_ratio,
            "total_commands": float(len(recent)),
        }

        top_prefixes = prefix_counts.most_common(5)
        top_prefix = top_prefixes[0][0] if top_prefixes else "unknown"

        if slash_ratio > 0.3:
            description = f"Heavy slash command user ({slash_ratio:.0%})"
            confidence = slash_ratio
        elif question_ratio > 0.5:
            description = f"Question-oriented style ({question_ratio:.0%})"
            confidence = question_ratio
        elif avg_length < 50:
            description = f"Terse commands (avg {avg_length:.0f} chars)"
            confidence = 0.7
        elif avg_length > 200:
            description = f"Detailed prompts (avg {avg_length:.0f} chars)"
            confidence = 0.7
        else:
            description = f"Mixed command style, top prefix: {top_prefix}"
            confidence = 0.5

        return SessionPattern(
            pattern_type="command_frequency",
            description=description,
            confidence=confidence,
            evidence=tuple(f"{p}: {c}" for p, c in top_prefixes[:5]),
            details=details,
        )

    def _analyze_time_usage(self) -> SessionPattern | None:
        """
        Analyze time-of-day usage patterns.

        Uses history.jsonl timestamps.
        """
        history_file = self.claude_dir / "history.jsonl"
        if not history_file.exists():
            return None

        entries = self._read_jsonl(history_file)
        if not entries:
            return None

        # Parse timestamps
        timestamps: list[datetime] = []
        for e in entries:
            ts = self._parse_timestamp(e.get("timestamp"))
            if ts:
                timestamps.append(ts)

        if len(timestamps) < 20:
            return None

        # Filter to recent
        cutoff = datetime.now() - timedelta(days=self.lookback_days)
        recent = [t for t in timestamps if t > cutoff]

        if len(recent) < 10:
            return None

        # Analyze hours
        hours = [t.hour for t in recent]
        hour_counts = Counter(hours)

        # Time buckets
        morning = sum(hour_counts.get(h, 0) for h in range(6, 12))
        afternoon = sum(hour_counts.get(h, 0) for h in range(12, 18))
        evening = sum(hour_counts.get(h, 0) for h in range(18, 24))
        night = sum(hour_counts.get(h, 0) for h in range(0, 6))
        total = len(recent)

        details = {
            "morning_ratio": morning / total if total else 0,
            "afternoon_ratio": afternoon / total if total else 0,
            "evening_ratio": evening / total if total else 0,
            "night_ratio": night / total if total else 0,
            "total_sessions": float(total),
        }

        time_ratios = [
            ("morning", morning / total if total else 0),
            ("afternoon", afternoon / total if total else 0),
            ("evening", evening / total if total else 0),
            ("night", night / total if total else 0),
        ]
        primary_time, primary_ratio = max(time_ratios, key=lambda x: x[1])

        if primary_ratio > 0.5:
            description = f"Primarily {primary_time} user ({primary_ratio:.0%})"
            confidence = primary_ratio
        else:
            description = "Distributed usage throughout day"
            confidence = 0.5

        return SessionPattern(
            pattern_type="time_usage",
            description=description,
            confidence=confidence,
            evidence=(
                f"Morning: {morning}/{total}",
                f"Afternoon: {afternoon}/{total}",
                f"Evening: {evening}/{total}",
                f"Night: {night}/{total}",
            ),
            details=details,
        )

    def _analyze_project_focus(self) -> SessionPattern | None:
        """
        Analyze which projects get most attention.

        Uses history.jsonl project field.
        """
        history_file = self.claude_dir / "history.jsonl"
        if not history_file.exists():
            return None

        entries = self._read_jsonl(history_file)
        if not entries:
            return None

        # Filter to recent
        cutoff = datetime.now() - timedelta(days=self.lookback_days)
        recent = [
            e for e in entries if self._parse_timestamp(e.get("timestamp")) > cutoff
        ]

        # Count project occurrences
        project_counts: Counter[str] = Counter()
        for e in recent:
            project = e.get("project", "")
            if project:
                # Extract project name from path
                name = Path(project).name
                project_counts[name] += 1

        if not project_counts:
            return None

        total = sum(project_counts.values())
        top_projects = project_counts.most_common(5)
        top_project, top_count = top_projects[0] if top_projects else ("unknown", 0)
        focus_ratio = top_count / total if total else 0

        details = {
            "total_commands": float(total),
            "unique_projects": float(len(project_counts)),
            "top_project_ratio": focus_ratio,
        }

        # Add ratios for top projects
        for i, (proj, count) in enumerate(top_projects[:3]):
            details[f"project_{i}_ratio"] = count / total if total else 0

        if focus_ratio > 0.7:
            description = f"Focused on {top_project} ({focus_ratio:.0%})"
            confidence = focus_ratio
        elif len(project_counts) <= 3:
            description = f"Works on {len(project_counts)} projects"
            confidence = 0.6
        else:
            description = f"Multi-project workflow ({len(project_counts)} projects)"
            confidence = 0.5

        return SessionPattern(
            pattern_type="project_focus",
            description=description,
            confidence=confidence,
            evidence=tuple(f"{p}: {c}" for p, c in top_projects[:5]),
            details=details,
        )

    def _analyze_tool_usage(self) -> SessionPattern | None:
        """
        Analyze tool usage patterns from stats-cache.json.

        Currently simplified - full implementation would analyze
        debug logs for detailed tool traces.
        """
        stats_file = self.claude_dir / "stats-cache.json"
        if not stats_file.exists():
            return None

        try:
            stats = json.loads(stats_file.read_text())
        except (json.JSONDecodeError, OSError):
            return None

        # Extract key metrics
        total_sessions = stats.get("totalSessions", 0)
        total_messages = stats.get("totalMessages", 0)

        if total_sessions < 10:
            return None

        messages_per_session = total_messages / total_sessions if total_sessions else 0

        # Analyze token usage by model
        model_usage = stats.get("cumulativeModelUsage", {})
        models_used = list(model_usage.keys())

        details = {
            "total_sessions": float(total_sessions),
            "total_messages": float(total_messages),
            "messages_per_session": messages_per_session,
            "models_count": float(len(models_used)),
        }

        if messages_per_session < 10:
            description = f"Short sessions (avg {messages_per_session:.0f} messages)"
            confidence = 0.6
        elif messages_per_session > 50:
            description = f"Extended sessions (avg {messages_per_session:.0f} messages)"
            confidence = 0.7
        else:
            description = (
                f"Moderate session length (avg {messages_per_session:.0f} messages)"
            )
            confidence = 0.5

        return SessionPattern(
            pattern_type="tool_usage",
            description=description,
            confidence=confidence,
            evidence=(
                f"Total sessions: {total_sessions}",
                f"Total messages: {total_messages}",
                f"Models: {', '.join(models_used[:3])}",
            ),
            details=details,
        )

    def _read_jsonl(self, path: Path) -> list[dict]:
        """Read a JSONL file, handling errors gracefully."""
        entries: list[dict] = []
        try:
            with path.open() as f:
                for line in f:
                    line = line.strip()
                    if line:
                        try:
                            entries.append(json.loads(line))
                        except json.JSONDecodeError:
                            continue
        except OSError as e:
            logger.warning(f"Failed to read {path}: {e}")
        return entries

    def _parse_timestamp(self, ts: int | str | None) -> datetime | None:
        """Parse timestamp from various formats."""
        if ts is None:
            return None

        try:
            if isinstance(ts, int):
                # Epoch milliseconds
                return datetime.fromtimestamp(ts / 1000)
            elif isinstance(ts, str):
                # ISO format
                return datetime.fromisoformat(ts.replace("Z", "+00:00"))
        except (ValueError, OSError):
            pass

        return None


def analyze_sessions(
    lookback_days: int = 30,
    current_project: Path | None = None,
) -> list[SessionPattern]:
    """
    Convenience function to analyze Claude Code sessions.

    Args:
        lookback_days: How many days of history to analyze
        current_project: Current project path for context

    Returns:
        List of detected patterns
    """
    analyzer = SessionPatternAnalyzer(
        lookback_days=lookback_days,
        current_project=current_project,
    )
    return analyzer.analyze()


__all__ = [
    "SessionPattern",
    "SessionPatternAnalyzer",
    "SessionAnalyzerError",
    "analyze_sessions",
]
