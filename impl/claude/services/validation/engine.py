"""
ValidationEngine: Witnessed Validation Orchestration.

The engine is the primary interface for:
- Registering initiatives (from YAML configs)
- Running validations with automatic Witness integration
- Querying status and blockers

Design:
- Coordinates runner (pure validation) and store (persistence)
- INTRINSIC Witness integration: every validation emits Marks
- "Validation IS witnessed measurement" — not a bolt-on

Philosophy:
    "If you can't measure it, you can't claim it."
    "The proof IS the decision. The mark IS the witness."

See: spec/validation/schema.md
See: plans/validation-framework-implementation.md
"""

from __future__ import annotations

import hashlib
import json
import logging
from dataclasses import dataclass, field, replace
from datetime import datetime, timedelta, timezone
from pathlib import Path
from typing import TYPE_CHECKING, Any

import yaml

from .runner import (
    calculate_gap,
    check_gate,
    check_proposition,
)
from .schema import (
    Blocker,
    GateResult,
    Initiative,
    InitiativeId,
    InitiativeStatus,
    MarkId,
    PhaseId,
    Proposition,
    PropositionId,
    PropositionResult,
    ValidationRun,
    initiative_from_dict,
)
from .store import ValidationStore, get_validation_store

# Witness imports — validation IS witnessed measurement
if TYPE_CHECKING:
    from services.proxy import ProxyHandle, ProxyHandleStore
    from services.witness.mark import Mark as MarkType
    from services.witness.trace_store import MarkStore as MarkStoreType

logger = logging.getLogger("kgents.validation.engine")


# =============================================================================
# ValidationEngine
# =============================================================================


@dataclass
class ValidationEngine:
    """
    Witnessed validation orchestration.

    Responsibilities:
    - Register initiatives from YAML configs
    - Run validations for initiatives/phases
    - Emit Marks for every measurement (intrinsic witnessing)
    - Track status and blockers
    - Persist validation runs

    Philosophy:
        "Validation IS witnessed measurement."
        Every proposition check emits a Mark.
        Every gate decision emits a Mark with Proof.empirical().

    Example:
        >>> engine = ValidationEngine()
        >>> engine.load_initiatives_from_dir(Path("initiatives/"))
        >>> run = engine.validate("brain", {"tests_pass": 1, "test_count": 250})
        >>> # run.gate_result.decision_id is populated
        >>> # Each proposition_result.mark_id is populated
        >>> status = engine.get_status("brain")
        >>> blockers = engine.get_blockers()
    """

    # Registered initiatives: id → Initiative
    _initiatives: dict[InitiativeId, Initiative] = field(default_factory=dict)

    # Phase completion tracking: (initiative_id, phase_id) → passed
    _phase_status: dict[tuple[InitiativeId, PhaseId], bool] = field(default_factory=dict)

    # Store for persistence (injected or use global)
    _store: ValidationStore | None = None

    # MarkStore for witness integration (injected or use global)
    _mark_store: MarkStoreType | None = None

    # ProxyHandleStore for caching (injected or use global)
    _proxy_store: "ProxyHandleStore | None" = None

    # Whether to emit marks (can be disabled for pure validation)
    emit_marks: bool = True

    @property
    def store(self) -> ValidationStore:
        """Get the validation store (lazy initialization)."""
        if self._store is None:
            self._store = get_validation_store()
        return self._store

    @property
    def mark_store(self) -> MarkStoreType:
        """Get the mark store (lazy initialization)."""
        if self._mark_store is None:
            from services.witness.trace_store import get_mark_store

            self._mark_store = get_mark_store()
        return self._mark_store

    @property
    def proxy_store(self) -> "ProxyHandleStore":
        """Get the proxy handle store (lazy initialization)."""
        if self._proxy_store is None:
            from services.proxy import get_proxy_handle_store

            self._proxy_store = get_proxy_handle_store()
        return self._proxy_store

    # =========================================================================
    # Witness Integration (Intrinsic)
    # =========================================================================

    def _emit_proposition_mark(
        self,
        initiative_id: InitiativeId,
        phase_id: PhaseId | None,
        proposition: Proposition,
        value: float | None,
        passed: bool,
        timestamp: datetime,
        witness_tags: tuple[str, ...],
    ) -> MarkId | None:
        """
        Emit a Mark for a proposition measurement.

        Returns the mark_id if emitted, None if marks disabled.
        """
        if not self.emit_marks:
            return None

        from services.witness.mark import Mark, Response, Stimulus

        direction_symbol = proposition.direction.value
        status = "PASS" if passed else "FAIL"
        value_str = str(value) if value is not None else "NOT_MEASURED"

        content = (
            f"Measured {proposition.id}: "
            f"{value_str} {direction_symbol} {proposition.threshold} = {status}"
        )

        mark = Mark.from_thought(
            content=content,
            source="validation",
            tags=witness_tags + ("validation", str(initiative_id), str(proposition.id)),
            origin="validation",
        )

        try:
            self.mark_store.append(mark)
            logger.debug(f"Emitted mark {mark.id} for proposition {proposition.id}")
            return MarkId(str(mark.id))
        except Exception as e:
            logger.warning(f"Failed to emit mark for {proposition.id}: {e}")
            return None

    def _emit_gate_decision_mark(
        self,
        initiative_id: InitiativeId,
        phase_id: PhaseId | None,
        gate_id: str,
        passed: bool,
        proposition_results: tuple[PropositionResult, ...],
        timestamp: datetime,
        witness_tags: tuple[str, ...],
    ) -> str | None:
        """
        Emit a Mark with Proof.empirical() for a gate decision.

        Returns the decision_id (mark_id) if emitted, None if marks disabled.
        """
        if not self.emit_marks:
            return None

        from services.witness.mark import Mark, Proof, Response, Stimulus

        passed_count = sum(1 for r in proposition_results if r.passed)
        total_count = len(proposition_results)
        status = "PASS" if passed else "BLOCKED"

        # Build data summary
        data = f"{passed_count}/{total_count} propositions passed"

        # Build claim
        claim = f"Gate {gate_id}: {status}"

        # Build warrant
        if passed:
            warrant = "All required propositions satisfied"
        else:
            failed = [str(r.proposition_id) for r in proposition_results if not r.passed]
            warrant = f"Blocked by: {', '.join(failed)}"

        # Create Proof.empirical
        proof = Proof.empirical(
            data=data,
            warrant=warrant,
            claim=claim,
            backing=f"Initiative: {initiative_id}" + (f", Phase: {phase_id}" if phase_id else ""),
        )

        # Create mark with proof
        content = f"Gate decision: {claim} ({data})"
        mark = Mark.from_thought(
            content=content,
            source="validation",
            tags=witness_tags + ("validation", "gate", str(initiative_id), str(gate_id)),
            origin="validation",
        )
        mark = mark.with_proof(proof)

        try:
            self.mark_store.append(mark)
            logger.debug(f"Emitted gate decision mark {mark.id} for gate {gate_id}")
            return str(mark.id)
        except Exception as e:
            logger.warning(f"Failed to emit gate decision mark for {gate_id}: {e}")
            return None

    def _validate_propositions_witnessed(
        self,
        initiative_id: InitiativeId,
        phase_id: PhaseId | None,
        propositions: tuple[Proposition, ...],
        measurements: dict[str, float],
        timestamp: datetime,
        witness_tags: tuple[str, ...],
    ) -> tuple[dict[PropositionId, PropositionResult], dict[PropositionId, Proposition]]:
        """
        Validate propositions with witness mark emission.

        Returns (results dict, propositions dict) for gate checking.
        """
        proposition_results: dict[PropositionId, PropositionResult] = {}
        propositions_map: dict[PropositionId, Proposition] = {}

        for prop in propositions:
            propositions_map[prop.id] = prop
            value = measurements.get(str(prop.id))

            # Use pure runner function
            result = check_proposition(prop, value, timestamp)

            # Emit witness mark
            mark_id = self._emit_proposition_mark(
                initiative_id=initiative_id,
                phase_id=phase_id,
                proposition=prop,
                value=value,
                passed=result.passed,
                timestamp=timestamp,
                witness_tags=witness_tags,
            )

            # Attach mark_id to result (frozen dataclass, use replace)
            if mark_id:
                result = replace(result, mark_id=mark_id)

            proposition_results[prop.id] = result

        return proposition_results, propositions_map

    # =========================================================================
    # Initiative Registration
    # =========================================================================

    def register_initiative(self, initiative: Initiative) -> None:
        """
        Register an initiative for validation.

        Args:
            initiative: The initiative to register

        Raises:
            ValueError: If initiative with this ID already exists
        """
        if initiative.id in self._initiatives:
            logger.warning(f"Re-registering initiative {initiative.id}")

        self._initiatives[initiative.id] = initiative
        logger.info(f"Registered initiative: {initiative.id} ({initiative.name})")

    def register_from_yaml(self, yaml_path: Path) -> Initiative:
        """
        Register an initiative from a YAML file.

        Args:
            yaml_path: Path to the YAML file

        Returns:
            The registered initiative
        """
        with yaml_path.open("r", encoding="utf-8") as f:
            data = yaml.safe_load(f)

        initiative = initiative_from_dict(data)
        self.register_initiative(initiative)
        return initiative

    def load_initiatives_from_dir(self, dir_path: Path) -> list[Initiative]:
        """
        Load all initiatives from a directory (recursive).

        Args:
            dir_path: Directory containing YAML files

        Returns:
            List of loaded initiatives
        """
        initiatives: list[Initiative] = []

        if not dir_path.exists():
            logger.warning(f"Initiatives directory does not exist: {dir_path}")
            return initiatives

        for yaml_file in dir_path.rglob("*.yaml"):
            try:
                initiative = self.register_from_yaml(yaml_file)
                initiatives.append(initiative)
            except Exception as e:
                logger.error(f"Failed to load {yaml_file}: {e}")

        logger.info(f"Loaded {len(initiatives)} initiatives from {dir_path}")
        return initiatives

    def get_initiative(self, initiative_id: InitiativeId | str) -> Initiative | None:
        """Get an initiative by ID."""
        if isinstance(initiative_id, str):
            initiative_id = InitiativeId(initiative_id)
        return self._initiatives.get(initiative_id)

    def list_initiatives(self) -> list[Initiative]:
        """List all registered initiatives."""
        return list(self._initiatives.values())

    # =========================================================================
    # Validation
    # =========================================================================

    def validate(
        self,
        initiative_id: InitiativeId | str,
        measurements: dict[str, float],
        phase_id: PhaseId | str | None = None,
    ) -> ValidationRun:
        """
        Run witnessed validation for an initiative.

        Every proposition measurement emits a Mark.
        Every gate decision emits a Mark with Proof.empirical().

        Args:
            initiative_id: The initiative to validate
            measurements: Map of proposition ID to measured value
            phase_id: For phased initiatives, which phase to validate

        Returns:
            ValidationRun with results (mark_ids populated)

        Raises:
            ValueError: If initiative not found or phase mismatch
        """
        if isinstance(initiative_id, str):
            initiative_id = InitiativeId(initiative_id)
        if isinstance(phase_id, str):
            phase_id = PhaseId(phase_id)

        initiative = self.get_initiative(initiative_id)
        if initiative is None:
            raise ValueError(f"Initiative {initiative_id} not found")

        timestamp = datetime.now(timezone.utc)
        witness_tags = initiative.witness_tags

        # Phased initiative
        if initiative.is_phased:
            if phase_id is None:
                # Find next phase to validate
                phase_id = self._get_next_phase(initiative)
                if phase_id is None:
                    raise ValueError(f"All phases of {initiative_id} are complete")

            phase = initiative.get_phase(phase_id)
            if phase is None:
                raise ValueError(f"Phase {phase_id} not found in {initiative_id}")

            # Check dependencies
            for dep_id in phase.depends_on:
                if not self._is_phase_passed(initiative_id, dep_id):
                    raise ValueError(f"Phase {phase_id} depends on {dep_id} which has not passed")

            # Validate phase with witnessing
            proposition_results, propositions_map = self._validate_propositions_witnessed(
                initiative_id=initiative_id,
                phase_id=phase_id,
                propositions=phase.propositions,
                measurements=measurements,
                timestamp=timestamp,
                witness_tags=witness_tags,
            )

            # Check gate using pure runner
            gate_result = check_gate(phase.gate, proposition_results, propositions_map, timestamp)

            # Emit gate decision mark
            decision_id = self._emit_gate_decision_mark(
                initiative_id=initiative_id,
                phase_id=phase_id,
                gate_id=str(phase.gate.id),
                passed=gate_result.passed,
                proposition_results=gate_result.proposition_results,
                timestamp=timestamp,
                witness_tags=witness_tags,
            )

            # Attach decision_id to gate_result
            if decision_id:
                gate_result = replace(gate_result, decision_id=decision_id)

            # Track phase status
            if gate_result.passed:
                self._phase_status[(initiative_id, phase_id)] = True

        else:
            # Flat initiative
            if phase_id is not None:
                raise ValueError(f"Initiative {initiative_id} is not phased")

            if initiative.gate is None:
                raise ValueError(f"Initiative {initiative_id} has no gate")

            # Validate propositions with witnessing
            proposition_results, propositions_map = self._validate_propositions_witnessed(
                initiative_id=initiative_id,
                phase_id=None,
                propositions=initiative.propositions,
                measurements=measurements,
                timestamp=timestamp,
                witness_tags=witness_tags,
            )

            # Check gate using pure runner
            gate_result = check_gate(
                initiative.gate, proposition_results, propositions_map, timestamp
            )

            # Emit gate decision mark
            decision_id = self._emit_gate_decision_mark(
                initiative_id=initiative_id,
                phase_id=None,
                gate_id=str(initiative.gate.id),
                passed=gate_result.passed,
                proposition_results=gate_result.proposition_results,
                timestamp=timestamp,
                witness_tags=witness_tags,
            )

            # Attach decision_id to gate_result
            if decision_id:
                gate_result = replace(gate_result, decision_id=decision_id)

        # Create and save run
        run = ValidationRun(
            initiative_id=initiative_id,
            phase_id=phase_id,
            gate_result=gate_result,
            measurements=measurements,
            timestamp=timestamp,
        )

        self.store.save_run(run)
        logger.info(
            f"Validated {initiative_id}"
            + (f"/{phase_id}" if phase_id else "")
            + f": {'PASS' if run.passed else 'BLOCKED'}"
        )

        return run

    def _get_next_phase(self, initiative: Initiative) -> PhaseId | None:
        """Get the next phase to validate (first incomplete phase with satisfied deps)."""
        for phase in initiative.phases:
            # Skip completed phases
            if self._is_phase_passed(initiative.id, phase.id):
                continue

            # Check if all dependencies are satisfied
            deps_satisfied = all(
                self._is_phase_passed(initiative.id, dep_id) for dep_id in phase.depends_on
            )

            if deps_satisfied:
                return phase.id

        return None  # All phases complete or blocked

    def _is_phase_passed(self, initiative_id: InitiativeId, phase_id: PhaseId) -> bool:
        """Check if a phase has passed validation."""
        # Check in-memory cache first
        if self._phase_status.get((initiative_id, phase_id)):
            return True

        # Check store for historical run
        latest = self.store.get_latest(initiative_id, phase_id)
        if latest and latest.passed:
            self._phase_status[(initiative_id, phase_id)] = True
            return True

        return False

    # =========================================================================
    # Status & Blockers
    # =========================================================================

    def get_status(self, initiative_id: InitiativeId | str) -> InitiativeStatus:
        """
        Get the current status of an initiative.

        Returns:
            InitiativeStatus with progress and blockers
        """
        if isinstance(initiative_id, str):
            initiative_id = InitiativeId(initiative_id)

        initiative = self.get_initiative(initiative_id)
        if initiative is None:
            raise ValueError(f"Initiative {initiative_id} not found")

        # Get phases complete
        phases_complete: list[PhaseId] = []
        if initiative.is_phased:
            for phase in initiative.phases:
                if self._is_phase_passed(initiative_id, phase.id):
                    phases_complete.append(phase.id)

        # Get current phase
        current_phase_id: PhaseId | None = None
        if initiative.is_phased:
            current_phase_id = self._get_next_phase(initiative)

        # Get blockers
        blockers = self._get_initiative_blockers(initiative)

        # Get last run
        last_run = self.store.get_latest(initiative_id)

        return InitiativeStatus(
            initiative_id=initiative_id,
            current_phase_id=current_phase_id,
            phases_complete=tuple(phases_complete),
            total_phases=len(initiative.phases),
            blockers=tuple(blockers),
            last_run=last_run,
        )

    def _get_initiative_blockers(self, initiative: Initiative) -> list[Blocker]:
        """Get blockers for an initiative based on latest runs."""
        blockers: list[Blocker] = []

        if initiative.is_phased:
            # Check each phase for blockers
            for phase in initiative.phases:
                if self._is_phase_passed(initiative.id, phase.id):
                    continue

                latest = self.store.get_latest(initiative.id, phase.id)
                if latest is None:
                    # Phase not yet validated
                    continue

                for prop in phase.propositions:
                    if not prop.required:
                        continue

                    # Find result for this proposition
                    for result in latest.gate_result.proposition_results:
                        if result.proposition_id == prop.id and not result.passed:
                            gap = calculate_gap(prop, result.value)
                            blockers.append(
                                Blocker(
                                    initiative_id=initiative.id,
                                    phase_id=phase.id,
                                    proposition=prop,
                                    current_value=result.value,
                                    gap=gap,
                                )
                            )

        else:
            # Flat initiative
            latest = self.store.get_latest(initiative.id)
            if latest is None or latest.passed:
                return blockers

            for prop in initiative.propositions:
                if not prop.required:
                    continue

                for result in latest.gate_result.proposition_results:
                    if result.proposition_id == prop.id and not result.passed:
                        gap = calculate_gap(prop, result.value)
                        blockers.append(
                            Blocker(
                                initiative_id=initiative.id,
                                phase_id=None,
                                proposition=prop,
                                current_value=result.value,
                                gap=gap,
                            )
                        )

        return blockers

    def get_blockers(self) -> list[Blocker]:
        """
        Get all blockers across all initiatives.

        Returns:
            List of Blocker objects (proposition details + gap)
        """
        all_blockers: list[Blocker] = []

        for initiative in self._initiatives.values():
            blockers = self._get_initiative_blockers(initiative)
            all_blockers.extend(blockers)

        return all_blockers

    def get_history(
        self,
        initiative_id: InitiativeId | str,
        phase_id: PhaseId | str | None = None,
        limit: int = 10,
    ) -> list[ValidationRun]:
        """
        Get validation history for an initiative/phase.

        Args:
            initiative_id: The initiative to query
            phase_id: Optional phase filter
            limit: Maximum runs to return

        Returns:
            List of runs in reverse chronological order
        """
        if isinstance(initiative_id, str):
            initiative_id = InitiativeId(initiative_id)
        if isinstance(phase_id, str):
            phase_id = PhaseId(phase_id)

        return self.store.get_history(initiative_id, phase_id, limit)

    # =========================================================================
    # Cached Validation (AD-015: Proxy Handle Integration)
    # =========================================================================

    def _compute_source_hash(
        self,
        initiative_id: InitiativeId,
        phase_id: PhaseId | None,
        measurements: dict[str, float],
    ) -> str:
        """
        Compute hash for cache invalidation.

        The hash captures the validation inputs so that changes in measurements
        automatically invalidate the cache (source-aware invalidation).
        """
        data = json.dumps(
            {
                "initiative": str(initiative_id),
                "phase": str(phase_id) if phase_id else None,
                "measurements": sorted(measurements.items()),
            },
            sort_keys=True,
        )
        return hashlib.sha256(data.encode()).hexdigest()[:16]

    async def validate_cached(
        self,
        initiative_id: InitiativeId | str,
        measurements: dict[str, float],
        phase_id: PhaseId | str | None = None,
        *,
        force: bool = False,
        ttl: timedelta | None = None,
    ) -> "ProxyHandle[ValidationRun]":
        """
        Validate with caching via ProxyHandleStore.

        If a fresh handle exists and measurements haven't changed, returns cached.
        Otherwise computes and caches the validation run.

        AD-015 Philosophy:
            "The representation of an object is distinct from the object itself."
            "Computation is ALWAYS explicit. There is no auto-compute."

        The cached validation is a lens on the validation run, not the run itself.
        The original validate() remains for witnessed, uncached validation.
        validate_cached() adds caching as an explicit choice.

        IMPORTANT: Cached results do NOT re-emit marks. Marks are for actual
        computation, not cache hits. ProxyHandle events provide transparency
        for cache behavior.

        Multi-Initiative Support:
            Each (initiative_id, phase_id) pair gets its own cache slot via
            composite keys. Caching phase1 then phase2 does NOT overwrite.

        Args:
            initiative_id: The initiative to validate
            measurements: Map of proposition ID to measured value
            phase_id: For phased initiatives, which phase to validate
            force: Force recomputation even if fresh cache exists
            ttl: Cache TTL (default 5 minutes)

        Returns:
            ProxyHandle containing ValidationRun

        Raises:
            ValueError: If initiative not found or phase mismatch
        """
        from services.proxy import SourceType

        # Normalize IDs
        if isinstance(initiative_id, str):
            initiative_id = InitiativeId(initiative_id)
        if isinstance(phase_id, str):
            phase_id = PhaseId(phase_id)

        # Build composite key for multi-initiative caching
        # Format: "{initiative_id}" or "{initiative_id}:{phase_id}"
        cache_key = str(initiative_id)
        if phase_id:
            cache_key += f":{phase_id}"

        # Build source_hash for cache invalidation (measurements changed)
        source_hash = self._compute_source_hash(initiative_id, phase_id, measurements)

        # Build human-readable label
        human_label = f"Validation: {initiative_id}"
        if phase_id:
            human_label += f"/{phase_id}"

        # Define the compute function (closure captures all context)
        async def _run_validation() -> ValidationRun:
            return self.validate(initiative_id, measurements, phase_id)

        # Use ProxyHandleStore for explicit caching with composite key
        return await self.proxy_store.compute(
            source_type=SourceType.VALIDATION_RUN,
            compute_fn=_run_validation,
            key=cache_key,  # Composite key enables multi-initiative caching
            force=force,
            ttl=ttl or timedelta(minutes=5),
            human_label=human_label,
            source_hash=source_hash,
        )


# =============================================================================
# Global Engine (Module Singleton Pattern)
# =============================================================================

_engine: ValidationEngine | None = None


def get_validation_engine() -> ValidationEngine:
    """Get the global ValidationEngine instance."""
    global _engine
    if _engine is None:
        _engine = ValidationEngine()

        # Auto-load built-in initiatives
        initiatives_dir = Path(__file__).parent / "initiatives"
        if initiatives_dir.exists():
            _engine.load_initiatives_from_dir(initiatives_dir)

    return _engine


def reset_validation_engine() -> None:
    """Reset the global ValidationEngine instance (for testing)."""
    global _engine
    _engine = None
