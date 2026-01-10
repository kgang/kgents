# HoTT Formal Verification Attack Plan

> *"The proof IS the decision. The Python scaffolding becomes the Lean theorem."*

**Status**: Active
**Date**: 2025-01-10
**Priority**: P1 (High Value) — Kent's explicit request
**Scope**: Complete HoTT verification pipeline from Python → Lean → Verified → Python
**Related**: `formal-verification-bridge.md`, `coherence-synthesis-master.md`

---

## Executive Summary

This plan orchestrates a three-phase attack on the HoTT formal verification system, transforming kgents' conceptual mathematical models into machine-verified proofs. The goal: **categorical laws verified by Lean 4, results imported back to Python**.

### Current State

| Component | Status | Gap |
|-----------|--------|-----|
| `hott.py` | ✅ 482 lines | Conceptual model only |
| `lean_export.py` | ✅ 202 lines | Generates code with `sorry` |
| `lean_import.py` | ❌ Not started | No proof result import |
| Lean 4 proofs | ❌ Not started | `sorry` stubs unproven |
| Round-trip verification | ❌ Not started | No Python ↔ Lean bridge |

### The Attack Vision

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                    PHASE 1: LEAN VALIDATION                                  │
│  Run existing Lean export → Compile with Lean 4 → See what works            │
├─────────────────────────────────────────────────────────────────────────────┤
│                    PHASE 2: PROOF IMPORT                                     │
│  Build lean_import.py → Parse Lean output → Report to Python                │
├─────────────────────────────────────────────────────────────────────────────┤
│                    PHASE 3: COMPLETE PROOFS                                  │
│  Replace `sorry` → Full Lean proofs → Verified categorical laws             │
└─────────────────────────────────────────────────────────────────────────────┘
```

### Success Metrics

| Metric | Target | Measurement |
|--------|--------|-------------|
| Category laws verified | 3/3 | `comp_assoc`, `id_comp`, `comp_id` pass Lean |
| Lean compilation | 0 errors | `lake build` succeeds |
| Proof import working | 100% | Python receives verification results |
| `sorry` count | 0 | All proofs completed |
| Round-trip latency | < 5s | Python → Lean → Python |

---

## Phase 1: Lean Validation Sprint

> *"First, see what already works."*

**Duration**: 1-2 days
**Effort**: Low
**Risk**: Low — just running existing code

### 1.1 Environment Setup

**Task 1.1.1: Install Lean 4 + Mathlib**

```bash
# Install elan (Lean version manager)
curl https://raw.githubusercontent.com/leanprover/elan/master/elan-init.sh -sSf | sh

# Create kgents Lean project
mkdir -p impl/claude/proofs
cd impl/claude/proofs
lake init kgents_proofs math

# Add Mathlib dependency (lakefile.lean)
# require mathlib from git "https://github.com/leanprover-community/mathlib4"

# Build (this takes ~20 minutes first time)
lake update
lake build
```

**Deliverable**: Working Lean 4 + Mathlib environment in `impl/claude/proofs/`

**Verification**:
```bash
lake env lean --version  # Should show Lean 4.x
```

---

**Task 1.1.2: Export Category Laws to Lean**

```python
# Run from impl/claude/
from services.verification.lean_export import LeanExporter

exporter = LeanExporter()
lean_code = exporter.export_category_laws()

# Write to Lean project
with open("proofs/Kgents/CategoryLaws.lean", "w") as f:
    f.write(lean_code)
```

**Deliverable**: `impl/claude/proofs/Kgents/CategoryLaws.lean`

---

**Task 1.1.3: Attempt Lean Compilation**

```bash
cd impl/claude/proofs
lake build
```

**Expected Outcomes**:

| Theorem | Expected Result | Reason |
|---------|----------------|--------|
| `comp_assoc` | ✅ Pass | `simp [Function.comp]` should work |
| `id_comp` | ✅ Pass | `simp` handles identity composition |
| `comp_id` | ✅ Pass | `simp` handles identity composition |

**If failures occur**: Document error messages for Phase 3.

---

**Task 1.1.4: Export Extended Laws**

```python
# Export functor and natural transformation laws
functor_code = exporter.export_functor_laws()
nat_trans_code = exporter.export_natural_transformation_laws()

# These have `sorry` stubs - expected to compile but not verify
```

**Deliverable**:
- `impl/claude/proofs/Kgents/FunctorLaws.lean`
- `impl/claude/proofs/Kgents/NatTransLaws.lean`

---

### 1.2 Phase 1 Checkpoint

| Criterion | Status |
|-----------|--------|
| Lean 4 + Mathlib installed | ☐ |
| CategoryLaws.lean compiles | ☐ |
| 3/3 basic laws verified | ☐ |
| FunctorLaws.lean compiles (with sorry) | ☐ |
| NatTransLaws.lean compiles (with sorry) | ☐ |

**Decision Point**: If basic laws fail, debug before Phase 2.

---

## Phase 2: Proof Import Pipeline

> *"Close the loop. Lean results flow back to Python."*

**Duration**: 2-3 days
**Effort**: Medium
**Risk**: Medium — requires parsing Lean output

### 2.1 Lean Output Analysis

**Task 2.1.1: Understand Lean Build Output**

Run `lake build` and capture output:

```bash
lake build 2>&1 | tee build_output.txt
```

**Key patterns to parse**:

| Pattern | Meaning |
|---------|---------|
| `✓ Built Kgents.CategoryLaws` | Module compiled successfully |
| `error: ...` | Compilation error |
| `warning: declaration uses 'sorry'` | Unproven theorem |
| `tactic 'simp' failed` | Proof tactic didn't work |

---

**Task 2.1.2: Implement LeanProofChecker**

```python
# File: impl/claude/services/verification/lean_import.py

from __future__ import annotations

import asyncio
import json
import re
import subprocess
from dataclasses import dataclass, field
from pathlib import Path
from enum import Enum


class ProofStatus(str, Enum):
    """Status of a Lean proof."""
    VERIFIED = "verified"       # Proof complete, no sorry
    SORRY = "sorry"             # Compiles but uses sorry
    FAILED = "failed"           # Compilation error
    TIMEOUT = "timeout"         # Build timed out
    NOT_FOUND = "not_found"     # Theorem not in output


@dataclass(frozen=True)
class ProofResult:
    """Result of checking a single Lean theorem."""

    theorem_name: str
    status: ProofStatus
    module: str
    error_message: str | None = None
    line_number: int | None = None

    def to_dict(self) -> dict:
        return {
            "theorem": self.theorem_name,
            "status": self.status.value,
            "module": self.module,
            "error": self.error_message,
            "line": self.line_number,
        }


@dataclass(frozen=True)
class VerificationReport:
    """Complete verification report from Lean."""

    results: tuple[ProofResult, ...]
    total_theorems: int
    verified_count: int
    sorry_count: int
    failed_count: int
    build_time_seconds: float
    lean_version: str

    @property
    def all_verified(self) -> bool:
        return self.verified_count == self.total_theorems

    @property
    def verification_rate(self) -> float:
        if self.total_theorems == 0:
            return 0.0
        return self.verified_count / self.total_theorems

    def to_dict(self) -> dict:
        return {
            "results": [r.to_dict() for r in self.results],
            "summary": {
                "total": self.total_theorems,
                "verified": self.verified_count,
                "sorry": self.sorry_count,
                "failed": self.failed_count,
                "rate": self.verification_rate,
            },
            "build_time_seconds": self.build_time_seconds,
            "lean_version": self.lean_version,
        }


@dataclass
class LeanProofChecker:
    """
    Check Lean 4 proofs and import results to Python.

    This class runs `lake build` on a Lean project and parses
    the output to determine which theorems are verified.

    Usage:
        checker = LeanProofChecker(Path("impl/claude/proofs"))
        report = await checker.check_all()

        if report.all_verified:
            print("All categorical laws verified!")
    """

    project_path: Path
    timeout_seconds: int = 300  # 5 minutes
    lake_command: str = "lake"

    async def check_all(self) -> VerificationReport:
        """Run full verification and return report."""
        import time
        start = time.monotonic()

        # Get Lean version
        lean_version = await self._get_lean_version()

        # Run build
        stdout, stderr, returncode = await self._run_build()

        elapsed = time.monotonic() - start

        # Parse results
        results = self._parse_build_output(stdout, stderr, returncode)

        # Compute counts
        verified = sum(1 for r in results if r.status == ProofStatus.VERIFIED)
        sorry = sum(1 for r in results if r.status == ProofStatus.SORRY)
        failed = sum(1 for r in results if r.status == ProofStatus.FAILED)

        return VerificationReport(
            results=tuple(results),
            total_theorems=len(results),
            verified_count=verified,
            sorry_count=sorry,
            failed_count=failed,
            build_time_seconds=elapsed,
            lean_version=lean_version,
        )

    async def check_file(self, lean_file: Path) -> list[ProofResult]:
        """Check a specific Lean file."""
        # Extract theorems from file
        theorems = self._extract_theorems(lean_file)

        # Run build
        stdout, stderr, returncode = await self._run_build()

        # Parse for specific file
        return self._parse_for_file(lean_file.stem, stdout, stderr, theorems)

    async def _get_lean_version(self) -> str:
        """Get Lean version string."""
        try:
            proc = await asyncio.create_subprocess_exec(
                self.lake_command, "env", "lean", "--version",
                cwd=self.project_path,
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE,
            )
            stdout, _ = await proc.communicate()
            return stdout.decode().strip().split("\n")[0]
        except Exception:
            return "unknown"

    async def _run_build(self) -> tuple[str, str, int]:
        """Run lake build and capture output."""
        try:
            proc = await asyncio.create_subprocess_exec(
                self.lake_command, "build",
                cwd=self.project_path,
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE,
            )
            stdout, stderr = await asyncio.wait_for(
                proc.communicate(),
                timeout=self.timeout_seconds,
            )
            return stdout.decode(), stderr.decode(), proc.returncode or 0
        except asyncio.TimeoutError:
            return "", "Build timed out", -1

    def _extract_theorems(self, lean_file: Path) -> list[str]:
        """Extract theorem names from a Lean file."""
        content = lean_file.read_text()
        # Match: theorem <name> or lemma <name>
        pattern = r"(?:theorem|lemma)\s+(\w+)"
        return re.findall(pattern, content)

    def _parse_build_output(
        self,
        stdout: str,
        stderr: str,
        returncode: int,
    ) -> list[ProofResult]:
        """Parse build output to extract proof results."""
        results = []
        combined = stdout + "\n" + stderr

        # Find all theorem declarations in .lean files
        for lean_file in self.project_path.rglob("*.lean"):
            if "lake-packages" in str(lean_file):
                continue
            theorems = self._extract_theorems(lean_file)
            module = lean_file.stem

            for thm in theorems:
                status = self._determine_status(thm, module, combined, returncode)
                error = self._extract_error(thm, combined) if status == ProofStatus.FAILED else None

                results.append(ProofResult(
                    theorem_name=thm,
                    status=status,
                    module=module,
                    error_message=error,
                ))

        return results

    def _determine_status(
        self,
        theorem: str,
        module: str,
        output: str,
        returncode: int,
    ) -> ProofStatus:
        """Determine proof status from build output."""
        # Check for sorry warning
        if f"'{theorem}'" in output and "sorry" in output.lower():
            return ProofStatus.SORRY

        # Check for error mentioning theorem
        if f"error" in output.lower() and theorem in output:
            return ProofStatus.FAILED

        # Check for successful build
        if returncode == 0:
            # If no sorry warning, it's verified
            if "sorry" not in output.lower() or theorem not in output:
                return ProofStatus.VERIFIED
            return ProofStatus.SORRY

        # Build failed
        if "timeout" in output.lower():
            return ProofStatus.TIMEOUT

        return ProofStatus.FAILED

    def _extract_error(self, theorem: str, output: str) -> str | None:
        """Extract error message for a theorem."""
        lines = output.split("\n")
        for i, line in enumerate(lines):
            if theorem in line and "error" in line.lower():
                # Return this line plus context
                context = lines[max(0, i-1):min(len(lines), i+3)]
                return "\n".join(context)
        return None

    def _parse_for_file(
        self,
        module: str,
        stdout: str,
        stderr: str,
        theorems: list[str],
    ) -> list[ProofResult]:
        """Parse output for a specific file's theorems."""
        combined = stdout + "\n" + stderr
        results = []

        for thm in theorems:
            status = self._determine_status(thm, module, combined, 0)
            results.append(ProofResult(
                theorem_name=thm,
                status=status,
                module=module,
            ))

        return results


# Convenience function
async def verify_categorical_laws(project_path: Path | str) -> VerificationReport:
    """Verify all categorical laws in a Lean project."""
    checker = LeanProofChecker(Path(project_path))
    return await checker.check_all()
```

**Deliverable**: `impl/claude/services/verification/lean_import.py`

---

**Task 2.1.3: Integration with HoTT Context**

```python
# Add to impl/claude/services/verification/hott.py

async def verify_with_lean(self, project_path: Path) -> dict[str, Any]:
    """
    Verify HoTT laws using external Lean 4 proof checker.

    This bridges conceptual Python models to formal verification.
    """
    from services.verification.lean_import import verify_categorical_laws

    report = await verify_categorical_laws(project_path)

    # Update internal state based on verification
    self._lean_verification_cache = {
        r.theorem_name: r.status.value
        for r in report.results
    }

    return report.to_dict()
```

**Deliverable**: Updated `hott.py` with Lean integration

---

**Task 2.1.4: CLI Command for Verification**

```python
# Add to appropriate CLI module

@click.command()
@click.option("--project", default="impl/claude/proofs", help="Lean project path")
@click.option("--json", "as_json", is_flag=True, help="Output as JSON")
async def verify_hott(project: str, as_json: bool):
    """Verify HoTT categorical laws with Lean 4."""
    from services.verification.lean_import import verify_categorical_laws

    report = await verify_categorical_laws(Path(project))

    if as_json:
        click.echo(json.dumps(report.to_dict(), indent=2))
    else:
        click.echo(f"Lean Version: {report.lean_version}")
        click.echo(f"Build Time: {report.build_time_seconds:.2f}s")
        click.echo(f"\nResults ({report.verification_rate:.0%} verified):")

        for r in report.results:
            icon = {"verified": "✓", "sorry": "⚠", "failed": "✗"}.get(r.status.value, "?")
            click.echo(f"  {icon} {r.module}.{r.theorem_name}: {r.status.value}")

        if not report.all_verified:
            click.echo(f"\n⚠ {report.sorry_count} theorems use sorry")
            click.echo(f"✗ {report.failed_count} theorems failed")
```

**Deliverable**: `kg hott verify` command

---

### 2.2 Phase 2 Checkpoint

| Criterion | Status |
|-----------|--------|
| `lean_import.py` implemented | ☐ |
| `LeanProofChecker` parses output correctly | ☐ |
| Integration with `HoTTContext` | ☐ |
| CLI command working | ☐ |
| Round-trip test passes | ☐ |

**Round-trip test**:
```python
# Export → Build → Import → Verify results match
exporter = LeanExporter()
code = exporter.export_category_laws()
# ... write to file, build ...
report = await verify_categorical_laws(project_path)
assert report.verified_count >= 3  # Basic laws
```

---

## Phase 3: Complete Proofs

> *"Replace `sorry` with truth. Every theorem earns its verification."*

**Duration**: 3-5 days
**Effort**: High — requires Lean expertise
**Risk**: High — proofs may be non-trivial

### 3.1 Proof Completion Strategy

**Task 3.1.1: Audit `sorry` Usage**

```bash
cd impl/claude/proofs
grep -rn "sorry" Kgents/
```

Expected `sorry` locations:

| File | Theorem | Difficulty |
|------|---------|------------|
| FunctorLaws.lean | `functor_id` | Medium |
| FunctorLaws.lean | `functor_comp` | Medium |
| NatTransLaws.lean | `naturality` | Hard |

---

**Task 3.1.2: Prove Functor Laws**

```lean
-- File: Kgents/FunctorLaws.lean

import Mathlib.CategoryTheory.Functor.Basic

namespace Kgents

universe u v

-- A functor between categories preserves identity
theorem functor_id {C D : Type*} [Category C] [Category D]
    (F : C ⥤ D) (X : C) : F.map (𝟙 X) = 𝟙 (F.obj X) := by
  exact F.map_id X

-- A functor preserves composition
theorem functor_comp {C D : Type*} [Category C] [Category D]
    (F : C ⥤ D) {X Y Z : C} (f : X ⟶ Y) (g : Y ⟶ Z) :
    F.map (f ≫ g) = F.map f ≫ F.map g := by
  exact F.map_comp f g

end Kgents
```

**Note**: Mathlib already has these as `Functor.map_id` and `Functor.map_comp`. We're wrapping them for kgents namespace.

---

**Task 3.1.3: Prove Natural Transformation Laws**

```lean
-- File: Kgents/NatTransLaws.lean

import Mathlib.CategoryTheory.NatTrans

namespace Kgents

universe u v

-- Natural transformation naturality square
theorem naturality {C D : Type*} [Category C] [Category D]
    {F G : C ⥤ D} (η : F ⟶ G) {X Y : C} (f : X ⟶ Y) :
    F.map f ≫ η.app Y = η.app X ≫ G.map f := by
  exact η.naturality f

end Kgents
```

---

**Task 3.1.4: Prove Operad Laws (Advanced)**

This requires defining operads in Lean. Options:

1. **Use existing Mathlib structures** (if available)
2. **Define minimal operad structure** for kgents
3. **Defer** if too complex for current scope

```lean
-- File: Kgents/OperadLaws.lean (Sketch)

import Mathlib.CategoryTheory.Category.Basic

namespace Kgents

-- Operad structure (minimal definition)
structure Operad (C : Type*) where
  obj : ℕ → C
  comp : {m n : ℕ} → obj (m + n) → obj m → obj n → obj (m + n)
  unit : obj 1
  -- Laws would go here

-- Operad left unit
theorem operad_unit_left {C : Type*} (O : Operad C) :
    ∀ x, O.comp O.unit x O.unit = x := by
  sorry  -- Requires operad axioms

end Kgents
```

**Decision Point**: Operads may be out of scope for Phase 3. Focus on category/functor/nat-trans first.

---

### 3.2 Proof Development Workflow

**Iterative Process**:

```
1. Write theorem statement in Lean
2. Try automatic tactics: simp, exact, rfl, trivial
3. If stuck, use `#check` and `#print` to explore Mathlib
4. Search Mathlib docs: https://leanprover-community.github.io/mathlib4_docs/
5. Ask for help in Lean Zulip if needed
```

**Useful Lean Tactics**:

| Tactic | Use Case |
|--------|----------|
| `simp` | Simplify using known lemmas |
| `exact` | Provide exact proof term |
| `rfl` | Prove by definitional equality |
| `apply` | Apply a lemma |
| `have` | Introduce intermediate step |
| `rw [lemma]` | Rewrite using lemma |

---

### 3.3 Phase 3 Checkpoint

| Criterion | Status |
|-----------|--------|
| CategoryLaws.lean — 0 sorry | ☐ |
| FunctorLaws.lean — 0 sorry | ☐ |
| NatTransLaws.lean — 0 sorry | ☐ |
| All theorems compile | ☐ |
| `kg hott verify` shows 100% verified | ☐ |

---

## Phase 4: Integration & Hardening

> *"Make it production. Make it sing."*

**Duration**: 2-3 days
**Effort**: Medium

### 4.1 Witness Integration

**Task 4.1.1: Connect Trace Witnesses to Lean Verification**

```python
# impl/claude/services/verification/trace_witness.py

@dataclass(frozen=True)
class FormallyVerifiedWitness:
    """A trace witness backed by Lean verification."""

    witness: TraceWitness
    lean_verification: VerificationReport
    categorical_laws_verified: bool

    @property
    def formally_verified(self) -> bool:
        return self.lean_verification.all_verified
```

---

**Task 4.1.2: Add to Constitutional Evaluator**

```python
# When evaluating COMPOSABLE principle, check Lean verification
async def evaluate_composable(self, mark: Mark) -> float:
    base_score = await self._evaluate_composable_base(mark)

    # Bonus for formally verified composition
    if await self._has_lean_verification():
        lean_bonus = 0.1  # 10% bonus for formal verification
        return min(1.0, base_score + lean_bonus)

    return base_score
```

---

### 4.2 CI/CD Integration

**Task 4.2.1: GitHub Action for Lean Verification**

```yaml
# .github/workflows/lean-verify.yml
name: Lean Verification

on:
  push:
    paths:
      - 'impl/claude/proofs/**'
      - 'impl/claude/services/verification/lean_export.py'

jobs:
  verify:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4

      - name: Install elan
        run: |
          curl https://raw.githubusercontent.com/leanprover/elan/master/elan-init.sh -sSf | sh -s -- -y
          echo "$HOME/.elan/bin" >> $GITHUB_PATH

      - name: Build Lean proofs
        working-directory: impl/claude/proofs
        run: |
          lake update
          lake build

      - name: Check for sorry
        working-directory: impl/claude/proofs
        run: |
          if grep -rn "sorry" Kgents/; then
            echo "::warning::Some theorems use sorry"
          fi
```

---

### 4.3 Documentation

**Task 4.3.1: Update Verification README**

```markdown
# Formal Verification with Lean 4

## Quick Start

```bash
# Verify all categorical laws
kg hott verify

# Export new laws to Lean
kg hott export --output impl/claude/proofs/Kgents/NewLaws.lean

# Check specific file
kg hott verify --file impl/claude/proofs/Kgents/CategoryLaws.lean
```

## Verified Laws

| Law | Status | Proof |
|-----|--------|-------|
| Composition Associativity | ✅ | `simp [Function.comp]` |
| Left Identity | ✅ | `simp` |
| Right Identity | ✅ | `simp` |
| Functor Identity | ✅ | `exact F.map_id X` |
| Functor Composition | ✅ | `exact F.map_comp f g` |
| Naturality | ✅ | `exact η.naturality f` |
```

---

## Risk Management

### Technical Risks

| Risk | Probability | Impact | Mitigation |
|------|-------------|--------|------------|
| Mathlib version incompatibility | Medium | High | Pin specific Mathlib version |
| Lean build timeout | Medium | Medium | Increase timeout, cache builds |
| Operad proofs too complex | High | Low | Defer, focus on category laws |
| CI flakiness | Medium | Medium | Retry logic, caching |

### Process Risks

| Risk | Probability | Impact | Mitigation |
|------|-------------|--------|------------|
| Scope creep to advanced proofs | High | Medium | Strict phase gates |
| Lean expertise gap | Medium | High | Use Mathlib docs, Zulip |
| Integration complexity | Medium | Medium | Incremental testing |

---

## Timeline

```
Week 1
├── Day 1-2: Phase 1 (Lean validation)
│   ├── Install Lean 4 + Mathlib
│   ├── Export category laws
│   └── Verify basic theorems compile
│
├── Day 3-5: Phase 2 (Proof import)
│   ├── Implement lean_import.py
│   ├── CLI integration
│   └── Round-trip test

Week 2
├── Day 1-3: Phase 3 (Complete proofs)
│   ├── Prove functor laws
│   ├── Prove nat-trans laws
│   └── Audit remaining sorry
│
├── Day 4-5: Phase 4 (Integration)
│   ├── Witness integration
│   ├── CI/CD setup
│   └── Documentation

Week 3 (Optional)
└── Advanced proofs (operads, sheaves)
```

---

## Appendix A: Lean Quick Reference

### Common Patterns

```lean
-- Prove by simplification
theorem foo : a = a := by simp

-- Prove by exact term
theorem bar : P → P := by exact id

-- Prove using Mathlib lemma
theorem baz : F.map (𝟙 X) = 𝟙 (F.obj X) := by
  exact F.map_id X

-- Introduce intermediate step
theorem qux : A → C := by
  intro a
  have b : B := f a
  exact g b
```

### Useful Commands

```lean
#check term           -- Show type of term
#print axioms theorem -- Show axioms used
#print instances Class -- Show typeclass instances
#help tactic          -- Show tactic documentation
```

---

## Appendix B: File Structure

```
impl/claude/
├── proofs/                          # Lean 4 project
│   ├── lakefile.lean                # Project config
│   ├── lean-toolchain               # Lean version
│   └── Kgents/
│       ├── CategoryLaws.lean        # ✅ Verified
│       ├── FunctorLaws.lean         # Target: ✅
│       ├── NatTransLaws.lean        # Target: ✅
│       └── OperadLaws.lean          # Stretch goal
│
└── services/verification/
    ├── hott.py                      # ✅ Conceptual model
    ├── lean_export.py               # ✅ Code generation
    ├── lean_import.py               # Target: New
    └── _tests/
        ├── test_hott.py             # ✅ Property tests
        └── test_lean_import.py      # Target: New
```

---

*"The category laws were always true. Lean 4 just made them undeniable."*
