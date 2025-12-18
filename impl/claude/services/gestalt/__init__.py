"""
Gestalt Crown Jewel: Living Garden Where Code Breathes.

The Gestalt provides a holistic view of the codebase as a living organism,
with topology visualization and governance monitoring.

AGENTESE Paths (via @node("world.codebase")):
- world.codebase.manifest  - Full architecture graph
- world.codebase.health    - Health metrics summary
- world.codebase.topology  - 3D visualization data
- world.codebase.drift     - Drift violations
- world.codebase.module    - Module details
- world.codebase.scan      - Force rescan

Design DNA:
- Organic: Code as living system
- Holistic: Whole greater than parts
- Observable: Health metrics visible

See: docs/skills/metaphysical-fullstack.md
"""

# Import node to register with @node decorator
from .node import GestaltNode
from .persistence import (
    CodeBlockView,
    CodeLinkView,
    GestaltPersistence,
    GestaltStatus,
    TopologyView,
)

__all__ = [
    "GestaltPersistence",
    "TopologyView",
    "CodeBlockView",
    "CodeLinkView",
    "GestaltStatus",
    # Node
    "GestaltNode",
]
