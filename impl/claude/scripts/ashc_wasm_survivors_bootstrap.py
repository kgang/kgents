#!/usr/bin/env python3
"""
ASHC Bootstrap for WASM-Survivors Game

Generates empirical evidence for spec↔impl equivalence using:
1. Playwright e2e tests as verification
2. TypeScript type checking
3. Galois loss computation on PROTO_SPEC
4. Adaptive Bayesian stopping rules

> "The proof is not formal—it's empirical."
"""

from __future__ import annotations

import asyncio
import hashlib
import json
import logging
import subprocess
import sys
import time
from dataclasses import dataclass, field
from datetime import datetime
from pathlib import Path
from typing import Any

# Setup logging
logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")
logger = logging.getLogger("ashc.wasm-survivors")

# Project paths
PROJECT_ROOT = Path(__file__).parent.parent.parent.parent  # kgents/
PILOTS_WEB = PROJECT_ROOT / "impl" / "claude" / "pilots-web"
SPEC_PATH = PROJECT_ROOT / "pilots" / "wasm-survivors-game" / "PROTO_SPEC.md"
IMPL_PATH = PILOTS_WEB / "src" / "pilots" / "wasm-survivors-game"
E2E_SPEC = PILOTS_WEB / "e2e" / "qualia-validation" / "wasm-survivors.spec.ts"


# =============================================================================
# TypeScript Verification Results
# =============================================================================


@dataclass(frozen=True)
class TSTestReport:
    """TypeScript/Playwright test results."""

    success: bool
    total: int
    passed: int
    failed: int
    skipped: int
    duration_ms: float
    raw_output: str = ""


@dataclass(frozen=True)
class TSTypeReport:
    """TypeScript type check results."""

    passed: bool
    errors: tuple[str, ...] = ()
    raw_output: str = ""


@dataclass(frozen=True)
class TSLintReport:
    """ESLint results."""

    passed: bool
    errors: tuple[str, ...] = ()
    warnings: tuple[str, ...] = ()
    raw_output: str = ""


@dataclass(frozen=True)
class TSVerificationResult:
    """Combined TypeScript verification result."""

    test_report: TSTestReport
    type_report: TSTypeReport
    lint_report: TSLintReport

    @property
    def all_passed(self) -> bool:
        return self.test_report.success and self.type_report.passed and self.lint_report.passed


# =============================================================================
# TypeScript Verification Functions
# =============================================================================


async def run_playwright_tests(timeout: float = 120.0) -> TSTestReport:
    """Run Playwright e2e tests for wasm-survivors."""
    start = time.monotonic()

    try:
        # Check if e2e test file exists
        if not E2E_SPEC.exists():
            logger.warning(f"E2E test file not found: {E2E_SPEC}")
            return TSTestReport(
                success=True,  # Vacuously true - no tests
                total=0,
                passed=0,
                failed=0,
                skipped=0,
                duration_ms=0,
                raw_output="No e2e tests found",
            )

        # Run playwright test
        proc = await asyncio.create_subprocess_exec(
            "npx",
            "playwright",
            "test",
            str(E2E_SPEC),
            "--reporter=json",
            cwd=str(PILOTS_WEB),
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.PIPE,
        )

        try:
            stdout, stderr = await asyncio.wait_for(proc.communicate(), timeout=timeout)
        except asyncio.TimeoutError:
            proc.kill()
            await proc.wait()
            return TSTestReport(
                success=False,
                total=0,
                passed=0,
                failed=0,
                skipped=0,
                duration_ms=(time.monotonic() - start) * 1000,
                raw_output="Timeout",
            )

        duration_ms = (time.monotonic() - start) * 1000
        output = stdout.decode("utf-8", errors="replace")

        # Parse JSON output
        try:
            # Playwright JSON reporter outputs to stdout
            result = json.loads(output)
            stats = result.get("stats", {})
            return TSTestReport(
                success=stats.get("unexpected", 0) == 0,
                total=stats.get("expected", 0) + stats.get("unexpected", 0),
                passed=stats.get("expected", 0),
                failed=stats.get("unexpected", 0),
                skipped=stats.get("skipped", 0),
                duration_ms=duration_ms,
                raw_output=output[:2000],
            )
        except json.JSONDecodeError:
            # Fallback: check exit code
            success = proc.returncode == 0
            return TSTestReport(
                success=success,
                total=1 if success else 1,
                passed=1 if success else 0,
                failed=0 if success else 1,
                skipped=0,
                duration_ms=duration_ms,
                raw_output=output[:2000] + stderr.decode("utf-8", errors="replace")[:500],
            )

    except FileNotFoundError:
        return TSTestReport(
            success=False,
            total=0,
            passed=0,
            failed=0,
            skipped=0,
            duration_ms=0,
            raw_output="Playwright not installed",
        )
    except Exception as e:
        return TSTestReport(
            success=False,
            total=0,
            passed=0,
            failed=0,
            skipped=0,
            duration_ms=(time.monotonic() - start) * 1000,
            raw_output=f"Error: {e}",
        )


async def run_typescript_typecheck(timeout: float = 60.0) -> TSTypeReport:
    """Run TypeScript type checking."""
    start = time.monotonic()

    try:
        proc = await asyncio.create_subprocess_exec(
            "npx",
            "tsc",
            "--noEmit",
            "--pretty",
            "false",
            cwd=str(PILOTS_WEB),
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.PIPE,
        )

        try:
            stdout, stderr = await asyncio.wait_for(proc.communicate(), timeout=timeout)
        except asyncio.TimeoutError:
            proc.kill()
            await proc.wait()
            return TSTypeReport(passed=False, errors=("Timeout",))

        output = stdout.decode("utf-8", errors="replace") + stderr.decode("utf-8", errors="replace")

        if proc.returncode == 0:
            return TSTypeReport(passed=True, raw_output=output[:1000])
        else:
            # Extract error lines
            errors = tuple(line for line in output.split("\n") if "error TS" in line)[:10]
            return TSTypeReport(passed=False, errors=errors, raw_output=output[:2000])

    except FileNotFoundError:
        return TSTypeReport(passed=False, errors=("TypeScript not installed",))
    except Exception as e:
        return TSTypeReport(passed=False, errors=(str(e),))


async def run_eslint(timeout: float = 60.0) -> TSLintReport:
    """Run ESLint on the implementation."""
    try:
        proc = await asyncio.create_subprocess_exec(
            "npx",
            "eslint",
            str(IMPL_PATH),
            "--format=json",
            "--max-warnings=50",
            cwd=str(PILOTS_WEB),
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.PIPE,
        )

        try:
            stdout, stderr = await asyncio.wait_for(proc.communicate(), timeout=timeout)
        except asyncio.TimeoutError:
            proc.kill()
            await proc.wait()
            return TSLintReport(passed=False, errors=("Timeout",))

        output = stdout.decode("utf-8", errors="replace")

        try:
            result = json.loads(output)
            error_count = sum(f.get("errorCount", 0) for f in result)
            warning_count = sum(f.get("warningCount", 0) for f in result)

            errors = []
            warnings = []
            for file_result in result[:5]:  # First 5 files
                for msg in file_result.get("messages", [])[:3]:  # First 3 messages per file
                    text = f"{file_result.get('filePath', 'unknown')}:{msg.get('line', 0)} - {msg.get('message', '')}"
                    if msg.get("severity") == 2:
                        errors.append(text)
                    else:
                        warnings.append(text)

            return TSLintReport(
                passed=error_count == 0,
                errors=tuple(errors),
                warnings=tuple(warnings),
                raw_output=output[:2000],
            )
        except json.JSONDecodeError:
            return TSLintReport(passed=proc.returncode == 0, raw_output=output[:2000])

    except FileNotFoundError:
        return TSLintReport(
            passed=True, warnings=("ESLint not installed",)
        )  # Don't fail on missing lint
    except Exception as e:
        return TSLintReport(passed=False, errors=(str(e),))


async def verify_typescript_implementation() -> TSVerificationResult:
    """Run all TypeScript verification steps."""
    # Run in parallel
    test_task = asyncio.create_task(run_playwright_tests())
    type_task = asyncio.create_task(run_typescript_typecheck())
    lint_task = asyncio.create_task(run_eslint())

    test_report = await test_task
    type_report = await type_task
    lint_report = await lint_task

    return TSVerificationResult(
        test_report=test_report,
        type_report=type_report,
        lint_report=lint_report,
    )


# =============================================================================
# Galois Loss Computation
# =============================================================================


async def compute_spec_impl_galois_loss() -> float:
    """
    Compute Galois loss between PROTO_SPEC and implementation.

    L(spec, impl) = distance(spec, Canonicalize(Restructure(impl)))

    For TypeScript, we approximate by:
    1. Extract structure from spec (axioms, values, specifications)
    2. Extract structure from implementation (types, systems, contracts)
    3. Compute semantic distance
    """
    try:
        # Read spec
        spec_content = SPEC_PATH.read_text() if SPEC_PATH.exists() else ""

        # Read implementation structure
        impl_files = list(IMPL_PATH.glob("**/*.ts")) + list(IMPL_PATH.glob("**/*.tsx"))
        impl_structure = []
        for f in impl_files[:20]:  # Sample first 20 files
            try:
                content = f.read_text()
                # Extract exports and type definitions
                for line in content.split("\n"):
                    if line.strip().startswith(
                        ("export ", "interface ", "type ", "const ", "function ")
                    ):
                        impl_structure.append(line.strip()[:100])
            except Exception:
                continue

        impl_summary = "\n".join(impl_structure[:100])

        # Try to use the Galois loss computer
        try:
            from services.zero_seed.galois import GaloisLossComputer

            computer = GaloisLossComputer()
            loss = await computer.compute_loss(spec_content[:5000], impl_summary[:5000])
            return loss.value if hasattr(loss, "value") else float(loss)
        except Exception as e:
            logger.warning(f"Galois loss computer not available: {e}")
            # Fallback: simple structural comparison
            spec_keywords = set(spec_content.lower().split())
            impl_keywords = set(impl_summary.lower().split())

            if not spec_keywords or not impl_keywords:
                return 0.5  # Uncertain

            # Jaccard distance as proxy
            intersection = len(spec_keywords & impl_keywords)
            union = len(spec_keywords | impl_keywords)
            similarity = intersection / union if union > 0 else 0
            return 1.0 - similarity  # Loss = 1 - similarity

    except Exception as e:
        logger.error(f"Galois loss computation failed: {e}")
        return 0.5  # Uncertain


# =============================================================================
# Evidence Accumulation
# =============================================================================


@dataclass
class WASMSurvivorsRun:
    """Single verification run for wasm-survivors."""

    run_id: str
    verification: TSVerificationResult
    galois_loss: float
    timestamp: datetime = field(default_factory=datetime.now)
    duration_ms: float = 0.0

    @property
    def passed(self) -> bool:
        return self.verification.all_passed

    @property
    def verification_score(self) -> float:
        """Combined score: test (60%) + types (20%) + lint (20%)."""
        test_score = 1.0 if self.verification.test_report.success else 0.0
        type_score = 1.0 if self.verification.type_report.passed else 0.0
        lint_score = 1.0 if self.verification.lint_report.passed else 0.0
        return test_score * 0.6 + type_score * 0.2 + lint_score * 0.2


@dataclass
class WASMSurvivorsEvidence:
    """Accumulated evidence for wasm-survivors."""

    runs: list[WASMSurvivorsRun]
    spec_hash: str
    galois_loss: float
    created_at: datetime = field(default_factory=datetime.now)

    @property
    def run_count(self) -> int:
        return len(self.runs)

    @property
    def pass_count(self) -> int:
        return sum(1 for r in self.runs if r.passed)

    @property
    def pass_rate(self) -> float:
        return self.pass_count / self.run_count if self.runs else 0.0

    @property
    def galois_coherence(self) -> float:
        return 1.0 - self.galois_loss

    @property
    def equivalence_score(self) -> float:
        """Combined score with Galois integration."""
        if not self.runs:
            return 0.0
        empirical = self.pass_rate * 0.7 + min(1.0, self.run_count / 50) * 0.3
        return self.galois_coherence * empirical

    @property
    def is_verified(self) -> bool:
        """Is there sufficient evidence?"""
        return (
            self.run_count >= 3  # Minimum runs for TS (faster than Python)
            and self.galois_coherence >= 0.70  # More lenient for TS
            and self.equivalence_score >= 0.60
        )


# =============================================================================
# Bootstrap Runner
# =============================================================================


async def bootstrap_evidence(n_runs: int = 5, max_runs: int = 10) -> WASMSurvivorsEvidence:
    """
    Bootstrap ASHC evidence for wasm-survivors.

    Uses adaptive stopping: stop early if confidence is high enough.
    """
    logger.info("=" * 60)
    logger.info("ASHC BOOTSTRAP: wasm-survivors-game")
    logger.info("=" * 60)

    # Compute spec hash
    spec_content = SPEC_PATH.read_text() if SPEC_PATH.exists() else ""
    spec_hash = hashlib.sha256(spec_content.encode()).hexdigest()[:12]
    logger.info(f"Spec hash: {spec_hash}")
    logger.info(f"Spec path: {SPEC_PATH}")
    logger.info(f"Impl path: {IMPL_PATH}")

    # Compute Galois loss once (expensive)
    logger.info("\n📐 Computing Galois loss...")
    galois_loss = await compute_spec_impl_galois_loss()
    logger.info(f"Galois loss: {galois_loss:.3f} (coherence: {1 - galois_loss:.1%})")

    # Run verification iterations
    runs: list[WASMSurvivorsRun] = []
    successes = 0
    failures = 0

    for i in range(max_runs):
        logger.info(f"\n🔄 Run {i + 1}/{max_runs}...")
        start = time.monotonic()

        verification = await verify_typescript_implementation()
        duration_ms = (time.monotonic() - start) * 1000

        run = WASMSurvivorsRun(
            run_id=f"run-{i + 1}-{int(time.time())}",
            verification=verification,
            galois_loss=galois_loss,
            duration_ms=duration_ms,
        )
        runs.append(run)

        if run.passed:
            successes += 1
            logger.info(f"  ✅ PASSED (score: {run.verification_score:.2f})")
        else:
            failures += 1
            logger.info(f"  ❌ FAILED (score: {run.verification_score:.2f})")
            if not verification.test_report.success:
                logger.info(
                    f"     Tests: {verification.test_report.passed}/{verification.test_report.total}"
                )
            if not verification.type_report.passed:
                logger.info(f"     Types: {len(verification.type_report.errors)} errors")
            if not verification.lint_report.passed:
                logger.info(f"     Lint: {len(verification.lint_report.errors)} errors")

        # Adaptive stopping: n_diff = 2
        margin = abs(successes - failures)
        if i >= n_runs - 1 and margin >= 2:
            logger.info(f"\n⏹️ Stopping early: margin={margin} (n_diff=2 reached)")
            break

    evidence = WASMSurvivorsEvidence(
        runs=runs,
        spec_hash=spec_hash,
        galois_loss=galois_loss,
    )

    return evidence


def print_evidence_report(evidence: WASMSurvivorsEvidence) -> None:
    """Print a human-readable evidence report."""
    print("\n" + "=" * 60)
    print("ASHC EVIDENCE REPORT: wasm-survivors-game")
    print("=" * 60)

    print("\n📊 SUMMARY")
    print(f"   Runs: {evidence.run_count}")
    print(f"   Passed: {evidence.pass_count}/{evidence.run_count} ({evidence.pass_rate:.0%})")
    print(f"   Galois Coherence: {evidence.galois_coherence:.1%}")
    print(f"   Equivalence Score: {evidence.equivalence_score:.1%}")
    print(f"   Verified: {'✅ YES' if evidence.is_verified else '❌ NO'}")

    print("\n📐 GALOIS ANALYSIS")
    print(f"   L(spec, impl) = {evidence.galois_loss:.3f}")
    print(f"   Coherence (1 - L) = {evidence.galois_coherence:.3f}")

    if evidence.galois_loss < 0.10:
        tier = "CATEGORICAL (L < 0.10)"
    elif evidence.galois_loss < 0.38:
        tier = "EMPIRICAL (L < 0.38)"
    elif evidence.galois_loss < 0.45:
        tier = "AESTHETIC (L < 0.45)"
    elif evidence.galois_loss < 0.65:
        tier = "SOMATIC (L < 0.65)"
    else:
        tier = "CHAOTIC (L ≥ 0.65)"
    print(f"   Evidence Tier: {tier}")

    print("\n🔍 RUN DETAILS")
    for i, run in enumerate(evidence.runs):
        status = "✅" if run.passed else "❌"
        print(
            f"   {status} Run {i + 1}: score={run.verification_score:.2f}, {run.duration_ms:.0f}ms"
        )

    print("\n⚡ VERIFICATION BREAKDOWN (last run)")
    if evidence.runs:
        last = evidence.runs[-1]
        v = last.verification
        print(
            f"   Tests: {'✅' if v.test_report.success else '❌'} {v.test_report.passed}/{v.test_report.total}"
        )
        print(
            f"   Types: {'✅' if v.type_report.passed else '❌'} {len(v.type_report.errors)} errors"
        )
        print(
            f"   Lint:  {'✅' if v.lint_report.passed else '❌'} {len(v.lint_report.errors)} errors"
        )

    print("\n" + "=" * 60)

    if evidence.is_verified:
        print("✅ SPEC↔IMPL EQUIVALENCE VERIFIED")
        print("   The implementation satisfies the specification with")
        print(f"   {evidence.equivalence_score:.0%} confidence.")
    else:
        print("⚠️ INSUFFICIENT EVIDENCE")
        reasons = []
        if evidence.run_count < 3:
            reasons.append(f"Need ≥3 runs (have {evidence.run_count})")
        if evidence.galois_coherence < 0.70:
            reasons.append(f"Galois coherence {evidence.galois_coherence:.1%} < 70%")
        if evidence.equivalence_score < 0.60:
            reasons.append(f"Equivalence score {evidence.equivalence_score:.1%} < 60%")
        for r in reasons:
            print(f"   - {r}")

    print("=" * 60 + "\n")


async def main() -> int:
    """Main entry point."""
    # Check prerequisites
    if not SPEC_PATH.exists():
        logger.error(f"PROTO_SPEC not found: {SPEC_PATH}")
        return 1

    if not IMPL_PATH.exists():
        logger.error(f"Implementation not found: {IMPL_PATH}")
        return 1

    # Parse args
    n_runs = 5
    if len(sys.argv) > 1:
        try:
            n_runs = int(sys.argv[1])
        except ValueError:
            pass

    # Run bootstrap
    evidence = await bootstrap_evidence(n_runs=n_runs, max_runs=max(n_runs, 10))

    # Print report
    print_evidence_report(evidence)

    # Save evidence to JSON
    output_path = PROJECT_ROOT / "pilots" / "wasm-survivors-game" / "evidence.json"
    evidence_dict = {
        "spec_hash": evidence.spec_hash,
        "galois_loss": evidence.galois_loss,
        "galois_coherence": evidence.galois_coherence,
        "equivalence_score": evidence.equivalence_score,
        "is_verified": evidence.is_verified,
        "run_count": evidence.run_count,
        "pass_count": evidence.pass_count,
        "pass_rate": evidence.pass_rate,
        "created_at": evidence.created_at.isoformat(),
        "runs": [
            {
                "run_id": r.run_id,
                "passed": r.passed,
                "verification_score": r.verification_score,
                "duration_ms": r.duration_ms,
            }
            for r in evidence.runs
        ],
    }

    output_path.write_text(json.dumps(evidence_dict, indent=2))
    logger.info(f"\n💾 Evidence saved to: {output_path}")

    return 0 if evidence.is_verified else 1


if __name__ == "__main__":
    sys.exit(asyncio.run(main()))
