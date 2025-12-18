"""
Chat Commands: Session management CLI interface.

Provides commands for managing persistent chat sessions:
- kg chat sessions     # List saved chat sessions
- kg chat resume <id>  # Resume a saved session
- kg chat search <q>   # Search session content

These complement the interactive chat available via:
- kg soul chat         # Chat with K-gent
- kg town chat <name>  # Chat with citizen
"""

from __future__ import annotations

SESSION_COMMANDS = {"sessions", "list", "resume", "search", "delete"}


def print_help() -> None:
    """Print help for chat command group."""
    print(__doc__)
    print()
    print("COMMANDS:")
    print("  sessions [--node PATH]  List saved chat sessions")
    print("  resume <name|id>        Resume a saved session")
    print("  search <query>          Search session content")
    print("  delete <id>             Delete a saved session")
    print()
    print("OPTIONS:")
    print("  --node PATH      Filter by AGENTESE path (e.g., self.soul)")
    print("  --limit N        Maximum sessions to list (default 10)")
    print("  --json           Output as JSON")
    print("  --help, -h       Show this help")
    print()
    print("EXAMPLES:")
    print("  kg chat sessions                    # List all sessions")
    print("  kg chat sessions --node self.soul   # List soul sessions only")
    print("  kg chat resume planning-session     # Resume by name")
    print("  kg chat search 'authentication'     # Search for keyword")
    print()
    print("NOTE: To start a new chat, use:")
    print("  kg soul chat           # Interactive K-gent chat")
    print("  kg town chat <citizen> # Interactive citizen chat")


__all__ = [
    "SESSION_COMMANDS",
    "print_help",
]
