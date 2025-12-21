#!/usr/bin/env python3
"""
Demo: MarimoProjector — Interactive Agent Exploration

This demo shows how the MarimoProjector compiles agent Halos into
marimo notebook cells for interactive exploration.

Run:
    cd impl/claude
    uv run python demos/marimo_projector_demo.py

The demo will:
1. Define several example agents with different capabilities
2. Compile each to a marimo cell
3. Save the generated cells to files you can open in marimo
"""

from pathlib import Path

# Add parent to path for imports
import sys

sys.path.insert(0, str(Path(__file__).parent.parent))

from agents.a.halo import Capability
from agents.poly.types import Agent
from system.projector import MarimoProjector, MarimoArtifact


# =============================================================================
# Example Agents with Different Capabilities
# =============================================================================


class TextTransformer(Agent[str, str]):
    """A simple text transformation agent."""

    @property
    def name(self) -> str:
        return "text-transformer"

    async def invoke(self, text: str) -> str:
        """Transform text to uppercase."""
        return text.upper()


@Capability.Stateful(schema=dict)
class CountingAgent(Agent[str, str]):
    """An agent that counts invocations."""

    def __init__(self):
        self._count = 0

    @property
    def name(self) -> str:
        return "counting-agent"

    async def invoke(self, text: str) -> str:
        """Echo text with invocation count."""
        self._count += 1
        return f"[{self._count}] {text}"


@Capability.Observable(metrics=True)
class MetricsAgent(Agent[str, str]):
    """An agent that exposes performance metrics."""

    @property
    def name(self) -> str:
        return "metrics-agent"

    async def invoke(self, text: str) -> str:
        """Process text with observable metrics."""
        # Simulate some processing
        words = text.split()
        return f"Processed {len(words)} words: {text.title()}"


@Capability.Soulful(persona="wise-owl", mode="friendly")
class WiseOwlAgent(Agent[str, str]):
    """An agent with a wise owl persona."""

    @property
    def name(self) -> str:
        return "wise-owl"

    async def invoke(self, question: str) -> str:
        """Answer questions with owl wisdom."""
        return (
            f"🦉 Hoo hoo! You ask about '{question}'... The wise owl says: seek and you shall find!"
        )


@Capability.Stateful(schema=dict)
@Capability.Observable(metrics=True)
@Capability.Soulful(persona="kent", mode="thoughtful")
class FullStackAgent(Agent[str, str]):
    """An agent with all capabilities for comprehensive exploration."""

    @property
    def name(self) -> str:
        return "full-stack-explorer"

    async def invoke(self, query: str) -> str:
        """Process query with full capabilities."""
        return f"✨ Processing: {query}\n→ Result: {query[::-1]} (reversed)"


# =============================================================================
# Demo Runner
# =============================================================================


def main():
    print("=" * 60)
    print("🎭 MarimoProjector Demo — Interactive Agent Exploration")
    print("=" * 60)
    print()

    # Create output directory
    output_dir = Path(__file__).parent / "marimo_cells"
    output_dir.mkdir(exist_ok=True)

    # Define agents to demo
    agents = [
        ("Plain Agent", TextTransformer),
        ("Stateful Agent", CountingAgent),
        ("Observable Agent", MetricsAgent),
        ("Soulful Agent", WiseOwlAgent),
        ("Full-Stack Agent", FullStackAgent),
    ]

    projector = MarimoProjector()

    for label, agent_cls in agents:
        print(f"📦 Compiling: {label} ({agent_cls.__name__})")

        # Compile to marimo cell
        cell = projector.compile(agent_cls)

        # Get artifact for metadata
        artifact = projector.compile_artifact(agent_cls)

        # Save to file
        filename = f"{artifact.agent_name}_cell.py"
        filepath = output_dir / filename
        filepath.write_text(cell)

        # Print summary
        print(f"   → Agent name: {artifact.agent_name}")
        print(f"   → Uses state: {artifact.uses_state}")
        print(f"   → Uses metrics: {artifact.uses_metrics}")
        print(f"   → Uses streaming: {artifact.uses_streaming}")
        print(f"   → Saved to: {filepath.relative_to(Path.cwd())}")
        print()

    print("=" * 60)
    print("✅ Demo complete!")
    print()
    print("To explore an agent in marimo:")
    print(f"  1. cd {output_dir.relative_to(Path.cwd())}")
    print("  2. marimo edit <filename>.py")
    print()
    print("Or view a generated cell directly:")
    print("-" * 60)

    # Show one example cell
    example_cell = projector.compile(TextTransformer)
    print(example_cell[:1500] + "\n..." if len(example_cell) > 1500 else example_cell)
    print("-" * 60)


if __name__ == "__main__":
    main()
