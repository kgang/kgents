"""
Lean 4 Proof Import for kgents Categorical Laws.

This module runs Lean 4 verification on kgents proofs and imports
the results back into Python for use in the Constitutional Evaluator.

The kgents proofs are in: impl/claude/proofs/kgents_proofs/

Usage:
    checker = LeanProofChecker()
    report = await checker.check_all()
    if report.all_verified:
        print("All categorical laws formally verified!")

IMPORTANT: Requires Lean 4 (via elan) and Mathlib installed.
"""

from __future__ import annotations

import asyncio
import os
import re
import subprocess
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from pathlib import Path
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from collections.abc import Sequence


class ProofStatus(Enum):
    """Status of a Lean proof verification."""

    VERIFIED = "verified"  # Proof complete, no sorry
    SORRY = "sorry"  # Proof incomplete, uses sorry
    FAILED = "failed"  # Compilation error
    NOT_FOUND = "not_found"  # Module not found


@dataclass
class TheoremResult:
    """Result of checking a single theorem."""

    name: str
    module: str
    status: ProofStatus
    message: str = ""
    line_number: int | None = None


@dataclass
class ModuleResult:
    """Result of checking a Lean module."""

    name: str
    path: Path
    status: ProofStatus
    theorems: list[TheoremResult] = field(default_factory=list)
    errors: list[str] = field(default_factory=list)
    build_time_ms: float = 0


@dataclass
class VerificationReport:
    """Complete verification report for all kgents proofs."""

    timestamp: datetime = field(default_factory=datetime.now)
    modules: list[ModuleResult] = field(default_factory=list)
    total_theorems: int = 0
    verified_theorems: int = 0
    sorry_count: int = 0
    errors: list[str] = field(default_factory=list)
    build_output: str = ""
    build_time_ms: float = 0

    @property
    def all_verified(self) -> bool:
        """Check if all proofs are complete with no sorry."""
        return self.sorry_count == 0 and len(self.errors) == 0

    @property
    def success_rate(self) -> float:
        """Percentage of verified theorems."""
        if self.total_theorems == 0:
            return 0.0
        return (self.verified_theorems / self.total_theorems) * 100

    def summary(self) -> str:
        """Generate human-readable summary."""
        status = "VERIFIED" if self.all_verified else "INCOMPLETE"
        lines = [
            "kgents Lean Verification Report",
            "================================",
            f"Status: {status}",
            f"Timestamp: {self.timestamp.isoformat()}",
            "",
            f"Theorems: {self.verified_theorems}/{self.total_theorems} verified ({self.success_rate:.1f}%)",
            f"Sorry count: {self.sorry_count}",
            f"Build time: {self.build_time_ms:.1f}ms",
            "",
            "Modules:",
        ]

        for module in self.modules:
            status_icon = {
                ProofStatus.VERIFIED: "",
                ProofStatus.SORRY: "",
                ProofStatus.FAILED: "",
                ProofStatus.NOT_FOUND: "",
            }.get(module.status, "?")
            lines.append(f"  {status_icon} {module.name}: {module.status.value}")
            for thm in module.theorems:
                thm_icon = "" if thm.status == ProofStatus.VERIFIED else ""
                lines.append(f"      {thm_icon} {thm.name}")

        if self.errors:
            lines.extend(["", "Errors:", *[f"  - {e}" for e in self.errors]])

        return "\n".join(lines)

    def to_dict(self) -> dict[str, object]:
        """Convert to dictionary for JSON serialization."""
        return {
            "timestamp": self.timestamp.isoformat(),
            "all_verified": self.all_verified,
            "success_rate": self.success_rate,
            "total_theorems": self.total_theorems,
            "verified_theorems": self.verified_theorems,
            "sorry_count": self.sorry_count,
            "build_time_ms": self.build_time_ms,
            "modules": [
                {
                    "name": m.name,
                    "status": m.status.value,
                    "theorems": [{"name": t.name, "status": t.status.value} for t in m.theorems],
                }
                for m in self.modules
            ],
            "errors": self.errors,
        }


class LeanProofChecker:
    """
    Verifies kgents Lean proofs and imports results into Python.

    This checker:
    1. Runs `lake build` on the kgents_proofs project
    2. Parses output to detect success, sorry, and errors
    3. Analyzes each module for theorem status
    4. Returns a comprehensive verification report
    """

    # Relative path from impl/claude to the proofs
    PROOFS_PATH = Path("proofs/kgents_proofs")

    # Expected modules and their theorems
    EXPECTED_MODULES = {
        "CategoryLaws": [
            "comp_assoc",
            "id_comp",
            "comp_id",
            "comp_three",
            "id_comp_id",
        ],
        "FunctorLaws": [
            "functor_map_id",
            "functor_map_comp",
            "id_functor_obj",
            "id_functor_map",
            "comp_functor_obj",
            "comp_functor_map",
            "functor_assoc_obj",
            "functor_assoc_map",
        ],
        "NatTransLaws": [
            "naturality",
            "naturality'",
            "id_nat_trans_app",
            "vcomp_app",
            "vcomp_assoc",
            "vcomp_id_left",
            "vcomp_id_right",
            "whisker_left_naturality",
            "whisker_right_naturality",
        ],
        "OperadLaws": [
            "trivial_comp_assoc",
            "trivial_ops_unique",
            "agent_comp_monoid_laws",
            "agent_assoc",
            "agent_id_left",
            "agent_id_right",
            "endo_composition_is_associative",
            "endo_id_left",
            "endo_id_right",
            "operad_morphism_comp_assoc",
            "operad_morphism_id_left",
            "operad_morphism_id_right",
            "operads_form_category",
        ],
    }

    def __init__(self, base_path: Path | None = None):
        """
        Initialize the proof checker.

        Args:
            base_path: Base path for impl/claude. Defaults to auto-detect.
        """
        if base_path is None:
            # Auto-detect: find impl/claude relative to this file
            this_file = Path(__file__).resolve()
            # Go up: services/verification -> services -> impl/claude
            base_path = this_file.parent.parent.parent

        self.base_path = base_path
        self.proofs_path = base_path / self.PROOFS_PATH

    async def check_all(self) -> VerificationReport:
        """
        Run full verification and return report.

        This is the main entry point. It:
        1. Validates the proofs directory exists
        2. Runs lake build
        3. Parses output for results
        4. Analyzes each module
        5. Returns comprehensive report
        """
        report = VerificationReport()
        start_time = datetime.now()

        # Validate proofs directory
        if not self.proofs_path.exists():
            report.errors.append(f"Proofs directory not found: {self.proofs_path}")
            return report

        # Check for elan/lean
        if not self._check_lean_installed():
            report.errors.append("Lean 4 not found. Install via: curl https://elan.sh -sSf | sh")
            return report

        # Run build
        build_result = await self._run_build()
        report.build_output = build_result.output
        report.build_time_ms = build_result.elapsed_ms

        # Parse build output
        if build_result.success:
            # Check for sorry in source files
            sorry_locations = self._find_sorries()
            report.sorry_count = len(sorry_locations)

            # Analyze each module
            for module_name, expected_theorems in self.EXPECTED_MODULES.items():
                module_result = self._analyze_module(module_name, expected_theorems)
                report.modules.append(module_result)
                report.total_theorems += len(module_result.theorems)
                report.verified_theorems += sum(
                    1 for t in module_result.theorems if t.status == ProofStatus.VERIFIED
                )
        else:
            # Build failed - parse errors
            report.errors.extend(self._parse_build_errors(build_result.output))

        end_time = datetime.now()
        report.build_time_ms = (end_time - start_time).total_seconds() * 1000

        return report

    def check_all_sync(self) -> VerificationReport:
        """Synchronous version of check_all."""
        return asyncio.run(self.check_all())

    def _check_lean_installed(self) -> bool:
        """Check if Lean 4 is installed and accessible."""
        try:
            result = subprocess.run(
                ["lean", "--version"],
                capture_output=True,
                text=True,
                timeout=10,
            )
            return result.returncode == 0 and "Lean" in result.stdout
        except (FileNotFoundError, subprocess.TimeoutExpired):
            return False

    @dataclass
    class BuildResult:
        success: bool
        output: str
        elapsed_ms: float

    async def _run_build(self) -> BuildResult:
        """Run lake build and return result."""
        start = datetime.now()

        # Set up environment with elan
        env = os.environ.copy()
        elan_path = Path.home() / ".elan" / "bin"
        if elan_path.exists():
            env["PATH"] = f"{elan_path}:{env.get('PATH', '')}"

        try:
            process = await asyncio.create_subprocess_exec(
                "lake",
                "build",
                cwd=self.proofs_path,
                env=env,
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.STDOUT,
            )
            stdout, _ = await asyncio.wait_for(process.communicate(), timeout=300)
            output = stdout.decode("utf-8") if stdout else ""
            success = process.returncode == 0
        except asyncio.TimeoutError:
            output = "Build timed out after 300 seconds"
            success = False
        except FileNotFoundError:
            output = "lake command not found"
            success = False

        elapsed = (datetime.now() - start).total_seconds() * 1000
        return self.BuildResult(success=success, output=output, elapsed_ms=elapsed)

    def _find_sorries(self) -> list[tuple[str, int]]:
        """Find all sorry occurrences in source files."""
        sorries: list[tuple[str, int]] = []
        lean_dir = self.proofs_path / "KgentsProofs"

        if not lean_dir.exists():
            return sorries

        for lean_file in lean_dir.glob("*.lean"):
            try:
                content = lean_file.read_text()
                for i, line in enumerate(content.split("\n"), 1):
                    # Match 'sorry' not in comments
                    if "sorry" in line and not line.strip().startswith("--"):
                        sorries.append((str(lean_file.name), i))
            except OSError:
                pass

        return sorries

    def _analyze_module(self, module_name: str, expected_theorems: Sequence[str]) -> ModuleResult:
        """Analyze a single module for theorem status."""
        module_path = self.proofs_path / "KgentsProofs" / f"{module_name}.lean"

        if not module_path.exists():
            return ModuleResult(
                name=module_name,
                path=module_path,
                status=ProofStatus.NOT_FOUND,
            )

        try:
            content = module_path.read_text()
        except OSError as e:
            return ModuleResult(
                name=module_name,
                path=module_path,
                status=ProofStatus.FAILED,
                errors=[str(e)],
            )

        # Parse theorems from content
        theorems: list[TheoremResult] = []
        has_sorry = "sorry" in content and not all(
            "sorry" in line and line.strip().startswith("--")
            for line in content.split("\n")
            if "sorry" in line
        )

        # Find theorem declarations
        theorem_pattern = re.compile(r"theorem\s+(\w+)")
        for match in theorem_pattern.finditer(content):
            name = match.group(1)
            theorems.append(
                TheoremResult(
                    name=name,
                    module=module_name,
                    status=ProofStatus.VERIFIED,  # Assume verified if built
                )
            )

        # Determine module status
        if has_sorry:
            status = ProofStatus.SORRY
        elif theorems:
            status = ProofStatus.VERIFIED
        else:
            status = ProofStatus.FAILED

        return ModuleResult(
            name=module_name,
            path=module_path,
            status=status,
            theorems=theorems,
        )

    def _parse_build_errors(self, output: str) -> list[str]:
        """Parse build output for error messages."""
        errors: list[str] = []
        error_pattern = re.compile(r"error:\s*(.+)")

        for line in output.split("\n"):
            match = error_pattern.search(line)
            if match:
                errors.append(match.group(1).strip())

        return errors if errors else [output[:500]] if output else ["Unknown build error"]


# Convenience functions for integration


async def verify_categorical_laws() -> tuple[bool, str]:
    """
    Quick verification of all categorical laws.

    Returns:
        (success, message) tuple for Constitutional Evaluator integration.
    """
    checker = LeanProofChecker()
    report = await checker.check_all()

    if report.all_verified:
        return True, f"All {report.verified_theorems} categorical laws formally verified"
    elif report.errors:
        return False, f"Build errors: {'; '.join(report.errors)}"
    else:
        return False, f"Incomplete proofs: {report.sorry_count} sorry remaining"


def verify_categorical_laws_sync() -> tuple[bool, str]:
    """Synchronous version for non-async contexts."""
    return asyncio.run(verify_categorical_laws())


# Constitutional Evaluator integration


@dataclass
class LeanVerificationEvidence:
    """
    Evidence structure for Constitutional Evaluator.

    This provides the formal verification backing for constitutional
    principles, particularly L2.5 (Composable) which requires
    categorical laws to hold.
    """

    verified: bool
    report: VerificationReport
    principle: str = "L2.5 COMPOSABLE"
    axiom: str = "L1.1 COMPOSE"

    @property
    def confidence(self) -> float:
        """Confidence level for constitutional evaluation."""
        if self.verified:
            return 1.0  # Formal proof = absolute confidence
        elif self.report.success_rate > 80:
            return 0.8
        elif self.report.success_rate > 50:
            return 0.5
        else:
            return 0.2

    def to_evidence_dict(self) -> dict[str, object]:
        """Format for Constitutional Evaluator."""
        return {
            "source": "lean4_formal_verification",
            "principle": self.principle,
            "axiom": self.axiom,
            "verified": self.verified,
            "confidence": self.confidence,
            "theorems_verified": self.report.verified_theorems,
            "theorems_total": self.report.total_theorems,
            "sorry_count": self.report.sorry_count,
            "timestamp": self.report.timestamp.isoformat(),
        }


async def get_constitutional_evidence() -> LeanVerificationEvidence:
    """
    Get formal verification evidence for Constitutional Evaluator.

    This is the primary integration point between Lean verification
    and the kgents constitutional framework.
    """
    checker = LeanProofChecker()
    report = await checker.check_all()
    return LeanVerificationEvidence(
        verified=report.all_verified,
        report=report,
    )
