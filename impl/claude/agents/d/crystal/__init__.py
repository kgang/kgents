"""
Crystal - Unified Data Crystal Architecture.

Core primitives for kgents' data layer:
- Datum: Schema-free, immutable atom of data
- Crystal[T]: Typed, versioned datum with schema contract
- Schema[T]: Versioned contract with migration functions
- Query: Declarative, backend-agnostic query specification

Philosophy:
"The datum is a lie. There is only the crystal."

Datums are ground truth - they always work, no schema required.
Crystals are typed views formed by applying Schema pressure.
When schemas evolve, old data auto-upgrades lazily.

Spec: spec/protocols/unified-data-crystal.md

Example:
    >>> from agents.d.crystal import Datum, Crystal, Schema, Query
    >>> from dataclasses import dataclass
    >>>
    >>> # Define a contract
    >>> @dataclass(frozen=True)
    ... class Mark:
    ...     action: str
    ...     reasoning: str
    >>>
    >>> # Create schema
    >>> schema = Schema(name="witness.mark", version=1, contract=Mark)
    >>>
    >>> # Create and crystallize data
    >>> datum = Datum.create(
    ...     {"action": "implemented crystal", "reasoning": "foundation"},
    ...     tags={"witness", "core"},
    ...     author="claude",
    ... )
    >>> crystal = Crystal.from_datum(datum, schema)
    >>>
    >>> # Type-safe access
    >>> crystal.value.action  # → "implemented crystal"
    >>>
    >>> # Raw access always available
    >>> crystal.datum.data    # → {"action": ..., "reasoning": ...}
    >>>
    >>> # Query declaratively
    >>> q = Query(schema="witness.mark", tags=frozenset(["witness"]))
"""

from .datum import Datum
from .crystal import Crystal, CrystalMeta
from .schema import Schema
from .query import Query
from .self_justifying import SelfJustifyingCrystal

__all__ = [
    "Datum",
    "Crystal",
    "CrystalMeta",
    "Schema",
    "Query",
    "SelfJustifyingCrystal",
]
