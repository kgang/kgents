"""
HabitEncoder: Aggregate developer patterns from multiple signal sources.

The central coordinator for Wave 4 of the Evergreen Prompt System.

Aggregates signals from:
- GitPatternAnalyzer: commit patterns, file focus, timing
- SessionPatternAnalyzer: Claude Code interaction patterns
- CodePatternAnalyzer: AST-based style detection

Produces a PolicyVector that influences prompt compilation.

See: spec/heritage.md Part II for theoretical foundations
See: plans/_continuations/evergreen-wave3-reformation-continuation.md
"""

from __future__ import annotations

import logging
from dataclasses import dataclass, field
from datetime import datetime
from pathlib import Path
from typing import Protocol, runtime_checkable

from .git_analyzer import GitAnalyzerError, GitPattern, GitPatternAnalyzer
from .policy import PolicyVector

logger = logging.getLogger(__name__)


@runtime_checkable
class PatternAnalyzer(Protocol):
    """Protocol for pattern analyzers."""

    def analyze(self) -> list[GitPattern]:
        """Analyze and return patterns."""
        ...


@dataclass(frozen=True)
class HabitEncoderConfig:
    """Configuration for habit encoding."""

    # Git analysis
    git_lookback_commits: int = 100
    git_enabled: bool = True

    # Session analysis
    session_enabled: bool = True
    session_lookback_days: int = 30

    # Code analysis
    code_enabled: bool = True
    code_sample_size: int = 50

    # Weights for combining signals
    git_weight: float = 0.4
    session_weight: float = 0.3
    code_weight: float = 0.3

    def validate(self) -> None:
        """Validate configuration."""
        total = self.git_weight + self.session_weight + self.code_weight
        if abs(total - 1.0) > 0.01:
            raise ValueError(f"Weights must sum to 1.0, got {total}")

    @classmethod
    def default(cls) -> HabitEncoderConfig:
        """Create default configuration."""
        return cls()


@dataclass
class HabitEncoder:
    """
    Encode developer habits from observable patterns.

    The HabitEncoder aggregates signals from multiple analyzers,
    weights them, and produces a PolicyVector that influences
    prompt compilation.

    Thread-safe: all operations are stateless and use subprocess.

    Example:
        >>> encoder = HabitEncoder(repo_path=Path("."))
        >>> policy = encoder.encode()
        >>> print(policy.verbosity)
        0.6
        >>> print(policy.reasoning_trace)
        ('Analyzing git patterns...', ...)
    """

    repo_path: Path
    config: HabitEncoderConfig = field(default_factory=HabitEncoderConfig.default)

    # Optional: inject custom analyzers for testing
    _git_analyzer: GitPatternAnalyzer | None = None
    _session_analyzer: PatternAnalyzer | None = None
    _code_analyzer: PatternAnalyzer | None = None

    def __post_init__(self) -> None:
        """Initialize analyzers."""
        if self._git_analyzer is None and self.config.git_enabled:
            self._git_analyzer = GitPatternAnalyzer(
                repo_path=self.repo_path,
                lookback_commits=self.config.git_lookback_commits,
            )

    def encode(self) -> PolicyVector:
        """
        Encode developer habits into a PolicyVector.

        Algorithm:
        1. Run enabled analyzers in sequence
        2. Convert patterns to partial PolicyVectors
        3. Merge with configured weights
        4. Return final PolicyVector with full reasoning trace

        Returns:
            PolicyVector with learned preferences
        """
        traces: list[str] = [
            f"HabitEncoder starting at {datetime.now().isoformat()}",
            f"Repository: {self.repo_path}",
        ]

        policies: list[tuple[PolicyVector, float]] = []

        # Git patterns
        if self.config.git_enabled:
            try:
                git_policy = self._encode_git_patterns(traces)
                if git_policy:
                    policies.append((git_policy, self.config.git_weight))
            except Exception as e:
                traces.append(f"Git analysis failed: {e}")
                logger.warning(f"Git analysis failed: {e}")

        # Session patterns
        if self.config.session_enabled:
            try:
                session_policy = self._encode_session_patterns(traces)
                if session_policy:
                    policies.append((session_policy, self.config.session_weight))
            except Exception as e:
                traces.append(f"Session analysis failed: {e}")
                logger.warning(f"Session analysis failed: {e}")

        # Code patterns
        if self.config.code_enabled:
            try:
                code_policy = self._encode_code_patterns(traces)
                if code_policy:
                    policies.append((code_policy, self.config.code_weight))
            except Exception as e:
                traces.append(f"Code analysis failed: {e}")
                logger.warning(f"Code analysis failed: {e}")

        # Merge all policies
        if not policies:
            traces.append("No patterns found, using defaults")
            return PolicyVector.default().with_trace("\n".join(traces))

        final_policy = self._merge_policies(policies, traces)
        traces.append(f"Final policy confidence: {final_policy.confidence:.2f}")

        return PolicyVector(
            verbosity=final_policy.verbosity,
            formality=final_policy.formality,
            risk_tolerance=final_policy.risk_tolerance,
            section_weights=final_policy.section_weights,
            domain_focus=final_policy.domain_focus,
            learned_from=final_policy.learned_from,
            confidence=final_policy.confidence,
            generated_at=datetime.now(),
            reasoning_trace=tuple(traces),
        )

    def _encode_git_patterns(self, traces: list[str]) -> PolicyVector | None:
        """Encode patterns from git history."""
        traces.append("Analyzing git patterns...")

        if self._git_analyzer is None:
            traces.append("  Git analyzer not available")
            return None

        try:
            patterns = self._git_analyzer.analyze()
            traces.append(f"  Found {len(patterns)} patterns")

            if not patterns:
                return None

            # Log pattern summaries
            for p in patterns[:3]:
                traces.append(f"    {p.pattern_type}: {p.description[:50]}...")

            policy = PolicyVector.from_git_patterns(patterns)
            traces.append(
                f"  Git policy: verbosity={policy.verbosity:.2f}, formality={policy.formality:.2f}"
            )

            return policy

        except GitAnalyzerError as e:
            traces.append(f"  Git error: {e}")
            return None

    def _encode_session_patterns(self, traces: list[str]) -> PolicyVector | None:
        """
        Encode patterns from Claude Code session history.

        Currently a stub - session analyzer will be implemented separately.
        """
        traces.append("Analyzing session patterns...")

        if self._session_analyzer is not None:
            # Use injected analyzer (for testing)
            patterns = self._session_analyzer.analyze()
            traces.append(f"  Found {len(patterns)} session patterns")
            if patterns:
                return PolicyVector.from_git_patterns(patterns)  # Reuse pattern conversion

        # Try to import session analyzer
        try:
            from .session_analyzer import SessionPatternAnalyzer

            analyzer = SessionPatternAnalyzer(
                lookback_days=self.config.session_lookback_days,
            )
            patterns = analyzer.analyze()
            traces.append(f"  Found {len(patterns)} session patterns")

            if patterns:
                return PolicyVector.from_session_patterns(patterns)
            return None

        except ImportError:
            traces.append("  Session analyzer not available (Wave 4 in progress)")
            return None
        except Exception as e:
            traces.append(f"  Session analysis error: {e}")
            return None

    def _encode_code_patterns(self, traces: list[str]) -> PolicyVector | None:
        """
        Encode patterns from code AST analysis.

        Currently a stub - code analyzer will be implemented separately.
        """
        traces.append("Analyzing code patterns...")

        if self._code_analyzer is not None:
            # Use injected analyzer (for testing)
            patterns = self._code_analyzer.analyze()
            traces.append(f"  Found {len(patterns)} code patterns")
            if patterns:
                return PolicyVector.from_git_patterns(patterns)  # Reuse pattern conversion

        # Try to import code analyzer
        try:
            from .code_analyzer import CodePatternAnalyzer

            analyzer = CodePatternAnalyzer(
                repo_path=self.repo_path,
                sample_size=self.config.code_sample_size,
            )
            patterns = analyzer.analyze()
            traces.append(f"  Found {len(patterns)} code patterns")

            if patterns:
                return PolicyVector.from_code_patterns(patterns)
            return None

        except ImportError:
            traces.append("  Code analyzer not available (Wave 4 in progress)")
            return None
        except Exception as e:
            traces.append(f"  Code analysis error: {e}")
            return None

    def _merge_policies(
        self,
        policies: list[tuple[PolicyVector, float]],
        traces: list[str],
    ) -> PolicyVector:
        """
        Merge multiple PolicyVectors with weights.

        Uses heuristic fusion per taste decision:
        - Scalar values: weighted average
        - Section weights: union with weighted values
        - Domain focus: union with weighted values
        - Confidence: minimum (conservative)
        """
        if len(policies) == 1:
            traces.append("Single source, no merging needed")
            return policies[0][0]

        traces.append(f"Merging {len(policies)} policy sources...")

        # Normalize weights
        total_weight = sum(w for _, w in policies)
        normalized: list[tuple[PolicyVector, float]] = [(p, w / total_weight) for p, w in policies]

        # Start with first policy
        result = normalized[0][0]
        traces.append(f"  Base: weight={normalized[0][1]:.2f}")

        # Merge in subsequent policies
        for i, (policy, weight) in enumerate(normalized[1:], 2):
            # Adjust weight for incremental merge
            # After merging N policies with equal weight, we want equal contribution
            merge_weight = weight / (sum(w for _, w in normalized[:i]))
            result = result.merge_with(policy, weight=merge_weight)
            traces.append(f"  Merged source {i}: weight={weight:.2f}")

        return result


def encode_habits(repo_path: Path | str, config: HabitEncoderConfig | None = None) -> PolicyVector:
    """
    Convenience function to encode habits from a repository.

    Args:
        repo_path: Path to the git repository
        config: Optional configuration

    Returns:
        PolicyVector with learned preferences
    """
    encoder = HabitEncoder(
        repo_path=Path(repo_path),
        config=config or HabitEncoderConfig.default(),
    )
    return encoder.encode()


__all__ = [
    "HabitEncoder",
    "HabitEncoderConfig",
    "PatternAnalyzer",
    "encode_habits",
]
