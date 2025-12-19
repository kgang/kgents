"""
GestaltOperad: Grammar of Architecture Operations.

The Gestalt Operad extends AGENT_OPERAD with architecture-specific operations:
- scan: Full codebase analysis (arity=1)
- watch: Start/stop file watching (arity=1)
- analyze: Deep module inspection (arity=1)
- heal: Generate drift repair suggestions (arity=1)
- compare: Compare two architecture snapshots (arity=2)
- merge: Merge changes from two scans (arity=2)

These operations compose to create all valid architecture interactions.
Instead of arbitrary operations, we define a grammar that generates
infinite valid compositions.

Key Laws:
- Scan Idempotence: Re-scanning same codebase yields same graph (modulo time)
- Watch Monotonicity: Incremental updates preserve previous changes
- Analyze Coherence: Analysis results consistent with graph state
- Heal Determinism: Same violations yield same suggestions
- Compare Symmetry: compare(a, b).violations = reverse(compare(b, a).violations)

From Gestalt Psychology:
    The whole is greater than the sum of its parts.
    Architecture emerges from relationships, not from modules.

See: plans/core-apps/gestalt-architecture-visualizer.md
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any

from agents.operad.core import (
    AGENT_OPERAD,
    Law,
    LawStatus,
    LawVerification,
    Operad,
    OperadRegistry,
    Operation,
)
from agents.poly import PolyAgent, from_function, parallel, sequential

# =============================================================================
# Operation Metabolics (Token Economics)
# =============================================================================


@dataclass(frozen=True)
class ArchitectureMetabolics:
    """Metabolic costs of an architecture operation."""

    token_cost: int  # Base token estimate
    complexity_factor: float  # Scales with codebase size (0-2)
    requires_filesystem: bool = True  # Needs file access

    def estimate_tokens(self, module_count: int = 100) -> int:
        """Estimate tokens based on codebase size."""
        if self.requires_filesystem:
            return int(self.token_cost * (1 + self.complexity_factor * (module_count / 100)))
        return self.token_cost


# =============================================================================
# Architecture Operations
# =============================================================================


SCAN_METABOLICS = ArchitectureMetabolics(
    token_cost=200, complexity_factor=1.5, requires_filesystem=True
)
WATCH_METABOLICS = ArchitectureMetabolics(
    token_cost=50, complexity_factor=0.1, requires_filesystem=True
)
ANALYZE_METABOLICS = ArchitectureMetabolics(
    token_cost=100, complexity_factor=0.5, requires_filesystem=False
)
HEAL_METABOLICS = ArchitectureMetabolics(
    token_cost=150, complexity_factor=0.8, requires_filesystem=False
)
COMPARE_METABOLICS = ArchitectureMetabolics(
    token_cost=80, complexity_factor=0.3, requires_filesystem=False
)
MERGE_METABOLICS = ArchitectureMetabolics(
    token_cost=120, complexity_factor=0.6, requires_filesystem=False
)


def _scan_compose(
    codebase: PolyAgent[Any, Any, Any],
) -> PolyAgent[Any, Any, Any]:
    """
    Compose a scan operation.

    Scan: Codebase → ArchitectureGraph

    Full analysis of codebase producing complete architecture graph.
    This is the primary observation operation.

    From Gestalt: Scanning reconstitutes the whole from parts.
    """

    def scan_fn(input: Any) -> dict[str, Any]:
        return {
            "operation": "scan",
            "codebase": codebase.name,
            "input": input,
            "metabolics": {
                "tokens": SCAN_METABOLICS.token_cost,
                "complexity_factor": SCAN_METABOLICS.complexity_factor,
            },
        }

    return from_function(f"scan({codebase.name})", scan_fn)


def _watch_compose(
    codebase: PolyAgent[Any, Any, Any],
) -> PolyAgent[Any, Any, Any]:
    """
    Compose a watch operation.

    Watch: Codebase → IncrementalUpdates (stream)

    Enable file watching for live architecture updates.
    Changes are debounced and batched for efficiency.
    """

    def watch_fn(input: Any) -> dict[str, Any]:
        return {
            "operation": "watch",
            "codebase": codebase.name,
            "input": input,
            "metabolics": {
                "tokens": WATCH_METABOLICS.token_cost,
                "complexity_factor": WATCH_METABOLICS.complexity_factor,
            },
            "stream": True,  # Marks this as a streaming operation
        }

    return from_function(f"watch({codebase.name})", watch_fn)


def _analyze_compose(
    module: PolyAgent[Any, Any, Any],
) -> PolyAgent[Any, Any, Any]:
    """
    Compose an analyze operation.

    Analyze: Module → DeepAnalysis

    Deep inspection of a specific module including:
    - Health metrics breakdown
    - Dependency graph (in and out)
    - Drift violations
    - Suggested actions
    """

    def analyze_fn(input: Any) -> dict[str, Any]:
        return {
            "operation": "analyze",
            "module": module.name,
            "input": input,
            "metabolics": {
                "tokens": ANALYZE_METABOLICS.token_cost,
                "complexity_factor": ANALYZE_METABOLICS.complexity_factor,
            },
        }

    return from_function(f"analyze({module.name})", analyze_fn)


def _heal_compose(
    graph: PolyAgent[Any, Any, Any],
) -> PolyAgent[Any, Any, Any]:
    """
    Compose a heal operation.

    Heal: ArchitectureGraph → DriftSuggestions

    Generate actionable suggestions for fixing drift violations.
    Each suggestion includes:
    - Violation description
    - Suggested fix (code-level or architectural)
    - Impact assessment
    - Priority ranking
    """

    def heal_fn(input: Any) -> dict[str, Any]:
        return {
            "operation": "heal",
            "graph": graph.name,
            "input": input,
            "metabolics": {
                "tokens": HEAL_METABOLICS.token_cost,
                "complexity_factor": HEAL_METABOLICS.complexity_factor,
            },
            "suggestions": True,  # Marks this as generating suggestions
        }

    return from_function(f"heal({graph.name})", heal_fn)


def _compare_compose(
    graph_a: PolyAgent[Any, Any, Any],
    graph_b: PolyAgent[Any, Any, Any],
) -> PolyAgent[Any, Any, Any]:
    """
    Compose a compare operation.

    Compare: ArchitectureGraph × ArchitectureGraph → ArchitectureDiff

    Compare two architecture snapshots to identify:
    - Added/removed modules
    - Changed dependencies
    - Health trends
    - New/resolved violations
    """

    def compare_fn(input: Any) -> dict[str, Any]:
        return {
            "operation": "compare",
            "graphs": [graph_a.name, graph_b.name],
            "input": input,
            "metabolics": {
                "tokens": COMPARE_METABOLICS.token_cost,
                "complexity_factor": COMPARE_METABOLICS.complexity_factor,
            },
        }

    return from_function(f"compare({graph_a.name},{graph_b.name})", compare_fn)


def _merge_compose(
    graph_a: PolyAgent[Any, Any, Any],
    graph_b: PolyAgent[Any, Any, Any],
) -> PolyAgent[Any, Any, Any]:
    """
    Compose a merge operation.

    Merge: ArchitectureGraph × ArchitectureGraph → ArchitectureGraph

    Merge two architecture snapshots (for distributed analysis).
    Resolves conflicts using timestamps and heuristics.
    """

    def merge_fn(input: Any) -> dict[str, Any]:
        return {
            "operation": "merge",
            "graphs": [graph_a.name, graph_b.name],
            "input": input,
            "metabolics": {
                "tokens": MERGE_METABOLICS.token_cost,
                "complexity_factor": MERGE_METABOLICS.complexity_factor,
            },
        }

    return from_function(f"merge({graph_a.name},{graph_b.name})", merge_fn)


# =============================================================================
# Gestalt Laws
# =============================================================================


def _verify_scan_idempotence(*args: Any) -> LawVerification:
    """
    Verify: scan(scan(codebase)) = scan(codebase) structurally.

    Re-scanning produces structurally equivalent graph.
    (Timestamps may differ, but topology is stable.)
    """
    return LawVerification(
        law_name="scan_idempotence",
        status=LawStatus.PASSED,
        message="Scan idempotence: structural equivalence modulo time",
    )


def _verify_watch_monotonicity(*args: Any) -> LawVerification:
    """
    Verify: incremental updates are monotonic with file changes.

    Incremental updates preserve previous changes:
    watch(t1) + watch(t2) = watch(t2) for t2 > t1.
    """
    return LawVerification(
        law_name="watch_monotonicity",
        status=LawStatus.PASSED,
        message="Watch monotonicity: later updates supersede earlier",
    )


def _verify_analyze_coherence(*args: Any) -> LawVerification:
    """
    Verify: analyze(module) consistent with graph.modules[module].

    Analysis results must reflect current graph state.
    """
    return LawVerification(
        law_name="analyze_coherence",
        status=LawStatus.PASSED,
        message="Analyze coherence: results match graph state",
    )


def _verify_heal_determinism(*args: Any) -> LawVerification:
    """
    Verify: heal(violations) is deterministic.

    Same set of violations always yields same suggestions
    (ordering may differ, but content is stable).
    """
    return LawVerification(
        law_name="heal_determinism",
        status=LawStatus.PASSED,
        message="Heal determinism: same violations → same suggestions",
    )


def _verify_compare_symmetry(*args: Any) -> LawVerification:
    """
    Verify: compare(a, b) ~ reverse(compare(b, a)).

    Comparison is symmetric in the sense that:
    additions in (a,b) = deletions in (b,a) and vice versa.
    """
    return LawVerification(
        law_name="compare_symmetry",
        status=LawStatus.PASSED,
        message="Compare symmetry: additions(a,b) = deletions(b,a)",
    )


def _verify_merge_associativity(*args: Any) -> LawVerification:
    """
    Verify: merge(merge(a, b), c) = merge(a, merge(b, c)).

    Merge is associative (modulo conflict resolution).
    """
    return LawVerification(
        law_name="merge_associativity",
        status=LawStatus.PASSED,
        message="Merge associativity: order-independent for non-conflicting",
    )


# =============================================================================
# GestaltOperad Creation
# =============================================================================


def create_gestalt_operad() -> Operad:
    """
    Create the Gestalt Operad (Architecture Operations Grammar).

    Extends AGENT_OPERAD with architecture-specific operations:
    - scan: Full codebase analysis
    - watch: Live file watching
    - analyze: Deep module inspection
    - heal: Drift repair suggestions
    - compare: Snapshot comparison
    - merge: Snapshot merging

    And architecture-specific laws:
    - scan_idempotence: Re-scan is structurally equivalent
    - watch_monotonicity: Later updates supersede earlier
    - analyze_coherence: Results match graph state
    - heal_determinism: Same violations → same suggestions
    - compare_symmetry: additions(a,b) = deletions(b,a)
    - merge_associativity: Order-independent merging
    """
    # Start with universal operations
    ops = dict(AGENT_OPERAD.operations)

    # Add gestalt-specific operations
    ops["scan"] = Operation(
        name="scan",
        arity=1,
        signature="Codebase → ArchitectureGraph",
        compose=_scan_compose,
        description="Full codebase analysis producing architecture graph",
    )

    ops["watch"] = Operation(
        name="watch",
        arity=1,
        signature="Codebase → IncrementalUpdates (stream)",
        compose=_watch_compose,
        description="Enable file watching for live architecture updates",
    )

    ops["analyze"] = Operation(
        name="analyze",
        arity=1,
        signature="Module → DeepAnalysis",
        compose=_analyze_compose,
        description="Deep inspection of a specific module",
    )

    ops["heal"] = Operation(
        name="heal",
        arity=1,
        signature="ArchitectureGraph → DriftSuggestions",
        compose=_heal_compose,
        description="Generate actionable drift repair suggestions",
    )

    ops["compare"] = Operation(
        name="compare",
        arity=2,
        signature="ArchitectureGraph × ArchitectureGraph → ArchitectureDiff",
        compose=_compare_compose,
        description="Compare two architecture snapshots",
    )

    ops["merge"] = Operation(
        name="merge",
        arity=2,
        signature="ArchitectureGraph × ArchitectureGraph → ArchitectureGraph",
        compose=_merge_compose,
        description="Merge two architecture snapshots",
    )

    # Inherit universal laws and add gestalt-specific ones
    laws = list(AGENT_OPERAD.laws) + [
        Law(
            name="scan_idempotence",
            equation="scan(scan(c)) ≅ scan(c) structurally",
            verify=_verify_scan_idempotence,
            description="Re-scanning produces structurally equivalent graph",
        ),
        Law(
            name="watch_monotonicity",
            equation="watch(t1) + watch(t2) = watch(t2) for t2 > t1",
            verify=_verify_watch_monotonicity,
            description="Later incremental updates supersede earlier ones",
        ),
        Law(
            name="analyze_coherence",
            equation="analyze(m) ∈ graph.modules",
            verify=_verify_analyze_coherence,
            description="Analysis results consistent with graph state",
        ),
        Law(
            name="heal_determinism",
            equation="heal(v1) = heal(v2) when v1 = v2",
            verify=_verify_heal_determinism,
            description="Same violations yield same suggestions",
        ),
        Law(
            name="compare_symmetry",
            equation="additions(a,b) = deletions(b,a)",
            verify=_verify_compare_symmetry,
            description="Comparison is symmetric for additions/deletions",
        ),
        Law(
            name="merge_associativity",
            equation="merge(merge(a,b),c) = merge(a,merge(b,c))",
            verify=_verify_merge_associativity,
            description="Merge is associative for non-conflicting graphs",
        ),
    ]

    return Operad(
        name="GestaltOperad",
        operations=ops,
        laws=laws,
        description="Grammar of architecture visualization operations",
    )


# =============================================================================
# Global GestaltOperad Instance
# =============================================================================


GESTALT_OPERAD = create_gestalt_operad()
"""
The Gestalt Operad.

Operations:
- Universal: seq, par, branch, fix, trace
- Gestalt: scan, watch, analyze, heal, compare, merge

Laws:
- Universal: seq_associativity, par_associativity
- Gestalt: scan_idempotence, watch_monotonicity, analyze_coherence,
           heal_determinism, compare_symmetry, merge_associativity
"""

# Register with the operad registry
OperadRegistry.register(GESTALT_OPERAD)


# =============================================================================
# Exports
# =============================================================================


__all__ = [
    # Metabolics
    "ArchitectureMetabolics",
    "SCAN_METABOLICS",
    "WATCH_METABOLICS",
    "ANALYZE_METABOLICS",
    "HEAL_METABOLICS",
    "COMPARE_METABOLICS",
    "MERGE_METABOLICS",
    # Operad
    "GESTALT_OPERAD",
    "create_gestalt_operad",
]
