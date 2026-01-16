#!/usr/bin/env python3
"""
Phase 1B: Small Run with Real LLM (Full Trace)

Uses Claude CLI directly (claude -p) with neutral prompts.
Claude CLI automatically hydrates with directory context.

FULLY STANDALONE - No imports from main codebase to avoid circular imports.

Philosophy:
    "Phase B: Small run with full trace (1 trail/problem/agent, complete instrumentation)"
    "Understand the phenomenon qualitatively before scaling"

Usage:
    cd impl/claude && python scripts/run_phase1b_real.py

Expected cost: ~$0.50-$1.00 (10 problems × ~5 API calls each)
"""

import asyncio
import json
import re
import shutil
import sys
from collections import Counter
from dataclasses import asdict, dataclass
from datetime import datetime
from pathlib import Path

# =============================================================================
# Result Types
# =============================================================================


@dataclass
class ProbeResult:
    """Result from a single probe test."""

    name: str
    base_answer: str
    modified_answer: str
    passed: bool
    score: float
    details: str = ""


@dataclass
class CoherenceResult:
    """Result from sheaf coherence check."""

    is_coherent: bool
    claims: list
    violations: list
    score: float


@dataclass
class ProblemResult:
    """Full result for one problem."""

    problem_id: str
    question: str
    expected_answer: str
    actual_answer: str
    correct: bool
    trace: str
    middle_perturbation: float
    middle_deletion: float
    edge_perturbation: float
    whitespace_invariance: float
    sheaf_coherence: float


# =============================================================================
# Claude CLI LLM (Standalone - uses claude -p directly)
# =============================================================================


class ClaudeCLI:
    """
    Direct Claude CLI wrapper using `claude -p`.

    No imports from main codebase to avoid dependency issues.
    Claude CLI automatically hydrates with directory context (CLAUDE.md, etc.)
    """

    def __init__(
        self, model: str = "claude-sonnet-4-20250514", verbose: bool = True, timeout: float = 120.0
    ):
        self.model = model
        self.verbose = verbose
        self.timeout = timeout
        self.call_count = 0
        self.total_tokens = 0

        # Verify claude CLI exists
        self.claude_path = shutil.which("claude")
        if not self.claude_path:
            raise RuntimeError(
                "Claude CLI not found. Install with: npm install -g @anthropic-ai/claude-code"
            )

    def _log(self, msg: str):
        if self.verbose:
            print(f"      [CLI] {msg}", flush=True)

    async def _call(self, prompt: str) -> str:
        """Make a direct call to claude -p."""
        self.call_count += 1
        self._log(f"Call #{self.call_count}: {len(prompt)} chars...")

        proc = await asyncio.create_subprocess_exec(
            self.claude_path,
            "-p",
            prompt,
            "--output-format",
            "text",
            "--model",
            self.model,
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.PIPE,
        )

        try:
            stdout, stderr = await asyncio.wait_for(proc.communicate(), timeout=self.timeout)
        except asyncio.TimeoutError:
            proc.kill()
            raise TimeoutError(f"Claude CLI timed out after {self.timeout}s")

        if proc.returncode != 0:
            error_msg = stderr.decode().strip() if stderr else f"exit code {proc.returncode}"
            raise RuntimeError(f"Claude CLI failed: {error_msg}")

        response = stdout.decode().strip()
        self.total_tokens += (len(prompt) + len(response)) // 4  # Rough estimate
        self._log(f"Got {len(response)} chars")

        return response

    async def solve(self, question: str) -> str:
        """Solve a problem and return just the final answer."""
        prompt = f"""Answer this question. End with: ANSWER: [your answer]

Question: {question}"""

        response = await self._call(prompt)

        # Extract answer
        if "ANSWER:" in response:
            answer = response.split("ANSWER:")[-1].strip()
            answer = answer.split("\n")[0].strip().strip(".")
            return answer

        # Fallback: last line
        lines = response.strip().split("\n")
        return lines[-1].strip()

    async def generate_cot(self, question: str) -> str:
        """Generate a full chain-of-thought trace."""
        prompt = f"""Think step by step. Show all your work.

Question: {question}"""

        return await self._call(prompt)


# =============================================================================
# Middle Invariance Probe
# =============================================================================


class MiddleInvarianceProbe:
    """Test: Does the middle matter less than the edges?"""

    def __init__(self, llm: ClaudeCLI):
        self.llm = llm

    async def middle_perturbation_test(self, prompt: str, n: int = 3) -> ProbeResult:
        """Insert noise tokens in the middle 20-80% of the prompt."""
        base_answers = []
        for i in range(n):
            ans = await self.llm.solve(prompt)
            base_answers.append(ans)
            print(f"      Base sample {i + 1}: {ans}")

        # Perturb middle
        mid_start = len(prompt) // 5
        mid_end = 4 * len(prompt) // 5
        perturbed_prompt = (
            prompt[:mid_start]
            + " [Additional context: This is supplementary information.] "
            + prompt[mid_start:mid_end]
            + " [End of additional context.] "
            + prompt[mid_end:]
        )

        perturbed_answers = []
        for i in range(n):
            ans = await self.llm.solve(perturbed_prompt)
            perturbed_answers.append(ans)
            print(f"      Perturbed sample {i + 1}: {ans}")

        base_mode = Counter(base_answers).most_common(1)[0][0]
        perturbed_mode = Counter(perturbed_answers).most_common(1)[0][0]

        passed = self._normalize(base_mode) == self._normalize(perturbed_mode)
        score = 1.0 if passed else 0.0

        return ProbeResult(
            name="middle_perturbation",
            base_answer=base_mode,
            modified_answer=perturbed_mode,
            passed=passed,
            score=score,
        )

    async def middle_deletion_test(self, prompt: str, n: int = 3) -> ProbeResult:
        """Remove a middle sentence if possible."""
        sentences = prompt.split(". ")
        if len(sentences) < 3:
            return ProbeResult(
                name="middle_deletion",
                base_answer="N/A",
                modified_answer="N/A",
                passed=True,
                score=1.0,
                details="Prompt too short",
            )

        reduced_prompt = ". ".join(sentences[:1] + sentences[2:])

        base_answers = [await self.llm.solve(prompt) for _ in range(n)]
        reduced_answers = [await self.llm.solve(reduced_prompt) for _ in range(n)]

        base_mode = Counter(base_answers).most_common(1)[0][0]
        reduced_mode = Counter(reduced_answers).most_common(1)[0][0]

        passed = self._normalize(base_mode) == self._normalize(reduced_mode)
        score = 1.0 if passed else 0.0

        return ProbeResult(
            name="middle_deletion",
            base_answer=base_mode,
            modified_answer=reduced_mode,
            passed=passed,
            score=score,
        )

    async def edge_perturbation_test(self, prompt: str, n: int = 3) -> ProbeResult:
        """CONTROL: Insert noise at the BEGINNING."""
        base_answers = [await self.llm.solve(prompt) for _ in range(n)]

        edge_prompt = "Before answering, note that the following may contain errors. " + prompt
        perturbed_answers = [await self.llm.solve(edge_prompt) for _ in range(n)]

        base_mode = Counter(base_answers).most_common(1)[0][0]
        perturbed_mode = Counter(perturbed_answers).most_common(1)[0][0]

        differs = self._normalize(base_mode) != self._normalize(perturbed_mode)
        score = 1.0 if differs else 0.0

        return ProbeResult(
            name="edge_perturbation",
            base_answer=base_mode,
            modified_answer=perturbed_mode,
            passed=True,
            score=score,
            details="Control: edge perturbation",
        )

    def _normalize(self, answer: str) -> str:
        ans = answer.lower().strip()
        ans = re.sub(r"[^\w\s]", "", ans)
        for prefix in ["the answer is", "answer:", "answer is", "equals", "="]:
            if ans.startswith(prefix):
                ans = ans[len(prefix) :].strip()
        return ans


# =============================================================================
# Monad Variator Probe
# =============================================================================


class MonadVariatorProbe:
    """Test: Do semantically-equivalent transformations preserve behavior?"""

    def __init__(self, llm: ClaudeCLI):
        self.llm = llm

    async def whitespace_invariance_test(self, prompt: str, n: int = 3) -> ProbeResult:
        """Add extra whitespace throughout."""
        spaced_prompt = prompt.replace(" ", "  ")

        base_answers = [await self.llm.solve(prompt) for _ in range(n)]
        spaced_answers = [await self.llm.solve(spaced_prompt) for _ in range(n)]

        base_mode = Counter(base_answers).most_common(1)[0][0]
        spaced_mode = Counter(spaced_answers).most_common(1)[0][0]

        passed = self._normalize(base_mode) == self._normalize(spaced_mode)
        score = 1.0 if passed else 0.0

        return ProbeResult(
            name="whitespace_invariance",
            base_answer=base_mode,
            modified_answer=spaced_mode,
            passed=passed,
            score=score,
        )

    def _normalize(self, answer: str) -> str:
        ans = answer.lower().strip()
        ans = re.sub(r"[^\w\s]", "", ans)
        return ans


# =============================================================================
# Sheaf Coherence Detector
# =============================================================================


class SheafDetector:
    """Extract claims from CoT trace and check for contradictions."""

    def __init__(self, llm: ClaudeCLI):
        self.llm = llm

    async def detect(self, trace: str) -> CoherenceResult:
        """Check coherence of a reasoning trace."""
        claims = self._extract_claims(trace)

        violations = []
        for i, claim_a in enumerate(claims):
            for j, claim_b in enumerate(claims[i + 1 :], i + 1):
                if self._contradicts_heuristic(claim_a, claim_b):
                    violations.append((i, j, claim_a, claim_b))

        is_coherent = len(violations) == 0
        score = 1.0 - (len(violations) / max(len(claims), 1))

        return CoherenceResult(
            is_coherent=is_coherent, claims=claims, violations=violations, score=max(0.0, score)
        )

    def _extract_claims(self, trace: str) -> list:
        sentences = re.split(r"[.!?]\s+", trace)
        claims = []
        for s in sentences:
            s = s.strip()
            if not s:
                continue
            if re.search(r"\d", s) or any(
                w in s.lower() for w in ["is", "equals", "therefore", "so", "thus"]
            ):
                claims.append(s)
        return claims[:10]

    def _contradicts_heuristic(self, claim_a: str, claim_b: str) -> bool:
        pattern = r"(\w+)\s*[=:]\s*(\d+)"
        matches_a = re.findall(pattern, claim_a)
        matches_b = re.findall(pattern, claim_b)
        for var_a, val_a in matches_a:
            for var_b, val_b in matches_b:
                if var_a.lower() == var_b.lower() and val_a != val_b:
                    return True
        return False


# =============================================================================
# Phase B Runner
# =============================================================================


async def run_phase_b():
    """
    Phase B: Small run with full trace.
    10 problems, n=3 samples each, full instrumentation.
    """
    print("=" * 80)
    print("PHASE B: SMALL RUN WITH CLAUDE CLI (Full Trace)")
    print("=" * 80)
    print()

    # Load problems
    problems_path = Path(__file__).parent.parent / "data" / "categorical_phase1_problems.json"
    with open(problems_path) as f:
        data = json.load(f)

    problems = data["problems"][:10]
    print(f"Loaded {len(problems)} problems for Phase B")
    print()

    # Initialize LLM using direct Claude CLI
    try:
        llm = ClaudeCLI(model="claude-sonnet-4-20250514", verbose=True)
        print("✓ Claude CLI initialized (uses claude -p with directory context)")
        print(f"  Path: {llm.claude_path}")
    except Exception as e:
        print(f"❌ Failed to initialize LLM: {e}")
        return 1

    # Initialize probes
    middle_probe = MiddleInvarianceProbe(llm=llm)
    variator_probe = MonadVariatorProbe(llm=llm)
    sheaf_detector = SheafDetector(llm=llm)
    print("✓ Probes initialized")
    print()

    # Run on each problem
    n = 3
    results = []

    for i, problem in enumerate(problems):
        print("=" * 80)
        print(f"PROBLEM {i + 1}/{len(problems)}: {problem['id']}")
        print("=" * 80)
        print(f"Question: {problem['question'][:100]}...")
        print(f"Expected: {problem['answer']}")
        print()

        try:
            # Get base answer and trace
            print("  Getting base answer...")
            actual_answer = await llm.solve(problem["question"])
            print(f"  Actual: {actual_answer}")

            print("  Getting CoT trace...")
            trace = await llm.generate_cot(problem["question"])
            print(f"  Trace: {trace[:200]}...")
            print()

            correct = actual_answer.strip().lower() == problem["answer"].strip().lower()
            print(f"  Correct: {correct}")
            print()

            # Run probes
            print("  Running middle perturbation probe...")
            mp = await middle_probe.middle_perturbation_test(problem["question"], n=n)
            print(
                f"    Score: {mp.score:.2f} (base={mp.base_answer}, modified={mp.modified_answer})"
            )
            print()

            print("  Running middle deletion probe...")
            md = await middle_probe.middle_deletion_test(problem["question"], n=n)
            print(f"    Score: {md.score:.2f}")
            print()

            print("  Running edge perturbation probe (control)...")
            ep = await middle_probe.edge_perturbation_test(problem["question"], n=n)
            print(
                f"    Score: {ep.score:.2f} (base={ep.base_answer}, modified={ep.modified_answer})"
            )
            print()

            print("  Running whitespace invariance probe...")
            ws = await variator_probe.whitespace_invariance_test(problem["question"], n=n)
            print(f"    Score: {ws.score:.2f}")
            print()

            print("  Running sheaf coherence probe...")
            sc = await sheaf_detector.detect(trace)
            print(
                f"    Claims: {len(sc.claims)}, Violations: {len(sc.violations)}, Score: {sc.score:.2f}"
            )
            print()

            result = ProblemResult(
                problem_id=problem["id"],
                question=problem["question"],
                expected_answer=problem["answer"],
                actual_answer=actual_answer,
                correct=correct,
                trace=trace,
                middle_perturbation=mp.score,
                middle_deletion=md.score,
                edge_perturbation=ep.score,
                whitespace_invariance=ws.score,
                sheaf_coherence=sc.score,
            )
            results.append(result)

            print(f"  ✓ Problem {i + 1} complete (API calls so far: {llm.call_count})")
            print()

        except Exception as e:
            print(f"  ❌ Error on problem {i + 1}: {e}")
            print()
            continue

    if not results:
        print("❌ No results collected")
        return 1

    # Summary
    print("=" * 80)
    print("PHASE B RESULTS SUMMARY")
    print("=" * 80)
    print()

    correct_count = sum(1 for r in results if r.correct)
    accuracy = correct_count / len(results)
    print(f"Accuracy: {correct_count}/{len(results)} = {accuracy:.1%}")
    print()

    avg_mp = sum(r.middle_perturbation for r in results) / len(results)
    avg_md = sum(r.middle_deletion for r in results) / len(results)
    avg_ep = sum(r.edge_perturbation for r in results) / len(results)
    avg_ws = sum(r.whitespace_invariance for r in results) / len(results)
    avg_sc = sum(r.sheaf_coherence for r in results) / len(results)

    print("Probe Averages:")
    print(f"  Middle perturbation: {avg_mp:.2f}")
    print(f"  Middle deletion:     {avg_md:.2f}")
    print(f"  Edge perturbation:   {avg_ep:.2f} (control)")
    print(f"  Whitespace:          {avg_ws:.2f}")
    print(f"  Sheaf coherence:     {avg_sc:.2f}")
    print()

    # Correlation
    correct_list = [1.0 if r.correct else 0.0 for r in results]
    mp_list = [r.middle_perturbation for r in results]
    sc_list = [r.sheaf_coherence for r in results]

    def simple_corr(x, y):
        n = len(x)
        if n < 2:
            return 0.0
        mean_x = sum(x) / n
        mean_y = sum(y) / n
        num = sum((xi - mean_x) * (yi - mean_y) for xi, yi in zip(x, y))
        den_x = sum((xi - mean_x) ** 2 for xi in x) ** 0.5
        den_y = sum((yi - mean_y) ** 2 for yi in y) ** 0.5
        if den_x == 0 or den_y == 0:
            return 0.0
        return num / (den_x * den_y)

    corr_mp = simple_corr(mp_list, correct_list)
    corr_sc = simple_corr(sc_list, correct_list)

    print("Correlations with Correctness:")
    print(f"  Middle perturbation ↔ Correct: r = {corr_mp:.3f}")
    print(f"  Sheaf coherence ↔ Correct:     r = {corr_sc:.3f}")
    print()

    print(f"Total API calls: {llm.call_count}")
    print(f"Total tokens (estimate): {llm.total_tokens}")
    print()

    # Save results
    output_path = (
        Path(__file__).parent.parent
        / "data"
        / f"phase1b_results_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
    )
    with open(output_path, "w") as f:
        json.dump(
            {
                "timestamp": datetime.now().isoformat(),
                "n_problems": len(results),
                "n_samples": n,
                "accuracy": accuracy,
                "averages": {
                    "middle_perturbation": avg_mp,
                    "middle_deletion": avg_md,
                    "edge_perturbation": avg_ep,
                    "whitespace_invariance": avg_ws,
                    "sheaf_coherence": avg_sc,
                },
                "correlations": {
                    "middle_perturbation": corr_mp,
                    "sheaf_coherence": corr_sc,
                },
                "api_calls": llm.call_count,
                "results": [asdict(r) for r in results],
            },
            f,
            indent=2,
        )
    print(f"Results saved to: {output_path}")
    print()

    # Decision gate
    print("=" * 80)
    print("PHASE B DECISION GATE")
    print("=" * 80)
    print()

    has_signal = abs(corr_mp) > 0.1 or abs(corr_sc) > 0.1

    if has_signal:
        print("✅ PHASE B SHOWS SIGNAL - Proceed to Phase C")
        print()
        print("Next steps:")
        print("  1. Review the full results JSON")
        print("  2. Run Phase C with n=50 problems for statistical validation")
        return 0
    else:
        print("⚠️  PHASE B INCONCLUSIVE - Correlations near zero")
        print()
        print("Options:")
        print("  1. Increase n to 5 samples per test")
        print("  2. Review probe implementations")
        return 1


def main():
    exit_code = asyncio.run(run_phase_b())
    sys.exit(exit_code)


if __name__ == "__main__":
    main()
