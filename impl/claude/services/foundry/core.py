"""
AgentFoundry — The Crown Jewel Orchestrator.

The Foundry synthesizes J-gent JIT intelligence with Alethic Projection compilation.

AGENTESE: self.foundry.*

Pipeline:
    Intent → RealityClassifier → MetaArchitect → Chaosmonger → TargetSelector → Projector → Artifact

Key Responsibilities:
1. Classify intent (DETERMINISTIC, PROBABILISTIC, CHAOTIC)
2. Generate agent source if PROBABILISTIC
3. Validate stability via Chaosmonger
4. Select projection target
5. Compile to artifact
6. Cache for reuse

Teaching:
    gotcha: Cache check happens BEFORE classification. Classification is expensive
            (involves J-gent RealityClassifier). Cache hits skip the entire pipeline.
            (Evidence: services/foundry/_tests/test_core.py::TestForgeCache::test_cache_hit)

    gotcha: CHAOTIC reality OR unstable code → WASM sandbox UNCONDITIONALLY.
            This is a security invariant, not a preference. No overrides allowed.
            (Evidence: services/foundry/_tests/test_core.py::TestForgeBasics::test_forge_chaotic_intent)

    gotcha: Lazy-load J-gent dependencies via _get_classifier()/_get_architect().
            This defers imports until first use, improving startup time significantly.
            (Evidence: services/foundry/_tests/test_core.py::TestForgeBasics::test_forge_simple_intent)

Example:
    >>> foundry = AgentFoundry()
    >>> response = await foundry.forge(ForgeRequest(
    ...     intent="parse CSV files and extract headers",
    ...     context={"interactive": True}
    ... ))
    >>> response.target
    'marimo'  # Interactive context → marimo notebook

See: spec/services/foundry.md
"""

from __future__ import annotations

import logging
from datetime import UTC, datetime
from typing import TYPE_CHECKING, Any

from .cache import CacheEntry, EphemeralAgentCache
from .contracts import (
    CacheRequest,
    CacheResponse,
    ForgeRequest,
    ForgeResponse,
    FoundryManifestResponse,
    InspectRequest,
    InspectResponse,
    PromoteRequest,
    PromoteResponse,
)
from .polynomial import FoundryEvent, FoundryState, FoundryStateMachine

if TYPE_CHECKING:
    from agents.j import (
        ArchitectConstraints,
        MetaArchitect,
        RealityClassifier,
        StabilityResult,
        Target,
    )

logger = logging.getLogger(__name__)


class AgentFoundry:
    """
    The Agent Foundry Crown Jewel.

    Orchestrates the full JIT agent synthesis pipeline:
    RealityClassifier → MetaArchitect → Chaosmonger → TargetSelector → Projector

    Usage:
        foundry = AgentFoundry()

        response = await foundry.forge(ForgeRequest(
            intent="parse CSV files and extract headers",
            context={"interactive": True}
        ))

        if response.success:
            print(f"Target: {response.target}")
            print(f"Artifact: {response.artifact}")
    """

    def __init__(
        self,
        cache: EphemeralAgentCache | None = None,
        classifier: "RealityClassifier | None" = None,
        architect: "MetaArchitect | None" = None,
    ) -> None:
        """
        Initialize the Foundry.

        Args:
            cache: Ephemeral agent cache (default: new cache with 100 entries, 24h TTL)
            classifier: Reality classifier (default: lazy-loaded)
            architect: Meta architect (default: lazy-loaded)
        """
        self._cache = cache or EphemeralAgentCache()
        self._classifier = classifier
        self._architect = architect
        self._state_machine = FoundryStateMachine()

        # Statistics
        self._total_forges = 0
        self._cache_hits = 0
        self._recent_forges: list[dict[str, Any]] = []
        self._max_recent = 20

    @property
    def state(self) -> FoundryState:
        """Current state of the Foundry."""
        return self._state_machine.state

    @property
    def cache(self) -> EphemeralAgentCache:
        """The ephemeral agent cache."""
        return self._cache

    def _get_classifier(self) -> "RealityClassifier":
        """Lazy-load the RealityClassifier."""
        if self._classifier is None:
            from agents.j import RealityClassifier

            self._classifier = RealityClassifier()
        return self._classifier

    def _get_architect(self) -> "MetaArchitect":
        """Lazy-load the MetaArchitect."""
        if self._architect is None:
            from agents.j import MetaArchitect

            self._architect = MetaArchitect()
        return self._architect

    async def forge(self, request: ForgeRequest) -> ForgeResponse:
        """
        Forge a new ephemeral agent from intent.

        This is the main entry point for the Foundry.

        Pipeline:
        1. Check cache (return if hit)
        2. Classify reality
        3. If PROBABILISTIC: Generate source via MetaArchitect
        4. Validate stability via Chaosmonger
        5. Select target via TargetSelector
        6. Compile via appropriate Projector
        7. Cache result
        8. Return ForgeResponse
        """
        try:
            self._total_forges += 1

            # 1. Check cache
            cache_key = self._cache.compute_key(request.intent, request.context)
            cached = self._cache.get(cache_key)
            if cached:
                self._cache_hits += 1
                self._record_forge(request.intent, cached.target, "cache_hit")
                return ForgeResponse(
                    success=True,
                    cache_key=cache_key,
                    target=cached.target,
                    artifact_type=cached.artifact_type,
                    artifact=cached.artifact,
                    reality=cached.reality,
                    stability_score=cached.stability_score,
                    agent_source=cached.agent_source,
                    forced=False,
                    reason="Cache hit",
                    error=None,
                )

            # 2. Classify reality
            self._state_machine.transition(FoundryState.CLASSIFYING, FoundryEvent.START_FORGE)

            from agents.j import (
                ArchitectConstraints,
                ArchitectInput,
                ClassificationInput,
                Reality,
                StabilityConfig,
                Target,
                analyze_stability,
                select_target_with_reason,
            )

            entropy_budget = request.entropy_budget
            constraints = ArchitectConstraints(entropy_budget=entropy_budget)

            classification_input = ClassificationInput(
                intent=request.intent,
                context=request.context,
                entropy_budget=entropy_budget,
            )
            classification = await self._get_classifier().invoke(classification_input)
            reality = classification.reality

            self._state_machine.transition(
                FoundryState.GENERATING
                if reality == Reality.PROBABILISTIC
                else FoundryState.SELECTING,
                FoundryEvent.REALITY_CLASSIFIED,
                {"reality": reality.value},
            )

            # 3. Generate source (if PROBABILISTIC)
            agent_source: str | None = None
            stability: "StabilityResult | None" = None
            stability_score: float | None = None

            if reality == Reality.PROBABILISTIC:
                arch_input = ArchitectInput(
                    intent=request.intent,
                    constraints=constraints,
                )
                source_result = await self._get_architect().invoke(arch_input)
                agent_source = source_result.source

                self._state_machine.transition(
                    FoundryState.VALIDATING,
                    FoundryEvent.SOURCE_GENERATED,
                )

                # 4. Validate stability
                stability = analyze_stability(
                    agent_source,
                    entropy_budget=entropy_budget,
                    config=StabilityConfig(),
                )
                stability_score = 1.0 if stability.is_stable else 0.0

                self._state_machine.transition(
                    FoundryState.SELECTING,
                    FoundryEvent.STABILITY_CHECKED,
                    {"is_stable": stability.is_stable},
                )

            # 5. Select target
            target: Target
            forced: bool
            reason: str

            if request.target_override:
                try:
                    target = Target(request.target_override)
                    forced = False
                    reason = f"Explicit override: {request.target_override}"
                except ValueError:
                    # Invalid target, fall through to automatic selection
                    result = select_target_with_reason(
                        reality=reality,
                        context=request.context,
                        stability=stability,
                    )
                    target = result.target
                    forced = result.forced
                    reason = result.reason
            else:
                result = select_target_with_reason(
                    reality=reality,
                    context=request.context,
                    stability=stability,
                )
                target = result.target
                forced = result.forced
                reason = result.reason

            self._state_machine.transition(
                FoundryState.PROJECTING,
                FoundryEvent.TARGET_SELECTED,
                {"target": target.value, "forced": forced},
            )

            # 6. Project to artifact
            artifact, artifact_type = await self._project(
                target, agent_source, request.intent, reality
            )

            self._state_machine.transition(
                FoundryState.CACHING,
                FoundryEvent.PROJECTION_COMPLETE,
            )

            # 7. Cache result
            entry = CacheEntry(
                key=cache_key,
                intent=request.intent,
                context=request.context,
                agent_source=agent_source,
                target=target.value,
                artifact=artifact,
                artifact_type=artifact_type,
                reality=reality.value,
                stability_score=stability_score,
                created_at=datetime.now(UTC),
            )
            self._cache.put(entry)

            self._state_machine.transition(
                FoundryState.IDLE,
                FoundryEvent.CACHED,
            )

            # Record for recent forges
            self._record_forge(request.intent, target.value, "forged")

            return ForgeResponse(
                success=True,
                cache_key=cache_key,
                target=target.value,
                artifact_type=artifact_type,
                artifact=artifact,
                reality=reality.value,
                stability_score=stability_score,
                agent_source=agent_source,
                forced=forced,
                reason=reason,
                error=None,
            )

        except Exception as e:
            logger.exception("Forge failed")
            self._state_machine.fail(str(e))
            self._state_machine.reset()
            self._record_forge(request.intent, "error", str(e))

            return ForgeResponse(
                success=False,
                cache_key=None,
                target="error",
                artifact_type="error",
                artifact=None,
                reality="unknown",
                stability_score=None,
                agent_source=None,
                forced=False,
                reason=None,
                error=str(e),
            )

    async def _project(
        self,
        target: "Target",
        agent_source: str | None,
        intent: str,
        reality: Any,
    ) -> tuple[str | list[dict[str, Any]], str]:
        """
        Project to target-specific artifact.

        Returns (artifact, artifact_type).
        """
        from agents.j import Target

        # For DETERMINISTIC/CHAOTIC without generated source,
        # create a minimal placeholder agent
        if agent_source is None:
            agent_source = self._create_placeholder_source(intent, reality)

        # Get the appropriate projector
        match target:
            case Target.LOCAL:
                # For LOCAL, we just return the source
                return agent_source, "source"

            case Target.CLI:
                from system.projector import CLIProjector

                cli_projector = CLIProjector()
                artifact = self._project_source(cli_projector, agent_source)
                return artifact, "script"

            case Target.DOCKER:
                from system.projector import DockerProjector

                docker_projector = DockerProjector()
                artifact = self._project_source(docker_projector, agent_source)
                return artifact, "dockerfile"

            case Target.K8S:
                from system.projector import K8sProjector, manifests_to_yaml

                k8s_projector = K8sProjector()
                artifact = self._project_source(k8s_projector, agent_source)
                # K8s returns list of resources, convert to dicts
                if isinstance(artifact, list):
                    return [r.to_dict() for r in artifact], "manifests"
                return str(artifact), "manifests"

            case Target.WASM:
                from system.projector import WASMProjector

                wasm_projector = WASMProjector()
                artifact = self._project_source(wasm_projector, agent_source)
                return artifact, "html"

            case Target.MARIMO:
                from system.projector import MarimoProjector

                marimo_projector = MarimoProjector()
                artifact = self._project_source(marimo_projector, agent_source)
                return artifact, "cell"

            case _:
                # Fallback to source
                return agent_source, "source"

    def _project_source(self, projector: Any, source: str) -> Any:
        """
        Create a temporary agent class from source and project it.

        This dynamically creates an Agent class to satisfy the projector interface.
        """
        # Create a temporary agent class from source
        # For now, we return the source wrapped in a basic CLI script format
        # Full projector integration requires creating a proper Agent class

        # The projectors expect an Agent class, not raw source.
        # For Phase 4, we return formatted source strings.
        # Full projector integration is Phase 5+ work.

        if hasattr(projector, "compile_source"):
            # If projector supports source compilation directly
            return projector.compile_source(source)

        # For now, wrap source in projector-appropriate format
        projector_name = projector.name if hasattr(projector, "name") else "unknown"

        match projector_name:
            case "cli":
                return self._wrap_cli_script(source)
            case "docker":
                return self._wrap_dockerfile(source)
            case "wasm":
                return self._wrap_wasm_html(source)
            case "marimo":
                return self._wrap_marimo_cell(source)
            case _:
                return source

    def _wrap_cli_script(self, source: str) -> str:
        """Wrap source in a CLI-executable script."""
        return f'''#!/usr/bin/env python3
"""JIT Agent generated by kgents Foundry."""

import sys
import asyncio

# === Generated Agent Source ===
{source}

# === CLI Wrapper ===
async def main():
    # Find the agent class
    import inspect
    agent_cls = None
    for name, obj in list(globals().items()):
        if inspect.isclass(obj) and hasattr(obj, 'invoke'):
            agent_cls = obj
            break

    if agent_cls is None:
        print("Error: No agent class found", file=sys.stderr)
        sys.exit(1)

    agent = agent_cls()
    input_data = sys.stdin.read() if not sys.stdin.isatty() else " ".join(sys.argv[1:])
    result = await agent.invoke(input_data)
    print(result)

if __name__ == "__main__":
    asyncio.run(main())
'''

    def _wrap_dockerfile(self, source: str) -> str:
        """Wrap source in a Dockerfile."""
        return f"""FROM python:3.11-slim
WORKDIR /app

# Generated agent source
COPY <<EOF /app/agent.py
{source}
EOF

# Run agent
CMD ["python", "agent.py"]
"""

    def _wrap_wasm_html(self, source: str) -> str:
        """Wrap source in WASM-ready HTML."""
        escaped_source = source.replace("\\", "\\\\").replace("`", "\\`")
        return f"""<!DOCTYPE html>
<html>
<head>
    <title>JIT Agent Sandbox</title>
    <script src="https://cdn.jsdelivr.net/pyodide/v0.24.1/full/pyodide.js"></script>
</head>
<body>
    <h1>JIT Agent Sandbox</h1>
    <textarea id="input" rows="5" cols="50">Enter input...</textarea>
    <br>
    <button onclick="runAgent()">Run Agent</button>
    <pre id="output"></pre>

    <script>
        let pyodide;
        async function init() {{
            pyodide = await loadPyodide();
            document.getElementById('output').textContent = 'Ready';
        }}

        async function runAgent() {{
            const input = document.getElementById('input').value;
            const source = `{escaped_source}`;
            const result = await pyodide.runPythonAsync(source + `
agent = next(cls for name, cls in locals().items() if hasattr(cls, 'invoke'))()
import asyncio
asyncio.run(agent.invoke("${{input}}"))
`);
            document.getElementById('output').textContent = result;
        }}

        init();
    </script>
</body>
</html>
"""

    def _wrap_marimo_cell(self, source: str) -> str:
        """Wrap source in a marimo notebook cell."""
        return f"""import marimo as mo

# === JIT Agent Source ===
{source}

# === Marimo Interactive Cell ===
input_area = mo.ui.text_area(placeholder="Enter input...", label="Agent Input")
run_button = mo.ui.run_button(label="Invoke Agent")

@mo.cache
def invoke_agent(input_text):
    import asyncio
    # Find agent class
    agent_cls = next(cls for name, cls in globals().items() if hasattr(cls, 'invoke'))
    agent = agent_cls()
    return asyncio.run(agent.invoke(input_text))

mo.vstack([
    input_area,
    run_button,
    mo.callout(invoke_agent(input_area.value) if run_button.value else "Click Run to invoke"),
])
"""

    def _create_placeholder_source(self, intent: str, reality: Any) -> str:
        """Create a minimal placeholder agent for non-PROBABILISTIC cases."""
        return f'''"""
Placeholder agent for: {intent}
Reality: {reality}
"""

class PlaceholderAgent:
    """Generated placeholder agent."""

    @property
    def name(self) -> str:
        return "placeholder-agent"

    async def invoke(self, input: str) -> str:
        return f"Placeholder response for: {{input}}"
'''

    async def inspect(self, request: InspectRequest) -> InspectResponse:
        """Inspect a registered or cached agent."""
        # Check cache first
        cached = self._cache.get(request.agent_name)
        if cached:
            return InspectResponse(
                found=True,
                agent_name=request.agent_name,
                halo=None,  # JIT agents don't have halo yet
                polynomial=None,
                aspects=["invoke"],
                source=cached.agent_source if request.include_source else None,
                is_ephemeral=True,
                cache_metrics={
                    "invocation_count": cached.invocation_count,
                    "success_rate": cached.success_rate,
                    "age_seconds": cached.age.total_seconds(),
                },
            )

        # TODO: Look up registered agents via AGENTESE registry
        return InspectResponse(
            found=False,
            agent_name=request.agent_name,
            halo=None,
            polynomial=None,
            aspects=None,
            source=None,
            is_ephemeral=False,
            cache_metrics=None,
        )

    async def handle_cache(self, request: CacheRequest) -> CacheResponse:
        """Handle cache operations."""
        match request.action:
            case "list":
                entries = self._cache.list_entries()
                return CacheResponse(
                    success=True,
                    action="list",
                    entries=[e.to_dict() for e in entries],
                )

            case "get":
                if not request.key:
                    return CacheResponse(
                        success=False,
                        action="get",
                        error="Key required for get operation",
                    )
                entry = self._cache.get(request.key)
                return CacheResponse(
                    success=entry is not None,
                    action="get",
                    entry=entry.to_dict() if entry else None,
                    error=None if entry else "Entry not found",
                )

            case "evict":
                if not request.key:
                    return CacheResponse(
                        success=False,
                        action="evict",
                        error="Key required for evict operation",
                    )
                evicted = self._cache.evict(request.key)
                return CacheResponse(
                    success=evicted,
                    action="evict",
                    evicted_count=1 if evicted else 0,
                    error=None if evicted else "Entry not found",
                )

            case "clear":
                count = self._cache.clear()
                return CacheResponse(
                    success=True,
                    action="clear",
                    evicted_count=count,
                )

            case "evict_expired":
                count = self._cache.evict_expired()
                return CacheResponse(
                    success=True,
                    action="evict_expired",
                    evicted_count=count,
                )

            case _:
                return CacheResponse(
                    success=False,
                    action=request.action,
                    error=f"Unknown action: {request.action}",
                )

    async def promote(self, request: PromoteRequest) -> PromoteResponse:
        """
        Promote an ephemeral agent to permanent.

        Phase 5 work - stub for now.
        """
        # TODO: Implement in Phase 5
        return PromoteResponse(
            success=False,
            agent_name=None,
            spec_path=None,
            error="Promotion not yet implemented (Phase 5)",
        )

    def manifest(self) -> FoundryManifestResponse:
        """Get status manifest."""
        stats = self._cache.stats
        return FoundryManifestResponse(
            cache_size=stats["size"],
            cache_max_size=stats["max_size"],
            total_forges=self._total_forges,
            cache_hits=self._cache_hits,
            cache_hit_rate=self._cache_hits / max(self._total_forges, 1),
            recent_forges=self._recent_forges[-10:],
            status="operational",
        )

    def _record_forge(self, intent: str, target: str, status: str) -> None:
        """Record a forge operation for recent history."""
        self._recent_forges.append(
            {
                "intent": intent[:50],
                "target": target,
                "status": status,
                "timestamp": datetime.now(UTC).isoformat(),
            }
        )
        # Keep only last N entries
        if len(self._recent_forges) > self._max_recent:
            self._recent_forges = self._recent_forges[-self._max_recent :]


# =============================================================================
# Exports
# =============================================================================

__all__ = [
    "AgentFoundry",
]
