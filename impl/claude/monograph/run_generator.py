#!/usr/bin/env python3
"""
Run the monograph generator to create the complete work.
"""

import asyncio
import sys
from pathlib import Path

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))

from monograph.generator import MonographGenerator, MonographConfig


async def main():
    """Generate the monograph."""
    print("\n" + "="*80)
    print("ADVANCED MONOGRAPH GENERATION SYSTEM")
    print("Multi-Agent Scholarly Writing with Dialectical Feedback")
    print("="*80 + "\n")

    config = MonographConfig(
        title="Process Ontology: The Primacy of Transformation",
        theme="A Categorical Journey Through Mathematics, Science, Philosophy, and Psychology",
        parts=5,
        iterations_per_part=1,
        entropy_budget=0.08,  # Accursed Share for creative exploration
    )

    generator = MonographGenerator(config)

    print("Initializing agents:")
    print("  ✓ Mathematician (AXIOM → PROOF → GENERALIZE → ABSTRACT)")
    print("  ✓ Scientist (OBSERVE → HYPOTHESIZE → EXPERIMENT → MODEL)")
    print("  ✓ Philosopher (QUESTION → DIALECTIC → SYNTHESIZE → CRITIQUE)")
    print("  ✓ Psychologist (PHENOMENOLOGY → MECHANISM → DEVELOPMENT → INTEGRATION)")
    print("  ✓ Synthesizer (GATHER → WEAVE → UNIFY → TRANSCEND)")
    print("\nOperad laws verified:")

    # Verify operad laws
    law_results = generator.operad.verify_laws()
    for law_name, holds in law_results.items():
        status = "✓" if holds else "✗"
        print(f"  {status} {law_name}")

    print("\n" + "-"*80)
    print("Beginning generation...\n")

    try:
        monograph = await generator.generate()

        # Statistics
        char_count = len(monograph)
        word_count = len(monograph.split())
        pages = word_count // 250  # Estimate: 250 words/page

        print("\n" + "="*80)
        print("GENERATION COMPLETE")
        print("="*80)
        print(f"\nStatistics:")
        print(f"  Characters: {char_count:,}")
        print(f"  Words: {word_count:,}")
        print(f"  Estimated pages: {pages:,}")
        print(f"  Parts generated: {len(generator.parts)}")
        print(f"\nOutput: generated/process_ontology_the_primacy_of_transformation.md")
        print("\n" + "="*80 + "\n")

        return monograph

    except Exception as e:
        print(f"\n✗ Error during generation: {e}")
        import traceback
        traceback.print_exc()
        return None


if __name__ == "__main__":
    result = asyncio.run(main())
    if result:
        print("SUCCESS: Monograph generated successfully!")
        sys.exit(0)
    else:
        print("FAILURE: Monograph generation failed.")
        sys.exit(1)
