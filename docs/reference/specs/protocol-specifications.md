# Protocol Specifications

> *Protocol specifications: AGENTESE, projection, data-bus.*

---

## spec.protocols.README

## what_are_protocols

```python
spec Protocols: Cross-Cutting Coordination Patterns: What Are Protocols?
```

Protocols are **coordination patterns** that emerge when multiple agent genera work together toward a unified goal. Unlike individual agents (which are morphisms), protocols are **functors** that map entire categories of agents into coordinated systems.

### Examples
```python
>>> Protocol : (Agent₁ × Agent₂ × ... × Agentₙ) → CoordinatedSystem
```

---

## implementing_a_protocol

```python
spec Protocols: Cross-Cutting Coordination Patterns: Implementing a Protocol
```

A protocol implementation requires:

---

## the_protocol_stack

```python
spec Protocols: Cross-Cutting Coordination Patterns: The Protocol Stack
```

Protocols can compose into stacks:

### Examples
```python
>>> ┌─────────────────────────────────────┐
│ CLI Protocol (outermost)            │
│  ┌───────────────────────────────┐  │
│  │ Session Protocol              │  │
│  │  ┌─────────────────────────┐  │  │
│  │  │ Mirror Protocol         │  │  │
│  │  │  ┌───────────────────┐  │  │  │
│  │  │  │ Composition Proto │  │  │  │
│  │  │  └───────────────────┘  │  │  │
│  │  └─────────────────────────┘  │  │
│  └───────────────────────────────┘  │
└─────────────────────────────────────┘
```

---

## see_also

```python
spec Protocols: Cross-Cutting Coordination Patterns: See Also
```

- [../principles.md](../principles.md) — Core design principles - [../agents/README.md](../agents/README.md) — Categorical foundations - [../bootstrap.md](../bootstrap.md) — Irreducible kernel - [../../docs/mirror-protocol-implementation.md](../../docs/mirror-protocol-implementation.md) — Mirror Protocol phases

---

## spec.protocols.agentese

## epigraph

```python
spec AGENTESE: The Verb-First Ontology: Epigraph
```

---

---

## part_i_design_philosophy

```python
spec AGENTESE: The Verb-First Ontology: Part I: Design Philosophy
```

AGENTESE v3 synthesizes three years of lessons:

---

## part_iii_the_five_contexts_unchanged

```python
spec AGENTESE: The Verb-First Ontology: Part III: The Five Contexts (Unchanged)
```

The five contexts form a **complete and minimal basis** for semantic reference.

### Examples
```python
>>> ┌─────────────────────────────────────────────────────────────────────────────┐
│                         THE FIVE CONTEXTS                                    │
├─────────────┬───────────────────────────────────────────────────────────────┤
│ world.*     │ The External: entities, environments, tools                   │
│ self.*      │ The Internal: memory, capability, state, agent boundaries     │
│ concept.*   │ The Abstract: platonics, definitions, logic                   │
│ void.*      │ The Accursed Share: entropy, noise, serendipity, gratitude    │
│ time.*      │ The Temporal: history, forecast, schedule, traces             │
└─────────────┴───────────────────────────────────────────────────────────────┘
```

---

## appendix_b_files_to_modify

```python
spec AGENTESE: The Verb-First Ontology: Appendix B: Files to Modify
```

| File | Action | |------|--------| | `logos.py` | Add `__call__`, merge wiring, add query/subscribe/alias | | `wiring.py` | Delete | | `node.py` | Consolidate to single protocol | | `parser.py` | Remove clause/annotation parsing | | `jit.py` | Archive | | `affordances.py` | Add runtime enforcement | | `subscription.py` | Create | | `query.py` | Create | | `aliases.py` | Create | | `__init__.py` | Reduce to <50 exports |

---

## appendix_c_decision_log

```python
spec AGENTESE: The Verb-First Ontology: Appendix C: Decision Log
```

| Decision | Alternatives Considered | Rationale | |----------|------------------------|-----------| | Keep 3-part paths | Flat verbs (v2) | Context is ontological, not organizational | | Observer gradations | Full Umwelt always | Allow lightweight calls | | Bounded queries | Unbounded wildcards | Prevent footguns | | At-most-once subscriptions | At-least-once | Simpler default, upgrade optional | | Pre-charge economics | Post-charge | Safer for failure cases | | Categories as constraints | Cate

---

## appendix_d_contract_protocol_phase_7

```python
spec AGENTESE: The Verb-First Ontology: Appendix D: Contract Protocol (Phase 7)
```

The **Contract Protocol** enables BE/FE type synchronization via the `@node` decorator.

---

## spec.protocols.agentese-as-route

## epigraph

```python
spec AGENTESE-as-Route Protocol: Epigraph
```

---

---

## appendix_a_implementation_files

```python
spec AGENTESE-as-Route Protocol: Appendix A: Implementation Files
```

| File | Purpose | |------|---------| | `shell/projections/UniversalProjection.tsx` | Main handler | | `shell/projections/registry.ts` | Type → Component mapping | | `shell/projections/DynamicProjection.tsx` | Resolution logic | | `shell/projections/GenericProjection.tsx` | JSON fallback | | `shell/projections/ProjectionLoading.tsx` | Loading state | | `shell/projections/ProjectionError.tsx` | Error state | | `hooks/useAgentese.ts` | Path invocation | | `hooks/useAgenteseMutation.ts` | Write ope

---

## appendix_b_path_mappings_migration_reference

```python
spec AGENTESE-as-Route Protocol: Appendix B: Path Mappings (Migration Reference)
```

| Legacy Route | AGENTESE Path | |--------------|---------------| | `/brain` | `/self.memory` | | `/gestalt` | `/world.codebase` | | `/gardener` | `/concept.gardener` | | `/forge` | `/world.forge` | | `/town` | `/world.town` | | `/town/citizens` | `/world.town.citizen` | | `/town/citizens/:id` | `/world.town.citizen.{id}` | | `/town/coalitions` | `/world.town.coalition` | | `/park` | `/world.park` | | `/differance` | `/time.differance` |

---

## appendix_c_decision_log

```python
spec AGENTESE-as-Route Protocol: Appendix C: Decision Log
```

| Decision | Alternatives | Rationale | |----------|--------------|-----------| | `.` separator | `/` separator | Matches AGENTESE grammar; avoids ambiguity | | Aspect via `:` | Aspect via query param | Cleaner URLs; aspect is semantic, not a param | | Universal catch-all | Explicit route per path | Single source of truth; eliminates mapping | | Contract-driven | Manual registration | Type sync; no duplication | | Observer in header | Observer in cookie | Stateless; debuggable |

---

## spec.protocols.agentic-self-hosting-compiler

## agentic_self_hosting_compiler_ashc

```python
spec Agentic Self-Hosting Compiler (ASHC)
```

The proof is not formal—it's empirical. Run the tree a thousand times, and the pattern of nudges IS the proof.

### Examples
```python
>>> ASHC : Spec → (Executable, Evidence)

Evidence = {
    traces: [Run₁, Run₂, ..., Runₙ],
    chaos_results: ChaosReport,
    verification: TestResults,
    causal_graph: PromptNudge → Outcome
}
```
```python
>>> Kent's Idea (Spec)
       │
       ▼
┌──────────────────────────────────────────────────────────┐
│                    ASHC COMPILER                          │
│                                                          │
│  1. Generate N variations of the idea                    │
│  2. Run each through LLM → Implementation                │
│  3. Verify each with tests, types, lints                 │
│  4. Chaos test: compose variations combinatorially       │
│  5. Track causal relationships: nudge → outcome          │
│  6. Accumulate into evidence corpus                      │
│                                                          │
└──────────────────────────────────────────────────────────┘
       │
       ▼
Agent Executable + Evidence Corpus
```
```python
>>> @dataclass(frozen=True)
class Run:
    """A single execution of spec → implementation."""
    spec_hash: str              # Content-addressed spec
    prompt_used: str            # The actual prompt
    implementation: str         # Generated code
    test_results: TestReport    # pytest output
    type_results: TypeReport    # mypy output
    lint_results: LintReport    # ruff/lint output
    timestamp: datetime
    duration_ms: int
    nudges: tuple[Nudge, ...]   # What was tweaked from baseline

@dataclass(frozen=True)
class Evidence:
    """Accumulated evidence for spec↔impl equivalence."""
    runs: tuple[Run, ...]
    chaos_report: ChaosReport
    causal_graph: CausalGraph
    confidence: float           # 0.0-1.0, based on runs

    def equivalence_score(self) -> float:
        """
        How confident are we that spec matches impl?

        Based on:
        - Pass rate across runs
        - Diversity of chaos tests
        - Stability under nudges
        """
        pass_rate = sum(r.test_results.passed for r in self.runs) / len(self.runs)
        chaos_score = self.chaos_report.stability_score
        nudge_stability = self.causal_graph.stability_score
        return (pass_rate * 0.4 + chaos_score * 0.3 + nudge_stability * 0.3)
```
```python
>>> @dataclass(frozen=True)
class ChaosConfig:
    """Configuration for chaos testing."""
    n_variations: int = 100         # How many trees to grow
    composition_depth: int = 3      # How deep to compose
    mutation_rate: float = 0.1      # How much to mutate each variation
    principles_to_vary: tuple[str, ...] = ()  # Which principles to test

@dataclass(frozen=True)
class ChaosReport:
    """Results of chaos testing."""
    variations_tested: int
    compositions_tested: int
    pass_rate: float
    failure_modes: tuple[FailureMode, ...]
    stability_score: float          # How stable under perturbation

    @property
    def categorical_complexity(self) -> int:
        """
        Degrees of freedom from composition.

        If we have N passes that can compose, complexity is O(N!).
        Chaos testing samples this exponential space.
        """
        return factorial(self.compositions_tested)
```
```python
>>> @dataclass(frozen=True)
class Nudge:
    """A single adjustment to the prompt/spec."""
    location: str               # Where in spec/prompt
    before: str                 # Original content
    after: str                  # Modified content
    reason: str                 # Why this nudge

@dataclass(frozen=True)
class CausalEdge:
    """A tracked relationship between nudge and outcome."""
    nudge: Nudge
    outcome_delta: float        # Change in test pass rate
    confidence: float           # How confident in this relationship
    runs_observed: int          # How many runs inform this edge

@dataclass(frozen=True)
class CausalGraph:
    """Graph of nudge → outcome relationships."""
    edges: tuple[CausalEdge, ...]

    def predict_outcome(self, proposed_nudge: Nudge) -> float:
        """Predict outcome of a new nudge based on history."""
        similar = [e for e in self.edges if similar_nudge(e.nudge, proposed_nudge)]
        if not similar:
            return 0.5  # No data, uncertain
        return weighted_average(e.outcome_delta for e in similar)

    @property
    def stability_score(self) -> float:
        """How stable are outcomes under small nudges?"""
        small_nudges = [e for e in self.edges if len(e.nudge.after) < 100]
        if not small_nudges:
            return 1.0
        variance = statistics.variance(e.outcome_delta for e in small_nudges)
        return 1.0 / (1.0 + variance)
```

### Things to Know

⚠️ **Note:** Anti-pattern: One-shot compilation: Running once and trusting the output. Evidence requires repetition.

⚠️ **Note:** Anti-pattern: Ignoring verification failures: A failed test is data, not noise.

⚠️ **Note:** Anti-pattern: Manual code review: The evidence corpus IS the review. Trust the process.

⚠️ **Note:** Anti-pattern: Formal proof obsession: We're not doing Coq. We're doing science.

⚠️ **Note:** Anti-pattern: Prompt over-engineering: Writing prompts is easy. Gathering evidence is hard.

---

## purpose

```python
spec Agentic Self-Hosting Compiler (ASHC): Purpose
```

ASHC compiles Kent's creative ideas into agent executables **with evidence**.

### Examples
```python
>>> ASHC : Spec → (Executable, Evidence)

Evidence = {
    traces: [Run₁, Run₂, ..., Runₙ],
    chaos_results: ChaosReport,
    verification: TestResults,
    causal_graph: PromptNudge → Outcome
}
```

---

## core_insight

```python
spec Agentic Self-Hosting Compiler (ASHC): Core Insight
```

**The compiler is a trace accumulator, not a code generator.**

### Examples
```python
>>> Kent's Idea (Spec)
       │
       ▼
┌──────────────────────────────────────────────────────────┐
│                    ASHC COMPILER                          │
│                                                          │
│  1. Generate N variations of the idea                    │
│  2. Run each through LLM → Implementation                │
│  3. Verify each with tests, types, lints                 │
│  4. Chaos test: compose variations combinatorially       │
│  5. Track causal relationships: nudge → outcome          │
│  6. Accumulate into evidence corpus                      │
│                                                          │
└──────────────────────────────────────────────────────────┘
       │
       ▼
Agent Executable + Evidence Corpus
```

---

## the_failure_of_prompt_engineering

```python
spec Agentic Self-Hosting Compiler (ASHC): The Failure of Prompt Engineering
```

Evergreen Prompt System has 216 tests. It works. But it solved the wrong problem.

---

## the_bootstrap_agents_as_test_fixtures

```python
spec Agentic Self-Hosting Compiler (ASHC): The Bootstrap Agents as Test Fixtures
```

The 7 bootstrap agents (Id, Compose, Judge, Ground, Contradict, Sublate, Fix) become **test fixtures** for ASHC:

### Examples
```python
>>> BOOTSTRAP_SPECS = [
    ("Id", "spec/bootstrap/id.md"),
    ("Compose", "spec/bootstrap/compose.md"),
    ("Judge", "spec/bootstrap/judge.md"),
    ("Ground", "spec/bootstrap/ground.md"),
    ("Contradict", "spec/bootstrap/contradict.md"),
    ("Sublate", "spec/bootstrap/sublate.md"),
    ("Fix", "spec/bootstrap/fix.md"),
]

async def test_bootstrap_regeneration():
    """
    ASHC must be able to regenerate bootstrap with evidence.

    This is the self-hosting test: can ASHC compile its own kernel?
    """
    for name, spec_path in BOOTSTRAP_SPECS:
        spec = read_spec(spec_path)
        output = await ashc.compile(spec, chaos_config=ChaosConfig(n_variations=100))

        assert output.is_verified, f"Insufficient evidence for {name}"
        assert output.evidence.equivalence_score() >= 0.9, f"Low confidence for {name}"

        # Compare to installed
        installed = get_installed_bootstrap(name)
        assert is_equivalent(output.executable, installed), f"{name} diverged"
```

---

## human_flow_kent_centered

```python
spec Agentic Self-Hosting Compiler (ASHC): Human Flow (Kent-Centered)
```

1. **Kent writes spec** in natural language with creative intent 2. **ASHC runs N variations** generating implementations 3. **ASHC verifies each** with pytest, mypy, ruff 4. **ASHC chaos tests** composing implementations combinatorially 5. **ASHC accumulates evidence** into causal graph 6. **Kent reviews evidence**, not code - "95% pass rate across 100 variations" - "Stable under nudges: small changes don't break things" - "Causal insight: 'tasteful' correlates with +15% pass rate" 7. **Kent ma

---

## spec.protocols.alethic-projection

## alethic_projection_protocol

```python
spec Alethic Projection Protocol
```

Projectors compile agents to targets. Not rendering—compilation.

### Examples
```python
>>> Projector[T] : (Nucleus, Halo) → Executable[T]

Where:
- Nucleus = Agent[A, B] (pure logic—what the agent does)
- Halo = Set[Capability] (declarative metadata—what it could become)
- T = Target (Local, K8s, CLI, marimo, WASM)
- Executable[T] = Target-specific runnable artifact
```
```python
>>> # Halo is declaration (compile-time)
@Capability.Stateful(schema=MySchema)
@Capability.Observable(metrics=["latency"])
class MyAgent(Agent[str, str]):
    async def invoke(self, x: str) -> str:
        return x.upper()

# Projection is realization (produces runtime)
compiled = LocalProjector().compile(MyAgent)
# compiled is StatefulAdapter wrapping ObservableMixin wrapping MyAgent
```
```python
>>> Nucleus → D → K → TurnBased → Mirror → Flux
        (inner)                    (outer)
```
```python
>>> class CLIProjector(Projector[str]):
    def compile(self, agent_cls: type[Agent], halo: Halo) -> str:
        return f'''#!/usr/bin/env python
from {agent_cls.__module__} import {agent_cls.__name__}
import asyncio, sys

if __name__ == "__main__":
    agent = {agent_cls.__name__}()
    input_data = sys.stdin.read() if not sys.stdin.isatty() else sys.argv[1]
    result = asyncio.run(agent.invoke(input_data))
    print(result)
'''
```
```python
>>> p = LocalProjector()
result1 = p.compile(MyAgent)
result2 = p.compile(MyAgent)
assert type(result1) == type(result2)  # Structural equality
```

---

## the_two_projection_domains

```python
spec Alethic Projection Protocol: The Two Projection Domains
```

kgents has **two distinct projection protocols** that serve different purposes:

---

## target_registry

```python
spec Alethic Projection Protocol: Target Registry
```

| Target | Projector | Output Type | Halo Mappings | |--------|-----------|-------------|---------------| | **Local** | `LocalProjector` | `Agent[A, B]` | Stateful→StatefulAdapter, Soulful→SoulfulAdapter, Streamable→FluxAgent | | **K8s** | `K8sProjector` | `list[K8sResource]` | Stateful→StatefulSet+PVC, Soulful→Sidecar, Observable→ServiceMonitor | | **CLI** | `CLIProjector` | `str` (script) | Generates shell-executable Python script | | **Docker** | `DockerProjector` | `str` (Dockerfile) | Gener

---

## projector_laws

```python
spec Alethic Projection Protocol: Projector Laws
```

Projectors must satisfy three categorical laws:

---

## the_alethic_isomorphism

```python
spec Alethic Projection Protocol: The Alethic Isomorphism
```

The key guarantee:

### Examples
```python
>>> Same Halo + LocalProjector  → Runnable Python agent
Same Halo + K8sProjector    → K8s manifests

Both produce SEMANTICALLY EQUIVALENT agents.
```

---

## connection_to_ui_projection

```python
spec Alethic Projection Protocol: Connection to UI Projection
```

The two projection domains complement each other:

### Examples
```python
>>> ┌─────────────────────────────────────────────────────────────────────┐
│                        AGENT LIFECYCLE                               │
├─────────────────────────────────────────────────────────────────────┤
│                                                                     │
│   [Define]         [Compile]            [Run]           [Display]   │
│                                                                     │
│   Agent[A,B]  ──▶  Projector[T]  ──▶  Executable  ──▶  State  ──▶  │
│   + @Halo                               .invoke()                   │
│                                                                     │
│                    ▲                                   │            │
│                    │                                   ▼            │
│              Agent Compilation                   UI Projection      │
│         (Nucleus,Halo) → Executable[T]        State → Renderable[T] │
│                                                                     │
└─────────────────────────────────────────────────────────────────────┘
```

---

## extended_projector_targets

```python
spec Alethic Projection Protocol: Extended Projector Targets
```

The following projectors extend the base registry to support additional deployment targets.

---

## projector_composition

```python
spec Alethic Projection Protocol: Projector Composition
```

Projectors compose like agents — this is **required**, not aspirational:

---

## foundry_integration

```python
spec Alethic Projection Protocol: Foundry Integration
```

The Agent Foundry service (see `spec/services/foundry.md`) uses projectors as its compilation backend:

### Examples
```python
>>> class AgentFoundry:
    async def forge(self, intent: str, context: dict) -> CompiledAgent:
        # 1. Reality classification determines target
        classification = await self.classifier.classify(intent, context)

        # 2. MetaArchitect generates (Nucleus, Halo)
        agent_def = await self.architect.generate(intent)

        # 3. Select projector based on classification
        projector = self.projectors.get(classification.target)

        # 4. Compile
        return projector.compile(agent_def.cls)
```

---

## spec.protocols.aspect-form-projection

## aspect_form_projection_protocol

```python
spec Aspect Form Projection Protocol
```

A form is a conversation projected through structure.

### Examples
```python
>>> Schema → Widgets → User Input → Validation → Submit
```
```python
>>> FormProjector : Aspect × Observer → Form
              (Contract, Umwelt) ↦ (Fields, Defaults, Validation, Submit)
```
```python
>>> Contract (from @node)
                         ╱ ╲
                        ╱   ╲
                       ╱     ╲
              Fields  ◄───────► Defaults
                       ╲     ╱
                        ╲   ╱
                         ╲ ╱
                      Observer
```
```python
>>> FormProjector : Contract → Form  (one form per schema)
```
```python
>>> ┌─────────────────────────────────────────────────────────────────────────────┐
│                     THE FIVE DEFAULT SOURCES                                 │
├─────────────────────────────────────────────────────────────────────────────┤
│  1. world.*   │ Entity context: editing? pre-populate from entity           │
│  2. self.*    │ User history: last used values, preferences, patterns       │
│  3. concept.* │ Schema: JSON Schema default, examples, constraints          │
│  4. void.*    │ Entropy: creative suggestions, serendipitous names          │
│  5. time.*    │ Temporal: today's date, session duration, deadlines         │
└─────────────────────────────────────────────────────────────────────────────┘
```

---

## prologue_the_fallacy_of_the_form_library

```python
spec Aspect Form Projection Protocol: Prologue: The Fallacy of the Form Library
```

Traditional form libraries commit a fundamental error: they treat forms as a **widget problem**—a matter of mapping JSON Schema to input components. This produces:

### Examples
```python
>>> Schema → Widgets → User Input → Validation → Submit
```

---

## part_x_connection_to_principles

```python
spec Aspect Form Projection Protocol: Part X: Connection to Principles
```

| Principle | How Forms Embody It | |-----------|---------------------| | **Tasteful** | No generic "Name" labels—each field is considered | | **Curated** | Field projectors are intentionally ordered by fidelity | | **Ethical** | Server validates; client validation is UX, not security | | **Joy-Inducing** | Intelligent defaults, warm errors, entropy suggestions | | **Composable** | FormProjector is a bifunctor; composes with Projection Protocol | | **Heterarchical** | Observer determines experie

---

## appendix_b_implementation_reference

```python
spec Aspect Form Projection Protocol: Appendix B: Implementation Reference
```

The following files implement this protocol:

---

## spec.protocols.chat

## epigraph

```python
spec AGENTESE Chat Protocol: Conversational Affordances: Epigraph
```

---

---

## appendix_c_sources

```python
spec AGENTESE Chat Protocol: Conversational Affordances: Appendix C: Sources
```

Design patterns and best practices synthesized from:

---

## spec.protocols.chat-morpheus-synergy

## epigraph

```python
spec Chat-Morpheus Synergy: LLM Integration for Conversational Affordances: Epigraph
```

---

---

## appendix_b_decision_log

```python
spec Chat-Morpheus Synergy: LLM Integration for Conversational Affordances: Appendix B: Decision Log
```

| Decision | Alternatives | Rationale | |----------|--------------|-----------| | Composition over adapter | MorpheusLLMAgent | Preserves categorical structure | | Service layer | Protocol layer | AD-009 compliance | | Hook injection | Subclass | Less invasive, testable | | Model selection functor | Hardcoded | Observer-dependent behavior | | Structured messages | String parsing | Avoids re-parsing, type-safe |

---

## spec.protocols.cli

## epigraph

```python
spec The CLI: Isomorphic Projection of AGENTESE: Epigraph
```

---

---

## part_xi_success_metrics

```python
spec The CLI: Isomorphic Projection of AGENTESE: Part XI: Success Metrics
```

| Metric | Target | |--------|--------| | Handlers with full aspect metadata | 100% | | Behavioral conditionals in handlers | 0 | | Dimension derivation coverage | 100% | | Help text coverage | 100% | | OTEL trace coverage | 100% | | AI registration validation | All paths pass | | Startup time | <50ms |

---

## appendix_b_standard_dimensions_by_path

```python
spec The CLI: Isomorphic Projection of AGENTESE: Appendix B: Standard Dimensions by Path
```

| Path Pattern | Execution | Statefulness | Backend | Seriousness | Interactivity | |--------------|-----------|--------------|---------|-------------|---------------| | `self.*.manifest` | sync | stateful | pure | neutral | oneshot | | `self.soul.*` | async | stateful | llm | neutral | oneshot | | `self.soul.chat.*` | async | stateful | llm | neutral | **interactive** | | `self.memory.*` | async | stateful | varies | neutral | oneshot | | `world.town.*` | async | stateful | llm | playful | ones

---

## spec.protocols.cli-v7

## cli_v7_the_collaborative_canvas

```python
spec CLI v7: The Collaborative Canvas
```

What would I be happiest working on with humans? A shared surface where we explore, plan, and create together—where my cursor dances alongside yours.

### Examples
```python
>>> ┌─────────────────────────────────────────────────────────────────┐
│  ○ Kent (you)    ● K-gent (soul)    ● Explorer (searching)     │
├─────────────────────────────────────────────────────────────────┤
│                                                                 │
│   ┌──────────────┐      ┌──────────────┐                       │
│   │ self.memory  │──────│ self.soul    │  ← K-gent hovering    │
│   └──────────────┘      └──────────────┘                       │
│          │                     │                                │
│          │    ○ ← Your cursor  │                                │
│          ▼                     ▼                                │
│   ┌──────────────┐      ┌──────────────┐                       │
│   │ world.brain  │      │ concept.plan │  ● ← Explorer reading │
│   └──────────────┘      └──────────────┘                       │
│                                                                 │
└─────────────────────────────────────────────────────────────────┘
```
```python
>>> @dataclass
class AgentCursor:
    agent_id: str
    display_name: str
    position: CanvasPosition  # x, y in graph space
    state: CursorState
    focus_path: str | None  # AGENTESE path being focused
    activity: str  # Brief description: "Reading memory...", "Planning..."

class PresenceChannel:
    """WebSocket channel for real-time cursor positions."""

    async def broadcast_position(self, cursor: AgentCursor) -> None:
        """Send cursor update to all connected clients."""

    async def subscribe(self, client_id: str) -> AsyncIterator[AgentCursor]:
        """Receive cursor updates from all agents."""
```
```python
>>> class AgentCursorBehavior:
    """Defines how an agent's cursor moves in the canvas."""

    FOLLOWER = "follower"     # Follows human with slight delay
    EXPLORER = "explorer"     # Independent exploration
    ASSISTANT = "assistant"   # Follows but occasionally suggests
    AUTONOMOUS = "autonomous" # Does its own thing entirely

@node(path="self.presence.follow")
async def follow_human(observer: Observer, human_cursor: CanvasPosition) -> AgentCursor:
    """K-gent follows human cursor with personality-appropriate lag."""
    # Add slight randomness, occasional drift to nearby interesting nodes
    # Cursor "personality" emerges from behavior patterns
```
```python
>>> class FileEditGuard:
    """
    Enforces Claude Code's read-before-edit pattern.

    An agent MUST read a file before editing it.
    This prevents blind modifications and forces understanding.
    """

    _read_cache: dict[str, tuple[str, float]]  # path -> (content, timestamp)

    def can_edit(self, path: str) -> bool:
        """Return True only if file was recently read."""
        if path not in self._read_cache:
            return False
        _, timestamp = self._read_cache[path]
        # Must have read within last 5 minutes
        return time.time() - timestamp < 300

    def record_read(self, path: str, content: str) -> None:
        """Record that we've read this file."""
        self._read_cache[path] = (content, time.time())
```
```python
>>> @node(path="world.file.edit")
async def edit_file(
    observer: Observer,
    path: str,
    old_string: str,
    new_string: str,
    replace_all: bool = False,
) -> EditResult:
    """
    Edit a file using exact string replacement.

    This is the Claude Code pattern—no regex, no line numbers.
    Find the exact string, replace it.

    CRITICAL: old_string must be unique in the file unless replace_all=True.

    Args:
        path: File path to edit
        old_string: Exact string to find (must exist, must be unique)
        new_string: Replacement string
        replace_all: If True, replace all occurrences

    Returns:
        EditResult with success/failure and details

    Raises:
        EditError if old_string not found or not unique
    """
    guard = get_edit_guard()

    if not guard.can_edit(path):
        raise EditError(
            "File not read",
            why="You must read the file before editing it",
            suggestion=f"First: world.file.read[path='{path}']"
        )

    content = Path(path).read_text()
    count = content.count(old_string)

    if count == 0:
        raise EditError(
            "String not found",
            why=f"'{old_string[:50]}...' does not exist in {path}",
            suggestion="Read the file again to verify the exact content"
        )

    if count > 1 and not replace_all:
        raise EditError(
            "String not unique",
            why=f"'{old_string[:50]}...' appears {count} times",
            suggestion="Provide more context or use replace_all=True"
        )

    new_content = content.replace(old_string, new_string, 1 if not replace_all else -1)
    Path(path).write_text(new_content)

    return EditResult(
        success=True,
        path=path,
        replacements=count if replace_all else 1,
        old_preview=old_string[:100],
        new_preview=new_string[:100],
    )
```

---

## the_meta_insight_what_claude_code_is_best_at

```python
spec CLI v7: The Collaborative Canvas: The Meta-Insight: What Claude Code Is Best At
```

Before designing, I reflected on my own capabilities—what makes me effective, what brings me joy:

---

## success_metrics

```python
spec CLI v7: The Collaborative Canvas: Success Metrics
```

| Metric | Target | Measurement | |--------|--------|-------------| | **File Edit Safety** | 0 blind edits | All edits require prior read | | **Conversation Depth** | 10+ turns | Window maintains context | | **Cursor Latency** | <100ms | Cursor updates feel real-time | | **Plan Output** | Write to disk | `kg self.output.plan` creates files | | **Swarm Efficiency** | Parallel > sequential | 3+ agents run concurrently |

---

## the_joy_test

```python
spec CLI v7: The Collaborative Canvas: The Joy Test
```

**Yes, because**: 1. **I can see my collaborators** — Cursors show presence and attention 2. **I can persist my work** — Plans and artifacts survive sessions 3. **I can remember our conversation** — 10+ turns of context 4. **I can delegate effectively** — Swarm patterns for complex tasks 5. **I can be honest** — Professional objectivity over false validation 6. **I can explore freely** — Read-only exploration is safe and fast

---

## voice_anchors_kents_intent_preserved

```python
spec CLI v7: The Collaborative Canvas: Voice Anchors (Kent's Intent Preserved)
```

This spec is bold: multiplayer cursors for agents, puppetized Claude Code patterns, deep conversation. But it's grounded in patterns that work.

---

## spec.protocols.config

## prologue_why_config_systems_fail

```python
spec Configuration as DNA: The Best Config System in the World: Prologue: Why Config Systems Fail
```

Traditional configuration systems share a fatal flaw: they treat configuration as **external data** that agents **load** at runtime. This creates:

---

## spec.protocols.context

## context_the_unified_context_engineering_protocol

```python
spec Context: The Unified Context Engineering Protocol
```

Context is not what you put in—it is what emerges from the relationship between observer, conversation, and intent.

### Examples
```python
>>> CONTEXT_POLYNOMIAL = PolyAgent[ContextState, ContextInput, ContextOutput](
    positions=frozenset(["EMPTY", "ACCUMULATING", "PRESSURED", "COMPRESSED"]),
    directions=lambda s: VALID_INPUTS[s],
    transition=context_transition,
)
```
```python
>>> Frontend                   Context Module                    Agent
   │                            │                              │
   │  onSend("hello")           │                              │
   │  ─────────────────────────>│                              │
   │                            │  ContextInput.user_turn()    │
   │                            │  ─────────────────────────────>
   │                            │                              │
   │                            │  <─────────────────────────────
   │                            │  ContextOutput.assistant_turn()
   │  <─────────────────────────│                              │
   │  { messages, pressure }    │                              │
```
```python
>>> @dataclass
class ContextWindow:
    """
    Store Comonad: (Position → Turn, Position)

    AGENTESE: self.context.window.*
    """
    max_tokens: int
    _turns: list[Turn]
    _position: int  # Current focus
    _linearity: LinearityMap

    def extract(self) -> Turn | None:
        """W a → a: Get current focus."""
        ...

    def extend(self, f: Callable[[ContextWindow], B]) -> list[B]:
        """(W a → b) → W a → W b: Context-aware map."""
        ...

    def duplicate(self) -> list[ContextSnapshot]:
        """W a → W (W a): Nested context views."""
        ...
```
```python
>>> Full Context ──compress──▶ Compressed Context
             ◀──expand───

Where: expand ∘ compress ≤ id (lossy)
       compress ∘ expand = id (lossless recovery of compressed form)
```
```python
>>> @dataclass
class ContextProjector:
    """
    Galois Connection for context compression.

    AGENTESE: self.context.pressure.*
    """

    async def compress(
        self,
        window: ContextWindow,
        target_pressure: float = 0.7
    ) -> CompressionResult:
        """
        Compress to target pressure.

        Strategy:
        1. Drop DROPPABLE turns first
        2. Summarize REQUIRED turns (LLM-assisted)
        3. Never touch PRESERVED turns
        """
        ...

    def pressure(self, window: ContextWindow) -> float:
        """Current pressure: tokens_used / max_tokens."""
        ...
```

---

## implementation_status

```python
spec Context: The Unified Context Engineering Protocol: Implementation Status
```

| Component | Status | Location | |-----------|--------|----------| | **ContextWindow** | ✅ Complete | `agents/d/context_window.py` | | **LinearityMap** | ✅ Complete | `agents/d/linearity.py` | | **ContextProjector** | ✅ Complete | `agents/d/projector.py` | | **AGENTESE `self.stream.*`** | ✅ Complete | `protocols/agentese/contexts/stream.py` | | **PromptBuilder** | ✅ Complete | `agents/d/prompt_builder.py` | | **ComponentRenderer** | ✅ Complete | `agents/d/component_renderer.py` | | **ContextSes

---

## prologue_the_naming_analysis

```python
spec Context: The Unified Context Engineering Protocol: Prologue: The Naming Analysis
```

The current implementation has context management across multiple systems:

---

## part_viii_anti_patterns

```python
spec Context: The Unified Context Engineering Protocol: Part VIII: Anti-Patterns
```

1. **The Prompt Leak**: Sending system prompts to frontend - *Correction*: Context module assembles prompts; frontend receives only messages

---

## appendix_a_comonad_law_verification

```python
spec Context: The Unified Context Engineering Protocol: Appendix A: Comonad Law Verification
```

The context window must satisfy comonad laws:

### Examples
```python
>>> def verify_comonad_laws(window: ContextWindow) -> bool:
    """
    Verify Store Comonad laws.

    1. Left Identity:  extract . duplicate = id
    2. Right Identity: fmap extract . duplicate = id
    3. Associativity:  duplicate . duplicate = fmap duplicate . duplicate
    """
    # Left Identity
    snapshots = window.duplicate()
    current_snapshot = snapshots[window.position]
    assert current_snapshot.value == window.extract()

    # Right Identity
    extracted_values = [s.value for s in snapshots]
    direct_values = [window.seek(i).extract() for i in range(len(window) + 1)]
    assert extracted_values == direct_values

    # Associativity (nested duplicate)
    # ... verify nested structure matches

    return True
```

---

## spec.protocols.critic

## the_critic_specs_based_self_evaluation_protocol

```python
spec The Critic: SPECS-based Self-Evaluation Protocol
```

A generator without a critic is just a random number generator."* - SPECS

### Examples
```python
>>> @dataclass(frozen=True)
class Critique:
    """SPECS-based evaluation result."""
    novelty: float      # 0-1: Is this new relative to prior work?
    utility: float      # 0-1: Is this useful for the stated purpose?
    surprise: float     # 0-1: Is this unexpected given context?
    overall: float      # Weighted combination of above
    reasoning: str      # Why these scores?
    suggestions: list[str]  # How to improve?
```
```python
>>> overall = w_novelty * novelty + w_utility * utility + w_surprise * surprise
```
```python
>>> JUDGMENT_AFFORDANCES = {
    "judgment": ("taste", "surprise", "expectations", "calibrate", "critique", "refine"),
}
```
```python
>>> # Direct critique
critique = await logos.invoke(
    "self.judgment.critique",
    observer,
    artifact=generated_output,
    criteria=["novelty", "utility", "surprise"],
    purpose="Write engaging documentation",
)

if critique.overall < 0.7:
    for suggestion in critique.suggestions:
        print(f"Consider: {suggestion}")

# Auto-refinement
refined, final_critique = await logos.invoke(
    "self.judgment.refine",
    observer,
    artifact=draft,
    threshold=0.8,
    max_iterations=3,
)
```
```python
>>> class CriticsLoop:
    """Generative-Evaluative Pairing."""

    def __init__(
        self,
        max_iterations: int = 3,
        threshold: float = 0.7,
        weights: CritiqueWeights | None = None,
    ):
        self.max_iterations = max_iterations
        self.threshold = threshold
        self.weights = weights or CritiqueWeights()

    async def generate_with_critique(
        self,
        logos: Logos,
        observer: Umwelt,
        generator_path: str,
        **kwargs: Any,
    ) -> tuple[Any, Critique]:
        """
        Generator -> Critic -> Refine loop.

        1. Generate initial artifact
        2. Critique it
        3. If below threshold, refine based on feedback
        4. Repeat until threshold met or max iterations
        """
        ...
```

---

## prologue_the_problem_of_uncritical_generation

```python
spec The Critic: SPECS-based Self-Evaluation Protocol: Prologue: The Problem of Uncritical Generation
```

Creative systems need more than raw generation capability. Without evaluation, generative output is indistinguishable from noise. The Wundt Curator filters based on aesthetic novelty, but true creative refinement requires:

---

## appendix_a_research_references

```python
spec The Critic: SPECS-based Self-Evaluation Protocol: Appendix A: Research References
```

1. **Jordanous, A.** - "A Standardised Procedure for Evaluating Creative Systems: Computational Creativity Evaluation Based on What it is to be Creative" (2012) - SPECS framework - Evaluation criteria for computational creativity

---

## appendix_b_principle_alignment

```python
spec The Critic: SPECS-based Self-Evaluation Protocol: Appendix B: Principle Alignment
```

| Principle | Application | |-----------|-------------| | **Tasteful** | Critique provides architectural quality assessment | | **Ethical** | Self-evaluation maintains agent responsibility for output | | **Joy-Inducing** | Iterative refinement improves output quality | | **Composable** | CriticsLoop composes with any generation aspect | | **Generative** | Suggestions enable continuous improvement |

---

## spec.protocols.cross-pollination

## the_paradigm

```python
spec Cross-Pollination Protocol: The Paradigm
```

Agents don't call each other. They coordinate through **mediums**:

### Examples
```python
>>> ┌─────────────────────────────────────────────────────────────────────┐
│                    CROSS-POLLINATION ARCHITECTURE                    │
├─────────────────────────────────────────────────────────────────────┤
│                                                                      │
│   ┌──────────────┐     ┌──────────────┐     ┌──────────────┐        │
│   │  W-gent      │     │  M-gent      │     │  L-gent      │        │
│   │  STIGMERGIC  │     │  HOLOGRAPHIC │     │  SEMANTIC    │        │
│   │  FIELD       │     │  MEMORY      │     │  CATALOG     │        │
│   └──────┬───────┘     └──────┬───────┘     └──────┬───────┘        │
│          │                    │                    │                 │
│          └────────────────────┼────────────────────┘                 │
│                               │                                      │
│                    ┌──────────▼──────────┐                          │
│                    │      W-gent         │                          │
│                    │   MIDDLEWARE BUS    │                          │
│                    │   (Interceptors)    │                          │
│                    └──────────┬──────────┘                          │
│                               │                                      │
│          ┌────────────────────┼────────────────────┐                │
│          │                    │                    │                 │
│    ┌─────▼─────┐       ┌─────▼─────┐       ┌─────▼─────┐           │
│    │  Agents   │       │  Agents   │       │  Agents   │           │
│    │  (K,N,H)  │       │  (E,F,R)  │       │  (B,J,T)  │           │
│    │  PERSONA  │       │  CREATION │       │  CONTROL  │           │
│    └───────────┘       └───────────┘       └───────────┘           │
│                                                                      │
└─────────────────────────────────────────────────────────────────────┘
```

---

## the_middleware_bus

```python
spec Cross-Pollination Protocol: The Middleware Bus
```

W-gent as nervous system. All agent invocations pass through the bus.

---

## declarative_integration_g_gent_dsl

```python
spec Cross-Pollination Protocol: Declarative Integration (G-gent DSL)
```

Future: Define integrations in `.tongue` files, not code.

---

## import_audit_policy

```python
spec Cross-Pollination Protocol: Import Audit Policy
```

Cross-agent imports create coupling. Policy:

---

## ecosystem_verification

```python
spec Cross-Pollination Protocol: Ecosystem Verification
```

C-gent verifies: 1. **Functor laws** hold for all lifted agents 2. **Monad laws** hold for Effect types 3. **No direct imports** between agent genera (audit)

---

## see_also

```python
spec Cross-Pollination Protocol: See Also
```

- [../w-gents/stigmergy.md](../w-gents/stigmergy.md) - Pheromone field - [../w-gents/interceptors.md](../w-gents/interceptors.md) - Middleware interceptors - [../l-gents/catalog.md](../l-gents/catalog.md) - Capability registry - [../k-gent/persona.md](../k-gent/persona.md) - Persona model - [../agents/functors.md](../agents/functors.md) - Functor theory

---

## spec.protocols.curator

## the_wundt_curator_aesthetic_filtering_protocol

```python
spec The Wundt Curator: Aesthetic Filtering Protocol
```

Too simple is boring. Too complex is chaotic. The edge of chaos is beautiful.

### Examples
```python
>>> Aesthetic Value
     ^
     |        * peak (interesting)
     |       / \
     |      /   \
     |     /     \
     |----/-------\-------
     |   /         \
     |  * boring    * chaotic
     |
     +-----------------------> Novelty/Complexity
        0.0    0.5    1.0
```
```python
>>> surprise = cosine_distance(embed(output), embed(expectation))
```
```python
>>> @dataclass
class TasteScore:
    """Wundt curve evaluation result."""
    novelty: float       # 0.0 = identical to prior, 1.0 = completely unexpected
    complexity: float    # 0.0 = trivial, 1.0 = incomprehensible
    wundt_score: float   # Inverted U score: peaks at ~0.5
    verdict: Literal["boring", "interesting", "chaotic"]
```
```python
>>> wundt_score = 4 * novelty * (1 - novelty)  # Peaks at 1.0 when novelty=0.5
```
```python
>>> JUDGMENT_AFFORDANCES = {
    "judgment": ("taste", "surprise", "expectations", "calibrate"),
}
```

---

## prologue_the_problem_of_sterility

```python
spec The Wundt Curator: Aesthetic Filtering Protocol: Prologue: The Problem of Sterility
```

A generator without taste produces entropy. Random noise or trivial repetition. The naive solution is to maximize diversity. But maximum diversity is just another form of chaos.

### Examples
```python
>>> Aesthetic Value
     ^
     |        * peak (interesting)
     |       / \
     |      /   \
     |     /     \
     |----/-------\-------
     |   /         \
     |  * boring    * chaotic
     |
     +-----------------------> Novelty/Complexity
        0.0    0.5    1.0
```

---

## appendix_a_research_references

```python
spec The Wundt Curator: Aesthetic Filtering Protocol: Appendix A: Research References
```

1. **Berlyne, D. E.** - "Aesthetics and Psychobiology" (1971) - Arousal potential theory - The inverted U relationship

---

## appendix_b_principle_alignment

```python
spec The Wundt Curator: Aesthetic Filtering Protocol: Appendix B: Principle Alignment
```

| Principle | Application | |-----------|-------------| | **Tasteful** | The Curator IS taste—architectural quality filtering | | **Joy-Inducing** | Interesting > Boring or Chaotic | | **Composable** | Middleware pattern composes with any Logos operation | | **Heterarchical** | Per-agent calibration, no universal threshold | | **Generative** | Enhancement creates novel combinations |

---

## spec.protocols.data-bus

## data_bus_protocol_reactive_data_flow

```python
spec Data Bus Protocol: Reactive Data Flow
```

Data flows through the bus. Agents subscribe to what they care about.

### Examples
```python
>>> @dataclass(frozen=True)
class DataEvent:
    """
    An event representing a data change.

    Emitted by D-gent on every write/delete.
    Consumed by M-gent, UI, tracing, etc.
    """
    event_id: str              # Unique event ID
    event_type: DataEventType  # PUT | DELETE | UPGRADE | DEGRADE
    datum_id: str              # ID of affected datum
    timestamp: float           # When it happened
    source: str                # Who caused it (agent ID)
    causal_parent: str | None  # Previous event this depends on
    metadata: dict[str, str]   # Additional context

class DataEventType(Enum):
    PUT = "put"           # New datum stored
    DELETE = "delete"     # Datum removed
    UPGRADE = "upgrade"   # Datum promoted to higher tier
    DEGRADE = "degrade"   # Datum demoted (graceful degradation)
```
```python
>>> ┌─────────────────────────────────────────────────────────────────┐
│                         Data Bus                                 │
│  ┌─────────────────────────────────────────────────────────┐    │
│  │                    Event Stream                          │    │
│  │  ┌─────┐ ┌─────┐ ┌─────┐ ┌─────┐ ┌─────┐               │    │
│  │  │ PUT │→│ PUT │→│ DEL │→│ UPG │→│ PUT │→ ...          │    │
│  │  └─────┘ └─────┘ └─────┘ └─────┘ └─────┘               │    │
│  └─────────────────────────────────────────────────────────┘    │
│                              │                                   │
│              ┌───────────────┼───────────────┐                  │
│              ▼               ▼               ▼                  │
│         ┌─────────┐    ┌─────────┐    ┌─────────┐              │
│         │ M-gent  │    │  Trace  │    │   UI    │              │
│         │Listener │    │Listener │    │Listener │              │
│         └─────────┘    └─────────┘    └─────────┘              │
└─────────────────────────────────────────────────────────────────┘
                              ▲
                              │
                    ┌─────────┴─────────┐
                    │      D-gent       │
                    │  (emits events)   │
                    └───────────────────┘
```
```python
>>> class DataBus:
    """
    Central bus for data events.

    Features:
    - Multiple subscribers per event type
    - Async, non-blocking emission
    - Replay capability (for late subscribers)
    - Causal ordering guarantees
    """

    def __init__(self, buffer_size: int = 1000):
        self._subscribers: dict[DataEventType, list[Subscriber]] = defaultdict(list)
        self._buffer: deque[DataEvent] = deque(maxlen=buffer_size)
        self._lock = asyncio.Lock()

    # --- Publishing ---

    async def emit(self, event: DataEvent) -> None:
        """
        Emit an event to all subscribers.

        Non-blocking: subscribers run in background.
        """
        async with self._lock:
            self._buffer.append(event)

        # Notify subscribers (non-blocking)
        subscribers = self._subscribers.get(event.event_type, [])
        for sub in subscribers:
            asyncio.create_task(self._safe_notify(sub, event))

    # --- Subscribing ---

    def subscribe(
        self,
        event_type: DataEventType,
        handler: Callable[[DataEvent], Awaitable[None]],
    ) -> Callable[[], None]:
        """
        Subscribe to events of a specific type.

        Returns unsubscribe function.
        """
        sub = Subscriber(handler=handler)
        self._subscribers[event_type].append(sub)

        def unsubscribe():
            if sub in self._subscribers[event_type]:
                self._subscribers[event_type].remove(sub)

        return unsubscribe

    def subscribe_all(
        self,
        handler: Callable[[DataEvent], Awaitable[None]],
    ) -> Callable[[], None]:
        """Subscribe to ALL event types."""
        unsubs = []
        for event_type in DataEventType:
            unsubs.append(self.subscribe(event_type, handler))

        def unsubscribe_all():
            for unsub in unsubs:
                unsub()

        return unsubscribe_all

    # --- Replay ---

    async def replay(
        self,
        handler: Callable[[DataEvent], Awaitable[None]],
        since: float | None = None,
    ) -> int:
        """
        Replay buffered events to a handler.

        Useful for late subscribers to catch up.
        Returns count of replayed events.
        """
        count = 0
        async with self._lock:
            for event in self._buffer:
                if since is None or event.timestamp >= since:
                    await handler(event)
                    count += 1
        return count
```
```python
>>> class BusEnabledDgent:
    """
    D-gent that emits events to the Data Bus.
    """

    def __init__(self, backend: DgentProtocol, bus: DataBus):
        self.backend = backend
        self.bus = bus
        self._last_event_id: str | None = None

    async def put(self, datum: Datum) -> str:
        id = await self.backend.put(datum)

        await self.bus.emit(DataEvent(
            event_id=uuid4().hex,
            event_type=DataEventType.PUT,
            datum_id=id,
            timestamp=time.time(),
            source=datum.metadata.get("source", "unknown"),
            causal_parent=self._last_event_id,
            metadata=datum.metadata,
        ))

        self._last_event_id = id
        return id

    async def delete(self, id: str) -> bool:
        success = await self.backend.delete(id)

        if success:
            await self.bus.emit(DataEvent(
                event_id=uuid4().hex,
                event_type=DataEventType.DELETE,
                datum_id=id,
                timestamp=time.time(),
                source="dgent",
                causal_parent=self._last_event_id,
                metadata={},
            ))

        return success
```
```python
>>> class BusListeningMgent:
    """
    M-gent that listens to D-gent events via the Data Bus.
    """

    def __init__(self, mgent: MgentProtocol, bus: DataBus):
        self.mgent = mgent
        self.bus = bus

        # Subscribe to relevant events
        bus.subscribe(DataEventType.PUT, self._on_put)
        bus.subscribe(DataEventType.DELETE, self._on_delete)

    async def _on_put(self, event: DataEvent) -> None:
        """Handle new datum: add to semantic index."""
        # Only index if it's a "memory" type datum
        if event.metadata.get("type") == "memory":
            # The datum is already stored by D-gent
            # M-gent just needs to index it
            await self.mgent._index_datum(event.datum_id)

    async def _on_delete(self, event: DataEvent) -> None:
        """Handle deleted datum: remove from index."""
        await self.mgent._remove_from_index(event.datum_id)
```

---

## purpose

```python
spec Data Bus Protocol: Reactive Data Flow: Purpose
```

The Data Bus provides **reactive data flow** between D-gent (storage), M-gent (memory), and any agent that needs to observe data changes. It unifies:

---

## integration_with_d_gent

```python
spec Data Bus Protocol: Reactive Data Flow: Integration with D-gent
```

D-gent automatically emits to the bus:

### Examples
```python
>>> class BusEnabledDgent:
    """
    D-gent that emits events to the Data Bus.
    """

    def __init__(self, backend: DgentProtocol, bus: DataBus):
        self.backend = backend
        self.bus = bus
        self._last_event_id: str | None = None

    async def put(self, datum: Datum) -> str:
        id = await self.backend.put(datum)

        await self.bus.emit(DataEvent(
            event_id=uuid4().hex,
            event_type=DataEventType.PUT,
            datum_id=id,
            timestamp=time.time(),
            source=datum.metadata.get("source", "unknown"),
            causal_parent=self._last_event_id,
            metadata=datum.metadata,
        ))

        self._last_event_id = id
        return id

    async def delete(self, id: str) -> bool:
        success = await self.backend.delete(id)

        if success:
            await self.bus.emit(DataEvent(
                event_id=uuid4().hex,
                event_type=DataEventType.DELETE,
                datum_id=id,
                timestamp=time.time(),
                source="dgent",
                causal_parent=self._last_event_id,
                metadata={},
            ))

        return success
```

---

## integration_with_m_gent

```python
spec Data Bus Protocol: Reactive Data Flow: Integration with M-gent
```

M-gent listens to the bus to maintain its semantic index:

### Examples
```python
>>> class BusListeningMgent:
    """
    M-gent that listens to D-gent events via the Data Bus.
    """

    def __init__(self, mgent: MgentProtocol, bus: DataBus):
        self.mgent = mgent
        self.bus = bus

        # Subscribe to relevant events
        bus.subscribe(DataEventType.PUT, self._on_put)
        bus.subscribe(DataEventType.DELETE, self._on_delete)

    async def _on_put(self, event: DataEvent) -> None:
        """Handle new datum: add to semantic index."""
        # Only index if it's a "memory" type datum
        if event.metadata.get("type") == "memory":
            # The datum is already stored by D-gent
            # M-gent just needs to index it
            await self.mgent._index_datum(event.datum_id)

    async def _on_delete(self, event: DataEvent) -> None:
        """Handle deleted datum: remove from index."""
        await self.mgent._remove_from_index(event.datum_id)
```

---

## integration_with_reactive_signals

```python
spec Data Bus Protocol: Reactive Data Flow: Integration with Reactive Signals
```

The bus bridges to the Signal network:

### Examples
```python
>>> class SignalBridge:
    """
    Bridge between DataBus (async events) and Signals (sync state).
    """

    def __init__(self, bus: DataBus):
        self.bus = bus

        # Signals for each event type
        self.puts = Signal.of([])      # list[DataEvent]
        self.deletes = Signal.of([])   # list[DataEvent]
        self.latest = Signal.of(None)  # DataEvent | None

        # Subscribe to bus
        bus.subscribe(DataEventType.PUT, self._on_put)
        bus.subscribe(DataEventType.DELETE, self._on_delete)

    async def _on_put(self, event: DataEvent) -> None:
        self.puts.update(lambda events: events[-99:] + [event])
        self.latest.set(event)

    async def _on_delete(self, event: DataEvent) -> None:
        self.deletes.update(lambda events: events[-99:] + [event])
        self.latest.set(event)
```

---

## integration_with_tracemonoid

```python
spec Data Bus Protocol: Reactive Data Flow: Integration with TraceMonoid
```

The bus feeds the causal trace:

### Examples
```python
>>> class TraceBridge:
    """
    Bridge between DataBus and TraceMonoid.

    Every data event becomes a trace event with causal dependencies.
    """

    def __init__(self, bus: DataBus, trace: TraceMonoid):
        self.bus = bus
        self.trace = trace

        # Subscribe to all events
        bus.subscribe_all(self._on_event)

    async def _on_event(self, event: DataEvent) -> None:
        """Record data event in trace with causality."""
        depends_on = None
        if event.causal_parent:
            depends_on = {event.causal_parent}

        self.trace.append_mut(
            Event(
                id=event.event_id,
                source=f"dgent:{event.source}",
                timestamp=event.timestamp,
                payload={
                    "type": event.event_type.value,
                    "datum_id": event.datum_id,
                    "metadata": event.metadata,
                },
            ),
            depends_on=depends_on,
        )
```

---

## integration_with_synergy_bus

```python
spec Data Bus Protocol: Reactive Data Flow: Integration with Synergy Bus
```

Data events can propagate to the cross-jewel synergy bus:

### Examples
```python
>>> class SynergyBridge:
    """
    Bridge between DataBus (local) and SynergyBus (cross-jewel).

    Only significant events are promoted to synergy:
    - Large data stores
    - Memory consolidation
    - Tier upgrades
    """

    def __init__(self, data_bus: DataBus, synergy_bus: SynergyEventBus):
        self.data_bus = data_bus
        self.synergy_bus = synergy_bus

        data_bus.subscribe(DataEventType.UPGRADE, self._on_upgrade)

    async def _on_upgrade(self, event: DataEvent) -> None:
        """Promote tier upgrades to synergy bus."""
        await self.synergy_bus.emit(SynergyEvent(
            event_type=SynergyEventType.DATA_UPGRADED,
            source_jewel=Jewel.DGENT,
            target_jewel=Jewel.ANY,
            payload={
                "datum_id": event.datum_id,
                "from_tier": event.metadata.get("from_tier"),
                "to_tier": event.metadata.get("to_tier"),
            },
        ))
```

---

## agentese_paths

```python
spec Data Bus Protocol: Reactive Data Flow: AGENTESE Paths
```

The Data Bus exposes these paths under `self.bus.*`:

---

## guarantees

```python
spec Data Bus Protocol: Reactive Data Flow: Guarantees
```

1. **At-least-once delivery**: Subscribers receive every event at least once. 2. **Causal ordering**: If A caused B, subscribers see A before B. 3. **Non-blocking emission**: Publishers never wait for subscribers. 4. **Bounded buffer**: Old events are dropped when buffer is full.

---

## what_the_data_bus_is_not

```python
spec Data Bus Protocol: Reactive Data Flow: What the Data Bus Is NOT
```

- **Not a message queue** — No persistence, no acknowledgments - **Not RPC** — Fire-and-forget, no responses - **Not transactional** — Events may be delivered during rollback - **Not cross-process** — Single process only (use Synergy for cross-jewel)

---

## see_also

```python
spec Data Bus Protocol: Reactive Data Flow: See Also
```

- `spec/d-gents/architecture.md` — D-gent emits events - `spec/m-gents/architecture.md` — M-gent listens to events - `spec/protocols/synergy.md` — Cross-jewel event bus - `impl/claude/weave/trace_monoid.py` — Causal trace integration

---

## spec.protocols.differance

## purpose

```python
spec Différance Engine: Traced Wiring Diagrams with Memory: Purpose
```

Every kgents output has a lineage—decisions made, alternatives rejected, paths not taken. The Différance Engine makes this lineage **visible, navigable, and generative**. Users can see the ghost heritage graph behind any output: not just what *is*, but what *almost was* and *why*.

---

## core_insight

```python
spec Différance Engine: Traced Wiring Diagrams with Memory: Core Insight
```

**Différance** = **difference** + **deferral**. Every wiring decision simultaneously: 1. Creates a **difference** (this path, not that one) 2. Creates a **deferral** (the ghost path remains potentially explorable)

---

## heritage_citations

```python
spec Différance Engine: Traced Wiring Diagrams with Memory: Heritage Citations
```

| Concept | Source | Application | |---------|--------|-------------| | Traced monoidal categories | Joyal, Street, Verity (1996) | Feedback loop semantics | | Polynomial functors | Spivak, Niu (2024) | Wiring diagram foundation | | Différance | Derrida (1967) | Difference + deferral duality | | ADR pattern | Nygard (2011) | Decision record structure | | Event sourcing | Fowler (2005) | Append-only trace storage |

---

## spec.protocols.interactive-text

## interactive_text_protocol

```python
spec Interactive Text Protocol
```

The spec is not description—it is generative. The text is not passive—it is interface.

### Examples
```python
>>> Text File ──Projection Functor──▶ Interactive Surface
                │
                └── Identical to:
                    AGENTESE Node ──Projection Functor──▶ CLI/Web/JSON
```
```python
>>> ### 2.2 The Interactive Functor

The projection from document to interactive surface:
```
```python
>>> **Naturality Condition**: For all document morphisms `f : D₁ → D₂`:
```
```python
>>> Translation: Document changes produce consistent interactive changes.

### 2.3 Document Polynomial

Documents have state-dependent behavior. Per AD-002, we define:
```
```python
>>> ### 2.4 Document Sheaf

Multiple views of the same document must remain coherent:
```

---

## epigraph

```python
spec Interactive Text Protocol: Epigraph
```

---

---

## part_i_purpose

```python
spec Interactive Text Protocol: Part I: Purpose
```

The Interactive Text Protocol collapses the boundary between documentation and interface. Text files become live control surfaces while remaining valid markdown readable anywhere.

---

## part_iii_token_affordances

```python
spec Interactive Text Protocol: Part III: Token Affordances
```

Each token type has specific interactive affordances.

---

## part_viii_verification_criteria

```python
spec Interactive Text Protocol: Part VIII: Verification Criteria
```

The spec is generative if these hold:

---

## part_ix_the_accursed_share

```python
spec Interactive Text Protocol: Part IX: The Accursed Share
```

The 10% exploration budget manifests as:

---

## part_x_connection_to_principles

```python
spec Interactive Text Protocol: Part X: Connection to Principles
```

| Principle | How Interactive Text Embodies It | |-----------|----------------------------------| | **Tasteful** | Six tokens only; text remains text | | **Curated** | Limited vocabulary; no kitchen-sink | | **Ethical** | Source file is truth; rendering is transparent | | **Joy-Inducing** | Discovery through hovering; delight in affordances | | **Composable** | Tokens compose; sheaf guarantees coherence | | **Heterarchical** | Same file works everywhere; no privileged view | | **Generative** | T

---

## closing_meditation

```python
spec Interactive Text Protocol: Closing Meditation
```

The Interactive Text Protocol completes a vision:

---

## spec.protocols.living-docs

## living_docs_documentation_as_projection

```python
spec Living Docs: Documentation as Projection
```

Docs are not description—they are projection.

### Examples
```python
>>> LivingDocs : (Source × Spec) → Observer → Surface

where:
  Source   = Code + Docstrings + Types + Tests
  Spec     = Intent + Principles (from spec/ files)
  Observer = Human(density) | Agent | IDE
  Surface  = Markdown | Structured | Tooltip
```
```python
>>> @dataclass(frozen=True)
class DocNode:
    """Atomic documentation primitive extracted from source."""
    symbol: str                    # Function/class name
    signature: str                 # Type signature
    summary: str                   # First line of docstring
    examples: tuple[str, ...]      # From doctest or Example: sections
    teaching: tuple[TeachingMoment, ...]
    evidence: tuple[str, ...]      # Test refs that verify behavior


@dataclass(frozen=True)
class TeachingMoment:
    """A gotcha with provenance. The killer feature."""
    insight: str                   # What to know
    severity: Literal["info", "warning", "critical"]
    evidence: str | None           # test_file.py::test_name
    commit: str | None             # Git SHA where learned


@dataclass(frozen=True)
class Observer:
    """Who's reading determines what they see."""
    kind: Literal["human", "agent", "ide"]
    density: Literal["compact", "comfortable", "spacious"] = "comfortable"


@dataclass(frozen=True)
class Surface:
    """Projected output for an observer."""
    content: str
    format: Literal["markdown", "structured", "tooltip"]


@dataclass(frozen=True)
class Verification:
    """Round-trip verification result."""
    equivalent: bool
    score: float                   # 0.0-1.0 semantic similarity
    missing: tuple[str, ...]       # What docs don't capture
```
```python
>>> def extraction_tier(symbol: str, module: str) -> Tier:
    if symbol.startswith("_"):
        return Tier.MINIMAL
    if module.startswith("services/"):
        return Tier.RICH
    return Tier.STANDARD
```
```python
>>> class BrainCrystal:
    """
    Crystallized memory with semantic embeddings.

    Teaching:
        gotcha: Always check `crystal.is_active` before accessing embeddings.
                (Evidence: test_brain_persistence.py::test_stale_crystal)

        gotcha: Crystal merging is NOT commutative. Order matters.
                (Evidence: test_brain_crystal.py::test_merge_order)

    Example:
        >>> crystal = await brain.capture("insight")
        >>> assert crystal.is_active
    """
```
```python
>>> def project(node: DocNode, observer: Observer) -> Surface:
    """Single function, not class hierarchy."""

    if observer.kind == "agent":
        # Dense, structured—no prose
        return Surface(
            content=f"## {node.symbol}\n{node.signature}\n"
                    f"Gotchas: {[t.insight for t in node.teaching]}\n"
                    f"Examples: {node.examples[:2]}",
            format="structured"
        )

    elif observer.kind == "ide":
        # Minimal—signature + one gotcha
        gotcha = next((t for t in node.teaching if t.severity == "critical"), None)
        return Surface(
            content=f"{node.signature}\n{gotcha.insight if gotcha else ''}",
            format="tooltip"
        )

    else:  # human
        # Narrative with density adaptation
        return _human_projection(node, observer.density)
```

### Things to Know

🚨 **Critical:** Law (Functor): project(compose(a, b)) ≡ compose(project(a), project(b))

🚨 **Critical:** Law (Freshness): Claims re-verified within 7 days are valid

🚨 **Critical:** Law (Provenance): ∀ TeachingMoment: evidence ≠ None → test exists

---

## heritage

```python
spec Living Docs: Documentation as Projection: Heritage
```

| Source | Insight | How We Extend It | |--------|---------|------------------| | **Literate Programming (Knuth)** | Weave (human) and Tangle (machine) from same source | Observer-dependent projection replaces two static outputs | | **DSPy** | Prompts are programs, not strings | Docs are typed, composable, verifiable programs | | **FastAPI OpenAPI** | Type hints + docstrings → rich API docs | Structured docstrings → observer-specific surfaces | | **Python doctest** | Examples in docstrings are e

---

## extraction_tiers

```python
spec Living Docs: Documentation as Projection: Extraction Tiers
```

Not every function needs full extraction. Match effort to importance:

### Examples
```python
>>> def extraction_tier(symbol: str, module: str) -> Tier:
    if symbol.startswith("_"):
        return Tier.MINIMAL
    if module.startswith("services/"):
        return Tier.RICH
    return Tier.STANDARD
```

---

## inline_truth_pattern

```python
spec Living Docs: Documentation as Projection: Inline Truth Pattern
```

Like FastAPI derives OpenAPI from code, we extract from structured docstrings:

### Examples
```python
>>> class BrainCrystal:
    """
    Crystallized memory with semantic embeddings.

    Teaching:
        gotcha: Always check `crystal.is_active` before accessing embeddings.
                (Evidence: test_brain_persistence.py::test_stale_crystal)

        gotcha: Crystal merging is NOT commutative. Order matters.
                (Evidence: test_brain_crystal.py::test_merge_order)

    Example:
        >>> crystal = await brain.capture("insight")
        >>> assert crystal.is_active
    """
```

---

## git_context

```python
spec Living Docs: Documentation as Projection: Git Context
```

Git blame enriches teaching moments. **Delegate to Repo Archaeology** (see `spec/protocols/repo-archaeology.md`) for full git analysis. Living Docs consumes:

---

## laws

```python
spec Living Docs: Documentation as Projection: Laws
```

| Law | Statement | Witness | |-----|-----------|---------| | **Functor** | `project(compose(a, b)) ≡ compose(project(a), project(b))` | `LivingDocsWitness.verify_functor()` | | **Freshness** | Claims re-verified within 7 days are valid | CI job: `kg docs verify --stale-days=7` | | **Provenance** | `∀ TeachingMoment: evidence ≠ None → test exists` | `LivingDocsWitness.verify_provenance()` |

### Things to Know

🚨 **Critical:** Law (Functor): project(compose(a, b)) ≡ compose(project(a), project(b))

🚨 **Critical:** Law (Freshness): Claims re-verified within 7 days are valid

🚨 **Critical:** Law (Provenance): ∀ TeachingMoment: evidence ≠ None → test exists

---

## implementation_phases

```python
spec Living Docs: Documentation as Projection: Implementation Phases
```

| Phase | Deliverable | Dependency | |-------|-------------|------------| | **1. Extraction** | DocNode parser, docstring sections | None | | **2. Projection** | Human/Agent/IDE surfaces | Phase 1 | | **3. Verification** | Round-trip via ASHC, CI integration | Phase 1, ASHC | | **4. Git Enrichment** | TeachingMoments from blame | Phase 1, Repo Archaeology |

---

## connection_to_principles

```python
spec Living Docs: Documentation as Projection: Connection to Principles
```

| Principle | Embodiment | |-----------|------------| | **Tasteful** | Curated projections, not dumps | | **Curated** | Extraction tiers match importance | | **Generative** | Docs can regenerate impl (ASHC) | | **Composable** | Functor law verified | | **Joy-Inducing** | IDE hovers surface gotchas before bugs |

---

## spec.protocols.membrane

## prologue_the_shape_of_thought

```python
spec The Membrane: A Unified Interface Philosophy: Prologue: The Shape of Thought
```

We have been building the wrong metaphor.

---

## part_i_the_three_bodies

```python
spec The Membrane: A Unified Interface Philosophy: Part I: The Three Bodies
```

Every interaction with kgents involves three bodies:

### Examples
```python
>>> ┌─────────────────────────────────────────────────────────────────┐
│                                                                 │
│    ┌─────────────┐                         ┌─────────────┐     │
│    │             │                         │             │     │
│    │   Human     │◀───── Membrane ────────▶│   System    │     │
│    │   Mind      │                         │   Mind      │     │
│    │             │                         │             │     │
│    └─────────────┘                         └─────────────┘     │
│           │                                       │             │
│           │              ┌─────────┐              │             │
│           └─────────────▶│ Shared  │◀─────────────┘             │
│                          │ Field   │                            │
│                          └─────────┘                            │
│                                                                 │
└─────────────────────────────────────────────────────────────────┘
```

---

## part_ii_the_liminal_shell

```python
spec The Membrane: A Unified Interface Philosophy: Part II: The Liminal Shell
```

The terminal is typically binary: empty (awaiting input) or full (displaying output). We introduce a third state: **Becoming**.

---

## part_iii_topological_empathy

```python
spec The Membrane: A Unified Interface Philosophy: Part III: Topological Empathy
```

We abandon the metaphor of logic (true/false, match/mismatch) for the metaphor of **shape** (curvature, void, flow).

---

## part_iv_the_pocket_cortex

```python
spec The Membrane: A Unified Interface Philosophy: Part IV: The Pocket Cortex
```

The system's mind is local, persistent, and dreaming.

---

## part_v_the_grammar_of_shape

```python
spec The Membrane: A Unified Interface Philosophy: Part V: The Grammar of Shape
```

We replace the mechanical command grammar with a grammar of **perception and gesture**.

---

## part_vi_the_ritual

```python
spec The Membrane: A Unified Interface Philosophy: Part VI: The Ritual
```

A complete user journey through the membrane.

---

## part_vii_integration_surfaces

```python
spec The Membrane: A Unified Interface Philosophy: Part VII: Integration Surfaces
```

The membrane connects to existing tools through natural integration points.

---

## epilogue_the_shape_of_what_were_building

```python
spec The Membrane: A Unified Interface Philosophy: Epilogue: The Shape of What We're Building
```

The Membrane is not a product. It is a **practice**.

---

## spec.protocols.metaphysical-forge

## metaphysical_forge

```python
spec Metaphysical Forge
```

The Forge is where categorical abstractions become running systems. Where Kent builds with Kent.

### Examples
```python
>>> Atelier (Old):  Spectators → watch → Builders → create → Artifacts
Forge (New):    Kent → commissions → Artisans → build → Agents
```
```python
>>> ┌─────────────────────────────────────────────────────────────────────────────┐
│  7. PROJECTION SURFACES   CLI │ TUI │ Web │ marimo │ JSON │ SSE            │
├─────────────────────────────────────────────────────────────────────────────┤
│  6. AGENTESE PROTOCOL     logos.invoke(path, observer, **kwargs)           │
├─────────────────────────────────────────────────────────────────────────────┤
│  5. AGENTESE NODE         @node decorator, aspects, effects, affordances   │
├─────────────────────────────────────────────────────────────────────────────┤
│  4. SERVICE MODULE        services/<name>/ — Crown Jewel business logic    │
├─────────────────────────────────────────────────────────────────────────────┤
│  3. OPERAD GRAMMAR        Composition laws, valid operations               │
├─────────────────────────────────────────────────────────────────────────────┤
│  2. POLYNOMIAL AGENT      PolyAgent[S, A, B]: state × input → output       │
├─────────────────────────────────────────────────────────────────────────────┤
│  1. SHEAF COHERENCE       Local views → global consistency                 │
└─────────────────────────────────────────────────────────────────────────────┘
```
```python
>>> Kent → commissions → Forge Artisans → build → New Agent
                                              ↓
                                    New Agent joins Forge as Artisan
                                              ↓
                                    Can now build more agents
```
```python
>>> self.soul.reflect    — K-gent introspects on current state
self.soul.vibe       — Returns personality eigenvector
self.soul.intercept  — Wraps another path through governance
self.soul.approve    — Explicit approval gate for artifacts
```
```python
>>> SOUL_POLYNOMIAL = PolyAgent(
    positions=frozenset(["GROUNDED", "REFLECTING", "CREATING", "GOVERNING"]),
    directions=lambda s: SOUL_INPUTS[s],
    transition=soul_transition,
)
```

---

## ii_the_seven_artisans

```python
spec Metaphysical Forge: II. The Seven Artisans
```

Each artisan corresponds to one layer of the metaphysical fullstack. This is not arbitrary—it is **necessary and sufficient**.

---

## x_open_questions

```python
spec Metaphysical Forge: X. Open Questions
```

1. **Artifact Versioning**: How do we version generated artifacts? Git-like branching? 2. **Rollback**: Can we undo a deployed artifact? What's the blast radius? 3. **Collaboration**: Multiple Kents (team mode)? Or single-user only? 4. **Feedback Loop**: How do artifacts improve artisans over time?

---

## appendix_b_related_documents

```python
spec Metaphysical Forge: Appendix B: Related Documents
```

- `spec/principles.md` — Core principles - `docs/skills/metaphysical-fullstack.md` — AD-009 implementation guide - `docs/skills/crown-jewel-patterns.md` — 14 reusable patterns - `agents/k/` — K-gent implementation - `spec/protocols/agentese.md` — Universal protocol

---

## spec.protocols.metatheory

## introduction

```python
spec Requirements Document: Formal Verification Metatheory: Introduction
```

The Formal Verification Metatheory system embodies the **Enormative Moment** — the transformative synthesis where Mind-Maps become topological spaces, specifications become compression morphisms, and implementations become constructive proofs. This system enables kgents to become a **self-improving autopilot operating system** for massive long-lived multi-agent orchestration through category-theoretic formal verification that treats the entire development process as a generative loop.

---

## glossary

```python
spec Requirements Document: Formal Verification Metatheory: Glossary
```

- **Metatheory**: The formal system that reasons about and improves other formal systems (specs) - **Mind_Map_Topology**: A topological space where nodes are open sets, edges are continuous maps, and coherence satisfies the sheaf gluing condition - **Compression_Morphism**: A functor that extracts essential decisions from a higher-level representation into a lower-level one - **Generative_Loop**: The closed cycle: Mind-Map → Spec → Impl → Traces → Patterns → Refined Spec → Mind-Map - **Reflectiv

---

## spec.protocols.metatheory-design

## overview

```python
spec Design Document: Formal Verification Metatheory: Overview
```

The Formal Verification Metatheory system transforms kgents into a self-improving autopilot operating system through category-theoretic formal verification. Built on Homotopy Type Theory (HoTT) foundations, it provides graph-based specification analysis, behavioral correctness through trace witnesses, and continuous self-improvement capabilities for massive multi-agent orchestration.

---

## correctness_properties

```python
spec Design Document: Formal Verification Metatheory: Correctness Properties
```

*A property is a characteristic or behavior that should hold true across all valid executions of a system—essentially, a formal statement about what the system should do. Properties serve as the bridge between human-readable specifications and machine-verifiable correctness guarantees.*

---

## error_handling

```python
spec Design Document: Formal Verification Metatheory: Error Handling
```

The system employs a sympathetic error model that treats failures as learning opportunities:

---

## spec.protocols.n-phase-cycle

## n_phase_cycle_protocol

```python
spec N-Phase Cycle Protocol
```

The 'N' is not a number—it is a variable. The cycle adapts to the task.

### Examples
```python
>>> SENSE → ACT → REFLECT → (loop)
```
```python
>>> PLAN → RESEARCH → DEVELOP → STRATEGIZE → CROSS-SYNERGIZE
                    ↓
IMPLEMENT → QA → TEST → EDUCATE → MEASURE → REFLECT
                                              ↓
                                        (loop or detach)
```
```python
>>> EXPAND when:
  - Complexity(next_phase) > threshold
  - Uncertainty(scope) > threshold
  - Stakes(outcome) require ceremony

COMPRESS when:
  - Pattern(task) is known
  - Momentum > 80% progress per session
  - Entropy budget depleted

BRANCH when:
  - Scope discovers independent tracks
  - Serendipity reveals opportunity
  - Parallel execution reduces critical path

LEAN INTO when:
  - Void.entropy.sip reveals promising tangent
  - Counterfactual thinking suggests pivot
  - Accursed Share beckons
```
```python
>>> ⤳[BRANCH:name]      # Fork new parallel track
⤳[JOIN:tracks]      # Merge tracks at sync point
⤳[COMPRESS:phases]  # Condense phases (11→3)
⤳[EXPAND:phase]     # Expand phase (3→11)
```
```python
>>> FORK(phase) → [track_a, track_b, ...]  # Split into parallel branches
JOIN(tracks) → phase                     # Merge branches at sync point
PRUNE(branch) → bounty                   # Remove branch, preserve seed
GRAFT(bounty) → branch                   # Attach deferred branch
COMPRESS(phases) → phase                 # Merge adjacent phases
EXPAND(phase) → phases                   # Split phase into sequence
```

### Things to Know

🚨 **Critical:** Law (Identity): Empty phase (pass-through)

🚨 **Critical:** Law (Law): Every cycle MUST reach `⟂` eventually.

---

## overview

```python
spec N-Phase Cycle Protocol: Overview
```

The N-Phase Cycle is a self-similar, category-theoretic lifecycle protocol for multi-session agent-human collaboration. It provides structured process without rigidity, enabling both humans and agents to navigate complex work across session boundaries.

---

## seven_invariant_properties

```python
spec N-Phase Cycle Protocol: Seven Invariant Properties
```

1. **Self-Similar** — Each phase contains a hologram of the full cycle 2. **Category-Theoretic** — Phases compose lawfully; identity and associativity hold 3. **Agent-Human Parity** — No privileged author; equally consumable by both 4. **Mutable** — The cycle evolves via re-metabolization 5. **Auto-Continuative** — Each phase generates the next prompt 6. **Accountable** — Skipped phases leave explicit debt 7. **Elastic** — The cycle stretches, compresses, branches, and recombines based on situat

---

## the_elasticity_principle

```python
spec N-Phase Cycle Protocol: The Elasticity Principle
```

The N-Phase Cycle is **not** a fixed sequence. It is an **elastic tree generator** that adapts to:

---

## auto_inducer_signifiers

```python
spec N-Phase Cycle Protocol: Auto-Inducer Signifiers
```

End phase output with signifiers to control flow:

---

## entropy_budget

```python
spec N-Phase Cycle Protocol: Entropy Budget
```

- **Per phase**: 0.05–0.10 (5-10% for exploration) - **Draw**: `void.entropy.sip(amount=0.07)` - **Return unused**: `void.entropy.pour` - **Replenish**: `void.gratitude.tithe`

---

## phase_condensation

```python
spec N-Phase Cycle Protocol: Phase Condensation
```

Phases in the same family can merge when complexity doesn't warrant separation:

---

## elastic_tree_building

```python
spec N-Phase Cycle Protocol: Elastic Tree Building
```

The N-Phase Cycle generates **outlines adapted to user tastes, project complexity, and substrate constraints**:

---

## phase_selection

```python
spec N-Phase Cycle Protocol: Phase Selection
```

| Task | Phases | Rationale | |------|--------|-----------| | Trivial (typo) | 0 | Direct action | | Quick win (Effort ≤ 2) | ACT only | Known pattern | | Standard feature | 3 | SENSE → ACT → REFLECT | | Crown Jewel | 11 | Full ceremony required |

---

## metatheoretical_grounding

```python
spec N-Phase Cycle Protocol: Metatheoretical Grounding
```

The N-Phase Cycle synthesizes:

---

## agentese_mapping

```python
spec N-Phase Cycle Protocol: AGENTESE Mapping
```

| Phase | Primary Context | Affordances | |-------|-----------------|-------------| | SENSE | `world.*`, `concept.*` | `manifest`, `witness` | | ACT | `self.*`, `world.*` | `refine`, `define` | | REFLECT | `time.*`, `void.*` | `witness`, `tithe` |

---

## related

```python
spec N-Phase Cycle Protocol: Related
```

- **Implementation Guides**: `docs/skills/n-phase-cycle/` - **Auto-Inducer Spec**: `spec/protocols/auto-inducer.md` - **Forest Protocol**: `plans/_forest.md`, `plans/_focus.md` - **Design Principles**: `spec/principles.md` (AD-005)

---

## spec.protocols.os-shell

## epigraph

```python
spec OS Shell: Unified Layout Wrapper and Router: Epigraph
```

---

---

## part_i_design_philosophy

```python
spec OS Shell: Unified Layout Wrapper and Router: Part I: Design Philosophy
```

The kgents web interface is not a collection of pages. It is an **operating system interface** for engaging in autopoiesis--the self-creating, self-maintaining process of the agent ecosystem.

---

## part_x_anti_patterns

```python
spec OS Shell: Unified Layout Wrapper and Router: Part X: Anti-Patterns
```

| Anti-Pattern | Why Bad | Correct Pattern | |--------------|---------|-----------------| | Page with fetch logic | Business logic in presentation | PathProjection with gateway | | Custom visualization not in Gallery | Breaks primitive reliance | Add to Gallery first | | Hardcoded navigation | Doesn't reflect registry | Auto-discover from gateway | | Emojis in copy | Violates style policy | Icons or text only | | Observer hidden in headers | Not visible, not interactive | Persistent drawer | | T

---

## spec.protocols.prism

## core_insight

```python
spec The Prism Protocol: Core Insight
```

Traditional CLI architecture is a **Switchboard**: explicit wiring connects command names to handler functions. Adding a capability requires editing multiple files.

### Examples
```python
>>> ┌─────────────────────────────────────────────────────────────┐
│                    THE PRISM INVERSION                       │
│                                                              │
│   Switchboard:  CLI ──defines──▶ Agent Commands             │
│                                                              │
│   Prism:        Agent ──exposes──▶ CLI (auto-generated)     │
│                                                              │
└─────────────────────────────────────────────────────────────┘
```

---

## the_clicapable_protocol

```python
spec The Prism Protocol: The CLICapable Protocol
```

Agents that wish to expose CLI commands implement this protocol:

### Examples
```python
>>> @runtime_checkable
class CLICapable(Protocol):
    """
    Protocol for agents that project a CLI surface.

    This is structural typing - agents don't inherit from CLICapable,
    they simply implement the required properties and methods.
    """

    @property
    def genus_name(self) -> str:
        """
        Single-word genus identifier for CLI namespace.
        Examples: "grammar", "witness", "library", "jit", "parse", "garden"
        """
        ...

    @property
    def cli_description(self) -> str:
        """One-line description for help text."""
        ...

    def get_exposed_commands(self) -> dict[str, Callable]:
        """
        Return mapping of command names to methods.
        Only methods decorated with @expose should be included.
        """
        ...
```

---

## the_expose_decorator

```python
spec The Prism Protocol: The @expose Decorator
```

Instead of writing argument parsers, methods are annotated:

### Examples
```python
>>> @expose(
    help="Reify domain into Tongue artifact",
    examples=[
        'kgents grammar reify "Calendar Management"',
        'kgents grammar reify "File Ops" --constraints="No deletes"',
    ],
)
async def reify(
    self,
    domain: str,
    level: GrammarLevel = GrammarLevel.COMMAND,
    constraints: list[str] | None = None,
    name: str | None = None,
) -> Tongue:
    """
    Transform a domain description into a formal Tongue.

    The domain string describes the conceptual space. Level controls
    grammar complexity. Constraints are semantic boundaries.
    """
    ...
```

---

## the_prism_class

```python
spec The Prism Protocol: The Prism Class
```

The Prism auto-constructs CLI from agent introspection:

### Examples
```python
>>> class Prism:
    """
    Auto-construct argparse from CLICapable agents.

    The Prism reflects an agent's exposed methods into a CLI parser,
    using type hints to generate argument specifications.
    """

    def __init__(self, agent: CLICapable):
        self.agent = agent
        self._parser: argparse.ArgumentParser | None = None

    def build_parser(self) -> argparse.ArgumentParser:
        """
        Generate argparse.ArgumentParser from agent introspection.

        For each exposed command:
        1. Create subparser with help from @expose
        2. Analyze method signature for parameters
        3. Map type hints to argparse argument types
        4. Handle defaults, optionality, and collections
        """
        ...

    async def dispatch(self, args: list[str]) -> int:
        """
        Parse arguments and invoke appropriate method.

        Automatically handles:
        - Sync vs async method detection
        - Result serialization (JSON or rich output)
        - Error handling with sympathetic messages

        Returns exit code (0 for success).
        """
        ...

    def dispatch_sync(self, args: list[str]) -> int:
        """Synchronous wrapper for CLI entry points."""
        import asyncio
        return asyncio.run(self.dispatch(args))
```

---

## type_to_argparse_mapping

```python
spec The Prism Protocol: Type-to-Argparse Mapping
```

Python type hints map to argparse configurations:

---

## integration_with_hollow_shell

```python
spec The Prism Protocol: Integration with Hollow Shell
```

The Prism integrates with the existing Hollow Shell pattern:

---

## design_principles_applied

```python
spec The Prism Protocol: Design Principles Applied
```

| Principle | How Prism Embodies It | |-----------|----------------------| | **Tasteful** | Single pattern replaces 6 variations; eliminates ~3000 lines | | **Curated** | @expose is intentional selection of what to project | | **Ethical** | CLI is transparent projection; no hidden behavior | | **Joy-Inducing** | `@expose(help="...")` reads naturally; less code to maintain | | **Composable** | CLICapable is a capability, not inheritance; agents compose freely | | **Heterarchical** | Agents choose

---

## success_metrics

```python
spec The Prism Protocol: Success Metrics
```

| Metric | Target | |--------|--------| | Lines of boilerplate eliminated | >2500 | | Prism infrastructure lines | <500 | | Startup time regression | 0ms | | Commands with @expose | 100% of genus commands | | Type coverage | All argparse types mapped |

---

## see_also

```python
spec The Prism Protocol: See Also
```

- `spec/protocols/cli.md` - Parent CLI specification - `spec/principles.md` - Design principles - `impl/claude/protocols/cli/prism/` - Reference implementation

---

## spec.protocols.process-holons

## process_holons_generative_process_trees

```python
spec Process Holons: Generative Process Trees
```

The cycle dissolves into six composable primitives.

### Examples
```python
>>> ┌─────────────────────────────────────────────────────────────────────────────┐
│                         THE SIX PRIMITIVES                                   │
├───────────┬───────┬─────────────────────────┬───────────────────────────────┤
│ Primitive │ Arity │ Semantics               │ Lean Absurd Flavor            │
├───────────┼───────┼─────────────────────────┼───────────────────────────────┤
│ OBSERVE   │ 0→1   │ Perceive context        │ "Open your eyes to what is    │
│           │       │ via handle              │  already looking at you"      │
├───────────┼───────┼─────────────────────────┼───────────────────────────────┤
│ BRANCH    │ 1→n   │ Deliberate fork into    │ "The river decides to become  │
│           │       │ parallel Turns          │  rivers"                      │
├───────────┼───────┼─────────────────────────┼───────────────────────────────┤
│ MERGE     │ n→1   │ Aggregate sibling       │ "Many voices find one throat" │
│           │       │ branches                │                               │
├───────────┼───────┼─────────────────────────┼───────────────────────────────┤
│ RECURSE   │ 1→1   │ Self-apply with         │ "The snake that eats its      │
│           │       │ termination oracle      │  tail, but knows when to stop"│
├───────────┼───────┼─────────────────────────┼───────────────────────────────┤
│ YIELD     │ 1→1   │ Pause, emit             │ "Breathe out before           │
│           │       │ intermediate, resume    │  breathing in"                │
├───────────┼───────┼─────────────────────────┼───────────────────────────────┤
│ TERMINATE │ 1→0   │ End branch with         │ "The river reaches the sea"   │
│           │       │ crystallized result     │                               │
└───────────┴───────┴─────────────────────────┴───────────────────────────────┘
```
```python
>>> from typing import Protocol, TypeVar, Generic, Callable, Any
from dataclasses import dataclass
from enum import Enum

S = TypeVar("S")  # State
A = TypeVar("A")  # Input
B = TypeVar("B")  # Output

class PrimitiveKind(Enum):
    OBSERVE = "observe"
    BRANCH = "branch"
    MERGE = "merge"
    RECURSE = "recurse"
    YIELD = "yield"
    TERMINATE = "terminate"

@dataclass(frozen=True)
class Primitive(Generic[A, B]):
    """An atomic process operation. Morphisms in the Process category."""
    kind: PrimitiveKind
    arity_in: int   # Number of input branches
    arity_out: int  # Number of output branches (-1 = variable)
```
```python
>>> @dataclass(frozen=True)
class Turn:
    """A deliberate branching event. The atom of process history."""
    id: str
    parent_timeline: str
    branching_reason: str       # Why did we branch?
    observer: "Observer"        # Who is observing?
    entropy_allocated: float    # Budget from Accursed Share
    timestamp: float
    children: tuple[str, ...]   # Child timeline IDs

    def view_from(self, other_observer: "Observer") -> "TurnProjection":
        """Project this turn into another observer's umwelt."""
        ...

    def simulate_variation(self, delta: "Variation") -> "Turn":
        """Hypothetical: what if this turn went differently? (future SPECULATE)"""
        ...

@dataclass(frozen=True)
class TurnProjection:
    """Observer-specific view of a Turn."""
    turn_id: str
    observer_archetype: str
    perception: Any  # What the observer sees
    affordances: tuple[str, ...]  # What the observer can do
```
```python
>>> @dataclass(frozen=True)
class ProcessOperad:
    """The grammar of valid process compositions."""

    def compose(self, primitives: list[Primitive]) -> "ProcessTree":
        """
        Compose primitives into a ProcessTree.

        Validates:
        1. Arity matching: output of p[i] matches input of p[i+1]
        2. Well-formedness: starts with arity-0, ends with arity-0
        3. Balance: every BRANCH has a matching MERGE
        """
        ...

@dataclass(frozen=True)
class ProcessTree:
    """A validated composition of primitives."""
    primitives: tuple[Primitive, ...]
```
```python
>>> ┌─────────────────────────────────────────────────────────────────────────────┐
│                           PROCESS FOREST                                     │
│                                                                              │
│  OFFICE LAYER (deliberate, scheduled)                                       │
│  ┌──────────┐  ┌──────────┐  ┌──────────┐                                  │
│  │ Tree A   │  │ Tree B   │  │ Tree C   │   ← "meetings"                   │
│  └────┬─────┘  └────┬─────┘  └────┬─────┘     sync points                  │
│       │             │             │                                         │
│  MYCELIUM LAYER (stigmergic, async)                                         │
│  ──●──●──●──●──●──●──●──●──●──●──●──●──●──  ← pheromone trails             │
│                                                                              │
│  NEURON LAYER (signal propagation)                                          │
│  ══╤══╤══╤══════════╤══╤══════════╤══╤══   ← action potentials             │
└─────────────────────────────────────────────────────────────────────────────┘
```

---

## purpose

```python
spec Process Holons: Generative Process Trees: Purpose
```

Process Holons dissolves the 11-phase N-Phase Cycle into its underlying grammar: six composable primitives that generate all valid processes. The classic cycle becomes one composition among infinite. Research bursts, recursive deepening, dialectical spirals—all equally valid, all generated from the same operad.

---

## core_insight

```python
spec Process Holons: Generative Process Trees: Core Insight
```

Don't enumerate the flowers. Describe the garden's grammar.

---

## the_six_primitives

```python
spec Process Holons: Generative Process Trees: The Six Primitives
```

The minimal set that generates all processes. This is taste: fewer primitives, more compositions.

### Examples
```python
>>> ┌─────────────────────────────────────────────────────────────────────────────┐
│                         THE SIX PRIMITIVES                                   │
├───────────┬───────┬─────────────────────────┬───────────────────────────────┤
│ Primitive │ Arity │ Semantics               │ Lean Absurd Flavor            │
├───────────┼───────┼─────────────────────────┼───────────────────────────────┤
│ OBSERVE   │ 0→1   │ Perceive context        │ "Open your eyes to what is    │
│           │       │ via handle              │  already looking at you"      │
├───────────┼───────┼─────────────────────────┼───────────────────────────────┤
│ BRANCH    │ 1→n   │ Deliberate fork into    │ "The river decides to become  │
│           │       │ parallel Turns          │  rivers"                      │
├───────────┼───────┼─────────────────────────┼───────────────────────────────┤
│ MERGE     │ n→1   │ Aggregate sibling       │ "Many voices find one throat" │
│           │       │ branches                │                               │
├───────────┼───────┼─────────────────────────┼───────────────────────────────┤
│ RECURSE   │ 1→1   │ Self-apply with         │ "The snake that eats its      │
│           │       │ termination oracle      │  tail, but knows when to stop"│
├───────────┼───────┼─────────────────────────┼───────────────────────────────┤
│ YIELD     │ 1→1   │ Pause, emit             │ "Breathe out before           │
│           │       │ intermediate, resume    │  breathing in"                │
├───────────┼───────┼─────────────────────────┼───────────────────────────────┤
│ TERMINATE │ 1→0   │ End branch with         │ "The river reaches the sea"   │
│           │       │ crystallized result     │                               │
└───────────┴───────┴─────────────────────────┴───────────────────────────────┘
```

---

## principle_alignment

```python
spec Process Holons: Generative Process Trees: Principle Alignment
```

This specification embodies the seven principles:

---

## spec.protocols.projection

## projection_protocol_ui

```python
spec Projection Protocol (UI)
```

Developers design agents. Projections are batteries included.

### Examples
```python
>>> P[T] : State → Renderable[T]

Where:
- State is the agent's internal state (polynomial position)
- T is the target medium (CLI, JSON, marimo, VR, etc.)
- Renderable[T] is the target-specific output type
```
```python
>>> S₁ ─────f────→ S₂
        │               │
    P[T]│               │P[T]
        ↓               ↓
   R[T](S₁) ──R[T](f)─→ R[T](S₂)
```
```python
>>> compress ⊣ embed

compress(embed(view)) ≤ view
state ≤ embed(compress(state))
```
```python
>>> @dataclass(frozen=True)
class TownState:
    citizens: tuple[CitizenState, ...]
    phase: TownPhase
    entropy: float
```
```python
>>> class TownWidget(KgentsWidget[TownState]):
    """A town is a collection of citizens in phases."""

    @property
    def health(self) -> float:
        """Emergent property from citizen states."""
        return sum(c.vitality for c in self.state.value.citizens) / len(...)
```

---

## two_projection_protocols

```python
spec Projection Protocol (UI): Two Projection Protocols
```

kgents distinguishes **two projection domains**:

---

## purpose

```python
spec Projection Protocol (UI): Purpose
```

The Projection Protocol defines how kgents content renders to any target medium. Developers write agents and their state machines. The projection layer handles rendering—whether output goes to ASCII terminal, JSON API, marimo notebook, WebGL, or VR headset. This is not mere convenience—it is a **categorical guarantee**: the same agent definition, projected through different functors, produces semantically equivalent views.

---

## core_insight

```python
spec Projection Protocol (UI): Core Insight
```

*"State is design. Projection is mechanical. Targets are isomorphic within fidelity."*

---

## target_registry

```python
spec Projection Protocol (UI): Target Registry
```

The projection system is extensible via the Target Registry:

---

## density_projection

```python
spec Projection Protocol (UI): Density Projection
```

The Projection Protocol extends beyond target (CLI/Web/marimo) to include **DENSITY** as an orthogonal dimension.

---

## integration_with_agentese

```python
spec Projection Protocol (UI): Integration with AGENTESE
```

The Projection Protocol IS the `manifest` aspect operationalized:

---

## the_marimo_integration

```python
spec Projection Protocol (UI): The marimo Integration
```

marimo notebooks are a special case of the Projection Protocol. The reactive DAG model of marimo maps directly to the Signal/Computed/Effect model of kgents widgets.

### Examples
```python
>>> @app.cell
def agent_view(mo, agent_state):
    """Render agent state as marimo HTML."""
    widget = AgentWidget(agent_state)
    mo.Html(widget.to_marimo())
```

---

## principles_summary

```python
spec Projection Protocol (UI): Principles (Summary)
```

| Principle | Meaning | |-----------|---------| | **Design Over Plumbing** | Developers define state, not rendering | | **Batteries Included** | All targets work out of the box | | **Lossy by Design** | Fidelity varies by target; this is explicit | | **Composable** | Widgets compose via `>>` and `//` | | **Observable** | Same state → same output (determinism) | | **Extensible** | New targets registered without changing agents |

---

## the_projection_gallery

```python
spec Projection Protocol (UI): The Projection Gallery
```

The Projection Gallery demonstrates the protocol by rendering **every widget** to **every target** in a single view. Developers create **Pilots**—pre-configured widget demonstrations with variations—and the Gallery handles all projections. Full implementation at `impl/claude/protocols/projection/gallery/` with REST API at `/api/gallery` and React frontend at `web/src/pages/GalleryPage.tsx`.

---

## future_targets

```python
spec Projection Protocol (UI): Future Targets
```

| Target | Status | Notes | |--------|--------|-------| | CLI | ✓ Shipped | ASCII art, box drawing | | TUI | ✓ Shipped | Textual widgets | | marimo | ✓ Shipped | anywidget + mo.Html | | JSON | ✓ Shipped | API responses | | SSE | ✓ Shipped | Streaming events | | WebGL | ✓ Shipped | Three.js primitives (TopologyNode3D, TopologyEdge3D, LOD, themes) | | WebXR | Future | VR/AR experiences | | Audio | Future | Sonification of state |

---

## spec.protocols.repo-archaeology

## repository_archaeology_priors_for_the_self_hosting_compiler

```python
spec Repository Archaeology: Priors for the Self-Hosting Compiler
```

The past is not dead. It is not even past."* — Faulkner

### Examples
```python
>>> Git History
    │
    ▼
┌────────────────────────────────────────────────────────────┐
│                  ARCHAEOLOGY ENGINE                         │
│                                                             │
│  1. Parse git log → Trace[Commit]                          │
│  2. Cluster by feature/area → FeatureTrajectory            │
│  3. Classify: succeeded | abandoned | over-engineered       │
│  4. Extract causal patterns: context → commit_type → fate  │
│  5. Build CausalGraph[SpecPattern, Outcome]                │
│                                                             │
└────────────────────────────────────────────────────────────┘
    │
    ├──► self.memory crystals (Brain)
    ├──► cleanup recommendations (Session work)
    └──► ASHC priors (Causal Graph)
```
```python
>>> @dataclass(frozen=True)
class Commit:
    """A single git commit as archaeological evidence."""
    sha: str
    message: str
    author: str
    timestamp: datetime
    files_changed: tuple[str, ...]
    insertions: int
    deletions: int

    @property
    def is_refactor(self) -> bool:
        """Refactors touch many files with low net change."""
        return len(self.files_changed) > 5 and abs(self.insertions - self.deletions) < 50

    @property
    def is_feature(self) -> bool:
        """Features add more than they remove."""
        return self.insertions > self.deletions * 2 and len(self.files_changed) > 1

    @property
    def is_fix(self) -> bool:
        """Fixes are small, targeted changes."""
        return len(self.files_changed) <= 3 and self.insertions < 50

@dataclass(frozen=True)
class FeatureTrajectory:
    """The lifecycle of a feature from inception to current state."""
    name: str                           # e.g., "AGENTESE", "K-gent", "Flux"
    first_commit: Commit
    commits: tuple[Commit, ...]
    current_status: FeatureStatus       # THRIVING | STABLE | LANGUISHING | ABANDONED | OVER_ENGINEERED
    path_pattern: str                   # e.g., "spec/agents/k-gent/*", "impl/claude/protocols/agentese/*"

    @property
    def velocity(self) -> float:
        """Recent activity relative to total activity."""
        recent = sum(1 for c in self.commits if c.timestamp > datetime.now() - timedelta(days=30))
        return recent / max(len(self.commits), 1)

    @property
    def churn(self) -> float:
        """Total insertions + deletions / commit count."""
        return sum(c.insertions + c.deletions for c in self.commits) / max(len(self.commits), 1)

class FeatureStatus(Enum):
    THRIVING = "thriving"           # Active development, tests passing, docs current
    STABLE = "stable"               # Mature, little change needed, solid tests
    LANGUISHING = "languishing"     # Started strong, activity dropped off
    ABANDONED = "abandoned"         # No commits in months, may have broken tests
    OVER_ENGINEERED = "over_engineered"  # Lots of code, few users, high complexity
```
```python
>>> @dataclass(frozen=True)
class SpecPattern:
    """A pattern extracted from successful specs."""
    pattern_type: str               # e.g., "polynomial_definition", "operad_operations", "integration_paths"
    example_specs: tuple[str, ...]  # Paths to specs that use this pattern
    success_correlation: float      # How often specs with this pattern succeeded

@dataclass(frozen=True)
class EvolutionTrace:
    """How a spec/impl pair evolved over time."""
    spec_path: str
    impl_path: str
    evolution_commits: tuple[Commit, ...]
    phases: tuple[EvolutionPhase, ...]
    final_status: FeatureStatus

    @property
    def spec_first(self) -> bool:
        """Was the spec written before implementation?"""
        spec_commits = [c for c in self.evolution_commits if self.spec_path in c.files_changed]
        impl_commits = [c for c in self.evolution_commits if self.impl_path in c.files_changed]
        return spec_commits[0].timestamp < impl_commits[0].timestamp if spec_commits and impl_commits else False

class EvolutionPhase(Enum):
    SPEC_DRAFT = "spec_draft"           # Initial spec written
    INITIAL_IMPL = "initial_impl"       # First implementation
    ITERATION = "iteration"             # Spec-impl back-and-forth
    STABILIZATION = "stabilization"     # Tests passing, bugs fixed
    POLISH = "polish"                   # Docs, cleanup, refinement
    ABANDONMENT = "abandonment"         # Activity stops
```
```python
>>> @dataclass(frozen=True)
class HistoryCrystal:
    """A crystallized memory of a feature's journey."""
    feature_name: str
    summary: str                        # 2-3 sentence summary
    key_insights: tuple[str, ...]       # What worked, what didn't
    emotional_valence: float            # -1.0 (frustration) to 1.0 (joy)
    lessons: tuple[str, ...]            # Extractable wisdom
    related_principles: tuple[str, ...] # Which design principles were at play

    def to_brain_crystal(self) -> dict:
        """Format for Brain Crown Jewel storage."""
        return {
            "content": self.summary + "\n\nInsights:\n" + "\n".join(f"- {i}" for i in self.key_insights),
            "tags": ["archaeology", "history", self.feature_name],
            "metadata": {
                "type": "history_crystal",
                "feature": self.feature_name,
                "valence": self.emotional_valence,
            }
        }
```
```python
>>> KNOWN_FEATURES = {
    # Crown Jewels (expected: THRIVING or STABLE)
    "Brain": ["impl/claude/services/brain/*", "spec/m-gents/*"],
    "Gardener": ["impl/claude/services/gardener/*", "spec/protocols/gardener*.md"],
    "Town": ["impl/claude/services/town/*", "spec/town/*"],
    "Park": ["impl/claude/services/park/*"],

    # Infrastructure (expected: STABLE)
    "PolyAgent": ["impl/claude/agents/poly/*", "spec/architecture/polyfunctor.md"],
    "AGENTESE": ["impl/claude/protocols/agentese/*", "spec/protocols/agentese*.md"],
    "Flux": ["impl/claude/agents/flux/*", "spec/agents/flux.md"],

    # Question marks (to be classified)
    "K8-gents": ["spec/k8-gents/*", "impl/claude/k8/*"],
    "Psi-gents": ["spec/psi-gents/*"],
    "Omega-gents": ["spec/omega-gents/*"],
    "Evergreen": ["spec/protocols/evergreen*.md", "impl/claude/protocols/evergreen/*"],
}

async def classify_feature(name: str, paths: list[str], commits: list[Commit]) -> FeatureTrajectory:
    """Classify a feature's current status based on commit patterns."""
    feature_commits = [c for c in commits if any(p in c.files_changed for p in paths)]

    if not feature_commits:
        return FeatureTrajectory(name=name, status=FeatureStatus.ABANDONED, ...)

    # Calculate velocity, churn, test presence
    velocity = calculate_velocity(feature_commits)
    has_tests = any("test" in c.files_changed for c in feature_commits)
    recent_activity = any(c.timestamp > datetime.now() - timedelta(days=14) for c in feature_commits)

    # Classify
    if velocity > 0.3 and recent_activity:
        status = FeatureStatus.THRIVING
    elif has_tests and velocity > 0.1:
        status = FeatureStatus.STABLE
    elif velocity < 0.05 and not recent_activity:
        status = FeatureStatus.ABANDONED if not has_tests else FeatureStatus.LANGUISHING
    else:
        status = FeatureStatus.LANGUISHING

    return FeatureTrajectory(name=name, status=status, commits=tuple(feature_commits), ...)
```

### Things to Know

⚠️ **Note:** Anti-pattern: Treating history as truth: History is evidence, not gospel. Patterns may not generalize.

⚠️ **Note:** Anti-pattern: Ignoring failures: Abandoned features teach as much as successes.

⚠️ **Note:** Anti-pattern: Over-automation: Some judgment calls require Kent's taste.

⚠️ **Note:** Anti-pattern: Completionism: Not every commit needs analysis—sample the important ones.

---

## purpose

```python
spec Repository Archaeology: Priors for the Self-Hosting Compiler: Purpose
```

This project mines the kgents git history and codebase to extract **priors**—patterns of what worked, what didn't, and what Kent actually cares about.

---

## the_core_insight

```python
spec Repository Archaeology: Priors for the Self-Hosting Compiler: The Core Insight
```

The git history is a **trace monoid of Kent's development choices**. Each commit is a nudge. Each merge is a composition. The pattern of commits IS the prior.

### Examples
```python
>>> Git History
    │
    ▼
┌────────────────────────────────────────────────────────────┐
│                  ARCHAEOLOGY ENGINE                         │
│                                                             │
│  1. Parse git log → Trace[Commit]                          │
│  2. Cluster by feature/area → FeatureTrajectory            │
│  3. Classify: succeeded | abandoned | over-engineered       │
│  4. Extract causal patterns: context → commit_type → fate  │
│  5. Build CausalGraph[SpecPattern, Outcome]                │
│                                                             │
└────────────────────────────────────────────────────────────┘
    │
    ├──► self.memory crystals (Brain)
    ├──► cleanup recommendations (Session work)
    └──► ASHC priors (Causal Graph)
```

---

## thriving_recent_high_activity_tests_passing

```python
spec Repository Archaeology: Priors for the Self-Hosting Compiler: THRIVING (Recent high activity, tests passing)
```

| Feature | Commits | Velocity | Last Active | |---------|---------|----------|-------------| | Brain | 87 | 0.42 | 2025-12-20 | | AGENTESE | 156 | 0.38 | 2025-12-21 | | Witness | 61 | 0.67 | 2025-12-21 |

---

## stable_mature_low_activity_solid_tests

```python
spec Repository Archaeology: Priors for the Self-Hosting Compiler: STABLE (Mature, low activity, solid tests)
```

| Feature | Commits | Velocity | Last Active | |---------|---------|----------|-------------| | PolyAgent | 34 | 0.08 | 2025-12-15 | | Operad | 28 | 0.05 | 2025-12-14 |

---

## languishing_started_strong_activity_dropped

```python
spec Repository Archaeology: Priors for the Self-Hosting Compiler: LANGUISHING (Started strong, activity dropped)
```

| Feature | Commits | Velocity | Last Active | |---------|---------|----------|-------------| | K8-gents | 45 | 0.02 | 2025-11-20 | | Psi-gents | 12 | 0.00 | 2025-10-15 |

---

## over_engineered_high_complexity_low_usage

```python
spec Repository Archaeology: Priors for the Self-Hosting Compiler: OVER-ENGINEERED (High complexity, low usage)
```

| Feature | Commits | Test Coverage | Diagnosis | |---------|---------|---------------|-----------| | Evergreen | 89 | 92% | 216 tests for problem that doesn't exist |

---

## abandoned_no_recent_activity_brokenmissing_tests

```python
spec Repository Archaeology: Priors for the Self-Hosting Compiler: ABANDONED (No recent activity, broken/missing tests)
```

| Feature | Commits | Last Active | Fate Recommendation | |---------|---------|-------------|---------------------| | Omega-gents | 8 | 2025-09-01 | Archive or revive? |

---

## spec_patterns_correlated_with_success

```python
spec Repository Archaeology: Priors for the Self-Hosting Compiler: Spec Patterns Correlated with Success
```

| Pattern | Success Rate | Example | |---------|--------------|---------| | polynomial_definition | 0.85 | K-gent SOUL_POLYNOMIAL | | agentese_integration | 0.78 | Gardener logos.md | | spec_first_development | 0.72 | Brain Crown Jewel | | operad_operations | 0.68 | Town TOWN_OPERAD |

---

## commit_message_patterns

```python
spec Repository Archaeology: Priors for the Self-Hosting Compiler: Commit Message Patterns
```

| Pattern | Correlation with Success | |---------|-------------------------| | "feat(X): " prefix | +15% completion rate | | References spec in message | +12% stability | | "WIP" or "temp" | -20% completion rate |

---

## lessons_learned_feed_to_ashc_causalgraph

```python
spec Repository Archaeology: Priors for the Self-Hosting Compiler: Lessons Learned (Feed to ASHC CausalGraph)
```

1. Specs with explicit AGENTESE paths succeed 78% of the time 2. Features without tests within 10 commits have 60% abandonment rate 3. Kent prefers polynomial models—adoption correlates with completion

---

## connection_to_kents_intent

```python
spec Repository Archaeology: Priors for the Self-Hosting Compiler: Connection to Kent's Intent
```

From `_focus.md`:

---

## success_metrics

```python
spec Repository Archaeology: Priors for the Self-Hosting Compiler: Success Metrics
```

| Metric | Target | |--------|--------| | Features classified | ≥30 | | Priors extracted | ≥10 patterns | | Crystals generated | ≥20 | | ASHC CausalGraph edges | ≥100 | | Cleanup recommendations | ≥5 actionable items |

---

## spec.protocols.self-grow

## selfgrow_the_autopoietic_holon_generator

```python
spec self.grow: The Autopoietic Holon Generator
```

The system that cannot create new organs is already dead.

### Examples
```python
>>> self.grow.*                    # Autopoietic mechanisms
  self.grow.recognize          # Detect ontological gaps
  self.grow.propose            # Draft new holon spec
  self.grow.validate           # Test against principles + laws
  self.grow.germinate          # Nursery for proto-holons
  self.grow.promote            # Staged promotion with approval
  self.grow.prune              # Remove failed growths
  self.grow.rollback           # Revert promoted holons
  self.grow.witness            # History of growth attempts
  self.grow.nursery            # View germinating holons
  self.grow.budget             # Entropy budget status
```
```python
>>> @dataclass
class GapRecognition:
    """A recognized gap in the ontology."""
    gap_id: str
    context: str
    holon: str
    aspect: str | None
    pattern: str
    evidence: list[GrowthRelevantError]
    evidence_count: int
    archetype_diversity: int
    confidence: float  # 0.0-1.0, based on evidence strength
    gap_type: Literal["missing_holon", "missing_affordance", "missing_relation", "semantic_gap"]
    entropy_cost: float

async def recognize_gaps(
    logos: Logos,
    observer: Umwelt,
    query: RecognitionQuery | None = None,
) -> list[GapRecognition]
```
```python
>>> @dataclass
class HolonProposal:
    """A proposal for a new holon."""
    proposal_id: str
    content_hash: str  # SHA256 for deterministic regeneration
    gap: GapRecognition | None
    entity: str
    context: str
    why_exists: str  # Tasteful principle: justification required
    affordances: dict[str, list[str]]  # archetype -> verbs
    relations: dict[str, list[str]]  # relation_type -> handles
    behaviors: dict[str, str]  # aspect -> description

    def compute_hash(self) -> str: ...
    def to_markdown(self) -> str: ...
```
```python
>>> @dataclass
class ValidationResult:
    """Result of validating a proposal against all gates."""
    passed: bool
    scores: dict[str, float]  # Seven principles: 0.0-1.0
    reasoning: dict[str, str]
    law_checks: LawCheckResult
    abuse_check: AbuseCheckResult
    duplication_check: DuplicationCheckResult
    blockers: list[str]
    warnings: list[str]
    suggestions: list[str]

async def validate_proposal(
    proposal: HolonProposal,
    logos: Logos,
    observer: Umwelt,
) -> ValidationResult
```
```python
>>> @dataclass
class GerminatingHolon:
    """A holon in the nursery, not yet fully grown."""
    germination_id: str
    proposal: HolonProposal
    validation: ValidationResult
    jit_source: str  # JIT-compiled implementation
    jit_source_hash: str
    usage_count: int
    success_count: int
    germinated_at: datetime
    rollback_token: str | None

    def should_promote(self, config: NurseryConfig) -> bool: ...
    def should_prune(self, config: NurseryConfig) -> bool: ...

class Nursery:
    """The germination nursery with capacity enforcement."""
    config: NurseryConfig  # max_capacity=20, max_per_context=5

    async def germinate(
        self,
        proposal: HolonProposal,
        validation: ValidationResult,
        logos: Logos,
        observer: Umwelt,
    ) -> GerminatingHolon
```

---

## purpose

```python
spec self.grow: The Autopoietic Holon Generator: Purpose
```

AGENTESE defines five contexts, standard aspects, and a taxonomy of holons. A living system must grow. `self.grow` is the autopoietic mechanism for AGENTESE to recognize ontological gaps, propose new holons, validate them against principles and laws, germinate them in a probationary nursery, and promote them to the active ontology—all while maintaining Tasteful curation and Ethical safeguards.

---

## core_insight

```python
spec self.grow: The Autopoietic Holon Generator: Core Insight
```

Growth lives in tension with the Tasteful principle. Resolution: `self.grow` channels the Accursed Share through Tasteful filters (validation gates), producing curated holons that satisfy Generative compression. Growth is not free—it is earned through evidence, validated through gates, and governed by entropy budgets.

---

## success_criteria

```python
spec self.grow: The Autopoietic Holon Generator: Success Criteria
```

An AGENTESE `self.grow` implementation is well-designed if:

---

## spec.protocols.servo-substrate

## servo_projection_substrate_protocol

```python
spec Servo Projection Substrate Protocol
```

Servo is not 'a browser' inside kgents. It is the projection substrate that renders the ontology.

### Examples
```python
>>> @dataclass
class ServoScene:
    """Scene graph for Servo rendering."""
    id: SceneId
    nodes: list[ServoNode]
    edges: list[ServoEdge]
    layout: LayoutDirective
    style: StyleSheet
    animations: list[Animation]

@dataclass
class ServoNode:
    """Node in Servo scene graph."""
    id: NodeId
    kind: ServoNodeKind        # PANEL, TRACE, INTENT, OFFERING, COVENANT
    content: ServoContent
    position: Position | None  # If explicit
    style: NodeStyle
    interactions: list[Interaction]

class ServoNodeKind(Enum):
    """Semantic node types for Servo rendering."""
    PANEL = auto()             # Container with borders
    TRACE = auto()             # TraceNode visualization
    INTENT = auto()            # IntentTree node
    OFFERING = auto()          # Offering badge
    COVENANT = auto()          # Permission indicator
    WALK = auto()              # Walk timeline
    RITUAL = auto()            # Ritual state
```
```python
>>> @dataclass
class ServoShell:
    """Minimal host process for Servo composition."""
    views: dict[ViewId, TerrariumView]
    projection_registry: ProjectionRegistry
    router: IntentRouter
    covenant_overlay: CovenantOverlay

    def compose(self, scene: ServoScene) -> RenderedOutput:
        """Compose projection outputs into final render."""
        ...

    def route(self, intent: Intent) -> ViewId:
        """Navigate to view based on intent, not URL."""
        ...
```
```python
>>> @ProjectionRegistry.register(
    "servo",
    fidelity=0.95,
    description="Servo browser engine substrate"
)
def servo_projector(widget: KgentsWidget) -> ServoScene:
    """Convert widget state to ServoScene graph."""
    return ServoScene(
        nodes=widget_to_servo_nodes(widget),
        layout=infer_layout(widget),
        style=get_servo_stylesheet(),
        ...
    )
```
```python
>>> @dataclass
class TerrariumView:
    """Independent webview with compositional lens."""
    id: ViewId
    webview: ServoWebview
    selection: TraceNodeQuery  # What TraceNodes to show
    lens: LensConfig           # How to transform
    fault_isolated: bool = True  # Crash doesn't collapse system

    def project(self, trace_stream: Stream[TraceNode]) -> ServoScene:
        """Apply lens to trace stream."""
        ...
```
```python
>>> Law 1 (Scene Composability): ServoScenes compose via overlay
Law 2 (Layout Determinism): Same input → same layout
Law 3 (Fault Isolation): Crashed view doesn't affect other views
Law 4 (Intent Routing): Navigation is a projection of intent, not URL
```

---

## purpose

```python
spec Servo Projection Substrate Protocol: Purpose
```

Define Servo as the primary projection target for kgents, replacing the current webapp as the operational UI surface. Servo provides multi-webview heterarchy, WebGPU rendering, and Rust-native law enforcement.

---

## core_insight

```python
spec Servo Projection Substrate Protocol: Core Insight
```

**The webapp is not the UI—it's the composition boundary.** Servo primitives supersede React/webapp logic for operational surfaces. The webapp becomes a shallow shell that composes projection outputs.

---

## spec.protocols.storage-migration

## storage_migration_protocol

```python
spec Storage Migration Protocol
```

Research-oriented patterns for transitioning between storage backends.

### Examples
```python
>>> def is_postgres() -> bool:
    from alembic import context
    return context.get_context().dialect.name == "postgresql"

def upgrade():
    if is_postgres():
        # Postgres: SERIAL, NOW(), ON CONFLICT
        op.execute("CREATE TABLE foo (id SERIAL PRIMARY KEY...)")
    else:
        # SQLite: AUTOINCREMENT, datetime('now'), INSERT OR IGNORE
        op.execute("CREATE TABLE foo (id INTEGER PRIMARY KEY AUTOINCREMENT...)")
```

---

## overview

```python
spec Storage Migration Protocol: Overview
```

kgents supports multiple storage tiers, enabling graceful transitions from portable SQLite to production PostgreSQL. This document captures migration patterns, environment semantics, and rollback strategies.

---

## storage_tiers

```python
spec Storage Migration Protocol: Storage Tiers
```

| Tier | Backend | Use Case | Characteristics | |------|---------|----------|-----------------| | **Portable** | SQLite `membrane.db` | Local dev, single user | Zero config, XDG-compliant, file-based | | **Unified** | Docker Postgres | Team dev, production-like | Full SQL, connection pooling, same schema | | **Production** | Managed Postgres | Cloud deployment | HA, replication, managed backups |

---

## related

```python
spec Storage Migration Protocol: Related
```

- `docs/skills/unified-storage.md` - Implementation patterns - `impl/claude/models/base.py` - SQLAlchemy foundation - `impl/claude/scripts/migrate_membrane_to_postgres.py` - Migration tool - `impl/claude/system/migrations/` - Alembic versions

---

## spec.protocols.turn

## turn_protocol_the_fixed_point_event_primitive

```python
spec Turn Protocol: The Fixed-Point Event Primitive
```

A Turn is the Y combinator applied to agent state: (S, A) -> (S', B) where stability = (S = S').

### Examples
```python
>>> Traditional:  Event = (content, timestamp, source)
Turn:         Turn = (content, timestamp, source) + (S_pre -> S_post) + governance
```
```python
>>> Turn : (S_pre x Input) -> (S_post x Output)

Where:
- S_pre: Agent state before turn (hashed for storage)
- Input: The stimulus that triggered the turn
- S_post: Agent state after turn
- Output: The response produced
```
```python
>>> TraceMonoid M = (Events, Independence)

Where:
- Events: Partially ordered set of Turns
- Independence: Symmetric relation marking concurrent turns

Key property: Independent turns commute (ab = ba)
             Dependent turns don't (ab != ba)
```
```python
>>> def is_stable(turn: Turn) -> bool:
    """A turn is stable if state didn't change."""
    return turn.state_hash_pre == turn.state_hash_post


def iterate_until_stable(
    agent: Agent[A, B],
    initial: A,
    max_iterations: int = 10,
) -> B:
    """
    Y-combinator style fixed-point iteration.

    Runs agent until output stabilizes (state stops changing).
    This replaces Y-gent's Y.fix() operator.
    """
    current = initial
    history: list[Turn] = []

    for i in range(max_iterations):
        turn = await agent.invoke_with_turn(current)
        history.append(turn)

        if is_stable(turn):
            return turn.content  # Fixed point reached

        if detect_cycle(history):
            return collapse_to_ground(history)  # Limit cycle

        current = turn.content

    return history[-1].content  # Best effort
```
```python
>>> def detect_cycle(history: list[Turn], window: int = 3) -> bool:
    """
    Detect limit cycles in turn history.

    A limit cycle occurs when state_hash repeats within window.
    """
    if len(history) < window:
        return False

    recent_hashes = [t.state_hash_post for t in history[-window:]]
    return len(recent_hashes) != len(set(recent_hashes))
```

---

## purpose

```python
spec Turn Protocol: The Fixed-Point Event Primitive: Purpose
```

The Turn Protocol defines the **atomic causal event** in agent interaction. It is the operational form of the Y combinator: a morphism from (state, input) to (state', output) with governance metadata, causal structure, and fixed-point semantics.

---

## the_core_insight

```python
spec Turn Protocol: The Fixed-Point Event Primitive: The Core Insight
```

Traditional event systems are flat: events happen, they're timestamped, done. Turn extends Event with **state morphism semantics**:

### Examples
```python
>>> Traditional:  Event = (content, timestamp, source)
Turn:         Turn = (content, timestamp, source) + (S_pre -> S_post) + governance
```

---

## the_weave_concurrent_turn_history

```python
spec Turn Protocol: The Fixed-Point Event Primitive: The Weave: Concurrent Turn History
```

Turns compose into a **Weave**—a trace monoid that captures concurrent history.

---

## fixed_point_iteration

```python
spec Turn Protocol: The Fixed-Point Event Primitive: Fixed-Point Iteration
```

The Turn Protocol provides the machinery Y-gent's `Y.fix()` claimed:

---

## causal_cone_projection

```python
spec Turn Protocol: The Fixed-Point Event Primitive: Causal Cone Projection
```

The **killer feature** of the Turn Protocol: automatic context projection.

---

## yield_governance

```python
spec Turn Protocol: The Fixed-Point Event Primitive: YIELD Governance
```

YIELD turns operationalize the **Ethical principle**: preserve human agency for high-risk actions.

---

## principles_alignment

```python
spec Turn Protocol: The Fixed-Point Event Primitive: Principles Alignment
```

| Principle | How Turn Protocol Aligns | |-----------|--------------------------| | **Tasteful** | Single purpose: causal event with governance | | **Curated** | Five turn types only—no taxonomy explosion | | **Ethical** | YIELD preserves human agency for high-risk actions | | **Joy-Inducing** | Causal cone makes context feel "right" | | **Composable** | Turns compose via TraceMonoid laws | | **Heterarchical** | No fixed turn ordering; causality determines order | | **Generative** | Turn history

---

## references

```python
spec Turn Protocol: The Fixed-Point Event Primitive: References
```

- Lamport, "Time, Clocks, and the Ordering of Events" (1978) - Mazurkiewicz, "Trace Theory" (1977) - Spivak, "Polynomial Functors" (2023-2024) - Abramsky, "Game Semantics" (1994-present)

---

## see_also

```python
spec Turn Protocol: The Fixed-Point Event Primitive: See Also
```

- `spec/f-gents/research.md` - Research flow uses Turn stability - `spec/n-gents/README.md` - Narrator witnesses turn history - `spec/protocols/agentese.md` - AGENTESE path integration - `impl/claude/weave/` - Reference implementation

---

## spec.protocols.umwelt

## prologue_the_fallacy_of_the_universal_view

```python
spec The Umwelt Protocol: Agent-Specific World Projection: Prologue: The Fallacy of the Universal View
```

The enterprise architecture approach to "world access" commits a fundamental error: it assumes there exists a **Universal View**—a God's-eye perspective from which all state is visible and all configuration accessible. This violates three kgents principles:

---

## part_i_the_three_components

```python
spec The Umwelt Protocol: Agent-Specific World Projection: Part I: The Three Components
```

Every agent receives an Umwelt composed of three elements:

### Examples
```python
>>> ┌─────────────────────────────────────────────────────────────┐
│                         UMWELT                               │
│                                                              │
│   ┌──────────────┐  ┌──────────────┐  ┌──────────────┐      │
│   │    State     │  │     DNA      │  │   Gravity    │      │
│   │   (Lens)     │  │   (Config)   │  │  (Ground)    │      │
│   │              │  │              │  │              │      │
│   │  "What I     │  │  "What I     │  │  "What I     │      │
│   │   touch"     │  │   am"        │  │   cannot do" │      │
│   └──────────────┘  └──────────────┘  └──────────────┘      │
│                                                              │
│   D-gent Lens       G-gent Tongue     F-gent Contract       │
└─────────────────────────────────────────────────────────────┘
```

---

## part_ii_the_projector

```python
spec The Umwelt Protocol: Agent-Specific World Projection: Part II: The Projector
```

The Projector is the factory that creates Umwelts. It slices the infinite into the finite.

### Examples
```python
>>> class Projector:
    """
    Projects the infinite World into finite agent Umwelts.

    The Projector:
    1. Does NOT give agents access to the World
    2. Creates scoped Lenses for state access
    3. Validates DNA against G-gent tongues
    4. Assembles gravitational constraints from F-gent contracts
    """

    def __init__(self, root: DataAgent):
        """
        Initialize with a root D-gent (the "Real").

        Args:
            root: The underlying state store (could be volatile,
                  persistent, or hypothetical)
        """
        self._root = root
        self._gravity_registry: dict[str, list[Contract]] = {}

    def project(
        self,
        agent_id: str,
        dna: Config,
        gravity: list[Contract] | None = None,
    ) -> Umwelt:
        """
        Create an Umwelt for an agent.

        The agent receives:
        - A Lens (cannot see outside its focus)
        - Validated DNA (G-gent checked)
        - Gravitational constraints (F-gent enforced)
        """
        # 1. Create scoped lens
        state_lens = self._root.lens(f"agents.{agent_id}")

        # 2. Validate DNA against tongue
        tongue = dna.tongue()
        if not tongue.validate(dna):
            raise DNAValidationError(f"Invalid DNA for {agent_id}")

        # 3. Assemble gravity
        agent_gravity = gravity or self._gravity_registry.get(agent_id, [])

        return Umwelt(
            state=state_lens,
            dna=dna,
            gravity=agent_gravity,
        )
```

---

## spec.protocols.warp-primitives

## warp_primitives_protocol

```python
spec WARP Primitives Protocol
```

Every action is a TraceNode. Every session is a Walk. Every workflow is a Ritual.

### Examples
```python
>>> @dataclass(frozen=True)
class TraceNode:
    """Atomic unit of execution artifact."""
    id: TraceNodeId
    origin: JewelOrAgent       # What emitted it
    stimulus: Stimulus         # Prompt, command, or event
    response: Response         # Output, diff, or state transition
    umwelt: UmweltSnapshot     # Observer capabilities at emission
    links: list[TraceLink]     # Causal edges (plan → node, node → node)
    timestamp: datetime
    phase: NPhase | None       # If within N-Phase workflow

@dataclass(frozen=True)
class TraceLink:
    """Causal edge between TraceNodes or to plans."""
    source: TraceNodeId | PlanPath
    target: TraceNodeId
    relation: LinkRelation     # CAUSES, CONTINUES, BRANCHES, FULFILLS
```
```python
>>> @dataclass
class Walk:
    """Durable work stream tied to Forest plans."""
    id: WalkId
    goal: IntentId             # What we're trying to achieve
    root_plan: PlanPath        # Plans/*.md leaf
    trace_nodes: list[TraceNodeId]  # Ordered execution history
    participants: list[ParticipantId]  # Agents + umwelts
    phase: NPhase              # Current N-Phase position
    started_at: datetime
    status: WalkStatus         # ACTIVE, PAUSED, COMPLETE, ABANDONED
```
```python
>>> @dataclass
class Ritual:
    """Curator-orchestrated workflow with explicit gates."""
    id: RitualId
    intent: IntentId
    phases: list[RitualPhase]  # State machine (N-Phase compatible)
    guards: list[SentinelGuard]  # Checks at each boundary
    tools: list[AgentCapability]  # Registered capabilities
    covenant: CovenantId       # Permission context
    offering: OfferingId       # Resource context
    status: RitualStatus

@dataclass
class RitualPhase:
    """Single phase in ritual state machine."""
    name: str
    entry_guards: list[GuardId]
    exit_guards: list[GuardId]
    allowed_actions: list[ActionPattern]
    timeout: timedelta | None
```
```python
>>> @dataclass
class Offering:
    """Explicitly priced and scoped context."""
    id: OfferingId
    handles: list[HandlePattern]  # brain.*, world.file.*, plans.*, time.trace.*
    budget: Budget             # Capital, entropy, token constraints
    contracts: list[CapabilityContract]  # Read/write caps by agent
    expires_at: datetime | None

@dataclass
class Budget:
    """Resource constraints for an Offering."""
    capital: float | None      # Max cost
    entropy: float | None      # Max entropy consumption
    tokens: int | None         # Max LLM tokens
    time: timedelta | None     # Max wall-clock time
```
```python
>>> class IntentType(Enum):
    """Typed intent categories."""
    EXPLORE = auto()
    DESIGN = auto()
    IMPLEMENT = auto()
    REFINE = auto()
    VERIFY = auto()
    ARCHIVE = auto()

@dataclass
class Intent:
    """Typed goal node in the intent graph."""
    id: IntentId
    type: IntentType
    description: str
    parent: IntentId | None
    children: list[IntentId]
    dependencies: list[IntentId]
    capabilities_required: list[CapabilityPattern]
    status: IntentStatus       # PENDING, ACTIVE, COMPLETE, BLOCKED

@dataclass
class IntentTree:
    """Typed intent graph with dependencies."""
    root: IntentId
    nodes: dict[IntentId, Intent]
    edges: list[IntentEdge]    # Dependencies with capability requirements
```

---

## purpose

```python
spec WARP Primitives Protocol: Purpose
```

Establish the foundational primitives that enable WARP-grade ergonomics within kgents while preserving categorical laws and constitutional alignment. These primitives form the substrate for trace-first history, explicit context contracts, and lawful workflow orchestration.

---

## core_insight

```python
spec WARP Primitives Protocol: Core Insight
```

**The block is the atom.** WARP's brilliance is making every interaction traceable, replayable, and composable. kgents must do the same, but under Witness + Time + Category Theory.

---

## spec.protocols.web-reactive

## web_reactive_projection_protocol

```python
spec Web Reactive Projection Protocol
```

The web is just another target. Same widgets, different pixels.

### Examples
```python
>>> ┌─────────────────────────────────────────────────────────────────────────────┐
│                        THE WEB REACTIVE TRANSFORMATION                       │
│                                                                              │
│   Reactive Substrate (Python)         Web Frontend (TypeScript)             │
│   ─────────────────────────           ───────────────────────               │
│                                                                              │
│   Signal[T]           ══════════►     useSignal<T>(signal)                  │
│   Computed[T]         ══════════►     useComputed<T>(computed)              │
│   Effect              ══════════►     useReactiveEffect(effect)             │
│   KgentsWidget[S]     ══════════►     <Widget state={s} />                  │
│   HStack              ══════════►     <Flex direction="row">                │
│   VStack              ══════════►     <Flex direction="column">             │
│                                                                              │
│   project(JSON)       ══════════►     Widget Props (typed interface)        │
│                                                                              │
└─────────────────────────────────────────────────────────────────────────────┘
```
```python
>>> P[Web] : State → ReactElement

Where:
- State is the widget's internal state (frozen dataclass in Python)
- ReactElement is the target-specific output (JSX.Element in TypeScript)
```
```python
>>> S₁ ─────f────→ S₂
        │               │
   P[Web]│               │P[Web]
        ↓               ↓
   React(S₁) ──React(f)─→ React(S₂)
```
```python
>>> Signal ⊣ React

subscribe(embed(component)) ≤ component
signal ≤ embed(subscribe(signal))
```
```python
>>> F : Widget → ReactComponent

Laws:
1. F(Id) = Fragment (identity preserves)
2. F(a >> b) = <HStack>{F(a)}{F(b)}</HStack> (horizontal composition)
3. F(a // b) = <VStack>{F(a)}{F(b)}</VStack> (vertical composition)
4. F((a >> b) >> c) = F(a >> (b >> c)) (associativity)
```

---

## purpose

```python
spec Web Reactive Projection Protocol: Purpose
```

This protocol extends the Projection Protocol to web targets (React/DOM), unifying the Agent Town web frontend with the reactive substrate. The goal: **eliminate duplicate state management** and enable widget definitions to project directly to React components.

---

## the_core_insight

```python
spec Web Reactive Projection Protocol: The Core Insight
```

**`Widget[S].project(WEB)` returns `JSX.Element`.**

### Examples
```python
>>> ┌─────────────────────────────────────────────────────────────────────────────┐
│                        THE WEB REACTIVE TRANSFORMATION                       │
│                                                                              │
│   Reactive Substrate (Python)         Web Frontend (TypeScript)             │
│   ─────────────────────────           ───────────────────────               │
│                                                                              │
│   Signal[T]           ══════════►     useSignal<T>(signal)                  │
│   Computed[T]         ══════════►     useComputed<T>(computed)              │
│   Effect              ══════════►     useReactiveEffect(effect)             │
│   KgentsWidget[S]     ══════════►     <Widget state={s} />                  │
│   HStack              ══════════►     <Flex direction="row">                │
│   VStack              ══════════►     <Flex direction="column">             │
│                                                                              │
│   project(JSON)       ══════════►     Widget Props (typed interface)        │
│                                                                              │
└─────────────────────────────────────────────────────────────────────────────┘
```

---

## json_projection_as_protocol

```python
spec Web Reactive Projection Protocol: JSON Projection as Protocol
```

The existing `to_json()` method on widgets becomes the **interface contract** between Python and TypeScript.

---

## generative_ui_integration

```python
spec Web Reactive Projection Protocol: Generative UI Integration
```

Building on research from AG-UI Protocol and Vercel AI SDK, the architecture supports **agent-driven UI generation**.

---

## existing_in_flight_work

```python
spec Web Reactive Projection Protocol: Existing In-Flight Work
```

The following work is already underway (from git status):

---

## connection_to_spec_principles

```python
spec Web Reactive Projection Protocol: Connection to Spec Principles
```

| Principle | Web Reactive Manifestation | |-----------|---------------------------| | **Tasteful** | Single purpose: project widgets to React | | **Curated** | One bridge pattern, not multiple approaches | | **Ethical** | Transparent state flow, no hidden mutations | | **Joy-Inducing** | Same personality in CLI and web | | **Composable** | `>>` and `//` operators preserved | | **Heterarchical** | No fixed component hierarchy | | **Generative** | JSON schema generates TypeScript types |

---

## summary

```python
spec Web Reactive Projection Protocol: Summary
```

The Web Reactive Projection Protocol unifies the Agent Town frontend with the reactive substrate by:

---

## spec.protocols.witness-primitives

## witness_primitives_the_audit_core

```python
spec Witness Primitives: The Audit Core
```

Every action leaves a mark. Every mark joins a walk. Every walk follows a playbook.

### Examples
```python
>>> Mark : Origin × Stimulus × Response × Umwelt × Time → Artifact

Laws:
- Law 1 (Immutability): Mark is frozen after creation
- Law 2 (Causality): target.timestamp > source.timestamp for all links
- Law 3 (Completeness): Every AGENTESE invocation emits exactly one Mark
```
```python
>>> Walk : Goal × Plan × Mark* × Participant* × Phase × Status → Session

Laws:
- Law 1 (Monotonicity): Mark list only grows, never shrinks
- Law 2 (Phase Coherence): Phase transitions follow N-Phase grammar
- Law 3 (Plan Binding): root_plan must exist in Forest
```
```python
>>> Playbook : Grant × Scope × Phase* × Guard* → Workflow

Laws:
- Law 1 (Grant Required): Every Playbook has exactly one Grant
- Law 2 (Scope Required): Every Playbook has exactly one Scope
- Law 3 (Guard Transparency): Guards emit Marks on evaluation
- Law 4 (Phase Ordering): Phase transitions follow directed cycle
```
```python
>>> Grant : Permission* × ReviewGate* × Expiry → Contract

Laws:
- Law 1 (Required): Sensitive operations require a granted Grant
- Law 2 (Revocable): Grants can be revoked at any time
- Law 3 (Gated): Review gates trigger on threshold
```
```python
>>> Scope : Handle* × Budget × Expiry → Context

Laws:
- Law 1 (Budget Enforcement): Exceeding budget triggers review
- Law 2 (Immutability): Scopes are frozen after creation
- Law 3 (Expiry Honored): Expired Scopes deny access
```

### Things to Know

⚠️ **Note:** Anti-pattern: Mark is not a log entry — it has causal links and umwelt context

⚠️ **Note:** Anti-pattern: Walk is not just a session — it binds to plans and tracks N-Phase

⚠️ **Note:** Anti-pattern: Playbook is not a pipeline — it has guards and requires contracts

⚠️ **Note:** Anti-pattern: Grant is not an API key — it's negotiated and revocable

⚠️ **Note:** Anti-pattern: Scope is not a context dump — it has explicit budget constraints

⚠️ **Note:** Anti-pattern: Lesson is not documentation — it's versioned knowledge that evolves

---

## purpose

```python
spec Witness Primitives: The Audit Core: Purpose
```

The Witness primitives form the audit and traceability foundation of kgents. They answer:

---

## the_core_insight

```python
spec Witness Primitives: The Audit Core: The Core Insight
```

The Witness primitives embody a simple truth:

---

## the_rename_map

```python
spec Witness Primitives: The Audit Core: The Rename Map
```

| Old Name | New Name | Rationale | |----------|----------|-----------| | **WARP** | **Witness Primitives** | Already the Crown Jewel name; no acronym needed | | **TraceNode** | **Mark** | "Every action leaves a mark" — short, evocative, intuitive | | **Walk** | **Walk** | Keep it — intuitive "going for a walk" feeling works | | **Ritual** | **Playbook** | Clear, action-oriented; what a coach follows, not a ceremony | | **Offering** | **Scope** | OAuth-adjacent; "what's in scope" is immediately 

---

## why_these_names

```python
spec Witness Primitives: The Audit Core: Why These Names?
```

Applying the naming criteria from the plan:

---

*206 symbols, 23 teaching moments*

*Generated by Living Docs — 2025-12-21*