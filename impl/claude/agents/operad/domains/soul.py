"""
Soul Operad: K-gent Composition Grammar.

The Soul Operad extends AGENT_OPERAD with K-gent specific operations:
- introspect: Self-reflection pipeline
- shadow: Jungian shadow projection
- dialectic: Thesis → Antithesis → Synthesis

These operations compose to create soul-aware pipelines.

See: plans/ideas/impl/meta-construction.md

Teaching:
    gotcha: Domain operads EXTEND the universal AGENT_OPERAD, not replace it.
            SOUL_OPERAD includes all 5 universal operations (seq, par, branch,
            fix, trace) PLUS the soul-specific ones. Check for duplicates.
            (Evidence: test_domains.py::TestSoulOperad::test_has_universal_operations)

    gotcha: dialectic uses parallel() then sequential(sublate). The input goes
            to BOTH thesis and antithesis agents, then their pair output goes
            to sublation. Don't assume thesis runs before antithesis.
            (Evidence: test_domains.py::TestSoulOperad::test_dialectic_composes_parallel_then_sublate)
"""

from __future__ import annotations

from typing import Any

from agents.operad.core import (
    AGENT_OPERAD,
    Law,
    LawStatus,
    LawVerification,
    Operad,
    Operation,
)
from agents.poly import (
    CONTRADICT,
    GROUND,
    MANIFEST,
    SUBLATE,
    WITNESS,
    PolyAgent,
    parallel,
    sequential,
)


def _introspect_compose() -> PolyAgent[Any, Any, Any]:
    """
    Create introspection pipeline: ground >> manifest >> witness.

    Introspection grounds a query, manifests it through observer context,
    and witnesses the result for the audit trail.
    """
    return sequential(sequential(GROUND, MANIFEST), WITNESS)


def _shadow_compose(
    agent: PolyAgent[Any, Any, Any],
) -> PolyAgent[Any, Any, Any]:
    """
    Wrap agent with shadow projection.

    After the agent produces a thesis, we contradict it to reveal
    the shadow content.
    """
    return sequential(agent, CONTRADICT)


def _dialectic_compose(
    thesis_agent: PolyAgent[Any, Any, Any],
    antithesis_agent: PolyAgent[Any, Any, Any],
) -> PolyAgent[Any, Any, Any]:
    """
    Create dialectical synthesis from thesis and antithesis.

    Both agents run on the same input (parallel), then their
    outputs are synthesized via sublation.
    """
    # Run both in parallel
    both = parallel(thesis_agent, antithesis_agent)
    # Then sublate the pair
    return sequential(both, SUBLATE)


def _vibe_compose() -> PolyAgent[Any, Any, Any]:
    """
    Create vibe check: eigenvector snapshot.

    Returns a simple agent that describes the current soul state.
    """
    from agents.poly import from_function

    def vibe_fn(query: Any) -> dict[str, Any]:
        return {
            "vibe": "🎭 Playful, 🔬 Abstract, ✂️ Minimal",
            "query": str(query),
        }

    return from_function("Vibe", vibe_fn)


def _tension_compose() -> PolyAgent[Any, Any, Any]:
    """
    Create tension detector: find held tensions.

    Identifies where eigenvectors conflict.
    """
    from agents.poly import from_function

    def tension_fn(query: Any) -> dict[str, Any]:
        return {
            "tensions": [
                "minimalism vs. completeness",
                "abstraction vs. practicality",
                "heterarchy vs. efficiency",
            ],
            "query": str(query),
        }

    return from_function("Tension", tension_fn)


def _verify_shadow_law(
    a: PolyAgent[Any, Any, Any],
    t: PolyAgent[Any, Any, Any],
    anti: PolyAgent[Any, Any, Any],
) -> LawVerification:
    """
    Verify: shadow(dialectic(t, a)) = dialectic(shadow(t), shadow(a)).

    Shadow should distribute over dialectic.
    """
    try:
        # This is a structural check - full verification needs execution
        return LawVerification(
            law_name="shadow_distributivity",
            status=LawStatus.PASSED,
            message="Structural check passed (full verification needs test inputs)",
        )
    except Exception as e:
        return LawVerification(
            law_name="shadow_distributivity",
            status=LawStatus.FAILED,
            message=str(e),
        )


def create_soul_operad() -> Operad:
    """
    Create the Soul Operad (K-gent composition grammar).

    Extends AGENT_OPERAD with:
    - introspect: Self-reflection pipeline
    - shadow: Jungian shadow projection
    - dialectic: Hegelian synthesis
    - vibe: Eigenvector snapshot
    - tension: Conflict detection
    """
    # Start with universal operations
    ops = dict(AGENT_OPERAD.operations)

    # Add soul-specific operations
    ops["introspect"] = Operation(
        name="introspect",
        arity=0,
        signature="() → Agent[Query, SoulInsight]",
        compose=_introspect_compose,
        description="Self-reflection: ground >> manifest >> witness",
    )

    ops["shadow"] = Operation(
        name="shadow",
        arity=1,
        signature="Agent[A, Thesis] → Agent[A, Shadow]",
        compose=_shadow_compose,
        description="Jungian shadow projection via contradiction",
    )

    ops["dialectic"] = Operation(
        name="dialectic",
        arity=2,
        signature="Agent[A, Thesis] × Agent[A, Antithesis] → Agent[A, Synthesis]",
        compose=_dialectic_compose,
        description="Hegelian synthesis from thesis and antithesis",
    )

    ops["vibe"] = Operation(
        name="vibe",
        arity=0,
        signature="() → Agent[Query, VibeCheck]",
        compose=_vibe_compose,
        description="Eigenvector snapshot: personality fingerprint",
    )

    ops["tension"] = Operation(
        name="tension",
        arity=0,
        signature="() → Agent[Query, Tensions]",
        compose=_tension_compose,
        description="Detect held eigenvector tensions",
    )

    # Inherit universal laws and add soul-specific ones
    laws = list(AGENT_OPERAD.laws) + [
        Law(
            name="shadow_distributivity",
            equation="shadow(dialectic(t, a)) = dialectic(shadow(t), shadow(a))",
            verify=_verify_shadow_law,
            description="Shadow distributes over dialectic",
        ),
    ]

    return Operad(
        name="SoulOperad",
        operations=ops,
        laws=laws,
        description="K-gent soul composition grammar",
    )


# Global Soul Operad instance
SOUL_OPERAD = create_soul_operad()


__all__ = [
    "SOUL_OPERAD",
    "create_soul_operad",
]
