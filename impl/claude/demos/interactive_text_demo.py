"""
Interactive Text × Servo Demo.

Demonstrates the bridge between Interactive Text's MeaningTokens
and Servo's SceneGraph rendering.

Usage:
    uv run python demos/interactive_text_demo.py

This script:
1. Parses a sample markdown document
2. Converts it to a SceneGraph
3. Prints the resulting structure

The SceneGraph can then be rendered by ServoSceneRenderer.tsx
in the React frontend.
"""

import asyncio
import json
from pathlib import Path

from protocols.agentese.projection.scene import LayoutMode
from protocols.agentese.projection.tokens_to_scene import (
    MeaningTokenKind,
    markdown_to_scene_graph,
)
from services.interactive_text.parser import parse_markdown

SAMPLE_MARKDOWN = """\
# Interactive Text Demo

This document demonstrates the unified projection surface.

## AGENTESE Paths

Check `self.brain.capture` for memory operations.
Navigate to `world.town.citizen` to see agent simulation.

## Tasks

- [x] Create tokens_to_scene_graph bridge
- [x] Add MeaningTokenRenderer component
- [ ] Wire up AGENTESE navigation
- [ ] Add hover state display

## Code Example

```python
# Example agent composition
pipeline = AgentA >> AgentB >> AgentC
result = await pipeline.invoke(input)
```

## References

See [P1] (Tasteful) and [R2.1] for design rationale.

![Diagram](docs/diagram.png)
"""


async def main() -> None:
    """Run the demo."""
    print("=" * 60)
    print("Interactive Text × Servo Bridge Demo")
    print("=" * 60)
    print()

    # Step 1: Parse markdown
    print("Step 1: Parsing markdown...")
    doc = parse_markdown(SAMPLE_MARKDOWN)
    print(f"  Found {doc.token_count} tokens in {len(doc.spans)} spans")
    print()

    # Show token summary
    print("Token Types Found:")
    token_types: dict[str, int] = {}
    for span in doc.tokens:
        token_type = span.token_type or "unknown"
        token_types[token_type] = token_types.get(token_type, 0) + 1

    for ttype, count in sorted(token_types.items()):
        print(f"  - {ttype}: {count}")
    print()

    # Step 2: Convert to SceneGraph
    print("Step 2: Converting to SceneGraph...")
    scene = await markdown_to_scene_graph(
        SAMPLE_MARKDOWN,
        layout_mode=LayoutMode.COMFORTABLE,
    )
    print(f"  Created SceneGraph with {len(scene.nodes)} nodes")
    print(f"  Layout: {scene.layout.direction}, mode={scene.layout.mode.name}")
    print()

    # Step 3: Show node breakdown
    print("Step 3: Node Breakdown by MeaningTokenKind:")
    kind_counts: dict[str, int] = {}
    for node in scene.nodes:
        kind = node.metadata.get("meaning_token_kind", "PLAIN_TEXT")
        kind_counts[kind] = kind_counts.get(kind, 0) + 1

    for kind, count in sorted(kind_counts.items()):
        print(f"  - {kind}: {count}")
    print()

    # Step 4: Show example node details
    print("Step 4: Example Node (first AGENTESE path):")
    for node in scene.nodes:
        if node.metadata.get("meaning_token_kind") == MeaningTokenKind.AGENTESE_PORTAL.value:
            print(f"  ID: {node.id}")
            print(f"  Kind: {node.kind.name}")
            print(f"  Label: {node.label}")
            print(f"  Style: breathing={node.style.breathing}, fg={node.style.foreground}")
            print(f"  Interactions: {len(node.interactions)}")
            for interaction in node.interactions[:3]:
                print(f"    - {interaction.kind}: {interaction.action}")

            # Show content structure
            if isinstance(node.content, dict):
                print("  Content:")
                print(f"    token_type: {node.content.get('token_type')}")
                print(f"    token_data: {node.content.get('token_data')}")
            break
    print()

    # Step 5: Serialize for frontend
    print("Step 5: Serialized for Frontend (first 3 nodes):")
    scene_dict = scene.to_dict()
    for i, node_dict in enumerate(scene_dict["nodes"][:3]):
        print(f"  Node {i + 1}:")
        print(f"    kind: {node_dict['kind']}")
        print(f"    label: {node_dict['label'][:40]}...")
        print(f"    metadata.meaning_token_kind: {node_dict['metadata'].get('meaning_token_kind')}")
    print()

    print("=" * 60)
    print("Demo complete! The SceneGraph can now be rendered by")
    print("ServoSceneRenderer.tsx in the React frontend.")
    print("=" * 60)


if __name__ == "__main__":
    asyncio.run(main())
