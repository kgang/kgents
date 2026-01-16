"""ROI Calculator for Witnessing Practices.

This module calculates the return on investment for witnessing practices,
answering the question: "RoC on kgents will be >$800/month".

Philosophy:
    Evidence over intuition. Traces over reflexes.
    Every mark has value - we quantify it.
"""

from dataclasses import dataclass
from datetime import datetime, timedelta
from pathlib import Path
from typing import Any

from .correlation import EvidenceCorrelator
from .mining import RepositoryMiner


@dataclass
class TimeROI:
    """Time-based return on investment."""

    hours_saved: float
    dollar_value: float
    breakdown: dict[str, float]  # category -> hours
    confidence_interval: tuple[float, float]  # (low, high) in dollars
    sample_size: int


@dataclass
class QualityROI:
    """Quality improvement metrics."""

    bug_rate_before: float  # bugs per commit
    bug_rate_after: float
    bug_reduction_percent: float
    pattern_reuse_count: int
    avg_pattern_reuse_saves_hours: float
    quality_dollar_value: float


@dataclass
class DecisionROI:
    """Decision-making efficiency metrics."""

    total_decisions: int
    decisions_with_proofs: int
    proof_ratio: float
    avg_decision_to_commit_hours: float
    supersession_count: int  # decisions that evolved
    decision_dollar_value: float


@dataclass
class MonthlyValue:
    """The KEY METRIC: Monthly dollar value."""

    total_hours_saved: float
    dollar_value: float
    confidence_interval: tuple[float, float]
    breakdown: dict[str, dict[str, Any]]  # category -> metrics
    assumptions: dict[str, Any]
    evidence_strength: str  # "weak" | "moderate" | "strong"


class ROICalculator:
    """Calculate ROI for witnessing practices.

    Answers the question: "What is the monthly dollar value of witnessing?"

    Key Assumptions:
        - Each gotcha mark saves 30 min average rediscovery time
        - Each decision with proof saves 2 hours vs. re-debating
        - Baseline decision time is 24-48 hours industry average
        - Pattern reuse saves 1 hour per reuse on average
        - Bug prevention saves 4 hours per bug (industry standard)
    """

    # Industry-standard assumptions
    GOTCHA_SAVES_MINUTES = 30  # Time saved per gotcha mark
    DECISION_PROOF_SAVES_HOURS = 2.0  # Time saved per documented decision
    PATTERN_REUSE_SAVES_HOURS = 1.0  # Time saved per pattern reuse
    BUG_COST_HOURS = 4.0  # Average cost to fix a bug (industry standard)
    BASELINE_DECISION_HOURS = 36.0  # Industry average decision time (24-48h range)

    def __init__(self, witness_persistence, repo_path: Path):
        """Initialize ROI calculator.

        Args:
            witness_persistence: WitnessPersistence instance for mark queries
            repo_path: Path to git repository for mining
        """
        self.witness_persistence = witness_persistence
        self.miner = RepositoryMiner(repo_path)
        self.correlator = EvidenceCorrelator(witness_persistence, repo_path)

    async def calculate_time_roi(
        self,
        since: datetime | None = None,
        hourly_rate: float = 80.0,
    ) -> TimeROI:
        """Calculate time-based ROI.

        Estimates time saved through:
        - Gotcha marks preventing rediscovery
        - Pattern reuse from annotations
        - Faster decision-making with proofs

        Args:
            since: Calculate ROI since this date (default: all time)
            hourly_rate: Dollar value per hour (default: $80/hour)

        Returns:
            TimeROI with hours saved and dollar value
        """
        # Get gotcha marks
        gotcha_marks = await self.witness_persistence.query_marks(
            filters={"mark_type": "gotcha"},
            since=since,
        )

        # Get pattern reuse via annotation links
        annotations = await self.witness_persistence.query_marks(
            filters={"mark_type": "annotation"},
            since=since,
        )

        # Estimate pattern reuse count (each annotation potentially reused)
        # Conservative: assume each annotation is referenced once
        pattern_reuse_count = len(annotations)

        # Calculate hours saved
        gotcha_hours = len(gotcha_marks) * (self.GOTCHA_SAVES_MINUTES / 60.0)
        pattern_hours = pattern_reuse_count * self.PATTERN_REUSE_SAVES_HOURS

        total_hours = gotcha_hours + pattern_hours
        dollar_value = total_hours * hourly_rate

        # Confidence interval: ±30% (conservative)
        confidence_low = dollar_value * 0.7
        confidence_high = dollar_value * 1.3

        return TimeROI(
            hours_saved=total_hours,
            dollar_value=dollar_value,
            breakdown={
                "gotcha_prevention": gotcha_hours,
                "pattern_reuse": pattern_hours,
            },
            confidence_interval=(confidence_low, confidence_high),
            sample_size=len(gotcha_marks) + len(annotations),
        )

    async def calculate_quality_roi(
        self,
        witness_start_date: datetime,
        hourly_rate: float = 80.0,
    ) -> QualityROI:
        """Calculate quality improvement ROI.

        Compares bug rates before and after witness adoption.

        Args:
            witness_start_date: When witnessing practice started
            hourly_rate: Dollar value per hour

        Returns:
            QualityROI with bug rate improvements
        """
        # Get commit history
        all_commits = await self.miner.get_commits_in_range(
            since=witness_start_date - timedelta(days=365),  # 1 year before
            until=None,
        )

        # Partition commits
        before_commits = [c for c in all_commits if c.authored_date < witness_start_date]
        after_commits = [c for c in all_commits if c.authored_date >= witness_start_date]

        # Count bug-fix commits (heuristic: "fix" in message)
        def is_bug_fix(commit) -> bool:
            msg_lower = commit.message.lower()
            return any(keyword in msg_lower for keyword in ["fix", "bug", "error", "crash"])

        bugs_before = sum(1 for c in before_commits if is_bug_fix(c))
        bugs_after = sum(1 for c in after_commits if is_bug_fix(c))

        bug_rate_before = bugs_before / len(before_commits) if before_commits else 0.0
        bug_rate_after = bugs_after / len(after_commits) if after_commits else 0.0

        # Calculate reduction
        if bug_rate_before > 0:
            reduction_percent = ((bug_rate_before - bug_rate_after) / bug_rate_before) * 100
            bugs_prevented = (bug_rate_before - bug_rate_after) * len(after_commits)
        else:
            reduction_percent = 0.0
            bugs_prevented = 0.0

        # Dollar value: bugs prevented × cost per bug
        quality_dollar_value = bugs_prevented * self.BUG_COST_HOURS * hourly_rate

        # Get pattern reuse from annotations
        annotations = await self.witness_persistence.query_marks(
            filters={"mark_type": "annotation"},
            since=witness_start_date,
        )
        pattern_reuse_count = len(annotations)
        pattern_hours = pattern_reuse_count * self.PATTERN_REUSE_SAVES_HOURS

        return QualityROI(
            bug_rate_before=bug_rate_before,
            bug_rate_after=bug_rate_after,
            bug_reduction_percent=reduction_percent,
            pattern_reuse_count=pattern_reuse_count,
            avg_pattern_reuse_saves_hours=pattern_hours,
            quality_dollar_value=quality_dollar_value + (pattern_hours * hourly_rate),
        )

    async def calculate_decision_roi(
        self,
        since: datetime | None = None,
        hourly_rate: float = 80.0,
    ) -> DecisionROI:
        """Calculate decision-making efficiency ROI.

        Measures:
        - Decisions with proofs (full reasoning traces)
        - Decision-to-commit time
        - Supersession tracking (evolving decisions)

        Args:
            since: Calculate since this date
            hourly_rate: Dollar value per hour

        Returns:
            DecisionROI with decision metrics
        """
        # Get all fusion marks (decisions)
        fusion_marks = await self.witness_persistence.query_marks(
            filters={"mark_type": "fusion"},
            since=since,
        )

        total_decisions = len(fusion_marks)

        # Count decisions with full proofs (kent_view + claude_view + synthesis)
        decisions_with_proofs = 0
        total_decision_time_hours = 0.0
        supersession_count = 0

        for mark in fusion_marks:
            metadata = mark.metadata or {}

            # Check if full proof exists
            has_proof = all(
                key in metadata for key in ["kent_view", "claude_view", "synthesis", "why"]
            )
            if has_proof:
                decisions_with_proofs += 1

            # Estimate decision time (timestamp to next commit)
            # This is a proxy - would need git correlation for accuracy
            # For now, assume documented decisions save time vs. baseline
            if has_proof:
                # With proof: assume quick (2 hours)
                total_decision_time_hours += 2.0
            else:
                # Without proof: assume baseline (36 hours)
                total_decision_time_hours += self.BASELINE_DECISION_HOURS

            # Check for supersession (metadata has 'supersedes' field)
            if metadata.get("supersedes"):
                supersession_count += 1

        proof_ratio = decisions_with_proofs / total_decisions if total_decisions > 0 else 0.0

        avg_decision_hours = (
            total_decision_time_hours / total_decisions if total_decisions > 0 else 0.0
        )

        # Dollar value: time saved vs. baseline
        # Each proof saves (BASELINE - 2 hours)
        time_saved_hours = decisions_with_proofs * (self.BASELINE_DECISION_HOURS - 2.0)
        decision_dollar_value = time_saved_hours * hourly_rate

        return DecisionROI(
            total_decisions=total_decisions,
            decisions_with_proofs=decisions_with_proofs,
            proof_ratio=proof_ratio,
            avg_decision_to_commit_hours=avg_decision_hours,
            supersession_count=supersession_count,
            decision_dollar_value=decision_dollar_value,
        )

    async def calculate_monthly_value(
        self,
        hourly_rate: float = 80.0,
        witness_start_date: datetime | None = None,
    ) -> MonthlyValue:
        """Calculate THE KEY METRIC: Monthly dollar value.

        This is the headline number that answers:
        "RoC on kgents will be >$800/month"

        Args:
            hourly_rate: Dollar value per hour (default: $80/hour)
            witness_start_date: When witnessing started (for quality comparison)

        Returns:
            MonthlyValue with total monthly dollar value and breakdown
        """
        # Default to 30 days ago if no start date
        if witness_start_date is None:
            witness_start_date = datetime.now() - timedelta(days=90)

        # Calculate last 30 days
        since = datetime.now() - timedelta(days=30)

        # Get all ROI components
        time_roi = await self.calculate_time_roi(since=since, hourly_rate=hourly_rate)
        quality_roi = await self.calculate_quality_roi(
            witness_start_date=witness_start_date, hourly_rate=hourly_rate
        )
        decision_roi = await self.calculate_decision_roi(since=since, hourly_rate=hourly_rate)

        # Total monthly value
        total_hours = time_roi.hours_saved
        total_dollars = (
            time_roi.dollar_value
            + quality_roi.quality_dollar_value
            + decision_roi.decision_dollar_value
        )

        # Confidence interval: combine intervals
        confidence_low = time_roi.confidence_interval[0] * 0.7
        confidence_high = time_roi.confidence_interval[1] * 1.3

        # Evidence strength based on sample size
        if time_roi.sample_size >= 50:
            evidence_strength = "strong"
        elif time_roi.sample_size >= 20:
            evidence_strength = "moderate"
        else:
            evidence_strength = "weak"

        # Breakdown by category
        breakdown = {
            "time_savings": {
                "hours": time_roi.hours_saved,
                "dollars": time_roi.dollar_value,
                "breakdown": time_roi.breakdown,
            },
            "quality_improvements": {
                "bug_reduction_percent": quality_roi.bug_reduction_percent,
                "dollars": quality_roi.quality_dollar_value,
                "pattern_reuse_count": quality_roi.pattern_reuse_count,
            },
            "decision_efficiency": {
                "decisions_with_proofs": decision_roi.decisions_with_proofs,
                "proof_ratio": decision_roi.proof_ratio,
                "dollars": decision_roi.decision_dollar_value,
                "avg_decision_hours": decision_roi.avg_decision_to_commit_hours,
            },
        }

        # Assumptions made
        assumptions = {
            "hourly_rate": hourly_rate,
            "gotcha_saves_minutes": self.GOTCHA_SAVES_MINUTES,
            "decision_proof_saves_hours": self.DECISION_PROOF_SAVES_HOURS,
            "pattern_reuse_saves_hours": self.PATTERN_REUSE_SAVES_HOURS,
            "bug_cost_hours": self.BUG_COST_HOURS,
            "baseline_decision_hours": self.BASELINE_DECISION_HOURS,
            "calculation_period_days": 30,
        }

        return MonthlyValue(
            total_hours_saved=total_hours,
            dollar_value=total_dollars,
            confidence_interval=(confidence_low, confidence_high),
            breakdown=breakdown,
            assumptions=assumptions,
            evidence_strength=evidence_strength,
        )


# Convenience functions for common queries


async def get_monthly_roi(
    witness_persistence,
    repo_path: Path,
    hourly_rate: float = 80.0,
) -> MonthlyValue:
    """Get monthly ROI - the headline metric.

    Args:
        witness_persistence: WitnessPersistence instance
        repo_path: Path to git repository
        hourly_rate: Dollar value per hour

    Returns:
        MonthlyValue with total monthly dollar value
    """
    calculator = ROICalculator(witness_persistence, repo_path)
    return await calculator.calculate_monthly_value(hourly_rate=hourly_rate)


async def exceeds_target(
    witness_persistence,
    repo_path: Path,
    target_monthly: float = 800.0,
    hourly_rate: float = 80.0,
) -> tuple[bool, MonthlyValue]:
    """Check if ROI exceeds target.

    Args:
        witness_persistence: WitnessPersistence instance
        repo_path: Path to git repository
        target_monthly: Target monthly value in dollars (default: $800)
        hourly_rate: Dollar value per hour

    Returns:
        Tuple of (exceeds_target, monthly_value)
    """
    monthly = await get_monthly_roi(witness_persistence, repo_path, hourly_rate)
    return (monthly.dollar_value >= target_monthly, monthly)
