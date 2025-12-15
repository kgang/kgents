"""
Monograph Generator - Orchestrates multi-agent iterative generation with dialectical feedback.

This is the main engine that coordinates the five polynomial agents to produce
a complete, coherent, PhD-level monograph.
"""

import asyncio
from dataclasses import dataclass, field
from typing import Any
from pathlib import Path

# Import polynomial agents
from monograph.agents.mathematician import (
    MathematicianPolynomial,
    MathState,
    MathInput,
)
from monograph.agents.scientist import (
    ScientistPolynomial,
    ScienceState,
    ScienceInput,
)
from monograph.agents.philosopher import (
    PhilosopherPolynomial,
    PhilosophyState,
    PhilosophyInput,
)
from monograph.agents.psychologist import (
    PsychologistPolynomial,
    PsychologyState,
    PsychologyInput,
)
from monograph.agents.synthesizer import (
    SynthesizerPolynomial,
    SynthesisState,
    SynthesisInput,
)

# Import operad
from monograph.operad.core import MonographOperad


@dataclass
class MonographConfig:
    """Configuration for monograph generation."""
    title: str
    theme: str
    parts: int = 5
    iterations_per_part: int = 1  # Refinement iterations
    entropy_budget: float = 0.08  # Accursed Share for exploration
    output_dir: Path = field(default_factory=lambda: Path("generated/"))


@dataclass
class PartSpec:
    """Specification for one part of the monograph."""
    number: int
    title: str
    agent_type: str  # "math" | "science" | "philosophy" | "psychology" | "synthesis"
    initial_state: Any
    input_data: Any
    depth: int = 5


class MonographGenerator:
    """
    Main generator orchestrating multi-agent monograph creation.

    Uses the PolyAgent + Operad + Sheaf pattern (AD-006):
    - Layer 1 (PolyAgent): Five domain agents with state machines
    - Layer 2 (Operad): Composition grammar for combining outputs
    - Layer 3 (Sheaf): Coherence checking across parts
    """

    def __init__(self, config: MonographConfig):
        """Initialize generator with configuration."""
        self.config = config
        self.operad = MonographOperad()

        # Initialize polynomial agents
        self.agents = {
            "math": MathematicianPolynomial(),
            "science": ScientistPolynomial(),
            "philosophy": PhilosopherPolynomial(),
            "psychology": PsychologistPolynomial(),
            "synthesis": SynthesizerPolynomial(),
        }

        # Track generated content
        self.parts: list[str] = []
        self.metadata: dict[str, Any] = {}

    async def generate(self) -> str:
        """Generate complete monograph."""
        print(f"\n{'='*80}")
        print(f"GENERATING: {self.config.title}")
        print(f"Theme: {self.config.theme}")
        print(f"Parts: {self.config.parts}")
        print(f"Entropy Budget: {self.config.entropy_budget}")
        print(f"{'='*80}\n")

        # Generate title page
        monograph = self._generate_title_page()

        # Define part specifications
        part_specs = self._define_part_structure()

        # Generate each part
        for spec in part_specs:
            print(f"\n--- Generating Part {spec.number}: {spec.title} ---\n")
            part_content = await self._generate_part(spec)
            self.parts.append(part_content)
            monograph += part_content

        # Generate synthesis (Part V)
        print(f"\n--- Generating Final Synthesis ---\n")
        synthesis = await self._generate_synthesis()
        monograph += synthesis

        # Save to file
        output_path = self.config.output_dir / f"{self._slugify(self.config.title)}.md"
        output_path.parent.mkdir(parents=True, exist_ok=True)
        output_path.write_text(monograph)

        print(f"\n{'='*80}")
        print(f"✓ Monograph generated: {output_path}")
        print(f"  Total length: {len(monograph):,} characters")
        print(f"  Parts: {len(self.parts)}")
        print(f"{'='*80}\n")

        return monograph

    def _generate_title_page(self) -> str:
        """Generate title page and front matter."""
        return f"""# {self.config.title}

> *{self.config.theme}*

---

## Abstract

This monograph explores the fundamental question of process ontology across four domains - mathematics, science, philosophy, and psychology - before synthesizing them into a unified categorical framework. We argue that morphisms (transformations/processes) are ontologically prior to objects (substances/products), and that this insight resolves longstanding philosophical puzzles while providing a productive framework for understanding reality at all scales.

Through rigorous mathematical foundations (category theory, functors, natural transformations), empirical grounding (dissipative structures, self-organization, bifurcation theory), conceptual clarity (substance/process dialectic), and phenomenological depth (consciousness as temporal flow, predictive processing, developmental phase transitions), we demonstrate that the same three-layer pattern - PolyAgent (state machines), Operad (composition grammar), Sheaf (local-to-global coherence) - appears across all domains.

This is not analogy but structural isomorphism: The pattern that patterns reality is itself an instance of the pattern.

**Keywords**: Process ontology, category theory, dissipative structures, phenomenology, predictive processing, polynomial functors, operads, sheaves

---

## Contents

**Part I: The Categorical Foundation (Mathematics)**
- Morphisms as primary; objects as derived (Yoneda)
- Composition and category laws
- Natural transformations as meta-processes

**Part II: Thermodynamic Emergence (Science)**
- Dissipative structures and self-organization
- Bifurcations and phase transitions
- Turing patterns and reaction-diffusion

**Part III: Process Philosophy**
- Substance vs Process dialectic
- The morphism synthesis
- Critique and limits

**Part IV: Mind as Process (Psychology)**
- Phenomenology of temporal flow
- Predictive processing mechanisms
- Developmental phase transitions
- Neurophenomenological integration

**Part V: The Unified Vision (Synthesis)**
- Cross-domain isomorphisms
- The five axioms of process ontology
- Transcendence: What lies beyond

---

"""

    def _define_part_structure(self) -> list[PartSpec]:
        """Define the structure of all parts."""
        return [
            PartSpec(
                number=1,
                title="The Categorical Foundation",
                agent_type="math",
                initial_state=MathState.AXIOM,
                input_data=MathInput(
                    topic="Category Theory as Process Ontology",
                    depth=5,
                    formalism="hybrid",
                    context={
                        "philosophical_stance": "Process ontology: morphisms primary, objects derivative",
                        "target_audience": "Philosophers and mathematicians",
                        "connection_to_science": "→ Prepares for dissipative structures (Part II)",
                    }
                ),
                depth=5,
            ),
            PartSpec(
                number=2,
                title="Thermodynamic Emergence",
                agent_type="science",
                initial_state=ScienceState.OBSERVE,
                input_data=ScienceInput(
                    phenomenon="Dissipative Structures and Self-Organization",
                    domain="physics",
                    empirical_grounding="theoretical",
                    context={
                        "connection_to_math": "→ Links to category theory (local-to-global, sheaves)",
                        "philosophical_bridge": "→ Process ontology: pattern is becoming, not being",
                        "connection_to_psychology": "→ Analogous to cognitive development",
                    }
                ),
                depth=5,
            ),
            PartSpec(
                number=3,
                title="Process Philosophy",
                agent_type="philosophy",
                initial_state=PhilosophyState.QUESTION,
                input_data=PhilosophyInput(
                    question="What is the relationship between substance and process?",
                    tradition="process",
                    rigor="formal",
                    context={
                        "connection_to_math": "→ Category theory provides framework",
                        "mathematical_bridge": "→ Morphisms as unifying concept",
                        "bridge_to_psychology": "→ Connects to consciousness as process",
                    }
                ),
                depth=5,
            ),
            PartSpec(
                number=4,
                title="Mind as Process",
                agent_type="psychology",
                initial_state=PsychologyState.PHENOMENOLOGY,
                input_data=PsychologyInput(
                    phenomenon="Consciousness as Temporal Process",
                    approach="phenomenological",
                    level="subjective",
                    context={
                        "bridge_to_mechanism": "→ Prepares for predictive processing",
                        "bridge_to_development": "→ Sets up developmental transitions",
                        "bridge_to_integration": "→ Leads to multi-scale synthesis",
                    }
                ),
                depth=5,
            ),
        ]

    async def _generate_part(self, spec: PartSpec) -> str:
        """Generate one part of the monograph."""
        agent = self.agents[spec.agent_type]
        state = spec.initial_state

        part_content = f"""
---

# Part {spec.number}: {spec.title}

"""

        # Run agent through its states (full cycle)
        for iteration in range(4):  # Each agent has 4 states
            print(f"  State {iteration + 1}/4: {state.name if hasattr(state, 'name') else state}")

            # Transition
            state, output = await agent.transition(state, spec.input_data)

            # Add content
            part_content += output.content + "\n\n"

            # Optional: Add references
            if hasattr(output, 'references') and output.references:
                part_content += "### References\n\n"
                for ref in output.references[:5]:  # Limit to avoid redundancy
                    part_content += f"- {ref}\n"
                part_content += "\n"

        return part_content

    async def _generate_synthesis(self) -> str:
        """Generate final synthesis using synthesizer agent."""
        synthesizer = self.agents["synthesis"]
        state = SynthesisState.GATHER

        # Gather insights from all parts
        domain_insights = {
            "math": "Morphisms primary (Yoneda), composition laws, natural transformations",
            "science": "Dissipative structures, bifurcations, self-organization, entropy production",
            "philosophy": "Substance/process synthesis via morphisms, scale relativity, limits of framework",
            "psychology": "Consciousness as flow, predictive processing, developmental transitions, neurophenomenology",
        }

        input_data = SynthesisInput(
            domain_insights=domain_insights,
            target="Unified Process Ontology",
            depth=5,
            context={
                "transition_to_weave": "→ Identifies deep structural isomorphisms",
                "transition_to_unify": "→ Constructs five-axiom framework",
                "transition_to_transcend": "→ Acknowledges limits, points beyond",
                "final_reflection": "→ The end is also a beginning",
            }
        )

        synthesis_content = ""

        # Run through all synthesis states
        for iteration in range(4):
            print(f"  Synthesis state {iteration + 1}/4: {state.name}")

            state, output = await synthesizer.transition(state, input_data)
            synthesis_content += output.content + "\n\n"

        return synthesis_content

    @staticmethod
    def _slugify(title: str) -> str:
        """Convert title to filename slug."""
        return title.lower().replace(" ", "_").replace(":", "")


# Main execution
async def main():
    """Generate the monograph."""
    config = MonographConfig(
        title="Process Ontology: The Primacy of Transformation",
        theme="A categorical journey through mathematics, science, philosophy, and psychology",
        parts=5,
        iterations_per_part=1,
        entropy_budget=0.08,
    )

    generator = MonographGenerator(config)
    monograph = await generator.generate()

    # Print statistics
    word_count = len(monograph.split())
    print(f"\nStatistics:")
    print(f"  Characters: {len(monograph):,}")
    print(f"  Words: {word_count:,}")
    print(f"  Estimated pages (250 words/page): {word_count // 250}")


if __name__ == "__main__":
    asyncio.run(main())
