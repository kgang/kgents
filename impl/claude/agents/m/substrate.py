"""
Substrate: Legacy stub for deleted module.

DEPRECATED: Use AssociativeMemory + DataBus instead.
"""

from dataclasses import dataclass, field
from typing import Any, Generic, TypeVar

T = TypeVar("T")


@dataclass
class MemoryQuota:
    """DEPRECATED: Old memory quota."""
    max_bytes: int = 1_000_000
    used_bytes: int = 0

    def can_allocate(self, size: int) -> bool:
        return self.used_bytes + size <= self.max_bytes

    def allocate(self, size: int) -> bool:
        if self.can_allocate(size):
            self.used_bytes += size
            return True
        return False


@dataclass
class SharedSubstrate(Generic[T]):
    """DEPRECATED: Old shared memory substrate."""
    quota: MemoryQuota = field(default_factory=MemoryQuota)
    _store: dict[str, T] = field(default_factory=dict, repr=False)

    def store(self, key: str, value: Any, size: int = 0) -> bool:
        if self.quota.allocate(size):
            self._store[key] = value
            return True
        return False

    def get(self, key: str) -> Any | None:
        return self._store.get(key)


def create_substrate(max_bytes: int = 1_000_000) -> SharedSubstrate[Any]:
    """Create a shared substrate (DEPRECATED)."""
    return SharedSubstrate(quota=MemoryQuota(max_bytes=max_bytes))


@dataclass
class CrystalPolicy:
    """DEPRECATED: Old crystal policy."""
    max_crystal_size: int = 10
    min_coherence: float = 0.5
