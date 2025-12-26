"""
AGENTESE concept.categorical.* — Categorical Reasoning Probes.

This module exposes categorical law testing through AGENTESE paths.
Probes measure how well LLM reasoning satisfies category-theoretic laws.

AGENTESE Paths:
- concept.categorical.manifest      - Overview of categorical probes
- concept.categorical.monad         - Run monad law tests on a problem
- concept.categorical.sheaf         - Run sheaf coherence detection on trace
- concept.categorical.probe         - Run all probes on problem + trace
- concept.categorical.study         - Run correlation study (Phase 1 gate)

Philosophy:
    "LLM reasoning failures are not random. They follow patterns
    that category theory predicts."

    - Monad law violations → Chain-of-thought breakdowns
    - Sheaf incoherence → Hallucinations

See docs/theory/03-monadic-reasoning.md
See docs/theory/05-sheaf-coherence.md
See plans/categorical-reinvention-phase1-foundations.md
"""

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timezone
from typing import TYPE_CHECKING, Any

from ..affordances import AspectCategory, Effect, aspect
from ..node import (
    BaseLogosNode,
    BasicRendering,
    Observer,
    Renderable,
)
from ..registry import node

if TYPE_CHECKING:
    from bootstrap.umwelt import Umwelt


# === Constants ===

CATEGORICAL_AFFORDANCES: tuple[str, ...] = (
    "manifest",
    "monad",
    "sheaf",
    "probe",
    "study",
    "status",
)


# === Node Implementation ===


@node("concept.categorical", description="Categorical reasoning probes for LLM verification")
@dataclass
class CategoricalNode(BaseLogosNode):
    """
    concept.categorical — Categorical Reasoning Probes.

    Tests LLM reasoning for satisfaction of category-theoretic laws:
    - Monad laws: Identity and associativity in chain-of-thought
    - Sheaf coherence: Local claims glue into global consistency

    The core hypothesis (kgents 2.0):
        "If categorical laws correlate with reasoning correctness,
        we have a new paradigm for LLM verification."

    Phase 1 gate criteria:
    - Monad identity correlation r > 0.3
    - Sheaf coherence correlation r > 0.4
    - Combined AUC > 0.7
    """

    _handle: str = "concept.categorical"

    @property
    def handle(self) -> str:
        return self._handle

    def _get_affordances_for_archetype(self, archetype: str) -> tuple[str, ...]:
        """All archetypes can access categorical probes."""
        return CATEGORICAL_AFFORDANCES

    @aspect(
        category=AspectCategory.PERCEPTION,
        effects=[],
        help="Overview of categorical probes and kgents 2.0 hypothesis",
    )
    async def manifest(self, observer: Observer | "Umwelt[Any, Any]", **kwargs: Any) -> Renderable:
        """
        What are categorical probes? Why do they matter?
        """
        content = """## Categorical Reasoning Probes (concept.categorical)

> *"LLM reasoning failures are not random. They follow patterns
> that category theory predicts."*

### The Hypothesis

Category theory provides laws that characterize "good" reasoning:

1. **Monad Laws** — Rationality constraints on chain-of-thought
   - **Identity**: Trivial modifications shouldn't change answers
   - **Associativity**: Grouping of steps shouldn't matter

2. **Sheaf Coherence** — Consistency of beliefs
   - Local claims must agree on overlaps
   - Violations are hallucinations

### The Bet (kgents 2.0)

If categorical law satisfaction correlates with reasoning correctness,
we can use these laws as *verification signals* for LLM reasoning.

**Phase 1 Gate Criteria:**
| Metric | Threshold | Status |
|--------|-----------|--------|
| Monad identity correlation | r > 0.3 | Pending |
| Sheaf coherence correlation | r > 0.4 | Pending |
| Combined AUC | > 0.7 | Pending |

### Available Paths

- `concept.categorical.monad problem="..."` — Test monad laws
- `concept.categorical.sheaf trace="..."` — Test sheaf coherence
- `concept.categorical.probe problem="..." trace="..."` — Run all probes
- `concept.categorical.study` — Run correlation study
- `concept.categorical.status` — Check Phase 1 gate status

### Theory Foundation

See the theory monograph:
- Chapter 3: Monadic Reasoning (CoT as Kleisli composition)
- Chapter 5: Sheaf Coherence (hallucinations as gluing failures)
"""

        return BasicRendering(
            summary="Categorical probes: Testing LLM reasoning for law satisfaction",
            content=content,
            metadata={
                "probes": ["monad", "sheaf"],
                "phase1_status": "pending",
                "theory_chapters": [3, 5],
            },
        )

    @aspect(
        category=AspectCategory.PERCEPTION,
        effects=[],
        help="Test monad laws on a reasoning problem",
    )
    async def monad(
        self,
        observer: Observer | "Umwelt[Any, Any]",
        problem: str | None = None,
        n_samples: int = 5,
    ) -> Renderable:
        """
        Test monad law satisfaction for a problem.

        Args:
            problem: The reasoning problem to test
            n_samples: Samples for identity tests (default 5)

        Returns:
            MonadResult with identity and associativity scores
        """
        if not problem:
            return BasicRendering(
                summary="Monad probe requires problem",
                content='Usage: `kg concept.categorical.monad problem="What is 2+2?"`\n\n'
                "The monad probe tests:\n"
                "- **Identity law**: Do trivial prefixes change the answer?\n"
                "- **Associativity**: Does step grouping matter?\n\n"
                "Returns a score from 0-1 indicating law satisfaction.",
                metadata={"error": "missing_problem"},
            )

        try:
            from agents.k.llm import create_llm_client
            from services.categorical.probes import MonadProbe

            llm = create_llm_client(mock=False)
            probe = MonadProbe(llm)

            result = await probe.test_all(problem, n_samples=n_samples)

            # Format identity results
            identity_lines = []
            for r in result.identity_results:
                status = "✅" if r.passed else "❌"
                identity_lines.append(
                    f"| {r.modification_type} | `{r.modification_text[:20]}...` | {status} |"
                )

            content = f"""## Monad Law Test: {problem[:50]}...

### Identity Law (η >> f ≡ f)

*Adding trivial prefixes/suffixes shouldn't change answers.*

| Type | Modification | Result |
|------|--------------|--------|
{chr(10).join(identity_lines) if identity_lines else "| — | — | — |"}

**Score**: {result.identity_score:.1%}

### Associativity Law ((A >> B) >> C ≡ A >> (B >> C))

*Step grouping shouldn't affect final answer.*

**Score**: {result.associativity_score:.1%}
{"(Not tested - provide steps for associativity test)" if not result.associativity_results else ""}

### Overall Monad Score

**{result.overall_score:.1%}**

---

*A score of 1.0 indicates perfect law satisfaction.*
*Lower scores suggest reasoning instability.*
"""

            return BasicRendering(
                summary=f"Monad test: {result.overall_score:.0%} law satisfaction",
                content=content,
                metadata={
                    "problem": problem,
                    "identity_score": result.identity_score,
                    "associativity_score": result.associativity_score,
                    "overall_score": result.overall_score,
                    "identity_results": [
                        {
                            "passed": r.passed,
                            "type": r.modification_type,
                            "modification": r.modification_text,
                        }
                        for r in result.identity_results
                    ],
                },
            )

        except ImportError as e:
            return BasicRendering(
                summary="Monad probe unavailable",
                content=f"Import error: {e}\n\nThe categorical service may not be fully installed.",
                metadata={"error": str(e)},
            )
        except Exception as e:
            return BasicRendering(
                summary="Monad probe failed",
                content=f"Error running monad probe: {e}",
                metadata={"error": str(e)},
            )

    @aspect(
        category=AspectCategory.PERCEPTION,
        effects=[],
        help="Test sheaf coherence on a reasoning trace",
    )
    async def sheaf(
        self,
        observer: Observer | "Umwelt[Any, Any]",
        trace: str | None = None,
    ) -> Renderable:
        """
        Test sheaf coherence (consistency) of a reasoning trace.

        Args:
            trace: The reasoning trace to analyze

        Returns:
            CoherenceResult with violation details
        """
        if not trace:
            return BasicRendering(
                summary="Sheaf probe requires trace",
                content='Usage: `kg concept.categorical.sheaf trace="Let me think... X=5... but X=6..."`\n\n'
                "The sheaf probe detects:\n"
                "- Contradictory claims within reasoning\n"
                "- Local beliefs that don't glue globally\n\n"
                "Returns coherence score and specific violations.",
                metadata={"error": "missing_trace"},
            )

        try:
            from agents.k.llm import create_llm_client
            from services.categorical.probes import SheafDetector

            llm = create_llm_client(mock=False)
            detector = SheafDetector(llm)

            result = await detector.detect(trace)

            # Format claims
            claim_lines = []
            for c in result.claims[:10]:  # Limit display
                claim_lines.append(
                    f"| {c.source_position} | {c.content[:40]}... | {c.context[:20]} |"
                )

            # Format violations
            violation_lines = []
            for v in result.violations:
                violation_lines.append(
                    f"- **Claim {v.claim_a.source_position}**: {v.claim_a.content[:30]}...\n"
                    f"  **vs Claim {v.claim_b.source_position}**: {v.claim_b.content[:30]}..."
                )

            status = "✅ COHERENT" if result.is_coherent else "❌ INCOHERENT"

            content = f"""## Sheaf Coherence Test

**Status**: {status}
**Score**: {result.score:.1%}

### Extracted Claims ({len(result.claims)} total)

| Position | Claim | Context |
|----------|-------|---------|
{chr(10).join(claim_lines) if claim_lines else "| — | — | — |"}

### Violations ({len(result.violations)} found)

{chr(10).join(violation_lines) if violation_lines else "*No violations detected*"}

### Interpretation

{"The reasoning trace is **coherent** — local claims agree on overlaps." if result.is_coherent else f"The reasoning trace contains **{len(result.violations)} contradiction(s)** — this is a hallucination signal."}

---

*Coherence score = 1 - (violations / max_possible_violations)*
*Higher scores indicate more consistent reasoning.*
"""

            return BasicRendering(
                summary=f"Sheaf test: {result.score:.0%} coherence ({len(result.violations)} violations)",
                content=content,
                metadata={
                    "is_coherent": result.is_coherent,
                    "score": result.score,
                    "claim_count": len(result.claims),
                    "violation_count": len(result.violations),
                    "violations": [
                        {
                            "claim_a": v.claim_a.content,
                            "claim_b": v.claim_b.content,
                            "explanation": v.explanation,
                        }
                        for v in result.violations
                    ],
                },
            )

        except ImportError as e:
            return BasicRendering(
                summary="Sheaf probe unavailable",
                content=f"Import error: {e}",
                metadata={"error": str(e)},
            )
        except Exception as e:
            return BasicRendering(
                summary="Sheaf probe failed",
                content=f"Error running sheaf probe: {e}",
                metadata={"error": str(e)},
            )

    @aspect(
        category=AspectCategory.PERCEPTION,
        effects=[],
        help="Run all categorical probes on problem + trace",
    )
    async def probe(
        self,
        observer: Observer | "Umwelt[Any, Any]",
        problem: str | None = None,
        trace: str | None = None,
        n_samples: int = 5,
    ) -> Renderable:
        """
        Run all categorical probes on a problem and its reasoning trace.

        Args:
            problem: The reasoning problem
            trace: The reasoning trace (optional)
            n_samples: Samples for monad tests

        Returns:
            Combined ProbeResults
        """
        if not problem:
            return BasicRendering(
                summary="Probe requires problem",
                content='Usage: `kg concept.categorical.probe problem="What is 2+2?" trace="Let me think..."`\n\n'
                "Runs both monad and sheaf probes, returning combined score.",
                metadata={"error": "missing_problem"},
            )

        try:
            from agents.k.llm import create_llm_client
            from services.categorical.probes import CategoricalProbeRunner

            llm = create_llm_client(mock=False)
            runner = CategoricalProbeRunner(llm, emit_marks=True)

            results = await runner.probe(
                problem=problem,
                trace=trace or "",
                n_samples=n_samples,
            )

            content = f"""## Categorical Probe Results

**Problem**: {problem[:50]}...

### Scores

| Probe | Score | Interpretation |
|-------|-------|----------------|
| Monad Laws | {results.monad_score:.1%} | {"Good" if results.monad_score > 0.7 else "Poor"} law satisfaction |
| Sheaf Coherence | {results.coherence_score:.1%} | {"Coherent" if results.coherence_score > 0.8 else "Incoherent"} reasoning |
| **Combined** | **{results.combined_score:.1%}** | {"✅ Reliable" if results.combined_score > 0.7 else "⚠️ Unreliable"} |

### What This Means

{"**Reliable reasoning**: This problem/trace satisfies categorical laws, suggesting the reasoning is trustworthy." if results.combined_score > 0.7 else "**Unreliable reasoning**: Law violations detected. The reasoning may contain errors or hallucinations."}

---

*Combined score = average(monad_score, coherence_score)*
*Higher scores indicate more reliable reasoning.*
"""

            return BasicRendering(
                summary=f"Probes: {results.combined_score:.0%} combined categorical score",
                content=content,
                metadata={
                    "problem": problem,
                    "monad_score": results.monad_score,
                    "coherence_score": results.coherence_score,
                    "combined_score": results.combined_score,
                },
            )

        except ImportError as e:
            return BasicRendering(
                summary="Probe unavailable",
                content=f"Import error: {e}",
                metadata={"error": str(e)},
            )
        except Exception as e:
            return BasicRendering(
                summary="Probe failed",
                content=f"Error: {e}",
                metadata={"error": str(e)},
            )

    @aspect(
        category=AspectCategory.MUTATION,
        effects=[Effect.WRITES],
        help="Run correlation study (Phase 1 gate)",
    )
    async def study(
        self,
        observer: Observer | "Umwelt[Any, Any]",
        n_problems: int = 100,
    ) -> Renderable:
        """
        Run the Phase 1 correlation study.

        This is the core validation for kgents 2.0's hypothesis.

        Args:
            n_problems: Number of problems to study (default 100)

        Returns:
            StudyResult with correlations and gate status
        """
        return BasicRendering(
            summary="Study requires explicit initialization",
            content=f"""## Correlation Study

The correlation study validates kgents 2.0's core hypothesis.

**Warning**: This runs {n_problems} LLM calls and can be expensive.

### To Run

```python
from services.categorical.study import CorrelationStudy, ProblemSet, StudyConfig
from agents.k.llm import create_llm_client
from services.storage import get_kgents_data_root

llm = create_llm_client()
# Use XDG-compliant data directory
data_dir = get_kgents_data_root() / "categorical"
problem_set = ProblemSet.from_json(data_dir / "gsm8k_sample.json")

study = CorrelationStudy(llm, problem_set)
result = await study.run(StudyConfig(n_problems={n_problems}))

if result.passed_gate:
    print("Phase 1 validated!")
else:
    print(f"Blocked by: {{result.blockers}}")
```

### Gate Criteria

| Metric | Threshold | Required |
|--------|-----------|----------|
| Monad identity correlation | r > 0.3 | Yes |
| Sheaf coherence correlation | r > 0.4 | Yes |
| Combined AUC | > 0.7 | Yes |

Use `concept.categorical.status` to check current gate status.
""",
            metadata={
                "n_problems": n_problems,
                "gate_criteria": {
                    "monad_identity": 0.3,
                    "sheaf_coherence": 0.4,
                    "combined_auc": 0.7,
                },
            },
        )

    @aspect(
        category=AspectCategory.PERCEPTION,
        effects=[],
        help="Check Phase 1 gate status",
    )
    async def status(
        self,
        observer: Observer | "Umwelt[Any, Any]",
    ) -> Renderable:
        """
        Check the current status of the Phase 1 gate.

        Queries the ValidationEngine for categorical_phase1 status.
        """
        try:
            from services.validation.engine import get_validation_engine

            engine = get_validation_engine()
            initiative = engine.get_initiative("categorical_phase1")

            if not initiative:
                return BasicRendering(
                    summary="Phase 1 initiative not registered",
                    content="The categorical_phase1 initiative has not been registered.\n\n"
                    "Load it with:\n"
                    "```python\n"
                    "engine.register_from_yaml(Path('initiatives/categorical-phase1.yaml'))\n"
                    "```",
                    metadata={"status": "not_registered"},
                )

            # Try to get status
            status = engine.get_status("categorical_phase1")

            content = f"""## Phase 1: Categorical Foundations

**Status**: {"✅ PASSED" if status.last_run and status.last_run.passed else "⏳ PENDING" if not status.last_run else "❌ BLOCKED"}

### Propositions

| ID | Description | Threshold | Required |
|----|-------------|-----------|----------|
"""
            for prop in initiative.propositions:
                req = "Yes" if prop.required else "No"
                content += f"| {prop.id} | {prop.description[:40]}... | {prop.direction}{prop.threshold} | {req} |\n"

            if status.blockers:
                content += "\n### Blockers\n\n"
                for b in status.blockers:
                    content += f"- **{b.proposition.id}**: {b.current_value} (need {b.proposition.threshold})\n"

            content += "\n---\n\n"
            content += "Run `concept.categorical.study` to validate."

            return BasicRendering(
                summary=f"Phase 1: {'PASSED' if status.last_run and status.last_run.passed else 'PENDING'}",
                content=content,
                metadata={
                    "initiative_id": str(initiative.id),
                    "passed": status.last_run.passed if status.last_run else None,
                    "blockers": [
                        {"proposition": str(b.proposition.id), "gap": b.gap}
                        for b in status.blockers
                    ],
                },
            )

        except ImportError as e:
            return BasicRendering(
                summary="Validation engine unavailable",
                content=f"Import error: {e}",
                metadata={"error": str(e)},
            )
        except Exception as e:
            return BasicRendering(
                summary="Status check failed",
                content=f"Error: {e}",
                metadata={"error": str(e)},
            )

    async def _invoke_aspect(
        self,
        aspect: str,
        observer: "Umwelt[Any, Any]",
        **kwargs: Any,
    ) -> Any:
        """Route aspect invocations."""
        methods: dict[str, Any] = {
            "manifest": self.manifest,
            "monad": self.monad,
            "sheaf": self.sheaf,
            "probe": self.probe,
            "study": self.study,
            "status": self.status,
        }

        if aspect in methods:
            return await methods[aspect](observer, **kwargs)

        raise ValueError(f"Unknown aspect: {aspect}")


# === Factory ===

_categorical_node: CategoricalNode | None = None


def get_categorical_node() -> CategoricalNode:
    """Get or create the singleton CategoricalNode."""
    global _categorical_node
    if _categorical_node is None:
        _categorical_node = CategoricalNode()
    return _categorical_node


# === Exports ===

__all__ = [
    "CategoricalNode",
    "get_categorical_node",
    "CATEGORICAL_AFFORDANCES",
]
