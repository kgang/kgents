"""
Tests for AGENTESE Contract Protocol (Phase 7).

Tests contract types, schema generation, and registry integration.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum
from typing import Any

import pytest
from protocols.agentese.contract import (
    Contract,
    ContractRegistry,
    Request,
    Response,
    get_contract_registry,
    reset_contract_registry,
)
from protocols.agentese.schema_gen import (
    contract_to_schema,
    dataclass_to_schema,
    node_contracts_to_schema,
    python_type_to_json_schema,
)

# === Test Fixtures ===


@dataclass
class SimpleResponse:
    """A simple response type."""

    name: str
    count: int


@dataclass
class SimpleRequest:
    """A simple request type."""

    query: str
    limit: int = 10


@dataclass
class ComplexResponse:
    """A response with complex types."""

    items: list[str]
    metadata: dict[str, Any]
    optional_field: str | None = None
    tags: frozenset[str] = field(default_factory=frozenset)


class StatusEnum(Enum):
    """Status enum for testing."""

    ACTIVE = "active"
    INACTIVE = "inactive"
    PENDING = "pending"


@dataclass
class EnumResponse:
    """Response with enum field."""

    status: StatusEnum
    count: int


@dataclass
class NestedRequest:
    """Request with nested dataclass."""

    simple: SimpleRequest
    name: str


@pytest.fixture(autouse=True)
def clean_registry() -> None:
    """Reset contract registry before each test."""
    reset_contract_registry()


# === Contract Type Tests ===


class TestResponse:
    """Tests for Response contract type."""

    def test_response_creation(self) -> None:
        """Response can be created with response type."""
        contract = Response(SimpleResponse)
        assert contract.response_type is SimpleResponse

    def test_response_has_request_false(self) -> None:
        """Response.has_request is always False."""
        contract = Response(SimpleResponse)
        assert contract.has_request is False

    def test_response_to_dict(self) -> None:
        """Response serializes to dict."""
        contract = Response(SimpleResponse)
        d = contract.to_dict()
        assert d["has_request"] is False
        assert d["response_type"] == "SimpleResponse"

    def test_response_is_frozen(self) -> None:
        """Response is immutable (frozen dataclass)."""
        contract = Response(SimpleResponse)
        with pytest.raises(AttributeError):
            contract.response_type = SimpleRequest  # type: ignore[misc]


class TestRequest:
    """Tests for Request contract type."""

    def test_request_creation(self) -> None:
        """Request can be created with request type."""
        contract = Request(SimpleRequest)
        assert contract.request_type is SimpleRequest

    def test_request_has_response_false(self) -> None:
        """Request.has_response is always False."""
        contract = Request(SimpleRequest)
        assert contract.has_response is False

    def test_request_to_dict(self) -> None:
        """Request serializes to dict."""
        contract = Request(SimpleRequest)
        d = contract.to_dict()
        assert d["has_response"] is False
        assert d["request_type"] == "SimpleRequest"


class TestContract:
    """Tests for full Contract type."""

    def test_contract_creation(self) -> None:
        """Contract can be created with request and response types."""
        contract = Contract(SimpleRequest, SimpleResponse)
        assert contract.request is SimpleRequest
        assert contract.response is SimpleResponse

    def test_contract_has_request_true(self) -> None:
        """Contract.has_request is True."""
        contract = Contract(SimpleRequest, SimpleResponse)
        assert contract.has_request is True

    def test_contract_has_response_true(self) -> None:
        """Contract.has_response is True."""
        contract = Contract(SimpleRequest, SimpleResponse)
        assert contract.has_response is True

    def test_contract_to_dict(self) -> None:
        """Contract serializes to dict."""
        contract = Contract(SimpleRequest, SimpleResponse)
        d = contract.to_dict()
        assert d["has_request"] is True
        assert d["has_response"] is True
        assert d["request_type"] == "SimpleRequest"
        assert d["response_type"] == "SimpleResponse"


# === Schema Generation Tests ===


class TestPythonTypeToJsonSchema:
    """Tests for python_type_to_json_schema."""

    def test_string_type(self) -> None:
        """String maps to JSON string."""
        schema = python_type_to_json_schema(str)
        assert schema["type"] == "string"

    def test_int_type(self) -> None:
        """Int maps to JSON integer."""
        schema = python_type_to_json_schema(int)
        assert schema["type"] == "integer"

    def test_float_type(self) -> None:
        """Float maps to JSON number."""
        schema = python_type_to_json_schema(float)
        assert schema["type"] == "number"

    def test_bool_type(self) -> None:
        """Bool maps to JSON boolean."""
        schema = python_type_to_json_schema(bool)
        assert schema["type"] == "boolean"

    def test_list_type(self) -> None:
        """List[str] maps to JSON array."""
        schema = python_type_to_json_schema(list[str])
        assert schema["type"] == "array"
        assert schema["items"]["type"] == "string"

    def test_dict_type(self) -> None:
        """Dict[str, int] maps to JSON object."""
        schema = python_type_to_json_schema(dict[str, int])
        assert schema["type"] == "object"
        assert schema["additionalProperties"]["type"] == "integer"

    def test_optional_type(self) -> None:
        """Optional[str] has nullable=True."""
        schema = python_type_to_json_schema(str | None)
        assert schema["type"] == "string"
        assert schema["nullable"] is True

    def test_enum_type(self) -> None:
        """Enum maps to JSON enum."""
        schema = python_type_to_json_schema(StatusEnum)
        assert schema["type"] == "string"
        assert set(schema["enum"]) == {"active", "inactive", "pending"}

    def test_nested_dataclass(self) -> None:
        """Nested dataclass generates nested schema."""
        schema = python_type_to_json_schema(SimpleRequest)
        assert schema["type"] == "object"
        assert "query" in schema["properties"]


class TestDataclassToSchema:
    """Tests for dataclass_to_schema."""

    def test_simple_dataclass(self) -> None:
        """Simple dataclass generates valid schema."""
        schema = dataclass_to_schema(SimpleResponse)
        assert schema["type"] == "object"
        assert schema["title"] == "SimpleResponse"
        assert "name" in schema["properties"]
        assert "count" in schema["properties"]
        assert "name" in schema["required"]
        assert "count" in schema["required"]

    def test_dataclass_with_defaults(self) -> None:
        """Fields with defaults are not required."""
        schema = dataclass_to_schema(SimpleRequest)
        assert "query" in schema["required"]
        assert "limit" not in schema["required"]
        # Default value included
        assert schema["properties"]["limit"]["default"] == 10

    def test_dataclass_with_docstring(self) -> None:
        """Docstring becomes description."""
        schema = dataclass_to_schema(SimpleResponse)
        assert "description" in schema
        assert "simple response" in schema["description"].lower()

    def test_complex_types(self) -> None:
        """Complex types (list, dict, optional) are handled."""
        schema = dataclass_to_schema(ComplexResponse)
        props = schema["properties"]

        # list[str]
        assert props["items"]["type"] == "array"
        assert props["items"]["items"]["type"] == "string"

        # dict[str, Any]
        assert props["metadata"]["type"] == "object"

        # str | None
        assert props["optional_field"]["nullable"] is True

    def test_nested_dataclass(self) -> None:
        """Nested dataclass generates nested schema."""
        schema = dataclass_to_schema(NestedRequest)
        props = schema["properties"]

        assert props["simple"]["type"] == "object"
        assert "query" in props["simple"]["properties"]

    def test_non_dataclass_raises(self) -> None:
        """Non-dataclass raises TypeError."""
        with pytest.raises(TypeError):
            dataclass_to_schema(str)  # type: ignore[arg-type]


class TestContractToSchema:
    """Tests for contract_to_schema."""

    def test_response_only(self) -> None:
        """Response contract generates response schema only."""
        contract = Response(SimpleResponse)
        schema = contract_to_schema(contract)

        assert "response" in schema
        assert "request" not in schema
        assert schema["response"]["title"] == "SimpleResponse"

    def test_request_only(self) -> None:
        """Request contract generates request schema only."""
        contract = Request(SimpleRequest)
        schema = contract_to_schema(contract)

        assert "request" in schema
        assert "response" not in schema
        assert schema["request"]["title"] == "SimpleRequest"

    def test_full_contract(self) -> None:
        """Full contract generates both schemas."""
        contract = Contract(SimpleRequest, SimpleResponse)
        schema = contract_to_schema(contract)

        assert "request" in schema
        assert "response" in schema
        assert schema["request"]["title"] == "SimpleRequest"
        assert schema["response"]["title"] == "SimpleResponse"


class TestNodeContractsToSchema:
    """Tests for node_contracts_to_schema."""

    def test_multiple_aspects(self) -> None:
        """Multiple aspects generate multiple schemas."""
        contracts = {
            "manifest": Response(SimpleResponse),
            "submit": Contract(SimpleRequest, SimpleResponse),
        }
        schemas = node_contracts_to_schema(contracts)

        assert "manifest" in schemas
        assert "submit" in schemas
        assert "response" in schemas["manifest"]
        assert "request" in schemas["submit"]
        assert "response" in schemas["submit"]


# === Contract Registry Tests ===


class TestContractRegistry:
    """Tests for ContractRegistry."""

    def test_register_and_get(self) -> None:
        """Contracts can be registered and retrieved."""
        registry = ContractRegistry()
        contracts = {"manifest": Response(SimpleResponse)}

        registry.register("test.path", contracts)
        retrieved = registry.get("test.path")

        assert retrieved is contracts

    def test_get_aspect(self) -> None:
        """Individual aspects can be retrieved."""
        registry = ContractRegistry()
        resp_contract = Response(SimpleResponse)
        contracts = {"manifest": resp_contract}

        registry.register("test.path", contracts)
        retrieved = registry.get_aspect("test.path", "manifest")

        assert retrieved is resp_contract

    def test_get_missing_returns_none(self) -> None:
        """Missing path returns None."""
        registry = ContractRegistry()
        assert registry.get("missing") is None
        assert registry.get_aspect("missing", "manifest") is None

    def test_list_paths(self) -> None:
        """list_paths returns all registered paths."""
        registry = ContractRegistry()
        registry.register("path.a", {"manifest": Response(SimpleResponse)})
        registry.register("path.b", {"manifest": Response(SimpleResponse)})

        paths = registry.list_paths()
        assert set(paths) == {"path.a", "path.b"}

    def test_list_aspects(self) -> None:
        """list_aspects returns all aspects for a path."""
        registry = ContractRegistry()
        contracts = {
            "manifest": Response(SimpleResponse),
            "submit": Contract(SimpleRequest, SimpleResponse),
        }
        registry.register("test.path", contracts)

        aspects = registry.list_aspects("test.path")
        assert set(aspects) == {"manifest", "submit"}

    def test_stats(self) -> None:
        """stats returns useful information."""
        registry = ContractRegistry()
        registry.register(
            "path.a",
            {
                "manifest": Response(SimpleResponse),
                "list": Response(SimpleResponse),
            },
        )
        registry.register("path.b", {"manifest": Response(SimpleResponse)})

        stats = registry.stats()
        assert stats["paths_with_contracts"] == 2
        assert stats["total_aspects"] == 3

    def test_clear(self) -> None:
        """clear removes all registrations."""
        registry = ContractRegistry()
        registry.register("test.path", {"manifest": Response(SimpleResponse)})
        registry.clear()

        assert registry.get("test.path") is None
        assert registry.list_paths() == []


class TestGlobalContractRegistry:
    """Tests for global contract registry functions."""

    def test_get_contract_registry_singleton(self) -> None:
        """get_contract_registry returns singleton."""
        registry1 = get_contract_registry()
        registry2 = get_contract_registry()
        assert registry1 is registry2

    def test_reset_clears_registry(self) -> None:
        """reset_contract_registry clears the registry."""
        registry = get_contract_registry()
        registry.register("test.path", {"manifest": Response(SimpleResponse)})

        reset_contract_registry()

        # After reset, new registry is empty
        new_registry = get_contract_registry()
        assert new_registry.get("test.path") is None


# === Integration Tests ===


class TestSchemaIntegration:
    """Integration tests for full schema generation flow."""

    def test_enum_in_dataclass(self) -> None:
        """Enums in dataclasses generate valid schemas."""
        schema = dataclass_to_schema(EnumResponse)
        status_schema = schema["properties"]["status"]

        assert status_schema["type"] == "string"
        assert set(status_schema["enum"]) == {"active", "inactive", "pending"}

    def test_deeply_nested(self) -> None:
        """Deeply nested structures work."""

        @dataclass
        class DeepNested:
            level1: dict[str, list[SimpleResponse]]

        schema = dataclass_to_schema(DeepNested)
        level1_schema = schema["properties"]["level1"]

        assert level1_schema["type"] == "object"
        assert level1_schema["additionalProperties"]["type"] == "array"
        assert level1_schema["additionalProperties"]["items"]["type"] == "object"

    def test_full_discovery_flow(self) -> None:
        """Full discovery flow generates expected output."""
        from protocols.agentese.schema_gen import discovery_schema

        all_contracts = {
            "world.town": {
                "manifest": Response(SimpleResponse),
                "citizen.list": Contract(SimpleRequest, SimpleResponse),
            },
            "self.memory": {
                "manifest": Response(SimpleResponse),
            },
        }

        schemas = discovery_schema(all_contracts)

        assert "world.town" in schemas
        assert "self.memory" in schemas
        assert "manifest" in schemas["world.town"]
        assert "citizen.list" in schemas["world.town"]
        assert "request" in schemas["world.town"]["citizen.list"]
        assert "response" in schemas["world.town"]["citizen.list"]
