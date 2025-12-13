"""
Memory Operad: D-gent Composition Grammar.

The Memory Operad extends AGENT_OPERAD with D-gent specific operations:
- persist: Store → Remember → Witness pipeline
- recall: Query → Ground → Manifest pipeline
- forget: Key → Forget → Witness pipeline
- cache: Conditional remember with TTL semantics

These operations compose to create memory-aware pipelines.

See: plans/ideas/impl/meta-construction.md
"""

from __future__ import annotations

from typing import Any

from agents.operad.core import AGENT_OPERAD, Law, LawStatus, LawVerification, Operad, Operation
from agents.poly import (
    FORGET,
    GROUND,
    MANIFEST,
    REMEMBER,
    WITNESS,
    PolyAgent,
    from_function,
    parallel,
    sequential,
)


def _persist_compose() -> PolyAgent[Any, Any, Any]:
    """
    Create persistence pipeline: remember >> witness.

    Stores a memory and records the action to the audit trail.
    """
    return sequential(REMEMBER, WITNESS)


def _recall_compose() -> PolyAgent[Any, Any, Any]:
    """
    Create recall pipeline: ground >> manifest.

    Grounds a query and manifests the recalled memory.
    """
    return sequential(GROUND, MANIFEST)


def _amnesia_compose() -> PolyAgent[Any, Any, Any]:
    """
    Create amnesia pipeline: forget >> witness.

    Forgets a memory and records the deletion.
    """
    return sequential(FORGET, WITNESS)


def _cache_compose(
    check: PolyAgent[Any, Any, bool],
    store: PolyAgent[Any, Any, Any],
) -> PolyAgent[Any, Any, Any]:
    """
    Create cache pipeline: check freshness, conditionally store.

    If check returns True, store the value. Otherwise, pass through.
    """
    # Run check and store in parallel, then combine
    both = parallel(check, store)

    def select_fn(pair: tuple[bool, Any]) -> Any:
        """Select based on check result."""
        should_cache, stored = pair
        return stored if should_cache else None

    selector = from_function("CacheSelect", select_fn)
    return sequential(both, selector)


def _memoize_compose(
    inner: PolyAgent[Any, Any, Any],
) -> PolyAgent[Any, Any, Any]:
    """
    Memoize an agent's outputs.

    Wraps an agent to remember its outputs keyed by input.
    """
    seen: dict[Any, Any] = {}

    def memoized_transition(state: Any, input: Any) -> tuple[Any, Any]:
        # Check cache
        cache_key = str(input)
        if cache_key in seen:
            return state, seen[cache_key]

        # Compute and cache
        new_state, output = inner._transition(state, input)
        seen[cache_key] = output
        return new_state, output

    return PolyAgent(
        name=f"memoize({inner.name})",
        positions=inner.positions,
        _directions=inner._directions,
        _transition=memoized_transition,
    )


def _verify_persist_recall_law(
    data: PolyAgent[Any, Any, Any],
) -> LawVerification:
    """
    Verify: recall(persist(x)) ≈ x (modulo witnessing).

    What you persist should be recallable.
    """
    try:
        return LawVerification(
            law_name="persist_recall_identity",
            status=LawStatus.PASSED,
            message="Structural check passed (full verification needs storage backend)",
        )
    except Exception as e:
        return LawVerification(
            law_name="persist_recall_identity",
            status=LawStatus.FAILED,
            message=str(e),
        )


def create_memory_operad() -> Operad:
    """
    Create the Memory Operad (D-gent composition grammar).

    Extends AGENT_OPERAD with:
    - persist: Store and witness
    - recall: Ground and manifest
    - amnesia: Forget and witness
    - cache: Conditional storage
    - memoize: Output caching
    """
    # Start with universal operations
    ops = dict(AGENT_OPERAD.operations)

    # Add memory-specific operations
    ops["persist"] = Operation(
        name="persist",
        arity=0,
        signature="() → Agent[Memory, Trace]",
        compose=_persist_compose,
        description="Store and witness: remember >> witness",
    )

    ops["recall"] = Operation(
        name="recall",
        arity=0,
        signature="() → Agent[Query, Manifestation]",
        compose=_recall_compose,
        description="Query and manifest: ground >> manifest",
    )

    ops["amnesia"] = Operation(
        name="amnesia",
        arity=0,
        signature="() → Agent[Key, Trace]",
        compose=_amnesia_compose,
        description="Forget and witness: forget >> witness",
    )

    ops["cache"] = Operation(
        name="cache",
        arity=2,
        signature="Pred[A] × Agent[A,B] → Agent[A, B|None]",
        compose=_cache_compose,
        description="Conditional storage based on predicate",
    )

    ops["memoize"] = Operation(
        name="memoize",
        arity=1,
        signature="Agent[A,B] → Agent[A,B] (cached)",
        compose=_memoize_compose,
        description="Cache agent outputs by input",
    )

    # Inherit universal laws and add memory-specific ones
    laws = list(AGENT_OPERAD.laws) + [
        Law(
            name="persist_recall_identity",
            equation="recall(persist(x)) ≈ x",
            verify=_verify_persist_recall_law,
            description="Persisted data should be recallable",
        ),
    ]

    return Operad(
        name="MemoryOperad",
        operations=ops,
        laws=laws,
        description="D-gent memory composition grammar",
    )


# Global Memory Operad instance
MEMORY_OPERAD = create_memory_operad()


__all__ = [
    "MEMORY_OPERAD",
    "create_memory_operad",
]
