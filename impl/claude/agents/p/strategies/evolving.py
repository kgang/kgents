"""
Evolving Parser: Schema Drift Tracking (Phase 3: Novel Techniques)

The Principle: LLM output formats drift over time. Parsers should track format
changes and adapt.

Why It's Better:
- Self-optimizing: Faster over time as it learns common formats
- Drift detection: Know when LLM behavior changes
- Data-driven: No manual reordering of fallback chains

Use Cases:
- Long-running E-gent evolution: Track code generation format drift
- B-gent hypothesis format: Detect when LLM starts using new section headers
- Cross-LLM compatibility: Different LLMs prefer different formats
"""

from dataclasses import dataclass, field
from typing import Callable, Optional
from collections import Counter
import json
import time

from agents.p.core import ParseResult, Parser, ParserConfig


@dataclass
class FormatStats:
    """Statistics for a specific format."""

    name: str
    success_count: int = 0
    failure_count: int = 0
    total_parse_time_ms: float = 0.0
    last_used: float = field(default_factory=time.time)
    avg_confidence: float = 0.0

    @property
    def success_rate(self) -> float:
        """Success rate as fraction 0.0-1.0."""
        total = self.success_count + self.failure_count
        return self.success_count / total if total > 0 else 0.0

    @property
    def avg_parse_time_ms(self) -> float:
        """Average parse time in milliseconds."""
        return (
            self.total_parse_time_ms / self.success_count
            if self.success_count > 0
            else 0.0
        )

    def to_dict(self) -> dict:
        """Convert to dict for serialization."""
        return {
            "name": self.name,
            "success_count": self.success_count,
            "failure_count": self.failure_count,
            "success_rate": self.success_rate,
            "avg_parse_time_ms": self.avg_parse_time_ms,
            "avg_confidence": self.avg_confidence,
            "last_used": self.last_used,
        }


@dataclass
class DriftReport:
    """Report on format drift over time."""

    formats: dict[str, FormatStats]
    total_parses: int
    current_dominant: Optional[str] = None
    drift_detected: bool = False
    drift_reason: Optional[str] = None

    def to_dict(self) -> dict:
        """Convert to dict for serialization."""
        return {
            "formats": {name: stats.to_dict() for name, stats in self.formats.items()},
            "total_parses": self.total_parses,
            "current_dominant": self.current_dominant,
            "drift_detected": self.drift_detected,
            "drift_reason": self.drift_reason,
        }


@dataclass
class EvolvingParser[A](Parser[A]):
    """
    Parser that learns from observed formats over time.

    Tracks which strategies succeed most often and reorders them
    dynamically for optimal performance.

    Features:
    - Success rate tracking per strategy
    - Parse time tracking
    - Confidence averaging
    - Drift detection (when format distribution changes)
    - Self-optimization (reorder strategies by success)

    Example:
        parser = EvolvingParser(
            strategies={
                "json": json_parser,
                "yaml": yaml_parser,
                "regex": regex_parser,
            }
        )

        # Over time, parser learns which strategy works most often
        for text in texts:
            result = parser.parse(text)

        # Check drift
        report = parser.report_drift()
        if report.drift_detected:
            print(f"Drift detected: {report.drift_reason}")
    """

    strategies: dict[str, Parser[A]]
    config: ParserConfig = field(default_factory=ParserConfig)

    # Internal state
    _stats: dict[str, FormatStats] = field(default_factory=dict, init=False, repr=False)
    _total_parses: int = field(default=0, init=False, repr=False)
    _last_dominant: Optional[str] = field(default=None, init=False, repr=False)
    _drift_threshold: float = 0.15  # 15% change in dominant format triggers drift

    def __post_init__(self):
        """Initialize stats for all strategies."""
        if not self._stats:
            self._stats = {
                name: FormatStats(name=name) for name in self.strategies.keys()
            }

    def parse(self, text: str) -> ParseResult[A]:
        """
        Parse and track which format succeeded.

        Tries strategies in order of historical success rate.
        """
        self._total_parses += 1

        # Get strategies ranked by success rate
        ranked = self._get_ranked_strategies()

        for name, strategy in ranked:
            start_time = time.time()

            try:
                result = strategy.parse(text)

                parse_time_ms = (time.time() - start_time) * 1000

                if result.success:
                    # Track successful format
                    stats = self._stats[name]
                    stats.success_count += 1
                    stats.total_parse_time_ms += parse_time_ms
                    stats.last_used = time.time()

                    # Update average confidence
                    n = stats.success_count
                    stats.avg_confidence = (
                        stats.avg_confidence * (n - 1) + result.confidence
                    ) / n

                    # Add format metadata
                    result.metadata["format"] = name
                    result.metadata["format_stats"] = stats.to_dict()

                    return result
                else:
                    # Track failure
                    self._stats[name].failure_count += 1

            except Exception as e:
                # Track exception as failure
                self._stats[name].failure_count += 1
                continue

        return ParseResult[A](
            success=False, error=f"All {len(self.strategies)} formats failed"
        )

    def _get_ranked_strategies(self) -> list[tuple[str, Parser[A]]]:
        """
        Get strategies ranked by success rate (descending).

        Ranking factors:
        1. Success rate (primary)
        2. Average confidence (secondary)
        3. Parse time (tertiary - lower is better)
        """

        def rank_score(name: str) -> float:
            stats = self._stats[name]
            success_rate = stats.success_rate
            avg_confidence = stats.avg_confidence
            # Penalize slow parsers (normalize to 0-1, invert)
            time_penalty = 1.0 - min(stats.avg_parse_time_ms / 1000.0, 1.0)

            # Weighted score
            return success_rate * 0.6 + avg_confidence * 0.3 + time_penalty * 0.1

        ranked_names = sorted(self.strategies.keys(), key=rank_score, reverse=True)
        return [(name, self.strategies[name]) for name in ranked_names]

    def report_drift(self) -> DriftReport:
        """
        Report which formats are becoming more/less common.

        Drift is detected when:
        - The dominant format changes by > threshold
        - A new format becomes dominant
        """
        if not self._stats:
            return DriftReport(
                formats={},
                total_parses=0,
                drift_detected=False,
            )

        # Find current dominant format
        ranked = sorted(
            self._stats.items(),
            key=lambda x: x[1].success_rate,
            reverse=True,
        )

        current_dominant = ranked[0][0] if ranked else None

        drift_detected = False
        drift_reason = None

        if self._last_dominant and current_dominant != self._last_dominant:
            old_stats = self._stats[self._last_dominant]
            new_stats = self._stats[current_dominant]

            rate_change = new_stats.success_rate - old_stats.success_rate

            if rate_change > self._drift_threshold:
                drift_detected = True
                drift_reason = (
                    f"Format changed from {self._last_dominant} "
                    f"({old_stats.success_rate:.1%}) to {current_dominant} "
                    f"({new_stats.success_rate:.1%})"
                )

        # Update last dominant
        self._last_dominant = current_dominant

        return DriftReport(
            formats=self._stats.copy(),
            total_parses=self._total_parses,
            current_dominant=current_dominant,
            drift_detected=drift_detected,
            drift_reason=drift_reason,
        )

    def export_stats(self, filepath: str) -> None:
        """Export statistics to JSON file."""
        report = self.report_drift()
        with open(filepath, "w") as f:
            json.dump(report.to_dict(), f, indent=2)

    def import_stats(self, filepath: str) -> None:
        """Import statistics from JSON file."""
        with open(filepath, "r") as f:
            data = json.load(f)

        for name, stats_dict in data.get("formats", {}).items():
            if name in self._stats:
                stats = self._stats[name]
                stats.success_count = stats_dict["success_count"]
                stats.failure_count = stats_dict["failure_count"]
                stats.total_parse_time_ms = stats_dict.get("total_parse_time_ms", 0.0)
                stats.avg_confidence = stats_dict.get("avg_confidence", 0.0)
                stats.last_used = stats_dict.get("last_used", time.time())

        self._total_parses = data.get("total_parses", 0)

    def parse_stream(self, tokens: list[str]) -> list[ParseResult[A]]:
        """Stream parsing (buffers and parses complete)."""
        text = "".join(tokens)
        return [self.parse(text)]

    def configure(self, **config_updates) -> "EvolvingParser[A]":
        """Return new parser with updated configuration."""
        new_config = ParserConfig(**{**self.config.__dict__, **config_updates})
        return EvolvingParser(strategies=self.strategies, config=new_config)


def create_multi_format_parser(formats: dict[str, Parser]) -> EvolvingParser:
    """
    Create an EvolvingParser that learns from multiple formats.

    Example:
        from agents.p.strategies.anchor import AnchorBasedParser
        from agents.p.strategies.stack_balancing import json_stream_parser

        parser = create_multi_format_parser({
            "anchor": AnchorBasedParser(anchor="###ITEM:"),
            "json": json_stream_parser(),
            "regex": RegexParser(pattern=r"item:\s*(.+)"),
        })

        # Parser learns which format is most common
        for text in dataset:
            result = parser.parse(text)

        # Check what it learned
        report = parser.report_drift()
        print(f"Dominant format: {report.current_dominant}")
    """
    return EvolvingParser(strategies=formats)
