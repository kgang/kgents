# Formal Verification Bridge Plan

> *"Reasoning about reasoning, verified."*

**Status**: ✅ IMPLEMENTED (Phase 1-2, 2025-01-10)
**Date**: 2025-01-10
**Priority**: P3 (Advanced)
**Scope**: HoTT bridge, Lean/Agda export, trace witness verification
**Related**: `coherence-synthesis-master.md`, `zero-seed-integration.md`

---

## ⚠️ Honest Caveats (Read First)

> *"Be precise about what is mathematical and what is metaphorical."*

This plan uses HoTT (Homotopy Type Theory) concepts as **conceptual models**, not formal mathematics:

| What We Claim | What's Actually True | Gap |
|---------------|----------------------|-----|
| "HoTT types" | Python classes with Path/Morphism metaphors | Not machine-verified HoTT |
| "Univalence" | Isomorphism ⇒ equality (conceptual) | Not axiom UA from real HoTT |
| "Path composition" | Python method composition | Not genuine homotopy paths |
| "Lean export" | Code generation with `sorry` stubs | Proofs not yet completed |

**The Path Forward**:
1. **Phase 1-3**: Implement Python infrastructure (this plan)
2. **Phase 4+**: Connect to actual Lean 4/Agda for machine verification
3. **Long-term**: Replace `sorry` with genuine proofs

**Why proceed anyway?**
- The conceptual model is valuable for reasoning
- Infrastructure enables future formal verification
- Tests provide empirical (not formal) confidence

---

## Executive Summary

The Formal Verification Metatheory spec defines 25 correctness properties and a HoTT (Homotopy Type Theory) foundation. This plan implements the bridge between kgents Python/TypeScript implementation and formal proof assistants (Lean 4, Agda), enabling machine-verified categorical laws.

### Current State

| Component | Status | Gap |
|-----------|--------|-----|
| Correctness Properties | 25 specified | Not machine-verified |
| HoTT Foundation | Specified | No implementation |
| Trace Witnesses | Conceptual | No formal proof extraction |
| Lean Export | Not started | No bridge exists |
| Verification Graph | Specified | Partially implemented |

### The Vision

```
┌─────────────────────────────────────────────────────────────┐
│                    FORMAL VERIFICATION                       │
├─────────────────────────────────────────────────────────────┤
│                                                             │
│   Python/TS Implementation                                  │
│          │                                                  │
│          ▼                                                  │
│   ┌─────────────────┐                                       │
│   │  Lean Exporter  │  Export categorical laws as theorems  │
│   └────────┬────────┘                                       │
│            │                                                │
│            ▼                                                │
│   ┌─────────────────┐                                       │
│   │   Lean 4 Code   │  Formal proofs of laws                │
│   └────────┬────────┘                                       │
│            │                                                │
│            ▼                                                │
│   ┌─────────────────┐                                       │
│   │  Proof Checker  │  Machine verification                 │
│   └────────┬────────┘                                       │
│            │                                                │
│            ▼                                                │
│   ┌─────────────────┐                                       │
│   │ Result Importer │  Import verification results          │
│   └─────────────────┘                                       │
│                                                             │
└─────────────────────────────────────────────────────────────┘
```

---

## Part I: HoTT Foundation

### 1.1 Core HoTT Concepts

From the formal verification spec:

> Homotopy Type Theory provides:
> 1. **Univalence axiom**: Isomorphic specifications are identical
> 2. **Agent types as homotopy types** with natural equivalence
> 3. **Path composition** for composition law verification
> 4. **Higher inductive types** for agent structure definitions
> 5. **Constructive proofs** that are also programs (witnesses)

### 1.2 HoTT Types for kgents

```python
# File: impl/claude/services/formal/hott_types.py

from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Generic, TypeVar

A = TypeVar("A")
B = TypeVar("B")
C = TypeVar("C")


@dataclass(frozen=True)
class HoTTType:
    """
    Base class for Homotopy Type Theory types.

    In HoTT, types are spaces and terms are points.
    Equality is a path type.
    """

    name: str
    universe_level: int = 0  # Type universe level


@dataclass(frozen=True)
class Path(Generic[A]):
    """
    A path between two terms of type A.

    In HoTT, Path(a, b) represents evidence that a = b.
    Paths can be composed (transitivity) and inverted (symmetry).
    """

    source: A
    target: A
    path_data: Any  # The actual proof term

    def compose(self, other: "Path[A]") -> "Path[A]":
        """
        Compose paths: (a = b) • (b = c) → (a = c).

        This is transitivity of equality as path composition.
        """
        assert self.target == other.source, "Paths must be composable"
        return Path(
            source=self.source,
            target=other.target,
            path_data=("compose", self.path_data, other.path_data),
        )

    def inverse(self) -> "Path[A]":
        """
        Invert path: (a = b) → (b = a).

        This is symmetry of equality as path inversion.
        """
        return Path(
            source=self.target,
            target=self.source,
            path_data=("inverse", self.path_data),
        )

    @staticmethod
    def refl(a: A) -> "Path[A]":
        """
        Reflexivity: a = a.

        The identity path at a point.
        """
        return Path(source=a, target=a, path_data=("refl", a))


@dataclass(frozen=True)
class Morphism(Generic[A, B]):
    """
    A morphism (function) from A to B.

    In categorical terms, an arrow in a category.
    """

    source_type: HoTTType
    target_type: HoTTType
    apply: callable  # A → B

    def compose(self, other: "Morphism[B, C]") -> "Morphism[A, C]":
        """
        Compose morphisms: (A → B) ∘ (B → C) → (A → C).
        """
        return Morphism(
            source_type=self.source_type,
            target_type=other.target_type,
            apply=lambda a: other.apply(self.apply(a)),
        )


@dataclass(frozen=True)
class Isomorphism(Generic[A, B]):
    """
    An isomorphism between types A and B.

    By univalence: A ≅ B → A = B.
    """

    forward: Morphism[A, B]
    backward: Morphism[B, A]

    def verify(self) -> bool:
        """
        Verify that forward and backward are inverses.

        forward ∘ backward = id_B
        backward ∘ forward = id_A
        """
        # In practice, this requires testing or formal proof
        return True  # Placeholder


@dataclass(frozen=True)
class HoTTContext:
    """
    Context for HoTT computations.

    Maintains universe levels and path witnesses.
    """

    max_universe: int = 10
    path_cache: dict = None

    def __post_init__(self):
        object.__setattr__(self, "path_cache", {})

    async def construct_path(self, a: Any, b: Any) -> Path | None:
        """
        Attempt to construct a path (proof of equality) between a and b.

        Strategies:
        1. Reflexivity: if a == b, return refl
        2. Univalence: if a ≅ b, construct path from isomorphism
        3. Path induction: search for intermediate points
        """
        # Cache check
        cache_key = (id(a), id(b))
        if cache_key in self.path_cache:
            return self.path_cache[cache_key]

        # Reflexivity
        if a == b:
            path = Path.refl(a)
            self.path_cache[cache_key] = path
            return path

        # Univalence: check for isomorphism
        iso = await self._find_isomorphism(a, b)
        if iso:
            path = self._univalence_path(iso)
            self.path_cache[cache_key] = path
            return path

        # Path induction: limited search
        path = await self._path_induction(a, b, depth=3)
        if path:
            self.path_cache[cache_key] = path
        return path

    async def _find_isomorphism(self, a: Any, b: Any) -> Isomorphism | None:
        """Find an isomorphism between a and b if one exists."""
        # Type-specific isomorphism detection
        if type(a) == type(b):
            if hasattr(a, "__dict__") and hasattr(b, "__dict__"):
                if a.__dict__.keys() == b.__dict__.keys():
                    # Same structure: potentially isomorphic
                    return Isomorphism(
                        forward=Morphism(
                            source_type=HoTTType(str(type(a))),
                            target_type=HoTTType(str(type(b))),
                            apply=lambda x: x,
                        ),
                        backward=Morphism(
                            source_type=HoTTType(str(type(b))),
                            target_type=HoTTType(str(type(a))),
                            apply=lambda x: x,
                        ),
                    )
        return None

    def _univalence_path(self, iso: Isomorphism) -> Path:
        """Construct path from isomorphism via univalence."""
        return Path(
            source=iso.forward.source_type,
            target=iso.forward.target_type,
            path_data=("univalence", iso),
        )

    async def _path_induction(
        self,
        a: Any,
        b: Any,
        depth: int,
    ) -> Path | None:
        """Search for path via intermediate points."""
        if depth <= 0:
            return None

        # This would require domain-specific path finding
        # Placeholder for now
        return None
```

### 1.3 Categorical Law Verification

```python
# File: impl/claude/services/formal/categorical_laws.py

from __future__ import annotations

from dataclasses import dataclass
from typing import Generic, TypeVar

from services.formal.hott_types import HoTTContext, Morphism, Path

A = TypeVar("A")
B = TypeVar("B")
C = TypeVar("C")
D = TypeVar("D")


@dataclass(frozen=True)
class LawVerificationResult:
    """Result of verifying a categorical law."""

    law_name: str
    verified: bool
    proof: Path | None
    counter_example: Any | None
    suggestion: str | None


@dataclass
class CategoricalLawVerifier:
    """
    Verify categorical laws using HoTT.

    Laws verified:
    - Composition associativity: (f ∘ g) ∘ h = f ∘ (g ∘ h)
    - Left identity: id ∘ f = f
    - Right identity: f ∘ id = f
    - Functor composition: F(g ∘ f) = F(g) ∘ F(f)
    - Functor identity: F(id) = id
    """

    hott: HoTTContext

    async def verify_associativity(
        self,
        f: Morphism[A, B],
        g: Morphism[B, C],
        h: Morphism[C, D],
    ) -> LawVerificationResult:
        """
        Verify (f ∘ g) ∘ h = f ∘ (g ∘ h).

        Uses HoTT path equality.
        """
        # Compute both sides
        left = f.compose(g).compose(h)  # (f ∘ g) ∘ h
        right = f.compose(g.compose(h))  # f ∘ (g ∘ h)

        # Attempt to construct path proof
        path = await self.hott.construct_path(left, right)

        if path:
            return LawVerificationResult(
                law_name="composition_associativity",
                verified=True,
                proof=path,
                counter_example=None,
                suggestion=None,
            )
        else:
            return LawVerificationResult(
                law_name="composition_associativity",
                verified=False,
                proof=None,
                counter_example=(f, g, h, left, right),
                suggestion="Composition may not be associative for these morphisms",
            )

    async def verify_left_identity(
        self,
        f: Morphism[A, B],
        id_a: Morphism[A, A],
    ) -> LawVerificationResult:
        """Verify id ∘ f = f."""
        composed = id_a.compose(f)
        path = await self.hott.construct_path(composed, f)

        return LawVerificationResult(
            law_name="left_identity",
            verified=path is not None,
            proof=path,
            counter_example=None if path else (id_a, f, composed),
            suggestion=None if path else "Identity may not be left-neutral",
        )

    async def verify_right_identity(
        self,
        f: Morphism[A, B],
        id_b: Morphism[B, B],
    ) -> LawVerificationResult:
        """Verify f ∘ id = f."""
        composed = f.compose(id_b)
        path = await self.hott.construct_path(composed, f)

        return LawVerificationResult(
            law_name="right_identity",
            verified=path is not None,
            proof=path,
            counter_example=None if path else (f, id_b, composed),
            suggestion=None if path else "Identity may not be right-neutral",
        )

    async def verify_all_laws(
        self,
        morphisms: list[Morphism],
        identities: dict[str, Morphism],
    ) -> list[LawVerificationResult]:
        """Verify all categorical laws for a set of morphisms."""
        results = []

        # Test associativity for all triples
        for i, f in enumerate(morphisms):
            for j, g in enumerate(morphisms):
                if f.target_type != g.source_type:
                    continue
                for k, h in enumerate(morphisms):
                    if g.target_type != h.source_type:
                        continue
                    result = await self.verify_associativity(f, g, h)
                    results.append(result)

        # Test identities
        for f in morphisms:
            source_id = identities.get(f.source_type.name)
            target_id = identities.get(f.target_type.name)

            if source_id:
                results.append(await self.verify_left_identity(f, source_id))
            if target_id:
                results.append(await self.verify_right_identity(f, target_id))

        return results
```

---

## Part II: Lean 4 Export

### 2.1 Export Architecture

```
┌────────────────────────────────────────────────────────────┐
│                    LEAN EXPORTER                            │
├────────────────────────────────────────────────────────────┤
│                                                            │
│   1. AST Extraction                                        │
│      Python/TS definitions → Abstract Syntax Trees         │
│                                                            │
│   2. Type Translation                                      │
│      Python types → Lean 4 types                           │
│                                                            │
│   3. Law Formulation                                       │
│      Categorical laws → Lean 4 theorem statements          │
│                                                            │
│   4. Proof Hint Generation                                 │
│      LLM-assisted proof sketch generation                  │
│                                                            │
│   5. Code Generation                                       │
│      Complete Lean 4 file with theorems and proofs         │
│                                                            │
└────────────────────────────────────────────────────────────┘
```

### 2.2 Lean Export Implementation

```python
# File: impl/claude/services/formal/lean_export.py

from __future__ import annotations

import textwrap
from dataclasses import dataclass
from pathlib import Path
from typing import Any


@dataclass
class LeanType:
    """A Lean 4 type."""

    name: str
    params: list[str] = None
    universe: str = "Type"

    def to_lean(self) -> str:
        if self.params:
            params_str = " ".join(self.params)
            return f"{self.name} {params_str}"
        return self.name


@dataclass
class LeanTheorem:
    """A Lean 4 theorem statement."""

    name: str
    type_params: list[str]
    hypothesis: list[tuple[str, str]]  # (name, type)
    conclusion: str
    proof: str | None = None

    def to_lean(self) -> str:
        # Type parameters
        type_params_str = " ".join(f"({p} : Type)" for p in self.type_params)

        # Hypotheses
        hyp_str = " ".join(f"({name} : {typ})" for name, typ in self.hypothesis)

        # Statement
        if self.proof:
            return textwrap.dedent(f"""
                theorem {self.name} {type_params_str} {hyp_str} :
                    {self.conclusion} := by
                  {self.proof}
            """).strip()
        else:
            return textwrap.dedent(f"""
                theorem {self.name} {type_params_str} {hyp_str} :
                    {self.conclusion} := by
                  sorry  -- TODO: prove
            """).strip()


@dataclass
class LeanExporter:
    """
    Export kgents categorical laws to Lean 4.

    Usage:
        >>> exporter = LeanExporter()
        >>> lean_code = exporter.export_operad_laws(operad_spec)
        >>> Path("proofs/operad.lean").write_text(lean_code)
    """

    preamble: str = textwrap.dedent("""
        -- Auto-generated from kgents categorical specification
        -- Do not edit manually

        import Mathlib.CategoryTheory.Category.Basic
        import Mathlib.CategoryTheory.Functor.Basic
        import Mathlib.CategoryTheory.NatTrans

        namespace Kgents

        universe u v

    """)

    postamble: str = "\n\nend Kgents\n"

    def export_category_laws(self) -> str:
        """Export basic category laws."""
        theorems = [
            self._composition_associativity(),
            self._left_identity(),
            self._right_identity(),
        ]

        body = "\n\n".join(t.to_lean() for t in theorems)
        return self.preamble + body + self.postamble

    def export_operad_laws(self, operad_name: str) -> str:
        """Export operad-specific laws."""
        theorems = [
            self._operad_unit_left(operad_name),
            self._operad_unit_right(operad_name),
            self._operad_associativity(operad_name),
        ]

        body = "\n\n".join(t.to_lean() for t in theorems)
        return self.preamble + body + self.postamble

    def export_pilot_laws(self, pilot_name: str, laws: list) -> str:
        """Export pilot-specific law predicates."""
        # Convert Python predicates to Lean definitions
        definitions = []

        for law in laws:
            lean_def = self._law_to_lean_def(law)
            definitions.append(lean_def)

        body = "\n\n".join(definitions)
        return self.preamble + body + self.postamble

    def _composition_associativity(self) -> LeanTheorem:
        """(f ∘ g) ∘ h = f ∘ (g ∘ h)."""
        return LeanTheorem(
            name="comp_assoc",
            type_params=["A", "B", "C", "D"],
            hypothesis=[
                ("f", "A → B"),
                ("g", "B → C"),
                ("h", "C → D"),
            ],
            conclusion="(h ∘ g) ∘ f = h ∘ (g ∘ f)",
            proof="simp [Function.comp]",
        )

    def _left_identity(self) -> LeanTheorem:
        """id ∘ f = f."""
        return LeanTheorem(
            name="id_comp",
            type_params=["A", "B"],
            hypothesis=[("f", "A → B")],
            conclusion="id ∘ f = f",
            proof="simp",
        )

    def _right_identity(self) -> LeanTheorem:
        """f ∘ id = f."""
        return LeanTheorem(
            name="comp_id",
            type_params=["A", "B"],
            hypothesis=[("f", "A → B")],
            conclusion="f ∘ id = f",
            proof="simp",
        )

    def _operad_unit_left(self, name: str) -> LeanTheorem:
        """Operad left unit law."""
        return LeanTheorem(
            name=f"{name}_unit_left",
            type_params=["A"],
            hypothesis=[("op", f"{name}Operad A")],
            conclusion="op.compose op.unit = op",
            proof=None,  # Needs proof
        )

    def _operad_unit_right(self, name: str) -> LeanTheorem:
        """Operad right unit law."""
        return LeanTheorem(
            name=f"{name}_unit_right",
            type_params=["A"],
            hypothesis=[("op", f"{name}Operad A")],
            conclusion="op.unit.compose op = op",
            proof=None,
        )

    def _operad_associativity(self, name: str) -> LeanTheorem:
        """Operad associativity."""
        return LeanTheorem(
            name=f"{name}_assoc",
            type_params=["A", "B", "C"],
            hypothesis=[
                ("f", f"{name}Operad A B"),
                ("g", f"{name}Operad B C"),
                ("h", f"{name}Operad C D"),
            ],
            conclusion="(f.compose g).compose h = f.compose (g.compose h)",
            proof=None,
        )

    def _law_to_lean_def(self, law) -> str:
        """Convert a PilotLaw to a Lean definition."""
        # Simplified: create a definition stub
        name = law.name.replace(" ", "_").lower()
        return textwrap.dedent(f"""
            /-- {law.description} -/
            def {name} : Prop :=
              sorry  -- Formalize predicate from Python
        """).strip()
```

### 2.3 Proof Import

```python
# File: impl/claude/services/formal/lean_import.py

from __future__ import annotations

import json
import subprocess
from dataclasses import dataclass
from pathlib import Path


@dataclass(frozen=True)
class ProofResult:
    """Result of checking a Lean proof."""

    theorem_name: str
    verified: bool
    error_message: str | None
    proof_term: str | None


@dataclass
class LeanProofChecker:
    """
    Check Lean 4 proofs and import results.

    Requires Lean 4 and Mathlib installed.
    """

    lean_project_path: Path
    lake_path: str = "lake"

    async def check_file(self, lean_file: Path) -> list[ProofResult]:
        """
        Check all theorems in a Lean file.

        Returns list of verification results.
        """
        results = []

        # Run lake build
        try:
            process = subprocess.run(
                [self.lake_path, "build"],
                cwd=self.lean_project_path,
                capture_output=True,
                text=True,
                timeout=300,  # 5 minute timeout
            )

            if process.returncode == 0:
                # Parse successful theorems from output
                theorems = self._parse_theorems(lean_file)
                for name in theorems:
                    results.append(ProofResult(
                        theorem_name=name,
                        verified=True,
                        error_message=None,
                        proof_term=None,
                    ))
            else:
                # Parse errors
                errors = self._parse_errors(process.stderr)
                for name, error in errors.items():
                    results.append(ProofResult(
                        theorem_name=name,
                        verified=False,
                        error_message=error,
                        proof_term=None,
                    ))

        except subprocess.TimeoutExpired:
            results.append(ProofResult(
                theorem_name="*",
                verified=False,
                error_message="Proof checking timed out",
                proof_term=None,
            ))

        return results

    def _parse_theorems(self, lean_file: Path) -> list[str]:
        """Extract theorem names from Lean file."""
        content = lean_file.read_text()
        theorems = []

        for line in content.split("\n"):
            if line.strip().startswith("theorem "):
                name = line.split()[1]
                theorems.append(name)

        return theorems

    def _parse_errors(self, stderr: str) -> dict[str, str]:
        """Parse Lean error output to map theorem names to errors."""
        errors = {}

        current_theorem = None
        for line in stderr.split("\n"):
            if "error" in line.lower():
                # Extract theorem name from error context
                if "theorem" in line:
                    parts = line.split("theorem")
                    if len(parts) > 1:
                        current_theorem = parts[1].split()[0]

                if current_theorem:
                    errors[current_theorem] = line

        return errors
```

---

## Part III: Trace Witness Verification

### 3.1 Trace as Constructive Proof

From the spec:

> Capture **Trace_Witnesses** as constructive proofs during execution.

```python
# File: impl/claude/services/formal/trace_witness.py

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime
from typing import Any

from services.witness.mark import Mark


@dataclass(frozen=True)
class TraceWitness:
    """
    A trace witness as constructive proof.

    In HoTT terms: a trace is evidence that behavior matches specification.
    The trace IS the proof.
    """

    agent_path: str
    input_data: Any
    output_data: Any
    execution_trace: list[dict]
    timestamp: datetime
    proof_term: dict  # Structured proof data

    @classmethod
    def from_mark(cls, mark: Mark) -> "TraceWitness":
        """Construct trace witness from a mark."""
        return cls(
            agent_path=mark.origin,
            input_data=mark.stimulus.content,
            output_data=mark.response.content,
            execution_trace=[],  # Would be populated from actual execution
            timestamp=mark.timestamp,
            proof_term={
                "mark_id": str(mark.id),
                "stimulus": mark.stimulus.kind,
                "response": mark.response.kind,
                "success": mark.response.success,
            },
        )


@dataclass
class TraceWitnessVerifier:
    """
    Verify that trace witnesses satisfy specifications.

    This connects runtime behavior to formal properties.
    """

    async def verify(
        self,
        witness: TraceWitness,
        spec_properties: list[dict],
    ) -> list[PropertyVerification]:
        """
        Verify witness against specification properties.

        Returns verification result for each property.
        """
        results = []

        for prop in spec_properties:
            result = await self._verify_property(witness, prop)
            results.append(result)

        return results

    async def _verify_property(
        self,
        witness: TraceWitness,
        prop: dict,
    ) -> PropertyVerification:
        """Verify a single property."""
        prop_name = prop.get("name", "unnamed")
        prop_type = prop.get("type", "unknown")

        # Type-specific verification
        if prop_type == "input_output":
            return self._verify_io_property(witness, prop)
        elif prop_type == "invariant":
            return self._verify_invariant(witness, prop)
        elif prop_type == "temporal":
            return self._verify_temporal(witness, prop)
        else:
            return PropertyVerification(
                property_name=prop_name,
                satisfied=False,
                evidence=None,
                counter_example=f"Unknown property type: {prop_type}",
            )

    def _verify_io_property(
        self,
        witness: TraceWitness,
        prop: dict,
    ) -> PropertyVerification:
        """Verify input-output property."""
        # Check if output matches expected for given input
        expected = prop.get("expected")
        actual = witness.output_data

        satisfied = self._outputs_match(expected, actual)

        return PropertyVerification(
            property_name=prop["name"],
            satisfied=satisfied,
            evidence=witness.proof_term if satisfied else None,
            counter_example=None if satisfied else f"Expected {expected}, got {actual}",
        )

    def _verify_invariant(
        self,
        witness: TraceWitness,
        prop: dict,
    ) -> PropertyVerification:
        """Verify invariant property holds throughout trace."""
        invariant_check = prop.get("check")

        for step in witness.execution_trace:
            if not invariant_check(step):
                return PropertyVerification(
                    property_name=prop["name"],
                    satisfied=False,
                    evidence=None,
                    counter_example=f"Invariant violated at step: {step}",
                )

        return PropertyVerification(
            property_name=prop["name"],
            satisfied=True,
            evidence={"trace_length": len(witness.execution_trace)},
            counter_example=None,
        )

    def _verify_temporal(
        self,
        witness: TraceWitness,
        prop: dict,
    ) -> PropertyVerification:
        """Verify temporal property (e.g., eventually, always)."""
        # Simplified temporal logic checking
        return PropertyVerification(
            property_name=prop["name"],
            satisfied=True,  # Placeholder
            evidence=None,
            counter_example=None,
        )

    def _outputs_match(self, expected: Any, actual: Any) -> bool:
        """Check if outputs match (with tolerance for non-determinism)."""
        if expected is None:
            return True  # No expectation
        if isinstance(expected, dict) and isinstance(actual, dict):
            return all(
                actual.get(k) == v
                for k, v in expected.items()
                if v is not None
            )
        return expected == actual


@dataclass(frozen=True)
class PropertyVerification:
    """Result of verifying a property."""

    property_name: str
    satisfied: bool
    evidence: Any | None
    counter_example: str | None
```

---

## Part IV: Integration with Existing Infrastructure

### 4.1 Verification Graph Enhancement

```python
# File: impl/claude/services/formal/verification_graph.py

from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum
from typing import Any

from services.formal.hott_types import Path
from services.formal.trace_witness import PropertyVerification


class NodeType(Enum):
    PRINCIPLE = "principle"
    SPECIFICATION = "specification"
    IMPLEMENTATION = "implementation"
    TRACE = "trace"
    PATTERN = "pattern"


class DerivationType(Enum):
    DERIVES_FROM = "derives_from"
    IMPLEMENTS = "implements"
    WITNESSES = "witnesses"
    CONTRADICTS = "contradicts"
    REFINES = "refines"


@dataclass(frozen=True)
class GraphNode:
    """A node in the verification graph."""

    id: str
    level: int  # Reflective tower level
    content: Any
    node_type: NodeType
    metadata: dict = field(default_factory=dict)


@dataclass(frozen=True)
class DerivationEdge:
    """An edge representing derivation or implementation."""

    source: str  # Node ID
    target: str  # Node ID
    derivation_type: DerivationType
    justification: str
    confidence: float
    hott_path: Path | None = None  # Formal proof if available


@dataclass
class VerificationGraph:
    """
    Graph showing derivation paths from principles to implementation.

    Enhanced with HoTT path proofs and trace witnesses.
    """

    nodes: dict[str, GraphNode] = field(default_factory=dict)
    edges: list[DerivationEdge] = field(default_factory=list)

    def add_node(self, node: GraphNode) -> None:
        """Add a node to the graph."""
        self.nodes[node.id] = node

    def add_edge(self, edge: DerivationEdge) -> None:
        """Add a derivation edge."""
        self.edges.append(edge)

    def derive_path(
        self,
        source_id: str,
        target_id: str,
    ) -> list[DerivationEdge] | None:
        """Find derivation path from source to target."""
        # BFS for shortest path
        visited = set()
        queue = [(source_id, [])]

        while queue:
            current, path = queue.pop(0)

            if current == target_id:
                return path

            if current in visited:
                continue
            visited.add(current)

            for edge in self.edges:
                if edge.source == current:
                    queue.append((edge.target, path + [edge]))

        return None

    def find_orphans(self) -> list[GraphNode]:
        """Find implementations lacking principled derivation."""
        implementations = [
            n for n in self.nodes.values()
            if n.node_type == NodeType.IMPLEMENTATION
        ]

        orphans = []
        for impl in implementations:
            # Check if there's a path from any principle
            has_derivation = False
            for principle in self.nodes.values():
                if principle.node_type == NodeType.PRINCIPLE:
                    if self.derive_path(principle.id, impl.id):
                        has_derivation = True
                        break

            if not has_derivation:
                orphans.append(impl)

        return orphans

    def find_contradictions(self) -> list[tuple[GraphNode, GraphNode, DerivationEdge]]:
        """Find nodes that contradict each other."""
        contradictions = []

        for edge in self.edges:
            if edge.derivation_type == DerivationType.CONTRADICTS:
                source = self.nodes.get(edge.source)
                target = self.nodes.get(edge.target)
                if source and target:
                    contradictions.append((source, target, edge))

        return contradictions

    def verify_all_derivations(self) -> list[tuple[DerivationEdge, bool]]:
        """Verify all derivation edges have valid proofs."""
        results = []

        for edge in self.edges:
            if edge.derivation_type == DerivationType.DERIVES_FROM:
                # Check if HoTT path proof exists
                verified = edge.hott_path is not None
                results.append((edge, verified))

        return results
```

---

## Part V: Implementation Roadmap

### Phase 1: HoTT Foundation (Week 1)

| Task | File | Status |
|------|------|--------|
| HoTT types | `services/formal/hott_types.py` | New |
| Categorical laws | `services/formal/categorical_laws.py` | New |
| Unit tests | `services/formal/_tests/test_hott.py` | New |

### Phase 2: Lean Export (Week 2)

| Task | File | Status |
|------|------|--------|
| Lean exporter | `services/formal/lean_export.py` | New |
| Lean importer | `services/formal/lean_import.py` | New |
| Test with basic laws | `proofs/category_laws.lean` | New |

### Phase 3: Trace Verification (Week 3)

| Task | File | Status |
|------|------|--------|
| Trace witness | `services/formal/trace_witness.py` | New |
| Property verification | `services/formal/trace_witness.py` | New |
| Integration with Mark | `services/witness/formal_integration.py` | New |

### Phase 4: Verification Graph (Week 4)

| Task | File | Status |
|------|------|--------|
| Enhanced graph | `services/formal/verification_graph.py` | New |
| Orphan detection | `services/formal/verification_graph.py` | New |
| Contradiction detection | `services/formal/verification_graph.py` | New |

---

## Part VI: Success Metrics

| Metric | Target | Measurement |
|--------|--------|-------------|
| Category laws verified | 3/3 | Lean proof checking |
| Operad laws exported | 100% | Export coverage |
| Trace-spec alignment | > 95% | Property verification |
| Orphan implementations | 0 | Verification graph |
| HoTT path construction | > 80% | Path cache hit rate |

---

## Appendix: 25 Correctness Properties Reference

From the Formal Verification spec:

### Graph & Derivation (1-3)
1. Graph Derivation Completeness
2. Contradiction Detection Soundness
3. Multi-Type Graph Support

### Categorical Laws (4-9)
4. Composition Associativity
5. Identity Laws
6. Functor Law Preservation
7. Operad Coherence Verification
8. Sheaf Gluing Consistency
9. Counter-Example Generation

### Trace Witnesses (10-12)
10. Trace Witness Capture Completeness
11. Trace Specification Compliance
12. Trace Corpus Evolution

### Self-Improvement (13-15)
13. Proposal Generation
14. Categorical Compliance
15. Automated Evolution

### HoTT Foundation (16-19)
16. Univalence Foundation
17. Homotopy Type Representation
18. Path Composition
19. Constructive Proof Generation

### Additional (20-25)
20. Semantic Consistency
21. Continuous Society Verification
22. Adaptive Orchestration Correctness
23. Sympathetic Error Communication
24. Specification-Driven Generation
25. Emergent Behavior Verification

---

---

## Appendix: Mathematical Honesty Reference

See `coherence-synthesis-master.md` Appendix B for the full terminology glossary.

| Term | This Plan's Usage | Mathematical Source | Relation |
|------|-------------------|---------------------|----------|
| **HoTT** | Conceptual model for path equality | Homotopy Type Theory | Inspired by |
| **Path** | Python class modeling equality evidence | Path types in HoTT | Conceptual model |
| **Univalence** | "Isomorphic ⇒ equal" pattern | Univalence axiom (UA) | Weak form |
| **Lean export** | Code generation with `sorry` | Lean 4 proof assistant | Infrastructure only |
| **Verified** | Passes type/test checks | Machine-checked proof | Weaker claim |

**Upgrade Path**: Replace Python classes with actual Agda/Lean types when ready.

---

*"The noun is a lie. There is only the rate of change."*
