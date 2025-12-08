#!/usr/bin/env python3
"""
Use kgents agents to create implementation plan for critical fixes.

Uses Robin (scientific companion) to reason about dependencies and priorities.
"""

import asyncio
from agents.b.robin import robin, RobinInput
from agents.k.persona import DialogueMode
from runtime.cli import ClaudeCLIRuntime


async def main() -> None:
    """Generate implementation plan using Robin agent."""

    runtime = ClaudeCLIRuntime(verbose=True, timeout=300.0)  # 5 min for complex Robin chains
    robin_agent = robin(runtime=runtime)

    query = """Create a detailed implementation plan to fix 10 critical architectural issues in kgents.

ISSUES TO FIX:

1. Type System Soundness (types.py) - CRITICAL
   Fix[A, B] should be Fix[A, A] (fixed points must map A→A)

2. FixComposedAgent Type Signature (compose.py) - CRITICAL
   Returns Agent[A, C] but should return Agent[A, B]

3. Judge Primitive Obsession (judge.py) - HIGH
   Uses boolean callbacks instead of composing 7 sub-judge agents via >>

4. Runtime Retry/Resilience (claude.py, openrouter.py) - HIGH
   Missing exponential backoff retry using Fix pattern

5. Evolution Agent Composition (evolution.py) - HIGH
   Violates morphism contract, should decompose into composable agents

6. Error Handling Transparency (base.py) - MEDIUM
   Implicit control flow, should use Result/Either types

7. Hegel Observability (hegel.py) - MEDIUM
   Missing dialectic lineage tracking metadata

8. Robin Runtime Coupling (robin.py) - MEDIUM
   Needs deterministic fallback mode when runtime unavailable

9. Parallel Resource Limits (parallel.py) - HIGH SECURITY
   DoS vulnerability, needs timeout/concurrency controls

10. Contradict Generic Coupling (contradict.py) - MEDIUM
    Should use protocol-based strategy pattern

CONTEXT:
- kgents = spec-first agent framework
- Core: Agents are morphisms (A → B)
- Bootstrap: Id, Compose, Judge, Ground, Contradict, Sublate, Fix
- Principle: "Conflicts are data" - explicit error handling

REQUIREMENTS:
- Order by dependencies (what must come first?)
- Identify breaking vs non-breaking changes
- Group into atomic commits
- Testing strategy per phase
- Parallel vs sequential work
- Spec updates needed?"""

    observations = [
        "10 critical fixes identified by evolve.py AST analysis",
        "2 are type signature bugs affecting composition laws",
        "3 are production robustness issues (retry, resources, coupling)",
        "3 are composability violations of core principles",
        "2 are observability/transparency gaps",
        "Some fixes depend on others (e.g., error types before retry logic)",
        "Type fixes are non-breaking if done carefully",
        "Judge refactor is breaking change requiring migration",
    ]

    print("🤖 Invoking Robin agent for implementation planning...")
    print("=" * 70)

    result = await robin_agent.invoke(RobinInput(
        query=query,
        observations=observations,
        domain="software architecture",
        dialogue_mode=DialogueMode.ADVISE,
        apply_dialectic=True,
    ))

    print("\n" + "=" * 70)
    print("📋 IMPLEMENTATION PLAN")
    print("=" * 70)
    print()

    if result.kgent_reflection:
        print("🎯 PERSONALIZED CONTEXT:")
        print(result.kgent_reflection)
        print()

    print("🔬 HYPOTHESES:")
    for i, h in enumerate(result.hypotheses, 1):
        print(f"\n{i}. {h.statement}")
        print(f"   Confidence: {h.confidence:.0%}")
        print(f"   Falsifiable by: {h.falsifiable_by}")

    if result.dialectic:
        print("\n" + "=" * 70)
        print("⚖️  DIALECTIC SYNTHESIS:")
        print("=" * 70)
        if result.dialectic.tension:
            print(f"\nThesis: {result.dialectic.tension.thesis}")
            print(f"Antithesis: {result.dialectic.tension.antithesis}")
        print(f"\n{result.dialectic.synthesis}")

        if result.dialectic.productive_tension:
            print(f"\n⚠️  Productive Tension: {result.dialectic.sublation_notes}")

    print("\n" + "=" * 70)
    print("📝 NARRATIVE SYNTHESIS:")
    print("=" * 70)
    print(f"\n{result.synthesis_narrative}")

    print("\n" + "=" * 70)
    print("❓ NEXT QUESTIONS TO EXPLORE:")
    print("=" * 70)
    for i, q in enumerate(result.next_questions, 1):
        print(f"{i}. {q}")

    print("\n" + "=" * 70)
    print("✅ Plan generation complete!")
    print("=" * 70)


if __name__ == "__main__":
    asyncio.run(main())
