"""
Cognitive Probes - LLM health checks beyond HTTP 200.

The test of a cognitive system is not whether it responds,
but whether it understands.

These probes verify that:
1. The LLM runtime is reachable (liveness)
2. The LLM can reason correctly (cognitive health)
3. AGENTESE paths resolve properly (path health)

Usage:
    from infra.cortex.probes import CognitiveProbe, probe_runtime

    probe = CognitiveProbe()
    result = await probe.check(runtime)

    # Or quick check
    healthy = await probe_runtime(runtime)
"""

from __future__ import annotations

import asyncio
import time
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from typing import TYPE_CHECKING, Any, Protocol, runtime_checkable

if TYPE_CHECKING:
    from runtime.base import Runtime


class ProbeStatus(Enum):
    """Probe result status."""

    HEALTHY = "healthy"
    DEGRADED = "degraded"
    UNHEALTHY = "unhealthy"
    TIMEOUT = "timeout"
    ERROR = "error"


@dataclass
class ProbeResult:
    """Result of a cognitive probe."""

    status: ProbeStatus
    latency_ms: float
    message: str = ""
    details: dict[str, Any] = field(default_factory=dict)
    timestamp: str = field(default_factory=lambda: datetime.now().isoformat())

    @property
    def healthy(self) -> bool:
        """True if probe indicates health."""
        return self.status in (ProbeStatus.HEALTHY, ProbeStatus.DEGRADED)

    def to_dict(self) -> dict[str, Any]:
        """Convert to dictionary."""
        return {
            "status": self.status.value,
            "healthy": self.healthy,
            "latency_ms": self.latency_ms,
            "message": self.message,
            "details": self.details,
            "timestamp": self.timestamp,
        }


@runtime_checkable
class LLMRuntime(Protocol):
    """Protocol for LLM runtimes that support cognitive probes."""

    async def raw_completion(
        self,
        context: Any,
    ) -> tuple[str, dict[str, Any]]:
        """Execute a raw LLM completion."""
        ...


class CognitiveProbe:
    """
    LLM health check - not just HTTP 200.

    Verifies that the LLM can:
    1. Respond to prompts (liveness)
    2. Echo text correctly (basic reasoning)
    3. Follow simple instructions (cognitive health)

    The probe uses cheap, fast prompts to minimize cost while
    still validating actual LLM functionality.
    """

    def __init__(
        self,
        timeout: float = 30.0,
        degraded_threshold_ms: float = 5000.0,
    ):
        """
        Initialize cognitive probe.

        Args:
            timeout: Maximum time to wait for response (seconds)
            degraded_threshold_ms: Latency above this triggers degraded status
        """
        self._timeout = timeout
        self._degraded_threshold_ms = degraded_threshold_ms

    async def check(self, runtime: LLMRuntime) -> ProbeResult:
        """
        Run cognitive health check against runtime.

        Returns ProbeResult indicating health status.
        """
        # Import here to avoid circular deps
        from runtime.base import AgentContext

        start_time = time.perf_counter()

        # Simple echo probe - validates LLM can respond coherently
        context = AgentContext(
            system_prompt="You are a health check probe. Respond exactly as instructed.",
            messages=[
                {
                    "role": "user",
                    "content": "Reply with exactly the word: HEALTHY",
                }
            ],
            temperature=0.0,  # Deterministic for probe
            max_tokens=10,  # Minimal tokens for speed
        )

        try:
            response_text, metadata = await asyncio.wait_for(
                runtime.raw_completion(context),
                timeout=self._timeout,
            )

            latency_ms = (time.perf_counter() - start_time) * 1000

            # Validate response contains expected content
            response_lower = response_text.strip().lower()
            if "healthy" in response_lower:
                # Check if degraded due to latency
                if latency_ms > self._degraded_threshold_ms:
                    return ProbeResult(
                        status=ProbeStatus.DEGRADED,
                        latency_ms=latency_ms,
                        message=f"High latency: {latency_ms:.0f}ms",
                        details={
                            "response": response_text[:100],
                            "threshold_ms": self._degraded_threshold_ms,
                        },
                    )

                return ProbeResult(
                    status=ProbeStatus.HEALTHY,
                    latency_ms=latency_ms,
                    message="LLM responding correctly",
                    details={
                        "response": response_text[:100],
                        "model": metadata.get("model", "unknown"),
                    },
                )
            else:
                # LLM responded but incorrectly - degraded
                return ProbeResult(
                    status=ProbeStatus.DEGRADED,
                    latency_ms=latency_ms,
                    message="Unexpected response content",
                    details={
                        "expected": "HEALTHY",
                        "received": response_text[:100],
                    },
                )

        except asyncio.TimeoutError:
            latency_ms = (time.perf_counter() - start_time) * 1000
            return ProbeResult(
                status=ProbeStatus.TIMEOUT,
                latency_ms=latency_ms,
                message=f"Probe timed out after {self._timeout}s",
            )

        except Exception as e:
            latency_ms = (time.perf_counter() - start_time) * 1000
            return ProbeResult(
                status=ProbeStatus.ERROR,
                latency_ms=latency_ms,
                message=str(e),
                details={"error_type": type(e).__name__},
            )


class ReasoningProbe:
    """
    Deeper cognitive probe that validates reasoning ability.

    Use sparingly - more expensive than basic CognitiveProbe.
    """

    def __init__(
        self,
        timeout: float = 60.0,
    ):
        self._timeout = timeout

    async def check(self, runtime: LLMRuntime) -> ProbeResult:
        """
        Run reasoning validation against runtime.

        Tests simple arithmetic to verify reasoning capability.
        """
        from runtime.base import AgentContext

        start_time = time.perf_counter()

        # Simple arithmetic probe
        context = AgentContext(
            system_prompt="You are a math checker. Answer with just the number.",
            messages=[
                {
                    "role": "user",
                    "content": "What is 7 + 5? Reply with just the number.",
                }
            ],
            temperature=0.0,
            max_tokens=10,
        )

        try:
            response_text, metadata = await asyncio.wait_for(
                runtime.raw_completion(context),
                timeout=self._timeout,
            )

            latency_ms = (time.perf_counter() - start_time) * 1000

            # Check for correct answer
            if "12" in response_text:
                return ProbeResult(
                    status=ProbeStatus.HEALTHY,
                    latency_ms=latency_ms,
                    message="Reasoning validated",
                    details={
                        "test": "arithmetic",
                        "expected": "12",
                        "response": response_text[:50],
                    },
                )
            else:
                return ProbeResult(
                    status=ProbeStatus.DEGRADED,
                    latency_ms=latency_ms,
                    message="Incorrect reasoning result",
                    details={
                        "expected": "12",
                        "received": response_text[:50],
                    },
                )

        except asyncio.TimeoutError:
            latency_ms = (time.perf_counter() - start_time) * 1000
            return ProbeResult(
                status=ProbeStatus.TIMEOUT,
                latency_ms=latency_ms,
                message=f"Reasoning probe timed out after {self._timeout}s",
            )

        except Exception as e:
            latency_ms = (time.perf_counter() - start_time) * 1000
            return ProbeResult(
                status=ProbeStatus.ERROR,
                latency_ms=latency_ms,
                message=str(e),
            )


class PathProbe:
    """
    Probe that validates AGENTESE path resolution.

    Tests that the Cortex can resolve and execute AGENTESE paths
    with LLM backing.
    """

    def __init__(
        self,
        path: str = "concept.define",
        timeout: float = 30.0,
    ):
        """
        Initialize path probe.

        Args:
            path: AGENTESE path to test
            timeout: Maximum time to wait
        """
        self._path = path
        self._timeout = timeout

    async def check(self, cortex_servicer: Any) -> ProbeResult:
        """
        Run path resolution probe.

        Args:
            cortex_servicer: CortexServicer instance to test
        """
        start_time = time.perf_counter()

        try:
            # Create a simple invoke request
            @dataclass
            class InvokeRequest:
                path: str
                observer_dna: bytes = b""
                lens: str = "optics.identity"
                kwargs: dict[str, str] = field(default_factory=dict)

            request = InvokeRequest(
                path=self._path,
                kwargs={"term": "test"},
            )

            result = await asyncio.wait_for(
                cortex_servicer.Invoke(request),
                timeout=self._timeout,
            )

            latency_ms = (time.perf_counter() - start_time) * 1000

            # Check result
            if result.result is not None or result.result_json:
                # Check for error in result
                if "error" in str(result.result_json).lower():
                    return ProbeResult(
                        status=ProbeStatus.DEGRADED,
                        latency_ms=latency_ms,
                        message=f"Path {self._path} returned error",
                        details={
                            "path": self._path,
                            "result": result.result_json[:200],
                        },
                    )

                return ProbeResult(
                    status=ProbeStatus.HEALTHY,
                    latency_ms=latency_ms,
                    message=f"Path {self._path} resolved successfully",
                    details={
                        "path": self._path,
                        "duration_ms": result.duration_ms,
                    },
                )
            else:
                return ProbeResult(
                    status=ProbeStatus.UNHEALTHY,
                    latency_ms=latency_ms,
                    message=f"Path {self._path} returned empty result",
                )

        except asyncio.TimeoutError:
            latency_ms = (time.perf_counter() - start_time) * 1000
            return ProbeResult(
                status=ProbeStatus.TIMEOUT,
                latency_ms=latency_ms,
                message=f"Path probe timed out after {self._timeout}s",
            )

        except Exception as e:
            latency_ms = (time.perf_counter() - start_time) * 1000
            return ProbeResult(
                status=ProbeStatus.ERROR,
                latency_ms=latency_ms,
                message=str(e),
                details={"path": self._path},
            )


# =============================================================================
# Convenience Functions
# =============================================================================


async def probe_runtime(
    runtime: LLMRuntime,
    include_reasoning: bool = False,
) -> bool:
    """
    Quick health check of an LLM runtime.

    Args:
        runtime: Runtime to check
        include_reasoning: Also run reasoning probe (slower, more expensive)

    Returns:
        True if runtime is healthy
    """
    probe = CognitiveProbe()
    result = await probe.check(runtime)

    if not result.healthy:
        return False

    if include_reasoning:
        reasoning_probe = ReasoningProbe()
        reasoning_result = await reasoning_probe.check(runtime)
        return reasoning_result.healthy

    return True


async def full_probe_suite(
    runtime: LLMRuntime,
    cortex_servicer: Any | None = None,
) -> dict[str, ProbeResult]:
    """
    Run full probe suite against runtime and optionally cortex.

    Returns dict mapping probe name to result.
    """
    results: dict[str, ProbeResult] = {}

    # Run cognitive probe
    cognitive = CognitiveProbe()
    results["cognitive"] = await cognitive.check(runtime)

    # Run reasoning probe
    reasoning = ReasoningProbe()
    results["reasoning"] = await reasoning.check(runtime)

    # Run path probe if cortex available
    if cortex_servicer is not None:
        path = PathProbe()
        results["path"] = await path.check(cortex_servicer)

    return results


__all__ = [
    "CognitiveProbe",
    "ReasoningProbe",
    "PathProbe",
    "ProbeResult",
    "ProbeStatus",
    "probe_runtime",
    "full_probe_suite",
    "LLMRuntime",
]
