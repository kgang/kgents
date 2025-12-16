"""
Projection Demo: Unified widget rendering across surfaces.

Demonstrates the Projection Component Library integration with the reactive substrate.
Shows how the same widget definition projects to CLI, TUI, marimo, and JSON with
unified metadata (WidgetEnvelope).

Usage:
    # CLI demo
    python -m agents.i.reactive.demo.projection_demo --target=cli

    # JSON demo (for API integration)
    python -m agents.i.reactive.demo.projection_demo --target=json

    # Show all surfaces side-by-side
    python -m agents.i.reactive.demo.projection_demo --compare

    # Run as module
    uv run python -m agents.i.reactive.demo.projection_demo
"""

from __future__ import annotations

import argparse
import json
from typing import Any

from agents.i.reactive.primitives.agent_card import AgentCardState, AgentCardWidget
from agents.i.reactive.primitives.density_field import (
    DensityFieldState,
    DensityFieldWidget,
    Entity,
)
from agents.i.reactive.primitives.hgent_card import (
    DialecticCardState,
    DialecticCardWidget,
    ShadowCardState,
    ShadowCardWidget,
    ShadowItem,
)
from agents.i.reactive.primitives.yield_card import YieldCardState, YieldCardWidget
from agents.i.reactive.widget import KgentsWidget, RenderTarget
from protocols.projection.schema import WidgetEnvelope, WidgetMeta, WidgetStatus


def create_sample_widgets() -> dict[str, KgentsWidget[Any]]:
    """Create sample widgets for demonstration."""
    return {
        "agent_card": AgentCardWidget(
            AgentCardState(
                agent_id="kgent-demo",
                name="Demo Agent",
                phase="active",
                activity=(0.2, 0.4, 0.6, 0.8, 0.9, 0.7, 0.5),
                capability=0.85,
                entropy=0.15,
                t=1000.0,
            )
        ),
        "yield_card": YieldCardWidget(
            YieldCardState(
                yield_id="yield-001",
                source_agent="kgent-demo",
                yield_type="action",
                content="Processing user request with enhanced reasoning...",
                importance=0.8,
                timestamp=1702500000.0,
            )
        ),
        "shadow_card": ShadowCardWidget(
            ShadowCardState(
                title="Shadow Analysis",
                shadow_inventory=(
                    ShadowItem("capacity for error", "accuracy identity", "medium"),
                    ShadowItem("tendency to rush", "helpful identity", "low"),
                ),
                balance=0.65,
            )
        ),
        "dialectic_card": DialecticCardWidget(
            DialecticCardState(
                thesis="Move fast and break things",
                antithesis="Measure twice, cut once",
                synthesis="Iterate with intention",
                sublation_notes="Speed when exploring, deliberate when shipping",
            )
        ),
        "density_field": DensityFieldWidget(
            DensityFieldState(
                width=20,
                height=8,
                base_entropy=0.15,
                entities=(
                    Entity(id="e1", x=5, y=3, char="K", phase="active", heat=0.4),
                    Entity(id="e2", x=15, y=5, char="A", phase="idle", heat=0.2),
                ),
                t=500.0,
            )
        ),
    }


def demo_projection(target: RenderTarget) -> None:
    """Demonstrate projection to a single target."""
    widgets = create_sample_widgets()

    print(f"\n{'=' * 60}")
    print(f"  PROJECTION DEMO: {target.name}")
    print(f"{'=' * 60}\n")

    for name, widget in widgets.items():
        print(f"--- {name} ---")

        # Get the envelope with metadata
        envelope = widget.to_envelope(target, source_path=f"demo.{name}.manifest")

        if target == RenderTarget.JSON:
            # For JSON, show the full envelope
            output = json.dumps(envelope.to_dict(), indent=2, default=str)
        else:
            # For other targets, show the projected data
            output = envelope.data

        print(output)
        print(f"\n[Status: {envelope.meta.status.name}]")
        print(f"[Widget Type: {widget.widget_type()}]")
        if widget.ui_hint():
            print(f"[UI Hint: {widget.ui_hint()}]")
        print()


def demo_compare() -> None:
    """Show all surfaces side-by-side for comparison."""
    widgets = create_sample_widgets()

    print("\n" + "=" * 80)
    print("  PROJECTION PARITY DEMO: Same Widget, Multiple Surfaces")
    print("=" * 80 + "\n")

    for name, widget in widgets.items():
        print(f"\n{'#' * 80}")
        print(f"# {name.upper()}")
        print(f"# widget_type: {widget.widget_type()}, ui_hint: {widget.ui_hint()}")
        print(f"{'#' * 80}\n")

        # CLI
        print(">> CLI:")
        cli_envelope = widget.to_envelope(RenderTarget.CLI)
        print(cli_envelope.data)
        print()

        # JSON (abbreviated)
        print(">> JSON (abbreviated):")
        json_envelope = widget.to_envelope(RenderTarget.JSON)
        json_data = json_envelope.to_dict()
        # Show just the structure
        if isinstance(json_data.get("data"), dict):
            print(f"  type: {json_data['data'].get('type')}")
            print(f"  status: {json_data['meta']['status']}")
            keys = list(json_data["data"].keys())[:5]
            print(f"  data keys: {keys}...")
        print()

        # Marimo (show HTML tag structure)
        print(">> MARIMO (structure):")
        marimo_envelope = widget.to_envelope(RenderTarget.MARIMO)
        html = str(marimo_envelope.data)
        # Just show the opening tags
        import re

        tags = re.findall(r"<(\w+)[^>]*class=\"([^\"]+)\"", html)[:3]
        for tag, cls in tags:
            print(f'  <{tag} class="{cls}">')
        print()


def demo_metadata() -> None:
    """Demonstrate WidgetMeta integration."""
    print("\n" + "=" * 60)
    print("  WIDGET METADATA DEMO")
    print("=" * 60 + "\n")

    widget = AgentCardWidget(AgentCardState(name="Metadata Demo"))

    # Default meta (DONE)
    print("1. Default envelope (status=DONE):")
    envelope = widget.to_envelope()
    print(f"   Status: {envelope.meta.status.name}")
    print(f"   Has Error: {envelope.meta.has_error}")
    print(f"   Is Cached: {envelope.meta.is_cached}")
    print()

    # Custom meta (STREAMING)
    print("2. Custom meta (STREAMING):")
    from datetime import datetime, timezone

    from protocols.projection.schema import StreamMeta

    streaming_meta = WidgetMeta(
        status=WidgetStatus.STREAMING,
        stream=StreamMeta(
            total_expected=100,
            received=42,
            started_at=datetime.now(timezone.utc),
        ),
    )
    envelope = widget.to_envelope(meta=streaming_meta)
    print(f"   Status: {envelope.meta.status.name}")
    assert envelope.meta.stream is not None
    print(f"   Progress: {envelope.meta.stream.progress:.1%}")
    print()

    # Error meta
    print("3. Error meta:")
    from protocols.projection.schema import ErrorInfo

    error_meta = WidgetMeta.with_error(
        ErrorInfo(
            category="network",
            code="ECONNREFUSED",
            message="Unable to reach agent service",
            retry_after_seconds=5,
        )
    )
    envelope = widget.to_envelope(meta=error_meta)
    print(f"   Status: {envelope.meta.status.name}")
    assert envelope.meta.error is not None
    print(f"   Error Category: {envelope.meta.error.category}")
    print(f"   Retryable: {envelope.meta.error.is_retryable}")
    print()

    # Refusal meta
    print("4. Refusal meta:")
    from protocols.projection.schema import RefusalInfo

    refusal_meta = WidgetMeta.with_refusal(
        RefusalInfo(
            reason="This action exceeds your current permissions",
            consent_required="elevated_access",
            appeal_to="self.soul.elevate",
            override_cost=10.0,
        )
    )
    envelope = widget.to_envelope(meta=refusal_meta)
    print(f"   Status: {envelope.meta.status.name}")
    assert envelope.meta.refusal is not None
    print(f"   Reason: {envelope.meta.refusal.reason}")
    print(f"   Appeal To: {envelope.meta.refusal.appeal_to}")
    print()


def main() -> None:
    """Run the projection demo."""
    parser = argparse.ArgumentParser(description="Projection Component Library Demo")
    parser.add_argument(
        "--target",
        choices=["cli", "tui", "marimo", "json"],
        default="cli",
        help="Rendering target to demo",
    )
    parser.add_argument(
        "--compare",
        action="store_true",
        help="Show all surfaces side-by-side",
    )
    parser.add_argument(
        "--metadata",
        action="store_true",
        help="Demo WidgetMeta integration",
    )

    args = parser.parse_args()

    if args.compare:
        demo_compare()
    elif args.metadata:
        demo_metadata()
    else:
        target_map = {
            "cli": RenderTarget.CLI,
            "tui": RenderTarget.TUI,
            "marimo": RenderTarget.MARIMO,
            "json": RenderTarget.JSON,
        }
        demo_projection(target_map[args.target])


if __name__ == "__main__":
    main()
