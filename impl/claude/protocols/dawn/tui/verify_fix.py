#!/usr/bin/env python3
"""
Verification script for Dawn TUI Enter key fix.

This script demonstrates that:
1. Tab switches panes correctly
2. j/k navigate within panes
3. Enter activates/copies without creating black bar
4. Copy confirmation shows in Garden view

Run: uv run python protocols/dawn/tui/verify_fix.py
"""

from protocols.dawn.focus import FocusManager
from protocols.dawn.snippets import SnippetLibrary
from protocols.dawn.tui.app import DawnCockpit


def main():
    """Run the Dawn Cockpit TUI with test data."""
    # Create managers with test data
    fm = FocusManager()
    fm.add("plans/test-plan.md", label="Test Focus Item")
    fm.add("self.test.verify", label="AGENTESE Test")

    sl = SnippetLibrary()
    sl.load_defaults()

    # Create and run app
    app = DawnCockpit(fm, sl)

    print("Dawn TUI Verification")
    print("=" * 60)
    print()
    print("TESTING INSTRUCTIONS:")
    print("1. Press Tab to switch between Focus and Snippets panes")
    print("   - Border should change from cyan to green")
    print("2. Press j/k or ↑↓ to navigate items")
    print("   - Selection indicator (▶) should move")
    print("3. Press Enter in Snippets pane")
    print("   - Should copy snippet to clipboard")
    print("   - Garden should show: '📋 Copied: [label]'")
    print("   - NO BLACK BAR should appear")
    print("4. Press Enter in Focus pane")
    print("   - Should activate the focus item")
    print("   - NO BLACK BAR should appear")
    print("5. Press q to quit")
    print()
    print("=" * 60)
    print()

    try:
        app.run()
        print("\n✅ Test completed successfully!")
        print("If you saw NO black bar when pressing Enter, the fix works!")
        return 0
    except Exception as e:
        print(f"\n❌ Test failed: {e}")
        return 1


if __name__ == "__main__":
    exit(main())
