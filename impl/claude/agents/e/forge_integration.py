"""
E-gent + F-gent Integration: Re-Forge from Evolved Intent

Cross-Pollination Opportunity T1.2 from CROSS_POLLINATION_ANALYSIS.md:
- E-gent proposes improved intent based on code evolution
- F-gent re-forges artifact cleanly from updated intent
- Provides clean regeneration vs incremental patching

Workflow:
    1. Analyze current artifact (code + intent)
    2. Propose improved intent based on learnings
    3. Re-forge artifact from improved intent
    4. Validate new artifact maintains lineage
"""

from dataclasses import dataclass
from enum import Enum
from typing import Optional

# E-gent imports
from agents.e.experiment import CodeModule, ExperimentResult
from agents.e.judge import JudgeResult

# F-gent imports
from agents.f.intent import parse_intent
from agents.f.contract import Contract, synthesize_contract
from agents.f.prototype import SourceCode, generate_prototype, PrototypeConfig


class ReforgeStrategy(Enum):
    """Strategy for re-forging artifacts"""

    FULL_REFORGE = "full_reforge"  # Complete regeneration from new intent
    INTENT_REFINEMENT = "intent_refinement"  # Update intent only, keep structure
    HYBRID = "hybrid"  # Re-forge with constraints from original


@dataclass
class ImprovedIntent:
    """Proposed improved intent based on evolution learnings"""

    original_intent: str
    improved_intent: str
    rationale: str
    changes: list[str]  # List of specific improvements
    preserved_constraints: list[str]  # Constraints to preserve from original
    breaking_changes: bool  # Whether this would break existing contracts


@dataclass
class ReforgeResult:
    """Result of re-forging from evolved intent"""

    strategy: ReforgeStrategy
    improved_intent: ImprovedIntent
    new_contract: Optional[Contract]
    new_source: Optional[SourceCode]
    original_artifact: CodeModule
    validation_passed: bool
    lineage: dict[str, str]  # Tracks evolution history


async def propose_improved_intent(
    artifact: CodeModule,
    original_intent: str = "",
    judge_result: Optional[JudgeResult] = None,
    experiment_result: Optional[ExperimentResult] = None,
) -> ImprovedIntent:
    """
    Analyze evolved code and propose improved intent.

    Args:
        artifact: Current code artifact
        original_intent: The original intent text for the artifact
        judge_result: Judgment from E-gent evaluation
        experiment_result: Results from E-gent experiments

    Returns:
        ImprovedIntent with proposed refinements
    """
    # Use provided intent or infer from module name
    if not original_intent:
        # Infer basic intent from module name
        original_intent = f"Agent that handles {artifact.name} functionality"

    # Collect improvement signals
    changes: list[str] = []
    preserved_constraints: list[str] = []
    breaking_changes = False

    # From judge result: analyze principle scores
    if judge_result:
        for score in judge_result.scores:
            if score.score < 0.7:
                reason_text = f": {score.reason}" if score.reason else ""
                changes.append(f"Improve {score.name}{reason_text}")

            # Preserve high-scoring aspects
            if score.score >= 0.9:
                preserved_constraints.append(f"Maintain {score.name} excellence")

    # From experiment result: analyze what worked
    if experiment_result and experiment_result.experiment:
        exp = experiment_result.experiment

        # If experiment passed without errors
        if exp.status.value in ["passed", "held"] and not exp.error:
            preserved_constraints.append("Maintain experimental improvements")

        # If experiment has test results
        if exp.test_results:
            preserved_constraints.append("Maintain test coverage")

    # Synthesize improved intent
    improved_intent = _synthesize_improved_intent(
        original_intent,
        changes,
        preserved_constraints,
    )

    # Detect breaking changes
    breaking_changes = _detect_breaking_changes(
        original_intent,
        improved_intent,
    )

    rationale = _generate_rationale(
        changes,
        preserved_constraints,
        breaking_changes,
    )

    return ImprovedIntent(
        original_intent=original_intent,
        improved_intent=improved_intent,
        rationale=rationale,
        changes=changes,
        preserved_constraints=preserved_constraints,
        breaking_changes=breaking_changes,
    )


async def reforge_from_evolved_intent(
    artifact: CodeModule,
    improved_intent: ImprovedIntent,
    agent_name: str,
    strategy: ReforgeStrategy = ReforgeStrategy.FULL_REFORGE,
    config: Optional[PrototypeConfig] = None,
) -> ReforgeResult:
    """
    Re-forge artifact from improved intent.

    Args:
        artifact: Original artifact
        improved_intent: Proposed improvements
        agent_name: Name for re-forged agent
        strategy: Re-forging strategy
        config: Optional prototype configuration

    Returns:
        ReforgeResult with new contract and source
    """
    # Phase 1: Parse improved intent
    new_intent = parse_intent(improved_intent.improved_intent)

    # Phase 2: Synthesize contract
    new_contract = synthesize_contract(new_intent, agent_name)

    # Phase 3: Generate prototype (if requested)
    new_source = None
    validation_passed = False

    if strategy in [ReforgeStrategy.FULL_REFORGE, ReforgeStrategy.HYBRID]:
        if config is None:
            config = PrototypeConfig()

        # generate_prototype needs both intent and contract
        new_source = generate_prototype(
            intent=new_intent,
            contract=new_contract,
            config=config,
        )
        validation_passed = new_source.analysis_report.passed

    # Build lineage
    lineage = {
        "parent": artifact.name,
        "parent_path": str(artifact.path),
        "parent_category": artifact.category,
        "reforge_strategy": strategy.value,
        "intent_changes": str(len(improved_intent.changes)),
        "breaking_changes": str(improved_intent.breaking_changes),
    }

    return ReforgeResult(
        strategy=strategy,
        improved_intent=improved_intent,
        new_contract=new_contract,
        new_source=new_source,
        original_artifact=artifact,
        validation_passed=validation_passed,
        lineage=lineage,
    )


def _synthesize_improved_intent(
    original: str,
    changes: list[str],
    preserved: list[str],
) -> str:
    """
    Synthesize improved intent from original + changes + constraints.

    Simple heuristic version - in production would use LLM.
    """
    # Start with original
    improved = original

    # Apply changes (simple concatenation for now)
    if changes:
        change_text = ". ".join(changes)
        improved = f"{improved}. IMPROVEMENTS: {change_text}"

    # Add preserved constraints
    if preserved:
        preserved_text = ", ".join(preserved)
        improved = f"{improved}. PRESERVE: {preserved_text}"

    return improved


def _detect_breaking_changes(
    original: str,
    improved: str,
) -> bool:
    """
    Detect if improved intent introduces breaking changes.

    Heuristic: Look for keywords indicating interface changes.
    """
    breaking_keywords = [
        "remove",
        "delete",
        "change signature",
        "different input",
        "different output",
        "incompatible",
    ]

    improved_lower = improved.lower()
    return any(keyword in improved_lower for keyword in breaking_keywords)


def _generate_rationale(
    changes: list[str],
    preserved: list[str],
    breaking_changes: bool,
) -> str:
    """Generate human-readable rationale for intent improvement"""

    parts = []

    if changes:
        parts.append(f"Proposed {len(changes)} improvements")

    if preserved:
        parts.append(f"Preserving {len(preserved)} high-quality aspects")

    if breaking_changes:
        parts.append("WARNING: Contains breaking changes")
    else:
        parts.append("No breaking changes detected")

    return ". ".join(parts)


async def evolve_and_reforge_workflow(
    artifact: CodeModule,
    agent_name: str,
    original_intent: str = "",
    judge_result: Optional[JudgeResult] = None,
    experiment_result: Optional[ExperimentResult] = None,
    strategy: ReforgeStrategy = ReforgeStrategy.FULL_REFORGE,
    config: Optional[PrototypeConfig] = None,
) -> ReforgeResult:
    """
    Full workflow: Analyze → Propose Intent → Re-forge

    This is the main integration point for E+F cross-pollination.

    Args:
        artifact: Current code artifact
        agent_name: Name for re-forged agent
        original_intent: Original intent text for the artifact
        judge_result: Optional judgment from E-gent
        experiment_result: Optional experiment results
        strategy: Re-forging strategy
        config: Optional prototype configuration

    Returns:
        ReforgeResult with complete lineage
    """
    # Step 1: Propose improved intent
    improved_intent = await propose_improved_intent(
        artifact=artifact,
        original_intent=original_intent,
        judge_result=judge_result,
        experiment_result=experiment_result,
    )

    # Step 2: Re-forge from improved intent
    result = await reforge_from_evolved_intent(
        artifact=artifact,
        improved_intent=improved_intent,
        agent_name=agent_name,
        strategy=strategy,
        config=config,
    )

    return result
