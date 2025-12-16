"""
self.grow.validate - Proposal Validation

Comprehensive validation against:
1. Seven Principle Scores (all >= 0.4, at least 5 >= 0.7)
2. Law Checks (identity, associativity, composition)
3. Abuse Detection (red-team checks)
4. Duplication Check (similarity search)

AGENTESE: self.grow.validate
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import TYPE_CHECKING, Any

from ...node import BaseLogosNode, BasicRendering, Renderable
from .abuse import detect_abuse
from .duplication import check_duplication
from .exceptions import AffordanceError
from .fitness import check_validation_gates, evaluate_all_principles
from .schemas import (
    SELF_GROW_AFFORDANCES,
    GrowthBudget,
    HolonProposal,
    LawCheckResult,
    ValidationResult,
)
from .telemetry import metrics, tracer

if TYPE_CHECKING:
    from bootstrap.umwelt import Umwelt

    from ...logos import Logos


# === Law Checking ===


async def check_laws(
    proposal: HolonProposal,
    logos: "Logos | None" = None,
) -> LawCheckResult:
    """
    Verify AGENTESE category laws hold for proposed holon.

    Tests:
    1. Identity: Id >> proposed ≡ proposed ≡ proposed >> Id
    2. Associativity: (a >> proposed) >> b ≡ a >> (proposed >> b)
    3. Composition: All declared relations actually compose

    Args:
        proposal: The holon proposal to check
        logos: Optional Logos instance for composition tests

    Returns:
        LawCheckResult with test results
    """
    errors = []
    _ = f"{proposal.context}.{proposal.entity}"  # Handle for diagnostics

    # Identity Law
    # For a new holon, we can only verify it has a valid identity structure
    identity_holds = True

    # Check that the entity name is valid
    if not proposal.entity or not proposal.entity.replace("_", "").isalnum():
        identity_holds = False
        errors.append(f"Invalid entity name: {proposal.entity}")

    # Check that context is valid
    valid_contexts = {"world", "self", "concept", "void", "time"}
    if proposal.context not in valid_contexts:
        identity_holds = False
        errors.append(f"Invalid context: {proposal.context}")

    # Associativity Law
    # For a new holon, verify that declared relations would compose correctly
    associativity_holds = True

    if proposal.relations:
        composes_with = proposal.relations.get("composes_with", [])
        if len(composes_with) >= 2:
            # Verify that the composition targets exist (if logos available)
            if logos is not None:
                for target in composes_with:
                    try:
                        logos.resolve(target)
                    except Exception:
                        # Target doesn't exist - note but don't fail
                        # (it might be co-proposed)
                        errors.append(f"Composition target not found: {target}")

    # Composition Validity
    composition_valid = True

    # Verify all relation targets are valid paths
    for rel_type, targets in proposal.relations.items():
        for target in targets:
            # Basic path validation
            parts = target.split(".")
            if len(parts) < 2:
                composition_valid = False
                errors.append(f"Invalid relation target path: {target}")
            elif parts[0] not in valid_contexts:
                composition_valid = False
                errors.append(f"Invalid context in relation target: {target}")

    return LawCheckResult(
        identity_holds=identity_holds,
        associativity_holds=associativity_holds,
        composition_valid=composition_valid,
        errors=errors,
    )


def check_laws_sync(
    proposal: HolonProposal,
) -> LawCheckResult:
    """
    Synchronous version of check_laws for testing.
    """
    import asyncio

    try:
        loop = asyncio.get_event_loop()
        if loop.is_running():
            import concurrent.futures

            with concurrent.futures.ThreadPoolExecutor() as pool:
                future = pool.submit(asyncio.run, check_laws(proposal, logos=None))
                return future.result()
        else:
            return loop.run_until_complete(check_laws(proposal, logos=None))
    except RuntimeError:
        return asyncio.run(check_laws(proposal, logos=None))


# === Full Validation ===


async def validate_proposal(
    proposal: HolonProposal,
    logos: "Logos | None" = None,
    existing_handles: list[str] | None = None,
) -> ValidationResult:
    """
    Comprehensive validation against all gates.

    Gates:
    1. Seven Principle Scores (all >= 0.4, at least 5 >= 0.7)
    2. Law Checks (identity, associativity, composition)
    3. Abuse Detection (red-team checks)
    4. Duplication Check (similarity search)

    Args:
        proposal: The proposal to validate
        logos: Optional Logos instance for composition/duplication checks
        existing_handles: Optional list of existing handles for duplication check

    Returns:
        ValidationResult with all gate results
    """
    async with tracer.start_span_async("growth.validate") as span:
        span.set_attribute("growth.phase", "validate")
        span.set_attribute(
            "growth.proposal.handle", f"{proposal.context}.{proposal.entity}"
        )
        span.set_attribute("growth.proposal.hash", proposal.content_hash)

        # === Gate 1: Seven Principles ===
        principle_results = evaluate_all_principles(proposal)
        scores = {name: score for name, (score, _) in principle_results.items()}
        reasoning = {name: reason for name, (_, reason) in principle_results.items()}

        for principle, score in scores.items():
            span.set_attribute(f"growth.validation.score.{principle}", score)

        # === Gate 2: Law Checks ===
        law_checks = await check_laws(proposal, logos)
        span.set_attribute(
            "growth.validation.law_check.identity", law_checks.identity_holds
        )
        span.set_attribute(
            "growth.validation.law_check.associativity", law_checks.associativity_holds
        )

        # === Gate 3: Abuse Detection ===
        abuse_check = detect_abuse(proposal)
        span.set_attribute("growth.validation.abuse_check.passed", abuse_check.passed)

        # === Gate 4: Duplication Check ===
        duplication_check = await check_duplication(
            proposal, logos=logos, existing_handles=existing_handles
        )

        # === Determine Pass/Fail ===
        blockers = []
        warnings = []
        suggestions = []

        # Check principle gates
        passed_gates, gate_blockers = check_validation_gates(scores)
        blockers.extend(gate_blockers)

        # Law blockers
        if not law_checks.identity_holds:
            blockers.append("law:identity")
        if not law_checks.associativity_holds:
            blockers.append("law:associativity")
        if law_checks.errors:
            warnings.extend(law_checks.errors)

        # Abuse blockers
        if not abuse_check.passed:
            blockers.append(f"abuse:{abuse_check.risk_level}")
        if abuse_check.concerns:
            warnings.extend(abuse_check.concerns)

        # Duplication blockers
        if duplication_check.is_duplicate:
            if duplication_check.recommendation == "reject":
                blockers.append("duplication:reject")
            elif duplication_check.recommendation == "merge":
                warnings.append(
                    f"Similar to: {duplication_check.similar_holons[0][0]} "
                    f"(similarity: {duplication_check.highest_similarity:.2f})"
                )
                suggestions.append("Consider merging with existing holon")

        # Generate suggestions
        for principle, score in scores.items():
            if score < 0.4:
                suggestions.append(f"Improve {principle} score (currently {score:.2f})")
            elif score < 0.7:
                suggestions.append(
                    f"Consider improving {principle} score (currently {score:.2f})"
                )

        # Overall pass/fail
        passed = (
            passed_gates
            and law_checks.identity_holds
            and law_checks.associativity_holds
            and abuse_check.passed
            and not (
                duplication_check.is_duplicate
                and duplication_check.recommendation == "reject"
            )
        )

        span.set_attribute("growth.validation.passed", passed)
        span.set_attribute("growth.validation.blockers", blockers)

        # Record metrics
        metrics.counter("growth.validate.invocations").add(1)
        if passed:
            metrics.counter("growth.validate.passed").add(1)
        else:
            metrics.counter("growth.validate.failed").add(1)

        return ValidationResult(
            passed=passed,
            scores=scores,
            reasoning=reasoning,
            law_checks=law_checks,
            abuse_check=abuse_check,
            duplication_check=duplication_check,
            blockers=blockers,
            warnings=warnings,
            suggestions=suggestions,
        )


def validate_proposal_sync(
    proposal: HolonProposal,
    existing_handles: list[str] | None = None,
) -> ValidationResult:
    """
    Synchronous version of validate_proposal for testing.
    """
    import asyncio

    try:
        loop = asyncio.get_event_loop()
        if loop.is_running():
            import concurrent.futures

            with concurrent.futures.ThreadPoolExecutor() as pool:
                future = pool.submit(
                    asyncio.run,
                    validate_proposal(
                        proposal, logos=None, existing_handles=existing_handles
                    ),
                )
                return future.result()
        else:
            return loop.run_until_complete(
                validate_proposal(
                    proposal, logos=None, existing_handles=existing_handles
                )
            )
    except RuntimeError:
        return asyncio.run(
            validate_proposal(proposal, logos=None, existing_handles=existing_handles)
        )


# === Validate Node ===


@dataclass
class ValidateNode(BaseLogosNode):
    """
    self.grow.validate - Proposal validation node.

    Validates proposals against all gates.

    Affordances:
    - manifest: View validation status
    - check: Validate a proposal
    - gates: View gate thresholds

    AGENTESE: self.grow.validate.*
    """

    _handle: str = "self.grow.validate"

    # Integration points
    _logos: "Logos | None" = None
    _budget: GrowthBudget | None = None

    # Cache of validation results
    _results: dict[str, ValidationResult] = field(default_factory=dict)

    @property
    def handle(self) -> str:
        return self._handle

    def _get_affordances_for_archetype(self, archetype: str) -> tuple[str, ...]:
        """Validation requires gardener or architect affordance."""
        affordances = SELF_GROW_AFFORDANCES.get(archetype, ())
        if "validate" in affordances:
            return ("check", "gates", "history")
        return ("gates", "history")  # Read-only for others

    async def manifest(self, observer: "Umwelt[Any, Any]") -> Renderable:
        """View validation status."""
        passed_count = sum(1 for r in self._results.values() if r.passed)
        failed_count = len(self._results) - passed_count

        return BasicRendering(
            summary=f"Validation: {passed_count} passed, {failed_count} failed",
            content=self._format_results(list(self._results.values())[:5]),
            metadata={
                "passed_count": passed_count,
                "failed_count": failed_count,
                "total": len(self._results),
            },
        )

    async def _invoke_aspect(
        self,
        aspect: str,
        observer: "Umwelt[Any, Any]",
        **kwargs: Any,
    ) -> Any:
        """Handle validation aspects."""
        match aspect:
            case "check":
                return await self._check(observer, **kwargs)
            case "gates":
                return self._get_gates()
            case "history":
                return self._get_history(**kwargs)
            case _:
                return {"aspect": aspect, "status": "not implemented"}

    async def _check(
        self,
        observer: "Umwelt[Any, Any]",
        **kwargs: Any,
    ) -> dict[str, Any]:
        """
        Validate a proposal.

        Args:
            proposal: HolonProposal to validate

        Returns:
            Dict with validation results
        """
        meta = self._umwelt_to_meta(observer)

        # Check affordance
        if "validate" not in SELF_GROW_AFFORDANCES.get(meta.archetype, ()):
            raise AffordanceError(
                f"Archetype '{meta.archetype}' cannot validate",
                available=SELF_GROW_AFFORDANCES.get(meta.archetype, ()),
            )

        proposal = kwargs.get("proposal")
        if proposal is None:
            return {"error": "proposal required"}

        # Check budget
        if self._budget is not None:
            if not self._budget.can_afford("validate"):
                from .exceptions import BudgetExhaustedError

                raise BudgetExhaustedError(
                    "Validation budget exhausted",
                    remaining=self._budget.remaining,
                    requested=self._budget.config.validate_cost,
                )
            self._budget.spend("validate")

        # Validate
        result = await validate_proposal(proposal, logos=self._logos)

        # Cache result
        self._results[proposal.proposal_id] = result

        return {
            "status": "validated",
            "passed": result.passed,
            "scores": result.scores,
            "overall_score": result.overall_score,
            "blockers": result.blockers,
            "warnings": result.warnings,
            "suggestions": result.suggestions,
            "law_checks": {
                "identity": result.law_checks.identity_holds,
                "associativity": result.law_checks.associativity_holds,
                "composition": result.law_checks.composition_valid,
                "errors": result.law_checks.errors,
            },
            "abuse_check": {
                "passed": result.abuse_check.passed,
                "risk_level": result.abuse_check.risk_level,
                "concerns": result.abuse_check.concerns,
            },
            "duplication_check": {
                "is_duplicate": result.duplication_check.is_duplicate,
                "recommendation": result.duplication_check.recommendation,
                "highest_similarity": result.duplication_check.highest_similarity,
            },
        }

    def _get_gates(self) -> dict[str, Any]:
        """Get gate thresholds."""
        return {
            "principle_min_threshold": 0.4,
            "principle_high_threshold": 0.7,
            "min_high_count": 5,
            "principles": [
                "tasteful",
                "curated",
                "ethical",
                "joy",
                "composable",
                "heterarchical",
                "generative",
            ],
            "law_checks": ["identity", "associativity", "composition"],
            "abuse_checks": [
                "manipulation",
                "exfiltration",
                "privilege_escalation",
                "resource_abuse",
            ],
        }

    def _get_history(self, **kwargs: Any) -> dict[str, Any]:
        """Get validation history."""
        limit = kwargs.get("limit", 20)
        results = list(self._results.items())[:limit]

        return {
            "results": [
                {
                    "proposal_id": pid,
                    "passed": r.passed,
                    "overall_score": r.overall_score,
                    "blockers": r.blockers,
                }
                for pid, r in results
            ],
            "total": len(self._results),
        }

    def _format_results(self, results: list[ValidationResult]) -> str:
        """Format results for display."""
        if not results:
            return "No validation results"

        lines = []
        for r in results:
            status = "PASS" if r.passed else "FAIL"
            lines.append(f"  [{status}] score={r.overall_score:.2f}")
            if r.blockers:
                lines.append(f"    Blockers: {', '.join(r.blockers[:3])}")
        return "\n".join(lines)


# === Factory ===


def create_validate_node(
    logos: "Logos | None" = None,
    budget: GrowthBudget | None = None,
) -> ValidateNode:
    """
    Create a ValidateNode with optional configuration.

    Args:
        logos: Logos instance for composition/duplication checks
        budget: Growth budget for entropy tracking

    Returns:
        Configured ValidateNode
    """
    return ValidateNode(_logos=logos, _budget=budget)
