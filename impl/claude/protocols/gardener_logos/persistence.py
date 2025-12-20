"""
GardenStore: SQLite Persistence for Gardener-Logos.

Stores garden state, plots, and gestures across sessions.
Enables the garden to persist through Claude Code session boundaries.

AGENTESE: concept.gardener.* persistence

Key Design:
- Gardens persist as JSON in SQLite with indexed metadata
- Plots stored per-garden with optional plan/crown jewel links
- Gestures form the audit trail (momentum trace)
- Default garden auto-created and auto-loaded

Phase 3 of Gardener-Logos Enactment Plan.
See: plans/gardener-logos-enactment.md
"""

from __future__ import annotations

import json
import sqlite3
from contextlib import contextmanager
from dataclasses import dataclass, field
from datetime import datetime
from pathlib import Path
from typing import Any, Iterator

from opentelemetry import trace

from .garden import GardenMetrics, GardenSeason, GardenState
from .plots import PlotState
from .tending import TendingGesture, TendingVerb

# =============================================================================
# OTEL Telemetry
# =============================================================================

_tracer: trace.Tracer | None = None


def _get_store_tracer() -> trace.Tracer:
    """Get the GardenStore tracer, creating if needed."""
    global _tracer
    if _tracer is None:
        _tracer = trace.get_tracer("kgents.gardener.garden_persistence", "0.1.0")
    return _tracer


# =============================================================================
# Schema
# =============================================================================

GARDEN_SCHEMA = """
-- Gardens table: the unified garden state
CREATE TABLE IF NOT EXISTS gardens (
    id TEXT PRIMARY KEY,
    name TEXT NOT NULL,
    season TEXT NOT NULL DEFAULT 'DORMANT',
    season_since TEXT NOT NULL,
    active_plot TEXT,
    session_id TEXT,
    prompt_count INTEGER DEFAULT 0,
    prompt_types_json TEXT DEFAULT '{}',
    memory_crystals_json TEXT DEFAULT '[]',
    entropy_spent REAL DEFAULT 0.0,
    entropy_budget REAL DEFAULT 1.0,
    created_at TEXT NOT NULL,
    updated_at TEXT NOT NULL,
    last_tended TEXT NOT NULL,
    is_default INTEGER DEFAULT 0
);

CREATE INDEX IF NOT EXISTS idx_gardens_default ON gardens(is_default);
CREATE INDEX IF NOT EXISTS idx_gardens_updated ON gardens(updated_at DESC);

-- Plots table: named focus regions
CREATE TABLE IF NOT EXISTS garden_plots (
    id TEXT PRIMARY KEY,
    garden_id TEXT NOT NULL REFERENCES gardens(id) ON DELETE CASCADE,
    name TEXT NOT NULL,
    path TEXT NOT NULL,
    description TEXT DEFAULT '',
    plan_path TEXT,
    crown_jewel TEXT,
    progress REAL DEFAULT 0.0,
    rigidity REAL DEFAULT 0.5,
    season_override TEXT,
    prompts_json TEXT DEFAULT '[]',
    tags_json TEXT DEFAULT '[]',
    metadata_json TEXT DEFAULT '{}',
    created_at TEXT NOT NULL,
    last_tended TEXT NOT NULL,
    UNIQUE(garden_id, name)
);

CREATE INDEX IF NOT EXISTS idx_plots_garden ON garden_plots(garden_id);
CREATE INDEX IF NOT EXISTS idx_plots_crown_jewel ON garden_plots(crown_jewel);
CREATE INDEX IF NOT EXISTS idx_plots_plan ON garden_plots(plan_path);

-- Gestures table: tending history (momentum trace)
CREATE TABLE IF NOT EXISTS garden_gestures (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    garden_id TEXT NOT NULL REFERENCES gardens(id) ON DELETE CASCADE,
    verb TEXT NOT NULL,
    target TEXT NOT NULL,
    tone REAL NOT NULL,
    reasoning TEXT,
    entropy_cost REAL NOT NULL,
    observer TEXT DEFAULT 'default',
    session_id TEXT,
    result_summary TEXT,
    timestamp TEXT NOT NULL
);

CREATE INDEX IF NOT EXISTS idx_gestures_garden ON garden_gestures(garden_id);
CREATE INDEX IF NOT EXISTS idx_gestures_timestamp ON garden_gestures(timestamp DESC);
CREATE INDEX IF NOT EXISTS idx_gestures_verb ON garden_gestures(verb);

-- Singleton for default garden
CREATE TABLE IF NOT EXISTS garden_default (
    id INTEGER PRIMARY KEY CHECK (id = 1),
    garden_id TEXT REFERENCES gardens(id),
    updated_at TEXT NOT NULL
);

INSERT OR IGNORE INTO garden_default (id, garden_id, updated_at)
VALUES (1, NULL, datetime('now'));
"""


# =============================================================================
# StoredGesture (for persistence)
# =============================================================================


@dataclass(frozen=True)
class StoredGesture:
    """A gesture stored in the database."""

    id: int | None
    garden_id: str
    verb: TendingVerb
    target: str
    tone: float
    reasoning: str
    entropy_cost: float
    observer: str
    session_id: str | None
    result_summary: str
    timestamp: datetime

    def to_tending_gesture(self) -> TendingGesture:
        """Convert to TendingGesture."""
        return TendingGesture(
            verb=self.verb,
            target=self.target,
            tone=self.tone,
            reasoning=self.reasoning,
            entropy_cost=self.entropy_cost,
            timestamp=self.timestamp,
            observer=self.observer,
            session_id=self.session_id,
            result_summary=self.result_summary,
        )

    @classmethod
    def from_row(cls, row: sqlite3.Row | dict[str, Any]) -> "StoredGesture":
        """Create from database row."""
        if isinstance(row, sqlite3.Row):
            row = dict(row)

        return cls(
            id=row.get("id"),
            garden_id=row["garden_id"],
            verb=TendingVerb[row["verb"]],
            target=row["target"],
            tone=row["tone"],
            reasoning=row.get("reasoning", ""),
            entropy_cost=row["entropy_cost"],
            observer=row.get("observer", "default"),
            session_id=row.get("session_id"),
            result_summary=row.get("result_summary", ""),
            timestamp=datetime.fromisoformat(row["timestamp"]),
        )


# =============================================================================
# GardenStore
# =============================================================================


@dataclass
class GardenStore:
    """
    SQLite persistence for GardenState.

    Thread-safe via connection-per-operation pattern.
    Uses WAL mode for concurrent reads.

    Usage:
        store = GardenStore(db_path)
        await store.init()

        # Get or create default garden
        garden = await store.get_default()

        # Save after modification
        await store.save(garden)

        # List all gardens
        gardens = await store.list_gardens(limit=10)
    """

    db_path: Path
    _initialized: bool = field(default=False, init=False)

    def __post_init__(self) -> None:
        """Ensure db_path is a Path."""
        if isinstance(self.db_path, str):
            self.db_path = Path(self.db_path)

    @contextmanager
    def _connection(self) -> Iterator[sqlite3.Connection]:
        """Get a database connection with row factory."""
        conn = sqlite3.connect(str(self.db_path), timeout=30.0)
        conn.row_factory = sqlite3.Row
        conn.execute("PRAGMA journal_mode=WAL")
        conn.execute("PRAGMA foreign_keys=ON")
        try:
            yield conn
            conn.commit()
        except Exception:
            conn.rollback()
            raise
        finally:
            conn.close()

    async def init(self) -> None:
        """Initialize the database schema."""
        tracer = _get_store_tracer()
        with tracer.start_as_current_span("garden_store.init") as span:
            # Ensure directory exists
            self.db_path.parent.mkdir(parents=True, exist_ok=True)

            with self._connection() as conn:
                conn.executescript(GARDEN_SCHEMA)

            self._initialized = True
            span.set_attribute("db.path", str(self.db_path))

    async def save(self, garden: GardenState) -> None:
        """
        Save garden state to database.

        This is an upsert operation - creates or updates.
        Also saves all plots and recent gestures.
        """
        tracer = _get_store_tracer()
        with tracer.start_as_current_span("garden_store.save") as span:
            span.set_attribute("garden.id", garden.garden_id)
            span.set_attribute("garden.name", garden.name)

            now = datetime.now()

            with self._connection() as conn:
                # Upsert garden
                conn.execute(
                    """
                    INSERT INTO gardens
                    (id, name, season, season_since, active_plot, session_id,
                     prompt_count, prompt_types_json, memory_crystals_json,
                     entropy_spent, entropy_budget, created_at, updated_at, last_tended, is_default)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                    ON CONFLICT(id) DO UPDATE SET
                        name = excluded.name,
                        season = excluded.season,
                        season_since = excluded.season_since,
                        active_plot = excluded.active_plot,
                        session_id = excluded.session_id,
                        prompt_count = excluded.prompt_count,
                        prompt_types_json = excluded.prompt_types_json,
                        memory_crystals_json = excluded.memory_crystals_json,
                        entropy_spent = excluded.entropy_spent,
                        entropy_budget = excluded.entropy_budget,
                        updated_at = excluded.updated_at,
                        last_tended = excluded.last_tended
                    """,
                    (
                        garden.garden_id,
                        garden.name,
                        garden.season.name,
                        garden.season_since.isoformat(),
                        garden.active_plot,
                        garden.session_id,
                        garden.prompt_count,
                        json.dumps(garden.prompt_types),
                        json.dumps(garden.memory_crystals),
                        garden.metrics.entropy_spent,
                        garden.metrics.entropy_budget,
                        garden.created_at.isoformat(),
                        now.isoformat(),
                        garden.last_tended.isoformat(),
                        0,  # is_default - managed separately
                    ),
                )

                # Save plots
                for plot_name, plot in garden.plots.items():
                    await self._save_plot(conn, garden.garden_id, plot)

                span.set_attribute("plots.count", len(garden.plots))

    async def _save_plot(
        self,
        conn: sqlite3.Connection,
        garden_id: str,
        plot: PlotState,
    ) -> None:
        """Save a plot to the database."""
        import uuid

        plot_id = f"{garden_id}:{plot.name}"

        conn.execute(
            """
            INSERT INTO garden_plots
            (id, garden_id, name, path, description, plan_path, crown_jewel,
             progress, rigidity, season_override, prompts_json, tags_json,
             metadata_json, created_at, last_tended)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            ON CONFLICT(garden_id, name) DO UPDATE SET
                path = excluded.path,
                description = excluded.description,
                plan_path = excluded.plan_path,
                crown_jewel = excluded.crown_jewel,
                progress = excluded.progress,
                rigidity = excluded.rigidity,
                season_override = excluded.season_override,
                prompts_json = excluded.prompts_json,
                tags_json = excluded.tags_json,
                metadata_json = excluded.metadata_json,
                last_tended = excluded.last_tended
            """,
            (
                plot_id,
                garden_id,
                plot.name,
                plot.path,
                plot.description,
                plot.plan_path,
                plot.crown_jewel,
                plot.progress,
                plot.rigidity,
                plot.season_override.name if plot.season_override else None,
                json.dumps(plot.prompts),
                json.dumps(plot.tags),
                json.dumps(plot.metadata),
                plot.created_at.isoformat(),
                plot.last_tended.isoformat(),
            ),
        )

    async def save_gesture(
        self,
        garden_id: str,
        gesture: TendingGesture,
    ) -> int:
        """
        Save a gesture to the database.

        Returns the gesture ID.
        """
        tracer = _get_store_tracer()
        with tracer.start_as_current_span("garden_store.save_gesture") as span:
            span.set_attribute("garden.id", garden_id)
            span.set_attribute("gesture.verb", gesture.verb.name)

            with self._connection() as conn:
                cursor = conn.execute(
                    """
                    INSERT INTO garden_gestures
                    (garden_id, verb, target, tone, reasoning, entropy_cost,
                     observer, session_id, result_summary, timestamp)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                    """,
                    (
                        garden_id,
                        gesture.verb.name,
                        gesture.target,
                        gesture.tone,
                        gesture.reasoning,
                        gesture.entropy_cost,
                        gesture.observer,
                        gesture.session_id,
                        gesture.result_summary,
                        gesture.timestamp.isoformat(),
                    ),
                )
                return cursor.lastrowid or 0

    async def load(self, garden_id: str) -> GardenState | None:
        """Load a garden by ID."""
        tracer = _get_store_tracer()
        with tracer.start_as_current_span("garden_store.load") as span:
            span.set_attribute("garden.id", garden_id)

            with self._connection() as conn:
                # Load garden
                cursor = conn.execute(
                    "SELECT * FROM gardens WHERE id = ?",
                    (garden_id,),
                )
                row = cursor.fetchone()

                if row is None:
                    return None

                garden = self._row_to_garden(row)

                # Load plots
                plots_cursor = conn.execute(
                    "SELECT * FROM garden_plots WHERE garden_id = ?",
                    (garden_id,),
                )
                for plot_row in plots_cursor.fetchall():
                    plot = self._row_to_plot(plot_row)
                    garden.plots[plot.name] = plot

                # Load recent gestures
                gestures_cursor = conn.execute(
                    """
                    SELECT * FROM garden_gestures
                    WHERE garden_id = ?
                    ORDER BY timestamp DESC
                    LIMIT 50
                    """,
                    (garden_id,),
                )
                gestures = [
                    StoredGesture.from_row(g).to_tending_gesture()
                    for g in gestures_cursor.fetchall()
                ]
                garden.recent_gestures = list(reversed(gestures))

                span.set_attribute("plots.count", len(garden.plots))
                span.set_attribute("gestures.count", len(garden.recent_gestures))

                return garden

    def _row_to_garden(self, row: sqlite3.Row) -> GardenState:
        """Convert database row to GardenState."""
        row_dict = dict(row)

        def parse_dt(val: str | None) -> datetime:
            if val:
                return datetime.fromisoformat(val)
            return datetime.now()

        metrics = GardenMetrics(
            entropy_spent=row_dict.get("entropy_spent", 0.0),
            entropy_budget=row_dict.get("entropy_budget", 1.0),
            total_prompts=row_dict.get("prompt_count", 0),
        )

        return GardenState(
            garden_id=row_dict["id"],
            name=row_dict["name"],
            season=GardenSeason[row_dict.get("season", "DORMANT")],
            season_since=parse_dt(row_dict.get("season_since")),
            active_plot=row_dict.get("active_plot"),
            session_id=row_dict.get("session_id"),
            prompt_count=row_dict.get("prompt_count", 0),
            prompt_types=json.loads(row_dict.get("prompt_types_json", "{}")),
            memory_crystals=json.loads(row_dict.get("memory_crystals_json", "[]")),
            metrics=metrics,
            created_at=parse_dt(row_dict.get("created_at")),
            last_tended=parse_dt(row_dict.get("last_tended")),
        )

    def _row_to_plot(self, row: sqlite3.Row) -> PlotState:
        """Convert database row to PlotState."""
        row_dict = dict(row)

        def parse_dt(val: str | None) -> datetime:
            if val:
                return datetime.fromisoformat(val)
            return datetime.now()

        season_override_name = row_dict.get("season_override")
        season_override = GardenSeason[season_override_name] if season_override_name else None

        return PlotState(
            name=row_dict["name"],
            path=row_dict["path"],
            description=row_dict.get("description", ""),
            plan_path=row_dict.get("plan_path"),
            crown_jewel=row_dict.get("crown_jewel"),
            prompts=json.loads(row_dict.get("prompts_json", "[]")),
            season_override=season_override,
            rigidity=row_dict.get("rigidity", 0.5),
            progress=row_dict.get("progress", 0.0),
            created_at=parse_dt(row_dict.get("created_at")),
            last_tended=parse_dt(row_dict.get("last_tended")),
            tags=json.loads(row_dict.get("tags_json", "[]")),
            metadata=json.loads(row_dict.get("metadata_json", "{}")),
        )

    async def get_default(self) -> GardenState:
        """
        Get the default garden, creating if needed.

        This is the main entry point for garden access.
        """
        tracer = _get_store_tracer()
        with tracer.start_as_current_span("garden_store.get_default"):
            with self._connection() as conn:
                # Check for existing default
                cursor = conn.execute(
                    """
                    SELECT g.* FROM gardens g
                    JOIN garden_default d ON g.id = d.garden_id
                    """
                )
                row = cursor.fetchone()

                if row:
                    garden_id = row["id"]
                else:
                    garden_id = None

            if garden_id:
                garden = await self.load(garden_id)
                if garden:
                    return garden

            # Create default garden
            import uuid

            from .plots import create_crown_jewel_plots

            garden = GardenState(
                garden_id=str(uuid.uuid4()),
                name="Default Garden",
                season=GardenSeason.DORMANT,
                plots=create_crown_jewel_plots(),
            )

            await self.save(garden)
            await self.set_default(garden.garden_id)

            return garden

    async def set_default(self, garden_id: str) -> None:
        """Set a garden as the default."""
        tracer = _get_store_tracer()
        with tracer.start_as_current_span("garden_store.set_default") as span:
            span.set_attribute("garden.id", garden_id)

            with self._connection() as conn:
                conn.execute(
                    """
                    UPDATE garden_default
                    SET garden_id = ?, updated_at = ?
                    WHERE id = 1
                    """,
                    (garden_id, datetime.now().isoformat()),
                )

    async def list_gardens(
        self,
        limit: int = 10,
    ) -> list[GardenState]:
        """List gardens, most recently updated first."""
        tracer = _get_store_tracer()
        with tracer.start_as_current_span("garden_store.list_gardens") as span:
            span.set_attribute("limit", limit)

            with self._connection() as conn:
                cursor = conn.execute(
                    """
                    SELECT * FROM gardens
                    ORDER BY updated_at DESC
                    LIMIT ?
                    """,
                    (limit,),
                )
                rows = cursor.fetchall()

            # Load each garden fully
            gardens = []
            for row in rows:
                garden = await self.load(row["id"])
                if garden:
                    gardens.append(garden)

            return gardens

    async def get_gestures(
        self,
        garden_id: str,
        limit: int = 100,
        verb: TendingVerb | None = None,
    ) -> list[TendingGesture]:
        """Get gestures for a garden."""
        tracer = _get_store_tracer()
        with tracer.start_as_current_span("garden_store.get_gestures") as span:
            span.set_attribute("garden.id", garden_id)

            with self._connection() as conn:
                if verb:
                    cursor = conn.execute(
                        """
                        SELECT * FROM garden_gestures
                        WHERE garden_id = ? AND verb = ?
                        ORDER BY timestamp DESC
                        LIMIT ?
                        """,
                        (garden_id, verb.name, limit),
                    )
                else:
                    cursor = conn.execute(
                        """
                        SELECT * FROM garden_gestures
                        WHERE garden_id = ?
                        ORDER BY timestamp DESC
                        LIMIT ?
                        """,
                        (garden_id, limit),
                    )

                rows = cursor.fetchall()

            return [StoredGesture.from_row(row).to_tending_gesture() for row in rows]

    async def delete(self, garden_id: str) -> bool:
        """Delete a garden and all its data."""
        tracer = _get_store_tracer()
        with tracer.start_as_current_span("garden_store.delete") as span:
            span.set_attribute("garden.id", garden_id)

            with self._connection() as conn:
                # Clear default if this was the default garden
                conn.execute(
                    """
                    UPDATE garden_default
                    SET garden_id = NULL, updated_at = ?
                    WHERE garden_id = ?
                    """,
                    (datetime.now().isoformat(), garden_id),
                )

                # Delete gestures (foreign key cascade should handle, but be explicit)
                conn.execute(
                    "DELETE FROM garden_gestures WHERE garden_id = ?",
                    (garden_id,),
                )

                # Delete plots
                conn.execute(
                    "DELETE FROM garden_plots WHERE garden_id = ?",
                    (garden_id,),
                )

                # Delete garden
                cursor = conn.execute(
                    "DELETE FROM gardens WHERE id = ?",
                    (garden_id,),
                )

                return cursor.rowcount > 0

    async def count(self) -> int:
        """Count total gardens."""
        with self._connection() as conn:
            cursor = conn.execute("SELECT COUNT(*) FROM gardens")
            row = cursor.fetchone()
            return row[0] if row else 0

    async def update_plot(
        self,
        garden_id: str,
        plot_name: str,
        progress: float | None = None,
        rigidity: float | None = None,
        season_override: GardenSeason | None = None,
    ) -> bool:
        """Update specific plot fields."""
        tracer = _get_store_tracer()
        with tracer.start_as_current_span("garden_store.update_plot") as span:
            span.set_attribute("garden.id", garden_id)
            span.set_attribute("plot.name", plot_name)

            updates = ["last_tended = ?"]
            params: list[Any] = [datetime.now().isoformat()]

            if progress is not None:
                updates.append("progress = ?")
                params.append(progress)

            if rigidity is not None:
                updates.append("rigidity = ?")
                params.append(rigidity)

            if season_override is not None:
                updates.append("season_override = ?")
                params.append(season_override.name)

            params.extend([garden_id, plot_name])

            with self._connection() as conn:
                cursor = conn.execute(
                    f"""
                    UPDATE garden_plots
                    SET {", ".join(updates)}
                    WHERE garden_id = ? AND name = ?
                    """,
                    params,
                )
                return cursor.rowcount > 0


# =============================================================================
# Factory
# =============================================================================


def create_garden_store(db_path: Path | str | None = None) -> GardenStore:
    """
    Create a GardenStore with sensible defaults.

    Args:
        db_path: Path to SQLite database. Defaults to XDG data directory.

    Returns:
        GardenStore ready for use (call await store.init() to initialize schema)
    """
    if db_path is None:
        import os

        xdg_data = os.environ.get("XDG_DATA_HOME", str(Path.home() / ".local" / "share"))
        db_path = Path(xdg_data) / "kgents" / "gardener_gardens.db"

    return GardenStore(db_path=Path(db_path))


# =============================================================================
# Singleton (for CLI convenience)
# =============================================================================

_default_store: GardenStore | None = None


async def get_garden_store() -> GardenStore:
    """
    Get the default GardenStore singleton.

    Creates and initializes if needed.
    """
    global _default_store
    if _default_store is None:
        _default_store = create_garden_store()
        await _default_store.init()
    return _default_store


def reset_garden_store() -> None:
    """Reset the singleton (for testing)."""
    global _default_store
    _default_store = None


__all__ = [
    "GardenStore",
    "StoredGesture",
    "create_garden_store",
    "get_garden_store",
    "reset_garden_store",
]
