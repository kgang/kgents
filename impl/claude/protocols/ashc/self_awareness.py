"""
ASHC Self-Awareness: Query Interface for Derivation Structure.

Enables ASHC to query its own derivation structure, answering:
- "Am I grounded?" - Do I have principled justification for existing?
- "What justifies this component?" - Which principles derive this?
- "Am I consistent?" - Do my derivations satisfy categorical laws?
- "How did A derive from B?" - Explain the derivation chain.

Philosophy:
    "The compiler that knows itself is the compiler that trusts itself.
     Self-awareness is not introspection—it's categorical structure."

Integration:
    - Uses DerivationPath from protocols/ashc/paths/
    - Uses K-Block DAG from services/k_block/core/derivation.py
    - Uses Galois loss from services/zero_seed/galois/galois_loss.py
    - Uses Constitutional evaluator for principle scoring

See: spec/protocols/zero-seed1/ashc.md
"""

from __future__ import annotations

import logging
from dataclasses import dataclass, field
from typing import TYPE_CHECKING, Any, Protocol, runtime_checkable

from protocols.ashc.paths import (
    DerivationPath,
    LawVerificationResult,
    verify_all_laws,
    verify_associativity,
    verify_identity_left,
    verify_identity_right,
)
from services.k_block.core.derivation import DerivationDAG

if TYPE_CHECKING:
    from agents.d.schemas.derivation import DerivationPathCrystal

logger = logging.getLogger("kgents.ashc.self_awareness")


# =============================================================================
# Constants
# =============================================================================

# The 7 Constitutional Principles
CONSTITUTIONAL_PRINCIPLES = [
    "TASTEFUL",
    "CURATED",
    "ETHICAL",
    "JOY_INDUCING",
    "COMPOSABLE",
    "HETERARCHICAL",
    "GENERATIVE",
]

# Core ASHC components that must be grounded
ASHC_COMPONENTS = [
    "evidence.py",
    "adaptive.py",
    "economy.py",
    "checker.py",
    "obligation.py",
    "search.py",
    "persistence.py",
    "paths/types.py",
    "paths/composition.py",
    "paths/witness_bridge.py",
]

# Grounding thresholds
GROUNDING_LOSS_THRESHOLD = 0.5  # Max loss for a path to be considered grounded
CONSISTENCY_LOSS_THRESHOLD = 0.65  # Layer L5 (SOMATIC) threshold for consistency

# Contradiction detection (super-additive loss)
CONTRADICTION_TOLERANCE = 0.1


# =============================================================================
# Result Types
# =============================================================================


@dataclass(frozen=True)
class GroundednessResult:
    """
    Result of checking if ASHC is grounded in Constitution.

    A component is grounded if there exists a derivation path from
    at least one Constitutional principle with acceptable loss.

    Fields:
        is_grounded: True if ALL components have paths to principles
        paths_to_principles: Mapping of component -> paths to principles
        ungrounded_components: Components with no principled derivation
        overall_confidence: Combined confidence (1 - avg_loss)
    """

    is_grounded: bool
    paths_to_principles: dict[str, list[DerivationPath[Any, Any]]]
    ungrounded_components: list[str]
    overall_confidence: float

    @property
    def grounding_ratio(self) -> float:
        """Ratio of grounded components."""
        total = len(self.paths_to_principles) + len(self.ungrounded_components)
        if total == 0:
            return 1.0
        return len(self.paths_to_principles) / total


@dataclass(frozen=True)
class ConsistencyResult:
    """
    Result of verifying ASHC's internal consistency.

    Checks:
    1. Categorical laws hold (identity, associativity)
    2. No contradictions (super-additive loss)
    3. Galois loss within layer bounds
    4. Constitutional principles satisfied

    Fields:
        is_consistent: True if all checks pass
        law_violations: Categorical law failures
        contradictions: Super-additive loss detected
        galois_violations: Loss exceeds layer threshold
        principle_violations: Constitutional alignment failures
    """

    is_consistent: bool
    law_violations: list[dict[str, Any]]
    contradictions: list[dict[str, Any]]
    galois_violations: list[dict[str, Any]]
    principle_violations: list[dict[str, Any]]

    @property
    def violation_count(self) -> int:
        """Total number of violations."""
        return (
            len(self.law_violations)
            + len(self.contradictions)
            + len(self.galois_violations)
            + len(self.principle_violations)
        )


# =============================================================================
# Store Protocol (for DI)
# =============================================================================


@runtime_checkable
class DerivationStoreProtocol(Protocol):
    """Protocol for derivation path storage."""

    async def query_paths_by_source(self, source_id: str) -> list[DerivationPath[Any, Any]]:
        """Get all paths starting from a source."""
        ...

    async def query_paths_by_target(self, target_id: str) -> list[DerivationPath[Any, Any]]:
        """Get all paths ending at a target."""
        ...

    async def query_all_paths(self, limit: int = 1000) -> list[DerivationPath[Any, Any]]:
        """Get all stored paths."""
        ...

    async def save_path(self, path: DerivationPath[Any, Any]) -> str:
        """Save a path and return its ID."""
        ...


# =============================================================================
# In-Memory Store Implementation
# =============================================================================


class InMemoryDerivationStore:
    """
    In-memory implementation of DerivationStore for testing.

    For production, use Universe-backed storage via agents/d/schemas/derivation.py.
    """

    def __init__(self) -> None:
        self._paths: dict[str, DerivationPath[Any, Any]] = {}

    async def query_paths_by_source(self, source_id: str) -> list[DerivationPath[Any, Any]]:
        """Get all paths starting from a source."""
        return [p for p in self._paths.values() if p.source_id == source_id]

    async def query_paths_by_target(self, target_id: str) -> list[DerivationPath[Any, Any]]:
        """Get all paths ending at a target."""
        return [p for p in self._paths.values() if p.target_id == target_id]

    async def query_all_paths(self, limit: int = 1000) -> list[DerivationPath[Any, Any]]:
        """Get all stored paths."""
        return list(self._paths.values())[:limit]

    async def save_path(self, path: DerivationPath[Any, Any]) -> str:
        """Save a path and return its ID."""
        self._paths[path.path_id] = path
        return path.path_id

    def add_path(self, path: DerivationPath[Any, Any]) -> None:
        """Synchronously add a path (for testing)."""
        self._paths[path.path_id] = path


# =============================================================================
# ASHCSelfAwareness
# =============================================================================


@dataclass
class ASHCSelfAwareness:
    """
    Interface for ASHC to query its own derivation structure.

    This is the core self-awareness module that enables ASHC to:
    1. Check if it's grounded in constitutional principles
    2. Find which principles justify specific components
    3. Verify internal consistency (categorical laws, no contradictions)
    4. Explain derivation chains between artifacts

    Philosophy:
        "ASHC asking 'Am I grounded?' is not introspection—
         it's querying the derivation graph for paths to L1 axioms."

    Usage:
        >>> store = InMemoryDerivationStore()
        >>> dag = DerivationDAG()
        >>> self_aware = ASHCSelfAwareness(store=store, dag=dag)
        >>> result = await self_aware.am_i_grounded()
        >>> print(f"Grounded: {result.is_grounded}")
    """

    store: DerivationStoreProtocol
    dag: DerivationDAG = field(default_factory=DerivationDAG)
    components: list[str] = field(default_factory=lambda: list(ASHC_COMPONENTS))
    principles: list[str] = field(default_factory=lambda: list(CONSTITUTIONAL_PRINCIPLES))

    async def am_i_grounded(self) -> GroundednessResult:
        """
        Check if ASHC has complete derivation paths from Constitution.

        ASHC asking: "Do I have principled justification for existing?"

        Algorithm:
            1. Get all ASHC components
            2. For each component, BFS backward through store to find paths to principles
            3. A component is grounded if at least one path reaches a principle with loss < 0.5
            4. ASHC is grounded if ALL components are grounded

        Returns:
            GroundednessResult with paths and confidence
        """
        paths_to_principles: dict[str, list[DerivationPath[Any, Any]]] = {}
        ungrounded: list[str] = []
        total_loss = 0.0
        path_count = 0

        for component in self.components:
            paths = await self._find_paths_to_principles(component)

            if paths:
                # Filter to paths with acceptable loss
                valid_paths = [p for p in paths if p.galois_loss < GROUNDING_LOSS_THRESHOLD]
                if valid_paths:
                    paths_to_principles[component] = valid_paths
                    # Track loss for confidence calculation
                    for p in valid_paths:
                        total_loss += p.galois_loss
                        path_count += 1
                else:
                    ungrounded.append(component)
                    logger.debug(f"Component {component} has paths but all exceed loss threshold")
            else:
                ungrounded.append(component)
                logger.debug(f"Component {component} has no paths to principles")

        # Compute overall confidence
        if path_count > 0:
            avg_loss = total_loss / path_count
            overall_confidence = 1.0 - avg_loss
        elif ungrounded:
            overall_confidence = 1.0 - (len(ungrounded) / len(self.components))
        else:
            overall_confidence = 1.0

        is_grounded = len(ungrounded) == 0

        logger.info(
            f"Groundedness check: grounded={is_grounded}, "
            f"components={len(paths_to_principles)}/{len(self.components)}, "
            f"confidence={overall_confidence:.2f}"
        )

        return GroundednessResult(
            is_grounded=is_grounded,
            paths_to_principles=paths_to_principles,
            ungrounded_components=ungrounded,
            overall_confidence=overall_confidence,
        )

    async def what_principle_justifies(
        self, component: str
    ) -> list[tuple[str, DerivationPath[Any, Any]]]:
        """
        For a given component, find which principles justify it.

        ASHC asking: "Why do I have this component?"

        Args:
            component: Component name (e.g., "evidence.py")

        Returns:
            List of (principle_id, path) tuples showing justification
        """
        paths = await self._find_paths_to_principles(component)

        result: list[tuple[str, DerivationPath[Any, Any]]] = []
        for path in paths:
            # The source of the path should be a principle
            if path.source_id in self.principles:
                result.append((path.source_id, path))
            else:
                # Check if any witness references a principle
                for witness in path.witnesses:
                    if (
                        witness.grounding_principle
                        and witness.grounding_principle in self.principles
                    ):
                        result.append((witness.grounding_principle, path))
                        break

        logger.debug(f"Component {component} justified by {len(result)} principles")
        return result

    async def verify_self_consistency(self) -> ConsistencyResult:
        """
        Verify ASHC's derivation is internally consistent.

        Checks:
        1. All paths satisfy categorical laws (identity, associativity)
        2. No contradictory witnesses (super-additive loss)
        3. Galois loss within acceptable bounds
        4. All required principles satisfied

        Returns:
            ConsistencyResult with any violations found
        """
        law_violations: list[dict[str, Any]] = []
        contradictions: list[dict[str, Any]] = []
        galois_violations: list[dict[str, Any]] = []
        principle_violations: list[dict[str, Any]] = []

        # Get all stored paths
        all_paths = await self.store.query_all_paths()

        # 1. Check categorical laws
        for path in all_paths:
            # Identity laws
            left_result = verify_identity_left(path)
            if not left_result.passed:
                law_violations.append(
                    {
                        "path_id": path.path_id,
                        "law": "left_identity",
                        "message": left_result.message,
                        "details": left_result.details,
                    }
                )

            right_result = verify_identity_right(path)
            if not right_result.passed:
                law_violations.append(
                    {
                        "path_id": path.path_id,
                        "law": "right_identity",
                        "message": right_result.message,
                        "details": right_result.details,
                    }
                )

        # Check associativity for composable triples
        composable_triples = self._find_composable_triples(all_paths)
        for p, q, r in composable_triples:
            assoc_result = verify_associativity(p, q, r)
            if not assoc_result.passed:
                law_violations.append(
                    {
                        "paths": [p.path_id, q.path_id, r.path_id],
                        "law": "associativity",
                        "message": assoc_result.message,
                        "details": assoc_result.details,
                    }
                )

        # 2. Check for contradictions (super-additive loss)
        contradictions = await self._detect_contradictions(all_paths)

        # 3. Check Galois loss bounds
        for path in all_paths:
            if path.galois_loss > CONSISTENCY_LOSS_THRESHOLD:
                galois_violations.append(
                    {
                        "path_id": path.path_id,
                        "galois_loss": path.galois_loss,
                        "threshold": CONSISTENCY_LOSS_THRESHOLD,
                        "message": f"Loss {path.galois_loss:.2f} exceeds threshold {CONSISTENCY_LOSS_THRESHOLD}",
                    }
                )

        # 4. Check principle satisfaction (simplified - check ETHICAL floor)
        for path in all_paths:
            ethical_score = path.principle_scores.get("ETHICAL", 1.0)
            if ethical_score < 0.6:  # Amendment A floor
                principle_violations.append(
                    {
                        "path_id": path.path_id,
                        "principle": "ETHICAL",
                        "score": ethical_score,
                        "threshold": 0.6,
                        "message": f"ETHICAL score {ethical_score:.2f} below floor 0.6",
                    }
                )

        is_consistent = (
            len(law_violations) == 0
            and len(contradictions) == 0
            and len(galois_violations) == 0
            and len(principle_violations) == 0
        )

        logger.info(
            f"Consistency check: consistent={is_consistent}, "
            f"law_violations={len(law_violations)}, "
            f"contradictions={len(contradictions)}, "
            f"galois_violations={len(galois_violations)}, "
            f"principle_violations={len(principle_violations)}"
        )

        return ConsistencyResult(
            is_consistent=is_consistent,
            law_violations=law_violations,
            contradictions=contradictions,
            galois_violations=galois_violations,
            principle_violations=principle_violations,
        )

    async def explain_derivation(
        self, from_artifact: str, to_artifact: str
    ) -> list[DerivationPath[Any, Any]]:
        """
        Explain how one artifact derives from another.

        Returns the composition of paths from source to target.

        Args:
            from_artifact: Source artifact ID
            to_artifact: Target artifact ID

        Returns:
            List of paths connecting source to target (composed if necessary)
        """
        # Find all paths from source
        paths_from_source = await self.store.query_paths_by_source(from_artifact)

        # Direct path?
        direct_paths = [p for p in paths_from_source if p.target_id == to_artifact]
        if direct_paths:
            return direct_paths

        # Need to find composed path via BFS
        composed_paths: list[DerivationPath[Any, Any]] = []
        visited: set[str] = set()
        queue: list[tuple[str, DerivationPath[Any, Any] | None]] = [(from_artifact, None)]

        while queue and len(composed_paths) < 10:  # Limit results
            current, current_path = queue.pop(0)

            if current in visited:
                continue
            visited.add(current)

            # Get outgoing paths
            outgoing = await self.store.query_paths_by_source(current)

            for path in outgoing:
                if current_path is not None:
                    try:
                        # Compose paths
                        composed = current_path.compose(path)
                    except ValueError:
                        # Can't compose (target mismatch)
                        continue
                else:
                    composed = path

                if path.target_id == to_artifact:
                    # Found path to target
                    composed_paths.append(composed)
                elif path.target_id not in visited:
                    # Continue search
                    queue.append((path.target_id, composed))

        logger.debug(f"Found {len(composed_paths)} paths from {from_artifact} to {to_artifact}")
        return composed_paths

    # -------------------------------------------------------------------------
    # Private Helpers
    # -------------------------------------------------------------------------

    async def _find_paths_to_principles(self, component: str) -> list[DerivationPath[Any, Any]]:
        """
        Find all derivation paths from principles to a component.

        Uses BFS backward from component through the derivation store.
        """
        result: list[DerivationPath[Any, Any]] = []

        # Get paths ending at this component
        paths_to_component = await self.store.query_paths_by_target(component)

        for path in paths_to_component:
            # Check if source is a principle
            if path.source_id in self.principles:
                result.append(path)
            else:
                # Recursively find paths from principles to this path's source
                upstream_paths = await self._find_paths_to_principles(path.source_id)
                for upstream in upstream_paths:
                    try:
                        # Compose: principle -> intermediate -> component
                        composed = upstream.compose(path)
                        result.append(composed)
                    except ValueError:
                        # Can't compose (target mismatch)
                        pass

        # Also check DAG if available
        if component in [n.kblock_id for n in self.dag._nodes.values()]:
            if self.dag.is_grounded(component):
                # The DAG says this is grounded, create a synthetic path
                lineage = self.dag.get_lineage(component)
                if lineage:
                    # First in lineage should be near L1
                    root = lineage[-1] if lineage else component
                    if root in self.principles or (
                        root in self.dag._nodes and self.dag._nodes[root].layer == 1
                    ):
                        result.append(
                            DerivationPath.derive(
                                source_id=root,
                                target_id=component,
                                galois_loss=0.1 * len(lineage),  # Approximate
                            )
                        )

        return result

    def _find_composable_triples(
        self, paths: list[DerivationPath[Any, Any]]
    ) -> list[tuple[DerivationPath[Any, Any], DerivationPath[Any, Any], DerivationPath[Any, Any]]]:
        """Find all triples (p, q, r) where p;q and q;r are composable."""
        triples: list[
            tuple[DerivationPath[Any, Any], DerivationPath[Any, Any], DerivationPath[Any, Any]]
        ] = []

        # Build index by source and target
        by_source: dict[str, list[DerivationPath[Any, Any]]] = {}
        by_target: dict[str, list[DerivationPath[Any, Any]]] = {}

        for path in paths:
            by_source.setdefault(path.source_id, []).append(path)
            by_target.setdefault(path.target_id, []).append(path)

        # Find composable triples
        for p in paths:
            # Find q where p.target == q.source
            for q in by_source.get(p.target_id, []):
                # Find r where q.target == r.source
                for r in by_source.get(q.target_id, []):
                    triples.append((p, q, r))

        return triples[:100]  # Limit to prevent explosion

    async def _detect_contradictions(
        self, paths: list[DerivationPath[Any, Any]]
    ) -> list[dict[str, Any]]:
        """
        Detect contradictions via super-additive loss.

        Contradiction: L(A ∪ B) > L(A) + L(B) + tau

        For paths, we check if composing paths results in super-additive loss.
        """
        contradictions: list[dict[str, Any]] = []

        # Check pairs of paths that share endpoints
        by_source: dict[str, list[DerivationPath[Any, Any]]] = {}
        for path in paths:
            by_source.setdefault(path.source_id, []).append(path)

        for source_id, source_paths in by_source.items():
            if len(source_paths) < 2:
                continue

            # Check pairs
            for i, path_a in enumerate(source_paths):
                for path_b in source_paths[i + 1 :]:
                    # Super-additive check
                    # If both paths go to same target, the "combined" loss
                    # should not exceed sum + tolerance
                    if path_a.target_id == path_b.target_id:
                        combined_loss = max(path_a.galois_loss, path_b.galois_loss)
                        sum_loss = path_a.galois_loss + path_b.galois_loss

                        # For same-endpoint paths, combined shouldn't need both losses
                        # Contradiction if combined behaves super-additively
                        if combined_loss > (
                            path_a.galois_loss + CONTRADICTION_TOLERANCE
                        ) and combined_loss > (path_b.galois_loss + CONTRADICTION_TOLERANCE):
                            # Both paths are insufficient alone
                            strength = combined_loss - min(path_a.galois_loss, path_b.galois_loss)
                            if strength > CONTRADICTION_TOLERANCE:
                                contradictions.append(
                                    {
                                        "path_a": path_a.path_id,
                                        "path_b": path_b.path_id,
                                        "loss_a": path_a.galois_loss,
                                        "loss_b": path_b.galois_loss,
                                        "strength": strength,
                                        "message": f"Super-additive loss detected: {strength:.2f}",
                                    }
                                )

        return contradictions


# =============================================================================
# Factory Functions
# =============================================================================


def create_self_awareness(
    store: DerivationStoreProtocol | None = None,
    dag: DerivationDAG | None = None,
) -> ASHCSelfAwareness:
    """
    Create an ASHCSelfAwareness instance with defaults.

    Args:
        store: DerivationStore (defaults to InMemoryDerivationStore)
        dag: DerivationDAG (defaults to empty DAG)

    Returns:
        Configured ASHCSelfAwareness instance
    """
    return ASHCSelfAwareness(
        store=store or InMemoryDerivationStore(),
        dag=dag or DerivationDAG(),
    )


# =============================================================================
# Exports
# =============================================================================

__all__ = [
    # Constants
    "CONSTITUTIONAL_PRINCIPLES",
    "ASHC_COMPONENTS",
    "GROUNDING_LOSS_THRESHOLD",
    "CONSISTENCY_LOSS_THRESHOLD",
    "CONTRADICTION_TOLERANCE",
    # Result Types
    "GroundednessResult",
    "ConsistencyResult",
    # Protocol
    "DerivationStoreProtocol",
    # Implementations
    "InMemoryDerivationStore",
    "ASHCSelfAwareness",
    # Factory
    "create_self_awareness",
]
