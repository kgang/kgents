# J-gent + Alethic Projection Synthesis: The Agent Foundry

> *"The agent that doesn't exist yet is the agent you need most. The projector determines how it manifests."*

**Session Type**: Transformative Architecture
**Prerequisites**: `spec/j-gents/`, `spec/protocols/alethic-projection.md`, `spec/a-gents/alethic.md`
**Status**: Brainstorming
**Decision**: WASM is near-term priority (see Servo work)

---

## The Insight

Two powerful subsystems exist in parallel:

| System | Purpose | Current State |
|--------|---------|---------------|
| **J-gents** | JIT Agent Intelligence — compile ephemeral agents on demand | Spec complete, impl dormant |
| **Alethic Projection** | Agent Compilation — project (Nucleus, Halo) to targets | Impl solid, just enhanced |

**The synthesis**: J-gent's MetaArchitect generates the **Nucleus + Halo**. Alethic Projectors compile it to **any target**.

```
┌────────────────────────────────────────────────────────────────────────────┐
│                        THE AGENT FOUNDRY                                    │
├────────────────────────────────────────────────────────────────────────────┤
│                                                                            │
│   Intent ──▶ J-gent ──▶ MetaArchitect ──▶ (Nucleus, Halo)                 │
│              Reality     JIT Generation    Agent Definition                │
│              Classifier                                                    │
│                                                                            │
│                                    │                                       │
│                                    ▼                                       │
│                                                                            │
│                         Alethic Projector Registry                         │
│                                                                            │
│                    ┌────────────┬─────────────┐                           │
│                    │            │             │                           │
│                    ▼            ▼             ▼                           │
│              LocalProjector  K8sProjector  CLIProjector                   │
│                    │            │             │                           │
│                    ▼            ▼             ▼                           │
│              In-Process      K8s YAML     Shell Script                    │
│               Agent          Manifests    Executable                      │
│                                                                            │
│              ┌────────────┬─────────────┐                                 │
│              │            │             │                                 │
│              ▼            ▼             ▼                                 │
│         MarimoProjector  WASMProjector  DockerProjector                   │
│              │            │             │                                 │
│              ▼            ▼             ▼                                 │
│          Notebook       Browser        Container                          │
│            Cell        Sandbox         Image                              │
│                                                                            │
└────────────────────────────────────────────────────────────────────────────┘
```

---

## Part 1: New Projector Targets

### 1.1 CLIProjector Enhancement (kg a manifest --target cli)

**Current**: Basic shell script generation (just implemented today)

**Enhanced Vision**:

```bash
# Generate and immediately run
kg a manifest MyAgent --target cli | bash

# Generate with custom options
kg a manifest MyAgent --target cli --input-mode=stdin --output-mode=json

# Generate with state persistence location
kg a manifest MyAgent --target cli --state-dir=/tmp/agent-state
```

**CLI Handler Integration** (`protocols/cli/handlers/a_gent.py`):

```python
@cli_command("a manifest")
async def manifest_command(
    agent_name: str,
    target: Literal["k8s", "cli", "docker", "marimo"] = "k8s",
    **kwargs
) -> str:
    """Generate deployment manifest for agent."""
    agent_cls = resolve_agent_class(agent_name)

    match target:
        case "k8s":
            return K8sProjector(**kwargs).compile(agent_cls)
        case "cli":
            return CLIProjector(**kwargs).compile(agent_cls)
        case "docker":
            return DockerProjector(**kwargs).compile(agent_cls)
        case "marimo":
            return MarimoProjector(**kwargs).compile(agent_cls)
```

### 1.2 MarimoProjector: Notebook Cell Generation

**Purpose**: Generate marimo notebook cells for interactive agent exploration.

**Why This Matters**:
- Exploratory development of new agents
- Teaching/documentation via executable notebooks
- J-gent MetaArchitect output can be immediately explored in marimo

```python
class MarimoProjector(Projector[str]):
    """Compile agent to marimo notebook cell."""

    def compile(self, agent_cls: type[Agent]) -> str:
        return f'''
import marimo as mo
from {agent_cls.__module__} import {agent_cls.__name__}
from system.projector import LocalProjector

# Compile agent with full capabilities
agent = LocalProjector().compile({agent_cls.__name__})

# Interactive input
input_widget = mo.ui.text(placeholder="Enter input...")

# Agent execution cell
@mo.cell
async def run_agent():
    if input_widget.value:
        result = await agent.invoke(input_widget.value)
        return mo.md(f"**Result**: {{result}}")
    return mo.md("Enter input above")

# State inspection (if stateful)
@mo.cell
def inspect_state():
    if hasattr(agent, 'state'):
        return mo.json(agent.state)
    return mo.md("Agent is stateless")
'''
```

**Capability Mappings**:

| Capability | marimo Feature |
|------------|----------------|
| @Stateful | `mo.json()` state inspector widget |
| @Soulful | Persona banner + conversation mode |
| @Observable | `mo.stat()` metrics dashboard |
| @Streamable | Streaming output cell with live updates |
| @TurnBased | Turn history visualization |

### 1.3 WASMProjector: Browser-Runnable Agents (NEAR-TERM PRIORITY)

**Purpose**: Compile agents to WebAssembly for sandboxed browser execution.

**Why This Matters** (and why it's near-term):
- Zero-trust execution environment for JIT-compiled agents
- J-gent chaotic reality classification → run in WASM sandbox, not on server
- **Servo work** provides the foundation — browser engine primitives are available
- Enables client-side agent execution without server round-trips
- Critical for offline-capable agents and edge deployment

```python
class WASMProjector(Projector[WASMModule]):
    """Compile agent to WebAssembly module."""

    def compile(self, agent_cls: type[Agent]) -> WASMModule:
        # 1. Generate Python source
        source = self._generate_minimal_source(agent_cls)

        # 2. Compile via Pyodide or RustPython
        wasm = self._compile_to_wasm(source)

        # 3. Add capability stubs
        if self._has_cap("Stateful"):
            wasm = self._add_indexeddb_state(wasm)

        if self._has_cap("Observable"):
            wasm = self._add_performance_api(wasm)

        return wasm
```

**Capability Mappings**:

| Capability | WASM Feature |
|------------|--------------|
| @Stateful | IndexedDB persistence |
| @Observable | Performance API + console.time |
| @Streamable | ReadableStream output |
| @Soulful | N/A (no K-gent in browser) |

**Use Case**: Chaosmonger runs JIT agent in WASM sandbox before promoting to LocalProjector.

### 1.4 DockerProjector: Container Image Generation

**Purpose**: Generate Dockerfile for containerized agent deployment.

```python
class DockerProjector(Projector[str]):
    """Compile agent to Dockerfile."""

    base_image: str = "python:3.12-slim"

    def compile(self, agent_cls: type[Agent]) -> str:
        return f'''
FROM {self.base_image}

WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt

COPY {agent_cls.__module__.replace('.', '/')} /app/

# Health check endpoint
EXPOSE 8080

CMD ["python", "-m", "uvicorn", "agent_server:app", "--host", "0.0.0.0", "--port", "8080"]
'''
```

---

## Part 2: J-gent Revitalization via Alethic Projection

### 2.1 The Missing Link: MetaArchitect + Projector

Current J-gent spec has MetaArchitect producing **source code**:

```python
MetaArchitect: (Intent, Context, Constraints) → SourceCode
```

**Enhanced design** — MetaArchitect produces **decorated agent class**:

```python
MetaArchitect: (Intent, Context, Constraints) → (Nucleus, Halo)

# Then Alethic Projection takes over
ProjectorRegistry.compile(nucleus, halo, target="local")
```

This means J-gent can:
1. Generate an ephemeral agent definition
2. Project it to **any target** based on context

### 2.2 Reality Classification → Projector Selection

Extend J-gent's reality classification to include **projection target selection**:

```python
class RealityClassifier:
    async def classify(self, intent: str, context: dict) -> Classification:
        reality = await self._classify_reality(intent)
        target = await self._select_target(reality, context)

        return Classification(
            reality=reality,      # DETERMINISTIC | PROBABILISTIC | CHAOTIC
            target=target,        # LOCAL | CLI | WASM | K8S | MARIMO
            entropy_budget=self._compute_budget(reality),
        )

    def _select_target(self, reality: Reality, context: dict) -> Target:
        match reality:
            case Reality.DETERMINISTIC:
                return Target.LOCAL  # Fast, in-process
            case Reality.PROBABILISTIC:
                if context.get("interactive"):
                    return Target.MARIMO  # Exploration
                elif context.get("production"):
                    return Target.K8S  # Scale
                else:
                    return Target.CLI  # Quick test
            case Reality.CHAOTIC:
                return Target.WASM  # Sandboxed, untrusted
```

### 2.3 The J-gent Service: Agent Foundry Crown Jewel

Create a new **Crown Jewel** that orchestrates J-gent + Alethic Projection:

```python
# services/foundry/
class AgentFoundry:
    """
    Crown Jewel: On-demand agent construction.

    Combines J-gent JIT intelligence with Alethic Projection
    to create and deploy ephemeral agents.
    """

    def __init__(
        self,
        reality_classifier: RealityClassifier,
        meta_architect: MetaArchitect,
        chaosmonger: Chaosmonger,
        projector_registry: ProjectorRegistry,
    ):
        self.classifier = reality_classifier
        self.architect = meta_architect
        self.chaosmonger = chaosmonger
        self.projectors = projector_registry

    async def forge(
        self,
        intent: str,
        context: dict | None = None,
        constraints: Constraints | None = None,
    ) -> CompiledAgent:
        """
        Forge an agent on demand.

        1. Classify reality to determine approach
        2. Generate agent definition via MetaArchitect
        3. Validate via Chaosmonger
        4. Project to appropriate target
        5. Return executable agent
        """
        context = context or {}
        constraints = constraints or Constraints()

        # 1. Classify
        classification = await self.classifier.classify(intent, context)

        if classification.reality == Reality.CHAOTIC:
            # Force WASM sandbox for untrusted
            classification.target = Target.WASM

        # 2. Generate
        agent_def = await self.architect.generate(
            intent=intent,
            context=context,
            constraints=constraints,
            entropy_budget=classification.entropy_budget,
        )

        # 3. Validate
        stability = await self.chaosmonger.analyze(
            agent_def.source,
            budget=classification.entropy_budget,
        )

        if not stability.is_stable:
            return self._fallback_agent(intent, stability.reason)

        # 4. Project
        projector = self.projectors.get(classification.target)
        compiled = projector.compile(agent_def.cls)

        # 5. Return
        return CompiledAgent(
            agent=compiled,
            target=classification.target,
            reality=classification.reality,
            ephemeral=True,
            cache_key=hash((intent, context)),
        )
```

### 2.4 AGENTESE Integration

```python
# self.foundry.* paths
@node(
    path="self.foundry.forge",
    aspects=["manifest"],
    dependencies=("agent_foundry",),
)
async def foundry_forge(
    umwelt: Umwelt,
    intent: str,
    context: dict | None = None,
    target: str | None = None,
) -> CompiledAgent:
    """Forge an ephemeral agent on demand."""
    foundry = container.get("agent_foundry")
    return await foundry.forge(intent, context)

# Usage from CLI or code
await logos.invoke(
    "self.foundry.forge",
    umwelt,
    intent="Parse CloudWatch logs and extract Lambda cold starts",
    context={"log_format": "json", "interactive": True},
)
```

---

## Part 3: Transformative Ideas

### 3.1 Agent Promotion Pipeline

Ephemeral agents that prove useful can be **promoted** to permanent:

```
Ephemeral (JIT) → Cached (Hash) → Promoted (spec/) → Deployed (K8s)
        │                │                │                │
        └── invocations  └── threshold    └── Judge       └── K8sProjector
             < N               > M            approval
```

**Meta-parameterized thresholds** — these are degrees of freedom to optimize and discover:

```python
@dataclass
class PromotionPolicy:
    """
    Promotion thresholds are hyperparameters, not constants.

    The Foundry can learn optimal values through:
    - A/B testing different thresholds
    - Bayesian optimization on promotion success
    - User feedback signals
    """

    # Invocation threshold: how many successful runs before considering promotion?
    invocation_threshold: int = field(default=100, metadata={"tunable": True, "range": (10, 1000)})

    # Success rate: what fraction must succeed?
    success_rate_threshold: float = field(default=0.95, metadata={"tunable": True, "range": (0.8, 0.99)})

    # Diversity threshold: how many unique inputs must succeed?
    unique_inputs_threshold: int = field(default=10, metadata={"tunable": True, "range": (5, 100)})

    # Time-in-cache: minimum age before promotion consideration
    min_cache_age_hours: float = field(default=24.0, metadata={"tunable": True, "range": (1.0, 168.0)})

    # Judge approval: always required for taste/ethics
    requires_judge_approval: bool = True


class PromotionOptimizer:
    """Learn optimal promotion thresholds from feedback."""

    async def update(self, promotion_outcome: PromotionOutcome) -> None:
        """Update policy based on whether promoted agent was useful."""
        if promotion_outcome.was_useful:
            # Agent proved valuable — maybe we can promote faster
            self._adjust_thresholds(direction="lower")
        else:
            # Agent was promoted too early — raise thresholds
            self._adjust_thresholds(direction="higher")


async def maybe_promote(
    agent: EphemeralAgent,
    metrics: AgentMetrics,
    policy: PromotionPolicy,
) -> PromotionDecision:
    """Evaluate agent for promotion using current policy."""
    if not _meets_thresholds(metrics, policy):
        return PromotionDecision.NOT_READY

    if policy.requires_judge_approval:
        judgment = await Judge().approve(agent.source)
        if not judgment.accepted:
            return PromotionDecision.REJECTED(judgment.reason)

    await persist_to_spec(agent)
    return PromotionDecision.PROMOTED
```

### 3.2 Multi-Target Deployment

Same agent definition, deployed to multiple targets simultaneously:

```python
async def deploy_everywhere(agent_def: AgentDefinition) -> MultiDeployment:
    """Deploy agent to all appropriate targets."""
    return MultiDeployment(
        local=LocalProjector().compile(agent_def.cls),
        cli=CLIProjector().compile(agent_def.cls),
        k8s=K8sProjector().compile(agent_def.cls),
        marimo=MarimoProjector().compile(agent_def.cls),
    )
```

This enables:
- Local development with `LocalProjector`
- CLI testing with `CLIProjector`
- Production deployment with `K8sProjector`
- Documentation with `MarimoProjector`

### 3.3 Projector Composition

Projectors compose like agents — this is **required**, not aspirational:

```python
# Sequential composition: Docker → K8s (build image, then deploy)
docker_k8s = DockerProjector() >> K8sProjector()
# Generates: Dockerfile + K8s Deployment referencing the image

# Sequential composition: K8s + Helm
k8s_helm = K8sProjector() >> HelmChartProjector()

# Parallel composition: multi-target
multi_target = LocalProjector() // K8sProjector() // CLIProjector()

# Usage
results = multi_target.compile(MyAgent)
# results = (LocalAgent, [K8sResource], str)
```

**The DockerProjector >> K8sProjector pattern**:

```python
class DockerProjector(Projector[DockerArtifact]):
    def compile(self, agent_cls: type[Agent]) -> DockerArtifact:
        dockerfile = self._generate_dockerfile(agent_cls)
        image_tag = f"kgents/{self._derive_name(agent_cls)}:latest"
        return DockerArtifact(dockerfile=dockerfile, image_tag=image_tag)


class K8sProjector(Projector[list[K8sResource]]):
    def compile(
        self,
        agent_cls: type[Agent],
        docker_artifact: DockerArtifact | None = None,  # From upstream
    ) -> list[K8sResource]:
        resources = self._base_resources(agent_cls)

        # If composed with DockerProjector, use its image tag
        if docker_artifact:
            for r in resources:
                if r.kind in ("Deployment", "StatefulSet"):
                    r.spec["template"]["spec"]["containers"][0]["image"] = (
                        docker_artifact.image_tag
                    )

        return resources


# Composition produces both artifacts
docker_k8s = DockerProjector() >> K8sProjector()
result = docker_k8s.compile(MyAgent)
# result.dockerfile = "FROM python:3.12..."
# result.manifests = [Deployment with image: kgents/my-agent:latest, ...]
```

### 3.4 Capability Inference

MetaArchitect could infer capabilities from intent:

```python
class CapabilityInferrer:
    """Infer Halo capabilities from intent analysis."""

    async def infer(self, intent: str) -> set[Capability]:
        capabilities = set()

        if "state" in intent or "remember" in intent:
            capabilities.add(Capability.Stateful(schema=dict))

        if "stream" in intent or "continuous" in intent:
            capabilities.add(Capability.Streamable(budget=5.0))

        if "observe" in intent or "metrics" in intent:
            capabilities.add(Capability.Observable(metrics=True))

        if "conversation" in intent or "persona" in intent:
            capabilities.add(Capability.Soulful(persona="default"))

        return capabilities
```

### 3.5 Sandbox Graduation

Chaotic reality agents start in WASM sandbox, graduate to Local:

```
Reality: CHAOTIC
    │
    ▼
WASMProjector (sandbox)
    │
    ├── Success × N → Confidence increases
    │
    ▼
LocalProjector (trusted)
    │
    ├── Success × M → Production ready
    │
    ▼
K8sProjector (deployed)
```

```python
class SandboxGraduator:
    wasm_success_threshold: int = 10
    local_success_threshold: int = 50

    async def evaluate(self, agent: EphemeralAgent) -> Target:
        if agent.metrics.wasm_successes < self.wasm_success_threshold:
            return Target.WASM  # Stay sandboxed
        elif agent.metrics.local_successes < self.local_success_threshold:
            return Target.LOCAL  # Graduated to local
        else:
            return Target.K8S  # Production ready
```

### 3.6 Intent-to-Deployment Pipeline

Full pipeline from natural language to running agent:

```
"Parse Nginx logs and alert on 5xx spikes"
                │
                ▼
        RealityClassifier
                │
                ▼
    Classification(PROBABILISTIC, K8S)
                │
                ▼
          MetaArchitect
                │
                ▼
    (NginxAlertAgent, {Stateful, Observable})
                │
                ▼
           Chaosmonger
                │
                ▼
          [STABLE ✓]
                │
                ▼
          K8sProjector
                │
                ▼
    [StatefulSet, PVC, ServiceMonitor, HPA]
                │
                ▼
        kubectl apply
                │
                ▼
    🚀 Agent Running in Production
```

---

## Part 4: Implementation Roadmap

### Phase 1: CLI + Docker Integration (Immediate)

```
[ ] Wire CLIProjector to `kg a manifest --target cli`
[ ] Add DockerProjector with basic Dockerfile generation
[ ] Implement DockerProjector >> K8sProjector composition
[ ] Add `kg a run` enhancements (--stream, --trace)
```

### Phase 2: WASM Foundation (Week 1) — PRIORITY

```
[ ] Research Servo primitives for WASM agent execution
[ ] Prototype WASMProjector with Pyodide/RustPython
[ ] Test sandboxed execution of simple agents
[ ] Integrate with Chaosmonger for chaotic reality sandbox
[ ] Define WASM capability mappings (IndexedDB, Performance API)
```

### Phase 3: Marimo Integration (Week 2)

```
[ ] Implement MarimoProjector
[ ] Create marimo template for agent exploration
[ ] Wire to `kg a manifest --target marimo`
[ ] Test with existing agents
```

### Phase 4: Agent Foundry Service (Week 3)

```
[ ] Create services/foundry/ Crown Jewel
[ ] Implement AgentFoundry orchestrator
[ ] Wire to AGENTESE (self.foundry.*)
[ ] Integrate RealityClassifier with Projector selection
```

### Phase 5: Promotion + Optimization (Week 4)

```
[ ] Implement PromotionPolicy with tunable hyperparameters
[ ] Add PromotionOptimizer for threshold learning
[ ] Add metrics tracking for ephemeral agents
[ ] Create promotion workflow with Judge approval
```

---

## Voice Anchors

*"Daring, bold, creative, opinionated but not gaudy"*

This synthesis is opinionated:
- **J-gent + Alethic Projection is THE answer** to dynamic agent creation
- **WASM sandbox for chaotic reality** — trust no one
- **Promotion pipeline preserves curation** — not everything becomes permanent

*"The Mirror Test: Does K-gent feel like me on my best day?"*

An Agent Factory that can materialize the right agent for any task, deploy it anywhere, and graduate it from sandbox to production based on proven behavior — this feels like Kent's vision of "the app-builder building app-builder for app-building app-builders."

*"Tasteful > feature-complete"*

Focus on:
1. **CLIProjector + kg integration** (immediate value)
2. **MarimoProjector** (exploratory development)
3. **AgentFactory Crown Jewel** (the synthesis)

Defer:
- WASMProjector (research phase)
- Multi-language JIT (far future)

---

## Files to Touch

```
# Phase 1: CLI + Docker (Immediate)
impl/claude/protocols/cli/handlers/a_gent.py    # Add --target flag
impl/claude/system/projector/docker.py          # NEW: DockerProjector
impl/claude/system/projector/compose.py         # NEW: Projector composition (>>)

# Phase 2: WASM (Week 1 — PRIORITY)
impl/claude/system/projector/wasm.py            # NEW: WASMProjector
impl/claude/system/projector/wasm_runtime.py    # NEW: Pyodide/RustPython integration
spec/protocols/alethic-projection.md            # UPDATE: Add WASM target + Servo notes

# Phase 3: Marimo (Week 2)
impl/claude/system/projector/marimo.py          # NEW: MarimoProjector

# Phase 4: Agent Foundry (Week 3)
impl/claude/services/foundry/                   # NEW: AgentFoundry Crown Jewel
impl/claude/agents/j/                           # UPDATE: Revitalize J-gent impl
spec/j-gents/integration.md                     # UPDATE: Alethic Projection integration
spec/services/foundry.md                        # NEW: Foundry service spec

# Phase 5: Promotion (Week 4)
impl/claude/services/foundry/promotion.py       # NEW: PromotionPolicy + Optimizer
```

---

## Decisions Made

1. **Reality → Target mapping**: Provide sensible defaults (CHAOTIC → WASM, etc.) but expose as a controllable knob. The mapping itself is a **degree of freedom** — let the system learn optimal mappings.

2. **Promotion thresholds**: Meta-parameterized. Thresholds are hyperparameters to optimize and discover, not fixed constants. The Foundry can learn what works.

3. **WASM priority**: **Near-term/now**. Servo work provides foundation. WASM is essential for zero-trust JIT execution.

4. **Naming**: **Foundry** — forging new agents from raw intent.

5. **Projector composition**: `DockerProjector() >> K8sProjector()` is valid and required. Projectors compose like agents.

---

## Open Questions

1. **Servo integration depth**: How much of Servo's browser primitives can we leverage for WASM agent execution? Research needed.

2. **Promotion feedback loop**: How do we measure "was this promotion useful"? User signals? Invocation patterns? Error rates?

3. **Reality classifier training**: Can we learn the DETERMINISTIC/PROBABILISTIC/CHAOTIC boundary from execution outcomes?

---

*"The agent that doesn't exist yet is the agent you need most. Now we can forge it on demand, project it anywhere, and graduate it to permanence."*
