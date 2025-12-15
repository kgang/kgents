#!/usr/bin/env python3
"""
Demonstration of the monograph generation system.

Shows the polynomial agents in action without generating the full monograph.
"""

import asyncio
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from monograph.agents.mathematician import MathematicianPolynomial, MathState, MathInput
from monograph.agents.scientist import ScientistPolynomial, ScienceState, ScienceInput
from monograph.agents.philosopher import PhilosopherPolynomial, PhilosophyState, PhilosophyInput
from monograph.agents.psychologist import PsychologistPolynomial, PsychologyState, PsychologyInput
from monograph.agents.synthesizer import SynthesizerPolynomial, SynthesisState, SynthesisInput
from monograph.operad.core import MonographOperad


async def demo_mathematician():
    """Demonstrate mathematician agent."""
    print("\n" + "="*80)
    print("MATHEMATICIAN AGENT DEMONSTRATION")
    print("="*80 + "\n")

    agent = MathematicianPolynomial()
    state = MathState.AXIOM

    input_data = MathInput(
        topic="Category Theory Foundations",
        depth=4,
        formalism="hybrid",
        context={"philosophical_stance": "Process ontology"}
    )

    # Show one transition
    print(f"Initial State: {state.name}\n")
    state, output = await agent.transition(state, input_data)
    print(f"→ Transitioned to: {state.name}\n")
    print("Output (first 500 chars):")
    print(output.content[:500] + "...\n")
    print(f"Theorems introduced: {output.theorems}")
    print(f"Open questions: {len(output.open_questions)}")


async def demo_scientist():
    """Demonstrate scientist agent."""
    print("\n" + "="*80)
    print("SCIENTIST AGENT DEMONSTRATION")
    print("="*80 + "\n")

    agent = ScientistPolynomial()
    state = ScienceState.OBSERVE

    input_data = ScienceInput(
        phenomenon="Self-Organization",
        domain="physics",
        empirical_grounding="theoretical"
    )

    print(f"Initial State: {state.name}\n")
    state, output = await agent.transition(state, input_data)
    print(f"→ Transitioned to: {state.name}\n")
    print("Output (first 500 chars):")
    print(output.content[:500] + "...\n")
    print(f"Phenomena described: {output.phenomena[:3]}")


async def demo_philosopher():
    """Demonstrate philosopher agent."""
    print("\n" + "="*80)
    print("PHILOSOPHER AGENT DEMONSTRATION")
    print("="*80 + "\n")

    agent = PhilosopherPolynomial()
    state = PhilosophyState.QUESTION

    input_data = PhilosophyInput(
        question="What is process?",
        tradition="process",
        rigor="formal"
    )

    print(f"Initial State: {state.name}\n")
    state, output = await agent.transition(state, input_data)
    print(f"→ Transitioned to: {state.name}\n")
    print("Output (first 500 chars):")
    print(output.content[:500] + "...\n")
    print(f"Arguments: {len(output.arguments)}")
    print(f"Objections: {len(output.objections)}")


async def demo_operad():
    """Demonstrate operad composition."""
    print("\n" + "="*80)
    print("OPERAD COMPOSITION DEMONSTRATION")
    print("="*80 + "\n")

    operad = MonographOperad()

    # Show law verification
    print("Verifying operad laws:")
    laws = operad.verify_laws()
    for law_name, holds in laws.items():
        status = "✓" if holds else "✗"
        print(f"  {status} {law_name}")

    # Show composition example
    print("\n--- Dialectic Composition Example ---\n")

    thesis = "Substance is fundamental: Objects exist independently and change accidentally."
    antithesis = "Process is fundamental: Becoming precedes being; objects are stable patterns in flux."

    composed = operad.operations["dialectic"].compose(thesis, antithesis)
    print(composed[:400] + "...")


async def demo_full_cycle():
    """Demonstrate a full generation cycle."""
    print("\n" + "="*80)
    print("FULL MULTI-AGENT CYCLE DEMONSTRATION")
    print("="*80 + "\n")

    # Initialize all agents
    agents = {
        "Mathematician": MathematicianPolynomial(),
        "Scientist": ScientistPolynomial(),
        "Philosopher": PhilosopherPolynomial(),
        "Psychologist": PsychologistPolynomial(),
        "Synthesizer": SynthesizerPolynomial(),
    }

    print("Initialized agents:")
    for name in agents:
        print(f"  ✓ {name}")

    print("\nEach agent has 4 states representing different modes of inquiry:")
    print("  • Mathematician: AXIOM → PROOF → GENERALIZE → ABSTRACT")
    print("  • Scientist: OBSERVE → HYPOTHESIZE → EXPERIMENT → MODEL")
    print("  • Philosopher: QUESTION → DIALECTIC → SYNTHESIZE → CRITIQUE")
    print("  • Psychologist: PHENOMENOLOGY → MECHANISM → DEVELOPMENT → INTEGRATION")
    print("  • Synthesizer: GATHER → WEAVE → UNIFY → TRANSCEND")

    print("\nThis implements the PolyAgent pattern (AD-006):")
    print("  Layer 1: PolyAgent - State machines with mode-dependent inputs")
    print("  Layer 2: Operad - Composition grammar")
    print("  Layer 3: Sheaf - Global coherence from local views")


async def main():
    """Run all demonstrations."""
    print("\n" + "="*80)
    print("ADVANCED MONOGRAPH GENERATION SYSTEM - DEMONSTRATION")
    print("="*80)
    print("\nThis system generates PhD-level monographs using:")
    print("  • 5 Polynomial Agents (domain specialists)")
    print("  • Compositional Operad (grammar for combining insights)")
    print("  • Iterative Refinement (dialectical feedback loops)")
    print("  • AGENTESE Integration (verb-first ontology)")

    await demo_mathematician()
    await demo_scientist()
    await demo_philosopher()
    await demo_operad()
    await demo_full_cycle()

    print("\n" + "="*80)
    print("DEMONSTRATION COMPLETE")
    print("="*80)
    print("\nTo generate the full monograph, run:")
    print("  python run_generator.py")
    print("\nThis will produce a ~200-page PhD-level work synthesizing")
    print("mathematics, science, philosophy, and psychology through")
    print("the lens of process ontology.\n")


if __name__ == "__main__":
    asyncio.run(main())
