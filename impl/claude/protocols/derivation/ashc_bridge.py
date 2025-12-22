"""
ASHC Bridge: Connect Derivation Framework to ASHC Evidence.

Phase 2 of the Derivation Framework: Bridge chaos testing evidence
to principle draws and derivation updates.

The bridge answers: "How do ASHC runs prove constitutional principles?"

Pattern Mapping:
    ASHC Result Pattern          → Constitutional Principle
    ───────────────────────────────────────────────────────
    Composition tests pass       → Composable
    Identity law tests pass      → Composable
    Mode switching tests pass    → Heterarchical
    Spec regeneration tests pass → Generative
    Deduplication tests pass     → Curated
    Type safety (mypy)           → Composable (contracts)
    Lint quality (ruff)          → Tasteful
    High pass rate overall       → General confidence boost

Heritage:
    - ASHC (empirical proofs) → spec/protocols/agentic-self-hosting-compiler.md
    - PrincipleRegistry → protocols/ashc/causal_penalty.py
    - Derivation Framework → spec/protocols/derivation-framework.md

Teaching:
    gotcha: ASHC evidence is EMPIRICAL, not CATEGORICAL. Even 100% pass
            rate doesn't make it categorical—that requires formal proofs.

    gotcha: PrincipleRegistry (causal_penalty.py) tracks credibility
            differently than PrincipleDraw. Sync carefully:
            - PrincipleCredibility.credibility → reputation from blame/reward
            - PrincipleDraw.draw_strength → evidence this agent uses principle
"""

from __future__ import annotations

import re
from dataclasses import replace
from datetime import datetime, timezone
from typing import TYPE_CHECKING

from .types import (
    Derivation,
    EvidenceType,
    PrincipleDraw,
)

if TYPE_CHECKING:
    from protocols.ashc import (
        AdaptiveEvidence,
        ASHCOutput,
        Evidence,
        Run,
    )
    from protocols.ashc.causal_penalty import (
        PrincipleRegistry,
    )

    from .registry import DerivationRegistry


# =============================================================================
# Pattern Mapping: Test Name → Principle
# =============================================================================

# Regex patterns to identify which tests map to which principles
# Order matters: first match wins
PRINCIPLE_PATTERNS: list[tuple[str, re.Pattern[str]]] = [
    # Composability tests
    ("Composable", re.compile(r"(compos|associat|identity|pipeline|chain)", re.I)),
    # Heterarchy tests
    ("Heterarchical", re.compile(r"(mode.*switch|dual.*mode|autonom|leader|follow)", re.I)),
    # Generative tests
    ("Generative", re.compile(r"(regener|spec.*impl|compress|derive|generate)", re.I)),
    # Curated tests (dedupe/dedup/deduplication, curation, curate all match)
    ("Curated", re.compile(r"(dedup|curat|select|prune|quality)", re.I)),
    # Tasteful tests
    ("Tasteful", re.compile(r"(taste|aesthetic|style|format|lint)", re.I)),
    # Joy-Inducing tests
    ("Joy-Inducing", re.compile(r"(joy|delight|persona|voice|warm)", re.I)),
    # Ethical tests
    ("Ethical", re.compile(r"(ethic|privacy|consent|safe|guard)", re.I)),
]

# Verification type → principle mapping
VERIFICATION_PRINCIPLES: dict[str, str] = {
    "test": "Composable",  # Tests verify composition behavior
    "type": "Composable",  # Types verify contracts
    "lint": "Tasteful",  # Lint verifies style/quality
}


def _classify_test_name(test_name: str) -> str | None:
    """
    Classify a test name to a constitutional principle.

    Returns None if no principle matches.
    """
    for principle, pattern in PRINCIPLE_PATTERNS:
        if pattern.search(test_name):
            return principle
    return None


# =============================================================================
# Core Bridge Functions
# =============================================================================


def extract_principle_evidence(
    output: ASHCOutput | AdaptiveEvidence | Evidence,
) -> tuple[PrincipleDraw, ...]:
    """
    Extract principle draws from ASHC evidence.

    Analyzes test results, type results, and lint results to identify
    which constitutional principles have empirical evidence.

    Args:
        output: ASHC compilation output (any evidence type)

    Returns:
        Tuple of PrincipleDraw with empirical evidence from this run

    Pattern Matching:
        - Composition tests → Composable principle
        - Identity tests → Composable principle
        - Mode switching tests → Heterarchical principle
        - Spec regeneration tests → Generative principle
        - Type safety → Composable (contracts respected)
        - Lint quality → Tasteful

    Teaching:
        gotcha: All evidence extracted here is EvidenceType.EMPIRICAL.
                For CATEGORICAL evidence, use lemma_strengthens_derivation().
    """
    # Use duck typing to detect evidence type
    # This allows mocks to work in tests

    # Check for AdaptiveEvidence pattern: has posterior_mean
    if hasattr(output, "posterior_mean"):
        # Type narrow with cast for mypy
        from typing import cast
        return _extract_from_adaptive(cast("AdaptiveEvidence", output))

    # Check for ASHCOutput pattern: has evidence.runs
    if hasattr(output, "evidence") and hasattr(output.evidence, "runs"):
        evidence = output.evidence
    elif hasattr(output, "runs"):
        # Direct Evidence type
        evidence = output
    else:
        # Unknown type, return empty
        return ()

    draws: list[PrincipleDraw] = []
    principle_evidence: dict[str, list[str]] = {}  # principle → list of evidence sources
    principle_scores: dict[str, list[float]] = {}  # principle → list of scores

    # Analyze each run
    for run in evidence.runs:
        # Only analyze runs that have test_results (not AdaptiveRunResult)
        if hasattr(run, "test_results"):
            _analyze_run(run, principle_evidence, principle_scores)
        elif hasattr(run, "success"):
            # Simple run with just success field
            _analyze_simple_run(run, principle_evidence, principle_scores)

    # Create PrincipleDraws from accumulated evidence
    now = datetime.now(timezone.utc)

    for principle, sources in principle_evidence.items():
        if not sources:
            continue

        scores = principle_scores.get(principle, [1.0])
        avg_score = sum(scores) / len(scores) if scores else 0.0

        draws.append(
            PrincipleDraw(
                principle=principle,
                draw_strength=min(0.95, avg_score),  # Cap below categorical
                evidence_type=EvidenceType.EMPIRICAL,
                evidence_sources=tuple(sources[:10]),  # Keep top 10
                last_verified=now,
            )
        )

    return tuple(draws)


def _analyze_run(
    run: Run,
    principle_evidence: dict[str, list[str]],
    principle_scores: dict[str, list[float]],
) -> None:
    """
    Analyze a single run for principle evidence.

    Mutates the evidence and scores dicts.
    """
    # Test results → principle evidence
    if run.test_results.success:
        # All tests passed - boost Composable
        _add_evidence(principle_evidence, principle_scores, "Composable", run.run_id, 1.0)
    elif run.test_results.total > 0:
        # Partial pass - proportional evidence
        rate = run.test_results.passed / run.test_results.total
        _add_evidence(principle_evidence, principle_scores, "Composable", run.run_id, rate)

    # Type results → Composable (contracts)
    if run.type_results.passed:
        _add_evidence(
            principle_evidence, principle_scores, "Composable", f"{run.run_id}:types", 1.0
        )
    else:
        # Type errors - weak negative signal (but we only track positive evidence)
        pass

    # Lint results → Tasteful
    if run.lint_results.passed:
        _add_evidence(
            principle_evidence, principle_scores, "Tasteful", f"{run.run_id}:lint", 0.8
        )

    # If there are specific test patterns in the implementation/prompt
    prompt = run.prompt_used.lower()

    for principle, pattern in PRINCIPLE_PATTERNS:
        if pattern.search(prompt):
            _add_evidence(
                principle_evidence,
                principle_scores,
                principle,
                f"{run.run_id}:pattern",
                run.verification_score,
            )


def _add_evidence(
    evidence_dict: dict[str, list[str]],
    scores_dict: dict[str, list[float]],
    principle: str,
    source: str,
    score: float,
) -> None:
    """Add evidence for a principle (helper)."""
    if principle not in evidence_dict:
        evidence_dict[principle] = []
        scores_dict[principle] = []

    evidence_dict[principle].append(source)
    scores_dict[principle].append(score)


def _analyze_simple_run(
    run: object,
    principle_evidence: dict[str, list[str]],
    principle_scores: dict[str, list[float]],
) -> None:
    """
    Analyze a simple run (just success field) for principle evidence.

    Used for AdaptiveRunResult and similar minimal run types.
    """
    run_id = getattr(run, "run_id", "unknown")
    success = getattr(run, "success", False)

    if success:
        _add_evidence(principle_evidence, principle_scores, "Composable", run_id, 1.0)
    else:
        _add_evidence(principle_evidence, principle_scores, "Composable", run_id, 0.0)


def _extract_from_adaptive(evidence: AdaptiveEvidence) -> tuple[PrincipleDraw, ...]:
    """
    Extract principle draws from AdaptiveEvidence.

    AdaptiveEvidence has Bayesian posteriors which give richer information
    about confidence than raw pass rates.
    """
    draws: list[PrincipleDraw] = []
    now = datetime.now(timezone.utc)

    # Use posterior mean as base confidence
    base_confidence = evidence.posterior_mean

    # Composable: From test/type pass rates
    if evidence.sample_count > 0:
        # Bayesian posterior gives better estimate than raw pass rate
        draws.append(
            PrincipleDraw(
                principle="Composable",
                draw_strength=min(0.95, base_confidence),
                evidence_type=EvidenceType.EMPIRICAL,
                evidence_sources=tuple(
                    r.run_id for r in evidence.runs[:5] if r.success
                ),
                last_verified=now,
            )
        )

    # Decision-based evidence
    if evidence.is_success:
        # Strong empirical evidence across principles
        for principle in ("Composable", "Tasteful"):
            draws.append(
                PrincipleDraw(
                    principle=principle,
                    draw_strength=min(0.90, base_confidence),
                    evidence_type=EvidenceType.EMPIRICAL,
                    evidence_sources=("adaptive-success",),
                    last_verified=now,
                )
            )

    return tuple(draws)


# =============================================================================
# Derivation Update Functions
# =============================================================================


async def update_derivation_from_ashc(
    registry: DerivationRegistry,
    agent_name: str,
    output: ASHCOutput | AdaptiveEvidence | Evidence,
) -> Derivation:
    """
    Update an agent's derivation with ASHC evidence.

    This is the main bridge function: ASHC runs → Derivation updates.

    Flow:
        1. Extract principle evidence from ASHC runs
        2. Get current derivation
        3. Merge new principle draws with existing
        4. Update empirical confidence from equivalence score
        5. Propagate confidence changes through DAG

    Args:
        registry: The derivation registry
        agent_name: Name of the agent to update
        output: ASHC compilation output

    Returns:
        Updated Derivation

    Raises:
        KeyError: If agent not found in registry
        ValueError: If trying to update bootstrap agent

    Teaching:
        gotcha: This function is async for consistency with ASHC patterns,
                even though current implementation is sync. Future versions
                may need async for evidence validation.
    """
    from protocols.ashc import AdaptiveEvidence, ASHCOutput

    # Get current derivation
    current = registry.get(agent_name)
    if current is None:
        raise KeyError(f"Agent '{agent_name}' not found in derivation registry")

    # Extract principle evidence
    new_draws = extract_principle_evidence(output)

    # Merge with existing draws
    merged_draws = merge_principle_draws(current.principle_draws, new_draws)

    # Compute empirical confidence from ASHC (duck typing for testability)
    if hasattr(output, "posterior_mean"):
        # AdaptiveEvidence pattern
        ashc_score = output.posterior_mean
    elif hasattr(output, "evidence") and hasattr(output.evidence, "equivalence_score"):
        # ASHCOutput pattern
        ashc_score = output.evidence.equivalence_score
    elif hasattr(output, "equivalence_score"):
        # Direct Evidence pattern
        ashc_score = output.equivalence_score
    else:
        # Fallback: try to compute from runs
        ashc_score = 0.5

    # Update the derivation
    # We use registry.update_evidence for propagation
    updated = registry.update_evidence(agent_name, ashc_score=ashc_score)

    # Now update principle draws (registry doesn't handle this)
    # We need to directly update the derivation
    if merged_draws != current.principle_draws:
        final = replace(updated, principle_draws=merged_draws)
        registry._derivations[agent_name] = final
        return final

    return updated


def merge_principle_draws(
    existing: tuple[PrincipleDraw, ...],
    new_draws: tuple[PrincipleDraw, ...],
) -> tuple[PrincipleDraw, ...]:
    """
    Merge new principle draws with existing ones.

    For each principle:
        - If new evidence is stronger, use new
        - If existing is categorical, keep it (categorical never demoted)
        - Otherwise, weighted average with recency bias

    Args:
        existing: Current principle draws
        new_draws: New draws from ASHC

    Returns:
        Merged tuple of PrincipleDraws
    """
    # Build lookup of existing by principle
    existing_by_principle: dict[str, PrincipleDraw] = {d.principle: d for d in existing}

    merged: dict[str, PrincipleDraw] = dict(existing_by_principle)

    for new_draw in new_draws:
        principle = new_draw.principle

        if principle not in merged:
            # New principle - just add it
            merged[principle] = new_draw
        else:
            old_draw = merged[principle]

            # Categorical evidence is never demoted
            if old_draw.evidence_type == EvidenceType.CATEGORICAL:
                continue

            # If new evidence is categorical, upgrade
            if new_draw.evidence_type == EvidenceType.CATEGORICAL:
                merged[principle] = new_draw
                continue

            # Both are non-categorical: weighted average with recency bias
            # New evidence gets 60% weight
            new_strength = 0.6 * new_draw.draw_strength + 0.4 * old_draw.draw_strength

            # Merge evidence sources (keep latest, dedupe)
            all_sources = list(new_draw.evidence_sources) + list(old_draw.evidence_sources)
            unique_sources = list(dict.fromkeys(all_sources))[:10]  # Keep top 10

            merged[principle] = PrincipleDraw(
                principle=principle,
                draw_strength=new_strength,
                evidence_type=EvidenceType.EMPIRICAL,  # Non-categorical merge
                evidence_sources=tuple(unique_sources),
                last_verified=new_draw.last_verified,
            )

    return tuple(sorted(merged.values(), key=lambda d: d.principle))


# =============================================================================
# PrincipleRegistry Integration
# =============================================================================


def sync_from_principle_registry(
    derivation: Derivation,
    principle_registry: PrincipleRegistry,
) -> Derivation:
    """
    Sync derivation principle draws from causal penalty PrincipleRegistry.

    The PrincipleRegistry (from causal_penalty.py) tracks principle credibility
    based on bet outcomes. This function bridges that credibility to PrincipleDraws.

    Mapping:
        PrincipleCredibility.credibility → modulates PrincipleDraw.draw_strength
        PrincipleCredibility.is_discredited → caps draw_strength at 0.3
        PrincipleCredibility.is_predictive → bonus to draw_strength

    Args:
        derivation: Current derivation to update
        principle_registry: Registry of principle credibilities

    Returns:
        Updated Derivation with credibility-adjusted draws

    Teaching:
        gotcha: This is a ONE-WAY sync from registry to derivation.
                The derivation captures what this agent draws on.
                The registry captures global principle credibility.
    """
    updated_draws: list[PrincipleDraw] = []

    for draw in derivation.principle_draws:
        # Get credibility for this principle
        cred = principle_registry.effective_weight(draw.principle)

        # Modulate draw strength by credibility
        if principle_registry.get_or_create(draw.principle).is_discredited:
            # Discredited principles are capped
            adjusted_strength = min(0.3, draw.draw_strength)
        elif principle_registry.get_or_create(draw.principle).is_predictive:
            # Predictive principles get a small bonus
            adjusted_strength = min(1.0, draw.draw_strength * 1.1)
        else:
            # Normal modulation
            adjusted_strength = draw.draw_strength * cred

        updated_draws.append(
            replace(draw, draw_strength=adjusted_strength)
        )

    return replace(derivation, principle_draws=tuple(updated_draws))


def sync_to_principle_registry(
    derivation: Derivation,
    principle_registry: PrincipleRegistry,
    success: bool,
) -> None:
    """
    Sync derivation outcome to PrincipleRegistry (reverse direction).

    When an agent's derivation-backed behavior succeeds or fails,
    reward or blame the principles it draws on.

    Args:
        derivation: The derivation whose outcome we're recording
        principle_registry: Registry to update
        success: Whether the behavior succeeded

    Teaching:
        gotcha: This is a lightweight sync - just cite/reward/blame.
                For full causal penalty tracking, use ASHCBet.
    """
    principle_ids = tuple(d.principle for d in derivation.principle_draws)

    # Always cite (records usage)
    principle_registry.cite_all(principle_ids)

    if success:
        # Small reward for success
        principle_registry.apply_reward(principle_ids, weight=0.01)
    # Note: For failures, use CausalPenalty.from_bet() for proper blame distribution


# =============================================================================
# Lemma Integration (Categorical Evidence)
# =============================================================================


async def lemma_strengthens_derivation(
    registry: DerivationRegistry,
    lemma_id: str,
    lemma_statement: str,
    agent_name: str,
) -> Derivation:
    """
    Strengthen derivation with verified lemma (categorical evidence).

    When a lemma is verified by a formal checker (Dafny, Lean4, Verus),
    it provides CATEGORICAL evidence for the principle it proves.

    Unlike ASHC empirical evidence, categorical evidence:
        - Never decays
        - Has draw_strength = 1.0
        - Comes from formal verification

    Args:
        registry: Derivation registry
        lemma_id: ID of the verified lemma
        lemma_statement: The proven statement (for principle classification)
        agent_name: Agent whose derivation to strengthen

    Returns:
        Updated Derivation with categorical principle draw

    Teaching:
        gotcha: This is the path from Dafny/Lean4 proofs to derivation.
                It's separate from ASHC because formal proofs give certainty.
    """
    current = registry.get(agent_name)
    if current is None:
        raise KeyError(f"Agent '{agent_name}' not found")

    # Classify lemma to principle
    principle = _classify_lemma_to_principle(lemma_statement)
    if principle is None:
        # Unknown principle - no update
        return current

    # Create categorical draw
    new_draw = PrincipleDraw(
        principle=principle,
        draw_strength=1.0,  # Categorical = certain
        evidence_type=EvidenceType.CATEGORICAL,
        evidence_sources=(lemma_id,),
        last_verified=datetime.now(timezone.utc),
    )

    # Merge with existing (categorical overwrites non-categorical)
    merged = merge_principle_draws(current.principle_draws, (new_draw,))

    # Update derivation
    updated = replace(current, principle_draws=merged)
    registry._derivations[agent_name] = updated

    return updated


def _classify_lemma_to_principle(statement: str) -> str | None:
    """Classify a formal lemma statement to a constitutional principle."""
    statement_lower = statement.lower()

    # Pattern matching on lemma statement
    if any(kw in statement_lower for kw in ("associat", "identity", "compos", "morphism")):
        return "Composable"
    if any(kw in statement_lower for kw in ("heterarch", "mode", "flux", "autonom")):
        return "Heterarchical"
    if any(kw in statement_lower for kw in ("generat", "compress", "deriv")):
        return "Generative"
    if any(kw in statement_lower for kw in ("ethic", "privacy", "consent")):
        return "Ethical"

    return None


# =============================================================================
# Exports
# =============================================================================

__all__ = [
    # Core functions
    "extract_principle_evidence",
    "update_derivation_from_ashc",
    "merge_principle_draws",
    # Registry integration
    "sync_from_principle_registry",
    "sync_to_principle_registry",
    # Lemma integration
    "lemma_strengthens_derivation",
]
