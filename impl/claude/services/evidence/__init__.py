"""
Evidence Mining Service - Crown Jewel

Prove witnessing ROI with data, not anecdotes.

Philosophy:
    "The proof IS the decision. The mark IS the witness."
    Evidence over intuition. Traces over reflexes.

Usage:
    from services.evidence import RepositoryMiner, ROICalculator, exceeds_target

    # Mine any git repository
    miner = RepositoryMiner("/path/to/repo")
    patterns = miner.mine_commit_patterns()

    # Calculate ROI
    calculator = ROICalculator(witness_persistence, repo_path)
    monthly = await calculator.calculate_monthly_value(hourly_rate=80.0)

    # Check target
    exceeds, value = await exceeds_target(witness, repo, target_monthly=800.0)

CLI:
    kg evidence mine              # Mine git patterns
    kg evidence correlate         # Link marks ↔ commits
    kg evidence roi               # Calculate ROI
    kg evidence lifecycle init    # Initialize tracking
    kg evidence lifecycle refresh # Re-mine and update
"""

from __future__ import annotations

# Models - frozen dataclasses for type-safe evidence
from .models import (
    # Enums
    CorrelationType,
    # Mining results
    CommitPattern,
    FileChurnMetric,
    AuthorPattern,
    BugCorrelation,
    # Witness correlation
    MarkCommitLink,
    DecisionCommitChain,
    GotchaVsBugCorrelation,
    # ROI metrics
    TimeROI,
    QualityROI,
    DecisionROI,
    EvidenceReport,
)

# Mining - generalizable git archaeology
from .mining import (
    RepositoryMiner,
    CommitPatternSummary,
)

# Correlation - link witness marks with commits
from .correlation import (
    EvidenceCorrelator,
)

# ROI - the key metric
from .roi import (
    ROICalculator,
    MonthlyValue,
    get_monthly_roi,
    exceeds_target,
)

__all__ = [
    # Enums
    "CorrelationType",
    # Models
    "CommitPattern",
    "FileChurnMetric",
    "AuthorPattern",
    "BugCorrelation",
    "MarkCommitLink",
    "DecisionCommitChain",
    "GotchaVsBugCorrelation",
    "TimeROI",
    "QualityROI",
    "DecisionROI",
    "EvidenceReport",
    # Mining
    "RepositoryMiner",
    "CommitPatternSummary",
    # Correlation
    "EvidenceCorrelator",
    # ROI
    "ROICalculator",
    "MonthlyValue",
    "get_monthly_roi",
    "exceeds_target",
]
