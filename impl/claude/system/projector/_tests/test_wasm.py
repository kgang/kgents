"""
Tests for WASMProjector.

Verifies:
- HTML bundle generation from agent Halo
- Capability-to-WASM feature mappings
- Pyodide bootstrap code
- Sandbox indicator presence
"""

import pytest

from agents.a.halo import Capability
from agents.poly.types import Agent
from system.projector import (
    WASMArtifact,
    WASMProjector,
)


# Test agent fixtures
@Capability.Stateful(schema=dict)
class StatefulWASMAgent(Agent[str, str]):
    @property
    def name(self):
        return "stateful-wasm"

    async def invoke(self, x):
        return x.upper()


@Capability.Observable(metrics=True)
class ObservableWASMAgent(Agent[str, str]):
    @property
    def name(self):
        return "observable-wasm"

    async def invoke(self, x):
        return x.upper()


@Capability.Soulful(persona="kent", mode="strict")
class SoulfulWASMAgent(Agent[str, str]):
    @property
    def name(self):
        return "soulful-wasm"

    async def invoke(self, x):
        return x.upper()


@Capability.Streamable(budget=5.0)
class StreamableWASMAgent(Agent[str, str]):
    @property
    def name(self):
        return "streamable-wasm"

    async def invoke(self, x):
        return x.upper()


@Capability.Stateful(schema=dict)
@Capability.Observable(metrics=True)
@Capability.Soulful(persona="kent")
class FullStackWASMAgent(Agent[str, str]):
    @property
    def name(self):
        return "full-stack-wasm"

    async def invoke(self, x):
        return x.upper()


class PlainWASMAgent(Agent[str, str]):
    @property
    def name(self):
        return "plain-wasm"

    async def invoke(self, x):
        return x.upper()


class TestWASMProjector:
    """Tests for WASMProjector basic functionality."""

    def test_projector_name(self):
        """WASMProjector has correct name."""
        projector = WASMProjector()
        assert projector.name == "WASMProjector"

    def test_projector_default_configuration(self):
        """WASMProjector has sensible defaults."""
        projector = WASMProjector()
        assert projector.pyodide_version == "0.24.1"
        assert projector.theme == "minimal"
        assert projector.title_prefix == "kgents sandbox"

    def test_projector_custom_configuration(self):
        """WASMProjector accepts custom configuration."""
        projector = WASMProjector(
            pyodide_version="0.25.0",
            theme="dark",
            title_prefix="custom sandbox",
        )
        assert projector.pyodide_version == "0.25.0"
        assert projector.theme == "dark"
        assert projector.title_prefix == "custom sandbox"

    def test_projector_supports_standard_capabilities(self):
        """WASMProjector supports all standard capabilities."""
        from agents.a.halo import (
            ObservableCapability,
            SoulfulCapability,
            StatefulCapability,
            StreamableCapability,
            TurnBasedCapability,
        )

        projector = WASMProjector()
        assert projector.supports(StatefulCapability)
        assert projector.supports(SoulfulCapability)
        assert projector.supports(ObservableCapability)
        assert projector.supports(StreamableCapability)
        assert projector.supports(TurnBasedCapability)


class TestHTMLGeneration:
    """Tests for HTML bundle content generation."""

    def test_compile_produces_html_string(self):
        """compile() returns HTML as string."""
        projector = WASMProjector()
        html = projector.compile(PlainWASMAgent)
        assert isinstance(html, str)
        assert len(html) > 0

    def test_html_has_doctype(self):
        """HTML includes DOCTYPE declaration."""
        projector = WASMProjector()
        html = projector.compile(PlainWASMAgent)
        assert "<!DOCTYPE html>" in html

    def test_html_has_pyodide_script(self):
        """HTML includes Pyodide CDN script."""
        projector = WASMProjector()
        html = projector.compile(PlainWASMAgent)
        assert "pyodide.js" in html
        assert "cdn.jsdelivr.net/pyodide" in html

    def test_html_has_sandbox_indicator(self):
        """HTML shows SANDBOXED badge."""
        projector = WASMProjector()
        html = projector.compile(PlainWASMAgent)
        assert "SANDBOXED" in html

    def test_html_has_input_textarea(self):
        """HTML has input textarea."""
        projector = WASMProjector()
        html = projector.compile(PlainWASMAgent)
        assert '<textarea id="input"' in html

    def test_html_has_output_div(self):
        """HTML has output div."""
        projector = WASMProjector()
        html = projector.compile(PlainWASMAgent)
        assert '<div id="output"' in html

    def test_html_has_run_button(self):
        """HTML has run button."""
        projector = WASMProjector()
        html = projector.compile(PlainWASMAgent)
        assert 'id="run-btn"' in html

    def test_html_has_agent_title(self):
        """HTML shows agent name in title."""
        projector = WASMProjector()
        html = projector.compile(PlainWASMAgent)
        # CamelCase → kebab-case: PlainWASMAgent → plain-w-a-s-m-agent
        assert "plain-w-a-s-m-agent" in html

    def test_html_embeds_agent_source(self):
        """HTML embeds agent source code."""
        projector = WASMProjector()
        html = projector.compile(PlainWASMAgent)
        # Should have the class definition
        assert "class PlainWASMAgent" in html or "PlainWASMAgent" in html

    def test_html_has_loadPyodide_call(self):
        """HTML calls loadPyodide()."""
        projector = WASMProjector()
        html = projector.compile(PlainWASMAgent)
        assert "loadPyodide" in html

    def test_html_has_runPythonAsync(self):
        """HTML uses runPythonAsync for execution."""
        projector = WASMProjector()
        html = projector.compile(PlainWASMAgent)
        assert "runPythonAsync" in html


class TestCapabilityMappings:
    """Tests for capability-to-WASM mappings."""

    def test_stateful_includes_indexeddb(self):
        """@Stateful includes IndexedDB/localStorage persistence."""
        projector = WASMProjector()
        html = projector.compile(StatefulWASMAgent)
        # Should have storage code
        assert "localStorage" in html or "indexedDB" in html

    def test_observable_shows_metrics(self):
        """@Observable with metrics=True shows metrics panel."""
        projector = WASMProjector()
        html = projector.compile(ObservableWASMAgent)
        assert 'id="metrics"' in html
        assert "latency" in html.lower()

    def test_soulful_shows_persona_badge(self):
        """@Soulful shows persona badge."""
        projector = WASMProjector()
        html = projector.compile(SoulfulWASMAgent)
        assert "kent" in html

    def test_streamable_indicates_capability(self):
        """@Streamable shows streaming capability."""
        projector = WASMProjector()
        html = projector.compile(StreamableWASMAgent)
        # Capability indicator in footer
        assert "streaming" in html.lower()

    def test_full_stack_includes_all_features(self):
        """Full stack agent includes all capability features."""
        projector = WASMProjector()
        html = projector.compile(FullStackWASMAgent)

        # Stateful
        assert "localStorage" in html or "indexedDB" in html

        # Observable
        assert 'id="metrics"' in html

        # Soulful
        assert "kent" in html


class TestWASMArtifact:
    """Tests for WASMArtifact structured output."""

    def test_compile_artifact_returns_structured(self):
        """compile_artifact() returns WASMArtifact."""
        projector = WASMProjector()
        artifact = projector.compile_artifact(PlainWASMAgent)
        assert isinstance(artifact, WASMArtifact)

    def test_artifact_has_html(self):
        """WASMArtifact contains HTML content."""
        projector = WASMProjector()
        artifact = projector.compile_artifact(PlainWASMAgent)
        assert isinstance(artifact.html, str)
        assert len(artifact.html) > 0

    def test_artifact_has_agent_name(self):
        """WASMArtifact has agent name."""
        projector = WASMProjector()
        artifact = projector.compile_artifact(PlainWASMAgent)
        # CamelCase → kebab-case: PlainWASMAgent → plain-w-a-s-m-agent
        assert artifact.agent_name == "plain-w-a-s-m-agent"

    def test_artifact_has_agent_source(self):
        """WASMArtifact includes agent source."""
        projector = WASMProjector()
        artifact = projector.compile_artifact(PlainWASMAgent)
        assert "PlainWASMAgent" in artifact.agent_source or len(artifact.agent_source) > 0

    def test_artifact_uses_indexeddb_flag(self):
        """WASMArtifact tracks IndexedDB usage."""
        projector = WASMProjector()

        plain_artifact = projector.compile_artifact(PlainWASMAgent)
        assert plain_artifact.uses_indexeddb is False

        stateful_artifact = projector.compile_artifact(StatefulWASMAgent)
        assert stateful_artifact.uses_indexeddb is True

    def test_artifact_uses_streaming_flag(self):
        """WASMArtifact tracks streaming usage."""
        projector = WASMProjector()

        plain_artifact = projector.compile_artifact(PlainWASMAgent)
        assert plain_artifact.uses_streaming is False

        stream_artifact = projector.compile_artifact(StreamableWASMAgent)
        assert stream_artifact.uses_streaming is True

    def test_artifact_exposed_functions(self):
        """WASMArtifact tracks exposed functions."""
        projector = WASMProjector()
        artifact = projector.compile_artifact(PlainWASMAgent)
        assert "invoke" in artifact.exposed_functions


class TestDecoratorStripping:
    """Tests for stripping @Capability decorators from source."""

    def test_capability_decorators_stripped(self):
        """@Capability decorators are removed from embedded source."""
        projector = WASMProjector()
        html = projector.compile(StatefulWASMAgent)
        # The @Capability.Stateful decorator should NOT appear in the output
        assert "@Capability.Stateful" not in html

    def test_class_definition_preserved(self):
        """Class definition is preserved after stripping decorators."""
        projector = WASMProjector()
        html = projector.compile(StatefulWASMAgent)
        # The class definition should still be there
        assert "class StatefulWASMAgent" in html

    def test_multiple_decorators_stripped(self):
        """Multiple @Capability decorators are all stripped."""
        projector = WASMProjector()
        html = projector.compile(FullStackWASMAgent)
        # None of the capability decorators should appear
        assert "@Capability" not in html
        # But the class should still be defined
        assert "class FullStackWASMAgent" in html


class TestPyodideRuntime:
    """Tests for Pyodide runtime code generation."""

    def test_runtime_has_agent_abc(self):
        """Runtime includes Agent ABC definition."""
        projector = WASMProjector()
        html = projector.compile(PlainWASMAgent)
        assert "class Agent" in html
        assert "ABC" in html

    def test_runtime_creates_agent_instance(self):
        """Runtime creates agent instance."""
        projector = WASMProjector()
        html = projector.compile(PlainWASMAgent)
        # Should create _agent instance
        assert "_agent = " in html

    def test_runtime_has_run_agent_function(self):
        """Runtime has run_agent async function."""
        projector = WASMProjector()
        html = projector.compile(PlainWASMAgent)
        assert "async def run_agent" in html

    def test_runtime_awaits_invoke(self):
        """Runtime awaits agent.invoke()."""
        projector = WASMProjector()
        html = projector.compile(PlainWASMAgent)
        assert "await _agent.invoke" in html


class TestSandboxSecurity:
    """Tests for sandbox security indicators."""

    def test_sandbox_badge_present(self):
        """Sandbox badge is prominently displayed."""
        projector = WASMProjector()
        html = projector.compile(PlainWASMAgent)
        assert "sandbox-indicator" in html
        assert "SANDBOXED" in html

    def test_no_filesystem_access(self):
        """Generated code doesn't use Node.js filesystem APIs."""
        projector = WASMProjector()
        html = projector.compile(PlainWASMAgent)
        # No Node.js filesystem calls
        assert "require('fs')" not in html
        assert "import fs" not in html.lower()

    def test_pyodide_version_specified(self):
        """Pyodide version is explicitly specified."""
        projector = WASMProjector()
        html = projector.compile(PlainWASMAgent)
        assert "0.24.1" in html


class TestUIFeatures:
    """Tests for UI functionality."""

    def test_ctrl_enter_shortcut(self):
        """Ctrl+Enter shortcut is wired up."""
        projector = WASMProjector()
        html = projector.compile(PlainWASMAgent)
        assert "ctrlKey" in html
        assert "Enter" in html

    def test_clear_button_exists(self):
        """Clear button is present."""
        projector = WASMProjector()
        html = projector.compile(PlainWASMAgent)
        assert 'id="clear-btn"' in html

    def test_loading_status_message(self):
        """Loading status message is shown."""
        projector = WASMProjector()
        html = projector.compile(PlainWASMAgent)
        assert "Loading" in html or "loading" in html

    def test_ready_status_class(self):
        """Ready status uses correct class."""
        projector = WASMProjector()
        html = projector.compile(PlainWASMAgent)
        assert "status ready" in html or "'status ready'" in html

    def test_error_status_class(self):
        """Error status uses correct class."""
        projector = WASMProjector()
        html = projector.compile(PlainWASMAgent)
        assert "status error" in html or "'status error'" in html


class TestProjectorComposition:
    """Tests for WASMProjector composition."""

    def test_wasm_can_compose_with_identity(self):
        """WASM can compose with IdentityProjector."""
        from system.projector import IdentityProjector

        identity = IdentityProjector()
        wasm = WASMProjector()
        composed = identity >> wasm

        result = composed.compile(PlainWASMAgent)
        assert result.upstream is PlainWASMAgent
        assert isinstance(result.downstream, str)  # HTML string

    def test_wasm_composition_name(self):
        """Composed WASM projector has combined name."""
        from system.projector import IdentityProjector

        identity = IdentityProjector()
        wasm = WASMProjector()
        composed = identity >> wasm

        assert composed.name == "IdentityProjector>>WASMProjector"
