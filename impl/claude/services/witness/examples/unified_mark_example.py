"""
Example demonstrating the unified Mark type with domain support.

Run this to verify the implementation:
    uv run python services/witness/examples/unified_mark_example.py
"""

from datetime import datetime, timezone

from services.witness import (
    EvidenceTier,
    Mark,
    Proof,
    Response,
    Stimulus,
    Trace,
    UmweltSnapshot,
)


def main() -> None:
    print("=" * 80)
    print("Unified Mark Type - Example")
    print("=" * 80)

    # Create marks for different domains
    print("\n1. Creating marks across domains...")

    nav_mark = Mark(
        origin="navigator",
        domain="navigation",
        stimulus=Stimulus(kind="route", content="Navigate to /chat"),
        response=Response(kind="navigation", content="Navigated to /chat"),
        timestamp=datetime.now(timezone.utc),
    )
    print(f"   ✓ Navigation mark: {nav_mark.id}")

    portal_mark = Mark(
        origin="context_perception",
        domain="portal",
        stimulus=Stimulus(kind="portal", content="Expand imports"),
        response=Response(kind="exploration", content="Expanded to depth 2"),
        timestamp=datetime.now(timezone.utc),
    )
    print(f"   ✓ Portal mark: {portal_mark.id}")

    chat_mark = Mark(
        origin="chat_session",
        domain="chat",
        stimulus=Stimulus(kind="prompt", content="Hello"),
        response=Response(kind="text", content="Hi there!"),
        timestamp=datetime.now(timezone.utc),
    )
    print(f"   ✓ Chat mark: {chat_mark.id}")

    edit_mark = Mark(
        origin="editor",
        domain="edit",
        stimulus=Stimulus(kind="kblock", content="Edit K-Block abc123"),
        response=Response(kind="mutation", content="K-Block updated"),
        timestamp=datetime.now(timezone.utc),
    )
    print(f"   ✓ Edit mark: {edit_mark.id}")

    # Build a trace
    print("\n2. Building trace...")
    trace = Trace[Mark]()
    trace = trace.add(nav_mark)
    trace = trace.add(portal_mark)
    trace = trace.add(chat_mark)
    trace = trace.add(edit_mark)
    print(f"   ✓ Trace contains {len(trace)} marks")

    # Filter by domain
    print("\n3. Filtering by domain...")
    chat_trace = trace.filter_by_domain("chat")
    print(f"   ✓ Chat marks: {len(chat_trace)}")
    assert len(chat_trace) == 1
    assert chat_trace.latest.domain == "chat"

    portal_trace = trace.filter_by_domain("portal")
    print(f"   ✓ Portal marks: {len(portal_trace)}")
    assert len(portal_trace) == 1

    # Filter by origin
    print("\n4. Filtering by origin...")
    navigator_trace = trace.filter_by_origin("navigator")
    print(f"   ✓ Navigator marks: {len(navigator_trace)}")
    assert len(navigator_trace) == 1

    # Custom filtering
    print("\n5. Custom filtering...")
    nav_or_chat = trace.filter(lambda m: m.domain in ("navigation", "chat"))
    print(f"   ✓ Navigation or Chat marks: {len(nav_or_chat)}")
    assert len(nav_or_chat) == 2

    # Serialization
    print("\n6. Testing serialization...")
    data = chat_mark.to_dict()
    assert "domain" in data
    assert data["domain"] == "chat"
    print(f"   ✓ Serialized domain: {data['domain']}")

    restored = Mark.from_dict(data)
    assert restored.domain == "chat"
    print(f"   ✓ Deserialized domain: {restored.domain}")

    # Immutability
    print("\n7. Testing immutability...")
    mark_with_proof = chat_mark.with_proof(
        Proof(
            data="User asked question",
            warrant="Questions require responses",
            claim="Response was helpful",
            tier=EvidenceTier.EMPIRICAL,
        )
    )
    assert mark_with_proof.domain == "chat"
    assert mark_with_proof.proof is not None
    print("   ✓ Mark.with_proof() preserves domain")

    # Trace operations
    print("\n8. Testing trace operations...")
    sliced = trace.slice(-2)  # Last 2 marks
    print(f"   ✓ Slice last 2: {len(sliced)} marks")
    assert len(sliced) == 2

    latest = trace.latest
    assert latest is not None
    print(f"   ✓ Latest mark domain: {latest.domain}")

    earliest = trace.earliest
    assert earliest is not None
    print(f"   ✓ Earliest mark domain: {earliest.domain}")

    # Merging
    print("\n9. Testing trace merging...")
    other_mark = Mark(
        origin="system",
        domain="system",
        stimulus=Stimulus(kind="system", content="System event"),
        response=Response(kind="log", content="Event logged"),
        timestamp=datetime.now(timezone.utc),  # Must be timezone-aware
    )
    other_trace = Trace[Mark]().add(other_mark)
    merged = trace.merge(other_trace)
    print(f"   ✓ Merged trace contains {len(merged)} marks")
    assert len(merged) == len(trace) + 1

    print("\n" + "=" * 80)
    print("✅ All examples completed successfully!")
    print("=" * 80)


if __name__ == "__main__":
    main()
