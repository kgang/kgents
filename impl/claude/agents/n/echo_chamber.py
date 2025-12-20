"""
N-gent Echo Chamber: Replay Simulation.

The Echo Chamber replays past executions via "echoes" - not exact replays,
but simulations that acknowledge LLM non-ergodicity.

Philosophy:
    LLMs are Non-Ergodic. Even with temperature=0, floating-point
    non-determinism makes "exact" replay a myth.

    We don't "resurrect" the dead. We create Echoes.
    Echoes are similar to the original, but not identical.

Components:
    - EchoMode: STRICT (use stored output) vs LUCID (re-execute)
    - Echo: A simulation of a past trace
    - EchoChamber: The replay engine with step navigation
    - LucidDreamer: Counterfactual exploration via modified inputs
    - DriftReport: Tracks semantic drift over time
"""

from __future__ import annotations

import json
from dataclasses import dataclass, field
from datetime import datetime, timezone
from enum import Enum
from typing import Any, Protocol, runtime_checkable

from .types import Determinism, SemanticTrace


class EchoMode(Enum):
    """
    How to handle traces during replay.

    STRICT: Return stored output exactly. Perfect reproduction, but brittle.
    LUCID: Re-execute with stored input. Allows drift detection.
    """

    STRICT = "strict"
    LUCID = "lucid"


@dataclass
class Echo:
    """
    An echo of a past execution.

    NOT the original. A simulation. A shadow of a shadow.

    Attributes:
        original_trace: The crystal being echoed
        echo_output: The output from this echo (may differ from original)
        mode: How this echo was created
        drift: Semantic distance from original (0.0 = identical, 1.0 = unrelated)
        echo_timestamp: When this echo was created
    """

    original_trace: SemanticTrace
    echo_output: dict[str, Any]
    mode: EchoMode
    drift: float | None = None
    echo_timestamp: datetime = field(default_factory=lambda: datetime.now(timezone.utc))

    @property
    def trace_id(self) -> str:
        """Get the original trace ID."""
        return self.original_trace.trace_id

    @property
    def is_identical(self) -> bool:
        """Check if echo output matches original exactly."""
        return self.echo_output == self.original_trace.outputs

    @property
    def drifted(self) -> bool:
        """Check if significant drift occurred."""
        return self.drift is not None and self.drift > 0.1

    def to_dict(self) -> dict[str, Any]:
        """Convert to dictionary for serialization."""
        return {
            "original_trace_id": self.original_trace.trace_id,
            "echo_output": self.echo_output,
            "mode": self.mode.value,
            "drift": self.drift,
            "echo_timestamp": self.echo_timestamp.isoformat(),
        }


@runtime_checkable
class AgentRegistry(Protocol):
    """Protocol for retrieving agents by ID for replay."""

    def get_agent(self, agent_id: str) -> Any | None:
        """Get an agent by ID for replay."""
        ...


@runtime_checkable
class DriftMeasurer(Protocol):
    """Protocol for measuring semantic drift between outputs."""

    def measure(self, original: dict[str, Any], echo: dict[str, Any]) -> float:
        """
        Measure drift between original and echo outputs.

        Returns:
            Float between 0.0 (identical) and 1.0 (completely different)
        """
        ...


class SimpleDriftMeasurer:
    """
    Simple drift measurement using structural comparison.

    For production, use L-gent embedding-based similarity.
    """

    def measure(self, original: dict[str, Any], echo: dict[str, Any]) -> float:
        """Measure drift via structural comparison."""
        if original == echo:
            return 0.0

        # Serialize and compare lengths as rough proxy
        orig_str = json.dumps(original, sort_keys=True, default=str)
        echo_str = json.dumps(echo, sort_keys=True, default=str)

        # Levenshtein-like ratio (simplified)
        max_len = max(len(orig_str), len(echo_str))
        if max_len == 0:
            return 0.0

        # Count matching characters at same positions
        min_len = min(len(orig_str), len(echo_str))
        matches = sum(1 for i in range(min_len) if orig_str[i] == echo_str[i])

        return 1.0 - (matches / max_len)


class EchoChamber:
    """
    The replay engine.

    Navigate through past traces and create echoes.
    Supports forward/backward stepping and echo generation.

    Usage:
        chamber = EchoChamber(traces)

        # Step through traces
        trace = chamber.step_forward()

        # Create an echo
        echo = await chamber.echo_from(trace, mode=EchoMode.LUCID)

        # Check for drift
        if echo.drifted:
            print(f"Drift detected: {echo.drift}")
    """

    def __init__(
        self,
        traces: list[SemanticTrace],
        agent_registry: AgentRegistry | None = None,
        drift_measurer: DriftMeasurer | None = None,
    ):
        """
        Initialize the Echo Chamber.

        Args:
            traces: The traces to replay
            agent_registry: Registry to retrieve agents for LUCID mode
            drift_measurer: Measurer for semantic drift (default: SimpleDriftMeasurer)
        """
        self.traces = sorted(traces, key=lambda t: t.timestamp)
        self.agent_registry = agent_registry
        self.drift_measurer = drift_measurer or SimpleDriftMeasurer()
        self.position = 0
        self.echoes: list[Echo] = []

    @property
    def current_trace(self) -> SemanticTrace | None:
        """Get the trace at current position."""
        if 0 <= self.position < len(self.traces):
            return self.traces[self.position]
        return None

    @property
    def at_start(self) -> bool:
        """Check if at the start of traces."""
        return self.position == 0

    @property
    def at_end(self) -> bool:
        """Check if at the end of traces."""
        return self.position >= len(self.traces) - 1

    @property
    def progress(self) -> float:
        """Get progress through traces (0.0 to 1.0)."""
        if not self.traces:
            return 1.0
        return self.position / len(self.traces)

    def step_forward(self) -> SemanticTrace | None:
        """Advance one step through the crystals."""
        if self.position >= len(self.traces):
            return None
        trace = self.traces[self.position]
        self.position += 1
        return trace

    def step_backward(self) -> SemanticTrace | None:
        """Rewind one step."""
        self.position = max(0, self.position - 1)
        return self.traces[self.position] if self.traces else None

    def seek(self, position: int) -> SemanticTrace | None:
        """Jump to a specific position."""
        self.position = max(0, min(position, len(self.traces) - 1))
        return self.current_trace

    def seek_to_trace(self, trace_id: str) -> SemanticTrace | None:
        """Jump to a specific trace by ID."""
        for i, trace in enumerate(self.traces):
            if trace.trace_id == trace_id:
                self.position = i
                return trace
        return None

    def reset(self) -> None:
        """Reset to the beginning."""
        self.position = 0
        self.echoes.clear()

    async def echo_from(
        self,
        trace: SemanticTrace,
        mode: EchoMode = EchoMode.STRICT,
    ) -> Echo:
        """
        Create an echo of a trace.

        Args:
            trace: The trace to echo
            mode: STRICT (use stored output) or LUCID (re-execute)

        Returns:
            An Echo with the output and drift measurement
        """
        if mode == EchoMode.STRICT:
            return Echo(
                original_trace=trace,
                echo_output=trace.outputs or {},
                mode=mode,
                drift=0.0,
            )

        # LUCID mode: behavior depends on determinism
        return await self._lucid_echo(trace)

    async def _lucid_echo(self, trace: SemanticTrace) -> Echo:
        """Create a lucid echo by re-executing or analyzing."""
        match trace.determinism:
            case Determinism.DETERMINISTIC:
                # Deterministic traces can be safely re-run
                echo_output = await self._replay_deterministic(trace)
                return Echo(
                    original_trace=trace,
                    echo_output=echo_output,
                    mode=EchoMode.LUCID,
                    drift=0.0,  # Should be identical
                )

            case Determinism.PROBABILISTIC:
                # LLM calls will drift
                echo_output = await self._replay_probabilistic(trace)
                drift = self.drift_measurer.measure(trace.outputs or {}, echo_output)
                return Echo(
                    original_trace=trace,
                    echo_output=echo_output,
                    mode=EchoMode.LUCID,
                    drift=drift,
                )

            case Determinism.CHAOTIC:
                # External APIs cannot be safely replayed
                # Fall back to STRICT mode
                return Echo(
                    original_trace=trace,
                    echo_output=trace.outputs or {},
                    mode=EchoMode.STRICT,  # Forced to strict
                    drift=None,  # Unknown
                )

    async def _replay_deterministic(self, trace: SemanticTrace) -> dict[str, Any]:
        """
        Replay a deterministic trace.

        For now, just return the stored output (should be identical).
        In production, actually re-execute the operation.
        """
        if self.agent_registry:
            agent = self.agent_registry.get_agent(trace.agent_id)
            if agent and hasattr(agent, "invoke"):
                input_data = self._deserialize_input(trace)
                try:
                    result = await agent.invoke(input_data)
                    return result if isinstance(result, dict) else {"result": result}
                except Exception as e:
                    return {"error": str(e), "type": type(e).__name__}

        # Fallback: return stored output
        return trace.outputs or {}

    async def _replay_probabilistic(self, trace: SemanticTrace) -> dict[str, Any]:
        """
        Replay a probabilistic trace (LLM call).

        Will drift from original due to non-determinism.
        """
        if self.agent_registry:
            agent = self.agent_registry.get_agent(trace.agent_id)
            if agent and hasattr(agent, "invoke"):
                input_data = self._deserialize_input(trace)
                try:
                    result = await agent.invoke(input_data)
                    return result if isinstance(result, dict) else {"result": result}
                except Exception as e:
                    return {"error": str(e), "type": type(e).__name__}

        # Fallback: return stored output
        return trace.outputs or {}

    def _deserialize_input(self, trace: SemanticTrace) -> Any:
        """Deserialize the input snapshot."""
        try:
            return json.loads(trace.input_snapshot.decode("utf-8"))
        except (json.JSONDecodeError, UnicodeDecodeError):
            return trace.inputs

    async def replay_all(
        self,
        mode: EchoMode = EchoMode.STRICT,
        stop_on_drift: float | None = None,
    ) -> list[Echo]:
        """
        Replay all traces and collect echoes.

        Args:
            mode: Echo mode for all traces
            stop_on_drift: Stop if drift exceeds this threshold

        Returns:
            List of echoes for all traces
        """
        self.reset()
        echoes: list[Echo] = []

        while trace := self.step_forward():
            echo = await self.echo_from(trace, mode)
            echoes.append(echo)

            if stop_on_drift and echo.drift and echo.drift > stop_on_drift:
                break

        self.echoes = echoes
        return echoes


@dataclass
class DriftReport:
    """
    Report on semantic drift for a trace.

    Used for tracking model behavior changes over time.
    """

    trace: SemanticTrace
    drift: float
    original_output: dict[str, Any]
    current_output: dict[str, Any]
    report_timestamp: datetime = field(default_factory=lambda: datetime.now(timezone.utc))

    @property
    def significant(self) -> bool:
        """Check if drift is significant (> 10%)."""
        return self.drift > 0.1

    @property
    def critical(self) -> bool:
        """Check if drift is critical (> 50%)."""
        return self.drift > 0.5


@dataclass
class CounterfactualResult:
    """
    Result of a counterfactual experiment.

    Compares what happened vs what might have happened.
    """

    original_echo: Echo
    variant_echo: Echo
    modified_input: Any
    divergence: float  # How different are the outcomes?

    @property
    def outcomes_similar(self) -> bool:
        """Check if outcomes are similar despite input change."""
        return self.divergence < 0.1

    @property
    def outcomes_divergent(self) -> bool:
        """Check if outcomes diverged significantly."""
        return self.divergence > 0.5


class LucidDreamer:
    """
    Explore counterfactuals through lucid echoes.

    "What if the input had been different?"
    "What if we used a different model?"
    "Is our agent behaving differently now than last month?"

    Usage:
        dreamer = LucidDreamer(agent_registry, drift_measurer)

        # Explore a counterfactual
        result = await dreamer.dream_variant(
            trace,
            modified_input={"prompt": "different prompt"}
        )

        # Detect drift over time
        reports = await dreamer.detect_drift_over_time(traces)
    """

    def __init__(
        self,
        agent_registry: AgentRegistry | None = None,
        drift_measurer: DriftMeasurer | None = None,
    ):
        """
        Initialize the LucidDreamer.

        Args:
            agent_registry: Registry to retrieve agents for re-execution
            drift_measurer: Measurer for semantic drift
        """
        self.agent_registry = agent_registry
        self.drift_measurer = drift_measurer or SimpleDriftMeasurer()

    async def dream_variant(
        self,
        trace: SemanticTrace,
        modified_input: Any,
    ) -> CounterfactualResult:
        """
        Compare: What happened vs What might have happened.

        Args:
            trace: The original trace
            modified_input: The alternative input to try

        Returns:
            CounterfactualResult comparing original and variant
        """
        chamber = EchoChamber(
            [trace],
            agent_registry=self.agent_registry,
            drift_measurer=self.drift_measurer,
        )

        # Original echo (lucid mode)
        original_echo = await chamber.echo_from(trace, EchoMode.LUCID)

        # Modified trace with new input
        modified_trace = self._modify_trace(trace, modified_input)

        # Variant echo
        variant_echo = await chamber.echo_from(modified_trace, EchoMode.LUCID)

        # Measure divergence between outcomes
        divergence = self.drift_measurer.measure(
            original_echo.echo_output,
            variant_echo.echo_output,
        )

        return CounterfactualResult(
            original_echo=original_echo,
            variant_echo=variant_echo,
            modified_input=modified_input,
            divergence=divergence,
        )

    async def detect_drift_over_time(
        self,
        traces: list[SemanticTrace],
        interval: int = 10,
        threshold: float = 0.1,
    ) -> list[DriftReport]:
        """
        Re-run old traces to detect model drift.

        Useful for: "Is our agent behaving differently now
        than it did last month?"

        Args:
            traces: Historical traces to check
            interval: Sample every N traces (for efficiency)
            threshold: Minimum drift to report

        Returns:
            List of DriftReports for traces with significant drift
        """
        reports: list[DriftReport] = []

        for trace in traces[::interval]:
            chamber = EchoChamber(
                [trace],
                agent_registry=self.agent_registry,
                drift_measurer=self.drift_measurer,
            )

            echo = await chamber.echo_from(trace, EchoMode.LUCID)

            if echo.drift is not None and echo.drift >= threshold:
                reports.append(
                    DriftReport(
                        trace=trace,
                        drift=echo.drift,
                        original_output=trace.outputs or {},
                        current_output=echo.echo_output,
                    )
                )

        return reports

    async def compare_models(
        self,
        trace: SemanticTrace,
        model_agents: dict[str, Any],
    ) -> dict[str, Echo]:
        """
        Run the same input through different models.

        Useful for comparing model behavior.

        Args:
            trace: The trace to replay
            model_agents: Dict of model_name -> agent

        Returns:
            Dict of model_name -> Echo
        """
        results: dict[str, Echo] = {}

        for model_name, agent in model_agents.items():
            # Create a temporary registry for this agent
            class TempRegistry:
                def get_agent(self, agent_id: str) -> Any:
                    return agent

            chamber = EchoChamber(
                [trace],
                agent_registry=TempRegistry(),
                drift_measurer=self.drift_measurer,
            )

            echo = await chamber.echo_from(trace, EchoMode.LUCID)
            results[model_name] = echo

        return results

    async def sensitivity_analysis(
        self,
        trace: SemanticTrace,
        input_variations: list[dict[str, Any]],
    ) -> list[CounterfactualResult]:
        """
        Analyze how sensitive output is to input variations.

        Args:
            trace: The base trace
            input_variations: List of input modifications to try

        Returns:
            List of CounterfactualResults for each variation
        """
        results: list[CounterfactualResult] = []

        for modified_input in input_variations:
            result = await self.dream_variant(trace, modified_input)
            results.append(result)

        return results

    def _modify_trace(
        self,
        trace: SemanticTrace,
        modified_input: Any,
    ) -> SemanticTrace:
        """Create a modified trace with new input."""
        # Serialize the modified input
        modified_snapshot = json.dumps(modified_input, sort_keys=True, default=str).encode("utf-8")

        # Create new inputs dict
        if isinstance(modified_input, dict):
            new_inputs = modified_input
        else:
            new_inputs = {"value": modified_input}

        # Use dataclass replace equivalent (frozen dataclass)
        return SemanticTrace(
            trace_id=trace.trace_id,
            parent_id=trace.parent_id,
            timestamp=trace.timestamp,
            agent_id=trace.agent_id,
            agent_genus=trace.agent_genus,
            action=trace.action,
            inputs=new_inputs,
            outputs=trace.outputs,
            input_hash=f"modified_{trace.input_hash}",
            input_snapshot=modified_snapshot,
            output_hash=trace.output_hash,
            gas_consumed=trace.gas_consumed,
            duration_ms=trace.duration_ms,
            vector=trace.vector,
            determinism=trace.determinism,
            metadata=trace.metadata,
        )


# Convenience function for quick drift checks
async def quick_drift_check(
    traces: list[SemanticTrace],
    agent_registry: AgentRegistry | None = None,
) -> tuple[int, int]:
    """
    Quick check for drift in a set of traces.

    Returns:
        Tuple of (total_traces, drifted_traces)
    """
    dreamer = LucidDreamer(agent_registry=agent_registry)
    reports = await dreamer.detect_drift_over_time(traces, interval=1)
    return len(traces), len(reports)
