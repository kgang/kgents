"""Demo applications for the reactive substrate.

Wave 10: TUI Dashboard (tui_dashboard.py)
Wave 11: Marimo Agents (marimo_agents.py)
Wave 12: Unified App (unified_app.py, unified_notebook.py) - Same widgets, any target
Wave 13: Projection Demo (projection_demo.py) - Projection Component Library integration

Usage:
    # CLI/TUI/JSON modes
    python -m agents.i.reactive.demo.unified_app --target=cli

    # Projection demo
    python -m agents.i.reactive.demo.projection_demo --compare

    # Notebook mode
    marimo run impl/claude/agents/i/reactive/demo/unified_notebook.py
"""

from agents.i.reactive.demo.projection_demo import (
    create_sample_widgets,
    demo_compare,
    demo_metadata,
    demo_projection,
)
from agents.i.reactive.demo.unified_app import (
    UnifiedDashboard,
    benchmark_renders,
    capture_comparison,
    create_sample_dashboard,
)

__all__ = [
    # Unified app
    "UnifiedDashboard",
    "create_sample_dashboard",
    "benchmark_renders",
    "capture_comparison",
    # Projection demo
    "create_sample_widgets",
    "demo_projection",
    "demo_compare",
    "demo_metadata",
]
