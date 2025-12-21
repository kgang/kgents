"""
WASM Sandbox Demo: Zero-trust agent execution in browser.

This demo shows how WASMProjector compiles an agent to run
sandboxed in the browser via Pyodide (Python in WASM).

Run:
    cd impl/claude
    uv run python demos/wasm_sandbox_demo.py
    # Opens demo.html in browser

Why this matters:
1. CHAOTIC reality agents need sandboxing before trust
2. Browser sandbox = battle-tested isolation
3. No filesystem, no network (unless opted in)
4. Same Halo, different projector → same semantics, different runtime
"""

import webbrowser
from pathlib import Path
from tempfile import gettempdir

from agents.a.halo import Capability
from agents.poly.types import Agent
from system.projector import WASMProjector


# A simple agent to demo
@Capability.Stateful(schema=dict)
@Capability.Observable(metrics=True)
class TextTransformerAgent(Agent[str, str]):
    """
    Transforms text in various ways.

    This agent runs COMPLETELY in the browser sandbox:
    - No server required after loading
    - No filesystem access
    - No network access
    - Pure Python via Pyodide WASM
    """

    @property
    def name(self) -> str:
        return "text-transformer"

    async def invoke(self, text: str) -> str:
        """Transform input text."""
        # Simple transformations
        lines = [
            f"Original: {text}",
            f"UPPERCASE: {text.upper()}",
            f"lowercase: {text.lower()}",
            f"Title Case: {text.title()}",
            f"Reversed: {text[::-1]}",
            f"Length: {len(text)} characters",
            f"Words: {len(text.split())} words",
        ]
        return "\n".join(lines)


def main() -> None:
    """Generate and open WASM sandbox demo."""
    print("🔧 Compiling agent to WASM sandbox...")

    # Compile to WASM bundle
    projector = WASMProjector()
    html = projector.compile(TextTransformerAgent)

    # Save to temp file
    output_path = Path(gettempdir()) / "kgents_wasm_demo.html"
    output_path.write_text(html)

    print(f"✅ Generated: {output_path}")
    print(f"📦 Bundle size: {len(html):,} bytes")
    print()
    print("Opening in browser...")
    print()
    print("=" * 60)
    print("TRY THIS: Enter any text and click 'Run Agent'")
    print("The agent runs ENTIRELY in your browser via WASM.")
    print("No server. No network. Pure sandboxed Python.")
    print("=" * 60)

    # Open in browser
    webbrowser.open(f"file://{output_path}")


if __name__ == "__main__":
    main()
