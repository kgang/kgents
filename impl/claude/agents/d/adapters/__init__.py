"""
D-gent Adapters: Bridge various storage systems to DgentProtocol.

This module provides adapters that wrap different storage backends
to implement the DgentProtocol interface.

Adapters:
    - TableAdapter: Bridge SQLAlchemy ORM models to DgentProtocol

Part of the Dual-Track Architecture:
    - D-gent Track: Agent memory (schema-free, append-only, lenses)
    - Alembic Track: Application state (typed models, migrations, FK)
    - TableAdapter: Bridge that lifts Alembic tables into DgentProtocol

AGENTESE: self.data.table.*
"""

from .table_adapter import TableAdapter

__all__ = ["TableAdapter"]
