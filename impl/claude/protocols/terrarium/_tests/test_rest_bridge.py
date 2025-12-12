"""Tests for PrismRestBridge.

Tests the auto-generation of REST endpoints from CLICapable agents.
"""

from __future__ import annotations

from collections.abc import Callable
from typing import Any

import pytest
from protocols.cli.prism import CLICapable, expose
from protocols.terrarium.rest_bridge import (
    EndpointSpec,
    ParameterSpec,
    PrismRestBridge,
    _type_to_json_schema,
)


class MockGrammarAgent:
    """Mock CLICapable agent for testing."""

    @property
    def genus_name(self) -> str:
        return "grammar"

    @property
    def cli_description(self) -> str:
        return "Grammar/DSL operations"

    def get_exposed_commands(self) -> dict[str, Callable[..., object]]:
        return {
            "parse": self.parse,
            "reify": self.reify,
            "validate": self.validate,
        }

    @expose(help="Parse text into grammar representation")
    def parse(self, text: str, verbose: bool = False) -> dict[str, Any]:
        """Parse text into structured representation."""
        return {"parsed": text, "verbose": verbose}

    @expose(help="Reify a domain into Tongue artifact")
    async def reify(self, domain: str, level: str = "command") -> dict[str, Any]:
        """Transform domain into formal Tongue."""
        return {"domain": domain, "level": level}

    @expose(help="Validate grammar syntax")
    def validate(self, grammar: str, strict: bool = True) -> dict[str, Any]:
        """Check grammar for errors."""
        return {"valid": True, "strict": strict}


class TestTypeToJsonSchema:
    """Tests for type → JSON schema mapping."""

    def test_str_type(self) -> None:
        """str maps to string."""
        schema = _type_to_json_schema(str)
        assert schema == {"type": "string"}

    def test_int_type(self) -> None:
        """int maps to integer."""
        schema = _type_to_json_schema(int)
        assert schema == {"type": "integer"}

    def test_float_type(self) -> None:
        """float maps to number."""
        schema = _type_to_json_schema(float)
        assert schema == {"type": "number"}

    def test_bool_type(self) -> None:
        """bool maps to boolean."""
        schema = _type_to_json_schema(bool)
        assert schema == {"type": "boolean"}

    def test_list_type(self) -> None:
        """list[str] maps to array of strings."""
        schema = _type_to_json_schema(list[str])
        assert schema == {"type": "array", "items": {"type": "string"}}

    def test_optional_type(self) -> None:
        """str | None maps to nullable string."""
        schema = _type_to_json_schema(str | None)
        assert schema["type"] == "string"
        assert schema.get("nullable") is True


class TestParameterSpec:
    """Tests for ParameterSpec."""

    def test_to_json_schema_string(self) -> None:
        """String parameter creates string schema."""
        spec = ParameterSpec(
            name="text",
            python_type=str,
            required=True,
        )
        schema = spec.to_json_schema()
        assert schema == {"type": "string"}

    def test_to_json_schema_int(self) -> None:
        """Int parameter creates integer schema."""
        spec = ParameterSpec(
            name="count",
            python_type=int,
            required=True,
        )
        schema = spec.to_json_schema()
        assert schema == {"type": "integer"}

    def test_optional_parameter(self) -> None:
        """Optional parameter with default."""
        spec = ParameterSpec(
            name="verbose",
            python_type=bool,
            required=False,
            default=False,
        )
        assert spec.required is False
        assert spec.default is False


class TestEndpointSpec:
    """Tests for EndpointSpec."""

    def test_endpoint_spec_creation(self) -> None:
        """EndpointSpec captures method metadata."""

        def dummy_method(x: str) -> str:
            return x

        spec = EndpointSpec(
            name="test",
            method=dummy_method,
            parameters={"x": ParameterSpec(name="x", python_type=str, required=True)},
            description="Test endpoint",
            is_async=False,
        )

        assert spec.name == "test"
        assert spec.is_async is False
        assert "x" in spec.parameters


class TestPrismRestBridgeInit:
    """Tests for PrismRestBridge initialization."""

    def test_default_init(self) -> None:
        """Bridge initializes with defaults."""
        bridge = PrismRestBridge()

        assert bridge.api_prefix == "/api"
        assert len(bridge.mounted_agents) == 0

    def test_custom_prefix(self) -> None:
        """Bridge accepts custom API prefix."""
        bridge = PrismRestBridge(api_prefix="/v1")

        assert bridge.api_prefix == "/v1"


class TestPrismRestBridgeIntrospection:
    """Tests for method introspection."""

    def test_introspect_sync_method(self) -> None:
        """Introspects sync method correctly."""
        bridge = PrismRestBridge()
        agent = MockGrammarAgent()

        spec = bridge._introspect_method("parse", agent.parse)

        assert spec.name == "parse"
        assert spec.is_async is False
        assert "text" in spec.parameters
        assert spec.parameters["text"].required is True
        assert "verbose" in spec.parameters
        assert spec.parameters["verbose"].required is False

    def test_introspect_async_method(self) -> None:
        """Introspects async method correctly."""
        bridge = PrismRestBridge()
        agent = MockGrammarAgent()

        spec = bridge._introspect_method("reify", agent.reify)

        assert spec.name == "reify"
        assert spec.is_async is True
        assert "domain" in spec.parameters

    def test_introspect_extracts_description(self) -> None:
        """Description from @expose metadata."""
        bridge = PrismRestBridge()
        agent = MockGrammarAgent()

        spec = bridge._introspect_method("parse", agent.parse)

        assert spec.description == "Parse text into grammar representation"


class TestPrismRestBridgeMount:
    """Tests for mounting agents."""

    def test_mount_requires_fastapi(self) -> None:
        """Mount raises ImportError if FastAPI unavailable."""
        bridge = PrismRestBridge()
        agent = MockGrammarAgent()

        # This will work if FastAPI is installed
        # If not installed, ImportError is expected
        try:
            from fastapi import FastAPI

            app = FastAPI()
            bridge.mount(app, agent)

            assert "grammar" in bridge.mounted_agents
        except ImportError:
            pytest.skip("FastAPI not installed")

    def test_mount_duplicate_raises(self) -> None:
        """Cannot mount same agent twice."""
        try:
            from fastapi import FastAPI
        except ImportError:
            pytest.skip("FastAPI not installed")

        bridge = PrismRestBridge()
        agent = MockGrammarAgent()
        app = FastAPI()

        bridge.mount(app, agent)

        with pytest.raises(ValueError, match="already mounted"):
            bridge.mount(app, agent)

    def test_mounted_agents_property(self) -> None:
        """mounted_agents returns list of genus names."""
        try:
            from fastapi import FastAPI
        except ImportError:
            pytest.skip("FastAPI not installed")

        bridge = PrismRestBridge()
        agent = MockGrammarAgent()
        app = FastAPI()

        assert bridge.mounted_agents == []

        bridge.mount(app, agent)

        assert bridge.mounted_agents == ["grammar"]


class TestPrismRestBridgeOpenAPI:
    """Tests for OpenAPI schema generation."""

    def test_get_openapi_schema(self) -> None:
        """Generates OpenAPI paths for agent."""
        bridge = PrismRestBridge()
        agent = MockGrammarAgent()

        schema = bridge.get_openapi_schema(agent)

        # Should have paths for each command
        assert "/api/grammar/parse" in schema
        assert "/api/grammar/reify" in schema
        assert "/api/grammar/validate" in schema

    def test_openapi_schema_has_post_methods(self) -> None:
        """All paths have POST method."""
        bridge = PrismRestBridge()
        agent = MockGrammarAgent()

        schema = bridge.get_openapi_schema(agent)

        for path, methods in schema.items():
            assert "post" in methods

    def test_openapi_schema_request_body(self) -> None:
        """Paths include request body schema."""
        bridge = PrismRestBridge()
        agent = MockGrammarAgent()

        schema = bridge.get_openapi_schema(agent)
        parse_path = schema["/api/grammar/parse"]

        request_body = parse_path["post"]["requestBody"]
        json_schema = request_body["content"]["application/json"]["schema"]

        assert "text" in json_schema["properties"]
        assert "text" in json_schema["required"]
        assert "verbose" in json_schema["properties"]

    def test_openapi_schema_responses(self) -> None:
        """Paths include response definitions."""
        bridge = PrismRestBridge()
        agent = MockGrammarAgent()

        schema = bridge.get_openapi_schema(agent)
        parse_path = schema["/api/grammar/parse"]

        responses = parse_path["post"]["responses"]

        assert "200" in responses
        assert "400" in responses
        assert "500" in responses


class TestPrismRestBridgeUnmount:
    """Tests for unmounting agents."""

    def test_unmount_removes_tracking(self) -> None:
        """Unmount removes agent from tracking."""
        try:
            from fastapi import FastAPI
        except ImportError:
            pytest.skip("FastAPI not installed")

        bridge = PrismRestBridge()
        agent = MockGrammarAgent()
        app = FastAPI()

        bridge.mount(app, agent)
        assert "grammar" in bridge.mounted_agents

        result = bridge.unmount(app, "grammar")

        assert result is True
        assert "grammar" not in bridge.mounted_agents

    def test_unmount_nonexistent(self) -> None:
        """Unmount returns False for unknown agent."""
        bridge = PrismRestBridge()

        result = bridge.unmount(None, "unknown")

        assert result is False


class TestPrismRestBridgeEndpoint:
    """Integration tests for generated endpoints."""

    @pytest.mark.asyncio
    async def test_endpoint_calls_sync_method(self) -> None:
        """Generated endpoint calls sync method."""
        try:
            from fastapi import FastAPI
            from fastapi.testclient import TestClient
        except ImportError:
            pytest.skip("FastAPI not installed")

        bridge = PrismRestBridge()
        agent = MockGrammarAgent()
        app = FastAPI()

        bridge.mount(app, agent)

        client = TestClient(app)
        response = client.post("/api/grammar/parse", json={"text": "hello world"})

        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True
        assert data["result"]["parsed"] == "hello world"

    @pytest.mark.asyncio
    async def test_endpoint_calls_async_method(self) -> None:
        """Generated endpoint calls async method."""
        try:
            from fastapi import FastAPI
            from fastapi.testclient import TestClient
        except ImportError:
            pytest.skip("FastAPI not installed")

        bridge = PrismRestBridge()
        agent = MockGrammarAgent()
        app = FastAPI()

        bridge.mount(app, agent)

        client = TestClient(app)
        response = client.post(
            "/api/grammar/reify", json={"domain": "Calendar Management"}
        )

        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True
        assert data["result"]["domain"] == "Calendar Management"

    @pytest.mark.asyncio
    async def test_endpoint_with_optional_params(self) -> None:
        """Endpoint handles optional parameters."""
        try:
            from fastapi import FastAPI
            from fastapi.testclient import TestClient
        except ImportError:
            pytest.skip("FastAPI not installed")

        bridge = PrismRestBridge()
        agent = MockGrammarAgent()
        app = FastAPI()

        bridge.mount(app, agent)

        client = TestClient(app)

        # Without optional param
        response = client.post("/api/grammar/parse", json={"text": "test"})
        assert response.json()["result"]["verbose"] is False

        # With optional param
        response = client.post(
            "/api/grammar/parse", json={"text": "test", "verbose": True}
        )
        assert response.json()["result"]["verbose"] is True

    @pytest.mark.asyncio
    async def test_endpoint_missing_required_param(self) -> None:
        """Endpoint returns 400 for missing required params."""
        try:
            from fastapi import FastAPI
            from fastapi.testclient import TestClient
        except ImportError:
            pytest.skip("FastAPI not installed")

        bridge = PrismRestBridge()
        agent = MockGrammarAgent()
        app = FastAPI()

        bridge.mount(app, agent)

        client = TestClient(app)
        response = client.post("/api/grammar/parse", json={})

        assert response.status_code == 400
        data = response.json()
        assert "missing" in data
        assert "text" in data["missing"]

    @pytest.mark.asyncio
    async def test_endpoint_empty_body(self) -> None:
        """Endpoint handles empty request body."""
        try:
            from fastapi import FastAPI
            from fastapi.testclient import TestClient
        except ImportError:
            pytest.skip("FastAPI not installed")

        bridge = PrismRestBridge()
        agent = MockGrammarAgent()
        app = FastAPI()

        bridge.mount(app, agent)

        client = TestClient(app)
        # Send request with no body
        response = client.post("/api/grammar/parse")

        assert response.status_code == 400


class TestCLICapableProtocol:
    """Test CLICapable protocol compliance."""

    def test_mock_agent_is_cli_capable(self) -> None:
        """MockGrammarAgent satisfies CLICapable protocol."""
        agent = MockGrammarAgent()
        assert isinstance(agent, CLICapable)
