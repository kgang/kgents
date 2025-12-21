"""
Pass Operad: Grammar of Valid Pass Compositions

The operad defines which pass sequences are valid.
It treats passes as morphisms in the compiler category.

Ground >> Judge -> Valid
Judge >> Ground -> Invalid (wrong order)
(A >> B) >> C == A >> (B >> C) -> Associativity holds

The bootstrap agents (Id, Compose, Judge, Ground, Contradict,
Sublate, Fix) become L0 passes. ASHC compiles them from spec,
verifies the laws, and emits them as artifacts.

"The operad defines the grammar. The passes speak the language."
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import TYPE_CHECKING, Any, Callable, cast

from .bootstrap import (
    ContradictPass,
    FixPass,
    GroundPass,
    IdentityPass,
    JudgePass,
    SublatePass,
    create_contradict_pass,
    create_fix_pass,
    create_ground_pass,
    create_identity_pass,
    create_judge_pass,
    create_sublate_pass,
)
from .composition import ComposedPass, compose
from .core import CompositionLaw, LawResult, LawStatus, PassProtocol
from .laws import COMPOSITION_LAWS

if TYPE_CHECKING:
    pass


# =============================================================================
# Pass Operation
# =============================================================================


@dataclass(frozen=True)
class PassOperation:
    """
    An operation in the Pass Operad.

    Operations are factories that produce passes.
    They specify the arity (number of inputs) and
    how to instantiate the pass.
    """

    name: str
    arity: int
    input_type: str
    output_type: str
    instantiate: Callable[[], Any]  # Returns a PassProtocol-compatible object
    description: str = ""

    def __call__(self) -> Any:
        """Instantiate the pass."""
        return self.instantiate()


# =============================================================================
# Pass Operad
# =============================================================================


@dataclass
class PassOperad:
    """
    The grammar of valid pass compositions.

    Provides:
    1. Operations: factories for bootstrap passes
    2. Composition: via >> operator
    3. Law verification: identity, associativity, etc.

    Usage:
        operad = PASS_OPERAD
        pipeline = operad.compose(["ground", "judge", "fix"])
        result = await operad.verify_laws(pipeline)
    """

    name: str = "PassOperad"
    operations: dict[str, PassOperation] = field(default_factory=dict)
    composition_laws: tuple[CompositionLaw, ...] = COMPOSITION_LAWS

    def compose(self, pass_names: list[str]) -> Any:
        """
        Compose named passes into a pipeline.

        Args:
            pass_names: List of pass names to compose

        Returns:
            Composed pass (or single pass if only one name)

        Raises:
            ValueError: If any pass name is unknown
        """
        if not pass_names:
            return self._resolve_pass("id")

        passes = [self._resolve_pass(name) for name in pass_names]

        if len(passes) == 1:
            return passes[0]

        result = passes[0]
        for p in passes[1:]:
            result = result >> p

        return result

    def compose_str(self, expr: str) -> Any:
        """
        Compose passes from a string expression.

        Args:
            expr: Expression like "ground >> judge >> fix"

        Returns:
            Composed pass
        """
        # Parse the expression
        parts = [p.strip() for p in expr.split(">>")]
        return self.compose(parts)

    async def verify_laws(
        self,
        composed: PassProtocol | None = None,
    ) -> LawResult:
        """
        Verify all composition laws hold.

        Args:
            composed: Optional specific pass to verify.
                     If None, uses default test passes.

        Returns:
            Aggregated LawResult
        """
        # Create test passes
        test_passes = [
            self._resolve_pass("id"),
            self._resolve_pass("ground"),
            self._resolve_pass("judge"),
        ]

        results = []
        for law in self.composition_laws:
            try:
                result = await law.verify(*test_passes)
                results.append(result)
            except Exception as e:
                results.append(LawResult.error(law.name, str(e)))

        return LawResult.aggregate(results)

    async def verify_law(
        self,
        law_name: str,
        *passes: PassProtocol,
    ) -> LawResult:
        """
        Verify a specific law.

        Args:
            law_name: Name of the law to verify
            *passes: Passes to test with

        Returns:
            LawResult for the specific law
        """
        for law in self.composition_laws:
            if law.name == law_name:
                return await law.verify(*passes)

        return LawResult(
            law=law_name,
            status=LawStatus.SKIPPED,
            evidence=f"Law '{law_name}' not found",
        )

    def _resolve_pass(self, name: str) -> Any:
        """Resolve a pass name to an instance."""
        if name not in self.operations:
            raise ValueError(f"Unknown pass: {name}")
        return self.operations[name]()

    def get_operation(self, name: str) -> PassOperation | None:
        """Get an operation by name."""
        return self.operations.get(name)

    def list_passes(self) -> list[dict[str, str]]:
        """List all available passes with their types."""
        return [
            {
                "name": op.name,
                "arity": str(op.arity),
                "input": op.input_type,
                "output": op.output_type,
                "description": op.description,
            }
            for op in self.operations.values()
        ]

    def list_laws(self) -> list[dict[str, str]]:
        """List all composition laws."""
        return [
            {
                "name": law.name,
                "equation": law.equation,
            }
            for law in self.composition_laws
        ]


# =============================================================================
# ASHC Pass Operad Instance
# =============================================================================


def create_pass_operad() -> PassOperad:
    """
    Create the ASHC Pass Operad.

    The canonical operad with all 7 bootstrap passes as operations.
    """
    return PassOperad(
        name="ASHC_PASS_OPERAD",
        operations={
            "id": PassOperation(
                name="id",
                arity=0,
                input_type="A",
                output_type="A",
                instantiate=lambda: create_identity_pass(),
                description="Identity pass (no-op)",
            ),
            "ground": PassOperation(
                name="ground",
                arity=0,
                input_type="Void",
                output_type="Facts",
                instantiate=lambda: create_ground_pass(),
                description="Inject empirical data",
            ),
            "judge": PassOperation(
                name="judge",
                arity=1,
                input_type="Spec",
                output_type="Verdict",
                instantiate=lambda: create_judge_pass(),
                description="Validate against principles",
            ),
            "contradict": PassOperation(
                name="contradict",
                arity=2,
                input_type="(A, B)",
                output_type="Tension | None",
                instantiate=lambda: create_contradict_pass(),
                description="Detect inconsistencies",
            ),
            "sublate": PassOperation(
                name="sublate",
                arity=1,
                input_type="Tension",
                output_type="Synthesis",
                instantiate=lambda: create_sublate_pass(),
                description="Synthesize from tension",
            ),
            "fix": PassOperation(
                name="fix",
                arity=1,
                input_type="(A -> A)",
                output_type="A",
                instantiate=lambda: create_fix_pass(),
                description="Fixed-point iteration",
            ),
        },
        composition_laws=COMPOSITION_LAWS,
    )


# Global instance
PASS_OPERAD = create_pass_operad()


# =============================================================================
# CLI Rendering
# =============================================================================


def render_operad_manifest(operad: PassOperad = PASS_OPERAD) -> str:
    """
    Render the operad as an ASCII manifest.

    Per spec: user-visible output for `kg concept.compiler.operad.manifest`
    """
    lines = [
        "┌─ ASHC PASS OPERAD ────────────────────────────────────┐",
        "│ Passes:                                                │",
    ]

    for op in operad.operations.values():
        type_sig = f"{op.input_type} -> {op.output_type}"
        line = f"│   {op.name:12} : {type_sig:20} (arity {op.arity})│"
        lines.append(line.ljust(57) + "│")

    lines.append("│                                                        │")
    lines.append("│ Laws:                                                  │")

    for law in operad.composition_laws:
        line = f"│   ? {law.name:14} ({law.equation[:28]}...)"
        lines.append(line.ljust(57) + "│")

    lines.append("└────────────────────────────────────────────────────────┘")

    return "\n".join(lines)


async def render_law_verification(operad: PassOperad = PASS_OPERAD) -> str:
    """
    Render law verification result as ASCII.

    Per spec: `kg concept.compiler.operad.verify`
    """
    result = await operad.verify_laws()

    lines = [
        "┌─ LAW VERIFICATION ─────────────────────────────────────┐",
        "│                                                         │",
    ]

    for law in operad.composition_laws:
        law_result = await operad.verify_law(law.name)
        status_icon = "✓" if law_result.holds else "✗"
        status_text = "HOLDS" if law_result.holds else "VIOLATED"
        line = f"│  {law.name:16} [{status_icon}] {status_text:20}"
        lines.append(line.ljust(58) + "│")

    lines.append("│                                                         │")

    overall = "ALL LAWS VERIFIED" if result.holds else "VIOLATIONS FOUND"
    lines.append(f"│  Overall: {overall:44}│")
    lines.append("└─────────────────────────────────────────────────────────┘")

    return "\n".join(lines)


__all__ = [
    "PassOperation",
    "PassOperad",
    "PASS_OPERAD",
    "create_pass_operad",
    "render_operad_manifest",
    "render_law_verification",
]
