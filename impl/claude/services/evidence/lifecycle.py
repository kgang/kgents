"""
Evidence Lifecycle Management - Generalizable to any repository.

Philosophy:
    "Don't treat this as final copy. Build lifecycle commands early."

Lifecycle Stages:
    1. INIT     - Set up evidence tracking for a repo
    2. MINE     - Extract patterns from git history
    3. CORRELATE - Link witness marks to commits
    4. CALCULATE - Compute ROI metrics
    5. SNAPSHOT - Save current state
    6. REFRESH  - Re-mine and update
    7. EXPORT   - Generate reports (JSON, Markdown)
    8. COMPARE  - Compare snapshots over time

Usage:
    from services.evidence.lifecycle import EvidenceLifecycle

    lifecycle = EvidenceLifecycle("/path/to/repo")
    await lifecycle.init()           # Initialize
    await lifecycle.refresh()        # Re-mine
    await lifecycle.export("roi.md") # Generate report
"""

from __future__ import annotations

import json
from dataclasses import asdict, dataclass, field
from datetime import datetime, timezone
from pathlib import Path
from typing import TYPE_CHECKING, Any

from .correlation import EvidenceCorrelator
from .mining import RepositoryMiner
from .roi import MonthlyValue, ROICalculator

if TYPE_CHECKING:
    from services.witness.persistence import WitnessPersistence


@dataclass
class EvidenceSnapshot:
    """Point-in-time snapshot of evidence metrics."""

    timestamp: datetime
    repo_path: str
    commit_sha: str  # HEAD at snapshot time

    # Mining results
    total_commits: int
    active_days: int
    top_authors: list[str]
    top_churning_files: list[str]

    # Correlation results
    mark_commit_links: int
    gotcha_marks: int
    decision_marks: int

    # ROI metrics
    monthly_value: float
    confidence_low: float
    confidence_high: float
    evidence_strength: str

    # Metadata
    version: str = "1.0"
    notes: str = ""

    def to_dict(self) -> dict[str, Any]:
        """Convert to JSON-serializable dict."""
        d = asdict(self)
        d["timestamp"] = self.timestamp.isoformat()
        return d

    @classmethod
    def from_dict(cls, d: dict[str, Any]) -> "EvidenceSnapshot":
        """Reconstruct from dict."""
        d["timestamp"] = datetime.fromisoformat(d["timestamp"])
        return cls(**d)


@dataclass
class EvidenceConfig:
    """Configuration for evidence lifecycle."""

    repo_path: Path
    snapshots_dir: Path
    hourly_rate: float = 80.0
    target_monthly: float = 800.0
    max_commits: int = 1000

    @classmethod
    def load(cls, config_path: Path) -> "EvidenceConfig":
        """Load from JSON config file."""
        if config_path.exists():
            with open(config_path) as f:
                data = json.load(f)
            return cls(
                repo_path=Path(data.get("repo_path", ".")),
                snapshots_dir=Path(data.get("snapshots_dir", ".evidence")),
                hourly_rate=data.get("hourly_rate", 80.0),
                target_monthly=data.get("target_monthly", 800.0),
                max_commits=data.get("max_commits", 1000),
            )
        return cls(repo_path=Path("."), snapshots_dir=Path(".evidence"))

    def save(self, config_path: Path) -> None:
        """Save to JSON config file."""
        data = {
            "repo_path": str(self.repo_path),
            "snapshots_dir": str(self.snapshots_dir),
            "hourly_rate": self.hourly_rate,
            "target_monthly": self.target_monthly,
            "max_commits": self.max_commits,
        }
        config_path.parent.mkdir(parents=True, exist_ok=True)
        with open(config_path, "w") as f:
            json.dump(data, f, indent=2)


class EvidenceLifecycle:
    """
    Manage the evidence mining lifecycle for any git repository.

    Generalizable: Works on ANY repo, not just kgents.
    """

    def __init__(
        self,
        repo_path: Path | str,
        witness_persistence: "WitnessPersistence | None" = None,
        config: EvidenceConfig | None = None,
    ):
        self.repo_path = Path(repo_path)
        self.witness = witness_persistence

        # Load or create config
        self.config = config or EvidenceConfig(
            repo_path=self.repo_path,
            snapshots_dir=self.repo_path / ".evidence",
        )

        # Initialize components (lazy)
        self._miner: RepositoryMiner | None = None
        self._correlator: EvidenceCorrelator | None = None
        self._calculator: ROICalculator | None = None

    @property
    def miner(self) -> RepositoryMiner:
        """Lazy-load miner."""
        if self._miner is None:
            self._miner = RepositoryMiner(self.repo_path)
        return self._miner

    @property
    def correlator(self) -> EvidenceCorrelator | None:
        """Lazy-load correlator (requires witness)."""
        if self._correlator is None and self.witness is not None:
            self._correlator = EvidenceCorrelator(self.witness, self.repo_path)
        return self._correlator

    @property
    def calculator(self) -> ROICalculator | None:
        """Lazy-load calculator (requires witness)."""
        if self._calculator is None and self.witness is not None:
            self._calculator = ROICalculator(self.witness, self.repo_path)
        return self._calculator

    async def init(self) -> dict[str, Any]:
        """
        Initialize evidence tracking for this repository.

        Creates:
            - .evidence/ directory
            - config.json with defaults
            - Initial snapshot
        """
        snapshots_dir = self.config.snapshots_dir
        snapshots_dir.mkdir(parents=True, exist_ok=True)

        # Save config
        config_path = snapshots_dir / "config.json"
        self.config.save(config_path)

        # Create initial snapshot
        snapshot = await self.snapshot(notes="Initial snapshot")

        return {
            "status": "initialized",
            "repo_path": str(self.repo_path),
            "snapshots_dir": str(snapshots_dir),
            "initial_snapshot": snapshot.to_dict(),
        }

    async def refresh(self) -> dict[str, Any]:
        """
        Re-mine repository and update evidence.

        Returns comparison with previous snapshot.
        """
        # Load previous snapshot if exists
        previous = self._load_latest_snapshot()

        # Create new snapshot
        current = await self.snapshot(notes="Refresh")

        # Compare
        comparison = self._compare_snapshots(previous, current)

        return {
            "status": "refreshed",
            "previous": previous.to_dict() if previous else None,
            "current": current.to_dict(),
            "comparison": comparison,
        }

    async def snapshot(self, notes: str = "") -> EvidenceSnapshot:
        """Create a point-in-time evidence snapshot."""
        import subprocess

        # Get current HEAD
        result = subprocess.run(
            ["git", "rev-parse", "HEAD"],
            capture_output=True,
            text=True,
            cwd=self.repo_path,
        )
        commit_sha = result.stdout.strip() if result.returncode == 0 else "unknown"

        # Mine patterns
        patterns = self.miner.mine_commit_patterns(max_commits=self.config.max_commits)
        authors = self.miner.mine_author_patterns(max_commits=self.config.max_commits)
        churn = self.miner.mine_file_churn(max_commits=self.config.max_commits, top_n=10)

        # Default values if no witness
        mark_commit_links = 0
        gotcha_marks = 0
        decision_marks = 0
        monthly_value = 0.0
        confidence_low = 0.0
        confidence_high = 0.0
        evidence_strength = "none"

        # Correlate and calculate ROI if witness available
        if self.correlator and self.calculator:
            links = await self.correlator.correlate_marks_with_commits(
                max_commits=self.config.max_commits
            )
            mark_commit_links = len(links)

            # Get mark counts
            gotcha_result = await self.correlator.correlate_gotchas_with_bugs()
            if gotcha_result:
                gotcha_marks = gotcha_result.gotcha_marks

            # Calculate ROI
            monthly = await self.calculator.calculate_monthly_value(
                hourly_rate=self.config.hourly_rate
            )
            monthly_value = monthly.dollar_value
            confidence_low = monthly.confidence_interval[0]
            confidence_high = monthly.confidence_interval[1]
            evidence_strength = monthly.evidence_strength

        snapshot = EvidenceSnapshot(
            timestamp=datetime.now(timezone.utc),
            repo_path=str(self.repo_path),
            commit_sha=commit_sha,
            total_commits=patterns.total_commits,
            active_days=patterns.active_days,
            top_authors=[a.author for a in authors[:5]],
            top_churning_files=[c.file_path for c in churn[:5]],
            mark_commit_links=mark_commit_links,
            gotcha_marks=gotcha_marks,
            decision_marks=decision_marks,
            monthly_value=monthly_value,
            confidence_low=confidence_low,
            confidence_high=confidence_high,
            evidence_strength=evidence_strength,
            notes=notes,
        )

        # Save snapshot
        self._save_snapshot(snapshot)

        return snapshot

    async def export(
        self,
        output_path: Path | str,
        format: str = "markdown",
    ) -> dict[str, Any]:
        """
        Export evidence report.

        Formats:
            - markdown: Human-readable report
            - json: Machine-readable data
        """
        output_path = Path(output_path)
        snapshot = await self.snapshot(notes="Export")

        if format == "json":
            content = json.dumps(snapshot.to_dict(), indent=2)
        else:
            content = self._render_markdown_report(snapshot)

        output_path.parent.mkdir(parents=True, exist_ok=True)
        with open(output_path, "w") as f:
            f.write(content)

        return {
            "status": "exported",
            "path": str(output_path),
            "format": format,
            "snapshot": snapshot.to_dict(),
        }

    async def compare(
        self,
        older: str | None = None,
        newer: str | None = None,
    ) -> dict[str, Any]:
        """
        Compare two snapshots.

        If not specified, compares latest with previous.
        """
        snapshots = self._list_snapshots()

        if len(snapshots) < 2:
            return {
                "status": "insufficient_data",
                "message": "Need at least 2 snapshots to compare",
            }

        older_snapshot = self._load_snapshot(older) if older else snapshots[-2]
        newer_snapshot = self._load_snapshot(newer) if newer else snapshots[-1]

        comparison = self._compare_snapshots(older_snapshot, newer_snapshot)

        return {
            "status": "compared",
            "older": older_snapshot.to_dict(),
            "newer": newer_snapshot.to_dict(),
            "comparison": comparison,
        }

    def _save_snapshot(self, snapshot: EvidenceSnapshot) -> None:
        """Persist snapshot to disk."""
        snapshots_dir = self.config.snapshots_dir
        snapshots_dir.mkdir(parents=True, exist_ok=True)

        filename = f"snapshot_{snapshot.timestamp.strftime('%Y%m%d_%H%M%S')}.json"
        filepath = snapshots_dir / filename

        with open(filepath, "w") as f:
            json.dump(snapshot.to_dict(), f, indent=2)

    def _load_latest_snapshot(self) -> EvidenceSnapshot | None:
        """Load most recent snapshot."""
        snapshots = self._list_snapshots()
        return snapshots[-1] if snapshots else None

    def _load_snapshot(self, name: str) -> EvidenceSnapshot | None:
        """Load specific snapshot by name."""
        snapshots_dir = self.config.snapshots_dir
        filepath = snapshots_dir / f"{name}.json"

        if not filepath.exists():
            filepath = snapshots_dir / name  # Try without .json

        if filepath.exists():
            with open(filepath) as f:
                return EvidenceSnapshot.from_dict(json.load(f))
        return None

    def _list_snapshots(self) -> list[EvidenceSnapshot]:
        """List all snapshots, oldest first."""
        snapshots_dir = self.config.snapshots_dir

        if not snapshots_dir.exists():
            return []

        snapshots = []
        for filepath in sorted(snapshots_dir.glob("snapshot_*.json")):
            with open(filepath) as f:
                snapshots.append(EvidenceSnapshot.from_dict(json.load(f)))

        return snapshots

    def _compare_snapshots(
        self,
        older: EvidenceSnapshot | None,
        newer: EvidenceSnapshot,
    ) -> dict[str, Any]:
        """Compare two snapshots."""
        if older is None:
            return {"status": "no_baseline", "message": "First snapshot, no comparison"}

        return {
            "time_delta_hours": (newer.timestamp - older.timestamp).total_seconds() / 3600,
            "commit_delta": newer.total_commits - older.total_commits,
            "monthly_value_delta": newer.monthly_value - older.monthly_value,
            "monthly_value_pct_change": (
                ((newer.monthly_value - older.monthly_value) / older.monthly_value * 100)
                if older.monthly_value > 0
                else 0.0
            ),
            "evidence_strength_change": (
                f"{older.evidence_strength} → {newer.evidence_strength}"
                if older.evidence_strength != newer.evidence_strength
                else "unchanged"
            ),
        }

    def _render_markdown_report(self, snapshot: EvidenceSnapshot) -> str:
        """Render snapshot as markdown report."""
        target = self.config.target_monthly
        exceeds = snapshot.monthly_value >= target

        return f"""# Evidence Report

**Repository**: {snapshot.repo_path}
**Generated**: {snapshot.timestamp.isoformat()}
**Commit**: {snapshot.commit_sha[:8]}

---

## Executive Summary

**Monthly Value**: ${snapshot.monthly_value:,.2f}
**Target**: ${target:,.2f}
**Status**: {"✅ EXCEEDS TARGET" if exceeds else "⚠️ Below target"}

Confidence Interval (95%): ${snapshot.confidence_low:,.2f} - ${snapshot.confidence_high:,.2f}
Evidence Strength: {snapshot.evidence_strength.upper()}

---

## Repository Activity

- **Total Commits Analyzed**: {snapshot.total_commits}
- **Active Days**: {snapshot.active_days}

### Top Authors
{chr(10).join(f"- {author}" for author in snapshot.top_authors)}

### High-Churn Files
{chr(10).join(f"- {f}" for f in snapshot.top_churning_files)}

---

## Witness Integration

- **Mark-Commit Correlations**: {snapshot.mark_commit_links}
- **Gotcha Marks**: {snapshot.gotcha_marks}
- **Decision Marks**: {snapshot.decision_marks}

---

## ROI Breakdown

The monthly value of ${snapshot.monthly_value:,.2f} comes from:

1. **Gotcha Prevention**: Each gotcha mark saves ~30 minutes of rediscovery time
2. **Decision Proofs**: Documented decisions save ~2 hours vs. re-debating
3. **Pattern Reuse**: Captured patterns save ~1 hour per reuse

At $80/hour, this translates to the monthly value above.

---

## Recommendations

{self._generate_recommendations(snapshot)}

---

*Report generated by kgents evidence lifecycle.*
*"The proof IS the decision. The mark IS the witness."*
"""

    def _generate_recommendations(self, snapshot: EvidenceSnapshot) -> str:
        """Generate actionable recommendations."""
        recs = []

        if snapshot.evidence_strength == "weak":
            recs.append("- **Increase witness usage**: Create more marks, especially gotchas")

        if snapshot.gotcha_marks < 10:
            recs.append(
                "- **Document gotchas**: Run `km 'gotcha' --tag gotcha` when you discover pitfalls"
            )

        if snapshot.mark_commit_links < 5:
            recs.append(
                "- **Link marks to work**: Reference commit SHAs in marks, or mark right before commits"
            )

        if snapshot.monthly_value < self.config.target_monthly:
            gap = self.config.target_monthly - snapshot.monthly_value
            needed_gotchas = int(gap / (0.5 * self.config.hourly_rate))  # 30 min each
            recs.append(f"- **To reach target**: Capture ~{needed_gotchas} more gotchas this month")

        if not recs:
            recs.append("- **Keep it up!** Evidence strength is good, continue current practices.")

        return "\n".join(recs)


# Convenience functions for CLI
async def init_lifecycle(
    repo_path: Path | str,
    witness: "WitnessPersistence | None" = None,
) -> dict[str, Any]:
    """Initialize evidence lifecycle for a repo."""
    lifecycle = EvidenceLifecycle(repo_path, witness)
    return await lifecycle.init()


async def refresh_lifecycle(
    repo_path: Path | str,
    witness: "WitnessPersistence | None" = None,
) -> dict[str, Any]:
    """Refresh evidence for a repo."""
    lifecycle = EvidenceLifecycle(repo_path, witness)
    return await lifecycle.refresh()


async def export_report(
    repo_path: Path | str,
    output_path: Path | str,
    format: str = "markdown",
    witness: "WitnessPersistence | None" = None,
) -> dict[str, Any]:
    """Export evidence report."""
    lifecycle = EvidenceLifecycle(repo_path, witness)
    return await lifecycle.export(output_path, format)


__all__ = [
    "EvidenceSnapshot",
    "EvidenceConfig",
    "EvidenceLifecycle",
    "init_lifecycle",
    "refresh_lifecycle",
    "export_report",
]
