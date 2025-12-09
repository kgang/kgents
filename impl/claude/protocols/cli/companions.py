"""
Daily Companion Commands - Tier 1 from cli-integrations.md

These are high-value, zero-token commands that run entirely locally.
They form the core daily interaction surface.

Commands:
    pulse   - 1-line project health pulse (W-gent + D-gent)
    ground  - Parse and reflect structure without opinion (Ground + P-gent)
    breathe - Contemplative pause, interrupt hyperfocus (I-gent)
    entropy - Show session entropy/chaos budget (D-gent)
"""

from __future__ import annotations

import re
import subprocess
import time
from dataclasses import dataclass
from datetime import datetime
from enum import Enum
from pathlib import Path

from .cli_types import (
    CLIContext,
    CommandResult,
    ErrorInfo,
    ErrorRecoverability,
    ErrorSeverity,
)


# =============================================================================
# Flow Phase Detection (for pulse)
# =============================================================================


class FlowPhase(Enum):
    """Time-of-day flow phases."""

    MORNING = "morning"  # 6-12
    AFTERNOON = "afternoon"  # 12-17
    EVENING = "evening"  # 17-21
    NIGHT = "night"  # 21-6

    @classmethod
    def current(cls) -> FlowPhase:
        """Get current flow phase based on time."""
        hour = datetime.now().hour
        if 6 <= hour < 12:
            return cls.MORNING
        elif 12 <= hour < 17:
            return cls.AFTERNOON
        elif 17 <= hour < 21:
            return cls.EVENING
        else:
            return cls.NIGHT


@dataclass(frozen=True)
class PulseReport:
    """
    1-line project health pulse.

    Captures:
    - Hypotheses pending (from notes/comments)
    - Tensions held (from kgents state)
    - Current flow phase
    - Recent activity level
    """

    hypotheses_pending: int
    tensions_held: int
    flow_phase: FlowPhase
    activity_level: str  # active, quiet, dormant
    last_change: datetime | None

    def render(self) -> str:
        """Render as single-line pulse."""
        # Build state indicators
        h_indicator = (
            f"{self.hypotheses_pending} hypotheses pending"
            if self.hypotheses_pending
            else ""
        )
        t_indicator = (
            f"{self.tensions_held} tensions held" if self.tensions_held else ""
        )

        parts = []
        if h_indicator:
            parts.append(h_indicator)
        if t_indicator:
            parts.append(t_indicator)

        state = " · ".join(parts) if parts else "clear"

        # Activity symbol
        activity_symbol = {
            "active": "◉",
            "quiet": "◐",
            "dormant": "◌",
        }.get(self.activity_level, "◌")

        return f"→ {activity_symbol} {state} · flow: {self.flow_phase.value}"


def detect_hypotheses_pending(path: Path) -> int:
    """
    Detect pending hypotheses from source files.

    Looks for patterns like:
    - TODO: hypothesis...
    - # H: ...
    - HYPOTHESIS: ...
    - What if...? (in comments)
    """
    patterns = [
        r"(?:TODO|FIXME|HYPOTHESIS|H:)\s*[Hh]ypothesis",
        r"#\s*H:\s*",
        r"#\s*[Ww]hat if",
        r"#\s*\?\s+",
    ]
    combined_pattern = re.compile("|".join(patterns))

    count = 0
    try:
        for ext in ("*.py", "*.md", "*.txt"):
            for file in path.rglob(ext):
                # Skip hidden and vendor directories
                if any(p.startswith(".") for p in file.parts):
                    continue
                if "node_modules" in file.parts or "venv" in file.parts:
                    continue
                try:
                    content = file.read_text(errors="ignore")
                    count += len(combined_pattern.findall(content))
                except (PermissionError, OSError):
                    continue
    except Exception:
        pass
    return count


def detect_tensions_held(path: Path) -> int:
    """
    Detect tensions from kgents state file or tension markers.

    Looks for:
    - .kgents/tensions.json
    - TENSION markers in files
    """
    count = 0

    # Check for kgents state file
    state_file = path / ".kgents" / "tensions.json"
    if state_file.exists():
        try:
            import json

            data = json.loads(state_file.read_text())
            count += len(data.get("held", []))
        except Exception:
            pass

    # Also scan for TENSION markers
    tension_pattern = re.compile(r"TENSION:|⚡\s*[Tt]ension|←→")
    try:
        for file in path.rglob("*.md"):
            if any(p.startswith(".") for p in file.parts):
                continue
            try:
                content = file.read_text(errors="ignore")
                count += len(tension_pattern.findall(content))
            except (PermissionError, OSError):
                continue
    except Exception:
        pass

    return min(count, 99)  # Cap at reasonable number


def detect_activity_level(path: Path) -> tuple[str, datetime | None]:
    """
    Detect activity level from git or file modification times.

    Returns (level, last_change_time)
    """
    # Try git first
    try:
        result = subprocess.run(
            ["git", "log", "-1", "--format=%ct"],
            cwd=path,
            capture_output=True,
            text=True,
            timeout=2,
        )
        if result.returncode == 0 and result.stdout.strip():
            timestamp = int(result.stdout.strip())
            last_change = datetime.fromtimestamp(timestamp)
            age_hours = (datetime.now() - last_change).total_seconds() / 3600

            if age_hours < 1:
                return "active", last_change
            elif age_hours < 24:
                return "quiet", last_change
            else:
                return "dormant", last_change
    except Exception:
        pass

    # Fallback: check file modification times
    try:
        latest = None
        for file in path.rglob("*"):
            if file.is_file() and not any(p.startswith(".") for p in file.parts):
                try:
                    mtime = datetime.fromtimestamp(file.stat().st_mtime)
                    if latest is None or mtime > latest:
                        latest = mtime
                except Exception:
                    continue

        if latest:
            age_hours = (datetime.now() - latest).total_seconds() / 3600
            if age_hours < 1:
                return "active", latest
            elif age_hours < 24:
                return "quiet", latest
            else:
                return "dormant", latest
    except Exception:
        pass

    return "dormant", None


# =============================================================================
# Ground Command (Parse & Reflect)
# =============================================================================


@dataclass(frozen=True)
class GroundReport:
    """
    Parsed structure of a statement.

    Pure reflection without opinion - "What did I actually say?"
    """

    raw: str
    parsed_intents: list[tuple[str, str]]  # (action, target) pairs
    contradiction_score: float  # 0-1, higher = more internal tension
    complexity_score: float  # 0-1, higher = more complex

    def render(self) -> str:
        """Render as grounded reflection."""
        if not self.parsed_intents:
            return (
                f"→ PARSED: [unclear intent] — complexity: {self.complexity_score:.1f}"
            )

        intent_strs = [f"[{action}:{target}]" for action, target in self.parsed_intents]
        intents = " ∧ ".join(intent_strs)

        extras = []
        if self.contradiction_score > 0.3:
            extras.append(f"contradiction score: {self.contradiction_score:.1f}")
        if self.complexity_score > 0.5:
            extras.append(f"complexity: {self.complexity_score:.1f}")

        extra_str = f" — {', '.join(extras)}" if extras else ""
        return f"→ PARSED: {intents}{extra_str}"


def ground_statement(statement: str) -> GroundReport:
    """
    Parse a natural language statement into structured intents.

    This is pure local parsing - no LLM calls. Uses heuristics
    to extract action-target pairs.
    """
    # Normalize
    statement = statement.strip().lower()

    # Action patterns
    action_patterns = [
        (r"\b(refactor|restructure|reorganize)\b.*\b(\w+)\b", "refactor"),
        (r"\b(add|create|implement|build)\b.*\b(\w+)\b", "add"),
        (r"\b(fix|repair|solve|resolve)\b.*\b(\w+)\b", "fix"),
        (r"\b(remove|delete|drop|eliminate)\b.*\b(\w+)\b", "remove"),
        (r"\b(update|upgrade|modify|change)\b.*\b(\w+)\b", "update"),
        (r"\b(test|verify|validate|check)\b.*\b(\w+)\b", "test"),
        (r"\b(optimize|improve|enhance)\b.*\b(\w+)\b", "optimize"),
        (r"\b(document|explain|describe)\b.*\b(\w+)\b", "document"),
    ]

    # Contradiction indicators
    contradiction_patterns = [
        r"\bbut\b",
        r"\band also\b",
        r"\bwhile also\b",
        r"\bat the same time\b",
        r"\bwithout\b",
        r"\bhowever\b",
    ]

    # Extract intents
    intents = []
    for pattern, action in action_patterns:
        matches = re.findall(pattern, statement)
        for match in matches:
            target = match[-1] if isinstance(match, tuple) else match
            if len(target) > 2:  # Skip very short words
                intents.append((action, target))

    # Calculate contradiction score
    contradiction_count = sum(
        1 for pattern in contradiction_patterns if re.search(pattern, statement)
    )
    contradiction_score = min(1.0, contradiction_count * 0.35)

    # If multiple intents, add slight contradiction
    if len(intents) > 1:
        contradiction_score = min(1.0, contradiction_score + 0.2 * (len(intents) - 1))

    # Complexity score based on length and clauses
    words = len(statement.split())
    clauses = len(re.split(r"[,;:]|\band\b|\bor\b", statement))
    complexity_score = min(1.0, (words / 20 + clauses / 4) / 2)

    return GroundReport(
        raw=statement,
        parsed_intents=intents,
        contradiction_score=contradiction_score,
        complexity_score=complexity_score,
    )


# =============================================================================
# Breathe Command (Contemplative Pause)
# =============================================================================


BREATHE_PROMPTS = [
    "what are you actually trying to do?",
    "what would you do if this didn't matter?",
    "what are you avoiding?",
    "is this the right problem?",
    "who is this for?",
    "what does done look like?",
    "what would make this joyful?",
    "what's the simplest thing that could work?",
]


def breathe(duration_seconds: float = 4.0) -> str:
    """
    Generate a contemplative pause with gentle prompt.

    Returns the breathe output (actual timing done by caller).
    """
    import random

    prompt = random.choice(BREATHE_PROMPTS)
    return f"◌ inhale . . . {prompt} . . . exhale ◌"


# =============================================================================
# Entropy Command (Chaos Budget)
# =============================================================================


@dataclass(frozen=True)
class EntropyReport:
    """Session entropy/chaos budget report."""

    session_entropy: float  # 0-1
    tokens_used: int
    llm_calls_made: int
    changes_made: int  # git diff stat or file changes
    time_active_minutes: int
    recommendation: str

    def render(self) -> str:
        """Render as entropy report."""
        if self.session_entropy < 0.3:
            level = "low"
            permission = "Permission to experiment?"
        elif self.session_entropy < 0.7:
            level = "moderate"
            permission = "Balanced exploration."
        else:
            level = "high"
            permission = "Consider consolidating."

        return (
            f"→ SESSION ENTROPY: {self.session_entropy:.2f} ({level}). "
            f"You've been {'conservative' if self.session_entropy < 0.3 else 'active'}. "
            f"{permission}"
        )


def calculate_entropy(path: Path, ctx: CLIContext | None = None) -> EntropyReport:
    """
    Calculate session entropy from various signals.

    Entropy sources:
    - Git uncommitted changes
    - LLM calls made (from budget)
    - File modifications in session
    """
    changes_made = 0
    time_active = 0

    # Git changes as entropy signal
    try:
        result = subprocess.run(
            ["git", "diff", "--stat"],
            cwd=path,
            capture_output=True,
            text=True,
            timeout=2,
        )
        if result.returncode == 0:
            # Count lines changed
            lines = result.stdout.strip().split("\n")
            if lines and lines[-1]:
                # Last line like "5 files changed, 100 insertions(+), 20 deletions(-)"
                match = re.search(r"(\d+) insertions?", lines[-1])
                if match:
                    changes_made += int(match.group(1))
                match = re.search(r"(\d+) deletions?", lines[-1])
                if match:
                    changes_made += int(match.group(1))
    except Exception:
        pass

    # Extract budget info if available
    tokens_used = 0
    llm_calls = 0
    if ctx and ctx.budget:
        tokens_used = ctx.budget.tokens_used
        llm_calls = ctx.budget.llm_calls_used

    # Calculate composite entropy
    change_entropy = min(1.0, changes_made / 500)  # Cap at 500 lines
    token_entropy = min(1.0, tokens_used / 10000)  # Cap at 10k tokens
    call_entropy = min(1.0, llm_calls / 10)  # Cap at 10 calls

    session_entropy = change_entropy * 0.5 + token_entropy * 0.3 + call_entropy * 0.2

    # Recommendation
    if session_entropy < 0.3:
        rec = "Space for bold moves."
    elif session_entropy < 0.7:
        rec = "Good flow. Continue."
    else:
        rec = "High entropy. Commit or revert?"

    return EntropyReport(
        session_entropy=session_entropy,
        tokens_used=tokens_used,
        llm_calls_made=llm_calls,
        changes_made=changes_made,
        time_active_minutes=time_active,
        recommendation=rec,
    )


# =============================================================================
# CLI Integration
# =============================================================================


class CompanionsCLI:
    """CLI handler for daily companion commands."""

    async def pulse(self, path: Path, ctx: CLIContext) -> CommandResult[PulseReport]:
        """
        Generate 1-line project health pulse.

        Cost: 0 tokens (local only)
        """
        start = time.time()

        try:
            hypotheses = detect_hypotheses_pending(path)
            tensions = detect_tensions_held(path)
            activity, last_change = detect_activity_level(path)
            flow = FlowPhase.current()

            report = PulseReport(
                hypotheses_pending=hypotheses,
                tensions_held=tensions,
                flow_phase=flow,
                activity_level=activity,
                last_change=last_change,
            )

            duration_ms = int((time.time() - start) * 1000)
            return CommandResult.ok(report, duration_ms=duration_ms)

        except Exception as e:
            return CommandResult.fail(
                ErrorInfo(
                    error_type=ErrorRecoverability.TRANSIENT,
                    severity=ErrorSeverity.FAILURE,
                    code="PULSE_FAILED",
                    message=str(e),
                )
            )

    async def ground(
        self, statement: str, ctx: CLIContext
    ) -> CommandResult[GroundReport]:
        """
        Parse statement and reflect structure without opinion.

        Cost: 0 tokens (local parsing only)
        """
        start = time.time()

        try:
            report = ground_statement(statement)
            duration_ms = int((time.time() - start) * 1000)
            return CommandResult.ok(report, duration_ms=duration_ms)

        except Exception as e:
            return CommandResult.fail(
                ErrorInfo(
                    error_type=ErrorRecoverability.PERMANENT,
                    severity=ErrorSeverity.FAILURE,
                    code="GROUND_FAILED",
                    message=str(e),
                )
            )

    async def breathe(self, ctx: CLIContext) -> CommandResult[str]:
        """
        Contemplative pause with gentle prompt.

        Cost: 0 tokens
        """
        output = breathe()
        return CommandResult.ok(output, duration_ms=0)

    async def entropy(
        self, path: Path, ctx: CLIContext
    ) -> CommandResult[EntropyReport]:
        """
        Show session entropy/chaos budget.

        Cost: 0 tokens (local git/file analysis)
        """
        start = time.time()

        try:
            report = calculate_entropy(path, ctx)
            duration_ms = int((time.time() - start) * 1000)
            return CommandResult.ok(report, duration_ms=duration_ms)

        except Exception as e:
            return CommandResult.fail(
                ErrorInfo(
                    error_type=ErrorRecoverability.TRANSIENT,
                    severity=ErrorSeverity.FAILURE,
                    code="ENTROPY_FAILED",
                    message=str(e),
                )
            )
