"""
Example 04: AGENTESE Observer
=============================

DEMONSTRATES: Same path invoked with different observers yields different results.

AGENTESE is the protocol for agent interaction. A fundamental principle is:
    "There is no view from nowhere. All operations require an observer."

The same entity (e.g., "world.house") manifests differently to different observers:
- An architect sees blueprints
- A poet sees metaphors
- A guest sees only the facade

This is observer-dependent semantics - the core of AGENTESE.

KEY CONCEPTS:
- Observer: Lightweight context (archetype, capabilities)
- Affordances: What actions are available to an observer
- Manifest: How an entity appears to an observer

RUN: cd impl/claude && uv run python ../../examples/04-agentese-observer/main.py
"""

import sys
from pathlib import Path

# Add impl/claude to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent.parent / "impl" / "claude"))

from protocols.agentese.node import AgentMeta, Observer


class HouseNode:
    """
    A simple AGENTESE node that demonstrates observer-dependent behavior.

    This simulates what a real LogosNode does: it responds differently
    based on WHO is observing.
    """

    def __init__(self) -> None:
        self.handle = "world.house"

    def affordances(self, observer: AgentMeta) -> list[str]:
        """
        Return available actions based on observer archetype.

        Different observers can do different things.
        """
        base = ["manifest", "witness"]

        archetype_affordances = {
            "architect": ["blueprint", "modify", "analyze"],
            "poet": ["metaphor", "dream", "feel"],
            "developer": ["inspect", "debug", "test"],
            "guest": [],  # Guests can only manifest and witness
        }

        extra = archetype_affordances.get(observer.archetype, [])
        return base + extra

    def manifest(self, observer: Observer) -> dict[str, str]:
        """
        Manifest the house according to observer archetype.

        The same house appears differently to different observers.
        """
        archetype = observer.archetype

        if archetype == "architect":
            return {
                "type": "blueprint",
                "content": "Load-bearing walls at 3m intervals. "
                "Foundation: reinforced concrete. "
                "Roof pitch: 30 degrees.",
                "view": "structural",
            }
        elif archetype == "poet":
            return {
                "type": "metaphor",
                "content": "A shelter against the storm of existence. "
                "Walls that hold memories like amber holds time. "
                "Windows that frame dreams.",
                "view": "lyrical",
            }
        elif archetype == "developer":
            return {
                "type": "schema",
                "content": "House(id=1, rooms=[Room(...)], "
                "state='constructed', tests_passing=True)",
                "view": "technical",
            }
        else:  # guest
            return {
                "type": "facade",
                "content": "A pleasant two-story home with a red roof.",
                "view": "surface",
            }


def main() -> None:
    print("AGENTESE Observer: Same Entity, Different Views")
    print("=" * 55)

    # Create the house node
    house = HouseNode()

    # Create different observers
    observers = [
        Observer(archetype="architect", capabilities=frozenset({"design", "modify"})),
        Observer(archetype="poet", capabilities=frozenset({"dream", "create"})),
        Observer(archetype="developer", capabilities=frozenset({"debug", "test"})),
        Observer.guest(),  # Anonymous guest
    ]

    print(f"\nEntity: {house.handle}")
    print("-" * 55)

    for observer in observers:
        # Check affordances
        meta = AgentMeta(name=observer.archetype, archetype=observer.archetype)
        affordances = house.affordances(meta)

        # Get manifest
        manifest = house.manifest(observer)

        print(f"\nObserver: {observer.archetype}")
        print(f"  Affordances: {affordances}")
        print(f"  Manifest type: {manifest['type']}")
        print(f"  Content: {manifest['content'][:60]}...")
        print(f"  View: {manifest['view']}")

    # === Demonstrate capability-based filtering ===

    print("\n" + "=" * 55)
    print("Capability-Based Affordances")
    print("=" * 55)

    # Observer with special capability
    admin = Observer(
        archetype="admin",
        capabilities=frozenset({"modify", "delete", "grant"}),
    )

    print(f"\nAdmin observer capabilities: {admin.capabilities}")
    print("Admins can access system-level operations via capabilities,")
    print("even if their archetype doesn't normally grant them.")

    # === Key insight ===

    print("\n" + "=" * 55)
    print("KEY INSIGHT")
    print("=" * 55)
    print("""
The same path ("world.house.manifest") returns:
- Blueprint for architects (structural view)
- Metaphor for poets (lyrical view)
- Schema for developers (technical view)
- Facade for guests (surface view)

This is observer-dependent semantics.
There is no "true" view of the house - only views FOR observers.
""")


if __name__ == "__main__":
    main()
