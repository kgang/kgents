"""
Dawn Cockpit TUI: Quarter-screen terminal interface.

"The cockpit doesn't fly the plane. The pilot flies the plane.
The cockpit just makes it easy."

This module provides Kent's daily operating surface as a Textual TUI:
- Two-pane layout: Focus (left) + Snippets (right)
- Keyboard-first navigation (arrow keys, Enter, Tab)
- Copy-to-clipboard as the killer feature
- Garden status bar (what grew overnight)

Key Features:
    - Quarter-screen: Dawn never takes over; lives alongside work
    - Copy on Enter: Selected snippet → clipboard instantly
    - Focus hygiene: Stale items visually marked
    - Witness integration: Copy actions recorded

Architecture:
    Dawn : (Coffee x Portal x Witness x Brain) -> TUI

See: spec/protocols/dawn-cockpit.md

Teaching:
    gotcha: Quarter-screen (80x24) is the target. The TUI should feel
            like a persistent overlay, not a full-screen takeover.
            (Evidence: spec/protocols/dawn-cockpit.md § Visual Design)

    gotcha: Reserve space > conditional render. Always render containers,
            toggle content visibility. Prevents layout shift.
            (Evidence: meta.md → Layout Sheaf)
"""

from .add_focus_modal import AddFocusModal
from .app import DawnCockpit, run_dawn_tui
from .focus_pane import FocusPane
from .garden_view import GardenView
from .snippet_pane import SnippetPane

__all__ = [
    "AddFocusModal",
    "DawnCockpit",
    "FocusPane",
    "SnippetPane",
    "GardenView",
    "run_dawn_tui",
]
