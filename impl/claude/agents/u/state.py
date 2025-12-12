"""
D-gent Client: HTTP client for D-gent sidecar state operations.

This module provides a client for U-gent to access the D-gent sidecar
running in the same pod. The sidecar pattern enables:
- Separation of concerns (U-gent: execution, D-gent: state)
- Heterarchical design (peers, not master/slave)
- Minimal coupling (HTTP API, not library import)

Usage (with D-gent sidecar at localhost:8081):
    client = DgentClient()
    await client.put("session:123", {"step": 1})
    state = await client.get("session:123")

Usage (with custom URL):
    client = DgentClient(base_url="http://dgent.kgents.svc:8081")

AGENTESE: world.ugent.state
"""

from __future__ import annotations

import os
from dataclasses import dataclass, field
from typing import Any, Optional

import httpx


class StateNotFoundError(Exception):
    """Raised when requested state key doesn't exist."""

    pass


class VersionConflictError(Exception):
    """Raised on optimistic concurrency violation."""

    pass


class DgentConnectionError(Exception):
    """Raised when D-gent sidecar is unreachable."""

    pass


@dataclass
class StateValue:
    """A versioned state value from D-gent."""

    key: str
    value: Any
    version: int
    namespace: str
    created_at: str
    updated_at: str


@dataclass
class DgentClient:
    """
    Client for D-gent sidecar state operations.

    Provides async HTTP access to the D-gent sidecar running in the same pod.
    The sidecar exposes state management via localhost:8081 by default.

    Features:
    - Key-value state CRUD
    - Optimistic concurrency via CAS (Compare-And-Swap)
    - Namespace isolation for multi-tenant state
    - Checkpoint triggering for durability

    Principles:
    - Tasteful: Minimal API - just what's needed
    - Composable: Works standalone or injected
    - Heterarchical: U-gent and D-gent are peers
    """

    base_url: str = field(
        default_factory=lambda: os.environ.get("DGENT_URL", "http://localhost:8081")
    )
    timeout: float = 5.0  # Default timeout in seconds

    async def get(self, key: str, namespace: str = "default") -> Optional[StateValue]:
        """
        Get state by key.

        Args:
            key: State key
            namespace: Namespace for isolation

        Returns:
            StateValue if found, None if not found

        Raises:
            DgentConnectionError: If D-gent sidecar is unreachable
        """
        try:
            async with httpx.AsyncClient(timeout=self.timeout) as client:
                response = await client.get(
                    f"{self.base_url}/state/{key}",
                    params={"namespace": namespace},
                )

                if response.status_code == 404:
                    return None

                response.raise_for_status()
                data = response.json()

                return StateValue(
                    key=data["key"],
                    value=data["value"],
                    version=data["version"],
                    namespace=data["namespace"],
                    created_at=data.get("created_at", ""),
                    updated_at=data.get("updated_at", ""),
                )
        except httpx.ConnectError as e:
            raise DgentConnectionError(
                f"Cannot connect to D-gent at {self.base_url}: {e}"
            ) from e
        except httpx.TimeoutException as e:
            raise DgentConnectionError(
                f"Timeout connecting to D-gent at {self.base_url}: {e}"
            ) from e

    async def put(
        self,
        key: str,
        value: Any,
        namespace: str = "default",
        expected_version: Optional[int] = None,
    ) -> StateValue:
        """
        Put state with optional optimistic concurrency.

        Args:
            key: State key
            value: State value (must be JSON-serializable)
            namespace: Namespace for isolation
            expected_version: If provided, CAS check (None = no check,
                              0 = expect key doesn't exist)

        Returns:
            Updated StateValue with new version

        Raises:
            VersionConflictError: If expected_version doesn't match
            DgentConnectionError: If D-gent sidecar is unreachable
        """
        try:
            async with httpx.AsyncClient(timeout=self.timeout) as client:
                payload: dict[str, Any] = {"value": value}
                if expected_version is not None:
                    payload["expected_version"] = expected_version

                response = await client.put(
                    f"{self.base_url}/state/{key}",
                    params={"namespace": namespace},
                    json=payload,
                )

                if response.status_code == 409:
                    detail = response.json().get("detail", "Version conflict")
                    raise VersionConflictError(detail)

                response.raise_for_status()
                data = response.json()

                return StateValue(
                    key=data["key"],
                    value=data["value"],
                    version=data["version"],
                    namespace=data["namespace"],
                    created_at=data.get("created_at", ""),
                    updated_at=data.get("updated_at", ""),
                )
        except httpx.ConnectError as e:
            raise DgentConnectionError(
                f"Cannot connect to D-gent at {self.base_url}: {e}"
            ) from e
        except httpx.TimeoutException as e:
            raise DgentConnectionError(
                f"Timeout connecting to D-gent at {self.base_url}: {e}"
            ) from e

    async def delete(self, key: str, namespace: str = "default") -> bool:
        """
        Delete state by key.

        Args:
            key: State key
            namespace: Namespace for isolation

        Returns:
            True if deleted, False if key didn't exist

        Raises:
            DgentConnectionError: If D-gent sidecar is unreachable
        """
        try:
            async with httpx.AsyncClient(timeout=self.timeout) as client:
                response = await client.delete(
                    f"{self.base_url}/state/{key}",
                    params={"namespace": namespace},
                )

                if response.status_code == 404:
                    return False

                response.raise_for_status()
                return True
        except httpx.ConnectError as e:
            raise DgentConnectionError(
                f"Cannot connect to D-gent at {self.base_url}: {e}"
            ) from e
        except httpx.TimeoutException as e:
            raise DgentConnectionError(
                f"Timeout connecting to D-gent at {self.base_url}: {e}"
            ) from e

    async def list_keys(self, namespace: str = "default") -> list[str]:
        """
        List all keys in namespace.

        Args:
            namespace: Namespace to list keys from

        Returns:
            List of key names

        Raises:
            DgentConnectionError: If D-gent sidecar is unreachable
        """
        try:
            async with httpx.AsyncClient(timeout=self.timeout) as client:
                response = await client.get(
                    f"{self.base_url}/keys",
                    params={"namespace": namespace},
                )
                response.raise_for_status()
                data = response.json()
                keys: list[str] = data.get("keys", [])
                return keys
        except httpx.ConnectError as e:
            raise DgentConnectionError(
                f"Cannot connect to D-gent at {self.base_url}: {e}"
            ) from e
        except httpx.TimeoutException as e:
            raise DgentConnectionError(
                f"Timeout connecting to D-gent at {self.base_url}: {e}"
            ) from e

    async def checkpoint(self, namespace: str = "default") -> dict[str, Any]:
        """
        Trigger checkpoint creation for durability.

        Args:
            namespace: Namespace to checkpoint

        Returns:
            Checkpoint info (checkpoint_id, keys count, timestamp)

        Raises:
            DgentConnectionError: If D-gent sidecar is unreachable
        """
        try:
            async with httpx.AsyncClient(timeout=self.timeout) as client:
                response = await client.post(
                    f"{self.base_url}/checkpoint",
                    params={"namespace": namespace},
                )
                response.raise_for_status()
                result: dict[str, Any] = response.json()
                return result
        except httpx.ConnectError as e:
            raise DgentConnectionError(
                f"Cannot connect to D-gent at {self.base_url}: {e}"
            ) from e
        except httpx.TimeoutException as e:
            raise DgentConnectionError(
                f"Timeout connecting to D-gent at {self.base_url}: {e}"
            ) from e

    async def health(self) -> dict[str, Any]:
        """
        Check D-gent sidecar health.

        Returns:
            Health info (status, storage_type, keys_stored, namespaces)

        Raises:
            DgentConnectionError: If D-gent sidecar is unreachable
        """
        try:
            async with httpx.AsyncClient(timeout=self.timeout) as client:
                response = await client.get(f"{self.base_url}/health")
                response.raise_for_status()
                result: dict[str, Any] = response.json()
                return result
        except httpx.ConnectError as e:
            raise DgentConnectionError(
                f"Cannot connect to D-gent at {self.base_url}: {e}"
            ) from e
        except httpx.TimeoutException as e:
            raise DgentConnectionError(
                f"Timeout connecting to D-gent at {self.base_url}: {e}"
            ) from e
