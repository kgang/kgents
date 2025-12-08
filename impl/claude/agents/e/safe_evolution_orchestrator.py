"""
SafeEvolutionOrchestrator: Orchestrate safe self-evolution with Bootstrap integration.

Extracted from evolve.py (H3) as part of Phase D polish.

This module implements the orchestration layer for safe self-evolution,
integrating Bootstrap agents (Ground, Judge, Fix, Contradict) with E-gents
safety checks.

Morphism: SafeEvolutionOrchestratorInput → SafeEvolutionOrchestratorResult

Philosophy:
> "Meta-evolution requires multiple safety layers orchestrated carefully."
"""

from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Optional, Callable

from bootstrap.types import Facts, VOID
from bootstrap.contradict import Contradict, ContradictInput, ContradictResult
from bootstrap.ground import Ground

from .safety import (
    SafetyConfig,
    SelfEvolutionAgent,
    SafeEvolutionInput,
    SafeEvolutionResult,
)
from .experiment import CodeModule


@dataclass(frozen=True)
class SafeEvolutionOrchestratorInput:
    """Input for SafeEvolutionOrchestrator."""

    target: str  # "meta", "bootstrap", "agents", or specific path
    safety_config: SafetyConfig
    dry_run: bool = True
    log_fn: Optional[Callable[[str], None]] = None


@dataclass
class SafeEvolutionOrchestratorResult:
    """Result from SafeEvolutionOrchestrator."""

    success: bool
    targets_processed: int
    targets_succeeded: int
    targets_failed: int
    results: list[tuple[Path, SafeEvolutionResult]] = field(default_factory=list)
    grounded_facts: Optional[Facts] = None
    error: Optional[str] = None


class SafeEvolutionOrchestrator:
    """
    Orchestrate safe self-evolution across multiple targets.

    Integrates Bootstrap agents for enhanced safety:
    1. Ground: Inject persona values into evolution
    2. Judge: Pre-filter hypotheses (handled in EvolutionPipeline)
    3. Fix: Convergence tracking (handled in SelfEvolutionAgent)
    4. Contradict: Detect tensions between old/new code

    Plus E-gents safety layers:
    - Chaosmonger stability checks
    - Syntax validation
    - Type checking (mypy)
    - Sandbox testing
    - Self-test (evolved code can still work)

    Usage:
        orchestrator = SafeEvolutionOrchestrator()
        result = await orchestrator.invoke(SafeEvolutionOrchestratorInput(
            target="meta",
            safety_config=SafetyConfig(dry_run=True),
            dry_run=True,
        ))
    """

    def __init__(self):
        """Initialize orchestrator with lazy-loaded Bootstrap agents."""
        self._ground: Optional[Ground] = None
        self._contradict: Optional[Contradict] = None

    def _log(self, msg: str, input: SafeEvolutionOrchestratorInput) -> None:
        """Log message using provided log function."""
        if input.log_fn:
            input.log_fn(msg)

    async def _get_grounded_context(self) -> Facts:
        """Get grounded context from Bootstrap Ground agent."""
        if self._ground is None:
            self._ground = Ground()
        return await self._ground.invoke(VOID)

    async def _detect_tensions(
        self,
        original_code: str,
        evolved_code: str,
        context: dict[str, Any],
    ) -> ContradictResult:
        """Detect tensions using Bootstrap Contradict agent."""
        if self._contradict is None:
            self._contradict = Contradict()
        return await self._contradict.invoke(
            ContradictInput(
                a=original_code,
                b=evolved_code,
                context=context,
            )
        )

    def _resolve_targets(self, target: str, base: Path) -> list[Path]:
        """
        Resolve target string to list of paths.

        Args:
            target: "meta", "bootstrap", "agents", or specific path
            base: Base directory (impl/claude)

        Returns:
            List of Path objects to evolve
        """
        if target == "meta":
            return [base / "evolve.py"]
        elif target == "bootstrap":
            return list((base / "bootstrap").glob("*.py"))
        elif target == "agents":
            targets = []
            for letter_dir in (base / "agents").iterdir():
                if letter_dir.is_dir() and not letter_dir.name.startswith("_"):
                    targets.extend(letter_dir.glob("*.py"))
            return targets
        else:
            # Assume it's a specific path
            path = Path(target)
            return [path] if path.exists() else []

    async def invoke(
        self, input: SafeEvolutionOrchestratorInput
    ) -> SafeEvolutionOrchestratorResult:
        """
        Orchestrate safe self-evolution.

        Steps:
        1. Get grounded context (persona values)
        2. Resolve targets
        3. For each target:
           a. Run SelfEvolutionAgent
           b. Detect tensions (Contradict)
           c. Log results
        4. Return summary

        Args:
            input: Orchestrator input with target and config

        Returns:
            Result with success status and details
        """
        self._log("=" * 60, input)
        self._log("SAFE SELF-EVOLUTION MODE (Bootstrap-Enhanced)", input)
        self._log("=" * 60, input)
        self._log(f"Target: {input.target}", input)
        self._log(
            f"Max iterations: {input.safety_config.max_iterations}", input
        )
        self._log(
            f"Convergence threshold: {input.safety_config.convergence_threshold}",
            input,
        )
        self._log(f"Dry run: {input.dry_run}", input)
        self._log("", input)

        # Step 1: Get grounded context
        try:
            facts = await self._get_grounded_context()
            self._log(
                f"📍 Grounded context: {facts.persona.name}'s preferences", input
            )
            self._log(
                f"   Values: {', '.join(facts.persona.values[:3])}...", input
            )
            self._log(f"   Style: {facts.persona.communication_style}", input)
            self._log("", input)
        except Exception as e:
            self._log(f"⚠️ Failed to load grounded context: {e}", input)
            facts = None

        # Step 2: Resolve targets
        base = Path(__file__).parent.parent  # agents/e/ -> impl/claude
        targets = self._resolve_targets(input.target, base)

        self._log(f"Targets: {len(targets)} files", input)
        for t in targets[:5]:
            self._log(f"  - {t.name}", input)
        if len(targets) > 5:
            self._log(f"  ... and {len(targets) - 5} more", input)
        self._log("", input)

        # Step 3: Process each target
        agent = SelfEvolutionAgent(config=input.safety_config)
        results: list[tuple[Path, SafeEvolutionResult]] = []
        succeeded = 0
        failed = 0

        for target in targets:
            self._log(f"\n{'='*60}", input)
            self._log(f"EVOLVING: {target.name}", input)
            self._log(f"{'='*60}", input)

            if not target.exists():
                self._log(f"  Skip: file not found", input)
                failed += 1
                continue

            original_code = target.read_text()
            self._log(
                f"  Original: {len(original_code.splitlines())} lines", input
            )

            # Run self-evolution
            result = await agent.invoke(
                SafeEvolutionInput(
                    target=target,
                    config=input.safety_config,
                )
            )

            results.append((target, result))

            if result.success:
                succeeded += 1
                self._log(f"  Status: SUCCESS", input)
                self._log(f"  Converged: {result.converged}", input)
                self._log(f"  Iterations: {result.iterations}", input)
                self._log(
                    f"  Final similarity: {result.final_similarity:.2%}", input
                )

                # Step 3b: Detect tensions
                if result.evolved_code and facts:
                    try:
                        tension_result = await self._detect_tensions(
                            original_code,
                            result.evolved_code,
                            context={
                                "target": target.name,
                                "persona": facts.persona.name,
                            },
                        )
                        if not tension_result.no_tension:
                            self._log(
                                f"  ⚠️ Tensions detected ({len(tension_result.tensions)}):",
                                input,
                            )
                            for tension in tension_result.tensions[:3]:
                                self._log(
                                    f"    • [{tension.mode.value}] {tension.description[:50]}...",
                                    input,
                                )
                        else:
                            self._log(
                                f"  ✓ No tensions detected between old/new code",
                                input,
                            )
                    except Exception as e:
                        self._log(
                            f"  ⚠️ Tension detection failed: {e}", input
                        )

                # Step 3c: Apply if not dry-run
                if result.evolved_code and not input.dry_run:
                    target.write_text(result.evolved_code)
                    self._log(
                        f"  Applied: {len(result.evolved_code.splitlines())} lines",
                        input,
                    )
                elif result.evolved_code:
                    self._log(
                        f"  (dry-run) Would write {len(result.evolved_code.splitlines())} lines",
                        input,
                    )
            else:
                failed += 1
                self._log(f"  Status: FAILED", input)
                self._log(f"  Error: {result.error}", input)

            # Show sandbox results
            if result.sandbox_results:
                self._log(
                    f"  Sandbox tests: {len(result.sandbox_results)}", input
                )
                for i, sr in enumerate(result.sandbox_results, 1):
                    status = "PASS" if sr.passed else "FAIL"
                    self._log(f"    [{i}] {status}", input)
                    if not sr.passed and sr.error:
                        self._log(
                            f"        Error: {sr.error[:80]}...", input
                        )

        # Step 4: Summary
        self._log(f"\n{'='*60}", input)
        self._log("SAFE SELF-EVOLUTION COMPLETE", input)
        self._log(f"{'='*60}", input)

        return SafeEvolutionOrchestratorResult(
            success=succeeded > 0,
            targets_processed=len(targets),
            targets_succeeded=succeeded,
            targets_failed=failed,
            results=results,
            grounded_facts=facts,
        )


# Convenience factory

def safe_evolution_orchestrator() -> SafeEvolutionOrchestrator:
    """Create a SafeEvolutionOrchestrator."""
    return SafeEvolutionOrchestrator()
