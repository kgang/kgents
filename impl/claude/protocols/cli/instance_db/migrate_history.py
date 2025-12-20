#!/usr/bin/env python3
"""
Migration utility: ~/.kgents/history.db -> membrane.db

This script migrates session data from the deprecated per-project
history.db to the unified membrane.db.

Usage:
    python -m protocols.cli.instance_db.migrate_history

    # Or with custom paths:
    python -m protocols.cli.instance_db.migrate_history --source ~/.kgents/history.db

MIGRATION NOTE (2025-12-20):
- Old: Per-project ~/.kgents/history.db (deprecated)
- New: Global ~/.local/share/kgents/membrane.db (cli_sessions table)
"""

from __future__ import annotations

import argparse
import asyncio
import json
import sqlite3
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path


@dataclass
class MigrationResult:
    """Result of migration operation."""

    sessions_migrated: int
    events_migrated: int
    agents_migrated: int
    artifacts_migrated: int
    errors: list[str]
    source_path: Path
    target_path: Path

    @property
    def success(self) -> bool:
        return len(self.errors) == 0

    def __str__(self) -> str:
        status = "SUCCESS" if self.success else "FAILED"
        return f"""
Migration {status}
================
Source: {self.source_path}
Target: {self.target_path}

Records migrated:
  Sessions:  {self.sessions_migrated}
  Events:    {self.events_migrated}
  Agents:    {self.agents_migrated}
  Artifacts: {self.artifacts_migrated}
{"" if self.success else f"Errors: {len(self.errors)}"}
"""


def get_default_paths() -> tuple[Path, Path]:
    """Get default source and target paths."""
    import os

    home = Path.home()

    # Source: deprecated history.db
    source = home / ".kgents" / "history.db"

    # Target: XDG-compliant membrane.db
    xdg_data = os.environ.get("XDG_DATA_HOME", str(home / ".local" / "share"))
    target = Path(xdg_data) / "kgents" / "membrane.db"

    return source, target


async def migrate_history_db(
    source_path: Path | None = None,
    target_path: Path | None = None,
    dry_run: bool = False,
) -> MigrationResult:
    """
    Migrate data from history.db to membrane.db.

    Args:
        source_path: Path to source history.db (default: ~/.kgents/history.db)
        target_path: Path to target membrane.db (default: XDG data dir)
        dry_run: If True, don't actually write to target

    Returns:
        MigrationResult with counts and any errors
    """
    from .storage import StorageProvider, XDGPaths

    default_source, default_target = get_default_paths()
    source = source_path or default_source
    target = target_path or default_target

    errors: list[str] = []
    sessions_migrated = 0
    events_migrated = 0
    agents_migrated = 0
    artifacts_migrated = 0

    # Check source exists
    if not source.exists():
        errors.append(f"Source database not found: {source}")
        return MigrationResult(
            sessions_migrated=0,
            events_migrated=0,
            agents_migrated=0,
            artifacts_migrated=0,
            errors=errors,
            source_path=source,
            target_path=target,
        )

    # Read source data
    try:
        source_conn = sqlite3.connect(str(source))
        source_conn.row_factory = sqlite3.Row

        # Check if tables exist
        cursor = source_conn.execute(
            "SELECT name FROM sqlite_master WHERE type='table'"
        )
        tables = {row[0] for row in cursor.fetchall()}

        sessions = []
        events = []
        agents = []
        artifacts = []

        if "sessions" in tables:
            cursor = source_conn.execute("SELECT * FROM sessions")
            sessions = [dict(row) for row in cursor.fetchall()]

        if "events" in tables:
            cursor = source_conn.execute("SELECT * FROM events")
            events = [dict(row) for row in cursor.fetchall()]

        if "agents" in tables:
            cursor = source_conn.execute("SELECT * FROM agents")
            agents = [dict(row) for row in cursor.fetchall()]

        if "artifacts" in tables:
            cursor = source_conn.execute("SELECT * FROM artifacts")
            artifacts = [dict(row) for row in cursor.fetchall()]

        source_conn.close()

    except Exception as e:
        errors.append(f"Failed to read source: {e}")
        return MigrationResult(
            sessions_migrated=0,
            events_migrated=0,
            agents_migrated=0,
            artifacts_migrated=0,
            errors=errors,
            source_path=source,
            target_path=target,
        )

    if dry_run:
        print("DRY RUN - Would migrate:")
        print(f"  {len(sessions)} sessions")
        print(f"  {len(events)} events")
        print(f"  {len(agents)} agents")
        print(f"  {len(artifacts)} artifacts")
        return MigrationResult(
            sessions_migrated=len(sessions),
            events_migrated=len(events),
            agents_migrated=len(agents),
            artifacts_migrated=len(artifacts),
            errors=[],
            source_path=source,
            target_path=target,
        )

    # Get target storage
    try:
        paths = XDGPaths.resolve()
        storage = await StorageProvider.from_config(paths=paths)
        await storage.run_migrations()  # Ensure schema exists
    except Exception as e:
        errors.append(f"Failed to connect to target: {e}")
        return MigrationResult(
            sessions_migrated=0,
            events_migrated=0,
            agents_migrated=0,
            artifacts_migrated=0,
            errors=errors,
            source_path=source,
            target_path=target,
        )

    # Migrate sessions
    for session in sessions:
        try:
            # Map old schema to new
            await storage.relational.execute(
                """
                INSERT OR IGNORE INTO cli_sessions
                (id, name, session_type, state, started_at, ended_at,
                 flow_name, flow_path, budget_level, tokens_used, metadata)
                VALUES (:id, :name, :session_type, :state, :started_at, :ended_at,
                        :flow_name, :flow_path, :budget_level, :tokens_used, :metadata)
                """,
                {
                    "id": session["id"],
                    "name": session.get("name", "Migrated Session"),
                    "session_type": "interactive",  # default
                    "state": session.get("state", "completed"),
                    "started_at": session.get("started_at"),
                    "ended_at": session.get("ended_at"),
                    "flow_name": session.get("flow_name"),
                    "flow_path": session.get("flow_path"),
                    "budget_level": session.get("budget_level", "medium"),
                    "tokens_used": session.get("tokens_used", 0),
                    "metadata": session.get("metadata", "{}"),
                },
            )
            sessions_migrated += 1
        except Exception as e:
            errors.append(f"Failed to migrate session {session.get('id')}: {e}")

    # Migrate events
    for event in events:
        try:
            await storage.relational.execute(
                """
                INSERT OR IGNORE INTO cli_session_events
                (id, session_id, timestamp, event_type, source, message, data)
                VALUES (:id, :session_id, :timestamp, :event_type, :source, :message, :data)
                """,
                {
                    "id": event["id"],
                    "session_id": event["session_id"],
                    "timestamp": event.get("timestamp"),
                    "event_type": event.get("event_type", "info"),
                    "source": event.get("source", "migration"),
                    "message": event.get("message", ""),
                    "data": event.get("data", "{}"),
                },
            )
            events_migrated += 1
        except Exception as e:
            errors.append(f"Failed to migrate event {event.get('id')}: {e}")

    # Migrate agents
    for agent in agents:
        try:
            await storage.relational.execute(
                """
                INSERT OR IGNORE INTO cli_session_agents
                (id, session_id, name, genus, status, started_at, completed_at, error, metadata)
                VALUES (:id, :session_id, :name, :genus, :status, :started_at, :completed_at, :error, :metadata)
                """,
                {
                    "id": agent["id"],
                    "session_id": agent["session_id"],
                    "name": agent.get("name", "unknown"),
                    "genus": agent.get("genus", "unknown"),
                    "status": agent.get("status", "completed"),
                    "started_at": agent.get("started_at"),
                    "completed_at": agent.get("completed_at"),
                    "error": agent.get("error"),
                    "metadata": "{}",
                },
            )
            agents_migrated += 1
        except Exception as e:
            errors.append(f"Failed to migrate agent {agent.get('id')}: {e}")

    # Migrate artifacts
    for artifact in artifacts:
        try:
            await storage.relational.execute(
                """
                INSERT OR IGNORE INTO cli_session_artifacts
                (id, session_id, name, path, artifact_type, created_at, updated_at, size_bytes, content_preview, metadata)
                VALUES (:id, :session_id, :name, :path, :artifact_type, :created_at, :updated_at, :size_bytes, :content_preview, :metadata)
                """,
                {
                    "id": artifact["id"],
                    "session_id": artifact["session_id"],
                    "name": artifact.get("name", "unknown"),
                    "path": artifact.get("path"),
                    "artifact_type": artifact.get("artifact_type", "unknown"),
                    "created_at": artifact.get("created_at"),
                    "updated_at": artifact.get("updated_at"),
                    "size_bytes": artifact.get("size_bytes", 0),
                    "content_preview": artifact.get("content_preview"),
                    "metadata": "{}",
                },
            )
            artifacts_migrated += 1
        except Exception as e:
            errors.append(f"Failed to migrate artifact {artifact.get('id')}: {e}")

    await storage.close()

    return MigrationResult(
        sessions_migrated=sessions_migrated,
        events_migrated=events_migrated,
        agents_migrated=agents_migrated,
        artifacts_migrated=artifacts_migrated,
        errors=errors,
        source_path=source,
        target_path=target,
    )


def main() -> None:
    """CLI entry point."""
    parser = argparse.ArgumentParser(
        description="Migrate ~/.kgents/history.db to membrane.db"
    )
    parser.add_argument(
        "--source",
        type=Path,
        help="Source history.db path (default: ~/.kgents/history.db)",
    )
    parser.add_argument(
        "--target",
        type=Path,
        help="Target membrane.db path (default: XDG data dir)",
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Show what would be migrated without writing",
    )

    args = parser.parse_args()

    result = asyncio.run(
        migrate_history_db(
            source_path=args.source,
            target_path=args.target,
            dry_run=args.dry_run,
        )
    )

    print(result)

    if not result.success:
        for error in result.errors:
            print(f"ERROR: {error}")
        exit(1)


if __name__ == "__main__":
    main()
