"""
Test Health Dashboard Integration.

Provides:
1. TestHealthMetrics - Test suite health data
2. TestHealthPanel - Textual widget for dashboard display
3. collect_test_health_metrics - Collector function

Dashboard Layout:
┌─────────────────────────────────────────────────────────────┐
│ TEST HEALTH                                      [1Hz]      │
├─────────────────────────────────────────────────────────────┤
│ Total: 11,673  │  Pass Rate: 99.9%  │  Avg Time: 7.3ms     │
│                                                             │
│ Tier Distribution:                                          │
│ ████████████████████████████████████░░░░ INSTANT (68%)     │
│ ████████████░░░░░░░░░░░░░░░░░░░░░░░░░░░░ FAST (25%)        │
│ ███░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░ MEDIUM (5%)       │
│ ░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░ SLOW (2%)         │
│                                                             │
│ Recommendations:                                            │
│ ⚠ 3 tests could be parallelized (saves ~12s)               │
│ ⚠ 2 tests have 95% coverage overlap                        │
└─────────────────────────────────────────────────────────────┘

AGENTESE: self.test.health.manifest
"""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from testing.optimization import (
    RefinementTracker,
    TestTier,
    recommend_optimizations,
)

# Default paths (same as pytest_plugin)
_PROJECT_ROOT = Path(__file__).parent.parent.parent.parent.parent  # -> kgents root
_GHOST_DIR = _PROJECT_ROOT / ".kgents" / "ghost"
_PROFILES_PATH = _GHOST_DIR / "test_profiles.jsonl"


@dataclass
class TestHealthMetrics:
    """Test suite health metrics for dashboard display."""

    total_tests: int = 0
    pass_rate: float = 1.0  # 0.0 - 1.0
    avg_time_ms: float = 0.0
    total_time_s: float = 0.0
    failure_count: int = 0

    # Tier distribution
    tier_counts: dict[str, int] = field(default_factory=dict)
    tier_percentages: dict[str, float] = field(default_factory=dict)

    # Recommendations
    recommendation_count: int = 0
    top_recommendations: list[dict[str, Any]] = field(default_factory=list)

    # Expensive tests
    expensive_test_count: int = 0
    expensive_tests: list[dict[str, Any]] = field(default_factory=list)

    # Status
    is_online: bool = True
    last_profile_time: datetime | None = None

    @property
    def status_text(self) -> str:
        """Human-readable status."""
        if not self.is_online:
            return "NO DATA"
        if self.expensive_test_count > 5:
            return "NEEDS WORK"
        if self.recommendation_count > 0:
            return "OPTIMIZABLE"
        if self.pass_rate < 0.95:
            return "FAILING"
        return "HEALTHY"


async def collect_test_health_metrics(
    profiles_path: Path | None = None,
) -> TestHealthMetrics:
    """
    Collect test health metrics from stored profiles.

    Returns empty metrics with is_online=False if no profiles exist.
    """
    path = profiles_path or _PROFILES_PATH

    if not path.exists():
        return TestHealthMetrics(is_online=False)

    try:
        tracker = RefinementTracker(log_path=path)

        if not tracker.profiles:
            return TestHealthMetrics(is_online=False)

        # Basic stats
        total = len(tracker.profiles)
        total_time = sum(p.duration_ms for p in tracker.profiles.values())
        avg_time = total_time / total if total > 0 else 0

        # Tier distribution
        tier_counts = {tier.value: 0 for tier in TestTier}
        for profile in tracker.profiles.values():
            tier_counts[profile.tier.value] += 1

        tier_pcts = {
            tier: (count / total * 100) if total > 0 else 0 for tier, count in tier_counts.items()
        }

        # Recommendations
        recommendations = recommend_optimizations(tracker)
        top_recs = [
            {
                "test_id": r.test_id,
                "action": r.action,
                "savings_ms": r.estimated_savings_ms,
            }
            for r in recommendations[:5]
        ]

        # Expensive tests
        expensive = tracker.expensive_tests()
        expensive_list = [
            {
                "test_id": p.test_id,
                "duration_ms": p.duration_ms,
            }
            for p in expensive[:5]
        ]

        # Get last profile time
        last_time = None
        for profile in tracker.profiles.values():
            if last_time is None or profile.last_profiled > last_time:
                last_time = profile.last_profiled

        return TestHealthMetrics(
            total_tests=total,
            pass_rate=1.0,  # TODO: Track from test results
            avg_time_ms=avg_time,
            total_time_s=total_time / 1000,
            failure_count=0,  # TODO: Track from test results
            tier_counts=tier_counts,
            tier_percentages=tier_pcts,
            recommendation_count=len(recommendations),
            top_recommendations=top_recs,
            expensive_test_count=len(expensive),
            expensive_tests=expensive_list,
            is_online=True,
            last_profile_time=last_time,
        )

    except Exception:
        return TestHealthMetrics(is_online=False)


def create_demo_test_metrics() -> TestHealthMetrics:
    """Create demo metrics for dashboard preview."""
    import random

    total = 11673
    tier_counts = {
        "instant": int(total * 0.68),
        "fast": int(total * 0.25),
        "medium": int(total * 0.05),
        "slow": int(total * 0.015),
        "expensive": int(total * 0.005),
    }

    return TestHealthMetrics(
        total_tests=total,
        pass_rate=0.999,
        avg_time_ms=7.3,
        total_time_s=85.2,
        failure_count=random.randint(0, 3),
        tier_counts=tier_counts,
        tier_percentages={tier: count / total * 100 for tier, count in tier_counts.items()},
        recommendation_count=5,
        top_recommendations=[
            {
                "test_id": "test_trace_analysis",
                "action": "mark_slow",
                "savings_ms": 35000,
            },
            {
                "test_id": "test_dashboard_collectors",
                "action": "cache_static_analysis",
                "savings_ms": 30000,
            },
        ],
        expensive_test_count=7,
        expensive_tests=[
            {"test_id": "test_trace_analysis::test_full", "duration_ms": 42000},
            {"test_id": "test_dashboard::test_collect", "duration_ms": 35000},
        ],
        is_online=True,
        last_profile_time=datetime.now(timezone.utc),
    )


# =============================================================================
# Textual Widget (for dashboard integration)
# =============================================================================


def create_test_health_panel_class() -> type:
    """
    Create TestHealthPanel class.

    Delayed creation to avoid importing textual at module load.
    """
    from textual.reactive import reactive
    from textual.widgets import Static

    class TestHealthPanel(Static, can_focus=True):
        """Test suite health panel for dashboard."""

        DEFAULT_CSS = """
        TestHealthPanel {
            width: 1fr;
            height: auto;
            border: round #9370db;
            padding: 0 1;
            background: #1a1a1a;
        }

        TestHealthPanel:focus {
            border: double #ba55d3;
            background: #252525;
        }

        TestHealthPanel .panel-title {
            color: #9370db;
            text-style: bold;
        }

        TestHealthPanel .healthy {
            color: #7d9c7a;
        }

        TestHealthPanel .warning {
            color: #e6a352;
        }

        TestHealthPanel .critical {
            color: #e88a8a;
        }
        """

        total_tests: reactive[int] = reactive(0)
        pass_rate: reactive[float] = reactive(1.0)
        avg_time_ms: reactive[float] = reactive(0.0)
        tier_counts: reactive[dict] = reactive({})  # type: ignore[type-arg]
        recommendation_count: reactive[int] = reactive(0)
        expensive_count: reactive[int] = reactive(0)
        status: reactive[str] = reactive("--")
        is_online: reactive[bool] = reactive(True)

        def _render_tier_bar(self, tier: str, pct: float, width: int = 20) -> str:
            """Render a tier distribution bar."""
            filled = int(pct / 5)  # Scale 100% to width
            bar = "█" * filled + "░" * (width - filled)
            return f"{bar} {tier.upper()} ({pct:.0f}%)"

        def render(self) -> str:
            if not self.is_online:
                return "TEST HEALTH\n├─ [no profile data]\n└─ Run: pytest --profile-tests"

            lines = [f"TEST HEALTH ({self.status})"]

            # Summary line
            lines.append(
                f"├─ Total: {self.total_tests:,} │ "
                f"Pass: {self.pass_rate:.1%} │ "
                f"Avg: {self.avg_time_ms:.1f}ms"
            )

            # Tier distribution (compact)
            if self.tier_counts:
                lines.append("├─ Tiers:")
                for tier in ["instant", "fast", "medium", "slow", "expensive"]:
                    count = self.tier_counts.get(tier, 0)
                    if count > 0:
                        pct = (count / self.total_tests * 100) if self.total_tests > 0 else 0
                        bar = self._render_tier_bar(tier, pct, width=15)
                        lines.append(f"│  {bar}")

            # Recommendations summary
            if self.recommendation_count > 0:
                lines.append(f"└─ ⚠ {self.recommendation_count} optimizations available")
            elif self.expensive_count > 0:
                lines.append(f"└─ ⚠ {self.expensive_count} expensive tests")
            else:
                lines.append("└─ ✓ Suite is optimized")

            return "\n".join(lines)

        def update_from_metrics(self, metrics: TestHealthMetrics) -> None:
            """Update panel from metrics bundle."""
            self.total_tests = metrics.total_tests
            self.pass_rate = metrics.pass_rate
            self.avg_time_ms = metrics.avg_time_ms
            self.tier_counts = metrics.tier_counts
            self.recommendation_count = metrics.recommendation_count
            self.expensive_count = metrics.expensive_test_count
            self.status = metrics.status_text
            self.is_online = metrics.is_online

    return TestHealthPanel


__all__ = [
    "TestHealthMetrics",
    "collect_test_health_metrics",
    "create_demo_test_metrics",
    "create_test_health_panel_class",
]
