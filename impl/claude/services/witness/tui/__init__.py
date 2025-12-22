"""
Witness TUI: Crystal Navigator Dashboard.

A proper Textual TUI for navigating the crystal hierarchy with
vim-style navigation, level filtering, and copy-to-clipboard.

ZenPortal Patterns Applied:
- Pattern 4: Vim Navigation (j/k)
- Pattern 6: Elastic Width Truncation
- Pattern 7: Status Glyphs (▪/▫)
- Pattern 8: Notification Toast
- Pattern 12: Context-Aware Hint Bar
- Pattern 14: Human-Friendly Age ("3m", "1h", "2d")
- Pattern 17: Active Pane Indicator
- Pattern 18: SelectablePane Base

See: docs/skills/zenportal-patterns.md
See: spec/protocols/witness-crystallization.md
"""

from .app import WitnessDashApp, run_witness_tui

__all__ = [
    "WitnessDashApp",
    "run_witness_tui",
]
