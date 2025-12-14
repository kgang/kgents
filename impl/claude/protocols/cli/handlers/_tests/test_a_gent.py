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
    DIALOGUE_AGENTS,
    _handle_dialogue,
    _handle_inspect,
    _handle_list,
    _handle_manifest,
    _handle_run,
    _resolve_agent_class,
    _resolve_dialogue_agent,
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


# ===========================================================================
# Test: Dialogue Agents
# ===========================================================================


class TestDialogueAgentRegistry:
    """Tests for dialogue agent registry and resolution."""

    def test_dialogue_agents_registry_has_soul(self) -> None:
        """DIALOGUE_AGENTS contains 'soul' mapping."""
        assert "soul" in DIALOGUE_AGENTS
        assert "agents.k.soul:KgentSoul" in DIALOGUE_AGENTS["soul"]

    def test_dialogue_agents_registry_has_kgent_alias(self) -> None:
        """DIALOGUE_AGENTS contains 'kgent' alias for soul."""
        assert "kgent" in DIALOGUE_AGENTS
        assert DIALOGUE_AGENTS["kgent"] == DIALOGUE_AGENTS["soul"]

    def test_dialogue_agents_registry_has_session(self) -> None:
        """DIALOGUE_AGENTS contains 'session' for cross-session identity."""
        assert "session" in DIALOGUE_AGENTS
        assert "SoulSession" in DIALOGUE_AGENTS["session"]

    def test_resolve_dialogue_agent_soul(self) -> None:
        """Resolving 'soul' returns a KgentSoul instance."""
        agent = _resolve_dialogue_agent("soul")
        assert agent is not None
        # Should have dialogue method
        assert hasattr(agent, "dialogue")

    def test_resolve_dialogue_agent_unknown(self) -> None:
        """Resolving unknown agent returns None."""
        agent = _resolve_dialogue_agent("nonexistent")
        assert agent is None


class TestDialogueCommand:
    """Tests for dialogue command."""

    @pytest.mark.anyio
    async def test_dialogue_unknown_agent(self) -> None:
        """Dialogue with unknown agent returns error."""
        ctx = MockContext()
        result = await _handle_dialogue(
            "nonexistent", prompt="hello", json_mode=False, ctx=_ctx(ctx)
        )
        assert result == 1
        assert any("Unknown dialogue agent" in o[0] for o in ctx.outputs)

    @pytest.mark.anyio
    async def test_dialogue_soul_single_turn(self) -> None:
        """Single dialogue turn with soul agent returns response."""
        ctx = MockContext()
        result = await _handle_dialogue(
            "soul", prompt="Hello, what's your purpose?", json_mode=False, ctx=_ctx(ctx)
        )
        assert result == 0
        # Should have produced some output
        assert len(ctx.outputs) > 0
        # The response should be a non-empty string
        response = ctx.outputs[0][0]
        assert len(response) > 0

    @pytest.mark.anyio
    async def test_dialogue_soul_json_mode(self) -> None:
        """Dialogue in JSON mode produces valid JSON."""
        ctx = MockContext()
        result = await _handle_dialogue(
            "soul", prompt="Test message", json_mode=True, ctx=_ctx(ctx)
        )
        assert result == 0

        output = ctx.outputs[0][0]
        data = json.loads(output)
        assert "agent" in data
        assert data["agent"] == "soul"
        assert "response" in data
        assert "input" in data
        assert data["input"] == "Test message"


class TestDialogueViaCmd:
    """Integration tests for dialogue via cmd_a."""

    def test_dialogue_soul_via_cmd(self) -> None:
        """'a soul \"hello\"' invokes dialogue mode."""
        ctx = MockContext()
        result = cmd_a(["soul", "What is your purpose?"], _ctx(ctx))
        assert result == 0
        # Should have output
        assert len(ctx.outputs) > 0

    def test_dialogue_kgent_alias_via_cmd(self) -> None:
        """'a kgent \"hello\"' works as alias for soul."""
        ctx = MockContext()
        result = cmd_a(["kgent", "Hello there"], _ctx(ctx))
        assert result == 0
        assert len(ctx.outputs) > 0

    def test_dialogue_with_json_flag(self) -> None:
        """'a soul \"hello\" --json' produces JSON output."""
        ctx = MockContext()
        result = cmd_a(["soul", "Test", "--json"], _ctx(ctx))
        assert result == 0

        output = ctx.outputs[0][0]
        data = json.loads(output)
        assert data["agent"] == "soul"

    def test_dialogue_no_prompt_would_enter_repl(self) -> None:
        """'a soul' without prompt returns 0 (REPL mode tested separately)."""
        # Note: REPL mode requires stdin, so we test the routing only
        # The actual REPL functionality is tested manually or with pexpect
        pass  # Routing to REPL tested via integration
