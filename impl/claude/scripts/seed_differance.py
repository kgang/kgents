#!/usr/bin/env python3
"""
Seed the Differance Engine with representative traces.

Populates the trace store with example operations from each Crown Jewel,
demonstrating causal chains and ghost alternatives (roads not taken).

Usage:
    # Ensure Postgres is running
    docker compose up -d postgres

    # Set connection URL and run
    export KGENTS_POSTGRES_URL=postgresql://kgents:kgents@localhost:5432/kgents
    cd impl/claude && uv run python scripts/seed_differance.py

After seeding:
    # View via AGENTESE
    uv run kg time.differance.recent
    uv run kg time.differance.why --output_id seed_forge_003

    # Or via API
    curl http://localhost:8000/agentese/time/differance/recent -X POST -d '{"limit": 10}'
"""

from __future__ import annotations

import asyncio
import os
from datetime import datetime, timedelta, timezone

# Enable asyncpg (Postgres backend)
os.environ.setdefault(
    "KGENTS_POSTGRES_URL",
    "postgresql://kgents:kgents@localhost:5432/kgents",
)


async def main() -> None:
    """Seed differance store with representative traces."""
    from agents.d.backends.postgres import ASYNCPG_AVAILABLE, PostgresBackend
    from agents.differance import DifferanceStore, WiringTrace
    from agents.differance.trace import Alternative

    if not ASYNCPG_AVAILABLE:
        print("Error: asyncpg not installed. Install with: pip install asyncpg")
        return

    postgres_url = os.environ.get("KGENTS_POSTGRES_URL")
    if not postgres_url:
        print("Error: KGENTS_POSTGRES_URL not set")
        return

    print("Connecting to Postgres...")

    # Create Postgres backend
    backend = PostgresBackend(url=postgres_url, namespace="differance")

    try:
        # Initialize schema
        await backend._ensure_schema()
        print("Schema initialized")

        # Create store
        store = DifferanceStore(backend=backend)

        # Define representative traces
        now = datetime.now(timezone.utc)

        traces = [
            # === Brain Operations ===
            WiringTrace.create(
                operation="capture",
                inputs=("Meeting notes: Q4 planning with stakeholders",),
                output="crystal_meeting_001",
                context="[brain] Captured meeting notes to memory crystal",
                alternatives=[
                    Alternative("summarize", ("before storing",), "Could compress first", True),
                    Alternative("categorize", ("auto-tag",), "Could auto-categorize", True),
                ],
                trace_id="seed_brain_001",
            ),
            WiringTrace(
                trace_id="seed_brain_002",
                timestamp=now - timedelta(hours=1, minutes=30),
                operation="recall",
                inputs=("Q4 planning",),
                output=["crystal_meeting_001"],
                context="[brain] Recalled crystals matching query",
                alternatives=(),
                positions_before={},
                positions_after={},
                parent_trace_id="seed_brain_001",
            ),
            # === Gardener Operations ===
            WiringTrace.create(
                operation="plant",
                inputs=("kgents-core", "Plot A"),
                output="plant_kgents_001",
                context="[gardener] Planted new project seed",
                alternatives=[
                    Alternative("graft", ("existing_plant",), "Could graft to existing", True),
                ],
                trace_id="seed_garden_001",
            ),
            WiringTrace(
                trace_id="seed_garden_002",
                timestamp=now - timedelta(minutes=45),
                operation="tend",
                inputs=("plant_kgents_001", "water"),
                output="tended",
                context="[gardener] Watered project plant",
                alternatives=[
                    Alternative("prune", ("plant_kgents_001",), "Could prune instead", True),
                    Alternative("fertilize", ("plant_kgents_001",), "Could add resources", False),
                ],
                positions_before={"plant_kgents_001": frozenset(["planted"])},
                positions_after={"plant_kgents_001": frozenset(["growing"])},
                parent_trace_id="seed_garden_001",
            ),
            # === Forge Operations (causal chain) ===
            WiringTrace.create(
                operation="ignite",
                inputs=("Build a REST API for user management",),
                output="intent_api_001",
                context="[forge] Ignited intent from natural language",
                alternatives=(),
                trace_id="seed_forge_001",
            ),
            WiringTrace(
                trace_id="seed_forge_002",
                timestamp=now - timedelta(minutes=25),
                operation="shape",
                inputs=("intent_api_001", "REST", "FastAPI"),
                output="design_api_001",
                context="[forge] Shaped intent into concrete design",
                alternatives=[
                    Alternative("shape", ("GraphQL",), "Could use GraphQL instead", True),
                    Alternative("shape", ("gRPC",), "Could use gRPC for performance", True),
                ],
                positions_before={"intent_api_001": frozenset(["sparked"])},
                positions_after={"design_api_001": frozenset(["designed"])},
                parent_trace_id="seed_forge_001",
            ),
            WiringTrace(
                trace_id="seed_forge_003",
                timestamp=now - timedelta(minutes=15),
                operation="temper",
                inputs=("design_api_001",),
                output="artifact_api_001",
                context="[forge] Tempered design into working code",
                alternatives=(),
                positions_before={"design_api_001": frozenset(["designed"])},
                positions_after={"artifact_api_001": frozenset(["forged"])},
                parent_trace_id="seed_forge_002",
            ),
            # === Town Operations ===
            WiringTrace.create(
                operation="dialogue",
                inputs=("citizen_scholar_01", "citizen_maker_01"),
                output="coalition_001",
                context="[town] Scholars and Makers formed coalition",
                alternatives=[
                    Alternative("debate", ("opposing_views",), "Could debate instead", False),
                ],
                trace_id="seed_town_001",
            ),
        ]

        # Seed all traces
        print(f"\nSeeding {len(traces)} traces...")
        for trace in traces:
            await store.append(trace)
            jewel = trace.context.split("]")[0][1:] if trace.context.startswith("[") else "unknown"
            ghost_count = len(trace.alternatives)
            ghost_str = f" ({ghost_count} ghosts)" if ghost_count > 0 else ""
            print(f"  + {trace.trace_id}: [{jewel}] {trace.operation}{ghost_str}")

        # Verify
        count = await store.count()
        print(f"\nTotal traces in store: {count}")

        # Show causal chain example
        print("\nCausal chain for seed_forge_003 (REST API artifact):")
        chain = await store.causal_chain("seed_forge_003")
        for t in chain:
            ghost_count = len(t.alternatives)
            ghost_str = f" [{ghost_count} ghosts]" if ghost_count > 0 else ""
            print(
                f"  -> {t.trace_id}: {t.operation}({', '.join(str(i)[:20] for i in t.inputs[:2])}){ghost_str}"
            )

        print("\nSeed complete!")
        print("\nExplore via:")
        print("  uv run kg time.differance.recent")
        print("  uv run kg time.differance.why --output_id seed_forge_003")

    finally:
        await backend.close()


if __name__ == "__main__":
    asyncio.run(main())
