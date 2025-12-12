"""
Tests for MCP K8s Resources (Phase E).

Tests the kgents:// resource scheme for exposing K8s cluster state.
"""

from __future__ import annotations

import json
import pytest

from ..resources import (
    K8sConfig,
    K8sResourceProvider,
    MCPResource,
    MCPResourceContent,
    KGENTS_RESOURCES,
    KGENTS_RESOURCE_TEMPLATES,
)
from ..server import MCPRequest, MCPServer


class TestMCPResource:
    """Tests for MCPResource dataclass."""

    def test_to_dict(self) -> None:
        resource = MCPResource(
            uri="kgents://test",
            name="Test",
            description="Test resource",
            mime_type="application/json",
        )
        d = resource.to_dict()
        assert d["uri"] == "kgents://test"
        assert d["name"] == "Test"
        assert d["mimeType"] == "application/json"

    def test_frozen(self) -> None:
        resource = MCPResource(uri="x", name="x", description="x")
        with pytest.raises(AttributeError):
            resource.uri = "y"  # type: ignore[misc]


class TestMCPResourceContent:
    """Tests for MCPResourceContent dataclass."""

    def test_to_dict(self) -> None:
        content = MCPResourceContent(
            uri="kgents://test",
            content='{"data": "value"}',
            mime_type="application/json",
        )
        d = content.to_dict()
        assert d["uri"] == "kgents://test"
        assert d["text"] == '{"data": "value"}'
        assert d["mimeType"] == "application/json"


class TestK8sConfig:
    """Tests for K8sConfig."""

    def test_defaults(self) -> None:
        config = K8sConfig()
        assert config.namespace == "kgents-agents"
        assert config.kubeconfig is None
        assert config.context is None

    def test_custom_namespace(self) -> None:
        config = K8sConfig(namespace="custom-ns")
        assert config.namespace == "custom-ns"


class TestK8sResourceProvider:
    """Tests for K8sResourceProvider."""

    def test_list_resources(self) -> None:
        provider = K8sResourceProvider()
        resources = provider.list_resources()

        assert len(resources) == 3
        uris = {r.uri for r in resources}
        assert "kgents://agents" in uris
        assert "kgents://pheromones" in uris
        assert "kgents://cluster/status" in uris

    def test_list_resource_templates(self) -> None:
        provider = K8sResourceProvider()
        templates = provider.list_resource_templates()

        assert len(templates) == 1
        assert templates[0]["uriTemplate"] == "kgents://agents/{name}"

    @pytest.mark.asyncio
    async def test_read_unknown_scheme(self) -> None:
        provider = K8sResourceProvider()
        result = await provider.read_resource("unknown://foo")

        data = json.loads(result.content)
        assert "error" in data

    @pytest.mark.asyncio
    async def test_read_unknown_path(self) -> None:
        provider = K8sResourceProvider()
        result = await provider.read_resource("kgents://nonexistent")

        data = json.loads(result.content)
        assert "error" in data


class TestKgentsResources:
    """Tests for exported resource constants."""

    def test_resources_defined(self) -> None:
        assert len(KGENTS_RESOURCES) == 3

    def test_templates_defined(self) -> None:
        assert len(KGENTS_RESOURCE_TEMPLATES) == 1

    def test_all_resources_have_kgents_scheme(self) -> None:
        for r in KGENTS_RESOURCES:
            assert r.uri.startswith("kgents://")


class TestMCPServerResources:
    """Tests for MCP server resource integration."""

    @pytest.mark.asyncio
    async def test_initialize_includes_resources(self) -> None:
        server = MCPServer()
        req = MCPRequest(jsonrpc="2.0", id=1, method="initialize", params={})
        resp = await server.handle_request(req)

        assert "resources" in resp.result["capabilities"]

    @pytest.mark.asyncio
    async def test_resources_list(self) -> None:
        server = MCPServer()
        req = MCPRequest(jsonrpc="2.0", id=1, method="resources/list", params={})
        resp = await server.handle_request(req)

        assert "resources" in resp.result
        assert len(resp.result["resources"]) == 3

    @pytest.mark.asyncio
    async def test_resources_templates_list(self) -> None:
        server = MCPServer()
        req = MCPRequest(
            jsonrpc="2.0", id=1, method="resources/templates/list", params={}
        )
        resp = await server.handle_request(req)

        assert "resourceTemplates" in resp.result
        assert len(resp.result["resourceTemplates"]) == 1

    @pytest.mark.asyncio
    async def test_resources_read(self) -> None:
        server = MCPServer()
        req = MCPRequest(
            jsonrpc="2.0",
            id=1,
            method="resources/read",
            params={"uri": "kgents://cluster/status"},
        )
        resp = await server.handle_request(req)

        assert "contents" in resp.result
        assert len(resp.result["contents"]) == 1
        content = resp.result["contents"][0]
        assert content["uri"] == "kgents://cluster/status"
        assert content["mimeType"] == "application/json"
