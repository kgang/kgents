"""
AGENTESE Integration for Gardener-Logos.

Provides the GardenerLogosNode for concept.gardener.* paths
with full tending calculus integration.

Paths:
- concept.gardener.manifest → Garden overview (ASCII/JSON)
- concept.gardener.tend → Apply tending gesture
- concept.gardener.season.manifest → Current season info
- concept.gardener.season.transition → Change season
- concept.gardener.plot.list → List all plots
- concept.gardener.plot.create → Create new plot
- concept.gardener.plot.focus → Set active plot
- concept.gardener.plot.manifest → View specific plot
"""

from .context import (
    GardenerLogosNode,
    GardenerLogosResolver,
    create_gardener_logos_node,
    create_gardener_logos_resolver,
)

__all__ = [
    "GardenerLogosNode",
    "GardenerLogosResolver",
    "create_gardener_logos_node",
    "create_gardener_logos_resolver",
]
