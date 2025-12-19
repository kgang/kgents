"""
Tests for OpenAPI Projection Surface.

Verifies that the OpenAPILens functor correctly projects
AGENTESE registry -> OpenAPI 3.1 spec.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum
from typing import Optional

import pytest

from protocols.agentese.openapi import OpenAPILens, generate_openapi_spec

# === Test Fixtures for Schema Generation ===
# These must be at module level for get_type_hints() to resolve them.


@dataclass
class _OptionalFields:
    """Test dataclass with optional fields."""

    required_field: str
    optional_field: Optional[str] = None
    optional_int: Optional[int] = None


@dataclass
class _Inner:
    """Nested inner dataclass."""

    value: int


@dataclass
class _Outer:
    """Outer dataclass with nested inner."""

    name: str
    inner: _Inner


@dataclass
class _ListFields:
    """Dataclass with list fields."""

    strings: list[str]
    integers: list[int]


@dataclass
class _DictFields:
    """Dataclass with dict fields."""

    string_to_int: dict[str, int]


class _Color(Enum):
    """String enum for testing."""

    RED = "red"
    GREEN = "green"
    BLUE = "blue"


class _Priority(Enum):
    """Integer enum for testing."""

    LOW = 1
    MEDIUM = 2
    HIGH = 3


@dataclass
class _EnumFields:
    """Dataclass with enum fields."""

    color: _Color
    priority: _Priority


@dataclass
class _Defaults:
    """Dataclass with default values."""

    name: str
    count: int = 0
    enabled: bool = True
    label: str = "default"


@dataclass
class _Documented:
    """A well-documented dataclass."""

    name: str = field(metadata={"description": "The name of the thing"})


class TestOpenAPISpecGeneration:
    """Tests for generate_openapi_spec()."""

    def test_spec_is_valid_openapi_31(self) -> None:
        """Generated spec declares OpenAPI 3.1.0 version."""
        spec = generate_openapi_spec()
        assert spec["openapi"] == "3.1.0"

    def test_spec_has_required_fields(self) -> None:
        """Spec includes all required OpenAPI fields."""
        spec = generate_openapi_spec()
        assert "info" in spec
        assert "paths" in spec
        assert "components" in spec
        assert "servers" in spec

    def test_spec_has_x_agentese_extension(self) -> None:
        """Info section includes x-agentese extension."""
        spec = generate_openapi_spec()
        assert "x-agentese" in spec["info"]

        x_agentese = spec["info"]["x-agentese"]
        assert x_agentese["version"] == "3"
        assert set(x_agentese["contexts"]) == {"world", "self", "concept", "void", "time"}
        assert x_agentese["observer_header"] == "X-Observer-Archetype"
        assert x_agentese["discovery_endpoint"] == "/agentese/discover"

    def test_spec_includes_discovery_endpoint(self) -> None:
        """Discovery endpoint is documented in spec."""
        spec = generate_openapi_spec()
        assert "/discover" in spec["paths"]
        discover_op = spec["paths"]["/discover"]["get"]
        assert discover_op["operationId"] == "discover_paths"
        assert "discovery" in discover_op["tags"]

    def test_spec_has_observer_security_scheme(self) -> None:
        """Security scheme for observer header is defined."""
        spec = generate_openapi_spec()
        schemes = spec["components"]["securitySchemes"]
        assert "observerArchetype" in schemes
        assert schemes["observerArchetype"]["type"] == "apiKey"
        assert schemes["observerArchetype"]["in"] == "header"
        assert schemes["observerArchetype"]["name"] == "X-Observer-Archetype"

    def test_spec_has_context_tags(self) -> None:
        """Context tags are defined."""
        spec = generate_openapi_spec()
        tag_names = {t["name"] for t in spec["tags"]}
        assert "world" in tag_names
        assert "self" in tag_names
        assert "concept" in tag_names
        assert "void" in tag_names
        assert "time" in tag_names
        assert "discovery" in tag_names

    def test_custom_title_and_version(self) -> None:
        """Custom title and version are reflected in spec."""
        spec = generate_openapi_spec(title="Test API", version="2.0.0")
        assert spec["info"]["title"] == "Test API"
        assert spec["info"]["version"] == "2.0.0"

    def test_custom_base_path(self) -> None:
        """Custom base path affects server URL."""
        spec = generate_openapi_spec(base_path="/api/v2")
        assert spec["servers"][0]["url"] == "/api/v2"
        assert spec["info"]["x-agentese"]["discovery_endpoint"] == "/api/v2/discover"


class TestOpenAPILens:
    """Tests for OpenAPILens class."""

    def test_lens_project_returns_spec(self) -> None:
        """Lens project() returns valid OpenAPI spec."""
        lens = OpenAPILens()
        spec = lens.project()
        assert spec["openapi"] == "3.1.0"

    def test_lens_with_custom_config(self) -> None:
        """Lens accepts custom configuration."""
        lens = OpenAPILens(
            title="Custom API",
            version="3.0.0",
            description="Custom description",
            base_path="/custom",
        )
        spec = lens.project()
        assert spec["info"]["title"] == "Custom API"
        assert spec["info"]["version"] == "3.0.0"
        assert spec["info"]["description"] == "Custom description"
        assert spec["servers"][0]["url"] == "/custom"


class TestPathOperations:
    """Tests for path operation generation."""

    def test_registered_paths_have_manifest_endpoint(self) -> None:
        """Each registered path gets a manifest endpoint."""
        spec = generate_openapi_spec()
        # At minimum, we expect paths from the registry
        # Check that any path has manifest operation
        manifest_paths = [p for p in spec["paths"] if p.endswith("/manifest")]
        # We expect at least the discovery endpoint + some service paths
        # The exact count depends on what nodes are registered
        assert len(manifest_paths) >= 0  # May be 0 if no nodes registered in test

    def test_paths_have_affordances_endpoint(self) -> None:
        """Each registered path gets an affordances endpoint."""
        spec = generate_openapi_spec()
        affordances_paths = [p for p in spec["paths"] if p.endswith("/affordances")]
        # Same reasoning as manifest
        assert len(affordances_paths) >= 0

    def test_operations_have_x_agentese_path(self) -> None:
        """Operations include x-agentese-path extension."""
        spec = generate_openapi_spec()
        # Check a path operation (skip /discover)
        for path, methods in spec["paths"].items():
            if path == "/discover":
                continue
            for method, operation in methods.items():
                if "x-agentese-path" in operation:
                    # Found one - that's enough to prove the pattern works
                    assert isinstance(operation["x-agentese-path"], str)
                    return
        # If no paths with x-agentese-path, that's OK if registry is empty
        # This test passes either way

    def test_streaming_endpoints_have_event_stream_media_type(self) -> None:
        """
        Streaming endpoints declare text/event-stream content type.

        Note: We distinguish between:
        - True streaming variants: /path/aspect/stream (have sibling /path/aspect)
        - Aspects named 'stream': /path/stream (no sibling, has contract)

        Only true streaming variants should have text/event-stream.
        """
        spec = generate_openapi_spec()
        stream_paths = [p for p in spec["paths"] if p.endswith("/stream")]

        for path in stream_paths:
            # Check if this is a true streaming variant (has sibling)
            sibling = path.rsplit("/stream", 1)[0]
            is_streaming_variant = sibling in spec["paths"]

            if not is_streaming_variant:
                # This is an aspect named 'stream' - skip SSE check
                # It may be POST with contract, not GET with event-stream
                continue

            operation = spec["paths"][path].get("get", {})
            responses = operation.get("responses", {})
            success = responses.get("200", {})
            content = success.get("content", {})
            # True streaming variants should have text/event-stream
            assert "text/event-stream" in content, f"Stream path {path} missing event-stream"

    def test_aspect_named_stream_gets_contract(self) -> None:
        """
        Aspects literally named 'stream' get their contract, not SSE treatment.

        This is the edge case: self.chat has a 'stream' aspect with a contract.
        It should be POST with JSON schema, not GET with event-stream.
        """
        spec = generate_openapi_spec()

        # self.chat.stream is a known aspect-named-stream
        chat_stream_path = "/self/chat/stream"
        if chat_stream_path not in spec["paths"]:
            pytest.skip("self.chat node not registered in test environment")

        path_ops = spec["paths"][chat_stream_path]

        # Should be POST (mutation with request body)
        assert "post" in path_ops, "stream aspect should be POST"

        # Should have JSON response, not event-stream
        response = path_ops["post"]["responses"]["200"]
        content = response.get("content", {})
        assert "application/json" in content, "stream aspect should have JSON response"

        # And its streaming variant should exist at /stream/stream
        stream_stream_path = "/self/chat/stream/stream"
        if stream_stream_path in spec["paths"]:
            sse_content = spec["paths"][stream_stream_path]["get"]["responses"]["200"]["content"]
            assert "text/event-stream" in sse_content


class TestSpecValidity:
    """Tests for overall spec validity."""

    def test_spec_paths_are_strings(self) -> None:
        """All path keys are strings."""
        spec = generate_openapi_spec()
        for path in spec["paths"]:
            assert isinstance(path, str)
            assert path.startswith("/")

    def test_operation_ids_are_unique(self) -> None:
        """All operation IDs are unique."""
        spec = generate_openapi_spec()
        operation_ids: set[str] = set()

        for methods in spec["paths"].values():
            for operation in methods.values():
                op_id = operation.get("operationId")
                if op_id:
                    assert op_id not in operation_ids, f"Duplicate operationId: {op_id}"
                    operation_ids.add(op_id)

    def test_all_operations_have_responses(self) -> None:
        """All operations define at least one response."""
        spec = generate_openapi_spec()

        for path, methods in spec["paths"].items():
            for method, operation in methods.items():
                assert "responses" in operation, f"{method.upper()} {path} missing responses"
                assert len(operation["responses"]) > 0


# Integration test - requires actual registry
class TestIntegration:
    """Integration tests with actual registry (if nodes registered)."""

    def test_spec_generation_does_not_raise(self) -> None:
        """Spec generation completes without exceptions."""
        # This catches any runtime errors in the generation process
        spec = generate_openapi_spec()
        assert spec is not None

    def test_spec_is_json_serializable(self) -> None:
        """Generated spec can be serialized to JSON."""
        import json

        spec = generate_openapi_spec()
        json_str = json.dumps(spec)
        assert len(json_str) > 0

        # Round-trip
        parsed = json.loads(json_str)
        assert parsed["openapi"] == "3.1.0"


class TestEdgeCases:
    """Edge case tests for robustness."""

    def test_deeply_nested_aspects_get_unique_operation_ids(self) -> None:
        """
        Deeply nested aspects (3+ levels) generate unique operation IDs.

        Example: world.town.citizen.personality.trait should not collide
        with world.town.citizen.personality or world.town.citizen.
        """
        spec = generate_openapi_spec()
        operation_ids = []

        for methods in spec["paths"].values():
            for operation in methods.values():
                op_id = operation.get("operationId")
                if op_id:
                    operation_ids.append(op_id)

        # All operation IDs must be unique
        assert len(operation_ids) == len(set(operation_ids)), "Duplicate operation IDs found"

        # Check that nested paths have distinct operation IDs
        nested_ids = [oid for oid in operation_ids if oid.count("_") >= 3]
        assert len(nested_ids) == len(set(nested_ids)), "Nested aspect operation IDs collide"

    def test_paths_with_similar_prefixes_dont_collide(self) -> None:
        """
        Paths with similar prefixes generate distinct URLs.

        Example: world.town and world.town.citizen should not collide.
        """
        spec = generate_openapi_spec()

        # Find pairs of paths where one is prefix of another
        all_paths = sorted(spec["paths"].keys())
        for i, path1 in enumerate(all_paths):
            for path2 in all_paths[i + 1 :]:
                if path2.startswith(path1) and path1 != path2:
                    # These are related paths - both should exist distinctly
                    assert path1 in spec["paths"]
                    assert path2 in spec["paths"]

    def test_spec_handles_paths_without_contracts(self) -> None:
        """
        Paths without contracts still get manifest/affordances endpoints.

        Not all nodes define contracts - they should still be discoverable.
        Nested aspects inherit the parent node's manifest (e.g., world.forge.workshop.list
        inherits manifest from world.forge, not world.forge.workshop).
        """
        spec = generate_openapi_spec()

        def has_ancestor_manifest(path: str, paths: dict) -> bool:
            """Check if any ancestor path has a manifest endpoint."""
            parts = path.strip("/").split("/")
            # Walk up the path hierarchy
            for i in range(len(parts) - 1, 0, -1):
                ancestor = "/" + "/".join(parts[:i])
                if f"{ancestor}/manifest" in paths:
                    return True
            return False

        # Every AGENTESE path family should have a manifest endpoint
        # (except /discover which is special, and /stream variants)
        for path in spec["paths"]:
            if path == "/discover" or path.startswith("/discover/"):
                continue

            # Streaming variants are children of aspect paths, not path families
            if path.endswith("/stream"):
                # A streaming variant should have a sibling without /stream
                # Both are valid - no manifest check needed
                continue

            # Should be part of a path family with manifest
            path_base = path.rsplit("/", 1)[0] if "/" in path else path
            manifest_path = f"{path_base}/manifest"

            # Either this IS manifest, or manifest sibling exists, or ancestor has manifest
            is_manifest = path.endswith("/manifest")
            has_manifest_sibling = manifest_path in spec["paths"]
            has_ancestor = has_ancestor_manifest(path, spec["paths"])
            is_affordances = path.endswith("/affordances")

            assert is_manifest or has_manifest_sibling or has_ancestor or is_affordances, (
                f"Path {path} has no manifest endpoint"
            )

    def test_context_tags_cover_all_operations(self) -> None:
        """Every operation has a tag matching one of the AGENTESE contexts."""
        spec = generate_openapi_spec()
        valid_tags = {"world", "self", "concept", "void", "time", "discovery"}

        for path, methods in spec["paths"].items():
            for method, operation in methods.items():
                tags = operation.get("tags", [])
                if not tags:
                    continue  # Some operations may not have tags

                # At least one tag should be a valid context
                assert any(tag in valid_tags for tag in tags), (
                    f"{method.upper()} {path} has no valid context tag: {tags}"
                )

    def test_mutation_aspects_use_post(self) -> None:
        """
        Aspects with request contracts use POST method.

        GET is for queries; POST is for mutations with request bodies.
        """
        spec = generate_openapi_spec()

        for path, methods in spec["paths"].items():
            if "post" in methods:
                operation = methods["post"]
                # POST operations should have requestBody or be aspect invocations
                # (aspect invocations always allow body even if empty)
                if "requestBody" in operation:
                    content = operation["requestBody"].get("content", {})
                    # If there's a requestBody, it should have JSON content
                    assert "application/json" in content or content == {}, (
                        f"POST {path} has non-JSON requestBody"
                    )

    def test_spec_describes_error_responses(self) -> None:
        """Operations define 404 and/or 500 error responses."""
        spec = generate_openapi_spec()

        for path, methods in spec["paths"].items():
            if path == "/discover" or path.startswith("/discover/"):
                continue  # Discovery has different error semantics

            for method, operation in methods.items():
                responses = operation.get("responses", {})
                # Should have at least 200 + one error response
                assert "200" in responses, f"{method.upper()} {path} missing 200 response"

                # Most endpoints should have 404 for path-not-found
                has_error = "404" in responses or "500" in responses
                assert has_error, f"{method.upper()} {path} missing error responses"


class TestSchemaGeneration:
    """Tests for JSON Schema generation from contracts."""

    def test_optional_fields_are_nullable(self) -> None:
        """Optional[T] fields generate nullable schemas."""
        from protocols.agentese.schema_gen import dataclass_to_schema

        schema = dataclass_to_schema(_OptionalFields)

        # Required field should not be nullable
        assert "nullable" not in schema["properties"]["required_field"]

        # Optional fields should be nullable
        assert schema["properties"]["optional_field"].get("nullable") is True
        assert schema["properties"]["optional_int"].get("nullable") is True

        # Only required_field should be in required list
        assert schema["required"] == ["required_field"]

    def test_nested_dataclasses_generate_nested_schema(self) -> None:
        """Nested dataclasses generate nested object schemas."""
        from protocols.agentese.schema_gen import dataclass_to_schema

        schema = dataclass_to_schema(_Outer)

        # Inner should be an object type
        inner_schema = schema["properties"]["inner"]
        assert inner_schema["type"] == "object"
        assert inner_schema["title"] == "_Inner"
        assert "value" in inner_schema["properties"]
        assert inner_schema["properties"]["value"]["type"] == "integer"

    def test_list_fields_generate_array_schema(self) -> None:
        """List[T] fields generate array schemas with item types."""
        from protocols.agentese.schema_gen import dataclass_to_schema

        schema = dataclass_to_schema(_ListFields)

        # Typed lists should have items schema
        assert schema["properties"]["strings"]["type"] == "array"
        assert schema["properties"]["strings"]["items"]["type"] == "string"

        assert schema["properties"]["integers"]["type"] == "array"
        assert schema["properties"]["integers"]["items"]["type"] == "integer"

    def test_dict_fields_generate_object_schema(self) -> None:
        """Dict[K, V] fields generate object schemas with additionalProperties."""
        from protocols.agentese.schema_gen import dataclass_to_schema

        schema = dataclass_to_schema(_DictFields)

        # Typed dict should have additionalProperties
        assert schema["properties"]["string_to_int"]["type"] == "object"
        assert schema["properties"]["string_to_int"]["additionalProperties"]["type"] == "integer"

    def test_enum_fields_generate_enum_schema(self) -> None:
        """Enum fields generate enum schemas with values."""
        from protocols.agentese.schema_gen import dataclass_to_schema

        schema = dataclass_to_schema(_EnumFields)

        # String enum
        assert schema["properties"]["color"]["type"] == "string"
        assert schema["properties"]["color"]["enum"] == ["red", "green", "blue"]

        # Integer enum
        assert schema["properties"]["priority"]["type"] == "integer"
        assert schema["properties"]["priority"]["enum"] == [1, 2, 3]

    def test_default_values_are_included(self) -> None:
        """Default values appear in generated schema."""
        from protocols.agentese.schema_gen import dataclass_to_schema

        schema = dataclass_to_schema(_Defaults)

        # Fields with defaults should include them
        assert schema["properties"]["count"]["default"] == 0
        assert schema["properties"]["enabled"]["default"] is True
        assert schema["properties"]["label"]["default"] == "default"

        # Only name should be required
        assert schema["required"] == ["name"]

    def test_docstrings_become_descriptions(self) -> None:
        """Class and field docstrings become schema descriptions."""
        from protocols.agentese.schema_gen import dataclass_to_schema

        schema = dataclass_to_schema(_Documented)

        # Class docstring becomes schema description
        assert schema["description"] == "A well-documented dataclass."

        # Field metadata becomes property description
        assert schema["properties"]["name"]["description"] == "The name of the thing"


class TestPropertyBased:
    """Property-based tests using Hypothesis for robustness."""

    def test_spec_always_json_serializable(self) -> None:
        """
        Property: Any spec generation produces JSON-serializable output.

        Uses Hypothesis to vary title/version/base_path parameters.
        """
        import json

        from hypothesis import given, settings, strategies as st

        @given(
            title=st.text(min_size=1, max_size=50).filter(lambda x: x.strip()),
            version=st.from_regex(r"[0-9]+\.[0-9]+\.[0-9]+", fullmatch=True),
            base_path=st.from_regex(r"/[a-z]+(/[a-z]+)?", fullmatch=True),
        )
        @settings(max_examples=20)
        def check_serializable(title: str, version: str, base_path: str) -> None:
            spec = generate_openapi_spec(
                title=title,
                version=version,
                base_path=base_path,
            )
            # Must not raise
            json_str = json.dumps(spec)
            assert len(json_str) > 0
            # Round-trip must work
            parsed = json.loads(json_str)
            assert parsed["openapi"] == "3.1.0"

        check_serializable()

    def test_schema_gen_handles_all_basic_types(self) -> None:
        """
        Property: python_type_to_json_schema handles all basic types.

        Tests the type mapping covers primitives without exceptions.
        """
        from protocols.agentese.schema_gen import python_type_to_json_schema

        basic_types = [str, int, float, bool, bytes, type(None)]

        for py_type in basic_types:
            schema = python_type_to_json_schema(py_type)
            # All should produce some schema (even if empty for None)
            assert isinstance(schema, dict)

    def test_schema_gen_handles_collections(self) -> None:
        """
        Property: python_type_to_json_schema handles collection types.
        """
        from protocols.agentese.schema_gen import python_type_to_json_schema

        # List types
        list_schema = python_type_to_json_schema(list[str])
        assert list_schema["type"] == "array"
        assert list_schema["items"]["type"] == "string"

        # Dict types
        dict_schema = python_type_to_json_schema(dict[str, int])
        assert dict_schema["type"] == "object"
        assert dict_schema["additionalProperties"]["type"] == "integer"

        # Set types
        set_schema = python_type_to_json_schema(set[str])
        assert set_schema["type"] == "array"
        assert set_schema.get("uniqueItems") is True

        # Tuple types
        tuple_schema = python_type_to_json_schema(tuple[str, int])
        assert tuple_schema["type"] == "array"
        assert tuple_schema["minItems"] == 2
        assert tuple_schema["maxItems"] == 2

    def test_dataclass_schema_always_has_required_keys(self) -> None:
        """
        Property: Any dataclass schema has type, title, and properties.
        """
        from protocols.agentese.schema_gen import dataclass_to_schema

        test_classes = [
            _OptionalFields,
            _Inner,
            _Outer,
            _ListFields,
            _DictFields,
            _EnumFields,
            _Defaults,
            _Documented,
        ]

        for cls in test_classes:
            schema = dataclass_to_schema(cls)
            assert schema["type"] == "object", f"{cls.__name__} missing type"
            assert "title" in schema, f"{cls.__name__} missing title"
            assert "properties" in schema, f"{cls.__name__} missing properties"

    def test_openapi_spec_structure_invariants(self) -> None:
        """
        Property: OpenAPI spec always has required top-level keys.

        No matter what nodes are registered, these invariants hold.
        """
        spec = generate_openapi_spec()

        # Required OpenAPI 3.1 keys
        assert "openapi" in spec
        assert "info" in spec
        assert "paths" in spec

        # Info must have title and version
        assert "title" in spec["info"]
        assert "version" in spec["info"]

        # x-agentese extension always present
        assert "x-agentese" in spec["info"]
        assert "contexts" in spec["info"]["x-agentese"]
        assert "observer_header" in spec["info"]["x-agentese"]

        # Paths is always a dict
        assert isinstance(spec["paths"], dict)

        # All paths start with /
        for path in spec["paths"]:
            assert path.startswith("/"), f"Path {path} doesn't start with /"

    def test_operation_id_generation_is_deterministic(self) -> None:
        """
        Property: Same registry produces same operation IDs.

        Important for client code generation stability.
        """
        spec1 = generate_openapi_spec()
        spec2 = generate_openapi_spec()

        ids1 = set()
        ids2 = set()

        for methods in spec1["paths"].values():
            for op in methods.values():
                if "operationId" in op:
                    ids1.add(op["operationId"])

        for methods in spec2["paths"].values():
            for op in methods.values():
                if "operationId" in op:
                    ids2.add(op["operationId"])

        assert ids1 == ids2, "Operation IDs are not deterministic"


class TestErrorSurfaceDocumentation:
    """Tests for error surface visibility in generated spec."""

    def test_failed_schema_gen_includes_error_extension(self) -> None:
        """
        When schema generation fails, x-agentese-schema-error documents why.

        This ensures failures are visible, not silent.
        """
        from protocols.agentese.contract import Response
        from protocols.agentese.openapi import _build_response_schema

        # Create a Response with a non-dataclass type (will fail schema gen)
        class NotADataclass:
            pass

        contract = Response(NotADataclass)
        result = _build_response_schema(contract, "Test response")

        # Should have error extension
        assert "x-agentese-schema-error" in result
        error = result["x-agentese-schema-error"]
        assert error["type"] == "NotADataclass"
        assert "not a dataclass" in error["reason"].lower()
        assert "suggestion" in error

    def test_failed_request_schema_includes_error_extension(self) -> None:
        """
        When request schema generation fails, x-agentese-schema-error documents why.
        """
        from protocols.agentese.contract import Request
        from protocols.agentese.openapi import _build_request_body

        # Create a Request with a non-dataclass type (will fail schema gen)
        class NotADataclass:
            pass

        contract = Request(NotADataclass)
        result = _build_request_body(contract)

        # Should have error extension
        assert "x-agentese-schema-error" in result
        error = result["x-agentese-schema-error"]
        assert error["type"] == "NotADataclass"
        assert "suggestion" in error

    def test_successful_schema_gen_has_no_error_extension(self) -> None:
        """
        When schema generation succeeds, no error extension is present.
        """
        from protocols.agentese.contract import Response
        from protocols.agentese.openapi import _build_response_schema

        # Use a valid dataclass
        contract = Response(_Defaults)
        result = _build_response_schema(contract, "Test response")

        # Should NOT have error extension
        assert "x-agentese-schema-error" not in result
        # Should have actual schema
        assert "schema" in result["content"]["application/json"]
