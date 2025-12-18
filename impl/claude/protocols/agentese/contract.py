"""
AGENTESE Contract Protocol.

Defines Contract, Request, and Response types for @node decorator contracts.
These enable type-safe BE/FE synchronization via schema discovery.

The Contract Protocol (Phase 7: Autopoietic Architecture):
- @node(contracts={}) makes node the contract authority
- BE defines contracts, FE discovers at build time
- JSON Schema bridges Python dataclasses to TypeScript interfaces

Example:
    @node(
        "world.town",
        contracts={
            "manifest": Response(TownManifestResponse),
            "citizen.list": Contract(
                request=CitizensRequest,
                response=CitizensResponse,
            ),
        }
    )
    class TownNode(BaseLogosNode):
        ...

Usage:
    from protocols.agentese.contract import Contract, Response, Request

    # Perception aspects (no request needed)
    contracts = {
        "manifest": Response(ManifestData),
        "affordances": Response(AffordanceList),
    }

    # Mutation aspects (request + response)
    contracts = {
        "capture": Contract(CaptureRequest, CaptureResponse),
        "evolve": Contract(EvolveRequest, EvolveResponse),
    }
"""

from __future__ import annotations

import logging
from dataclasses import dataclass, field, is_dataclass
from typing import (
    TYPE_CHECKING,
    Any,
    Dict,
    Generic,
    Type,
    TypeVar,
    Union,
    get_type_hints,
)

if TYPE_CHECKING:
    pass

logger = logging.getLogger(__name__)

# Type variables for generic contracts
RequestT = TypeVar("RequestT")
ResponseT = TypeVar("ResponseT")


# === Contract Types ===


@dataclass(frozen=True)
class Response(Generic[ResponseT]):
    """
    Response-only contract for perception aspects.

    Use for aspects that don't require request parameters,
    such as manifest, affordances, witness.

    Attributes:
        response_type: The dataclass type for the response

    Example:
        contracts = {
            "manifest": Response(TownManifestResponse),
        }
    """

    response_type: Type[ResponseT]

    def __post_init__(self) -> None:
        """Validate response_type is a dataclass."""
        if not is_dataclass(self.response_type):
            logger.warning(
                f"Response type {self.response_type.__name__} is not a dataclass. "
                "Schema generation may not work correctly."
            )

    @property
    def has_request(self) -> bool:
        """Whether this contract has a request type."""
        return False

    def to_dict(self) -> dict[str, Any]:
        """Convert to dictionary for serialization."""
        return {
            "has_request": False,
            "response_type": self.response_type.__name__,
        }


@dataclass(frozen=True)
class Request(Generic[RequestT]):
    """
    Request-only contract (rare - for fire-and-forget operations).

    Attributes:
        request_type: The dataclass type for the request

    Example:
        contracts = {
            "notify": Request(NotificationRequest),
        }
    """

    request_type: Type[RequestT]

    def __post_init__(self) -> None:
        """Validate request_type is a dataclass."""
        if not is_dataclass(self.request_type):
            logger.warning(
                f"Request type {self.request_type.__name__} is not a dataclass. "
                "Schema generation may not work correctly."
            )

    @property
    def has_response(self) -> bool:
        """Whether this contract has a response type."""
        return False

    def to_dict(self) -> dict[str, Any]:
        """Convert to dictionary for serialization."""
        return {
            "has_response": False,
            "request_type": self.request_type.__name__,
        }


@dataclass(frozen=True)
class Contract(Generic[RequestT, ResponseT]):
    """
    Full contract with request and response types.

    Use for mutation aspects that require input parameters,
    such as capture, evolve, apply.

    Attributes:
        request: The dataclass type for the request
        response: The dataclass type for the response

    Example:
        contracts = {
            "capture": Contract(CaptureRequest, CaptureResponse),
            "citizen.list": Contract(
                request=CitizensRequest,
                response=CitizensResponse,
            ),
        }
    """

    request: Type[RequestT]
    response: Type[ResponseT]

    def __post_init__(self) -> None:
        """Validate both types are dataclasses."""
        if not is_dataclass(self.request):
            logger.warning(
                f"Request type {self.request.__name__} is not a dataclass. "
                "Schema generation may not work correctly."
            )
        if not is_dataclass(self.response):
            logger.warning(
                f"Response type {self.response.__name__} is not a dataclass. "
                "Schema generation may not work correctly."
            )

    @property
    def has_request(self) -> bool:
        """Whether this contract has a request type."""
        return True

    @property
    def has_response(self) -> bool:
        """Whether this contract has a response type."""
        return True

    def to_dict(self) -> dict[str, Any]:
        """Convert to dictionary for serialization."""
        return {
            "has_request": True,
            "has_response": True,
            "request_type": self.request.__name__,
            "response_type": self.response.__name__,
        }


# Union type for all contract kinds
ContractType = Union[Contract[Any, Any], Response[Any], Request[Any]]

# Type alias for contracts dictionary
ContractsDict = Dict[str, ContractType]


# === Contract Registry ===


@dataclass
class ContractRegistry:
    """
    Registry for node contracts.

    Stores contracts by path.aspect key for schema generation.
    """

    _contracts: dict[str, ContractsDict] = field(default_factory=dict)

    def register(self, path: str, contracts: ContractsDict) -> None:
        """
        Register contracts for a path.

        Args:
            path: AGENTESE path (e.g., "world.town")
            contracts: Dictionary of aspect -> contract
        """
        if path in self._contracts:
            logger.warning(f"Overwriting contracts for path: {path}")
        self._contracts[path] = contracts

    def get(self, path: str) -> ContractsDict | None:
        """Get contracts for a path."""
        return self._contracts.get(path)

    def get_aspect(self, path: str, aspect: str) -> ContractType | None:
        """Get contract for a specific path.aspect."""
        contracts = self._contracts.get(path)
        if contracts is None:
            return None
        return contracts.get(aspect)

    def list_paths(self) -> list[str]:
        """List all paths with contracts."""
        return list(self._contracts.keys())

    def list_aspects(self, path: str) -> list[str]:
        """List all aspects for a path."""
        contracts = self._contracts.get(path)
        if contracts is None:
            return []
        return list(contracts.keys())

    def stats(self) -> dict[str, Any]:
        """Get registry statistics."""
        total_aspects = sum(len(c) for c in self._contracts.values())
        return {
            "paths_with_contracts": len(self._contracts),
            "total_aspects": total_aspects,
            "paths": self.list_paths(),
        }

    def clear(self) -> None:
        """Clear all contracts (for testing)."""
        self._contracts.clear()


# Global singleton
_contract_registry: ContractRegistry | None = None


def get_contract_registry() -> ContractRegistry:
    """Get the global contract registry."""
    global _contract_registry
    if _contract_registry is None:
        _contract_registry = ContractRegistry()
    return _contract_registry


def reset_contract_registry() -> None:
    """Reset the global contract registry (for testing)."""
    global _contract_registry
    if _contract_registry is not None:
        _contract_registry.clear()
    _contract_registry = None


# === Exports ===

__all__ = [
    # Contract types
    "Contract",
    "Response",
    "Request",
    "ContractType",
    "ContractsDict",
    # Registry
    "ContractRegistry",
    "get_contract_registry",
    "reset_contract_registry",
]
