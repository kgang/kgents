"""
K-gent Audit Trail: Logging and querying mediation decisions.

Every K-gent mediation (intercept) is logged with:
- What was evaluated
- What decision was made
- What principles informed the decision
- Confidence level
- Reasoning

This provides accountability and enables learning over time.

Usage:
    audit = AuditTrail()
    audit.log(entry)
    recent = audit.recent(limit=10)

Storage:
    By default, stores to ~/.kgents/audit/audit.jsonl
    Can be configured to use different storage paths.
"""

from __future__ import annotations

import json
import os
from dataclasses import asdict, dataclass, field
from datetime import datetime
from pathlib import Path
from typing import Any, Optional


@dataclass
class AuditEntry:
    """A single audit trail entry."""

    timestamp: datetime
    token_id: str
    action: str  # approve/reject/escalate
    confidence: float
    principles: list[str]
    reasoning: str

    # Optional metadata
    operation: str = ""  # The operation being evaluated
    severity: float = 0.0
    was_deep: bool = False  # Was this a deep (LLM-backed) intercept?

    def to_dict(self) -> dict[str, Any]:
        """Convert to dictionary for JSON serialization."""
        d = asdict(self)
        d["timestamp"] = self.timestamp.isoformat()
        return d

    @classmethod
    def from_dict(cls, d: dict[str, Any]) -> "AuditEntry":
        """Create from dictionary."""
        d = d.copy()
        d["timestamp"] = datetime.fromisoformat(d["timestamp"])
        return cls(**d)

    def to_audit_string(self) -> str:
        """Convert to human-readable audit string."""
        return (
            f"[{self.timestamp.isoformat()}] {self.action.upper()} "
            f"(confidence: {self.confidence:.2%})\n"
            f"  Token: {self.token_id}\n"
            f"  Principles: {', '.join(self.principles) if self.principles else 'None'}\n"
            f"  Reasoning: {self.reasoning}"
        )

    def to_short_string(self) -> str:
        """Short one-line summary."""
        return (
            f"[{self.timestamp.strftime('%Y-%m-%d %H:%M')}] "
            f"{self.action.upper():8} "
            f"{self.confidence:.0%} "
            f"- {self.reasoning[:50]}..."
            if len(self.reasoning) > 50
            else f"[{self.timestamp.strftime('%Y-%m-%d %H:%M')}] "
            f"{self.action.upper():8} "
            f"{self.confidence:.0%} "
            f"- {self.reasoning}"
        )


def _default_storage_path() -> Path:
    """Get default storage path for audit logs."""
    home = Path.home()
    audit_dir = home / ".kgents" / "audit"
    audit_dir.mkdir(parents=True, exist_ok=True)
    return audit_dir


class AuditTrail:
    """
    Audit trail for K-gent mediation decisions.

    Stores entries in JSON Lines format for easy appending and reading.
    """

    def __init__(
        self,
        storage_path: Optional[Path] = None,
        max_entries: int = 10000,
    ):
        """Initialize audit trail.

        Args:
            storage_path: Directory to store audit logs. Defaults to ~/.kgents/audit/
            max_entries: Maximum entries to keep in memory cache (for recent queries)
        """
        self._storage = storage_path or _default_storage_path()
        self._max_entries = max_entries
        self._cache: list[AuditEntry] = []
        self._cache_loaded = False

    @property
    def log_file(self) -> Path:
        """Path to the audit log file."""
        return self._storage / "audit.jsonl"

    def log(self, entry: AuditEntry) -> None:
        """Log an audit entry.

        Appends to both the file and the in-memory cache.
        File writes use append mode which is generally atomic on POSIX systems.
        """
        # Append to file - append mode is atomic on most filesystems
        try:
            self._storage.mkdir(parents=True, exist_ok=True)
            with open(self.log_file, "a") as f:
                f.write(json.dumps(entry.to_dict()) + "\n")
                f.flush()  # Ensure write is committed
                os.fsync(f.fileno())  # Force OS to flush to disk
        except OSError as e:
            # Log error but don't fail - audit is important but not critical
            import logging

            logging.getLogger(__name__).warning("Failed to write audit entry to disk: %s", e)

        # Update cache regardless of file write success
        self._cache.append(entry)
        if len(self._cache) > self._max_entries:
            self._cache = self._cache[-self._max_entries :]

    def recent(self, limit: int = 10) -> list[AuditEntry]:
        """Get recent audit entries.

        Args:
            limit: Maximum number of entries to return

        Returns:
            List of recent audit entries (newest first)
        """
        self._ensure_cache_loaded()
        return list(reversed(self._cache[-limit:]))

    def all_entries(self) -> list[AuditEntry]:
        """Get all audit entries."""
        self._ensure_cache_loaded()
        return list(self._cache)

    def filter_by_action(self, action: str) -> list[AuditEntry]:
        """Filter entries by action type."""
        self._ensure_cache_loaded()
        return [e for e in self._cache if e.action == action]

    def filter_by_date(
        self,
        start: Optional[datetime] = None,
        end: Optional[datetime] = None,
    ) -> list[AuditEntry]:
        """Filter entries by date range."""
        self._ensure_cache_loaded()
        entries = self._cache

        if start:
            entries = [e for e in entries if e.timestamp >= start]
        if end:
            entries = [e for e in entries if e.timestamp <= end]

        return entries

    def summary(self) -> dict[str, Any]:
        """Get summary statistics of the audit trail."""
        self._ensure_cache_loaded()

        if not self._cache:
            return {
                "total_entries": 0,
                "by_action": {},
                "avg_confidence": 0.0,
                "deep_intercepts": 0,
            }

        by_action: dict[str, int] = {}
        total_confidence = 0.0
        deep_count = 0

        for entry in self._cache:
            by_action[entry.action] = by_action.get(entry.action, 0) + 1
            total_confidence += entry.confidence
            if entry.was_deep:
                deep_count += 1

        return {
            "total_entries": len(self._cache),
            "by_action": by_action,
            "avg_confidence": total_confidence / len(self._cache),
            "deep_intercepts": deep_count,
        }

    def format_recent(self, limit: int = 10) -> str:
        """Format recent entries for display."""
        entries = self.recent(limit)

        if not entries:
            return "[AUDIT] No entries yet."

        lines = [f"[AUDIT] Recent mediations ({len(entries)} shown):"]
        lines.append("")

        for entry in entries:
            lines.append(entry.to_short_string())

        return "\n".join(lines)

    def format_summary(self) -> str:
        """Format summary for display."""
        summary = self.summary()

        lines = [
            "[AUDIT] Summary:",
            f"  Total entries: {summary['total_entries']}",
            "  By action:",
        ]

        for action, count in summary["by_action"].items():
            lines.append(f"    {action}: {count}")

        lines.append(f"  Avg confidence: {summary['avg_confidence']:.1%}")
        lines.append(f"  Deep intercepts: {summary['deep_intercepts']}")

        return "\n".join(lines)

    def _ensure_cache_loaded(self) -> None:
        """Load cache from file if not already loaded."""
        if self._cache_loaded:
            return

        if self.log_file.exists():
            with open(self.log_file, "r") as f:
                for line in f:
                    line = line.strip()
                    if line:
                        try:
                            entry = AuditEntry.from_dict(json.loads(line))
                            self._cache.append(entry)
                        except (json.JSONDecodeError, KeyError, TypeError):
                            # Skip malformed entries
                            continue

            # Keep only max_entries
            if len(self._cache) > self._max_entries:
                self._cache = self._cache[-self._max_entries :]

        self._cache_loaded = True

    def clear(self) -> None:
        """Clear the audit trail (for testing)."""
        self._cache = []
        self._cache_loaded = True
        if self.log_file.exists():
            self.log_file.unlink()
