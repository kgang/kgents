"""
Demo: Chat Persistence in Action

This script demonstrates that chat sessions survive "server restarts"
by saving a session, simulating a restart, and loading it back.

Run with: uv run python services/chat/demo_persistence.py
"""

import asyncio
from pathlib import Path

from services.chat import ChatSession
from services.chat.persistence import ChatPersistence


async def demo_persistence():
    """Demonstrate persistent chat sessions."""
    print("=" * 80)
    print("CHAT PERSISTENCE DEMO: Sessions Survive Restarts")
    print("=" * 80)

    # Part 1: Create and save session
    print("\n📝 Part 1: Creating session and adding turns...")

    persistence = await ChatPersistence.create()

    session = ChatSession.create(project_id="demo-project", branch_name="main")
    print(f"   Created session: {session.id}")

    # Add some conversation turns
    session.add_turn(
        user_message="Hello! Can you help me understand D-gent persistence?",
        assistant_response="Of course! D-gent provides a unified storage abstraction with four stores: Relational, Vector, Blob, and Telemetry.",
    )

    session.add_turn(
        user_message="That's interesting! What makes it special?",
        assistant_response="It's XDG-compliant, supports multiple backends (SQLite, PostgreSQL, S3), and provides a consistent interface across all storage types.",
    )

    session.add_turn(
        user_message="Show me how to persist a chat session.",
        assistant_response="Sure! Use ChatPersistence.save_session(session) to save, and ChatPersistence.load_session(session_id) to load. Sessions survive server restarts!",
    )

    print(f"   Added {session.turn_count} conversation turns")

    # Save to database
    await persistence.save_session(session)
    print(f"   ✅ Saved session to database")

    session_id = session.id

    # Close connection (simulate server shutdown)
    await persistence.close()
    print("   🔌 Closed persistence connection (simulating server shutdown)")

    # Part 2: Simulate restart and load
    print("\n🔄 Part 2: Simulating server restart...")

    # Create new persistence instance (simulates restart)
    persistence = await ChatPersistence.create()
    print("   🚀 New persistence instance created (server 'restarted')")

    # Load session from database
    loaded_session = await persistence.load_session(session_id)
    print(f"   ✅ Loaded session: {loaded_session.id if loaded_session else 'FAILED'}")

    if loaded_session:
        print(f"   📊 Session stats:")
        print(f"      - Project: {loaded_session.project_id}")
        print(f"      - Branch: {loaded_session.node.branch_name}")
        print(f"      - Turns: {loaded_session.turn_count}")
        print(f"      - Created: {loaded_session.node.created_at.isoformat()}")

        print(f"\n   💬 Conversation history:")
        for i, turn in enumerate(loaded_session.turns, 1):
            print(f"\n      Turn {i}:")
            print(f"      User: {turn.user_message}")
            print(f"      Assistant: {turn.assistant_response}")

    # Part 3: Demonstrate other features
    print("\n🎯 Part 3: Additional features...")

    # List all sessions
    all_sessions = await persistence.list_sessions()
    print(f"   📋 Total sessions in database: {len(all_sessions)}")

    # Save a crystal
    if loaded_session:
        await persistence.save_crystal(
            session_id=loaded_session.id,
            title="D-gent Persistence Tutorial",
            summary="User learned about D-gent persistence and ChatPersistence API",
            key_decisions=[
                "Use ChatPersistence for chat storage",
                "Sessions survive server restarts",
                "XDG-compliant storage locations",
            ],
            artifacts=["persistence_demo.py"],
        )
        print(f"   💎 Crystallized session summary")

        # Load crystal
        crystal = await persistence.load_crystal(loaded_session.id)
        if crystal:
            print(f"   ✨ Crystal title: {crystal['title']}")
            print(f"   ✨ Key decisions: {len(crystal['key_decisions'])}")

    # Cleanup
    await persistence.close()

    print("\n" + "=" * 80)
    print("✅ DEMO COMPLETE: Sessions are persistent!")
    print("=" * 80)
    print(f"\nDatabase location: ~/.local/share/kgents/membrane.db")
    print(f"To inspect: sqlite3 ~/.local/share/kgents/membrane.db")
    print(f"            SELECT * FROM chat_sessions;")
    print("=" * 80)


if __name__ == "__main__":
    asyncio.run(demo_persistence())
