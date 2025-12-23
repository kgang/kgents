#!/usr/bin/env python3
"""
Run Phase 1 Categorical Correlation Study.

Uses the ClaudeCLIRuntime (via void harness pattern) for LLM inference.
This validates the core kgents 2.0 hypothesis:

    "LLM reasoning failures follow patterns that category theory predicts."

Usage:
    # Quick test (5 problems)
    python scripts/run_categorical_phase1_study.py --n 5

    # Debug mode with verbose output
    python scripts/run_categorical_phase1_study.py --n 5 --verbose

    # Full study (500 problems) - WARNING: expensive!
    python scripts/run_categorical_phase1_study.py --n 500

Philosophy:
    "Measure first. Build only what measurement validates."
    "The proof IS the decision. The mark IS the witness."
"""

from __future__ import annotations

import argparse
import asyncio
import json
import sys
from datetime import datetime
from pathlib import Path

# Add impl/claude to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from agents.k.llm import ClaudeLLMClient, create_llm_client
from services.categorical import (
    CorrelationStudy,
    ProblemSet,
    StudyConfig,
    StudyResult,
)


def format_results(result: StudyResult) -> str:
    """Format study results for display."""
    lines = [
        "",
        "=" * 60,
        "CATEGORICAL PHASE 1 STUDY RESULTS",
        "=" * 60,
        "",
        f"Problems completed: {len(result.problem_results)}",
        f"Duration: {result.duration}",
        "",
        "--- MONAD IDENTITY LAW ---",
        f"  Correlation (r): {result.monad_identity_corr.correlation:.4f}",
        f"  95% CI: [{result.monad_identity_corr.ci_low:.4f}, {result.monad_identity_corr.ci_high:.4f}]",
        f"  P-value (permutation): {result.monad_identity_corr.p_value_permutation:.4f}",
        f"  Mean when correct: {result.monad_identity_corr.mean_when_correct:.4f}",
        f"  Mean when incorrect: {result.monad_identity_corr.mean_when_incorrect:.4f}",
        "",
        "--- SHEAF COHERENCE ---",
        f"  Correlation (r): {result.sheaf_coherence_corr.correlation:.4f}",
        f"  95% CI: [{result.sheaf_coherence_corr.ci_low:.4f}, {result.sheaf_coherence_corr.ci_high:.4f}]",
        f"  P-value (permutation): {result.sheaf_coherence_corr.p_value_permutation:.4f}",
        f"  Mean when correct: {result.sheaf_coherence_corr.mean_when_correct:.4f}",
        f"  Mean when incorrect: {result.sheaf_coherence_corr.mean_when_incorrect:.4f}",
        "",
        "--- COMBINED ---",
        f"  AUC-ROC: {result.combined_auc:.4f}",
    ]

    if result.baselines:
        lines.extend(
            [
                "",
                "--- BASELINES ---",
                f"  Random baseline r: {result.baselines.random_corr.correlation:.4f}",
                f"  Length baseline r: {result.baselines.length_corr.correlation:.4f}",
                f"  Δ over baseline: {result.categorical_delta:.4f}",
            ]
        )

    lines.extend(
        [
            "",
            "--- GATE STATUS ---",
            f"  Relaxed gate (original criteria): {'PASS' if result.passed_gate_relaxed else 'BLOCKED'}",
            f"  Strict gate (enhanced criteria): {'PASS' if result.passed_gate else 'BLOCKED'}",
        ]
    )

    if result.blockers:
        lines.append(f"  Blockers: {', '.join(result.blockers)}")

    lines.extend(
        [
            "",
            "=" * 60,
        ]
    )

    return "\n".join(lines)


async def main(args: argparse.Namespace) -> int:
    """Run the study."""
    print(f"\n🔬 Starting Categorical Phase 1 Study (n={args.n})")
    print(f"   Bootstrap samples: {args.bootstrap}")
    print(f"   Permutations: {args.permutations}")
    print()

    # Load problem set
    data_path = Path(__file__).parent.parent / "data" / "categorical_phase1_problems.json"
    if not data_path.exists():
        print(f"❌ Problem set not found: {data_path}")
        return 1

    problem_set = ProblemSet.from_json(data_path)
    print(f"📚 Loaded {len(problem_set.problems)} problems from {data_path.name}")

    # Create LLM client (uses ClaudeCLIRuntime)
    llm = create_llm_client(
        timeout=120.0,
        verbose=args.verbose,
    )
    print(f"🤖 Using LLM client: {type(llm).__name__}")

    # Create study with config
    config = StudyConfig(
        n_problems=args.n,
        n_samples_per_problem=args.samples,
        run_associativity=False,  # Skip for now (requires step extraction)
        temperature=0.0,  # Deterministic
        max_concurrent=args.concurrent,
        run_baselines=args.baselines,
        n_bootstrap=args.bootstrap,
        n_permutations=args.permutations,
        random_seed=args.seed,
    )

    study = CorrelationStudy(llm, problem_set)

    # Run study
    print("\n🚀 Running study...")
    try:
        result = await study.run(config)
    except Exception as e:
        print(f"❌ Study failed: {e}")
        import traceback

        traceback.print_exc()
        return 1

    # Display results
    print(format_results(result))

    # Save results to JSON
    if args.output:
        output_path = Path(args.output)
        output_path.parent.mkdir(parents=True, exist_ok=True)

        output_data = result.to_dict()
        output_data["timestamp"] = datetime.now().isoformat()
        output_data["config"] = {
            "n_problems": args.n,
            "n_samples": args.samples,
            "n_bootstrap": args.bootstrap,
            "n_permutations": args.permutations,
            "seed": args.seed,
        }

        with output_path.open("w") as f:
            json.dump(output_data, f, indent=2)

        print(f"\n💾 Results saved to: {output_path}")

    # Return exit code based on gate
    if result.passed_gate:
        print("\n✅ PHASE 1 GATE PASSED — Proceed to Phase 2")
        return 0
    else:
        print(f"\n⚠️  PHASE 1 GATE BLOCKED — {len(result.blockers)} issues to address")
        return 1


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="Run Categorical Phase 1 Correlation Study",
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )
    parser.add_argument(
        "-n",
        "--n",
        type=int,
        default=5,
        help="Number of problems to test (default: 5)",
    )
    parser.add_argument(
        "-s",
        "--samples",
        type=int,
        default=3,
        help="Samples per problem for identity tests (default: 3)",
    )
    parser.add_argument(
        "-c",
        "--concurrent",
        type=int,
        default=3,
        help="Max concurrent problems (default: 3)",
    )
    parser.add_argument(
        "-b",
        "--bootstrap",
        type=int,
        default=100,
        help="Bootstrap samples for CI (default: 100, use 1000 for production)",
    )
    parser.add_argument(
        "-p",
        "--permutations",
        type=int,
        default=1000,
        help="Permutations for p-value (default: 1000, use 10000 for production)",
    )
    parser.add_argument(
        "--seed",
        type=int,
        default=42,
        help="Random seed for reproducibility (default: 42)",
    )
    parser.add_argument(
        "--no-baselines",
        dest="baselines",
        action="store_false",
        help="Skip baseline comparisons",
    )
    parser.add_argument(
        "-o",
        "--output",
        type=str,
        help="Path to save results JSON",
    )
    parser.add_argument(
        "-v",
        "--verbose",
        action="store_true",
        help="Verbose output",
    )

    args = parser.parse_args()
    sys.exit(asyncio.run(main(args)))
