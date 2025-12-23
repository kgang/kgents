#!/usr/bin/env python
"""
Migrate membrane.db (SQLite) to Docker Postgres.

Usage:
    cd impl/claude
    uv run python scripts/migrate_membrane_to_postgres.py --dry-run
    uv run python scripts/migrate_membrane_to_postgres.py --execute

Prerequisites:
    1. Docker Postgres running: docker compose up -d
    2. Source membrane.db exists: ~/.local/share/kgents/membrane.db
    3. KGENTS_DATABASE_URL set to Postgres URL (or will use default)
    4. Alembic migrations applied to Postgres: uv run alembic upgrade head

Environment Variables:
    KGENTS_DATABASE_URL: PostgreSQL connection string

AGENTESE: time.trace.migrate.membrane
"""

from __future__ import annotations

import argparse
import asyncio
import os
import sqlite3
from pathlib import Path

# Tables to migrate (ordered by dependencies)
TABLES_TO_MIGRATE = [
    # Self-grow
    "self_grow_proposals",
    "self_grow_nursery",
    "self_grow_rollback_tokens",
    "self_grow_budget",
    # Brain
    "brain_crystals",
    "brain_crystal_tags",
    "brain_settings",
    # Town
    "town_citizens",
    "town_conversations",
    "town_conversation_turns",
    "town_citizen_relationships",
    # Gardener
    "garden_sessions",
    "garden_plots",
    "garden_ideas",
    "garden_idea_connections",
    # Gestalt
    "gestalt_topologies",
    "gestalt_code_blocks",
    "gestalt_code_links",
    "gestalt_topology_snapshots",
    # Atelier
    "atelier_workshops",
    "atelier_artisans",
    "atelier_exhibitions",
    "atelier_gallery_items",
    "atelier_artifact_contributions",
    # Coalition
    "coalition_coalitions",
    "coalition_members",
    "coalition_proposals",
    "coalition_proposal_votes",
    "coalition_outputs",
    # Park
    "park_hosts",
    "park_episodes",
    "park_host_memories",
    "park_interactions",
    "park_locations",
]


def get_sqlite_path() -> Path:
    """Get path to membrane.db."""
    xdg_data = os.environ.get("XDG_DATA_HOME")
    if xdg_data:
        data_dir = Path(xdg_data) / "kgents"
    else:
        data_dir = Path.home() / ".local" / "share" / "kgents"
    return data_dir / "membrane.db"


def get_postgres_url() -> str:
    """Get Postgres URL from environment."""
    url = os.environ.get("KGENTS_DATABASE_URL")
    if url and url.startswith("postgresql"):
        # Strip async driver for asyncpg
        return url.replace("postgresql+asyncpg://", "postgresql://", 1)

    url = os.environ.get("KGENTS_POSTGRES_URL")
    if url:
        return url

    # Default for local Docker development
    return "postgresql://kgents:kgents@localhost:5432/kgents"


def get_table_columns(conn: sqlite3.Connection, table: str) -> list[str]:
    """Get column names for a table."""
    cursor = conn.execute(f"PRAGMA table_info({table})")
    return [row[1] for row in cursor.fetchall()]


def count_rows(conn: sqlite3.Connection, table: str) -> int:
    """Count rows in a table."""
    cursor = conn.execute(f"SELECT COUNT(*) FROM {table}")
    return cursor.fetchone()[0]


async def migrate_table(
    sqlite_conn: sqlite3.Connection,
    pg_pool,
    table: str,
    dry_run: bool = True,
) -> tuple[int, int]:
    """
    Migrate a single table from SQLite to Postgres.

    Returns:
        (source_count, migrated_count)
    """
    import asyncpg

    # Get source data
    columns = get_table_columns(sqlite_conn, table)
    source_count = count_rows(sqlite_conn, table)

    if source_count == 0:
        print(f"  {table}: 0 rows (skipping)")
        return 0, 0

    cursor = sqlite_conn.execute(f"SELECT * FROM {table}")
    rows = cursor.fetchall()

    if dry_run:
        print(f"  {table}: {source_count} rows (dry run)")
        return source_count, 0

    # Build INSERT statement for Postgres
    placeholders = ", ".join([f"${i + 1}" for i in range(len(columns))])
    columns_str = ", ".join(columns)
    insert_sql = f"""
        INSERT INTO {table} ({columns_str})
        VALUES ({placeholders})
        ON CONFLICT DO NOTHING
    """

    # Insert rows
    migrated = 0
    async with pg_pool.acquire() as conn:
        for row in rows:
            try:
                await conn.execute(insert_sql, *row)
                migrated += 1
            except Exception as e:
                print(f"    Warning: Failed to insert row in {table}: {e}")

    print(f"  {table}: {migrated}/{source_count} rows migrated")
    return source_count, migrated


async def run_migration(dry_run: bool = True) -> None:
    """Run the full migration."""
    import asyncpg

    sqlite_path = get_sqlite_path()
    postgres_url = get_postgres_url()

    print("=" * 60)
    print("Membrane Database Migration: SQLite -> PostgreSQL")
    print("=" * 60)
    print()
    print(f"Source:      {sqlite_path}")
    print(f"Destination: {postgres_url.split('@')[1] if '@' in postgres_url else postgres_url}")
    print(f"Mode:        {'DRY RUN' if dry_run else 'EXECUTE'}")
    print()

    # Check source exists
    if not sqlite_path.exists():
        print(f"ERROR: Source database not found: {sqlite_path}")
        return

    # Connect to SQLite
    sqlite_conn = sqlite3.connect(sqlite_path)

    # Connect to Postgres
    try:
        pg_pool = await asyncpg.create_pool(postgres_url, min_size=1, max_size=5)
    except Exception as e:
        print(f"ERROR: Failed to connect to Postgres: {e}")
        sqlite_conn.close()
        return

    print("Migrating tables...")
    print()

    total_source = 0
    total_migrated = 0

    for table in TABLES_TO_MIGRATE:
        # Check if table exists in source
        cursor = sqlite_conn.execute(
            "SELECT name FROM sqlite_master WHERE type='table' AND name=?", (table,)
        )
        if not cursor.fetchone():
            continue

        source, migrated = await migrate_table(sqlite_conn, pg_pool, table, dry_run)
        total_source += source
        total_migrated += migrated

    print()
    print("=" * 60)
    print(f"Summary: {total_migrated}/{total_source} rows migrated")

    if dry_run:
        print()
        print("This was a DRY RUN. No data was actually migrated.")
        print("Run with --execute to perform the actual migration.")
    else:
        print()
        print("Migration complete!")
        print()
        print("Next steps:")
        print("  1. Verify with: kg brain status")
        print("  2. If successful, delete old SQLite:")
        print(f"     rm {sqlite_path}")

    print("=" * 60)

    # Cleanup
    await pg_pool.close()
    sqlite_conn.close()


def main():
    parser = argparse.ArgumentParser(description="Migrate membrane.db from SQLite to PostgreSQL")
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Show what would be migrated without making changes",
    )
    parser.add_argument(
        "--execute",
        action="store_true",
        help="Actually perform the migration",
    )

    args = parser.parse_args()

    if not args.dry_run and not args.execute:
        print("Please specify --dry-run or --execute")
        return

    asyncio.run(run_migration(dry_run=not args.execute))


if __name__ == "__main__":
    main()
