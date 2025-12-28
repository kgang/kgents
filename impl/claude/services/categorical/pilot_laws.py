"""
Pilot Law Grammar (Amendment G).

The problem: The 5 pilots define 25 laws across different domains. Without formal
grammar, each pilot reinvents the wheel, and law consistency cannot be verified.

The fix: Five universal law schemas that all pilot laws derive from.

Philosophy:
    "All laws are variations on five themes. The schema IS the law.
     The pilot IS the context. The verification IS the witness."

The Five Universal Law Schemas:
    1. COHERENCE_GATE: X is valid only if Y is marked
    2. DRIFT_ALERT: If loss > threshold, surface it
    3. GHOST_PRESERVATION: Unchosen paths remain inspectable
    4. COURAGE_PRESERVATION: High-risk acts protected from negative weighting
    5. COMPRESSION_HONESTY: Crystal discloses what was dropped

See: plans/enlightened-synthesis/01-theoretical-amendments.md (Amendment G)
See: spec/protocols/witness-primitives.md
"""

from __future__ import annotations

import logging
from dataclasses import dataclass, field
from datetime import datetime, timezone
from enum import Enum
from typing import Any, Callable

logger = logging.getLogger("kgents.categorical.pilot_laws")


# =============================================================================
# Law Schemas
# =============================================================================


class LawSchema(Enum):
    """
    The five universal law schemas derived from pilot analysis.

    All pilot laws derive from these five fundamental patterns. Each schema
    represents a recurring constraint that emerges across different pilots.

    Usage:
        Use LawSchema to categorize and filter laws by their fundamental pattern.
        When creating new PilotLaw instances, select the schema that best matches
        the law's underlying constraint structure.

    Philosophy:
        "All laws are variations on five themes. The schema IS the law.
         The pilot IS the context. The verification IS the witness."
    """

    COHERENCE_GATE = "coherence_gate"
    """X is valid only if Y is marked.

    Pattern: An action or state is only valid when a prerequisite has been witnessed.
    This enforces temporal ordering and dependency chains in the witness graph.

    Predicate signature:
        coherence_gate(action_type, marked_types, has_prerequisite, **kwargs) -> bool

    Examples:
        - Day is complete only when crystal is produced (trail-to-crystal L1)
        - Run is valid only if every major build shift is marked (wasm-survivors L1)
        - Every session begins with declared intent (rap-coach L1)

    Edge cases:
        - None action_type: defaults to True (no constraint)
        - Empty marked_types: any action_type fails
    """

    DRIFT_ALERT = "drift_alert"
    """If loss > threshold, surface it.

    Pattern: When semantic drift exceeds a tolerance, the system must alert.
    This prevents silent degradation and ensures visibility of quality changes.

    Predicate signature:
        drift_alert(current_loss, threshold, surfaced, in_canon, **kwargs) -> bool

    Examples:
        - If Galois loss exceeds threshold, surface the drift (wasm-survivors L2)
        - High-loss mutations cannot redefine canon (sprite-procedural L2)
        - Intent/delivery drift surfaces repair path (rap-coach L5)

    Edge cases:
        - None current_loss: treated as 0.0 (no drift)
        - Negative loss: treated as no drift (passes)
    """

    GHOST_PRESERVATION = "ghost_preservation"
    """Unchosen paths remain inspectable.

    Pattern: Alternatives not taken must be preserved for later inspection.
    This enables counterfactual reasoning and decision archaeology.

    Predicate signature:
        ghost_preservation(unchosen_paths, inspectable_paths, ghosts_preserved, **kwargs) -> bool

    Examples:
        - Unchosen upgrades recorded as ghost alternatives (wasm-survivors L3)
        - Branch alternatives remain viewable (sprite-procedural L4)
        - Voice choices preserved for style tracing (rap-coach L3)

    Edge cases:
        - None/empty unchosen_paths: passes (nothing to preserve)
        - None inspectable_paths with unchosen_paths: fails (ghosts lost)
    """

    COURAGE_PRESERVATION = "courage_preservation"
    """High-risk acts protected from negative weighting.

    Pattern: Bold, daring choices should not be penalized by the scoring system.
    This aligns with "Daring, bold, creative, opinionated but not gaudy."

    Predicate signature:
        courage_preservation(risk_level, penalty_applied, risk_threshold, is_protected, **kwargs) -> bool

    Examples:
        - High-risk takes protected from negative weighting (rap-coach L4)
        - Experimental mutations not penalized (sprite-procedural, implicit)

    Edge cases:
        - Negative risk_level: treated as low risk (passes)
        - None penalty_applied: treated as 0.0 (no penalty)
    """

    COMPRESSION_HONESTY = "compression_honesty"
    """Crystal discloses what was dropped.

    Pattern: When compression occurs, the dropped content must be disclosed.
    This ensures lossy operations remain auditable and reversible in principle.

    Predicate signature:
        compression_honesty(original_elements, crystal_elements, disclosed_elements, drops_disclosed, **kwargs) -> bool

    Examples:
        - All crystals must disclose what was dropped (trail-to-crystal L4)
        - Proof compression honest about lost detail (wasm-survivors L5)
        - Style evolution traced through compression (sprite-procedural L5)

    Edge cases:
        - None original_elements: passes (nothing to compress)
        - Empty crystal_elements: all original elements must be disclosed
    """


# =============================================================================
# Pilot Law
# =============================================================================


@dataclass
class PilotLaw:
    """
    A law instance derived from a schema.

    Each pilot law is a concrete instance of one of the five schemas,
    specialized for a specific pilot's domain.

    Attributes:
        schema: The universal schema this law derives from
        pilot: The pilot that defined this law (e.g., "trail-to-crystal")
        name: Human-readable name for the law
        description: Explanation of what the law enforces
        predicate: Function that checks if the law holds
    """

    schema: LawSchema
    pilot: str
    name: str
    description: str
    predicate: Callable[..., bool]
    metadata: dict[str, Any] = field(default_factory=dict)

    def verify(self, **context: Any) -> bool:
        """
        Check if the law holds in the given context.

        Args:
            **context: Keyword arguments passed to the predicate

        Returns:
            True if the law holds, False otherwise
        """
        try:
            return self.predicate(**context)
        except Exception as e:
            logger.warning(f"Law verification failed for {self.name}: {e}")
            return False

    def to_dict(self) -> dict[str, Any]:
        """Serialize to dictionary (excluding predicate)."""
        return {
            "schema": self.schema.value,
            "pilot": self.pilot,
            "name": self.name,
            "description": self.description,
            "metadata": self.metadata,
        }


# =============================================================================
# Schema Predicate Functions
# =============================================================================


def coherence_gate(
    action_type: str | None = None,
    marked_types: list[str] | None = None,
    has_prerequisite: bool | None = None,
    **kwargs: Any,
) -> bool:
    """
    COHERENCE GATE: X is valid only if Y is marked.

    Can be called in two ways:
    1. With action_type and marked_types: checks if action_type is in marked_types
    2. With has_prerequisite: direct boolean check

    Args:
        action_type: The type of action being validated
        marked_types: List of action types that have been marked/witnessed
        has_prerequisite: Direct boolean for prerequisite satisfaction

    Returns:
        True if coherence gate passes

    Edge cases:
        - has_prerequisite=None with no other args: True (no constraint)
        - action_type=None: True (nothing to validate)
        - marked_types=None: True (no requirements)
        - marked_types=[]: False for any non-None action_type
    """
    # Direct boolean check takes precedence
    if has_prerequisite is not None:
        return bool(has_prerequisite)

    # Both must be provided for action/marked check
    if action_type is not None and marked_types is not None:
        # Handle empty marked_types explicitly
        if not marked_types:
            return False
        return action_type in marked_types

    # Default to True if no valid arguments provided (no constraint)
    return True


def drift_alert(
    current_loss: float | None = 0.0,
    threshold: float | None = 0.5,
    surfaced: bool = True,
    in_canon: bool | None = None,
    **kwargs: Any,
) -> bool:
    """
    DRIFT ALERT: If loss > threshold, must be surfaced.

    Pattern variations:
    1. Standard: If loss exceeds threshold, surfaced must be True
    2. Canon check: High-loss mutations cannot be in canon

    Args:
        current_loss: Current Galois loss value (None treated as 0.0)
        threshold: Maximum acceptable loss before alert required (None treated as 0.5)
        surfaced: Whether the drift has been surfaced to the user
        in_canon: If provided, checks canon eligibility (high loss cannot be canon)

    Returns:
        True if drift alert law is satisfied

    Edge cases:
        - current_loss=None: treated as 0.0 (no drift)
        - threshold=None: treated as 0.5 (default threshold)
        - Negative loss: treated as no drift (passes)
    """
    # Normalize None values to defaults
    loss = current_loss if current_loss is not None else 0.0
    thresh = threshold if threshold is not None else 0.5

    # Negative loss is no drift
    if loss < 0:
        loss = 0.0

    if in_canon is not None:
        # Canon check: high loss cannot be in canon
        if loss >= thresh:
            return not in_canon  # Must NOT be in canon
        return True

    # Standard drift alert: if loss exceeds threshold, must be surfaced
    if loss > thresh:
        return bool(surfaced)
    return True


def ghost_preservation(
    unchosen_paths: list[str] | None = None,
    inspectable_paths: list[str] | None = None,
    ghosts_preserved: bool | None = None,
    **kwargs: Any,
) -> bool:
    """
    GHOST PRESERVATION: Unchosen paths remain inspectable.

    Can be called in two ways:
    1. With unchosen_paths and inspectable_paths: checks all unchosen are inspectable
    2. With ghosts_preserved: direct boolean check

    Args:
        unchosen_paths: Paths/alternatives that were not chosen
        inspectable_paths: Paths that are currently inspectable
        ghosts_preserved: Direct boolean for preservation status

    Returns:
        True if all ghost alternatives are preserved

    Edge cases:
        - ghosts_preserved=None with no other args: True (no constraint)
        - unchosen_paths=None or []: True (nothing to preserve)
        - inspectable_paths=None with unchosen_paths: False (ghosts lost)
    """
    # Direct boolean check takes precedence
    if ghosts_preserved is not None:
        return bool(ghosts_preserved)

    # If unchosen_paths provided, need to verify preservation
    if unchosen_paths is not None:
        # Empty unchosen list: nothing to preserve
        if not unchosen_paths:
            return True
        # Unchosen but no inspectable: ghosts are lost
        if inspectable_paths is None:
            return False
        return all(path in inspectable_paths for path in unchosen_paths)

    # No constraint specified
    return True


def courage_preservation(
    risk_level: float | None = 0.0,
    penalty_applied: float | None = 0.0,
    risk_threshold: float | None = 0.7,
    is_protected: bool | None = None,
    **kwargs: Any,
) -> bool:
    """
    COURAGE PRESERVATION: High-risk acts protected from negative weighting.

    Args:
        risk_level: Risk level of the action (0.0 to 1.0), None treated as 0.0
        penalty_applied: Amount of penalty applied to the action, None treated as 0.0
        risk_threshold: Threshold above which actions are considered "courageous", None treated as 0.7
        is_protected: Direct boolean for protection status

    Returns:
        True if courageous actions are properly protected

    Edge cases:
        - is_protected=None with no other args: True (no constraint)
        - risk_level=None or negative: treated as 0.0 (low risk, passes)
        - penalty_applied=None: treated as 0.0 (no penalty)
        - risk_threshold=None: treated as 0.7 (default threshold)
    """
    # Direct boolean check takes precedence
    if is_protected is not None:
        return bool(is_protected)

    # Normalize None values to defaults
    risk = risk_level if risk_level is not None else 0.0
    penalty = penalty_applied if penalty_applied is not None else 0.0
    thresh = risk_threshold if risk_threshold is not None else 0.7

    # Negative risk is treated as no risk
    if risk < 0:
        risk = 0.0

    if risk >= thresh:
        # High-risk acts should not receive penalties
        return penalty <= 0.0
    return True


def compression_honesty(
    original_elements: set[str] | None = None,
    crystal_elements: set[str] | None = None,
    disclosed_elements: set[str] | None = None,
    drops_disclosed: bool | None = None,
    **kwargs: Any,
) -> bool:
    """
    COMPRESSION HONESTY: Crystal discloses what was dropped.

    Args:
        original_elements: Set of elements in the original content
        crystal_elements: Set of elements in the compressed crystal
        disclosed_elements: Set of dropped elements that were disclosed
        drops_disclosed: Direct boolean for disclosure status

    Returns:
        True if all dropped elements are disclosed

    Edge cases:
        - drops_disclosed=None with no other args: True (no constraint)
        - original_elements=None or empty: True (nothing to compress)
        - crystal_elements=None with original: all original must be disclosed
        - disclosed_elements=None with drops: False (drops not disclosed)
    """
    # Direct boolean check takes precedence
    if drops_disclosed is not None:
        return bool(drops_disclosed)

    # If original elements provided, verify disclosure
    if original_elements is not None:
        # Empty original: nothing to compress
        if not original_elements:
            return True

        # Default crystal_elements to empty set if not provided
        crystal = crystal_elements if crystal_elements is not None else set()
        dropped = original_elements - crystal

        if not dropped:
            return True  # Nothing dropped, nothing to disclose
        if disclosed_elements is not None:
            return dropped <= disclosed_elements  # All dropped items disclosed
        return False  # Items dropped but no disclosure provided

    # No constraint specified
    return True


# =============================================================================
# Pilot Law Registry
# =============================================================================


def _create_pilot_laws() -> list[PilotLaw]:
    """
    Create the registry of pilot laws.

    Each pilot defines laws that instantiate one of the five schemas.
    """
    return [
        # =====================================================================
        # trail-to-crystal-daily-lab
        # =====================================================================
        PilotLaw(
            schema=LawSchema.COHERENCE_GATE,
            pilot="trail-to-crystal",
            name="L1 Day Closure Law",
            description="A day is complete only when a crystal is produced",
            predicate=lambda has_crystal=False, **kw: has_crystal,
        ),
        PilotLaw(
            schema=LawSchema.DRIFT_ALERT,
            pilot="trail-to-crystal",
            name="L2 Crystal Quality Law",
            description="If crystal quality drifts from baseline, surface it",
            predicate=drift_alert,
        ),
        PilotLaw(
            schema=LawSchema.GHOST_PRESERVATION,
            pilot="trail-to-crystal",
            name="L3 Unchosen Insight Law",
            description="Insights not included in crystal remain retrievable",
            predicate=ghost_preservation,
        ),
        PilotLaw(
            schema=LawSchema.COMPRESSION_HONESTY,
            pilot="trail-to-crystal",
            name="L4 Compression Honesty Law",
            description="All crystals must disclose what was dropped",
            predicate=compression_honesty,
        ),

        # =====================================================================
        # wasm-survivors-game
        # =====================================================================
        PilotLaw(
            schema=LawSchema.COHERENCE_GATE,
            pilot="wasm-survivors",
            name="L1 Run Coherence Law",
            description="A run is valid only if every major build shift is marked",
            predicate=coherence_gate,
        ),
        PilotLaw(
            schema=LawSchema.DRIFT_ALERT,
            pilot="wasm-survivors",
            name="L2 Build Drift Law",
            description="If Galois loss exceeds threshold, surface the drift",
            predicate=drift_alert,
        ),
        PilotLaw(
            schema=LawSchema.GHOST_PRESERVATION,
            pilot="wasm-survivors",
            name="L3 Ghost Commitment Law",
            description="Unchosen upgrades recorded as ghost alternatives",
            predicate=ghost_preservation,
        ),
        PilotLaw(
            schema=LawSchema.COURAGE_PRESERVATION,
            pilot="wasm-survivors",
            name="L4 Bold Migration Law",
            description="Risky upgrade paths protected from penalty if witnessed",
            predicate=courage_preservation,
        ),
        PilotLaw(
            schema=LawSchema.COMPRESSION_HONESTY,
            pilot="wasm-survivors",
            name="L5 Proof Compression Law",
            description="Proof compression honest about lost detail",
            predicate=compression_honesty,
        ),

        # =====================================================================
        # disney-portal-daily-witness-lab
        # =====================================================================
        PilotLaw(
            schema=LawSchema.COHERENCE_GATE,
            pilot="disney-portal",
            name="L2 Day Integrity Law",
            description="Day entries are coherent with marked experiences",
            predicate=coherence_gate,
        ),
        PilotLaw(
            schema=LawSchema.GHOST_PRESERVATION,
            pilot="disney-portal",
            name="L3 Unchosen Experience Law",
            description="Experiences considered but not recorded remain inspectable",
            predicate=ghost_preservation,
        ),
        PilotLaw(
            schema=LawSchema.COMPRESSION_HONESTY,
            pilot="disney-portal",
            name="L5 Crystal Legibility Law",
            description="Crystals remain legible even to future selves",
            predicate=lambda is_legible=True, **kw: bool(is_legible),
        ),

        # =====================================================================
        # rap-coach-flow-lab
        # =====================================================================
        PilotLaw(
            schema=LawSchema.COHERENCE_GATE,
            pilot="rap-coach",
            name="L1 Intent Declaration Law",
            description="Every session begins with declared intent",
            predicate=lambda intent_declared=False, **kw: intent_declared,
        ),
        PilotLaw(
            schema=LawSchema.GHOST_PRESERVATION,
            pilot="rap-coach",
            name="L3 Voice Continuity Law",
            description="Voice choices preserved for style tracing",
            predicate=ghost_preservation,
        ),
        PilotLaw(
            schema=LawSchema.COURAGE_PRESERVATION,
            pilot="rap-coach",
            name="L4 Courage Preservation Law",
            description="High-risk takes are protected from negative weighting",
            predicate=courage_preservation,
        ),
        PilotLaw(
            schema=LawSchema.DRIFT_ALERT,
            pilot="rap-coach",
            name="L5 Repair Path Law",
            description="If intent/delivery drift, surface repair path",
            predicate=drift_alert,
        ),
        PilotLaw(
            schema=LawSchema.COMPRESSION_HONESTY,
            pilot="rap-coach",
            name="L6 Session Compression Law",
            description="Flow session summaries disclose omitted takes",
            predicate=compression_honesty,
        ),

        # =====================================================================
        # sprite-procedural-taste-lab
        # =====================================================================
        PilotLaw(
            schema=LawSchema.DRIFT_ALERT,
            pilot="sprite-procedural",
            name="L2 Wildness Quarantine Law",
            description="High-loss mutations can exist but cannot redefine canon",
            predicate=drift_alert,
        ),
        PilotLaw(
            schema=LawSchema.COHERENCE_GATE,
            pilot="sprite-procedural",
            name="L3 Mutation Justification Law",
            description="Every mutation has a marked justification",
            predicate=lambda mutation_justified=False, **kw: mutation_justified,
        ),
        PilotLaw(
            schema=LawSchema.GHOST_PRESERVATION,
            pilot="sprite-procedural",
            name="L4 Branch Preservation Law",
            description="Branch alternatives remain viewable",
            predicate=ghost_preservation,
        ),
        PilotLaw(
            schema=LawSchema.COURAGE_PRESERVATION,
            pilot="sprite-procedural",
            name="L5 Experimental Mutation Law",
            description="Experimental mutations protected from taste penalties",
            predicate=courage_preservation,
        ),
        PilotLaw(
            schema=LawSchema.COMPRESSION_HONESTY,
            pilot="sprite-procedural",
            name="L6 Style Continuity Law",
            description="Style evolution traced through compression",
            predicate=compression_honesty,
        ),
    ]


# Create the global registry
PILOT_LAWS: list[PilotLaw] = _create_pilot_laws()


# =============================================================================
# Law Verification
# =============================================================================


@dataclass
class LawVerificationResult:
    """Result of verifying a single law."""

    law: PilotLaw
    passed: bool
    verified_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    error_message: str | None = None

    def to_dict(self) -> dict[str, Any]:
        """Serialize to dictionary."""
        return {
            "law_name": self.law.name,
            "pilot": self.law.pilot,
            "schema": self.law.schema.value,
            "passed": self.passed,
            "verified_at": self.verified_at.isoformat(),
            "error_message": self.error_message,
        }


@dataclass
class LawVerificationReport:
    """Report from verifying multiple laws."""

    results: list[LawVerificationResult]
    verified_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))

    @property
    def all_passed(self) -> bool:
        """True if all laws passed verification."""
        return all(r.passed for r in self.results)

    @property
    def pass_count(self) -> int:
        """Number of laws that passed."""
        return sum(1 for r in self.results if r.passed)

    @property
    def fail_count(self) -> int:
        """Number of laws that failed."""
        return sum(1 for r in self.results if not r.passed)

    @property
    def failures(self) -> list[LawVerificationResult]:
        """List of failed verifications."""
        return [r for r in self.results if not r.passed]

    @property
    def by_pilot(self) -> dict[str, list[LawVerificationResult]]:
        """Group results by pilot."""
        result: dict[str, list[LawVerificationResult]] = {}
        for r in self.results:
            pilot = r.law.pilot
            if pilot not in result:
                result[pilot] = []
            result[pilot].append(r)
        return result

    @property
    def by_schema(self) -> dict[LawSchema, list[LawVerificationResult]]:
        """Group results by schema."""
        result: dict[LawSchema, list[LawVerificationResult]] = {}
        for r in self.results:
            schema = r.law.schema
            if schema not in result:
                result[schema] = []
            result[schema].append(r)
        return result

    def to_dict(self) -> dict[str, Any]:
        """Serialize to dictionary."""
        return {
            "verified_at": self.verified_at.isoformat(),
            "all_passed": self.all_passed,
            "pass_count": self.pass_count,
            "fail_count": self.fail_count,
            "results": [r.to_dict() for r in self.results],
        }


def verify_law(
    law: PilotLaw,
    context: dict[str, Any],
) -> LawVerificationResult:
    """
    Verify a single law against a context.

    Args:
        law: The law to verify
        context: Context dictionary with verification data

    Returns:
        LawVerificationResult with pass/fail status
    """
    try:
        # Call predicate directly to capture any exceptions
        passed = law.predicate(**context)
        return LawVerificationResult(law=law, passed=passed)
    except Exception as e:
        return LawVerificationResult(
            law=law,
            passed=False,
            error_message=str(e),
        )


def verify_all_laws(context: dict[str, Any]) -> dict[str, bool]:
    """
    Verify all pilot laws against a context.

    The context should be organized by pilot, with each pilot's context
    containing the arguments needed for its laws.

    Example context:
        {
            "trail-to-crystal": {"has_crystal": True},
            "wasm-survivors": {
                "action_type": "build",
                "marked_types": ["build", "deploy"],
                "current_loss": 0.3,
                "threshold": 0.5,
                "surfaced": True,
            },
        }

    Args:
        context: Dictionary organized by pilot with verification data

    Returns:
        Dictionary mapping law name to pass/fail status
    """
    results: dict[str, bool] = {}

    for law in PILOT_LAWS:
        try:
            # Get pilot-specific context
            pilot_context = context.get(law.pilot, {})
            # Merge with any global context
            full_context = {**context, **pilot_context}
            results[law.name] = law.verify(**full_context)
        except Exception as e:
            logger.warning(f"Law verification failed for {law.name}: {e}")
            results[law.name] = False

    return results


def verify_pilot_laws(
    pilot: str,
    context: dict[str, Any],
) -> LawVerificationReport:
    """
    Verify all laws for a specific pilot.

    Args:
        pilot: Pilot name to filter laws
        context: Context dictionary with verification data

    Returns:
        LawVerificationReport with all results for the pilot
    """
    pilot_laws = [law for law in PILOT_LAWS if law.pilot == pilot]
    results = [verify_law(law, context) for law in pilot_laws]
    return LawVerificationReport(results=results)


def verify_schema_laws(
    schema: LawSchema,
    context: dict[str, Any],
) -> LawVerificationReport:
    """
    Verify all laws of a specific schema type.

    Args:
        schema: Schema type to filter laws
        context: Context dictionary with verification data

    Returns:
        LawVerificationReport with all results for the schema
    """
    schema_laws = [law for law in PILOT_LAWS if law.schema == schema]
    results = [verify_law(law, context) for law in schema_laws]
    return LawVerificationReport(results=results)


def verify_all_pilot_laws(
    contexts: dict[str, dict[str, Any]] | None = None,
) -> LawVerificationReport:
    """
    Comprehensive verification of all pilot laws across all pilots.

    This is the primary entry point for full system verification.
    Each pilot can have its own context, or defaults are used.

    Args:
        contexts: Optional dict mapping pilot names to their contexts.
                  Missing pilots use empty context (laws may fail or pass by default).

    Returns:
        LawVerificationReport with results for all laws across all pilots.

    Example:
        >>> report = verify_all_pilot_laws({
        ...     "trail-to-crystal": {"has_crystal": True, "drops_disclosed": True},
        ...     "wasm-survivors": {"has_prerequisite": True, "current_loss": 0.2},
        ... })
        >>> print(f"Passed: {report.pass_count}/{len(report.results)}")
        >>> for failure in report.failures:
        ...     print(f"  FAIL: {failure.law.name}")

    Coverage Report:
        Use report.by_pilot to see results grouped by pilot.
        Use report.by_schema to see results grouped by schema type.
    """
    if contexts is None:
        contexts = {}

    all_results: list[LawVerificationResult] = []

    for pilot in get_all_pilots():
        pilot_context = contexts.get(pilot, {})
        pilot_laws = get_laws_by_pilot(pilot)
        for law in pilot_laws:
            result = verify_law(law, pilot_context)
            all_results.append(result)

    return LawVerificationReport(results=all_results)


# =============================================================================
# Law Registry Utilities
# =============================================================================


def get_laws_by_pilot(pilot: str) -> list[PilotLaw]:
    """Get all laws defined by a specific pilot."""
    return [law for law in PILOT_LAWS if law.pilot == pilot]


def get_laws_by_schema(schema: LawSchema) -> list[PilotLaw]:
    """Get all laws that derive from a specific schema."""
    return [law for law in PILOT_LAWS if law.schema == schema]


def get_all_pilots() -> list[str]:
    """Get list of all pilot names with defined laws."""
    return list(sorted(set(law.pilot for law in PILOT_LAWS)))


def get_law_by_name(name: str) -> PilotLaw | None:
    """Get a specific law by name."""
    for law in PILOT_LAWS:
        if law.name == name:
            return law
    return None


def summarize_pilot_laws() -> dict[str, dict[str, list[str]]]:
    """
    Create a summary of all pilot laws organized by pilot and schema.

    Returns:
        Nested dictionary: {pilot: {schema: [law_names]}}
    """
    summary: dict[str, dict[str, list[str]]] = {}

    for law in PILOT_LAWS:
        if law.pilot not in summary:
            summary[law.pilot] = {}
        schema_name = law.schema.value
        if schema_name not in summary[law.pilot]:
            summary[law.pilot][schema_name] = []
        summary[law.pilot][schema_name].append(law.name)

    return summary


# =============================================================================
# Module Exports
# =============================================================================

__all__ = [
    # Enums
    "LawSchema",
    # Core types
    "PilotLaw",
    "LawVerificationResult",
    "LawVerificationReport",
    # Schema predicates
    "coherence_gate",
    "drift_alert",
    "ghost_preservation",
    "courage_preservation",
    "compression_honesty",
    # Registry
    "PILOT_LAWS",
    # Verification functions
    "verify_law",
    "verify_all_laws",
    "verify_pilot_laws",
    "verify_schema_laws",
    "verify_all_pilot_laws",
    # Registry utilities
    "get_laws_by_pilot",
    "get_laws_by_schema",
    "get_all_pilots",
    "get_law_by_name",
    "summarize_pilot_laws",
]
