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


class SemanticGatekeeper:
    """
    Semantic Gatekeeper: Validate code against kgents principles.

    The gatekeeper performs:
    1. Heuristic pattern matching (fast, no LLM)
    2. LLM-backed semantic analysis (deeper, requires LLM)

    Example:
        >>> gatekeeper = SemanticGatekeeper()
        >>> result = await gatekeeper.validate_file("src/agent.py")
        >>> if not result.passed:
        ...     print(result.format())
    """

    def __init__(
        self,
        llm: Optional["LLMClient"] = None,
        use_llm: bool = True,
    ) -> None:
        """
        Initialize gatekeeper.

        Args:
            llm: Optional LLM client for semantic analysis
            use_llm: Whether to use LLM for deep analysis
        """
        self._llm = llm
        self._use_llm = use_llm

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
    ) -> ValidationResult:
        """
        Validate content against principles.

        Args:
            content: The content to validate
            target: Description of what is being validated

        Returns:
            ValidationResult with any violations found
        """
        result = ValidationResult(target=target)

        # Phase 1: Heuristic pattern matching
        heuristic_violations = self._check_heuristics(content, target)
        result.violations.extend(heuristic_violations)

        # Phase 2: LLM semantic analysis (if available)
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

        return result

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
    # The Gatekeeper
    "SemanticGatekeeper",
    # Convenience
    "validate_file",
    "validate_content",
]
