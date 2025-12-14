"""Demo applications for the reactive substrate.

Wave 10: TUI Dashboard (tui_dashboard.py)
Wave 11: Marimo Agents (marimo_agents.py)
Wave 12: Unified App (unified_app.py, unified_notebook.py) - Same widgets, any target

Usage:
    # CLI/TUI/JSON modes
    python -m agents.i.reactive.demo.unified_app --target=cli

    # Notebook mode
    marimo run impl/claude/agents/i/reactive/demo/unified_notebook.py
"""

from agents.i.reactive.demo.unified_app import (
    UnifiedDashboard,
    benchmark_renders,
    capture_comparison,
    create_sample_dashboard,
)

__all__ = [
    "UnifiedDashboard",
    "create_sample_dashboard",
    "benchmark_renders",
    "capture_comparison",
]
