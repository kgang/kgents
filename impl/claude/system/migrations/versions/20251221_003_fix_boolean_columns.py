"""Fix boolean columns: Convert INTEGER to BOOLEAN for PostgreSQL.

Revision ID: 003
Revises: 002
Create Date: 2025-12-21

The original migration created boolean columns as INTEGER for SQLite compatibility.
PostgreSQL needs native BOOLEAN columns for SQLAlchemy's boolean expressions
(e.g., `WHERE is_active` instead of `WHERE is_active = 1`).

This migration:
- PostgreSQL: Converts INTEGER columns to BOOLEAN with proper casting
- SQLite: No-op (SQLite handles integers as booleans natively)

Affected tables:
- town_citizens.is_active
- town_conversations.is_active
- atelier_workshops.is_active
- atelier_artisans.is_active
- atelier_exhibitions.is_open
- coalition_members.can_propose
- coalition_members.can_vote
- coalition_members.is_active
- park_hosts.is_active
- park_locations.is_open
- park_interactions.consent_requested
- park_interactions.consent_given
"""

from __future__ import annotations

from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op

# revision identifiers, used by Alembic.
revision: str = "003"
down_revision: Union[str, None] = "002"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def is_postgres() -> bool:
    """Check if running against PostgreSQL."""
    from alembic import context

    return context.get_context().dialect.name == "postgresql"


def convert_int_to_bool(table: str, column: str, default_value: bool = True) -> None:
    """Convert an INTEGER column to BOOLEAN in PostgreSQL.

    Steps:
    1. Drop the default constraint
    2. Convert the type with USING clause
    3. Set the new boolean default
    """
    default_sql = "TRUE" if default_value else "FALSE"

    # Drop default, convert type, set new default
    op.execute(f"""
        ALTER TABLE {table}
        ALTER COLUMN {column} DROP DEFAULT,
        ALTER COLUMN {column} TYPE BOOLEAN USING ({column} = 1),
        ALTER COLUMN {column} SET DEFAULT {default_sql}
    """)


def convert_int_to_bool_nullable(table: str, column: str) -> None:
    """Convert a nullable INTEGER column to BOOLEAN in PostgreSQL."""
    op.execute(f"""
        ALTER TABLE {table}
        ALTER COLUMN {column} DROP DEFAULT,
        ALTER COLUMN {column} TYPE BOOLEAN
        USING (CASE WHEN {column} IS NULL THEN NULL ELSE {column} = 1 END)
    """)


def convert_bool_to_int(table: str, column: str, default_value: int = 1) -> None:
    """Convert a BOOLEAN column back to INTEGER in PostgreSQL."""
    op.execute(f"""
        ALTER TABLE {table}
        ALTER COLUMN {column} DROP DEFAULT,
        ALTER COLUMN {column} TYPE INTEGER
        USING (CASE WHEN {column} THEN 1 ELSE 0 END),
        ALTER COLUMN {column} SET DEFAULT {default_value}
    """)


def convert_bool_to_int_nullable(table: str, column: str) -> None:
    """Convert a nullable BOOLEAN column back to INTEGER in PostgreSQL."""
    op.execute(f"""
        ALTER TABLE {table}
        ALTER COLUMN {column} TYPE INTEGER
        USING (CASE WHEN {column} IS NULL THEN NULL
               WHEN {column} THEN 1 ELSE 0 END)
    """)


def upgrade() -> None:
    if not is_postgres():
        # SQLite handles INTEGER as boolean natively - no changes needed
        return

    # Town tables
    convert_int_to_bool("town_citizens", "is_active", default_value=True)
    convert_int_to_bool("town_conversations", "is_active", default_value=True)

    # Atelier tables
    convert_int_to_bool("atelier_workshops", "is_active", default_value=True)
    convert_int_to_bool("atelier_artisans", "is_active", default_value=True)
    convert_int_to_bool("atelier_exhibitions", "is_open", default_value=False)

    # Coalition tables
    convert_int_to_bool("coalition_members", "can_propose", default_value=True)
    convert_int_to_bool("coalition_members", "can_vote", default_value=True)
    convert_int_to_bool("coalition_members", "is_active", default_value=True)

    # Park tables
    convert_int_to_bool("park_hosts", "is_active", default_value=True)
    convert_int_to_bool("park_locations", "is_open", default_value=True)
    convert_int_to_bool("park_interactions", "consent_requested", default_value=False)
    convert_int_to_bool_nullable("park_interactions", "consent_given")


def downgrade() -> None:
    if not is_postgres():
        return

    # Town tables
    convert_bool_to_int("town_citizens", "is_active", default_value=1)
    convert_bool_to_int("town_conversations", "is_active", default_value=1)

    # Atelier tables
    convert_bool_to_int("atelier_workshops", "is_active", default_value=1)
    convert_bool_to_int("atelier_artisans", "is_active", default_value=1)
    convert_bool_to_int("atelier_exhibitions", "is_open", default_value=0)

    # Coalition tables
    convert_bool_to_int("coalition_members", "can_propose", default_value=1)
    convert_bool_to_int("coalition_members", "can_vote", default_value=1)
    convert_bool_to_int("coalition_members", "is_active", default_value=1)

    # Park tables
    convert_bool_to_int("park_hosts", "is_active", default_value=1)
    convert_bool_to_int("park_locations", "is_open", default_value=1)
    convert_bool_to_int("park_interactions", "consent_requested", default_value=0)
    convert_bool_to_int_nullable("park_interactions", "consent_given")
