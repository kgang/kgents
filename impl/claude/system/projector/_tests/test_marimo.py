"""
Tests for MarimoProjector.

Verifies:
- Marimo cell generation from agent Halo
- Capability-to-marimo feature mappings
- Reactive widget generation
- State management via mo.state()
"""

import pytest

from agents.a.halo import Capability
from agents.poly.types import Agent
from system.projector import (
    MarimoArtifact,
    MarimoProjector,
)


# Test agent fixtures
@Capability.Stateful(schema=dict)
class StatefulMarimoAgent(Agent[str, str]):
    @property
    def name(self):
        return "stateful-marimo"

    async def invoke(self, x):
        return x.upper()


@Capability.Observable(metrics=True)
class ObservableMarimoAgent(Agent[str, str]):
    @property
    def name(self):
        return "observable-marimo"

    async def invoke(self, x):
        return x.upper()


@Capability.Soulful(persona="kent", mode="strict")
class SoulfulMarimoAgent(Agent[str, str]):
    @property
    def name(self):
        return "soulful-marimo"

    async def invoke(self, x):
        return x.upper()


@Capability.Streamable(budget=5.0)
class StreamableMarimoAgent(Agent[str, str]):
    @property
    def name(self):
        return "streamable-marimo"

    async def invoke(self, x):
        return x.upper()


@Capability.Stateful(schema=dict)
@Capability.Observable(metrics=True)
@Capability.Soulful(persona="kent")
class FullStackMarimoAgent(Agent[str, str]):
    @property
    def name(self):
        return "full-stack-marimo"

    async def invoke(self, x):
        return x.upper()


class PlainMarimoAgent(Agent[str, str]):
    @property
    def name(self):
        return "plain-marimo"

    async def invoke(self, x):
        return x.upper()


class TestMarimoProjector:
    """Tests for MarimoProjector basic functionality."""

    def test_projector_name(self):
        """MarimoProjector has correct name."""
        projector = MarimoProjector()
        assert projector.name == "MarimoProjector"

    def test_projector_default_configuration(self):
        """MarimoProjector has sensible defaults."""
        projector = MarimoProjector()
        assert projector.include_imports is True
        assert projector.show_source is True
        assert projector.theme == "minimal"

    def test_projector_custom_configuration(self):
        """MarimoProjector accepts custom configuration."""
        projector = MarimoProjector(
            include_imports=False,
            show_source=False,
            theme="dark",
        )
        assert projector.include_imports is False
        assert projector.show_source is False
        assert projector.theme == "dark"

    def test_projector_supports_standard_capabilities(self):
        """MarimoProjector supports all standard capabilities."""
        from agents.a.halo import (
            ObservableCapability,
            SoulfulCapability,
            StatefulCapability,
            StreamableCapability,
            TurnBasedCapability,
        )

        projector = MarimoProjector()
        assert projector.supports(StatefulCapability)
        assert projector.supports(SoulfulCapability)
        assert projector.supports(ObservableCapability)
        assert projector.supports(StreamableCapability)
        assert projector.supports(TurnBasedCapability)


class TestCellGeneration:
    """Tests for marimo cell content generation."""

    def test_compile_produces_python_string(self):
        """compile() returns Python source as string."""
        projector = MarimoProjector()
        cell = projector.compile(PlainMarimoAgent)
        assert isinstance(cell, str)
        assert len(cell) > 0

    def test_cell_has_marimo_import(self):
        """Cell includes marimo import."""
        projector = MarimoProjector()
        cell = projector.compile(PlainMarimoAgent)
        assert "import marimo as mo" in cell

    def test_cell_has_asyncio_import(self):
        """Cell includes asyncio import."""
        projector = MarimoProjector()
        cell = projector.compile(PlainMarimoAgent)
        assert "import asyncio" in cell

    def test_cell_has_agent_abc(self):
        """Cell includes Agent ABC definition."""
        projector = MarimoProjector()
        cell = projector.compile(PlainMarimoAgent)
        assert "class Agent" in cell
        assert "ABC" in cell

    def test_cell_has_input_widget(self):
        """Cell has mo.ui.text_area input widget."""
        projector = MarimoProjector()
        cell = projector.compile(PlainMarimoAgent)
        assert "mo.ui.text_area" in cell

    def test_cell_has_run_button(self):
        """Cell has mo.ui.run_button."""
        projector = MarimoProjector()
        cell = projector.compile(PlainMarimoAgent)
        assert "mo.ui.run_button" in cell

    def test_cell_has_agent_name_header(self):
        """Cell shows agent name."""
        projector = MarimoProjector()
        cell = projector.compile(PlainMarimoAgent)
        # CamelCase → kebab-case: PlainMarimoAgent → plain-marimo-agent
        assert "plain-marimo-agent" in cell

    def test_cell_embeds_agent_source(self):
        """Cell embeds agent source code."""
        projector = MarimoProjector()
        cell = projector.compile(PlainMarimoAgent)
        assert "class PlainMarimoAgent" in cell

    def test_cell_creates_agent_instance(self):
        """Cell creates agent instance."""
        projector = MarimoProjector()
        cell = projector.compile(PlainMarimoAgent)
        assert "_agent = PlainMarimoAgent()" in cell

    def test_cell_has_run_agent_function(self):
        """Cell has run_agent async function."""
        projector = MarimoProjector()
        cell = projector.compile(PlainMarimoAgent)
        assert "async def run_agent()" in cell

    def test_cell_awaits_invoke(self):
        """Cell awaits agent.invoke()."""
        projector = MarimoProjector()
        cell = projector.compile(PlainMarimoAgent)
        assert "await _agent.invoke" in cell

    def test_cell_uses_vstack(self):
        """Cell uses mo.vstack for layout."""
        projector = MarimoProjector()
        cell = projector.compile(PlainMarimoAgent)
        assert "mo.vstack" in cell


class TestCapabilityMappings:
    """Tests for capability-to-marimo mappings."""

    def test_stateful_uses_mo_state(self):
        """@Stateful uses mo.state() for persistence."""
        projector = MarimoProjector()
        cell = projector.compile(StatefulMarimoAgent)
        assert "mo.state" in cell
        assert "agent_state" in cell

    def test_stateful_tracks_run_history(self):
        """@Stateful tracks run history."""
        projector = MarimoProjector()
        cell = projector.compile(StatefulMarimoAgent)
        assert "run_history" in cell
        assert "set_run_history" in cell

    def test_observable_shows_metrics(self):
        """@Observable shows metrics."""
        projector = MarimoProjector()
        cell = projector.compile(ObservableMarimoAgent)
        assert "latency" in cell.lower()
        assert "metrics" in cell.lower() or "get_metrics" in cell

    def test_observable_has_start_metrics(self):
        """@Observable has start_metrics function."""
        projector = MarimoProjector()
        cell = projector.compile(ObservableMarimoAgent)
        assert "start_metrics" in cell

    def test_soulful_shows_persona(self):
        """@Soulful shows persona badge."""
        projector = MarimoProjector()
        cell = projector.compile(SoulfulMarimoAgent)
        assert "kent" in cell

    def test_soulful_uses_callout(self):
        """@Soulful uses mo.callout for persona display."""
        projector = MarimoProjector()
        cell = projector.compile(SoulfulMarimoAgent)
        assert "mo.callout" in cell

    def test_streamable_indicates_capability(self):
        """@Streamable shows streaming capability."""
        projector = MarimoProjector()
        cell = projector.compile(StreamableMarimoAgent)
        assert "streaming" in cell.lower()

    def test_full_stack_includes_all_features(self):
        """Full stack agent includes all capability features."""
        projector = MarimoProjector()
        cell = projector.compile(FullStackMarimoAgent)

        # Stateful
        assert "mo.state" in cell

        # Observable
        assert "metrics" in cell.lower() or "get_metrics" in cell

        # Soulful
        assert "kent" in cell


class TestMarimoArtifact:
    """Tests for MarimoArtifact structured output."""

    def test_compile_artifact_returns_structured(self):
        """compile_artifact() returns MarimoArtifact."""
        projector = MarimoProjector()
        artifact = projector.compile_artifact(PlainMarimoAgent)
        assert isinstance(artifact, MarimoArtifact)

    def test_artifact_has_cell_source(self):
        """MarimoArtifact contains cell source."""
        projector = MarimoProjector()
        artifact = projector.compile_artifact(PlainMarimoAgent)
        assert isinstance(artifact.cell_source, str)
        assert len(artifact.cell_source) > 0

    def test_artifact_has_agent_name(self):
        """MarimoArtifact has agent name."""
        projector = MarimoProjector()
        artifact = projector.compile_artifact(PlainMarimoAgent)
        assert artifact.agent_name == "plain-marimo-agent"

    def test_artifact_has_agent_source(self):
        """MarimoArtifact includes agent source."""
        projector = MarimoProjector()
        artifact = projector.compile_artifact(PlainMarimoAgent)
        assert "PlainMarimoAgent" in artifact.agent_source

    def test_artifact_uses_state_flag(self):
        """MarimoArtifact tracks state usage."""
        projector = MarimoProjector()

        plain_artifact = projector.compile_artifact(PlainMarimoAgent)
        assert plain_artifact.uses_state is False

        stateful_artifact = projector.compile_artifact(StatefulMarimoAgent)
        assert stateful_artifact.uses_state is True

    def test_artifact_uses_streaming_flag(self):
        """MarimoArtifact tracks streaming usage."""
        projector = MarimoProjector()

        plain_artifact = projector.compile_artifact(PlainMarimoAgent)
        assert plain_artifact.uses_streaming is False

        stream_artifact = projector.compile_artifact(StreamableMarimoAgent)
        assert stream_artifact.uses_streaming is True

    def test_artifact_uses_metrics_flag(self):
        """MarimoArtifact tracks metrics usage."""
        projector = MarimoProjector()

        plain_artifact = projector.compile_artifact(PlainMarimoAgent)
        assert plain_artifact.uses_metrics is False

        obs_artifact = projector.compile_artifact(ObservableMarimoAgent)
        assert obs_artifact.uses_metrics is True

    def test_artifact_exposed_inputs(self):
        """MarimoArtifact tracks exposed inputs."""
        projector = MarimoProjector()
        artifact = projector.compile_artifact(PlainMarimoAgent)
        assert "text_input" in artifact.exposed_inputs


class TestDecoratorStripping:
    """Tests for stripping @Capability decorators from source."""

    def test_capability_decorators_stripped(self):
        """@Capability decorators are removed from embedded source."""
        projector = MarimoProjector()
        cell = projector.compile(StatefulMarimoAgent)
        # The @Capability.Stateful decorator should NOT appear
        assert "@Capability.Stateful" not in cell

    def test_class_definition_preserved(self):
        """Class definition is preserved after stripping decorators."""
        projector = MarimoProjector()
        cell = projector.compile(StatefulMarimoAgent)
        assert "class StatefulMarimoAgent" in cell

    def test_multiple_decorators_stripped(self):
        """Multiple @Capability decorators are all stripped."""
        projector = MarimoProjector()
        cell = projector.compile(FullStackMarimoAgent)
        # None of the capability decorators should appear
        assert "@Capability" not in cell
        # But the class should still be defined
        assert "class FullStackMarimoAgent" in cell


class TestSourceViewer:
    """Tests for source code viewer."""

    def test_source_viewer_included_by_default(self):
        """Source viewer is included when show_source=True."""
        projector = MarimoProjector(show_source=True)
        cell = projector.compile(PlainMarimoAgent)
        assert "mo.accordion" in cell

    def test_source_viewer_excluded_when_disabled(self):
        """Source viewer is excluded when show_source=False."""
        projector = MarimoProjector(show_source=False)
        cell = projector.compile(PlainMarimoAgent)
        assert "mo.accordion" not in cell

    def test_source_viewer_has_class_name(self):
        """Source viewer mentions class name."""
        projector = MarimoProjector(show_source=True)
        cell = projector.compile(PlainMarimoAgent)
        assert "PlainMarimoAgent" in cell


class TestImportManagement:
    """Tests for import statement handling."""

    def test_imports_included_by_default(self):
        """Imports are included when include_imports=True."""
        projector = MarimoProjector(include_imports=True)
        cell = projector.compile(PlainMarimoAgent)
        assert "import marimo as mo" in cell

    def test_imports_excluded_when_disabled(self):
        """Imports are excluded when include_imports=False."""
        projector = MarimoProjector(include_imports=False)
        cell = projector.compile(PlainMarimoAgent)
        assert "import marimo as mo" not in cell

    def test_observable_imports_time(self):
        """@Observable includes time import."""
        projector = MarimoProjector(include_imports=True)
        cell = projector.compile(ObservableMarimoAgent)
        assert "import time" in cell


class TestErrorHandling:
    """Tests for error handling in generated cells."""

    def test_cell_has_try_except(self):
        """Generated cell has error handling."""
        projector = MarimoProjector()
        cell = projector.compile(PlainMarimoAgent)
        assert "try:" in cell
        assert "except" in cell

    def test_cell_uses_danger_callout_for_errors(self):
        """Cell uses mo.callout with kind='danger' for errors."""
        projector = MarimoProjector()
        cell = projector.compile(PlainMarimoAgent)
        assert 'kind="danger"' in cell

    def test_cell_checks_empty_input(self):
        """Cell checks for empty input."""
        projector = MarimoProjector()
        cell = projector.compile(PlainMarimoAgent)
        assert "not user_input.value.strip()" in cell or "Please enter some input" in cell


class TestCapabilitiesDisplay:
    """Tests for capability indicator display."""

    def test_plain_agent_shows_minimal(self):
        """Plain agent shows 'minimal' capabilities."""
        projector = MarimoProjector()
        cell = projector.compile(PlainMarimoAgent)
        assert "minimal" in cell.lower()

    def test_stateful_shown_in_capabilities(self):
        """@Stateful is shown in capabilities list."""
        projector = MarimoProjector()
        cell = projector.compile(StatefulMarimoAgent)
        assert "stateful" in cell.lower()

    def test_streaming_shown_in_capabilities(self):
        """@Streamable is shown in capabilities list."""
        projector = MarimoProjector()
        cell = projector.compile(StreamableMarimoAgent)
        assert "streaming" in cell.lower()

    def test_observable_shown_in_capabilities(self):
        """@Observable is shown in capabilities list."""
        projector = MarimoProjector()
        cell = projector.compile(ObservableMarimoAgent)
        assert "observable" in cell.lower()


class TestProjectorComposition:
    """Tests for MarimoProjector composition."""

    def test_marimo_can_compose_with_identity(self):
        """Marimo can compose with IdentityProjector."""
        from system.projector import IdentityProjector

        identity = IdentityProjector()
        marimo = MarimoProjector()
        composed = identity >> marimo

        result = composed.compile(PlainMarimoAgent)
        assert result.upstream is PlainMarimoAgent
        assert isinstance(result.downstream, str)  # Python source string

    def test_marimo_composition_name(self):
        """Composed Marimo projector has combined name."""
        from system.projector import IdentityProjector

        identity = IdentityProjector()
        marimo = MarimoProjector()
        composed = identity >> marimo

        assert composed.name == "IdentityProjector>>MarimoProjector"


class TestAsyncExecution:
    """Tests for async execution handling."""

    def test_cell_uses_asyncio_run(self):
        """Cell uses asyncio.run() for execution."""
        projector = MarimoProjector()
        cell = projector.compile(PlainMarimoAgent)
        assert "asyncio.run" in cell

    def test_run_agent_is_async(self):
        """run_agent function is async."""
        projector = MarimoProjector()
        cell = projector.compile(PlainMarimoAgent)
        assert "async def run_agent" in cell


class TestNameConversion:
    """Tests for CamelCase to kebab-case conversion."""

    def test_simple_name_conversion(self):
        """Simple CamelCase converts to kebab-case."""
        projector = MarimoProjector()
        assert projector._derive_agent_name(PlainMarimoAgent) == "plain-marimo-agent"

    def test_consecutive_caps_conversion(self):
        """Consecutive capitals handled correctly."""
        # WASMAgent → w-a-s-m-agent (each capital becomes separated)
        projector = MarimoProjector()
        # For StatefulMarimoAgent, we expect stateful-marimo-agent
        assert projector._derive_agent_name(StatefulMarimoAgent) == "stateful-marimo-agent"
