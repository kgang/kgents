"""
Chat-ASHC Integration Bridge

Connects chat spec editing with ASHC compilation for evidence accumulation.

When users edit specs through chat:
1. ASHC compiles the spec with adaptive Bayesian sampling
2. Accumulates evidence from verification runs
3. Returns equivalence scores to display in chat
4. Provides confidence in the edit

Philosophy:
    "The edit is not verified until ASHC says so. Evidence > intuition."

See: spec/protocols/ASHC-agentic-self-hosting-compiler.md
See: spec/protocols/chat-web.md §3.3
"""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Any

from protocols.ashc.adaptive import BetaPrior, ConfidenceTier, StoppingState
from protocols.ashc.evidence import ASHCOutput, EvidenceCompiler
from protocols.ashc.harness import VoidHarness, VoidHarnessConfig

# =============================================================================
# ASHC Output for Chat
# =============================================================================


@dataclass(frozen=True)
class ASHCChatOutput:
    """
    ASHC compilation output for chat display.

    Simplified from full ASHCOutput for chat UI consumption.
    """

    # Evidence metrics
    equivalence_score: float  # 0.0-1.0, spec↔impl equivalence
    is_verified: bool  # True if equivalence_score >= 0.8 and runs >= 10
    runs_completed: int
    runs_passed: int
    runs_total: int  # Max runs (may be > completed if stopped early)

    # Bayesian stopping state
    confidence: float  # Posterior mean (p of success)
    prior_alpha: float
    prior_beta: float
    stopping_decision: str  # "continue" | "stop_success" | "stop_failure" | "stop_uncertain"

    # Chaos stability (if available)
    chaos_stability: float | None = None

    @property
    def pass_rate(self) -> float:
        """Fraction of runs that passed (0.0-1.0)."""
        if self.runs_completed == 0:
            return 0.0
        return self.runs_passed / self.runs_completed

    def to_dict(self) -> dict[str, Any]:
        """Convert to dict for JSON serialization."""
        return {
            "equivalence_score": self.equivalence_score,
            "is_verified": self.is_verified,
            "runs_completed": self.runs_completed,
            "runs_passed": self.runs_passed,
            "runs_total": self.runs_total,
            "pass_rate": self.pass_rate,
            "confidence": self.confidence,
            "prior_alpha": self.prior_alpha,
            "prior_beta": self.prior_beta,
            "stopping_decision": self.stopping_decision,
            "chaos_stability": self.chaos_stability,
        }


# =============================================================================
# ASHC Bridge
# =============================================================================


class ASHCBridge:
    """
    Bridge between chat and ASHC compilation.

    Provides simplified interface for chat to trigger ASHC compilation
    when specs are edited.

    Usage:
        bridge = ASHCBridge()

        # When chat edits a spec file
        output = await bridge.compile_spec(
            spec_path="spec/agents/new.md",
            proposed_changes="Add @node decorator...",
            tier=ConfidenceTier.LIKELY_WORKS,
        )

        # Display in chat
        print(f"Equivalence: {output.equivalence_score:.2%}")
        print(f"Verified: {output.is_verified}")
    """

    def __init__(
        self,
        harness: VoidHarness | None = None,
        enable_compilation: bool = True,
    ):
        """
        Initialize ASHC bridge.

        Args:
            harness: VoidHarness for LLM generation (optional, uses default if None)
            enable_compilation: If False, skips compilation (for testing)
        """
        self._harness = harness
        self._enable_compilation = enable_compilation
        self._cache: dict[str, ASHCChatOutput] = {}  # Spec path -> cached output

    async def compile_spec(
        self,
        spec_path: str,
        proposed_changes: str,
        tier: ConfidenceTier = ConfidenceTier.LIKELY_WORKS,
        max_runs: int = 20,
        use_cache: bool = True,
    ) -> ASHCChatOutput:
        """
        Compile a spec with ASHC adaptive compilation.

        Args:
            spec_path: Path to spec file (e.g., "spec/agents/new.md")
            proposed_changes: The edited spec content
            tier: Confidence tier for prior (determines stopping config)
            max_runs: Maximum verification runs (adaptive may stop earlier)
            use_cache: If True, return cached output if available

        Returns:
            ASHCChatOutput with evidence and stopping state
        """
        # Check cache
        cache_key = f"{spec_path}:{hash(proposed_changes)}"
        if use_cache and cache_key in self._cache:
            return self._cache[cache_key]

        # If compilation disabled, return mock output
        if not self._enable_compilation:
            return self._mock_output(tier)

        # Initialize harness if needed
        if self._harness is None:
            self._harness = VoidHarness(
                VoidHarnessConfig(
                    timeout_seconds=60.0,
                    max_concurrent=3,
                    max_tokens=50_000,  # Reasonable budget for spec compilation
                )
            )

        # Set up adaptive compiler
        compiler = EvidenceCompiler(generate_fn=self._harness.generate)

        # Compile with adaptive stopping
        try:
            ashc_output = await compiler.compile(
                spec=proposed_changes,
                n_variations=max_runs,
                run_tests=True,
                run_types=True,
                run_lint=True,
                timeout=60.0,
            )

            # Convert to chat output
            output = self._convert_output(ashc_output, tier, max_runs)

            # Cache result
            self._cache[cache_key] = output

            return output

        except Exception as e:
            # On error, return failure output
            return ASHCChatOutput(
                equivalence_score=0.0,
                is_verified=False,
                runs_completed=0,
                runs_passed=0,
                runs_total=max_runs,
                confidence=0.0,
                prior_alpha=1.0,
                prior_beta=1.0,
                stopping_decision="stop_failure",
                chaos_stability=None,
            )

    def get_cached_evidence(self, spec_path: str) -> ASHCChatOutput | None:
        """
        Get cached ASHC evidence for a spec.

        Args:
            spec_path: Path to spec file

        Returns:
            Cached output if available, None otherwise
        """
        # Return first matching cache entry for this spec path
        for key, output in self._cache.items():
            if key.startswith(f"{spec_path}:"):
                return output
        return None

    def clear_cache(self, spec_path: str | None = None) -> None:
        """
        Clear cached evidence.

        Args:
            spec_path: If provided, clear only this spec's cache. Otherwise clear all.
        """
        if spec_path is None:
            self._cache.clear()
        else:
            # Remove all entries for this spec
            keys_to_remove = [k for k in self._cache if k.startswith(f"{spec_path}:")]
            for key in keys_to_remove:
                del self._cache[key]

    # =========================================================================
    # Internal Helpers
    # =========================================================================

    def _convert_output(
        self, ashc_output: ASHCOutput, tier: ConfidenceTier, max_runs: int
    ) -> ASHCChatOutput:
        """Convert full ASHCOutput to chat-friendly output."""
        evidence = ashc_output.evidence
        runs_completed = evidence.run_count
        runs_passed = evidence.pass_count

        # Build posterior from evidence
        prior = BetaPrior.from_confidence(tier)
        posterior = prior.update(successes=runs_passed, failures=runs_completed - runs_passed)

        # Determine stopping decision
        if ashc_output.is_verified:
            stopping_decision = "stop_success"
        elif runs_completed >= max_runs:
            stopping_decision = "stop_uncertain"
        elif evidence.pass_rate < 0.3:  # Low pass rate
            stopping_decision = "stop_failure"
        else:
            stopping_decision = "continue"

        return ASHCChatOutput(
            equivalence_score=evidence.equivalence_score,
            is_verified=ashc_output.is_verified,
            runs_completed=runs_completed,
            runs_passed=runs_passed,
            runs_total=max_runs,
            confidence=posterior.mean,
            prior_alpha=posterior.alpha,
            prior_beta=posterior.beta,
            stopping_decision=stopping_decision,
            chaos_stability=None,  # TODO: Add chaos testing later
        )

    def _mock_output(self, tier: ConfidenceTier) -> ASHCChatOutput:
        """Generate mock output for testing."""
        prior = BetaPrior.from_confidence(tier)
        return ASHCChatOutput(
            equivalence_score=prior.mean,
            is_verified=False,
            runs_completed=0,
            runs_passed=0,
            runs_total=10,
            confidence=prior.mean,
            prior_alpha=prior.alpha,
            prior_beta=prior.beta,
            stopping_decision="continue",
            chaos_stability=None,
        )


# =============================================================================
# Utility Functions
# =============================================================================


def is_spec_file(file_path: str) -> bool:
    """
    Check if a file path is a spec file.

    Spec files are in spec/ and end with .md.
    """
    path = Path(file_path)
    return "spec/" in file_path and path.suffix == ".md"


async def compile_spec_from_chat(
    spec_path: str,
    proposed_changes: str,
    tier: ConfidenceTier = ConfidenceTier.LIKELY_WORKS,
) -> ASHCChatOutput:
    """
    Convenience function to compile a spec from chat.

    Args:
        spec_path: Path to spec file
        proposed_changes: Edited spec content
        tier: Confidence tier

    Returns:
        ASHC compilation output
    """
    bridge = ASHCBridge()
    return await bridge.compile_spec(spec_path, proposed_changes, tier)


# =============================================================================
# Exports
# =============================================================================

__all__ = [
    "ASHCBridge",
    "ASHCChatOutput",
    "is_spec_file",
    "compile_spec_from_chat",
]
