"""
CISignalCollector - Collect CI workflow signals for feedback loop.

Reads .kgents/ghost/ci_signals.jsonl and analyzes:
- Recent CI results (last hour, last 24h)
- Pass/fail ratio
- Failing test suites
- Commit correlation

This closes the feedback loop: CI emits signals → CISignalCollector reads them
→ GhostDaemon projects to health.status → Agents can learn from CI results.

Part of the Multi-Agent Compatible CI infrastructure.
"""

from __future__ import annotations

import json
import logging
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path
from typing import Any

from .collectors import CollectorResult, GhostCollector

logger = logging.getLogger(__name__)


@dataclass
class CISignal:
    """
    A single CI workflow signal.

    Attributes:
        ts: Unix timestamp when signal was emitted
        type: Signal type (CI_SUCCESS or CI_FAILURE)
        sha: Git commit SHA
        ref: Git ref (e.g., refs/heads/main)
        run_number: GitHub Actions run number
        suites: Test suite results {name: "success"|"failure"|"skipped"}
    """

    ts: float
    type: str
    sha: str
    ref: str
    run_number: int
    suites: dict[str, str]

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> "CISignal | None":
        """Parse a CISignal from a JSONL line."""
        try:
            return cls(
                ts=float(data.get("ts", 0)),
                type=str(data.get("type", "UNKNOWN")),
                sha=str(data.get("sha", "")),
                ref=str(data.get("ref", "")),
                run_number=int(data.get("run_number", 0)),
                suites=data.get("suites", {}),
            )
        except (TypeError, ValueError) as e:
            logger.debug(f"Failed to parse CI signal: {e}")
            return None

    @property
    def is_success(self) -> bool:
        """Check if this signal represents a successful CI run."""
        return self.type == "CI_SUCCESS"

    @property
    def failed_suites(self) -> list[str]:
        """Get list of failed suite names."""
        return [name for name, status in self.suites.items() if status == "failure"]

    @property
    def short_sha(self) -> str:
        """Get short SHA (first 7 characters)."""
        return self.sha[:7] if self.sha else "unknown"


class CISignalCollector(GhostCollector):
    """
    Collect CI workflow signals for the ghost feedback loop.

    Reads .kgents/ghost/ci_signals.jsonl (written by GitHub Actions workflow)
    and produces health summaries for the GhostDaemon.

    Health Line Examples:
        ci:all_pass (5 runs)           # All recent runs passed
        ci:3/5 passed                  # 3 of 5 recent runs passed
        ci:failing(laws,integration)   # Specific suites failing
        ci:no_data                     # No CI signals found

    Usage:
        collector = CISignalCollector()
        result = await collector.collect()
        print(result.health_line)  # "ci:3/5 passed"
    """

    def __init__(self, signal_path: Path | None = None):
        """
        Initialize CISignalCollector.

        Args:
            signal_path: Path to ci_signals.jsonl (default: .kgents/ghost/ci_signals.jsonl)
        """
        self.signal_path = signal_path or Path.cwd() / ".kgents/ghost/ci_signals.jsonl"

    @property
    def name(self) -> str:
        return "ci"

    async def collect(self) -> CollectorResult:
        """
        Collect and analyze CI signals.

        Returns:
            CollectorResult with health_line and detailed data
        """
        timestamp = datetime.now().isoformat()

        if not self.signal_path.exists():
            return CollectorResult(
                source=self.name,
                timestamp=timestamp,
                success=True,
                data={
                    "total": 0,
                    "health_line": "ci:no_data",
                    "message": "No CI signals file found",
                },
            )

        try:
            signals = self._parse_signals()

            if not signals:
                return CollectorResult(
                    source=self.name,
                    timestamp=timestamp,
                    success=True,
                    data={
                        "total": 0,
                        "health_line": "ci:empty",
                        "message": "CI signals file exists but is empty",
                    },
                )

            # Time-based analysis
            now = datetime.now().timestamp()
            hour_ago = now - 3600
            day_ago = now - 86400

            recent_hour = [s for s in signals if s.ts > hour_ago]
            recent_day = [s for s in signals if s.ts > day_ago]

            # Use last 24h for health calculation, or all if fewer
            analysis_set = recent_day if recent_day else signals[-10:]

            # Calculate pass/fail
            passed = sum(1 for s in analysis_set if s.is_success)
            total = len(analysis_set)

            # Find failing suites (from most recent failure)
            failing_suites: set[str] = set()
            for signal in reversed(analysis_set):
                if not signal.is_success:
                    failing_suites.update(signal.failed_suites)
                    break  # Only look at most recent failure

            # Build health line
            if total == 0:
                health_line = "ci:no_data"
            elif passed == total:
                health_line = f"ci:all_pass ({total} runs)"
            elif failing_suites:
                health_line = f"ci:failing({','.join(sorted(failing_suites))})"
            else:
                health_line = f"ci:{passed}/{total} passed"

            # Build detailed data
            data: dict[str, Any] = {
                "total": len(signals),
                "last_hour": len(recent_hour),
                "last_24h": len(recent_day),
                "passed_24h": passed,
                "failed_24h": total - passed,
                "pass_rate": passed / total if total > 0 else 0,
                "failing_suites": list(failing_suites),
                "health_line": health_line,
            }

            # Add most recent signal info
            if signals:
                latest = signals[-1]
                data["latest"] = {
                    "sha": latest.short_sha,
                    "type": latest.type,
                    "run_number": latest.run_number,
                    "suites": latest.suites,
                    "timestamp": datetime.fromtimestamp(latest.ts).isoformat(),
                }

            return CollectorResult(
                source=self.name,
                timestamp=timestamp,
                success=True,
                data=data,
            )

        except Exception as e:
            logger.exception(f"Failed to collect CI signals: {e}")
            return CollectorResult(
                source=self.name,
                timestamp=timestamp,
                success=False,
                error=str(e),
            )

    def _parse_signals(self) -> list[CISignal]:
        """Parse all signals from the JSONL file."""
        signals: list[CISignal] = []

        try:
            with open(self.signal_path) as f:
                for line in f:
                    line = line.strip()
                    if not line:
                        continue
                    try:
                        data = json.loads(line)
                        signal = CISignal.from_dict(data)
                        if signal is not None:
                            signals.append(signal)
                    except json.JSONDecodeError:
                        logger.debug(f"Skipping malformed JSON line: {line[:50]}...")
                        continue
        except OSError as e:
            logger.warning(f"Failed to read CI signals file: {e}")

        # Sort by timestamp (oldest first)
        signals.sort(key=lambda s: s.ts)
        return signals

    def get_recent_failures(self, limit: int = 5) -> list[CISignal]:
        """
        Get recent CI failures (synchronous for CLI).

        Args:
            limit: Maximum number of failures to return

        Returns:
            List of failed CISignal objects, most recent first
        """
        signals = self._parse_signals()
        failures = [s for s in signals if not s.is_success]
        return list(reversed(failures[-limit:]))

    def get_suite_stats(self) -> dict[str, dict[str, int]]:
        """
        Get pass/fail counts per test suite (synchronous for CLI).

        Returns:
            Dict of {suite_name: {"passed": n, "failed": n}}
        """
        signals = self._parse_signals()
        stats: dict[str, dict[str, int]] = {}

        for signal in signals:
            for suite, status in signal.suites.items():
                if suite not in stats:
                    stats[suite] = {"passed": 0, "failed": 0, "skipped": 0}
                if status == "success":
                    stats[suite]["passed"] += 1
                elif status == "failure":
                    stats[suite]["failed"] += 1
                else:
                    stats[suite]["skipped"] += 1

        return stats
