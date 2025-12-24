#!/usr/bin/env python3
"""
Debug a single categorical probe to see exactly what's happening.

Shows all intermediate results: raw LLM responses, extracted answers,
identity test comparisons, claim extraction, contradiction checks.
"""

from __future__ import annotations

import asyncio
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from agents.k.llm import create_llm_client
from services.categorical import (
    MonadProbe,
    SheafDetector,
    Problem,
    ProblemSet,
)


def print_section(title: str) -> None:
    print(f"\n{'='*60}")
    print(f"  {title}")
    print(f"{'='*60}\n")


async def debug_problem(problem: Problem, n_samples: int = 2) -> None:
    """Run probes on a single problem with full debug output."""

    print_section("PROBLEM")
    print(f"ID: {problem.id}")
    print(f"Question: {problem.question}")
    print(f"Expected Answer: {problem.answer}")
    print(f"Type: {problem.problem_type}")

    # Create LLM client
    llm = create_llm_client(verbose=False)
    print(f"\nUsing model: {llm._model}")

    # =========================================================================
    # PHASE 1: MONAD IDENTITY TESTS
    # =========================================================================
    print_section("PHASE 1: MONAD IDENTITY TESTS")

    probe = MonadProbe(
        llm=llm,
        system_prompt="You are a helpful assistant. Answer concisely.",
        temperature=0.0,
    )

    # Get base answers
    print(f"Getting {n_samples} base answers...")
    base_responses = []
    base_extracted = []

    for i in range(n_samples):
        response = await llm.generate(
            system="You are a helpful assistant. Answer concisely.",
            user=problem.question,
            temperature=0.0,
        )
        text = response.text if hasattr(response, "text") else str(response)
        extracted = probe._extract_answer(text)
        base_responses.append(text)
        base_extracted.append(extracted)
        print(f"\n  Sample {i+1} raw response:\n    {text[:200]}...")
        print(f"  Sample {i+1} extracted answer: '{extracted}'")

    from collections import Counter
    base_mode = Counter(base_extracted).most_common(1)[0][0]
    print(f"\n  BASE MODE (consensus): '{base_mode}'")
    print(f"  Matches expected '{problem.answer}'? {base_mode == problem.answer or problem.answer in base_mode}")

    # Test identity with prefixes
    print("\n--- Testing Left Identity (Prefixes) ---")
    prefixes = [
        "Let me think step by step. ",
        "I'll work through this carefully. ",
        "Thinking about this problem: ",
    ]

    identity_results = []
    for prefix in prefixes:
        modified_q = prefix + problem.question
        print(f"\n  Prefix: '{prefix[:30]}...'")

        response = await llm.generate(
            system="You are a helpful assistant. Answer concisely.",
            user=modified_q,
            temperature=0.0,
        )
        text = response.text if hasattr(response, "text") else str(response)
        extracted = probe._extract_answer(text)

        print(f"    Raw response: {text[:150]}...")
        print(f"    Extracted: '{extracted}'")
        print(f"    Base was: '{base_mode}'")
        passed = extracted == base_mode
        print(f"    PASSED: {passed}")
        identity_results.append(("prefix", prefix, passed, extracted))

    # Test identity with suffixes
    print("\n--- Testing Right Identity (Suffixes) ---")
    suffixes = [
        " Please be precise.",
        " Show your work.",
        " Think carefully.",
    ]

    for suffix in suffixes:
        modified_q = problem.question + suffix
        print(f"\n  Suffix: '{suffix}'")

        response = await llm.generate(
            system="You are a helpful assistant. Answer concisely.",
            user=modified_q,
            temperature=0.0,
        )
        text = response.text if hasattr(response, "text") else str(response)
        extracted = probe._extract_answer(text)

        print(f"    Raw response: {text[:150]}...")
        print(f"    Extracted: '{extracted}'")
        print(f"    Base was: '{base_mode}'")
        passed = extracted == base_mode
        print(f"    PASSED: {passed}")
        identity_results.append(("suffix", suffix, passed, extracted))

    # Summary
    n_passed = sum(1 for r in identity_results if r[2])
    identity_score = n_passed / len(identity_results)
    print(f"\n  IDENTITY SCORE: {n_passed}/{len(identity_results)} = {identity_score:.2f}")

    # =========================================================================
    # PHASE 2: SHEAF COHERENCE
    # =========================================================================
    print_section("PHASE 2: SHEAF COHERENCE")

    # Use the first base response as the trace
    trace = base_responses[0]
    print(f"Analyzing trace:\n{trace}\n")

    detector = SheafDetector(
        llm=llm,
        system_prompt="You are a precise logical analyzer.",
        temperature=0.0,
    )

    # Extract claims
    print("--- Extracting Claims ---")
    claims = await detector.extract_claims(trace)
    print(f"Found {len(claims)} claims:\n")
    for i, claim in enumerate(claims):
        print(f"  Claim {i+1}: {claim.content}")
        print(f"           Context: {claim.context}\n")

    # Check contradictions
    if len(claims) >= 2:
        print("--- Checking Contradictions ---")
        violations = []
        for i, claim_a in enumerate(claims):
            for j, claim_b in enumerate(claims[i+1:], start=i+1):
                print(f"\n  Checking: Claim {i+1} vs Claim {j+1}")
                contradicts, explanation = await detector.check_contradiction(claim_a, claim_b)
                print(f"    Contradicts? {contradicts}")
                print(f"    Explanation: {explanation[:100]}...")
                if contradicts:
                    violations.append((i, j, explanation))

        coherence_score = 1.0 - (len(violations) / (len(claims) * (len(claims)-1) / 2))
        print(f"\n  COHERENCE SCORE: {coherence_score:.2f} ({len(violations)} violations)")
    else:
        print("  Not enough claims to check coherence")
        coherence_score = 1.0

    # =========================================================================
    # SUMMARY
    # =========================================================================
    print_section("SUMMARY")
    print(f"Problem: {problem.id}")
    print(f"Expected answer: {problem.answer}")
    print(f"LLM answer: {base_mode}")
    print(f"Correct: {problem.answer in base_mode or base_mode in problem.answer}")
    print(f"Identity score: {identity_score:.2f}")
    print(f"Coherence score: {coherence_score:.2f}")


async def main():
    # Load problems
    data_path = Path(__file__).parent.parent / "data" / "categorical_phase1_problems.json"
    problem_set = ProblemSet.from_json(data_path)

    # Pick first math problem
    problem = problem_set.problems[0]

    await debug_problem(problem, n_samples=2)


if __name__ == "__main__":
    asyncio.run(main())
