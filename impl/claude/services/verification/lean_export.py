"""
Lean 4 Export for kgents Categorical Laws.

This module generates Lean 4 code for categorical law verification,
allowing kgents' conceptual models to be formally verified using
Mathlib's category theory library.

IMPORTANT: This generates Lean 4 code but does NOT execute it.
The generated code should be compiled with a Lean 4 installation
and Mathlib for genuine formal verification.

Usage:
    exporter = LeanExporter()
    lean_code = exporter.export_category_laws()
    # Write to .lean file and compile with Lean 4
"""

from __future__ import annotations

import textwrap
from dataclasses import dataclass, field


@dataclass
class LeanTheorem:
    """
    Representation of a Lean 4 theorem for code generation.

    This captures the structure of a theorem without executing it.
    The generated Lean code can be compiled separately for formal verification.
    """

    name: str
    type_params: list[str] = field(default_factory=list)
    hypothesis: list[tuple[str, str]] = field(default_factory=list)
    conclusion: str = ""
    proof: str | None = None

    def to_lean(self) -> str:
        """Generate Lean 4 theorem syntax."""
        type_params_str = " ".join(f"({p} : Type)" for p in self.type_params)
        hyp_str = " ".join(f"({name} : {typ})" for name, typ in self.hypothesis)
        proof_line = self.proof if self.proof else "sorry"

        # Build the theorem declaration
        parts = ["theorem", self.name]
        if type_params_str:
            parts.append(type_params_str)
        if hyp_str:
            parts.append(hyp_str)
        parts.append(":")
        parts.append(self.conclusion)
        parts.append(":= by")

        declaration = " ".join(parts)
        return f"{declaration}\n  {proof_line}"


class LeanExporter:
    """
    Export kgents categorical laws to Lean 4.

    This class generates Lean 4 code that can be compiled with Mathlib
    for formal verification of categorical laws. The generated code
    uses standard Mathlib tactics and doesn't require custom definitions.

    IMPORTANT: This is a code generator, not a proof checker.
    The generated code must be compiled with Lean 4 to verify correctness.
    """

    PREAMBLE = textwrap.dedent("""
        -- Auto-generated from kgents
        -- Formal verification of categorical laws
        -- Requires: Lean 4 with Mathlib

        import Mathlib.CategoryTheory.Category.Basic

        namespace Kgents
    """).strip()

    POSTAMBLE = "\nend Kgents"

    def export_category_laws(self) -> str:
        """
        Generate Lean 4 code for all categorical laws.

        Returns complete Lean 4 source file with:
        - Composition associativity
        - Left identity
        - Right identity

        These are the fundamental laws that define a category.
        """
        theorems = [
            self._composition_associativity(),
            self._left_identity(),
            self._right_identity(),
        ]
        body = "\n\n".join(t.to_lean() for t in theorems)
        return f"{self.PREAMBLE}\n\n{body}\n{self.POSTAMBLE}"

    def _composition_associativity(self) -> LeanTheorem:
        """
        Generate theorem for composition associativity.

        States: (h . g) . f = h . (g . f)

        This is the fundamental associativity law for morphism composition.
        In Lean 4 with Mathlib, this is provable by simplification.
        """
        return LeanTheorem(
            name="comp_assoc",
            type_params=["A", "B", "C", "D"],
            hypothesis=[("f", "A -> B"), ("g", "B -> C"), ("h", "C -> D")],
            conclusion="(h . g) . f = h . (g . f)",
            proof="simp [Function.comp]",
        )

    def _left_identity(self) -> LeanTheorem:
        """
        Generate theorem for left identity.

        States: id . f = f

        Composing with identity on the left yields the original morphism.
        """
        return LeanTheorem(
            name="id_comp",
            type_params=["A", "B"],
            hypothesis=[("f", "A -> B")],
            conclusion="id . f = f",
            proof="simp",
        )

    def _right_identity(self) -> LeanTheorem:
        """
        Generate theorem for right identity.

        States: f . id = f

        Composing with identity on the right yields the original morphism.
        """
        return LeanTheorem(
            name="comp_id",
            type_params=["A", "B"],
            hypothesis=[("f", "A -> B")],
            conclusion="f . id = f",
            proof="simp",
        )

    def export_functor_laws(self) -> str:
        """
        Generate Lean 4 code for functor laws.

        Functors must preserve:
        - Identity: F(id) = id
        - Composition: F(g . f) = F(g) . F(f)
        """
        theorems = [
            LeanTheorem(
                name="functor_id",
                type_params=["A"],
                hypothesis=[("F", "Type -> Type")],
                conclusion="F id = id",
                proof="sorry  -- Requires functor axioms",
            ),
            LeanTheorem(
                name="functor_comp",
                type_params=["A", "B", "C"],
                hypothesis=[
                    ("F", "Type -> Type"),
                    ("f", "A -> B"),
                    ("g", "B -> C"),
                ],
                conclusion="F (g . f) = F g . F f",
                proof="sorry  -- Requires functor axioms",
            ),
        ]
        body = "\n\n".join(t.to_lean() for t in theorems)
        return f"{self.PREAMBLE}\n\n-- Functor Laws\n\n{body}\n{self.POSTAMBLE}"

    def export_natural_transformation_laws(self) -> str:
        """
        Generate Lean 4 code for natural transformation laws.

        Natural transformations must satisfy the naturality square:
        For any f : A -> B, we have: eta_B . F(f) = G(f) . eta_A
        """
        theorem = LeanTheorem(
            name="naturality",
            type_params=["A", "B"],
            hypothesis=[
                ("F", "Type -> Type"),
                ("G", "Type -> Type"),
                ("eta", "(X : Type) -> F X -> G X"),
                ("f", "A -> B"),
            ],
            conclusion="eta B . F f = G f . eta A",
            proof="sorry  -- Requires naturality axiom",
        )
        return f"{self.PREAMBLE}\n\n-- Natural Transformation Laws\n\n{theorem.to_lean()}\n{self.POSTAMBLE}"
