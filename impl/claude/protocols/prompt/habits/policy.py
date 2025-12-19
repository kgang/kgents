"""
PolicyVector: Learned preferences that influence prompt compilation.

Part of Wave 4 of the Evergreen Prompt System reformation.

The policy vector captures developer habits learned from:
- Git history
- Session logs (when available)
- Code patterns

It is used to:
- Adjust section priorities
- Tune verbosity levels
- Focus on relevant domains
"""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime


@dataclass(frozen=True)
class PolicyVector:
    """
    Learned preferences that influence prompt compilation.

    All values are normalized to 0.0-1.0 range for easy composition.
    Immutable to ensure thread safety and enable caching.
    """

    # Style preferences
    verbosity: float = 0.5  # 0.0 = terse, 1.0 = verbose
    formality: float = 0.6  # 0.0 = casual, 1.0 = formal
    risk_tolerance: float = 0.4  # 0.0 = conservative, 1.0 = experimental

    # Section priorities (higher = more important, included earlier)
    section_weights: tuple[tuple[str, float], ...] = ()
    # e.g., (("principles", 1.0), ("skills", 0.8), ("forest", 0.6))

    # Domain focus (which areas get attention)
    domain_focus: tuple[tuple[str, float], ...] = ()
    # e.g., (("agentese", 0.9), ("cli", 0.7), ("web", 0.3))

    # Metadata
    learned_from: tuple[str, ...] = ()  # ["git", "sessions", "code"]
    confidence: float = 0.5
    generated_at: datetime | None = None
    reasoning_trace: tuple[str, ...] = ()

    def get_section_weight(self, section_name: str, default: float = 0.5) -> float:
        """Get weight for a specific section."""
        for name, weight in self.section_weights:
            if name == section_name:
                return weight
        return default

    def get_domain_focus(self, domain: str, default: float = 0.5) -> float:
        """Get focus level for a specific domain."""
        for name, focus in self.domain_focus:
            if name == domain:
                return focus
        return default

    def merge_with(self, other: PolicyVector, weight: float = 0.5) -> PolicyVector:
        """
        Heuristic merge of two policy vectors.

        Per taste decision: merge heuristically, not hard precedence.

        Args:
            other: The other policy vector to merge with
            weight: Weight for the other vector (0.0 = all self, 1.0 = all other)

        Returns:
            A new merged PolicyVector
        """
        self_weight = 1.0 - weight

        # Merge scalar values
        new_verbosity = self.verbosity * self_weight + other.verbosity * weight
        new_formality = self.formality * self_weight + other.formality * weight
        new_risk_tolerance = self.risk_tolerance * self_weight + other.risk_tolerance * weight

        # Merge section weights
        section_dict: dict[str, float] = {}
        for name, w in self.section_weights:
            section_dict[name] = w * self_weight
        for name, w in other.section_weights:
            if name in section_dict:
                section_dict[name] += w * weight
            else:
                section_dict[name] = w * weight

        # Merge domain focus
        domain_dict: dict[str, float] = {}
        for name, f in self.domain_focus:
            domain_dict[name] = f * self_weight
        for name, f in other.domain_focus:
            if name in domain_dict:
                domain_dict[name] += f * weight
            else:
                domain_dict[name] = f * weight

        # Merge metadata
        new_sources = tuple(sorted(set(self.learned_from) | set(other.learned_from)))
        new_confidence = min(self.confidence, other.confidence)  # Conservative
        new_traces = (
            self.reasoning_trace + (f"Merged with weight={weight}",) + other.reasoning_trace
        )

        return PolicyVector(
            verbosity=new_verbosity,
            formality=new_formality,
            risk_tolerance=new_risk_tolerance,
            section_weights=tuple(sorted(section_dict.items())),
            domain_focus=tuple(sorted(domain_dict.items())),
            learned_from=new_sources,
            confidence=new_confidence,
            generated_at=datetime.now(),
            reasoning_trace=new_traces,
        )

    def with_trace(self, trace: str) -> PolicyVector:
        """Return a new PolicyVector with an added reasoning trace."""
        return PolicyVector(
            verbosity=self.verbosity,
            formality=self.formality,
            risk_tolerance=self.risk_tolerance,
            section_weights=self.section_weights,
            domain_focus=self.domain_focus,
            learned_from=self.learned_from,
            confidence=self.confidence,
            generated_at=self.generated_at,
            reasoning_trace=self.reasoning_trace + (trace,),
        )

    @classmethod
    def default(cls) -> PolicyVector:
        """Create a default policy vector with neutral settings."""
        return cls(
            verbosity=0.5,
            formality=0.6,
            risk_tolerance=0.4,
            section_weights=(
                ("identity", 1.0),
                ("principles", 0.9),
                ("systems", 0.8),
                ("skills", 0.7),
                ("forest", 0.6),
                ("context", 0.5),
            ),
            domain_focus=(),
            learned_from=("default",),
            confidence=0.5,
            generated_at=datetime.now(),
            reasoning_trace=("Created with default settings",),
        )

    @classmethod
    def from_git_patterns(cls, patterns: list) -> PolicyVector:
        """
        Create a PolicyVector from git patterns.

        Args:
            patterns: List of GitPattern objects from GitPatternAnalyzer

        Returns:
            PolicyVector derived from the patterns
        """
        from .git_analyzer import GitPattern

        traces = ["Deriving policy from git patterns"]
        section_weights: dict[str, float] = {}
        domain_focus: dict[str, float] = {}
        verbosity = 0.5
        formality = 0.6

        for pattern in patterns:
            if not isinstance(pattern, GitPattern):
                continue

            traces.append(f"Processing {pattern.pattern_type}: {pattern.description}")

            if pattern.pattern_type == "commit_style":
                # Derive verbosity from message length
                avg_length = pattern.details.get("avg_length", 50)
                if avg_length > 80:
                    verbosity = 0.7
                    traces.append("  → Higher verbosity (long commit messages)")
                elif avg_length < 30:
                    verbosity = 0.3
                    traces.append("  → Lower verbosity (short commit messages)")

                # Derive formality from conventional commits
                conv_ratio = pattern.details.get("conventional_ratio", 0)
                if conv_ratio > 0.7:
                    formality = 0.8
                    traces.append("  → Higher formality (conventional commits)")

            elif pattern.pattern_type == "file_focus":
                # Derive domain focus from directory patterns
                for i in range(3):
                    ratio = pattern.details.get(f"dir_{i}_ratio", 0)
                    if ratio > 0.1 and len(pattern.evidence) > i:
                        dir_name = pattern.evidence[i].split(":")[0].strip().rstrip("/")
                        # Extract last component for domain name
                        domain = dir_name.split("/")[-1] if "/" in dir_name else dir_name
                        if domain:
                            domain_focus[domain] = min(1.0, ratio * 2)  # Scale up
                            traces.append(
                                f"  → Domain focus: {domain} = {domain_focus[domain]:.2f}"
                            )

        # Calculate overall confidence
        confidences = [p.confidence for p in patterns if isinstance(p, GitPattern)]
        avg_confidence = sum(confidences) / len(confidences) if confidences else 0.5

        return cls(
            verbosity=verbosity,
            formality=formality,
            risk_tolerance=0.4,  # Default, could derive from commit frequency
            section_weights=tuple(sorted(section_weights.items())),
            domain_focus=tuple(sorted(domain_focus.items())),
            learned_from=("git",),
            confidence=avg_confidence,
            generated_at=datetime.now(),
            reasoning_trace=tuple(traces),
        )

    @classmethod
    def from_session_patterns(cls, patterns: list) -> "PolicyVector":
        """
        Create a PolicyVector from session patterns.

        Args:
            patterns: List of SessionPattern objects from SessionPatternAnalyzer

        Returns:
            PolicyVector derived from the patterns
        """
        traces = ["Deriving policy from session patterns"]
        domain_focus: dict[str, float] = {}
        verbosity = 0.5
        formality = 0.6
        risk_tolerance = 0.4

        for pattern in patterns:
            # Handle both SessionPattern and objects with to_git_pattern
            pattern_type = getattr(pattern, "pattern_type", None)
            details = getattr(pattern, "details", {})
            description = getattr(pattern, "description", "")
            evidence = getattr(pattern, "evidence", ())

            traces.append(f"Processing {pattern_type}: {description}")

            if pattern_type == "command_frequency":
                # Derive verbosity from message length
                avg_length = details.get("avg_length", 100)
                if avg_length > 150:
                    verbosity = 0.7
                    traces.append("  → Higher verbosity (long prompts)")
                elif avg_length < 50:
                    verbosity = 0.3
                    traces.append("  → Lower verbosity (short prompts)")

                # Question-oriented users might want more detailed responses
                question_ratio = details.get("question_ratio", 0)
                if question_ratio > 0.5:
                    verbosity = max(verbosity, 0.6)
                    traces.append("  → Question-oriented user")

            elif pattern_type == "project_focus":
                # Derive domain focus from project patterns
                for i in range(3):
                    ratio = details.get(f"project_{i}_ratio", 0)
                    if ratio > 0.1 and len(evidence) > i:
                        project = evidence[i].split(":")[0].strip()
                        if project:
                            domain_focus[project] = min(1.0, ratio * 1.5)
                            traces.append(
                                f"  → Project focus: {project} = {domain_focus[project]:.2f}"
                            )

            elif pattern_type == "tool_usage":
                # Long sessions might indicate complex tasks
                messages_per_session = details.get("messages_per_session", 25)
                if messages_per_session > 40:
                    risk_tolerance = 0.5  # More experienced user
                    traces.append("  → Extended sessions, higher risk tolerance")

        # Calculate overall confidence
        confidences = [getattr(p, "confidence", 0.5) for p in patterns]
        avg_confidence = sum(confidences) / len(confidences) if confidences else 0.5

        return cls(
            verbosity=verbosity,
            formality=formality,
            risk_tolerance=risk_tolerance,
            section_weights=(),
            domain_focus=tuple(sorted(domain_focus.items())),
            learned_from=("sessions",),
            confidence=avg_confidence,
            generated_at=datetime.now(),
            reasoning_trace=tuple(traces),
        )

    @classmethod
    def from_code_patterns(cls, patterns: list) -> "PolicyVector":
        """
        Create a PolicyVector from code patterns.

        Args:
            patterns: List of CodePattern objects from CodePatternAnalyzer

        Returns:
            PolicyVector derived from the patterns
        """
        traces = ["Deriving policy from code patterns"]
        verbosity = 0.5
        formality = 0.6
        risk_tolerance = 0.4

        for pattern in patterns:
            pattern_type = getattr(pattern, "pattern_type", None)
            details = getattr(pattern, "details", {})
            description = getattr(pattern, "description", "")

            traces.append(f"Processing {pattern_type}: {description}")

            if pattern_type == "typing":
                # Strong type hints suggest formal style preference
                arg_ratio = details.get("arg_annotation_ratio", 0)
                return_ratio = details.get("return_annotation_ratio", 0)
                if arg_ratio > 0.7 or return_ratio > 0.7:
                    formality = 0.8
                    traces.append("  → Strong type hints, higher formality")

            elif pattern_type == "docstrings":
                # Well-documented code suggests verbosity preference
                func_ratio = details.get("function_docstring_ratio", 0)
                if func_ratio > 0.7:
                    verbosity = 0.7
                    traces.append("  → Well documented, higher verbosity")
                elif func_ratio < 0.2:
                    verbosity = 0.4
                    traces.append("  → Limited docs, lower verbosity")

            elif pattern_type == "naming":
                # Naming conventions indicate formality
                snake_ratio = details.get("snake_case_ratio", 0)
                if snake_ratio > 0.9:
                    formality = 0.7
                    traces.append("  → Consistent naming, higher formality")

            elif pattern_type == "structure":
                # Class-heavy code might indicate different complexity
                class_ratio = details.get("class_ratio", 0)
                if class_ratio > 0.6:
                    traces.append("  → Class-heavy structure noted")

        # Calculate overall confidence
        confidences = [getattr(p, "confidence", 0.5) for p in patterns]
        avg_confidence = sum(confidences) / len(confidences) if confidences else 0.5

        return cls(
            verbosity=verbosity,
            formality=formality,
            risk_tolerance=risk_tolerance,
            section_weights=(),
            domain_focus=(),
            learned_from=("code",),
            confidence=avg_confidence,
            generated_at=datetime.now(),
            reasoning_trace=tuple(traces),
        )


__all__ = [
    "PolicyVector",
]
