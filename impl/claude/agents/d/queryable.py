"""
QueryableDataAgent: Structured queries over D-gent state.

Provides a query interface for complex state access:
- Path-based access (JSONPath-like)
- Predicate filtering
- Aggregations
- Projections

Enables expressive state interrogation without full loads.
"""

import re
from dataclasses import dataclass, field
from enum import Enum, auto
from typing import (
    Any,
    Callable,
    Dict,
    Generic,
    List,
    Optional,
    TypeVar,
)

from .errors import StateError
from .protocol import DataAgent


class QueryError(StateError):
    """Query operation failed."""


class PathNotFoundError(QueryError):
    """Specified path does not exist in state."""


class InvalidQueryError(QueryError):
    """Query syntax or semantics invalid."""


S = TypeVar("S")
T = TypeVar("T")


class Operator(Enum):
    """Comparison operators for predicates."""

    EQ = auto()  # ==
    NE = auto()  # !=
    LT = auto()  # <
    LE = auto()  # <=
    GT = auto()  # >
    GE = auto()  # >=
    IN = auto()  # in
    CONTAINS = auto()  # contains
    MATCHES = auto()  # regex
    EXISTS = auto()  # exists


@dataclass
class Predicate:
    """A condition for filtering."""

    path: str
    operator: Operator
    value: Any = None

    def evaluate(self, data: Any) -> bool:
        """Evaluate predicate against data."""
        try:
            actual = _extract_path(data, self.path)
        except (KeyError, IndexError, TypeError, AttributeError):
            if self.operator == Operator.EXISTS:
                return False
            return False

        if self.operator == Operator.EXISTS:
            return True
        elif self.operator == Operator.EQ:
            return actual == self.value
        elif self.operator == Operator.NE:
            return actual != self.value
        elif self.operator == Operator.LT:
            return actual < self.value
        elif self.operator == Operator.LE:
            return actual <= self.value
        elif self.operator == Operator.GT:
            return actual > self.value
        elif self.operator == Operator.GE:
            return actual >= self.value
        elif self.operator == Operator.IN:
            return actual in self.value
        elif self.operator == Operator.CONTAINS:
            return self.value in actual
        elif self.operator == Operator.MATCHES:
            return bool(re.match(self.value, str(actual)))

        return False


@dataclass
class Query:
    """
    A structured query over state.

    Supports:
    - select: paths to extract (projection)
    - where: predicates to filter
    - limit: max results
    - offset: skip first N results
    """

    select: List[str] = field(default_factory=list)  # Paths to project
    where: List[Predicate] = field(default_factory=list)  # Filters
    order_by: Optional[str] = None  # Sort path
    descending: bool = False
    limit: Optional[int] = None
    offset: int = 0


@dataclass
class QueryResult(Generic[T]):
    """Result of a query execution."""

    data: T
    count: int
    total: int  # Total before limit/offset
    query_time_ms: float = 0.0


def _extract_path(data: Any, path: str) -> Any:
    """
    Extract value at path from data.

    Supports:
    - Dot notation: "user.name"
    - Index notation: "items[0]"
    - Mixed: "users[0].email"
    """
    if not path or path == ".":
        return data

    parts = re.split(r"\.|\[|\]", path)
    parts = [p for p in parts if p]  # Remove empty strings

    current = data
    for part in parts:
        if isinstance(current, dict):
            current = current[part]
        elif isinstance(current, (list, tuple)):
            current = current[int(part)]
        elif hasattr(current, part):
            current = getattr(current, part)
        else:
            raise KeyError(f"Cannot access '{part}' on {type(current)}")

    return current


def _set_path(data: Dict, path: str, value: Any) -> Dict:
    """Set value at path in data (immutable - returns new dict)."""
    if not path or path == ".":
        return value

    # Make a copy
    result = dict(data) if isinstance(data, dict) else data

    parts = path.split(".")
    current = result

    for i, part in enumerate(parts[:-1]):
        if part not in current:
            current[part] = {}
        elif not isinstance(current[part], dict):
            current[part] = {}
        else:
            current[part] = dict(current[part])
        current = current[part]

    current[parts[-1]] = value
    return result


class QueryableDataAgent(Generic[S]):
    """
    D-gent with query capabilities.

    Features:
    - get(): Path-based value extraction
    - query(): Structured queries with filtering/projection
    - aggregate(): Compute aggregates (count, sum, avg, etc.)
    - exists(): Check if path exists
    - find(): Find items matching predicate

    Example:
        >>> memory = VolatileAgent(_state={"users": [{"name": "Alice"}, {"name": "Bob"}]})
        >>> qa = QueryableDataAgent(memory)
        >>>
        >>> # Path-based access
        >>> await qa.get("users[0].name")  # Returns "Alice"
        >>>
        >>> # Query
        >>> result = await qa.query(Query(
        ...     select=["name"],
        ...     where=[Predicate("name", Operator.CONTAINS, "A")],
        ... ))
        >>> # Returns QueryResult with [{"name": "Alice"}]
    """

    def __init__(self, underlying: DataAgent[S]):
        """
        Wrap a D-gent with query capabilities.

        Args:
            underlying: The D-gent to wrap
        """
        self._underlying = underlying

    # === DataAgent Protocol ===

    async def load(self) -> S:
        """Load full state."""
        return await self._underlying.load()

    async def save(self, state: S) -> None:
        """Save full state."""
        await self._underlying.save(state)

    async def history(self, limit: int | None = None) -> List[S]:
        """Get state history."""
        return await self._underlying.history(limit)

    # === Query Operations ===

    async def get(self, path: str, default: Any = None) -> Any:
        """
        Get value at path.

        Args:
            path: Dot/bracket notation path (e.g., "user.name", "items[0]")
            default: Value to return if path doesn't exist

        Returns:
            Value at path, or default if not found
        """
        state = await self._underlying.load()
        try:
            return _extract_path(state, path)
        except (KeyError, IndexError, TypeError, AttributeError):
            return default

    async def exists(self, path: str) -> bool:
        """Check if path exists in state."""
        state = await self._underlying.load()
        try:
            _extract_path(state, path)
            return True
        except (KeyError, IndexError, TypeError, AttributeError):
            return False

    async def set(self, path: str, value: Any) -> None:
        """
        Set value at path (creates intermediate dicts as needed).

        Only works for dict-based states.
        """
        state = await self._underlying.load()
        if not isinstance(state, dict):
            raise QueryError("set() only works on dict-based states")

        new_state = _set_path(state, path, value)
        await self._underlying.save(new_state)

    async def query(self, q: Query) -> QueryResult:
        """
        Execute a structured query.

        Args:
            q: Query specification

        Returns:
            QueryResult with matching data
        """
        import time

        start = time.time()
        state = await self._underlying.load()

        # Determine what to query (state itself or a collection within)
        data = state

        # Apply filters
        if q.where:
            if isinstance(data, (list, tuple)):
                data = [item for item in data if all(p.evaluate(item) for p in q.where)]
            elif isinstance(data, dict):
                # Filter dict values if iterable
                if all(isinstance(v, dict) for v in data.values()):
                    data = {
                        k: v
                        for k, v in data.items()
                        if all(p.evaluate(v) for p in q.where)
                    }

        total = len(data) if isinstance(data, (list, tuple, dict)) else 1

        # Apply ordering
        if q.order_by and isinstance(data, list):
            try:
                data = sorted(
                    data,
                    key=lambda x: _extract_path(x, q.order_by),
                    reverse=q.descending,
                )
            except Exception:
                pass  # Skip sort on error

        # Apply offset/limit
        if isinstance(data, list):
            if q.offset:
                data = data[q.offset :]
            if q.limit:
                data = data[: q.limit]

        # Apply projection (select)
        if q.select and isinstance(data, list):
            projected = []
            for item in data:
                proj = {}
                for path in q.select:
                    try:
                        proj[path.split(".")[-1]] = _extract_path(item, path)
                    except Exception:
                        proj[path.split(".")[-1]] = None
                projected.append(proj)
            data = projected

        elapsed = (time.time() - start) * 1000

        return QueryResult(
            data=data,
            count=len(data) if isinstance(data, (list, tuple, dict)) else 1,
            total=total,
            query_time_ms=elapsed,
        )

    async def find(
        self,
        path: str,
        predicate: Callable[[Any], bool],
    ) -> List[Any]:
        """
        Find items matching a predicate.

        Args:
            path: Path to collection to search
            predicate: Function returning True for matches

        Returns:
            List of matching items
        """
        state = await self._underlying.load()
        collection = _extract_path(state, path) if path else state

        if not isinstance(collection, (list, tuple)):
            raise QueryError(f"Path '{path}' is not a collection")

        return [item for item in collection if predicate(item)]

    async def find_one(
        self,
        path: str,
        predicate: Callable[[Any], bool],
    ) -> Optional[Any]:
        """Find first item matching predicate."""
        results = await self.find(path, predicate)
        return results[0] if results else None

    # === Aggregations ===

    async def count(self, path: str = "") -> int:
        """Count items at path."""
        state = await self._underlying.load()
        data = _extract_path(state, path) if path else state

        if isinstance(data, (list, tuple, dict)):
            return len(data)
        return 1

    async def sum(self, path: str, value_path: str = "") -> float:
        """
        Sum numeric values at path.

        Args:
            path: Path to collection
            value_path: Path within each item to numeric value
        """
        state = await self._underlying.load()
        collection = _extract_path(state, path) if path else state

        if not isinstance(collection, (list, tuple)):
            raise QueryError(f"Path '{path}' is not a collection")

        total = 0.0
        for item in collection:
            try:
                value = _extract_path(item, value_path) if value_path else item
                total += float(value)
            except (TypeError, ValueError):
                continue

        return total

    async def avg(self, path: str, value_path: str = "") -> Optional[float]:
        """Average of numeric values at path."""
        state = await self._underlying.load()
        collection = _extract_path(state, path) if path else state

        if not isinstance(collection, (list, tuple)):
            raise QueryError(f"Path '{path}' is not a collection")

        values = []
        for item in collection:
            try:
                value = _extract_path(item, value_path) if value_path else item
                values.append(float(value))
            except (TypeError, ValueError):
                continue

        return sum(values) / len(values) if values else None

    async def min_value(self, path: str, value_path: str = "") -> Optional[Any]:
        """Minimum value at path."""
        state = await self._underlying.load()
        collection = _extract_path(state, path) if path else state

        if not isinstance(collection, (list, tuple)):
            raise QueryError(f"Path '{path}' is not a collection")

        values = []
        for item in collection:
            try:
                value = _extract_path(item, value_path) if value_path else item
                values.append(value)
            except Exception:
                continue

        return min(values) if values else None

    async def max_value(self, path: str, value_path: str = "") -> Optional[Any]:
        """Maximum value at path."""
        state = await self._underlying.load()
        collection = _extract_path(state, path) if path else state

        if not isinstance(collection, (list, tuple)):
            raise QueryError(f"Path '{path}' is not a collection")

        values = []
        for item in collection:
            try:
                value = _extract_path(item, value_path) if value_path else item
                values.append(value)
            except Exception:
                continue

        return max(values) if values else None

    async def distinct(self, path: str, value_path: str = "") -> List[Any]:
        """Get distinct values at path."""
        state = await self._underlying.load()
        collection = _extract_path(state, path) if path else state

        if not isinstance(collection, (list, tuple)):
            raise QueryError(f"Path '{path}' is not a collection")

        seen = set()
        results = []
        for item in collection:
            try:
                value = _extract_path(item, value_path) if value_path else item
                # Make hashable for dedup
                key = (
                    str(value)
                    if not isinstance(value, (str, int, float, bool))
                    else value
                )
                if key not in seen:
                    seen.add(key)
                    results.append(value)
            except Exception:
                continue

        return results

    async def group_by(
        self,
        path: str,
        key_path: str,
    ) -> Dict[Any, List[Any]]:
        """
        Group items by a key.

        Args:
            path: Path to collection
            key_path: Path to grouping key within each item

        Returns:
            Dict mapping key values to lists of items
        """
        state = await self._underlying.load()
        collection = _extract_path(state, path) if path else state

        if not isinstance(collection, (list, tuple)):
            raise QueryError(f"Path '{path}' is not a collection")

        groups: Dict[Any, List[Any]] = {}
        for item in collection:
            try:
                key = _extract_path(item, key_path)
                # Make hashable
                if isinstance(key, dict):
                    key = str(key)
                if key not in groups:
                    groups[key] = []
                groups[key].append(item)
            except Exception:
                continue

        return groups


# === Convenience Functions ===


def eq(path: str, value: Any) -> Predicate:
    """Create equality predicate."""
    return Predicate(path, Operator.EQ, value)


def ne(path: str, value: Any) -> Predicate:
    """Create inequality predicate."""
    return Predicate(path, Operator.NE, value)


def lt(path: str, value: Any) -> Predicate:
    """Create less-than predicate."""
    return Predicate(path, Operator.LT, value)


def le(path: str, value: Any) -> Predicate:
    """Create less-than-or-equal predicate."""
    return Predicate(path, Operator.LE, value)


def gt(path: str, value: Any) -> Predicate:
    """Create greater-than predicate."""
    return Predicate(path, Operator.GT, value)


def ge(path: str, value: Any) -> Predicate:
    """Create greater-than-or-equal predicate."""
    return Predicate(path, Operator.GE, value)


def contains(path: str, value: Any) -> Predicate:
    """Create contains predicate."""
    return Predicate(path, Operator.CONTAINS, value)


def matches(path: str, pattern: str) -> Predicate:
    """Create regex match predicate."""
    return Predicate(path, Operator.MATCHES, pattern)


def exists(path: str) -> Predicate:
    """Create exists predicate."""
    return Predicate(path, Operator.EXISTS)


def in_list(path: str, values: List[Any]) -> Predicate:
    """Create in-list predicate."""
    return Predicate(path, Operator.IN, values)
