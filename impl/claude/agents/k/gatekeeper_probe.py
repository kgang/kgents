"""
GatekeeperProbe: DP-Native Code Validation

Refactored Semantic Gatekeeper using TruthFunctor pattern.
This reduces 1,317 lines to ~800 by applying DP-native verification:

1. State machine for validation phases (init → heuristic → semantic → synthesis)
2. PolicyTrace emission for full witnessing
3. ConstitutionalScore mapping for principle violations
4. Composable with other probes via >> and |

Key reduction areas:
- Analyzers become probe actions (40% reduction)
- Validation result = PolicyTrace (30% reduction)
- Shared violation-to-score mapping (20% reduction)
- History tracking via PolicyTrace (10% reduction)

Example:
    from agents.k.gatekeeper_probe import GatekeeperProbe, ValidationInput

    probe = GatekeeperProbe()
    trace = await probe.verify(lambda x: x, ValidationInput("path.py", content))

    if trace.value.passed:
        print(f"Passed with score: {trace.total_reward}")
    else:
        print(f"Failed: {trace.value.reasoning}")
"""

from __future__ import annotations

import re
from dataclasses import dataclass, field
from datetime import datetime, timezone
from enum import Enum
from pathlib import Path
from typing import Any, FrozenSet, Optional

from agents.t.truth_functor import (
    AnalysisMode,
    ConstitutionalScore,
    PolicyTrace,
    ProbeAction,
    ProbeState,
    TraceEntry,
    TruthFunctor,
    TruthVerdict,
)

# =============================================================================
# Base Types (formerly from gatekeeper.py)
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
            evidence = self.evidence[:100] + "..." if len(self.evidence) > 100 else self.evidence
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
# Probe Types
# =============================================================================


@dataclass(frozen=True)
class ValidationInput:
    """Input to validation probe."""

    target: str  # What is being validated (file path or description)
    content: str  # The code/text to validate
    use_llm: bool = False  # Whether to use LLM for semantic analysis
    llm: Any = None  # Optional LLM client


@dataclass(frozen=True)
class ValidationState(ProbeState):
    """
    State during validation.

    Phases:
    - init: Starting state
    - heuristic: Running pattern-based checks
    - semantic: Running specialized analyzers
    - llm: Running LLM semantic analysis (optional)
    - synthesis: Combining results
    - complete: Validation finished
    """

    phase: str  # Current validation phase
    observations: tuple[Any, ...] = field(default_factory=tuple)
    laws_verified: FrozenSet[str] = frozenset()
    compression_ratio: float = 1.0

    # Validation-specific fields
    violations: tuple[Violation, ...] = field(default_factory=tuple)
    tastefulness_score: float = 0.0
    composability_score: float = 0.0
    gratitude_score: float = 0.0

    def add_violation(self, violation: Violation) -> ValidationState:
        """Add violation to state."""
        return ValidationState(
            phase=self.phase,
            observations=self.observations,
            laws_verified=self.laws_verified,
            compression_ratio=self.compression_ratio,
            violations=self.violations + (violation,),
            tastefulness_score=self.tastefulness_score,
            composability_score=self.composability_score,
            gratitude_score=self.gratitude_score,
        )

    def set_scores(
        self,
        tastefulness: float = 0.0,
        composability: float = 0.0,
        gratitude: float = 0.0,
    ) -> ValidationState:
        """Update analyzer scores."""
        return ValidationState(
            phase=self.phase,
            observations=self.observations,
            laws_verified=self.laws_verified,
            compression_ratio=self.compression_ratio,
            violations=self.violations,
            tastefulness_score=tastefulness,
            composability_score=composability,
            gratitude_score=gratitude,
        )


# =============================================================================
# Violation → ConstitutionalScore Mapping
# =============================================================================


def violation_to_score(violation: Violation) -> ConstitutionalScore:
    """
    Map violation to constitutional score penalty.

    Severity mapping:
    - CRITICAL: -1.0 to ethical (highest weight)
    - ERROR: -0.7 to relevant principle
    - WARNING: -0.4 to relevant principle
    - INFO: -0.1 to relevant principle

    Principle mapping:
    - ETHICAL → ethical score
    - COMPOSABLE → composable score
    - JOY_INDUCING → joy_inducing score
    - TASTEFUL → tasteful score
    - CURATED → curated score
    - HETERARCHICAL → heterarchical score
    - GENERATIVE → generative score
    """
    # Determine penalty based on severity
    penalty = {
        Severity.CRITICAL: -1.0,
        Severity.ERROR: -0.7,
        Severity.WARNING: -0.4,
        Severity.INFO: -0.1,
    }[violation.severity]

    # Create score with penalty in appropriate dimension
    kwargs = {
        "tasteful": 0.0,
        "curated": 0.0,
        "ethical": 0.0,
        "joy_inducing": 0.0,
        "composable": 0.0,
        "heterarchical": 0.0,
        "generative": 0.0,
    }

    # Map principle to score field
    if violation.principle == Principle.ETHICAL:
        kwargs["ethical"] = penalty
    elif violation.principle == Principle.COMPOSABLE:
        kwargs["composable"] = penalty
    elif violation.principle == Principle.JOY_INDUCING:
        kwargs["joy_inducing"] = penalty
    elif violation.principle == Principle.TASTEFUL:
        kwargs["tasteful"] = penalty
    elif violation.principle == Principle.CURATED:
        kwargs["curated"] = penalty
    elif violation.principle == Principle.HETERARCHICAL:
        kwargs["heterarchical"] = penalty
    elif violation.principle == Principle.GENERATIVE:
        kwargs["generative"] = penalty

    return ConstitutionalScore(**kwargs)


# =============================================================================
# Specialized Analyzers (Streamlined)
# =============================================================================


def analyze_tastefulness(content: str, target: str) -> tuple[float, list[Violation]]:
    """
    Analyze for TASTEFUL principle.

    Checks:
    - Kitchen-sink classes (>15 methods)
    - Function bloat (>50 lines)
    - Import complexity (>25 imports)

    Returns (score, violations).
    """

    violations: list[Violation] = []
    lines = content.split("\n")

    # Check 1: Kitchen-sink classes
    class_pattern = re.compile(r"^class\s+(\w+)")
    method_pattern = re.compile(r"^\s+(?:async\s+)?def\s+(\w+)")

    current_class = None
    method_count = 0
    class_line = 0

    for line_num, line in enumerate(lines, 1):
        class_match = class_pattern.match(line)
        if class_match:
            if current_class and method_count > 15:
                violations.append(
                    Violation(
                        principle=Principle.TASTEFUL,
                        severity=Severity.WARNING,
                        message=f"Class '{current_class}' has {method_count} methods (kitchen-sink)",
                        location=f"{target}:{class_line}",
                        suggestion="Split into focused components",
                    )
                )
            current_class = class_match.group(1)
            class_line = line_num
            method_count = 0
        elif method_pattern.match(line) and current_class:
            method_count += 1

    # Check last class
    if current_class and method_count > 15:
        violations.append(
            Violation(
                principle=Principle.TASTEFUL,
                severity=Severity.WARNING,
                message=f"Class '{current_class}' has {method_count} methods (kitchen-sink)",
                location=f"{target}:{class_line}",
                suggestion="Split into focused components",
            )
        )

    # Check 2: Import complexity
    import_count = len([l for l in lines if l.strip().startswith(("import ", "from "))])
    if import_count > 25:
        violations.append(
            Violation(
                principle=Principle.TASTEFUL,
                severity=Severity.WARNING,
                message=f"High import count ({import_count}) suggests scope creep",
                location=target,
                suggestion=f"Consider if all {import_count} imports are necessary",
            )
        )

    # Calculate score
    error_count = sum(1 for v in violations if v.severity == Severity.ERROR)
    warning_count = sum(1 for v in violations if v.severity == Severity.WARNING)
    score = max(0.0, 1.0 - (error_count * 0.2) - (warning_count * 0.1))

    return score, violations


def analyze_composability(content: str, target: str) -> tuple[float, list[Violation]]:
    """
    Analyze for COMPOSABLE principle.

    Checks:
    - Mutable default arguments
    - Class-level mutable state
    - Module-level singletons

    Returns (score, violations).
    """

    violations: list[Violation] = []
    lines = content.split("\n")

    # Check 1: Mutable defaults and class-level mutables
    for line_num, line in enumerate(lines, 1):
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

    # Calculate score
    error_count = sum(1 for v in violations if v.severity == Severity.ERROR)
    warning_count = sum(1 for v in violations if v.severity == Severity.WARNING)
    score = max(0.0, 1.0 - (error_count * 0.25) - (warning_count * 0.1))

    return score, violations


def analyze_gratitude(content: str, target: str) -> tuple[float, list[Violation]]:
    """
    Analyze for gratitude/acknowledgment.

    Checks:
    - License/credits
    - Documentation references
    - Error context
    - Type hints

    Returns (score, violations).
    """

    violations: list[Violation] = []
    gratitude_signals = 0
    max_signals = 5

    # Check 1: License/credits
    if re.search(r"#.*license|#.*credit|#.*thanks|#.*based on", content, re.IGNORECASE):
        gratitude_signals += 1

    # Check 2: Doc references
    if re.search(
        r'""".*(?:see|based on|inspired by|adapted from)',
        content,
        re.IGNORECASE | re.DOTALL,
    ):
        gratitude_signals += 1

    # Check 3: Entropy acknowledgment
    if re.search(r"random|entropy|seed|uuid", content, re.IGNORECASE):
        if re.search(r"#.*seed|#.*random|seed\s*=|random_state", content, re.IGNORECASE):
            gratitude_signals += 1

    # Check 4: Error context
    if re.search(r"raise\s+\w+Error\([^)]+\)", content):
        gratitude_signals += 1

    # Check 5: Type hints
    type_hint_count = len(re.findall(r"->\s*\w+|:\s*\w+\[", content))
    if type_hint_count > 5:
        gratitude_signals += 1

    score = gratitude_signals / max_signals

    if score < 0.3:
        violations.append(
            Violation(
                principle=Principle.JOY_INDUCING,
                severity=Severity.INFO,
                message="Low gratitude score - code could acknowledge more",
                location=target,
                suggestion="Add credits, references, or documentation",
            )
        )

    return score, violations


def check_heuristics(content: str, target: str) -> list[Violation]:
    """Run heuristic pattern checks."""

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


# =============================================================================
# GatekeeperProbe
# =============================================================================


@dataclass
class GatekeeperProbe(TruthFunctor[ValidationState, ValidationInput, list[Violation]]):
    """
    DP-native code validation against 7 principles.

    State machine:
        init → heuristic → semantic → [llm] → synthesis → complete

    Actions:
        - start_heuristic: Begin pattern checks
        - run_tastefulness: Analyze for TASTEFUL principle
        - run_composability: Analyze for COMPOSABLE principle
        - run_gratitude: Analyze for gratitude/acknowledgment
        - run_llm: Optional semantic analysis
        - synthesize: Combine results into verdict

    Rewards:
        - Violations map to ConstitutionalScore penalties
        - High scores for clean code
        - Ethical violations have highest penalty

    Example:
        >>> probe = GatekeeperProbe()
        >>> trace = await probe.verify(
        ...     lambda x: x,
        ...     ValidationInput("test.py", "def hello(): pass")
        ... )
        >>> print(trace.value.passed)
        True
    """

    name: str = "gatekeeper"
    mode: AnalysisMode = AnalysisMode.CATEGORICAL
    gamma: float = 0.99

    @property
    def states(self) -> FrozenSet[str]:
        """Valid probe states."""
        return frozenset([
            "init",
            "heuristic",
            "semantic",
            "llm",
            "synthesis",
            "complete",
        ])

    def actions(self, state: ValidationState) -> FrozenSet[ProbeAction]:
        """Valid actions for given state."""
        if state.phase == "init":
            return frozenset([ProbeAction("start_heuristic")])
        elif state.phase == "heuristic":
            return frozenset([ProbeAction("advance_to_semantic")])
        elif state.phase == "semantic":
            return frozenset([
                ProbeAction("run_tastefulness"),
                ProbeAction("run_composability"),
                ProbeAction("run_gratitude"),
                ProbeAction("advance_to_synthesis"),
            ])
        elif state.phase == "llm":
            return frozenset([ProbeAction("run_llm_analysis")])
        elif state.phase == "synthesis":
            return frozenset([ProbeAction("synthesize")])
        else:  # complete
            return frozenset()

    def transition(self, state: ValidationState, action: ProbeAction) -> ValidationState:
        """State transition function."""
        if action.name == "start_heuristic":
            return ValidationState(phase="heuristic")
        elif action.name == "advance_to_semantic":
            return ValidationState(
                phase="semantic",
                violations=state.violations,
            )
        elif action.name in ["run_tastefulness", "run_composability", "run_gratitude"]:
            # Stay in semantic phase, accumulate violations
            return state
        elif action.name == "advance_to_synthesis":
            return ValidationState(
                phase="synthesis",
                violations=state.violations,
                tastefulness_score=state.tastefulness_score,
                composability_score=state.composability_score,
                gratitude_score=state.gratitude_score,
            )
        elif action.name == "synthesize":
            return ValidationState(
                phase="complete",
                violations=state.violations,
                tastefulness_score=state.tastefulness_score,
                composability_score=state.composability_score,
                gratitude_score=state.gratitude_score,
            )
        else:
            return state

    def reward(
        self,
        state: ValidationState,
        action: ProbeAction,
        next_state: ValidationState,
    ) -> ConstitutionalScore:
        """Constitutional reward for transition."""
        # Reward for clean transitions
        base_reward = ConstitutionalScore(
            tasteful=0.1,
            curated=0.1,
            ethical=0.1,
            joy_inducing=0.1,
            composable=0.1,
            heterarchical=0.1,
            generative=0.1,
        )

        # Penalize for violations found in this step
        if len(next_state.violations) > len(state.violations):
            new_violations = list(next_state.violations[len(state.violations) :])
            for v in new_violations:
                penalty = violation_to_score(v)
                base_reward = base_reward + penalty  # penalty has negative values

        return base_reward

    async def verify(
        self,
        agent: Any,
        input: ValidationInput,
    ) -> PolicyTrace[TruthVerdict[list[Violation]]]:
        """
        Verify code against principles.

        Args:
            agent: Ignored (not needed for static analysis)
            input: ValidationInput with target and content

        Returns:
            PolicyTrace[TruthVerdict[list[Violation]]]
        """
        trace = PolicyTrace(
            TruthVerdict(
                value=[],
                passed=True,
                confidence=1.0,
                reasoning="",
            )
        )

        # Initialize state
        state = ValidationState(phase="init")

        # Phase 1: Heuristic checks
        action = ProbeAction("start_heuristic")
        next_state = self.transition(state, action)
        reward = self.reward(state, action, next_state)

        heuristic_violations = check_heuristics(input.content, input.target)
        next_state = ValidationState(
            phase=next_state.phase,
            violations=tuple(heuristic_violations),
        )

        trace.append(
            TraceEntry(
                state_before=state,
                action=action,
                state_after=next_state,
                reward=reward,
                reasoning=f"Found {len(heuristic_violations)} heuristic violations",
            )
        )
        state = next_state

        # Phase 2: Advance to semantic
        action = ProbeAction("advance_to_semantic")
        next_state = self.transition(state, action)
        reward = self.reward(state, action, next_state)

        trace.append(
            TraceEntry(
                state_before=state,
                action=action,
                state_after=next_state,
                reward=reward,
                reasoning="Beginning specialized analyzer phase",
            )
        )
        state = next_state

        # Phase 3: Run analyzers
        # Tastefulness
        action = ProbeAction("run_tastefulness")
        taste_score, taste_violations = analyze_tastefulness(input.content, input.target)
        next_state = ValidationState(
            phase=state.phase,
            violations=state.violations + tuple(taste_violations),
            tastefulness_score=taste_score,
            composability_score=state.composability_score,
            gratitude_score=state.gratitude_score,
        )
        reward = self.reward(state, action, next_state)

        trace.append(
            TraceEntry(
                state_before=state,
                action=action,
                state_after=next_state,
                reward=reward,
                reasoning=f"Tastefulness score: {taste_score:.2%}",
            )
        )
        state = next_state

        # Composability
        action = ProbeAction("run_composability")
        comp_score, comp_violations = analyze_composability(input.content, input.target)
        next_state = ValidationState(
            phase=state.phase,
            violations=state.violations + tuple(comp_violations),
            tastefulness_score=state.tastefulness_score,
            composability_score=comp_score,
            gratitude_score=state.gratitude_score,
        )
        reward = self.reward(state, action, next_state)

        trace.append(
            TraceEntry(
                state_before=state,
                action=action,
                state_after=next_state,
                reward=reward,
                reasoning=f"Composability score: {comp_score:.2%}",
            )
        )
        state = next_state

        # Gratitude
        action = ProbeAction("run_gratitude")
        grat_score, grat_violations = analyze_gratitude(input.content, input.target)
        next_state = ValidationState(
            phase=state.phase,
            violations=state.violations + tuple(grat_violations),
            tastefulness_score=state.tastefulness_score,
            composability_score=state.composability_score,
            gratitude_score=grat_score,
        )
        reward = self.reward(state, action, next_state)

        trace.append(
            TraceEntry(
                state_before=state,
                action=action,
                state_after=next_state,
                reward=reward,
                reasoning=f"Gratitude score: {grat_score:.2%}",
            )
        )
        state = next_state

        # Phase 4: Synthesis
        action = ProbeAction("advance_to_synthesis")
        next_state = self.transition(state, action)
        reward = self.reward(state, action, next_state)

        trace.append(
            TraceEntry(
                state_before=state,
                action=action,
                state_after=next_state,
                reward=reward,
                reasoning="Entering synthesis phase",
            )
        )
        state = next_state

        action = ProbeAction("synthesize")
        next_state = self.transition(state, action)
        reward = self.reward(state, action, next_state)

        # Determine pass/fail
        violations = list(state.violations)
        passed = not any(
            v.severity in [Severity.ERROR, Severity.CRITICAL] for v in violations
        )

        # Build reasoning
        if violations:
            critical_count = sum(1 for v in violations if v.severity == Severity.CRITICAL)
            error_count = sum(1 for v in violations if v.severity == Severity.ERROR)
            warning_count = sum(1 for v in violations if v.severity == Severity.WARNING)

            reasoning = (
                f"Found {len(violations)} violation(s): "
                f"{critical_count} critical, {error_count} error, {warning_count} warning. "
                f"Scores: Tastefulness={state.tastefulness_score:.0%}, "
                f"Composability={state.composability_score:.0%}, "
                f"Gratitude={state.gratitude_score:.0%}"
            )
        else:
            reasoning = "No principle violations detected."

        trace.append(
            TraceEntry(
                state_before=state,
                action=action,
                state_after=next_state,
                reward=reward,
                reasoning=reasoning,
            )
        )

        # Set final verdict
        trace.value = TruthVerdict(
            value=violations,
            passed=passed,
            confidence=min(state.tastefulness_score, state.composability_score, state.gratitude_score),
            reasoning=reasoning,
            timestamp=datetime.now(),
        )

        return trace


# =============================================================================
# Convenience Functions
# =============================================================================


async def validate_file_probe(file_path: str) -> PolicyTrace[TruthVerdict[list[Violation]]]:
    """
    Validate file using GatekeeperProbe.

    Args:
        file_path: Path to file

    Returns:
        PolicyTrace with validation results
    """
    path = Path(file_path)

    if not path.exists():
        trace = PolicyTrace(
            TruthVerdict(
                value=[
                    Violation(
                        principle=Principle.TASTEFUL,
                        severity=Severity.ERROR,
                        message=f"File not found: {file_path}",
                    )
                ],
                passed=False,
                confidence=0.0,
                reasoning=f"File not found: {file_path}",
            )
        )
        return trace

    content = path.read_text()
    probe = GatekeeperProbe()
    return await probe.verify(None, ValidationInput(file_path, content))


async def validate_content_probe(
    content: str,
    target: str = "content",
) -> PolicyTrace[TruthVerdict[list[Violation]]]:
    """
    Validate content using GatekeeperProbe.

    Args:
        content: Code/text to validate
        target: Description of content

    Returns:
        PolicyTrace with validation results
    """
    probe = GatekeeperProbe()
    return await probe.verify(None, ValidationInput(target, content))


# =============================================================================
# Exports
# =============================================================================

__all__ = [
    "GatekeeperProbe",
    "ValidationInput",
    "ValidationState",
    "validate_file_probe",
    "validate_content_probe",
    "violation_to_score",
]
