"""
Semantic Gatekeeper: Validate code against principles.

K-gent's Semantic Gatekeeper capability. Checks code, designs, and proposals
against the kgents principles and reports potential violations.

The Seven Principles:
1. Tasteful - Clear, justified purpose
2. Curated - Quality over quantity
3. Ethical - Augment, don't replace judgment
4. Joy-Inducing - Personality matters
5. Composable - Agents are morphisms
6. Heterarchical - Flux, not hierarchy
7. Generative - Spec compresses implementation

Usage:
    from agents.k.gatekeeper import SemanticGatekeeper, validate_file

    gatekeeper = SemanticGatekeeper()
    result = await gatekeeper.validate_file("path/to/file.py")
    print(result.format())

    # Or quick check
    violations = await validate_file("path/to/file.py")
"""

from __future__ import annotations

import re
from dataclasses import dataclass, field
from datetime import datetime, timezone
from enum import Enum
from pathlib import Path
from typing import TYPE_CHECKING, Any, Optional

if TYPE_CHECKING:
    from .llm import LLMClient


# =============================================================================
# Types
# =============================================================================


class Principle(str, Enum):
    """The seven kgents principles."""

    TASTEFUL = "tasteful"
    CURATED = "curated"
    ETHICAL = "ethical"
    JOY_INDUCING = "joy-inducing"
    COMPOSABLE = "composable"
    HETERARCHICAL = "heterarchical"
    GENERATIVE = "generative"


class Severity(str, Enum):
    """Severity of a violation."""

    INFO = "info"  # Observation, not necessarily a problem
    WARNING = "warning"  # Potential issue, worth reviewing
    ERROR = "error"  # Clear violation of principles
    CRITICAL = "critical"  # Severe violation, blocks merge


@dataclass
class Violation:
    """A potential principle violation."""

    principle: Principle
    severity: Severity
    message: str
    location: Optional[str] = None  # file:line or section
    evidence: Optional[str] = None  # The code/text that triggered this
    suggestion: Optional[str] = None  # How to fix

    def to_dict(self) -> dict[str, Any]:
        """Serialize to dictionary."""
        return {
            "principle": self.principle.value,
            "severity": self.severity.value,
            "message": self.message,
            "location": self.location,
            "evidence": self.evidence,
            "suggestion": self.suggestion,
        }

    def format(self) -> str:
        """Format for display."""
        severity_icons = {
            Severity.INFO: "i",
            Severity.WARNING: "!",
            Severity.ERROR: "X",
            Severity.CRITICAL: "XX",
        }
        icon = severity_icons.get(self.severity, "*")
        loc = f" ({self.location})" if self.location else ""

        lines = [f"[{icon}] [{self.principle.value}]{loc}: {self.message}"]

        if self.evidence:
            # Truncate long evidence
            evidence = (
                self.evidence[:100] + "..."
                if len(self.evidence) > 100
                else self.evidence
            )
            lines.append(f"    Evidence: {evidence}")

        if self.suggestion:
            lines.append(f"    Suggestion: {self.suggestion}")

        return "\n".join(lines)


@dataclass
class ValidationResult:
    """Result of validating against principles."""

    target: str  # What was validated
    timestamp: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    violations: list[Violation] = field(default_factory=list)
    passed: bool = True
    summary: str = ""

    def to_dict(self) -> dict[str, Any]:
        """Serialize to dictionary."""
        return {
            "target": self.target,
            "timestamp": self.timestamp.isoformat(),
            "violations": [v.to_dict() for v in self.violations],
            "passed": self.passed,
            "summary": self.summary,
            "by_severity": self.by_severity,
            "by_principle": self.by_principle,
        }

    @property
    def by_severity(self) -> dict[str, int]:
        """Count violations by severity."""
        counts: dict[str, int] = {}
        for v in self.violations:
            counts[v.severity.value] = counts.get(v.severity.value, 0) + 1
        return counts

    @property
    def by_principle(self) -> dict[str, int]:
        """Count violations by principle."""
        counts: dict[str, int] = {}
        for v in self.violations:
            counts[v.principle.value] = counts.get(v.principle.value, 0) + 1
        return counts

    def format(self) -> str:
        """Format for display."""
        lines = [
            f"[GATEKEEPER] Validation: {self.target}",
            "",
        ]

        if self.passed:
            lines.append("  Result: PASSED (no critical/error violations)")
        else:
            lines.append("  Result: FAILED")

        if self.violations:
            lines.append("")
            lines.append(f"  Violations: {len(self.violations)}")

            # Group by severity
            for severity in [
                Severity.CRITICAL,
                Severity.ERROR,
                Severity.WARNING,
                Severity.INFO,
            ]:
                count = self.by_severity.get(severity.value, 0)
                if count > 0:
                    lines.append(f"    {severity.value}: {count}")

            lines.append("")
            lines.append("  Details:")
            for violation in self.violations:
                lines.append("")
                lines.append("  " + violation.format().replace("\n", "\n  "))
        else:
            lines.append("")
            lines.append("  No violations detected.")

        if self.summary:
            lines.append("")
            lines.append(f"  Summary: {self.summary}")

        return "\n".join(lines)


# =============================================================================
# Specialized Analyzers (110% Domain 2)
# =============================================================================


@dataclass
class AnalyzerResult:
    """Result from a specialized analyzer."""

    score: float  # 0.0 (bad) to 1.0 (good)
    violations: list[Violation]
    insights: list[str]  # Non-violation observations


class TastefullnessAnalyzer:
    """
    Analyzer for TASTEFUL principle (110% Domain 2).

    Checks for:
    - Kitchen-sink classes (too many responsibilities)
    - Function bloat (>50 lines suggests unclear purpose)
    - Naming that suggests unclear scope
    - Accumulation of unrelated features
    """

    MAX_METHODS_PER_CLASS = 15
    MAX_LINES_PER_FUNCTION = 50
    MAX_IMPORTS = 25

    async def analyze(self, content: str, target: str) -> AnalyzerResult:
        """Analyze content for tastefulness."""
        violations: list[Violation] = []
        insights: list[str] = []
        lines = content.split("\n")

        # Check 1: Kitchen-sink classes
        class_violations = self._check_class_complexity(content, target)
        violations.extend(class_violations)

        # Check 2: Function length
        function_violations = self._check_function_length(content, target)
        violations.extend(function_violations)

        # Check 3: Import complexity
        import_count = len(
            [l for l in lines if l.strip().startswith(("import ", "from "))]
        )
        if import_count > self.MAX_IMPORTS:
            violations.append(
                Violation(
                    principle=Principle.TASTEFUL,
                    severity=Severity.WARNING,
                    message=f"High import count ({import_count}) suggests scope creep",
                    location=target,
                    suggestion=f"Consider if all {import_count} imports are necessary",
                )
            )
        elif import_count < 5:
            insights.append(f"Lean imports ({import_count}) - well-focused module")

        # Calculate score (1.0 = perfect, lower = worse)
        error_count = sum(1 for v in violations if v.severity == Severity.ERROR)
        warning_count = sum(1 for v in violations if v.severity == Severity.WARNING)
        score = max(0.0, 1.0 - (error_count * 0.2) - (warning_count * 0.1))

        return AnalyzerResult(score=score, violations=violations, insights=insights)

    def _check_class_complexity(self, content: str, target: str) -> list[Violation]:
        """Check for kitchen-sink classes."""
        violations: list[Violation] = []

        # Find all class definitions
        class_pattern = re.compile(r"^class\s+(\w+)")
        method_pattern = re.compile(r"^\s+(?:async\s+)?def\s+(\w+)")

        current_class = None
        method_count = 0
        class_line = 0

        for line_num, line in enumerate(content.split("\n"), 1):
            class_match = class_pattern.match(line)
            if class_match:
                # Check previous class
                if current_class and method_count > self.MAX_METHODS_PER_CLASS:
                    violations.append(
                        Violation(
                            principle=Principle.TASTEFUL,
                            severity=Severity.WARNING,
                            message=f"Class '{current_class}' has {method_count} methods (kitchen-sink pattern)",
                            location=f"{target}:{class_line}",
                            evidence=f"class {current_class}",
                            suggestion="Consider splitting into focused components",
                        )
                    )
                current_class = class_match.group(1)
                class_line = line_num
                method_count = 0
            elif method_pattern.match(line) and current_class:
                method_count += 1

        # Check last class
        if current_class and method_count > self.MAX_METHODS_PER_CLASS:
            violations.append(
                Violation(
                    principle=Principle.TASTEFUL,
                    severity=Severity.WARNING,
                    message=f"Class '{current_class}' has {method_count} methods (kitchen-sink pattern)",
                    location=f"{target}:{class_line}",
                    evidence=f"class {current_class}",
                    suggestion="Consider splitting into focused components",
                )
            )

        return violations

    def _check_function_length(self, content: str, target: str) -> list[Violation]:
        """Check for overly long functions."""
        violations: list[Violation] = []

        func_pattern = re.compile(r"^(\s*)(?:async\s+)?def\s+(\w+)")
        lines = content.split("\n")

        func_name = None
        func_indent = 0
        func_start = 0
        func_lines = 0

        for line_num, line in enumerate(lines, 1):
            match = func_pattern.match(line)
            if match:
                # Check previous function
                if func_name and func_lines > self.MAX_LINES_PER_FUNCTION:
                    violations.append(
                        Violation(
                            principle=Principle.TASTEFUL,
                            severity=Severity.WARNING,
                            message=f"Function '{func_name}' is {func_lines} lines (max: {self.MAX_LINES_PER_FUNCTION})",
                            location=f"{target}:{func_start}",
                            suggestion="Consider extracting helper functions",
                        )
                    )
                func_name = match.group(2)
                func_indent = len(match.group(1))
                func_start = line_num
                func_lines = 0
            elif func_name:
                # Count lines in current function
                if line.strip() and not line.strip().startswith("#"):
                    current_indent = len(line) - len(line.lstrip())
                    if current_indent > func_indent or line.strip():
                        func_lines += 1

        # Check last function
        if func_name and func_lines > self.MAX_LINES_PER_FUNCTION:
            violations.append(
                Violation(
                    principle=Principle.TASTEFUL,
                    severity=Severity.WARNING,
                    message=f"Function '{func_name}' is {func_lines} lines (max: {self.MAX_LINES_PER_FUNCTION})",
                    location=f"{target}:{func_start}",
                    suggestion="Consider extracting helper functions",
                )
            )

        return violations


class ComposabilityAnalyzer:
    """
    Analyzer for COMPOSABLE principle (110% Domain 2).

    Checks for:
    - Hidden state (global variables, class-level mutables)
    - Singleton patterns
    - Impure functions with side effects
    - Non-injectable dependencies
    """

    async def analyze(self, content: str, target: str) -> AnalyzerResult:
        """Analyze content for composability."""
        violations: list[Violation] = []
        insights: list[str] = []
        lines = content.split("\n")

        # Check 1: Global mutable state
        for line_num, line in enumerate(lines, 1):
            # Mutable default arguments
            if re.search(r"def\s+\w+\([^)]*=\s*(\[\]|\{\}|\set\(\))", line):
                violations.append(
                    Violation(
                        principle=Principle.COMPOSABLE,
                        severity=Severity.ERROR,
                        message="Mutable default argument (hidden shared state)",
                        location=f"{target}:{line_num}",
                        evidence=line.strip()[:80],
                        suggestion="Use None as default and initialize inside function",
                    )
                )

            # Class-level mutable state
            if re.match(r"\s+\w+\s*:\s*(list|dict|set)\s*=", line):
                violations.append(
                    Violation(
                        principle=Principle.COMPOSABLE,
                        severity=Severity.WARNING,
                        message="Class-level mutable annotation (potential shared state)",
                        location=f"{target}:{line_num}",
                        evidence=line.strip()[:80],
                        suggestion="Use field(default_factory=...) for mutable defaults",
                    )
                )

        # Check 2: Module-level singletons
        singleton_patterns = [
            (r"^\w+_instance\s*:", "Module-level singleton instance"),
            (r"^_\w+\s*=\s*None\s*#.*singleton", "Commented singleton"),
            (
                r"@functools\.cache|@lru_cache",
                "Unbounded cache (implicit global state)",
            ),
        ]

        for pattern, message in singleton_patterns:
            for line_num, line in enumerate(lines, 1):
                if re.search(pattern, line, re.IGNORECASE):
                    violations.append(
                        Violation(
                            principle=Principle.COMPOSABLE,
                            severity=Severity.WARNING,
                            message=message,
                            location=f"{target}:{line_num}",
                            evidence=line.strip()[:80],
                            suggestion="Consider dependency injection or context managers",
                        )
                    )

        # Positive: Dependency injection indicators
        if re.search(r"def\s+__init__\s*\([^)]+:\s*\w+", content):
            insights.append("Uses constructor injection (composable pattern)")

        # Calculate score
        error_count = sum(1 for v in violations if v.severity == Severity.ERROR)
        warning_count = sum(1 for v in violations if v.severity == Severity.WARNING)
        score = max(0.0, 1.0 - (error_count * 0.25) - (warning_count * 0.1))

        return AnalyzerResult(score=score, violations=violations, insights=insights)


class GratitudeAnalyzer:
    """
    Analyzer for Accursed Share acknowledgment (110% Domain 2).

    Measures how well code acknowledges:
    - External dependencies (credits, licenses)
    - Borrowed patterns (citations)
    - Entropy sources (randomness, side effects)
    - The Gift (appreciation comments)

    Returns a GratitudeScore rather than violations.
    """

    async def analyze(self, content: str, target: str) -> AnalyzerResult:
        """Analyze content for gratitude/acknowledgment."""
        violations: list[Violation] = []
        insights: list[str] = []

        # Positive signals (contribute to gratitude score)
        gratitude_signals = 0
        max_signals = 5

        # Check 1: License/credits comments
        if re.search(
            r"#.*license|#.*credit|#.*thanks|#.*based on", content, re.IGNORECASE
        ):
            gratitude_signals += 1
            insights.append("Credits/license acknowledgment found")

        # Check 2: Docstrings with references
        if re.search(
            r'""".*(?:see|based on|inspired by|adapted from)',
            content,
            re.IGNORECASE | re.DOTALL,
        ):
            gratitude_signals += 1
            insights.append("References in documentation")

        # Check 3: Entropy acknowledgment
        if re.search(r"random|entropy|seed|uuid", content, re.IGNORECASE):
            if re.search(
                r"#.*seed|#.*random|seed\s*=|random_state", content, re.IGNORECASE
            ):
                gratitude_signals += 1
                insights.append("Entropy sources documented")
            else:
                violations.append(
                    Violation(
                        principle=Principle.GENERATIVE,  # Closest principle
                        severity=Severity.INFO,
                        message="Entropy usage without seed documentation",
                        location=target,
                        suggestion="Consider documenting entropy sources for reproducibility",
                    )
                )

        # Check 4: Error handling with context
        if re.search(r"raise\s+\w+Error\([^)]+\)", content):
            gratitude_signals += 1
            insights.append("Contextual error messages (respects human reader)")

        # Check 5: Type hints (gift to future readers)
        type_hint_count = len(re.findall(r"->\s*\w+|:\s*\w+\[", content))
        if type_hint_count > 5:
            gratitude_signals += 1
            insights.append(f"Rich type hints ({type_hint_count}) (gift to readers)")

        # Calculate gratitude score
        score = gratitude_signals / max_signals

        if score < 0.3:
            violations.append(
                Violation(
                    principle=Principle.JOY_INDUCING,
                    severity=Severity.INFO,
                    message="Low gratitude score - code could acknowledge more",
                    location=target,
                    suggestion="Add credits, references, or documentation for borrowed patterns",
                )
            )

        return AnalyzerResult(score=score, violations=violations, insights=insights)


@dataclass
class ValidationHistoryEntry:
    """A historical validation record."""

    target: str
    timestamp: datetime
    violations: list[str]  # Simplified: just principle+message
    passed: bool


class ValidationHistory:
    """
    Tracks validation history for pattern detection (110% Domain 2).

    Identifies:
    - Recurring violations (same principle violated repeatedly)
    - Improvement trends (fewer violations over time)
    - Blind spots (principles never violated = untested?)
    """

    def __init__(self, max_entries: int = 100) -> None:
        """Initialize validation history."""
        self._entries: list[ValidationHistoryEntry] = []
        self._max_entries = max_entries

    def record(self, result: "ValidationResult") -> None:
        """Record a validation result."""
        entry = ValidationHistoryEntry(
            target=result.target,
            timestamp=result.timestamp,
            violations=[
                f"{v.principle.value}:{v.message[:50]}" for v in result.violations
            ],
            passed=result.passed,
        )
        self._entries.append(entry)

        # Prune old entries
        if len(self._entries) > self._max_entries:
            self._entries = self._entries[-self._max_entries :]

    def recurring_violations(self) -> dict[str, int]:
        """Find principles that are repeatedly violated."""
        counts: dict[str, int] = {}
        for entry in self._entries:
            for v in entry.violations:
                principle = v.split(":")[0]
                counts[principle] = counts.get(principle, 0) + 1
        return {k: v for k, v in sorted(counts.items(), key=lambda x: -x[1]) if v > 1}

    def improvement_trend(self) -> float:
        """Calculate improvement trend (-1 to 1, positive = improving)."""
        if len(self._entries) < 2:
            return 0.0

        # Compare first half to second half
        mid = len(self._entries) // 2
        first_half = self._entries[:mid]
        second_half = self._entries[mid:]

        first_avg = sum(len(e.violations) for e in first_half) / len(first_half)
        second_avg = sum(len(e.violations) for e in second_half) / len(second_half)

        if first_avg == 0:
            return 0.0

        improvement = (first_avg - second_avg) / first_avg
        return max(-1.0, min(1.0, improvement))

    def blind_spots(self) -> list[str]:
        """Find principles that have never been violated (potential blind spots)."""
        violated = set()
        for entry in self._entries:
            for v in entry.violations:
                violated.add(v.split(":")[0])

        all_principles = {p.value for p in Principle}
        return list(all_principles - violated)

    def generate_report(self) -> str:
        """Generate a human-readable history report."""
        lines = [
            "[HISTORY] Validation Pattern Report",
            "",
            f"  Total validations: {len(self._entries)}",
            f"  Pass rate: {sum(1 for e in self._entries if e.passed) / len(self._entries):.0%}"
            if self._entries
            else "  No validations yet",
        ]

        recurring = self.recurring_violations()
        if recurring:
            lines.append("")
            lines.append("  Recurring violations:")
            for principle, count in list(recurring.items())[:5]:
                lines.append(f"    {principle}: {count} times")

        trend = self.improvement_trend()
        if abs(trend) > 0.1:
            lines.append("")
            direction = "improving" if trend > 0 else "regressing"
            lines.append(f"  Trend: {direction} ({trend:+.0%})")

        blind = self.blind_spots()
        if blind:
            lines.append("")
            lines.append("  Blind spots (never violated):")
            for principle in blind:
                lines.append(f"    {principle}")

        return "\n".join(lines)


# =============================================================================
# Heuristic Patterns
# =============================================================================


# Patterns that may indicate principle violations
VIOLATION_PATTERNS: list[tuple[str, Principle, Severity, str, str | None]] = [
    # Tasteful
    (
        r"class\s+\w+Manager\b",
        Principle.TASTEFUL,
        Severity.WARNING,
        "Manager classes often indicate unclear responsibility",
        "Consider if this class has a single, clear purpose",
    ),
    (
        r"def\s+do_everything\b",
        Principle.TASTEFUL,
        Severity.ERROR,
        "Function name suggests unclear scope",
        "Break into focused functions",
    ),
    (
        r"#\s*TODO.*later|#\s*FIXME.*eventually",
        Principle.TASTEFUL,
        Severity.INFO,
        "Deferred work may indicate design uncertainty",
        "Consider if this belongs in the backlog instead",
    ),
    # Curated
    (
        r"class\s+\w+(V2|V3|Version\d)\b",
        Principle.CURATED,
        Severity.WARNING,
        "Versioned classes may indicate accumulation rather than evolution",
        "Consider replacing the original instead of adding versions",
    ),
    (
        r"#\s*deprecated|@deprecated",
        Principle.CURATED,
        Severity.INFO,
        "Deprecated code should be removed, not kept",
        "Remove deprecated code or set a removal date",
    ),
    # Ethical
    (
        r"password\s*=\s*['\"]",
        Principle.ETHICAL,
        Severity.CRITICAL,
        "Hardcoded password detected",
        "Use environment variables or secret management",
    ),
    (
        r"api_key\s*=\s*['\"]",
        Principle.ETHICAL,
        Severity.CRITICAL,
        "Hardcoded API key detected",
        "Use environment variables or secret management",
    ),
    (
        r"secret\s*=\s*['\"]",
        Principle.ETHICAL,
        Severity.CRITICAL,
        "Hardcoded secret detected",
        "Use environment variables or secret management",
    ),
    (
        r"trust_remote_code\s*=\s*True",
        Principle.ETHICAL,
        Severity.WARNING,
        "Trusting remote code is a security risk",
        "Consider alternatives or add explicit review",
    ),
    # Composable
    (
        r"global\s+\w+",
        Principle.COMPOSABLE,
        Severity.WARNING,
        "Global state prevents composition",
        "Use dependency injection or context objects",
    ),
    (
        r"class\s+\w*Singleton\b",
        Principle.COMPOSABLE,
        Severity.ERROR,
        "Singleton pattern prevents composition",
        "Use dependency injection instead",
    ),
    (
        r"\.instance\(\s*\)|getInstance\(\)",
        Principle.COMPOSABLE,
        Severity.WARNING,
        "Singleton access pattern detected",
        "Pass dependencies explicitly",
    ),
    # Heterarchical
    (
        r"class\s+\w*Orchestrator\b",
        Principle.HETERARCHICAL,
        Severity.WARNING,
        "Orchestrator suggests fixed hierarchy",
        "Consider heterarchical composition instead",
    ),
    (
        r"class\s+\w*Master\b|class\s+\w*Slave\b",
        Principle.HETERARCHICAL,
        Severity.ERROR,
        "Master/slave terminology indicates fixed hierarchy (and is outdated)",
        "Use leader/follower or heterarchical patterns",
    ),
    # Generative
    (
        r"#\s*AUTO-GENERATED.*DO NOT EDIT",
        Principle.GENERATIVE,
        Severity.INFO,
        "Generated code detected (good!)",
        None,  # This is actually positive
    ),
    (
        r"(def|class)\s+\w+.*#\s*hand-?written",
        Principle.GENERATIVE,
        Severity.INFO,
        "Hand-written code marked - consider if it could be generated",
        "Could this be derived from a spec?",
    ),
]


# =============================================================================
# Semantic Gatekeeper
# =============================================================================


@dataclass
class DeepAnalysisResult:
    """Result from deep analysis with explanations (110% Domain 2)."""

    validation: "ValidationResult"
    tastefulness_score: float
    composability_score: float
    gratitude_score: float
    insights: list[str]
    principle_explanations: dict[str, str]  # principle -> detailed explanation

    def format(self) -> str:
        """Format with explanations."""
        lines = [self.validation.format()]

        lines.append("")
        lines.append("  Scores:")
        lines.append(f"    Tastefulness: {self.tastefulness_score:.0%}")
        lines.append(f"    Composability: {self.composability_score:.0%}")
        lines.append(f"    Gratitude: {self.gratitude_score:.0%}")

        if self.insights:
            lines.append("")
            lines.append("  Insights:")
            for insight in self.insights:
                lines.append(f"    + {insight}")

        if self.principle_explanations:
            lines.append("")
            lines.append("  Principle Details:")
            for principle, explanation in self.principle_explanations.items():
                lines.append(f"    [{principle}]: {explanation}")

        return "\n".join(lines)


class SemanticGatekeeper:
    """
    Semantic Gatekeeper: Validate code against kgents principles.

    The gatekeeper performs:
    1. Heuristic pattern matching (fast, no LLM)
    2. Specialized analyzers (Tastefulness, Composability, Gratitude)
    3. LLM-backed semantic analysis (deeper, requires LLM)
    4. Validation history tracking (pattern detection)

    Example:
        >>> gatekeeper = SemanticGatekeeper()
        >>> result = await gatekeeper.validate_file("src/agent.py")
        >>> if not result.passed:
        ...     print(result.format())
        >>>
        >>> # Deep analysis with explanations (110%)
        >>> deep = await gatekeeper.validate_deep("src/agent.py", explain=True)
        >>> print(deep.format())
    """

    def __init__(
        self,
        llm: Optional["LLMClient"] = None,
        use_llm: bool = True,
        history: Optional[ValidationHistory] = None,
    ) -> None:
        """
        Initialize gatekeeper.

        Args:
            llm: Optional LLM client for semantic analysis
            use_llm: Whether to use LLM for deep analysis
            history: Optional ValidationHistory for pattern tracking
        """
        self._llm = llm
        self._use_llm = use_llm
        self._history = history or ValidationHistory()

        # Specialized analyzers (110%)
        self._tastefulness = TastefullnessAnalyzer()
        self._composability = ComposabilityAnalyzer()
        self._gratitude = GratitudeAnalyzer()

    @property
    def history(self) -> ValidationHistory:
        """Get validation history."""
        return self._history

    # ─────────────────────────────────────────────────────────────────────────
    # Validation
    # ─────────────────────────────────────────────────────────────────────────

    async def validate_file(self, file_path: str) -> ValidationResult:
        """
        Validate a file against principles.

        Args:
            file_path: Path to file to validate

        Returns:
            ValidationResult with any violations found
        """
        path = Path(file_path)

        if not path.exists():
            return ValidationResult(
                target=file_path,
                passed=False,
                violations=[
                    Violation(
                        principle=Principle.TASTEFUL,
                        severity=Severity.ERROR,
                        message=f"File not found: {file_path}",
                    )
                ],
            )

        content = path.read_text()
        return await self.validate_content(content, target=file_path)

    async def validate_content(
        self,
        content: str,
        target: str = "content",
        use_analyzers: bool = True,
    ) -> ValidationResult:
        """
        Validate content against principles.

        Args:
            content: The content to validate
            target: Description of what is being validated
            use_analyzers: Whether to use specialized analyzers (110%)

        Returns:
            ValidationResult with any violations found
        """
        result = ValidationResult(target=target)

        # Phase 1: Heuristic pattern matching
        heuristic_violations = self._check_heuristics(content, target)
        result.violations.extend(heuristic_violations)

        # Phase 2: Specialized analyzers (110%)
        if use_analyzers:
            taste_result = await self._tastefulness.analyze(content, target)
            result.violations.extend(taste_result.violations)

            comp_result = await self._composability.analyze(content, target)
            result.violations.extend(comp_result.violations)

            grat_result = await self._gratitude.analyze(content, target)
            result.violations.extend(grat_result.violations)

        # Phase 3: LLM semantic analysis (if available)
        if self._llm and self._use_llm:
            llm_violations = await self._check_semantic(content, target)
            result.violations.extend(llm_violations)

        # Determine pass/fail
        result.passed = not any(
            v.severity in [Severity.ERROR, Severity.CRITICAL] for v in result.violations
        )

        # Generate summary
        if result.violations:
            result.summary = (
                f"{len(result.violations)} potential issue(s) found. "
                f"Critical: {result.by_severity.get('critical', 0)}, "
                f"Error: {result.by_severity.get('error', 0)}, "
                f"Warning: {result.by_severity.get('warning', 0)}"
            )
        else:
            result.summary = "No principle violations detected."

        # Record in history
        self._history.record(result)

        return result

    async def validate_deep(
        self,
        file_path: str,
        explain: bool = True,
    ) -> DeepAnalysisResult:
        """
        Deep validation with explanations (110% Domain 2).

        Runs all analyzers and provides detailed insights and
        principle-by-principle explanations.

        Args:
            file_path: Path to file to validate
            explain: Whether to generate principle explanations

        Returns:
            DeepAnalysisResult with scores and explanations
        """
        path = Path(file_path)

        if not path.exists():
            return DeepAnalysisResult(
                validation=ValidationResult(
                    target=file_path,
                    passed=False,
                    violations=[
                        Violation(
                            principle=Principle.TASTEFUL,
                            severity=Severity.ERROR,
                            message=f"File not found: {file_path}",
                        )
                    ],
                ),
                tastefulness_score=0.0,
                composability_score=0.0,
                gratitude_score=0.0,
                insights=[],
                principle_explanations={},
            )

        content = path.read_text()

        # Run base validation (without analyzers - we'll run them separately)
        result = ValidationResult(target=file_path)
        heuristic_violations = self._check_heuristics(content, file_path)
        result.violations.extend(heuristic_violations)

        # Run specialized analyzers
        taste_result = await self._tastefulness.analyze(content, file_path)
        result.violations.extend(taste_result.violations)

        comp_result = await self._composability.analyze(content, file_path)
        result.violations.extend(comp_result.violations)

        grat_result = await self._gratitude.analyze(content, file_path)
        result.violations.extend(grat_result.violations)

        # LLM analysis if available
        if self._llm and self._use_llm:
            llm_violations = await self._check_semantic(content, file_path)
            result.violations.extend(llm_violations)

        # Determine pass/fail
        result.passed = not any(
            v.severity in [Severity.ERROR, Severity.CRITICAL] for v in result.violations
        )

        # Collect insights
        all_insights = (
            taste_result.insights + comp_result.insights + grat_result.insights
        )

        # Generate principle explanations if requested
        explanations: dict[str, str] = {}
        if explain:
            explanations = self._generate_explanations(result.violations)

        # Generate summary
        if result.violations:
            result.summary = (
                f"{len(result.violations)} potential issue(s) found. "
                f"Tastefulness: {taste_result.score:.0%}, "
                f"Composability: {comp_result.score:.0%}, "
                f"Gratitude: {grat_result.score:.0%}"
            )
        else:
            result.summary = "No principle violations detected."

        # Record in history
        self._history.record(result)

        return DeepAnalysisResult(
            validation=result,
            tastefulness_score=taste_result.score,
            composability_score=comp_result.score,
            gratitude_score=grat_result.score,
            insights=all_insights,
            principle_explanations=explanations,
        )

    def _generate_explanations(self, violations: list[Violation]) -> dict[str, str]:
        """Generate detailed explanations for violated principles."""
        explanations: dict[str, str] = {}

        principle_details = {
            Principle.TASTEFUL: (
                "TASTEFUL means clear, justified purpose. Every class and function "
                "should have a single responsibility. Kitchen-sink patterns (classes "
                "with too many methods) and function bloat suggest unclear scope."
            ),
            Principle.CURATED: (
                "CURATED means quality over quantity. Avoid accumulating versions, "
                "deprecated code, or features 'just in case'. If it's not actively "
                "used and valued, remove it."
            ),
            Principle.ETHICAL: (
                "ETHICAL means augmenting, not replacing judgment. Never hardcode "
                "secrets or credentials. Be transparent about data collection. "
                "Trust boundaries should be explicit."
            ),
            Principle.JOY_INDUCING: (
                "JOY-INDUCING means personality matters. Code should be pleasant to "
                "read and maintain. Good error messages, thoughtful documentation, "
                "and acknowledgment of sources all contribute."
            ),
            Principle.COMPOSABLE: (
                "COMPOSABLE means agents are morphisms. Avoid global state, "
                "singletons, and hidden dependencies. Use dependency injection. "
                "Pure functions compose better than impure ones."
            ),
            Principle.HETERARCHICAL: (
                "HETERARCHICAL means flux over hierarchy. Avoid permanent "
                "orchestrator/worker patterns. Roles should be dynamic, not fixed. "
                "Peer-to-peer over master-slave."
            ),
            Principle.GENERATIVE: (
                "GENERATIVE means spec compresses implementation. Prefer generating "
                "code from specifications over hand-writing everything. Acknowledge "
                "entropy sources. Document what's derived vs. authored."
            ),
        }

        # Find which principles were violated
        violated_principles = {v.principle for v in violations}

        for principle in violated_principles:
            explanation = principle_details.get(principle, "")
            violation_count = sum(1 for v in violations if v.principle == principle)
            explanations[principle.value] = (
                f"{explanation} (Found {violation_count} issue(s))"
            )

        return explanations

    # ─────────────────────────────────────────────────────────────────────────
    # Heuristic Checks
    # ─────────────────────────────────────────────────────────────────────────

    def _check_heuristics(self, content: str, target: str) -> list[Violation]:
        """Check content against heuristic patterns."""
        violations: list[Violation] = []
        lines = content.split("\n")

        for pattern, principle, severity, message, suggestion in VIOLATION_PATTERNS:
            regex = re.compile(pattern, re.IGNORECASE)

            for line_num, line in enumerate(lines, 1):
                match = regex.search(line)
                if match:
                    violations.append(
                        Violation(
                            principle=principle,
                            severity=severity,
                            message=message,
                            location=f"{target}:{line_num}",
                            evidence=line.strip()[:100],
                            suggestion=suggestion,
                        )
                    )

        return violations

    # ─────────────────────────────────────────────────────────────────────────
    # Semantic Checks (LLM)
    # ─────────────────────────────────────────────────────────────────────────

    async def _check_semantic(self, content: str, target: str) -> list[Violation]:
        """Check content using LLM semantic analysis."""
        if not self._llm:
            return []

        # Truncate very long content
        if len(content) > 8000:
            content = content[:8000] + "\n... (truncated)"

        system_prompt = """You are a code reviewer checking against the kgents design principles:

1. TASTEFUL: Clear, justified purpose. Anti-patterns: kitchen-sink, feature creep
2. CURATED: Quality over quantity. Anti-patterns: accumulation, legacy kept for nostalgia
3. ETHICAL: Augment, don't replace judgment. Anti-patterns: hidden data collection, manipulation
4. JOY-INDUCING: Personality matters. Anti-patterns: robotic responses, needless formality
5. COMPOSABLE: Agents are morphisms. Anti-patterns: global state, singletons, monoliths
6. HETERARCHICAL: Flux, not hierarchy. Anti-patterns: permanent orchestrator/worker
7. GENERATIVE: Spec compresses implementation. Anti-patterns: spec rot, hand-crafted everything

For each violation found, output in this format:
VIOLATION: [PRINCIPLE] [SEVERITY] - [MESSAGE]
EVIDENCE: [relevant code snippet]
SUGGESTION: [how to fix]

Valid severities: info, warning, error, critical
Only report clear violations, not style preferences."""

        user_prompt = f"""Review this code for principle violations:

```
{content}
```

List any violations of the kgents principles. If none found, say "No violations found."
"""

        try:
            response = await self._llm.generate(
                system=system_prompt,
                user=user_prompt,
                temperature=0.2,
                max_tokens=1000,
            )

            return self._parse_llm_response(response.text, target)

        except Exception:
            # LLM failure is non-fatal
            return []

    def _parse_llm_response(self, response: str, target: str) -> list[Violation]:
        """Parse LLM response into violations."""
        violations: list[Violation] = []

        if "no violations found" in response.lower():
            return violations

        # Parse VIOLATION: lines
        violation_pattern = re.compile(
            r"VIOLATION:\s*\[?(\w+(?:-\w+)?)\]?\s*\[?(\w+)\]?\s*-?\s*(.+?)(?=EVIDENCE:|SUGGESTION:|VIOLATION:|$)",
            re.IGNORECASE | re.DOTALL,
        )

        evidence_pattern = re.compile(
            r"EVIDENCE:\s*(.+?)(?=SUGGESTION:|VIOLATION:|$)",
            re.IGNORECASE | re.DOTALL,
        )

        suggestion_pattern = re.compile(
            r"SUGGESTION:\s*(.+?)(?=VIOLATION:|$)",
            re.IGNORECASE | re.DOTALL,
        )

        # Find all violations
        for match in violation_pattern.finditer(response):
            principle_str = match.group(1).lower().replace("_", "-")
            severity_str = match.group(2).lower()
            message = match.group(3).strip()

            # Map to enum
            try:
                principle = Principle(principle_str)
            except ValueError:
                # Try to match partial
                principle = Principle.TASTEFUL  # Default
                for p in Principle:
                    if principle_str in p.value:
                        principle = p
                        break

            try:
                severity = Severity(severity_str)
            except ValueError:
                severity = Severity.WARNING

            # Look for evidence and suggestion after this violation
            remaining = response[match.end() :]
            evidence_match = evidence_pattern.search(remaining)
            suggestion_match = suggestion_pattern.search(remaining)

            violations.append(
                Violation(
                    principle=principle,
                    severity=severity,
                    message=message,
                    location=f"{target} (LLM analysis)",
                    evidence=evidence_match.group(1).strip()[:200]
                    if evidence_match
                    else None,
                    suggestion=suggestion_match.group(1).strip()
                    if suggestion_match
                    else None,
                )
            )

        return violations


# =============================================================================
# Convenience Functions
# =============================================================================


async def validate_file(
    file_path: str,
    use_llm: bool = False,
    llm: Optional["LLMClient"] = None,
) -> ValidationResult:
    """
    Validate a file against principles.

    Args:
        file_path: Path to file to validate
        use_llm: Whether to use LLM for deeper analysis
        llm: Optional LLM client

    Returns:
        ValidationResult with any violations found
    """
    gatekeeper = SemanticGatekeeper(llm=llm, use_llm=use_llm)
    return await gatekeeper.validate_file(file_path)


async def validate_content(
    content: str,
    target: str = "content",
    use_llm: bool = False,
    llm: Optional["LLMClient"] = None,
) -> ValidationResult:
    """
    Validate content against principles.

    Args:
        content: The content to validate
        target: Description of what is being validated
        use_llm: Whether to use LLM for deeper analysis
        llm: Optional LLM client

    Returns:
        ValidationResult with any violations found
    """
    gatekeeper = SemanticGatekeeper(llm=llm, use_llm=use_llm)
    return await gatekeeper.validate_content(content, target)


# =============================================================================
# Exports
# =============================================================================

__all__ = [
    # Types
    "Principle",
    "Severity",
    "Violation",
    "ValidationResult",
    # Analyzers (110%)
    "AnalyzerResult",
    "TastefullnessAnalyzer",
    "ComposabilityAnalyzer",
    "GratitudeAnalyzer",
    "ValidationHistory",
    "ValidationHistoryEntry",
    "DeepAnalysisResult",
    # The Gatekeeper
    "SemanticGatekeeper",
    # Convenience
    "validate_file",
    "validate_content",
]
