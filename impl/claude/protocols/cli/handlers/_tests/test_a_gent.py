"""
Tests for A-gent CLI handler.

The A-gent handler exposes the Alethic Architecture via CLI:
- kgents a inspect <agent>  - Show Halo + Nucleus
- kgents a manifest <agent> - K8sProjector -> YAML
- kgents a run <agent>      - LocalProjector -> run
- kgents a list             - List available agents
"""

from __future__ import annotations

import json
from typing import TYPE_CHECKING, Any, cast

import pytest
from protocols.cli.handlers.a_gent import (
    _handle_inspect,
    _handle_list,
    _handle_manifest,
    _handle_run,
    _resolve_agent_class,
    cmd_a,
)

if TYPE_CHECKING:
    from protocols.cli.reflector import InvocationContext


class MockContext:
    """Mock invocation context for testing.

    Implements the `output` method used by handlers.
    Cast to InvocationContext for type checker satisfaction.
    """

    def __init__(self) -> None:
        self.outputs: list[tuple[str, dict[str, Any]]] = []

    def output(self, human: str, semantic: dict[str, Any]) -> None:
        self.outputs.append((human, semantic))


def _ctx(mock: MockContext) -> "InvocationContext | None":
    """Cast MockContext to InvocationContext for type checking."""
    return cast("InvocationContext | None", mock)


# ===========================================================================
# Test: Agent Resolution
# ===========================================================================


class TestAgentResolution:
    """Tests for agent class resolution."""

    def test_resolve_kappa_archetype(self) -> None:
        """Kappa archetype is resolved."""
        cls = _resolve_agent_class("Kappa")
        assert cls is not None
        assert cls.__name__ == "Kappa"

    def test_resolve_lambda_archetype(self) -> None:
        """Lambda archetype is resolved."""
        cls = _resolve_agent_class("Lambda")
        assert cls is not None
        assert cls.__name__ == "Lambda"

    def test_resolve_delta_archetype(self) -> None:
        """Delta archetype is resolved."""
        cls = _resolve_agent_class("Delta")
        assert cls is not None
        assert cls.__name__ == "Delta"

    def test_resolve_case_insensitive(self) -> None:
        """Resolution is case-insensitive for archetypes."""
        cls1 = _resolve_agent_class("kappa")
        cls2 = _resolve_agent_class("KAPPA")
        cls3 = _resolve_agent_class("Kappa")
        assert cls1 is cls2 is cls3

    def test_resolve_nonexistent_returns_none(self) -> None:
        """Non-existent agent returns None."""
        cls = _resolve_agent_class("NonExistentAgent")
        assert cls is None


# ===========================================================================
# Test: cmd_a (Main Handler)
# ===========================================================================


class TestCmdA:
    """Tests for the main cmd_a handler."""

    def test_help_flag(self) -> None:
        """--help shows help and returns 0."""
        result = cmd_a(["--help"])
        assert result == 0

    def test_no_args_shows_help(self) -> None:
        """No arguments shows help and returns 0."""
        result = cmd_a([])
        assert result == 0

    def test_unknown_command_returns_error(self) -> None:
        """Unknown command returns 1."""
        ctx = MockContext()
        result = cmd_a(["unknown"], _ctx(ctx))
        assert result == 1
        assert any("Unknown command" in o[0] for o in ctx.outputs)


# ===========================================================================
# Test: Inspect Command
# ===========================================================================


class TestInspectCommand:
    """Tests for 'a inspect' command."""

    def test_inspect_kappa(self) -> None:
        """Inspect Kappa archetype shows capabilities."""
        ctx = MockContext()
        result = _handle_inspect("Kappa", json_mode=False, ctx=_ctx(ctx))
        assert result == 0
        output = ctx.outputs[0][0]
        assert "Kappa" in output
        assert "Capabilities" in output

    def test_inspect_kappa_json(self) -> None:
        """Inspect Kappa in JSON mode produces valid JSON."""
        ctx = MockContext()
        result = _handle_inspect("Kappa", json_mode=True, ctx=_ctx(ctx))
        assert result == 0

        output = ctx.outputs[0][0]
        data = json.loads(output)
        assert data["agent"] == "Kappa"
        assert "capabilities" in data

    def test_inspect_lambda_shows_observable(self) -> None:
        """Lambda archetype shows Observable capability."""
        ctx = MockContext()
        result = _handle_inspect("Lambda", json_mode=True, ctx=_ctx(ctx))
        assert result == 0

        data = json.loads(ctx.outputs[0][0])
        cap_names = [c["name"] for c in data["capabilities"]]
        assert "ObservableCapability" in cap_names

    def test_inspect_nonexistent_returns_error(self) -> None:
        """Inspect non-existent agent returns error."""
        ctx = MockContext()
        result = _handle_inspect("NonExistent", json_mode=False, ctx=_ctx(ctx))
        assert result == 1
        assert any("not found" in o[0] for o in ctx.outputs)


# ===========================================================================
# Test: Manifest Command
# ===========================================================================


class TestManifestCommand:
    """Tests for 'a manifest' command."""

    def test_manifest_kappa_produces_yaml(self) -> None:
        """Manifest for Kappa produces YAML output."""
        ctx = MockContext()
        result = _handle_manifest(
            "Kappa",
            namespace="test-ns",
            json_mode=False,
            validate_mode=False,
            ctx=_ctx(ctx),
        )
        assert result == 0

        output = ctx.outputs[0][0]
        # Should contain K8s resource indicators
        assert "apiVersion" in output or "kind" in output

    def test_manifest_kappa_json(self) -> None:
        """Manifest in JSON mode produces valid JSON."""
        ctx = MockContext()
        result = _handle_manifest(
            "Kappa",
            namespace="test-ns",
            json_mode=True,
            validate_mode=False,
            ctx=_ctx(ctx),
        )
        assert result == 0

        data = json.loads(ctx.outputs[0][0])
        assert isinstance(data, dict)
        assert "manifests" in data
        assert len(data["manifests"]) > 0

        # Should have various K8s resource kinds
        kinds = {r["kind"] for r in data["manifests"]}
        assert "StatefulSet" in kinds  # Kappa is @Stateful
        assert "Service" in kinds

    def test_manifest_lambda_produces_deployment(self) -> None:
        """Lambda (minimal) produces Deployment not StatefulSet."""
        ctx = MockContext()
        result = _handle_manifest(
            "Lambda",
            namespace="test",
            json_mode=True,
            validate_mode=False,
            ctx=_ctx(ctx),
        )
        assert result == 0

        data = json.loads(ctx.outputs[0][0])
        kinds = {r["kind"] for r in data["manifests"]}
        assert "Deployment" in kinds
        assert "StatefulSet" not in kinds

    def test_manifest_custom_namespace(self) -> None:
        """Manifest uses custom namespace."""
        ctx = MockContext()
        result = _handle_manifest(
            "Kappa",
            namespace="production",
            json_mode=True,
            validate_mode=False,
            ctx=_ctx(ctx),
        )
        assert result == 0

        data = json.loads(ctx.outputs[0][0])
        namespaces = {r["metadata"]["namespace"] for r in data["manifests"]}
        assert "production" in namespaces

    def test_manifest_nonexistent_returns_error(self) -> None:
        """Manifest for non-existent agent returns error."""
        ctx = MockContext()
        result = _handle_manifest(
            "NonExistent",
            namespace="test",
            json_mode=False,
            validate_mode=False,
            ctx=_ctx(ctx),
        )
        assert result == 1

    def test_manifest_with_validate_flag(self) -> None:
        """Manifest with --validate validates and reports success."""
        ctx = MockContext()
        result = _handle_manifest(
            "Kappa",
            namespace="test",
            json_mode=False,
            validate_mode=True,
            ctx=_ctx(ctx),
        )
        assert result == 0
        output = ctx.outputs[0][0]
        assert "valid" in output.lower()

    def test_manifest_validate_json_includes_valid_field(self) -> None:
        """Manifest with --validate --json includes 'valid' field."""
        ctx = MockContext()
        result = _handle_manifest(
            "Kappa", namespace="test", json_mode=True, validate_mode=True, ctx=_ctx(ctx)
        )
        assert result == 0

        data = json.loads(ctx.outputs[0][0])
        assert data["valid"] is True
        assert "manifests" in data
        assert "message" in data


# ===========================================================================
# Test: Run Command
# ===========================================================================


class TestRunCommand:
    """Tests for 'a run' command.

    Note: Archetypes (Kappa, Lambda, Delta) are abstract base classes
    and cannot be instantiated directly. Run tests use concrete subclasses.
    """

    @pytest.mark.anyio
    async def test_run_abstract_archetype_fails(self) -> None:
        """Running abstract archetype returns helpful error."""
        ctx = MockContext()
        result = await _handle_run(
            "Kappa", input_data=None, json_mode=False, ctx=_ctx(ctx)
        )
        # Abstract archetypes can't be run directly
        assert result == 1
        output = ctx.outputs[0][0]
        assert "abstract archetype" in output.lower()
        assert "subclass" in output.lower()
        assert "Example" in output

    @pytest.mark.anyio
    async def test_run_nonexistent_returns_error(self) -> None:
        """Run non-existent agent returns error."""
        ctx = MockContext()
        result = await _handle_run(
            "NonExistent", input_data=None, json_mode=False, ctx=_ctx(ctx)
        )
        assert result == 1


# ===========================================================================
# Test: List Command
# ===========================================================================


class TestListCommand:
    """Tests for 'a list' command."""

    def test_list_shows_archetypes(self) -> None:
        """List shows available archetypes."""
        ctx = MockContext()
        result = _handle_list(json_mode=False, ctx=_ctx(ctx))
        assert result == 0

        output = ctx.outputs[0][0]
        assert "Kappa" in output
        assert "Lambda" in output
        assert "Delta" in output

    def test_list_json(self) -> None:
        """List in JSON mode produces valid JSON."""
        ctx = MockContext()
        result = _handle_list(json_mode=True, ctx=_ctx(ctx))
        assert result == 0

        data = json.loads(ctx.outputs[0][0])
        assert "archetypes" in data
        assert len(data["archetypes"]) == 3

        names = {a["name"] for a in data["archetypes"]}
        assert "Kappa" in names
        assert "Lambda" in names
        assert "Delta" in names


# ===========================================================================
# Test: Integration via cmd_a
# ===========================================================================


class TestIntegration:
    """Integration tests using cmd_a directly."""

    def test_a_inspect_via_cmd(self) -> None:
        """'a inspect Kappa' via cmd_a."""
        ctx = MockContext()
        result = cmd_a(["inspect", "Kappa"], _ctx(ctx))
        assert result == 0
        assert any("Kappa" in o[0] for o in ctx.outputs)

    def test_a_manifest_via_cmd(self) -> None:
        """'a manifest Kappa' via cmd_a."""
        ctx = MockContext()
        result = cmd_a(["manifest", "Kappa"], _ctx(ctx))
        assert result == 0

    def test_a_list_via_cmd(self) -> None:
        """'a list' via cmd_a."""
        ctx = MockContext()
        result = cmd_a(["list"], _ctx(ctx))
        assert result == 0

    def test_a_inspect_json_flag(self) -> None:
        """'a inspect Kappa --json' uses JSON mode."""
        ctx = MockContext()
        result = cmd_a(["inspect", "Kappa", "--json"], _ctx(ctx))
        assert result == 0

        # Should be valid JSON
        output = ctx.outputs[0][0]
        data = json.loads(output)
        assert data["agent"] == "Kappa"

    def test_a_manifest_custom_namespace(self) -> None:
        """'a manifest Kappa --namespace prod' uses custom namespace."""
        ctx = MockContext()
        result = cmd_a(
            ["manifest", "Kappa", "--namespace", "prod", "--json"], _ctx(ctx)
        )
        assert result == 0

        data = json.loads(ctx.outputs[0][0])
        namespaces = {r["metadata"]["namespace"] for r in data["manifests"]}
        assert "prod" in namespaces
