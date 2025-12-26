"""
Audit Service: Spec validation against principles and implementation.

This service provides:
1. Principle scoring - Evaluate specs against 7 constitutional principles
2. Drift detection - Compare spec vs implementation
3. System auditing - Health checks for all Crown Jewels

Philosophy:
    "The specification is a promise. The audit verifies the promise."

See: brainstorming/tool-use/CLAUDE_CODE_CLI_STRATEGY.md (Phase 1)
See: spec/principles.md (7 constitutional principles)
"""

from .drift import detect_drift
from .principles import score_principles
from .types import AuditResult, AuditSeverity, DriftItem, PrincipleScores

__all__ = [
    "AuditResult",
    "DriftItem",
    "PrincipleScores",
    "AuditSeverity",
    "score_principles",
    "detect_drift",
]
