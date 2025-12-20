"""
The Analyst: Counterfactual Debugging and Causal Inference.

Philosophy: Move from "what failed" to "WHY did it fail".
Uses recorded data to simulate alternative histories.

Research Basis:
- Judea Pearl's Causal Inference ("Causality", 2009)
- Delta Debugging (Zeller & Hildebrandt, 1999)

Phase 8.2 - Causal Analysis:
- TestWitness: Recorded test execution with causal context
- CausalAnalyst: Delta debugging and counterfactual queries
- Root cause analysis via causal graphs
"""

import math
import re
from dataclasses import dataclass, field
from datetime import datetime
from typing import Any, Callable, Literal, Sequence

# =============================================================================
# Core Types
# =============================================================================


@dataclass
class TestWitness:
    """A recorded test execution with causal context.

    This is richer than a simple pass/fail - it captures the
    context needed for causal reasoning.
    """

    test_id: str
    agent_path: list[str]  # Agents in the composition chain
    input_data: Any
    input_embedding: list[float] | None = None  # For similarity queries
    outcome: Literal["pass", "fail", "skip", "error"] = "pass"
    duration_ms: float = 0.0
    error_trace: str | None = None
    timestamp: datetime = field(default_factory=datetime.now)
    commit_hash: str = ""
    prompt_template_hash: str = ""
    system_metrics: dict[str, Any] = field(default_factory=dict)

    # Causal features
    parent_test_id: str | None = None  # If this was a retry/variation
    input_mutations: list[str] = field(default_factory=list)

    def to_dict(self) -> dict[str, Any]:
        """Serialize to dictionary."""
        return {
            "test_id": self.test_id,
            "agent_path": self.agent_path,
            "input_data": str(self.input_data),
            "outcome": self.outcome,
            "duration_ms": self.duration_ms,
            "error_trace": self.error_trace,
            "timestamp": self.timestamp.isoformat(),
            "commit_hash": self.commit_hash,
            "prompt_template_hash": self.prompt_template_hash,
            "system_metrics": self.system_metrics,
            "parent_test_id": self.parent_test_id,
            "input_mutations": self.input_mutations,
        }


@dataclass
class DeltaDebugResult:
    """Result of delta debugging: the minimal failure-inducing input."""

    original_input: Any
    minimal_failing_input: Any | None
    passing_variations: list[Any]
    failing_variations: list[Any]
    isolated_cause: str
    confidence: float

    def __repr__(self) -> str:
        return f"DeltaDebugResult(cause='{self.isolated_cause}', confidence={self.confidence:.2f})"


@dataclass
class CounterfactualResult:
    """Answer to "What if...?" queries."""

    query: dict[str, Any]
    answer: str
    confidence: float
    supporting_evidence: list[TestWitness] = field(default_factory=list)

    def __repr__(self) -> str:
        return f"CounterfactualResult('{self.answer}', confidence={self.confidence:.2f})"


@dataclass
class CausalFactor:
    """A factor that causally influences test outcomes."""

    feature: str
    fail_distribution: dict[str, int]
    pass_distribution: dict[str, int]
    p_value: float  # Statistical significance

    @property
    def effect_size(self) -> float:
        """Cohen's d effect size (simplified)."""
        fail_mean = self._mean(self.fail_distribution)
        pass_mean = self._mean(self.pass_distribution)
        pooled_std = 1.0  # Simplified
        return abs(fail_mean - pass_mean) / pooled_std

    def _mean(self, dist: dict[str, int]) -> float:
        """Calculate mean from distribution."""
        total = sum(dist.values())
        if total == 0:
            return 0.0
        weighted = sum(int(k) * v for k, v in dist.items() if k.isdigit())
        return weighted / total


@dataclass
class CausalGraph:
    """Graph of causal relationships between factors and outcomes."""

    nodes: list[str]  # Feature names
    edges: list[tuple[str, str, float]]  # (from, to, strength)
    root_cause: CausalFactor | None

    def __repr__(self) -> str:
        cause = self.root_cause.feature if self.root_cause else "unknown"
        return f"CausalGraph(nodes={len(self.nodes)}, root_cause='{cause}')"


@dataclass
class FlakinessDiagnosis:
    """Diagnosis of WHY a test is flaky."""

    entropy: float  # Shannon entropy of outcomes
    diagnosis: str
    cause: str | None

    def __repr__(self) -> str:
        return f"FlakinessDiagnosis(entropy={self.entropy:.2f}, cause='{self.cause}')"


# =============================================================================
# Witness Store (In-Memory, can be backed by D-gent)
# =============================================================================


class WitnessStore:
    """Storage for test witnesses.

    Can be backed by D-gent PersistentAgent for persistence.
    """

    def __init__(self) -> None:
        self._witnesses: list[TestWitness] = []

    def record(self, witness: TestWitness) -> None:
        """Record a test witness."""
        self._witnesses.append(witness)

    async def query(
        self,
        test_id: str | None = None,
        outcome: str | None = None,
        since: datetime | None = None,
        limit: int = 100,
    ) -> list[TestWitness]:
        """Query witnesses with filters."""
        results = self._witnesses.copy()

        if test_id:
            results = [w for w in results if w.test_id == test_id]
        if outcome:
            results = [w for w in results if w.outcome == outcome]
        if since:
            results = [w for w in results if w.timestamp >= since]

        # Sort by timestamp descending
        results.sort(key=lambda w: w.timestamp, reverse=True)

        return results[:limit]

    def __len__(self) -> int:
        return len(self._witnesses)


# =============================================================================
# The Analyst
# =============================================================================


class CausalAnalyst:
    """Causal inference engine for test failures.

    The Analyst doesn't just report what failed - it uses
    causal reasoning to determine WHY.
    """

    def __init__(self, store: WitnessStore | None = None):
        """Initialize Causal Analyst.

        Args:
            store: Witness store (defaults to in-memory)
        """
        self.store = store or WitnessStore()

    async def delta_debug(
        self,
        failing_witness: TestWitness,
        test_func: Callable[[Any], Any],
    ) -> DeltaDebugResult:
        """Automatically find minimal failure-inducing input.

        This implements Zeller's delta debugging algorithm.

        Args:
            failing_witness: The failing test witness
            test_func: Function to test variations (should raise on failure)

        Returns:
            DeltaDebugResult with isolated cause
        """
        original_input = failing_witness.input_data

        # Generate input variations
        variations = await self._generate_variations(original_input)

        # Test each variation
        passing = []
        failing = [original_input]

        for variation in variations:
            try:
                await test_func(variation)
                passing.append(variation)
            except Exception:
                failing.append(variation)

        # Find the delta between passing and failing
        if passing:
            minimal_delta = self._diff_inputs(passing[0], failing[-1])
        else:
            minimal_delta = "All variations failed - irreducible input"

        confidence = len(passing) / (len(passing) + len(failing)) if variations else 0.0

        return DeltaDebugResult(
            original_input=original_input,
            minimal_failing_input=failing[-1] if failing else None,
            passing_variations=passing,
            failing_variations=failing,
            isolated_cause=minimal_delta,
            confidence=confidence,
        )

    async def _generate_variations(self, input_data: Any) -> list[Any]:
        """Generate input variations for delta debugging."""
        variations: list[Any] = []

        if isinstance(input_data, str):
            text = input_data
            # Text variations
            variations.extend(
                [
                    text[: len(text) // 2],  # First half
                    text[len(text) // 2 :],  # Second half
                    re.sub(r"\s+", " ", text),  # Normalize whitespace
                    re.sub(r"[^\w\s]", "", text),  # Remove punctuation
                    text.lower(),  # Lowercase
                    self._remove_markdown(text),  # Strip markdown
                    self._simplify_nesting(text),  # Flatten nested structures
                ]
            )
        elif isinstance(input_data, dict):
            # Dict variations - remove each key
            for key in input_data:
                variations.append({k: v for k, v in input_data.items() if k != key})
        elif isinstance(input_data, list):
            # List variations - remove each element
            for i in range(len(input_data)):
                variations.append(input_data[:i] + input_data[i + 1 :])
            # Also try first/second half
            mid = len(input_data) // 2
            variations.extend([input_data[:mid], input_data[mid:]])

        return [v for v in variations if v]  # Filter empty

    def _remove_markdown(self, text: str) -> str:
        """Strip markdown formatting."""
        # Remove code blocks
        text = re.sub(r"```.*?```", "", text, flags=re.DOTALL)
        # Remove inline code
        text = re.sub(r"`[^`]+`", "", text)
        # Remove headers
        text = re.sub(r"^#+\s*", "", text, flags=re.MULTILINE)
        # Remove bold/italic
        text = re.sub(r"\*+([^*]+)\*+", r"\1", text)
        return text.strip()

    def _simplify_nesting(self, text: str) -> str:
        """Flatten nested structures."""
        # Remove nested brackets/braces
        while re.search(r"\[\[[^\]]+\]\]", text):
            text = re.sub(r"\[\[([^\]]+)\]\]", r"[\1]", text)
        while re.search(r"\{\{[^}]+\}\}", text):
            text = re.sub(r"\{\{([^}]+)\}\}", r"{\1}", text)
        return text

    def _diff_inputs(self, passing: Any, failing: Any) -> str:
        """Find the difference between passing and failing input."""
        str_pass = str(passing)
        str_fail = str(failing)

        # Find common prefix
        common_prefix = 0
        for i, (a, b) in enumerate(zip(str_pass, str_fail)):
            if a == b:
                common_prefix = i + 1
            else:
                break

        # Find common suffix
        common_suffix = 0
        for i, (a, b) in enumerate(zip(reversed(str_pass), reversed(str_fail))):
            if a == b:
                common_suffix = i + 1
            else:
                break

        # The difference is in the middle
        diff_pass = str_pass[common_prefix : len(str_pass) - common_suffix or None]
        diff_fail = str_fail[common_prefix : len(str_fail) - common_suffix or None]

        if diff_pass and diff_fail:
            return f"Failure triggered by: '{diff_fail}' (was '{diff_pass}')"
        elif diff_fail:
            return f"Failure triggered by presence of: '{diff_fail}'"
        elif diff_pass:
            return f"Failure triggered by absence of: '{diff_pass}'"
        else:
            return "Inputs are identical - non-deterministic failure"

    async def counterfactual_query(
        self,
        test_id: str,
        intervention: dict[str, Any],
    ) -> CounterfactualResult:
        """Ask: "What would have happened if...?"

        Args:
            test_id: Test to query about
            intervention: Counterfactual conditions (e.g., {"prompt_template": "v2"})

        Returns:
            CounterfactualResult with predicted outcome
        """
        # Find historical runs matching the counterfactual scenario
        historical = await self.store.query(test_id=test_id, limit=1000)

        if not historical:
            return CounterfactualResult(
                query=intervention,
                answer="No historical data for this test",
                confidence=0.0,
            )

        # Filter to runs matching intervention criteria
        matching = []
        for w in historical:
            matches = True
            for key, value in intervention.items():
                witness_val = getattr(w, key, None)
                if witness_val is None:
                    witness_val = w.system_metrics.get(key)
                if witness_val != value:
                    matches = False
                    break
            if matches:
                matching.append(w)

        if not matching:
            return CounterfactualResult(
                query=intervention,
                answer="No historical data matches this counterfactual",
                confidence=0.0,
            )

        # Calculate outcome distribution under intervention
        pass_count = sum(1 for w in matching if w.outcome == "pass")
        pass_rate = pass_count / len(matching)

        return CounterfactualResult(
            query=intervention,
            answer=f"Under these conditions, pass rate was {pass_rate:.1%}",
            confidence=min(len(matching) / 100, 1.0),
            supporting_evidence=matching[:5],
        )

    async def root_cause_analysis(self, test_id: str) -> CausalGraph:
        """Build causal graph of failure factors.

        Args:
            test_id: Test to analyze

        Returns:
            CausalGraph with root cause identification
        """
        failures = await self.store.query(test_id=test_id, outcome="fail", limit=500)
        passes = await self.store.query(test_id=test_id, outcome="pass", limit=500)

        if not failures or not passes:
            return CausalGraph(nodes=[], edges=[], root_cause=None)

        # Extract features that differ between pass/fail
        fail_features = self._extract_features(failures)
        pass_features = self._extract_features(passes)

        # Statistical test for each feature
        causal_factors = []
        for feature in fail_features.keys():
            if feature in pass_features:
                p_value = self._chi_squared_test(
                    fail_features[feature],
                    pass_features[feature],
                )
                if p_value < 0.05:  # Significant
                    causal_factors.append(
                        CausalFactor(
                            feature=feature,
                            fail_distribution=fail_features[feature],
                            pass_distribution=pass_features[feature],
                            p_value=p_value,
                        )
                    )

        # Sort by significance
        causal_factors.sort(key=lambda f: f.p_value)

        # Build causal graph edges (simplified)
        edges = []
        for i, factor in enumerate(causal_factors):
            if i > 0:
                # More significant factors cause less significant ones
                edges.append((causal_factors[0].feature, factor.feature, 1 - factor.p_value))

        return CausalGraph(
            nodes=[f.feature for f in causal_factors],
            edges=edges,
            root_cause=causal_factors[0] if causal_factors else None,
        )

    def _extract_features(self, witnesses: list[TestWitness]) -> dict[str, dict[str, int]]:
        """Extract features from witnesses for causal analysis."""
        features: dict[str, dict[str, int]] = {}

        for w in witnesses:
            # Duration bucket
            duration_bucket = str(int(w.duration_ms / 100) * 100)
            features.setdefault("duration_bucket", {})
            features["duration_bucket"][duration_bucket] = (
                features["duration_bucket"].get(duration_bucket, 0) + 1
            )

            # Input length bucket
            input_len = len(str(w.input_data))
            len_bucket = str(input_len // 100 * 100)
            features.setdefault("input_length_bucket", {})
            features["input_length_bucket"][len_bucket] = (
                features["input_length_bucket"].get(len_bucket, 0) + 1
            )

            # Agent path length
            path_len = str(len(w.agent_path))
            features.setdefault("agent_path_length", {})
            features["agent_path_length"][path_len] = (
                features["agent_path_length"].get(path_len, 0) + 1
            )

            # Commit hash
            features.setdefault("commit", {})
            features["commit"][w.commit_hash or "unknown"] = (
                features["commit"].get(w.commit_hash or "unknown", 0) + 1
            )

        return features

    def _chi_squared_test(self, dist_a: dict[str, int], dist_b: dict[str, int]) -> float:
        """Simplified chi-squared test for independence.

        Returns p-value (lower = more significant difference).
        """
        all_keys = set(dist_a.keys()) | set(dist_b.keys())
        if not all_keys:
            return 1.0

        total_a = sum(dist_a.values())
        total_b = sum(dist_b.values())
        total = total_a + total_b

        if total == 0:
            return 1.0

        chi_sq = 0.0
        for key in all_keys:
            observed_a = dist_a.get(key, 0)
            observed_b = dist_b.get(key, 0)
            expected = (observed_a + observed_b) * (total_a / total)
            if expected > 0:
                chi_sq += (observed_a - expected) ** 2 / expected

        # Simplified p-value from chi-squared
        # (would normally use scipy.stats.chi2.sf)
        df = len(all_keys) - 1
        if df <= 0:
            return 1.0

        # Rough approximation
        p_value = math.exp(-chi_sq / 2)
        return min(1.0, max(0.0, p_value))

    async def flakiness_diagnosis(self, test_id: str) -> FlakinessDiagnosis:
        """Diagnose WHY a test is flaky, not just that it is.

        Args:
            test_id: Test to diagnose

        Returns:
            FlakinessDiagnosis with cause identification
        """
        runs = await self.store.query(test_id=test_id, limit=200)

        if len(runs) < 5:
            return FlakinessDiagnosis(
                entropy=0.0,
                diagnosis="Insufficient data",
                cause=None,
            )

        # Calculate entropy
        outcomes = [r.outcome for r in runs]
        entropy = self._calculate_entropy(outcomes)

        if entropy < 0.1:
            return FlakinessDiagnosis(
                entropy=entropy,
                diagnosis="Deterministic - low entropy",
                cause=None,
            )

        # Cluster failures by characteristics
        fail_runs = [r for r in runs if r.outcome == "fail"]

        if not fail_runs:
            return FlakinessDiagnosis(
                entropy=entropy,
                diagnosis="High entropy but no recent failures",
                cause="Unknown",
            )

        # Check for temporal patterns
        temporal_pattern = self._detect_temporal_pattern(fail_runs)
        if temporal_pattern:
            return FlakinessDiagnosis(
                entropy=entropy,
                diagnosis=f"Time-correlated: {temporal_pattern}",
                cause="Resource contention or time-dependent behavior",
            )

        # Check for input patterns
        input_pattern = self._detect_input_pattern(fail_runs)
        if input_pattern:
            return FlakinessDiagnosis(
                entropy=entropy,
                diagnosis=f"Input-correlated: {input_pattern}",
                cause="Edge case in input space",
            )

        return FlakinessDiagnosis(
            entropy=entropy,
            diagnosis="True randomness",
            cause="Non-deterministic agent behavior",
        )

    def _calculate_entropy(self, outcomes: Sequence[str]) -> float:
        """Calculate Shannon entropy of outcome distribution."""
        if not outcomes:
            return 0.0

        counts: dict[str, int] = {}
        for o in outcomes:
            counts[o] = counts.get(o, 0) + 1

        total = len(outcomes)
        entropy = 0.0
        for count in counts.values():
            if count > 0:
                p = count / total
                entropy -= p * math.log2(p)

        return entropy

    def _detect_temporal_pattern(self, fail_runs: list[TestWitness]) -> str | None:
        """Detect time-based patterns in failures."""
        if len(fail_runs) < 3:
            return None

        # Check for time clustering
        timestamps = [r.timestamp for r in fail_runs]
        timestamps.sort()

        # Check for same-hour clustering
        hours = [t.hour for t in timestamps]
        hour_counts: dict[int, int] = {}
        for h in hours:
            hour_counts[h] = hour_counts.get(h, 0) + 1

        max_hour_count = max(hour_counts.values())
        if max_hour_count >= len(fail_runs) * 0.6:
            peak_hour = max(hour_counts, key=hour_counts.get)  # type: ignore
            return f"Failures cluster at hour {peak_hour}"

        return None

    def _detect_input_pattern(self, fail_runs: list[TestWitness]) -> str | None:
        """Detect input-based patterns in failures."""
        if len(fail_runs) < 3:
            return None

        # Check for input length patterns
        lengths = [len(str(r.input_data)) for r in fail_runs]
        sum(lengths) / len(lengths)

        # Check if failures cluster around certain length
        short_fails = sum(1 for l in lengths if l < 100)
        long_fails = sum(1 for l in lengths if l > 1000)

        if short_fails >= len(lengths) * 0.6:
            return "Failures cluster on short inputs"
        if long_fails >= len(lengths) * 0.6:
            return "Failures cluster on long inputs"

        return None


# =============================================================================
# Report Generation
# =============================================================================


def format_analyst_report(
    delta_results: list[DeltaDebugResult],
    counterfactual_results: list[CounterfactualResult],
    causal_graphs: list[CausalGraph],
    flakiness_diagnoses: list[FlakinessDiagnosis],
) -> str:
    """Format Analyst report for display."""
    lines = [
        "=" * 60,
        "               ANALYST CAUSAL REPORT                    ",
        "=" * 60,
    ]

    if delta_results:
        lines.append(" DELTA DEBUGGING RESULTS:")
        for delta_r in delta_results:
            lines.append(f"   Cause: {delta_r.isolated_cause}")
            lines.append(f"   Confidence: {delta_r.confidence:.2f}")
            lines.append("")

    if counterfactual_results:
        lines.append(" COUNTERFACTUAL QUERIES:")
        for cf_r in counterfactual_results:
            lines.append(f"   Q: {cf_r.query}")
            lines.append(f"   A: {cf_r.answer}")
            lines.append(f"   Confidence: {cf_r.confidence:.2f}")
            lines.append("")

    if causal_graphs:
        lines.append(" CAUSAL ANALYSIS:")
        for g in causal_graphs:
            if g.root_cause:
                lines.append(f"   Root cause: {g.root_cause.feature}")
                lines.append(f"   p-value: {g.root_cause.p_value:.4f}")
            lines.append("")

    if flakiness_diagnoses:
        lines.append(" FLAKINESS DIAGNOSIS:")
        for d in flakiness_diagnoses:
            lines.append(f"   Entropy: {d.entropy:.2f}")
            lines.append(f"   Diagnosis: {d.diagnosis}")
            lines.append(f"   Cause: {d.cause}")
            lines.append("")

    lines.append("=" * 60)
    return "\n".join(lines)
