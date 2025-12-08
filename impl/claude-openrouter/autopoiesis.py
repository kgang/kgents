"""
Autopoiesis - kgents improving itself using its own bootstrap agents.

This script uses {Contradict, Judge, Sublate, Fix} to analyze and improve
the kgents implementation. The target autopoiesis score is >50%.

Usage:
    python autopoiesis.py

What it does:
    1. Ground - Load current state (spec files, impl files, their contents)
    2. Contradict - Find tensions between spec and impl
    3. Judge - Evaluate implementations against 7 principles
    4. Sublate - Resolve or hold detected tensions
    5. Fix - Iterate until stable (all tensions resolved or held consciously)
"""

import asyncio
from dataclasses import dataclass
from pathlib import Path
from typing import Any

# Bootstrap imports
from bootstrap import (
    Contradict,
    ContradictInput,
    Ground,
    Judge,
    JudgeInput,
    Sublate,
    Fix,
    FixConfig,
    fix,
    make_default_principles,
)
from bootstrap.types import (
    Agent,
    Facts,
    HoldTension,
    PersonaSeed,
    Synthesis,
    Tension,
    TensionMode,
    Verdict,
    VerdictType,
    WorldSeed,
)


# ============================================================================
# Self-Analysis State
# ============================================================================


@dataclass
class SpecImplPair:
    """A specification and its corresponding implementation."""
    name: str
    spec_path: Path | None
    impl_path: Path | None
    spec_content: str | None = None
    impl_content: str | None = None


@dataclass
class AnalysisState:
    """State of the autopoiesis analysis."""
    pairs: list[SpecImplPair]
    tensions: list[Tension]
    resolutions: list[Synthesis | HoldTension]
    verdicts: list[tuple[str, Verdict]]
    iteration: int = 0

    def is_stable(self) -> bool:
        """Check if analysis has reached a stable state."""
        # Stable when all verdicts are ACCEPT and no unresolved tensions
        all_accepted = all(v.type == VerdictType.ACCEPT for _, v in self.verdicts)
        all_resolved = len(self.tensions) == len(self.resolutions)
        return all_accepted and all_resolved


# ============================================================================
# Custom Contradiction Checker for Spec vs Impl
# ============================================================================


def spec_impl_contradiction_check(
    spec: SpecImplPair, _: Any, mode: TensionMode
) -> Tension | None:
    """Check for contradictions between spec and implementation."""

    # Tension 1: Spec exists but no impl
    if spec.spec_path and not spec.impl_path:
        return Tension(
            mode=TensionMode.PRAGMATIC,
            thesis=f"Spec exists: {spec.spec_path}",
            antithesis="No implementation found",
            description=f"'{spec.name}' has spec but no implementation",
            severity=0.8,
        )

    # Tension 2: Impl exists but no spec
    if spec.impl_path and not spec.spec_path:
        return Tension(
            mode=TensionMode.PRAGMATIC,
            thesis="No specification found",
            antithesis=f"Impl exists: {spec.impl_path}",
            description=f"'{spec.name}' has implementation but no spec (spec-first violation)",
            severity=0.7,
        )

    # Tension 3: Both exist but impl lacks docstring (Judge-generate violation)
    if spec.impl_content and not ('"""' in spec.impl_content or "'''" in spec.impl_content):
        return Tension(
            mode=TensionMode.AXIOLOGICAL,
            thesis="Spec provides documentation",
            antithesis="Implementation lacks docstring",
            description=f"'{spec.name}' impl is not generative (no docstring)",
            severity=0.5,
        )

    return None


# ============================================================================
# Ground: Load Current State
# ============================================================================


def load_kgents_state() -> list[SpecImplPair]:
    """Load all spec/impl pairs from the kgents repository."""

    base = Path(__file__).parent.parent.parent  # kgents root
    spec_dir = base / "spec"
    impl_dir = base / "impl" / "claude-openrouter"

    pairs: list[SpecImplPair] = []

    # Known mappings
    mappings = [
        # Bootstrap agents (all specified in spec/bootstrap.md)
        ("bootstrap/Id", spec_dir / "bootstrap.md", impl_dir / "bootstrap" / "id.py"),
        ("bootstrap/Compose", spec_dir / "bootstrap.md", impl_dir / "bootstrap" / "compose.py"),
        ("bootstrap/Judge", spec_dir / "bootstrap.md", impl_dir / "bootstrap" / "judge.py"),
        ("bootstrap/Ground", spec_dir / "bootstrap.md", impl_dir / "bootstrap" / "ground.py"),
        ("bootstrap/Contradict", spec_dir / "bootstrap.md", impl_dir / "bootstrap" / "contradict.py"),
        ("bootstrap/Sublate", spec_dir / "bootstrap.md", impl_dir / "bootstrap" / "sublate.py"),
        ("bootstrap/Fix", spec_dir / "bootstrap.md", impl_dir / "bootstrap" / "fix.py"),

        # A-gents
        ("a-gents/skeleton", spec_dir / "a-gents" / "abstract" / "skeleton.md", impl_dir / "agents" / "a" / "skeleton.py"),
        ("a-gents/creativity", spec_dir / "a-gents" / "art" / "creativity-coach.md", impl_dir / "agents" / "a" / "creativity.py"),

        # B-gents
        ("b-gents/hypothesis", spec_dir / "b-gents" / "hypothesis-engine.md", impl_dir / "agents" / "b" / "hypothesis.py"),
        ("b-gents/bio-gent", spec_dir / "b-gents" / "bio-gent.md", impl_dir / "agents" / "b" / "robin.py"),  # Robin implements Bio-gent
        ("b-gents/robin", spec_dir / "b-gents" / "robin.md", impl_dir / "agents" / "b" / "robin.py"),

        # C-gents
        ("c-gents/composition", spec_dir / "c-gents" / "composition.md", impl_dir / "bootstrap" / "compose.py"),
        ("c-gents/functors", spec_dir / "c-gents" / "functors.md", impl_dir / "agents" / "c" / "functor.py"),
        ("c-gents/monads", spec_dir / "c-gents" / "monads.md", impl_dir / "agents" / "c" / "monad.py"),
        ("c-gents/conditional", spec_dir / "c-gents" / "conditional.md", impl_dir / "agents" / "c" / "conditional.py"),
        ("c-gents/parallel", spec_dir / "c-gents" / "parallel.md", impl_dir / "agents" / "c" / "parallel.py"),

        # H-gents
        ("h-gents/hegel", spec_dir / "h-gents" / "hegel.md", impl_dir / "agents" / "h" / "hegel.py"),
        ("h-gents/jung", spec_dir / "h-gents" / "jung.md", impl_dir / "agents" / "h" / "jung.py"),
        ("h-gents/lacan", spec_dir / "h-gents" / "lacan.md", impl_dir / "agents" / "h" / "lacan.py"),

        # K-gent
        ("k-gent/persona", spec_dir / "k-gent" / "persona.md", impl_dir / "agents" / "k" / "persona.py"),
        ("k-gent/evolution", spec_dir / "k-gent" / "evolution.md", impl_dir / "agents" / "k" / "evolution.py"),
    ]

    for name, spec_path, impl_path in mappings:
        spec_content = None
        impl_content = None

        if spec_path and spec_path.exists():
            spec_content = spec_path.read_text()
        if impl_path and impl_path.exists():
            impl_content = impl_path.read_text()

        pairs.append(SpecImplPair(
            name=name,
            spec_path=spec_path if spec_path and spec_path.exists() else None,
            impl_path=impl_path if impl_path and impl_path.exists() else None,
            spec_content=spec_content,
            impl_content=impl_content,
        ))

    return pairs


# ============================================================================
# The Autopoiesis Loop
# ============================================================================


async def run_autopoiesis() -> AnalysisState:
    """
    Run the autopoiesis loop: analyze kgents using kgents.

    Returns the final analysis state after Fix converges.
    """

    print("=" * 60)
    print("AUTOPOIESIS: kgents analyzing itself")
    print("=" * 60)

    # Step 1: Ground - Load current state
    print("\n[1] GROUND: Loading kgents state...")
    pairs = load_kgents_state()
    print(f"    Loaded {len(pairs)} spec/impl pairs")

    initial_state = AnalysisState(
        pairs=pairs,
        tensions=[],
        resolutions=[],
        verdicts=[],
        iteration=0,
    )

    # Step 2-5: Fix(Contradict >> Judge >> Sublate)
    async def analysis_step(state: AnalysisState) -> AnalysisState:
        """One iteration of the analysis loop."""
        state.iteration += 1
        print(f"\n[Iteration {state.iteration}]")

        # Contradict: Find tensions
        print("  [CONTRADICT] Finding tensions...")
        contradict = Contradict(checker=spec_impl_contradiction_check)
        new_tensions: list[Tension] = []

        for pair in state.pairs:
            tension = await contradict.invoke(ContradictInput(a=pair, b=None))
            if tension:
                new_tensions.append(tension)
                print(f"    ⚡ {tension.description}")

        # Judge: Evaluate against principles
        print("  [JUDGE] Evaluating implementations...")
        judge = Judge()
        principles = make_default_principles()
        verdicts: list[tuple[str, Verdict]] = []

        # Create dummy agents for pairs with implementations
        for pair in state.pairs:
            if pair.impl_path:
                # Create a minimal agent representation for judging
                @dataclass
                class ImplAgent(Agent[None, None]):
                    _name: str
                    _doc: str | None

                    @property
                    def name(self) -> str:
                        return self._name

                    async def invoke(self, _: None) -> None:
                        pass

                agent = ImplAgent(
                    _name=pair.name,
                    _doc=pair.impl_content[:200] if pair.impl_content else None,
                )
                agent.__doc__ = agent._doc

                verdict = await judge.invoke(JudgeInput(agent=agent, principles=principles))
                verdicts.append((pair.name, verdict))

                if verdict.type != VerdictType.ACCEPT:
                    print(f"    ❌ {pair.name}: {verdict.type.value} - {verdict.reasons}")

        # Sublate: Resolve tensions
        print("  [SUBLATE] Resolving tensions...")
        sublate = Sublate()
        resolutions: list[Synthesis | HoldTension] = []

        for tension in new_tensions:
            resolution = await sublate.invoke(tension)
            resolutions.append(resolution)

            if isinstance(resolution, HoldTension):
                print(f"    ⏸️  HOLD: {tension.description}")
                print(f"       Reason: {resolution.reason}")
            else:
                print(f"    ✅ RESOLVED: {tension.description}")
                print(f"       {resolution.resolution_type.value}: {resolution.explanation}")

        return AnalysisState(
            pairs=state.pairs,
            tensions=new_tensions,
            resolutions=resolutions,
            verdicts=verdicts,
            iteration=state.iteration,
        )

    # Run Fix until stable
    print("\n[FIX] Iterating to stability...")
    result = await fix(
        transform=analysis_step,
        initial=initial_state,
        equality_check=lambda a, b: a.is_stable() or b.iteration >= 3,
        max_iterations=5,
    )

    final_state = result.value

    # Report
    print("\n" + "=" * 60)
    print("AUTOPOIESIS REPORT")
    print("=" * 60)
    print(f"Iterations: {result.iterations}")
    print(f"Converged: {result.converged}")
    print(f"Tensions found: {len(final_state.tensions)}")
    print(f"Resolutions: {len(final_state.resolutions)}")

    held = sum(1 for r in final_state.resolutions if isinstance(r, HoldTension))
    resolved = len(final_state.resolutions) - held

    print(f"  - Resolved: {resolved}")
    print(f"  - Held: {held}")

    print(f"\nVerdicts:")
    accept_count = sum(1 for _, v in final_state.verdicts if v.type == VerdictType.ACCEPT)
    print(f"  - Accept: {accept_count}/{len(final_state.verdicts)}")

    # List held tensions (these need human judgment)
    if held > 0:
        print("\nHELD TENSIONS (require human judgment):")
        for t, r in zip(final_state.tensions, final_state.resolutions):
            if isinstance(r, HoldTension):
                print(f"  • {t.description}")
                print(f"    Revisit when: {r.revisit_conditions}")

    return final_state


# ============================================================================
# Main
# ============================================================================


if __name__ == "__main__":
    asyncio.run(run_autopoiesis())
