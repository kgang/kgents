"""
TableAdapter: Bridge functor APP_STATE -> AGENT_MEMORY.

Lifts SQLAlchemy ORM models into DgentProtocol, enabling agent access
to application state through familiar D-gent patterns (lenses, causal chains).

This is the Bridge in the Dual-Track Architecture:
    APP_STATE (Alembic) <--Bridge--> AGENT_MEMORY (D-gent)

Category-theoretic perspective:
    TableAdapter is a functor F: APP_STATE -> AGENT_MEMORY
    where:
        - F(Table[T]) = DgentProtocol with content = serialize(T)
        - F(Migration) = identity (migrations don't exist in agent memory)

The functor is intentionally lossy (schema -> bytes loses type info)
but enables unified access patterns.

AGENTESE: self.data.table.*
"""

from __future__ import annotations

import json
import time
from dataclasses import dataclass, field
from typing import Any, Callable, Generic, TypeVar, cast

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker

from agents.d.datum import Datum
from agents.d.protocol import BaseDgent

T = TypeVar("T")  # SQLAlchemy model type


def _default_serialize(obj: Any) -> bytes:
    """
    Default serializer: model -> JSON bytes.

    Handles SQLAlchemy models by extracting non-private attributes.
    """
    if hasattr(obj, "__dict__"):
        # SQLAlchemy model: extract columns
        data = {
            k: v
            for k, v in obj.__dict__.items()
            if not k.startswith("_")
        }
        # Handle datetime serialization
        for k, v in data.items():
            if hasattr(v, "isoformat"):
                data[k] = v.isoformat()
        return json.dumps(data).encode("utf-8")
    else:
        return json.dumps(obj).encode("utf-8")


def _default_deserialize(data: bytes, model_cls: type[T]) -> dict[str, Any]:
    """
    Default deserializer: JSON bytes -> dict for model instantiation.

    Returns a dict that can be passed to model constructor.
    """
    return json.loads(data.decode("utf-8"))


@dataclass
class TableAdapter(BaseDgent, Generic[T]):
    """
    Lifts an Alembic-managed table into DgentProtocol.

    Enables agent access to application state via the same
    patterns used for agent memory (lenses, causal chains).

    Category-theoretic: This is a functor APP_STATE -> AGENT_MEMORY.

    Example:
        # Create adapter for Crystal model
        adapter = TableAdapter(
            model=Crystal,
            session_factory=get_session_factory(),
        )

        # Use D-gent patterns on application state
        datum = await adapter.get(crystal_id)
        crystals = await adapter.list(prefix="brain-")

        # Even works with causal chains (if model has causal_parent)
        chain = await adapter.causal_chain(turn_id)

    Attributes:
        model: The SQLAlchemy model class (e.g., Crystal)
        session_factory: Factory for creating async sessions
        id_field: Name of the primary key field (default: "id")
        serialize: Custom serializer (model -> bytes)
        deserialize: Custom deserializer (bytes -> dict)
    """

    model: type[T]
    session_factory: async_sessionmaker[AsyncSession]
    id_field: str = "id"
    serialize: Callable[[T], bytes] = field(default_factory=lambda: _default_serialize)
    deserialize: Callable[[bytes, type[T]], dict[str, Any]] = field(
        default_factory=lambda: _default_deserialize
    )

    # =========================================================================
    # DgentProtocol Implementation
    # =========================================================================

    async def put(self, datum: Datum) -> str:
        """
        Store datum by upserting into the Alembic table.

        The datum.content is deserialized to model attributes.
        If a record with the same ID exists, it's updated.
        """
        data = self.deserialize(datum.content, self.model)

        async with self.session_factory() as session:
            # Try to get existing record
            existing = await session.get(self.model, datum.id)

            if existing:
                # Update existing record
                for key, value in data.items():
                    if not key.startswith("_") and hasattr(existing, key):
                        setattr(existing, key, value)
            else:
                # Create new record
                # Ensure ID is set
                data[self.id_field] = datum.id

                # Handle causal_parent if model supports it
                if datum.causal_parent and hasattr(self.model, "causal_parent"):
                    data["causal_parent"] = datum.causal_parent

                # Handle timestamps if model supports them
                if hasattr(self.model, "created_at") and "created_at" not in data:
                    from datetime import datetime
                    data["created_at"] = datetime.fromtimestamp(datum.created_at)

                if hasattr(self.model, "updated_at") and "updated_at" not in data:
                    from datetime import datetime
                    data["updated_at"] = datetime.fromtimestamp(datum.created_at)

                instance = self.model(**data)
                session.add(instance)

            await session.commit()

        return datum.id

    async def get(self, id: str) -> Datum | None:
        """
        Retrieve from table, return as Datum.

        Converts the SQLAlchemy model back to a Datum with
        serialized content.
        """
        async with self.session_factory() as session:
            instance = await session.get(self.model, id)
            if instance is None:
                return None

            return self._model_to_datum(instance)

    async def delete(self, id: str) -> bool:
        """
        Delete from table.

        Returns True if record existed and was deleted.
        """
        async with self.session_factory() as session:
            instance = await session.get(self.model, id)
            if instance:
                await session.delete(instance)
                await session.commit()
                return True
            return False

    async def list(
        self,
        prefix: str | None = None,
        after: float | None = None,
        limit: int = 100,
    ) -> list[Datum]:
        """
        List from table with filters.

        Args:
            prefix: Filter by ID prefix (uses LIKE query)
            after: Filter by created_at > timestamp
            limit: Maximum results to return

        Returns:
            List of Datum, newest first
        """
        async with self.session_factory() as session:
            query = select(self.model)

            # Filter by ID prefix
            if prefix:
                id_col = getattr(self.model, self.id_field)
                query = query.where(id_col.startswith(prefix))

            # Filter by created_at timestamp
            if after and hasattr(self.model, "created_at"):
                from datetime import datetime
                created_col = getattr(self.model, "created_at")
                after_dt = datetime.fromtimestamp(after)
                query = query.where(created_col > after_dt)

            # Order by created_at descending (newest first)
            if hasattr(self.model, "created_at"):
                query = query.order_by(getattr(self.model, "created_at").desc())

            query = query.limit(limit)

            result = await session.execute(query)
            instances = result.scalars().all()

            return [self._model_to_datum(inst) for inst in instances]

    async def causal_chain(self, id: str) -> list[Datum]:
        """
        Get causal chain via recursive query.

        Follows causal_parent links to build ancestry.
        Returns [oldest_ancestor, ..., parent, current].

        Requires the model to have a causal_parent column.
        """
        if not hasattr(self.model, "causal_parent"):
            # Model doesn't support causality
            datum = await self.get(id)
            return [datum] if datum else []

        chain: list[Datum] = []
        current_id: str | None = id

        async with self.session_factory() as session:
            while current_id:
                instance = await session.get(self.model, current_id)
                if instance is None:
                    break

                chain.append(self._model_to_datum(instance))
                current_id = getattr(instance, "causal_parent", None)

        # Reverse to get oldest-first order
        chain.reverse()
        return chain

    async def exists(self, id: str) -> bool:
        """Check if record exists (optimized)."""
        async with self.session_factory() as session:
            result = await session.get(self.model, id)
            return result is not None

    async def count(self) -> int:
        """Count total records (optimized)."""
        from sqlalchemy import func

        async with self.session_factory() as session:
            query = select(func.count()).select_from(self.model)
            result = await session.execute(query)
            return result.scalar() or 0

    # =========================================================================
    # Helper Methods
    # =========================================================================

    def _model_to_datum(self, instance: T) -> Datum:
        """
        Convert SQLAlchemy model instance to Datum.

        Extracts:
        - id from id_field
        - created_at (or uses current time)
        - causal_parent (if available)
        - content as serialized model
        """
        # Get ID
        datum_id = getattr(instance, self.id_field)

        # Get created_at timestamp
        created_at = time.time()
        if hasattr(instance, "created_at"):
            created = getattr(instance, "created_at")
            if created:
                created_at = created.timestamp() if hasattr(created, "timestamp") else float(created)

        # Get causal_parent if available
        causal_parent = None
        if hasattr(instance, "causal_parent"):
            causal_parent = getattr(instance, "causal_parent")

        # Build metadata
        metadata = {
            "source": "alembic",
            "table": getattr(self.model, "__tablename__", self.model.__name__),
        }

        return Datum(
            id=str(datum_id),
            content=self.serialize(instance),
            created_at=created_at,
            causal_parent=causal_parent,
            metadata=metadata,
        )

    @property
    def table_name(self) -> str:
        """Get the underlying table name."""
        return getattr(self.model, "__tablename__", self.model.__name__)

    # =========================================================================
    # Integration with StateFunctor (Dual-Track Bridge)
    # =========================================================================

    def as_state_backend(self, key: str) -> "TableStateBackend[T]":
        """
        Create a StateBackend that uses this table for state storage.

        This enables StateFunctor to use Alembic tables for typed state:

            adapter = TableAdapter(Crystal, session_factory)
            backend = adapter.as_state_backend("session_crystal")

            state_functor = StateFunctor.create(backend=backend)
            crystal_agent = state_functor.lift_logic(crystal_logic)

        Args:
            key: The ID to use for state storage in this table

        Returns:
            StateBackend compatible with StateFunctor
        """
        return TableStateBackend(adapter=self, key=key)


@dataclass
class TableStateBackend(Generic[T]):
    """
    StateBackend implementation backed by TableAdapter.

    Enables StateFunctor to use Alembic tables for typed state storage.
    The state is stored as a single row with a fixed key/ID.

    This bridges S-gent (state threading) with D-gent (persistence)
    and Alembic (typed models).
    """

    adapter: TableAdapter[T]
    key: str
    initial: T | None = None

    async def load(self) -> T:
        """Load state from table."""
        datum = await self.adapter.get(self.key)
        if datum is None:
            if self.initial is not None:
                return self.initial
            raise ValueError(
                f"No state found for key '{self.key}' and no initial provided"
            )

        # Deserialize and reconstruct model
        data = self.adapter.deserialize(datum.content, self.adapter.model)
        return cast(T, self.adapter.model(**data))

    async def save(self, state: T) -> None:
        """Save state to table."""
        datum = Datum(
            id=self.key,
            content=self.adapter.serialize(state),
            created_at=time.time(),
            causal_parent=None,
            metadata={"type": "state", "table": self.adapter.table_name},
        )
        await self.adapter.put(datum)


__all__ = ["TableAdapter", "TableStateBackend"]
