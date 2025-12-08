"""
Error Memory: Track and learn from failure patterns.

This module implements Layer 3c of the Evolution Reliability Plan:
- Record failure patterns across evolution attempts
- Learn what errors are common for specific module categories
- Generate warnings for prompts based on historical failures
- Integrate with ImprovementMemory for unified memory layer

Goals:
- Avoid repeating the same mistakes
- Provide failure-aware context to LLM prompts
- Learn cross-session patterns (persistent storage)
"""

from __future__ import annotations

import hashlib
import json
from collections import Counter, defaultdict
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from pathlib import Path
from typing import Any, Optional


@dataclass
class ErrorPattern:
    """
    A recorded error pattern from a failed experiment.

    Immutable record of what went wrong, when, and in what context.
    """
    module_category: str  # "bootstrap", "agents", "runtime", etc.
    module_name: str
    hypothesis_type: str  # Categorized hypothesis type
    failure_type: str  # "syntax", "type", "import", "test", etc.
    failure_details: str
    timestamp: str
    hypothesis_hash: str  # For deduplication

    def to_dict(self) -> dict[str, Any]:
        """Convert to dictionary for JSON serialization."""
        return {
            "module_category": self.module_category,
            "module_name": self.module_name,
            "hypothesis_type": self.hypothesis_type,
            "failure_type": self.failure_type,
            "failure_details": self.failure_details,
            "timestamp": self.timestamp,
            "hypothesis_hash": self.hypothesis_hash,
        }

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> "ErrorPattern":
        """Create from dictionary."""
        return cls(
            module_category=data["module_category"],
            module_name=data["module_name"],
            hypothesis_type=data["hypothesis_type"],
            failure_type=data["failure_type"],
            failure_details=data["failure_details"],
            timestamp=data["timestamp"],
            hypothesis_hash=data["hypothesis_hash"],
        )


@dataclass
class ErrorWarning:
    """A warning about common failure patterns."""
    pattern_type: str
    occurrences: int
    common_detail: str
    severity: str  # "low", "medium", "high"
    recommendation: str


@dataclass
class ErrorMemoryStats:
    """Statistics about error memory."""
    total_failures: int
    unique_patterns: int
    most_common_failures: list[tuple[str, int]]
    categories_affected: set[str] = field(default_factory=set)


class ErrorMemory:
    """
    Track error patterns and learn what to avoid.

    Integrated with ImprovementMemory to provide unified memory layer.
    Persists to disk for cross-session learning.

    Storage format: JSON file with error patterns indexed by category and type.
    """

    def __init__(self, storage_path: Optional[Path] = None):
        """
        Initialize error memory.

        Args:
            storage_path: Path to store error patterns. Defaults to
                         .memory/error_patterns.json
        """
        if storage_path is None:
            storage_path = Path(".memory/error_patterns.json")

        self.storage_path = storage_path
        self.error_patterns: dict[str, list[ErrorPattern]] = defaultdict(list)
        self._load()

    def _load(self) -> None:
        """Load error patterns from disk."""
        if not self.storage_path.exists():
            return

        try:
            with open(self.storage_path, 'r') as f:
                data = json.load(f)

            for key, patterns in data.items():
                self.error_patterns[key] = [
                    ErrorPattern.from_dict(p) for p in patterns
                ]
        except (json.JSONDecodeError, KeyError) as e:
            # Corrupted storage, start fresh
            print(f"Warning: Could not load error memory: {e}")
            self.error_patterns = defaultdict(list)

    def _persist(self) -> None:
        """Persist error patterns to disk."""
        # Ensure directory exists
        self.storage_path.parent.mkdir(parents=True, exist_ok=True)

        # Convert to serializable format
        data = {
            key: [p.to_dict() for p in patterns]
            for key, patterns in self.error_patterns.items()
        }

        with open(self.storage_path, 'w') as f:
            json.dump(data, f, indent=2)

    def record_failure(
        self,
        module_category: str,
        module_name: str,
        hypothesis: str,
        failure_type: str,
        failure_details: str
    ) -> None:
        """
        Record a failure for future learning.

        Args:
            module_category: Category of module ("bootstrap", "agents", etc.)
            module_name: Name of the specific module
            hypothesis: The hypothesis that failed
            failure_type: Type of failure ("syntax", "type", "import", etc.)
            failure_details: Detailed error message
        """
        # Hash hypothesis for deduplication
        hypothesis_hash = hashlib.sha256(hypothesis.encode()).hexdigest()[:16]

        # Categorize hypothesis type
        hypothesis_type = self._categorize_hypothesis(hypothesis)

        pattern = ErrorPattern(
            module_category=module_category,
            module_name=module_name,
            hypothesis_type=hypothesis_type,
            failure_type=failure_type,
            failure_details=failure_details,
            timestamp=datetime.now().isoformat(),
            hypothesis_hash=hypothesis_hash,
        )

        # Store by category:failure_type key
        key = f"{module_category}:{failure_type}"
        self.error_patterns[key].append(pattern)

        # Persist immediately
        self._persist()

    def get_warnings_for_module(
        self,
        module_category: str,
        threshold: int = 3,
        days_back: int = 30
    ) -> list[ErrorWarning]:
        """
        Get warnings based on past failures for this module category.

        Args:
            module_category: Category to get warnings for
            threshold: Minimum occurrences to trigger warning (default 3)
            days_back: Only consider failures from last N days (default 30)

        Returns:
            List of warnings about common failure patterns
        """
        warnings = []
        cutoff_date = datetime.now() - timedelta(days=days_back)

        # Find all patterns for this category
        relevant_keys = [k for k in self.error_patterns if k.startswith(f"{module_category}:")]

        for key in relevant_keys:
            patterns = self.error_patterns[key]

            # Filter by date
            recent_patterns = [
                p for p in patterns
                if datetime.fromisoformat(p.timestamp) >= cutoff_date
            ]

            if len(recent_patterns) >= threshold:
                failure_type = key.split(':')[1]
                common_detail = self._find_common_pattern(recent_patterns)

                # Determine severity based on occurrence count
                if len(recent_patterns) >= 10:
                    severity = "high"
                elif len(recent_patterns) >= 5:
                    severity = "medium"
                else:
                    severity = "low"

                # Generate recommendation
                recommendation = self._generate_recommendation(
                    failure_type,
                    common_detail
                )

                warnings.append(ErrorWarning(
                    pattern_type=failure_type,
                    occurrences=len(recent_patterns),
                    common_detail=common_detail,
                    severity=severity,
                    recommendation=recommendation,
                ))

        return warnings

    def format_warnings_for_prompt(
        self,
        warnings: list[ErrorWarning]
    ) -> str:
        """
        Format warnings for inclusion in LLM prompt.

        Returns formatted warning section to prepend to prompts.
        """
        if not warnings:
            return ""

        # Sort by severity and occurrence count
        severity_order = {"high": 0, "medium": 1, "low": 2}
        warnings = sorted(
            warnings,
            key=lambda w: (severity_order[w.severity], -w.occurrences)
        )

        lines = ["## ⚠️ COMMON PITFALLS (Learn from past failures)\n"]

        for warning in warnings[:5]:  # Limit to top 5 warnings
            severity_emoji = {
                "high": "🔴",
                "medium": "🟡",
                "low": "🟢"
            }[warning.severity]

            lines.append(f"""
{severity_emoji} **{warning.pattern_type.upper()} errors** (occurred {warning.occurrences} times)
   - Pattern: {warning.common_detail}
   - **Recommendation**: {warning.recommendation}
""")

        lines.append("""
**IMPORTANT**: These errors have occurred multiple times in similar code.
Take extra care to avoid them in your improvement.
""")

        return "\n".join(lines)

    def get_stats(self) -> ErrorMemoryStats:
        """Get statistics about error memory."""
        total_failures = sum(len(patterns) for patterns in self.error_patterns.values())

        # Count unique patterns (by hypothesis hash)
        unique_hashes = set(
            p.hypothesis_hash
            for patterns in self.error_patterns.values()
            for p in patterns
        )

        # Most common failure types
        failure_counts: Counter[str] = Counter()
        for key in self.error_patterns:
            failure_type = key.split(':')[1]
            failure_counts[failure_type] += len(self.error_patterns[key])

        # Categories affected
        categories = {
            key.split(':')[0]
            for key in self.error_patterns
        }

        return ErrorMemoryStats(
            total_failures=total_failures,
            unique_patterns=len(unique_hashes),
            most_common_failures=failure_counts.most_common(10),
            categories_affected=categories,
        )

    def clear_old_patterns(self, days_to_keep: int = 90) -> int:
        """
        Clear error patterns older than specified days.

        Returns number of patterns removed.
        """
        cutoff_date = datetime.now() - timedelta(days=days_to_keep)
        removed_count = 0

        for key in list(self.error_patterns.keys()):
            patterns = self.error_patterns[key]
            new_patterns = [
                p for p in patterns
                if datetime.fromisoformat(p.timestamp) >= cutoff_date
            ]

            removed = len(patterns) - len(new_patterns)
            removed_count += removed

            if new_patterns:
                self.error_patterns[key] = new_patterns
            else:
                del self.error_patterns[key]

        if removed_count > 0:
            self._persist()

        return removed_count

    def _categorize_hypothesis(self, hypothesis: str) -> str:
        """
        Categorize hypothesis type for pattern matching.

        Categories:
        - refactor: Code structure improvements
        - type_hints: Type annotation improvements
        - docs: Documentation improvements
        - bug_fix: Bug fixes
        - feature: New functionality
        - test: Test improvements
        - other: Uncategorized
        """
        hypothesis_lower = hypothesis.lower()

        if any(word in hypothesis_lower for word in ["refactor", "restructure", "reorganize"]):
            return "refactor"
        if any(word in hypothesis_lower for word in ["type", "annotation", "hint"]):
            return "type_hints"
        if any(word in hypothesis_lower for word in ["doc", "comment", "docstring"]):
            return "docs"
        if any(word in hypothesis_lower for word in ["fix", "bug", "error", "issue"]):
            return "bug_fix"
        if any(word in hypothesis_lower for word in ["add", "feature", "implement", "create"]):
            return "feature"
        if any(word in hypothesis_lower for word in ["test", "pytest", "coverage"]):
            return "test"

        return "other"

    def _find_common_pattern(self, patterns: list[ErrorPattern]) -> str:
        """
        Find common substring/pattern in failure details.

        Uses word frequency analysis to identify common error messages.
        """
        if not patterns:
            return ""

        # Extract all words from failure details
        all_words = []
        for p in patterns:
            # Remove common noise words
            words = [
                w for w in p.failure_details.split()
                if len(w) > 3 and w not in {"line", "error", "file", "code"}
            ]
            all_words.extend(words)

        if not all_words:
            return patterns[0].failure_details[:100]  # Fallback to first error

        # Find most common words
        word_counts = Counter(all_words)
        common_words = [word for word, _ in word_counts.most_common(5)]

        return " ".join(common_words)

    def _generate_recommendation(
        self,
        failure_type: str,
        common_detail: str
    ) -> str:
        """Generate actionable recommendation based on failure type."""
        recommendations = {
            "syntax": "Validate all brackets, quotes, and colons before returning code",
            "type": "Double-check all type annotations and generic parameter counts",
            "import": "Include complete import block from original file",
            "constructor": "Ensure all classes have @dataclass or __init__",
            "test": "Run tests locally before submitting changes",
            "incomplete": "Remove all TODO/pass placeholders before returning",
        }

        return recommendations.get(
            failure_type,
            f"Address the recurring issue: {common_detail}"
        )


# Singleton instance with default storage path
error_memory = ErrorMemory()
