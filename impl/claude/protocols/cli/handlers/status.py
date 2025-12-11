"""
Status Handler: Cortex health at a glance.

DevEx V4 Phase 1 - Foundation Layer.

Usage:
    kgents status          # Compact one-liner
    kgents status --full   # Full ASCII dashboard
    kgents status --json   # Machine-readable JSON

Example output:
    [CORTEX] OK HEALTHY | L:45ms R:12ms | H:45/100 | S:0.3 | Dreams:12
"""

from __future__ import annotations

import json
import sys
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from protocols.cli.hollow import get_lifecycle_state


def cmd_status(args: list[str]) -> int:
    """
    Display cortex health status.

    Shows the Bicameral Engine's current state via CortexDashboard.
    Requires bootstrap to be complete for full functionality.
    """
    # Parse args
    full_mode = "--full" in args
    json_mode = "--json" in args
    help_mode = "--help" in args or "-h" in args

    if help_mode:
        print(__doc__)
        return 0

    # Get lifecycle state (may be None if bootstrap failed)
    from protocols.cli.hollow import get_lifecycle_state

    state = get_lifecycle_state()

    if state is None:
        # DB-less mode: show minimal status
        print("[CORTEX] ? DB-LESS | No persistence available")
        print("  Run 'kgents init' to initialize workspace.")
        return 0

    # Try to get observer and dashboard
    try:
        observer = _get_or_create_observer(state)
        dashboard = _get_or_create_dashboard(observer)

        if json_mode:
            print(dashboard.to_json())
        elif full_mode:
            print(dashboard.render_full())
        else:
            print(dashboard.render_compact())

        return 0

    except ImportError as e:
        print(f"[CORTEX] ! DEGRADED | Missing component: {e}")
        return 1
    except Exception as e:
        print(f"[CORTEX] X ERROR | {e}")
        return 1


def _get_or_create_observer(state):
    """
    Get or create a CortexObserver from lifecycle state.

    The observer pulls metrics from:
    - Bicameral Memory (if available)
    - Synapse (if available)
    - Hippocampus (if available)
    - Dreamer (if available)
    """
    from agents.o.cortex_observer import CortexObserver, create_cortex_observer

    # Check if observer already exists on state
    if hasattr(state, "cortex_observer") and state.cortex_observer is not None:
        return state.cortex_observer

    # Create minimal observer if components not available
    # This handles graceful degradation
    return create_cortex_observer(
        bicameral=getattr(state, "bicameral", None),
        synapse=getattr(state, "synapse", None),
        hippocampus=getattr(state, "hippocampus", None),
        dreamer=getattr(state, "dreamer", None),
    )


def _get_or_create_dashboard(observer):
    """Create CortexDashboard from observer."""
    from agents.w.cortex_dashboard import CortexDashboard, create_cortex_dashboard

    return create_cortex_dashboard(observer=observer)
