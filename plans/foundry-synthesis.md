# Foundry Synthesis Implementation Roadmap

> *"The agent that doesn't exist yet is the agent you need most. The projector determines how it manifests."*

**Source**: `brainstorming/2025-12-21-jgent-alethic-projection-synthesis.md`
**Spec**: `spec/services/foundry.md`
**Status**: Phases 1-4 Complete (414 tests, Phase 5: Promotion next)

---

## Overview

This plan implements the **Agent Foundry** — the synthesis of J-gent JIT intelligence with Alethic Projection compilation.

**The Core Insight**:
```
Intent ──► J-gent ──► MetaArchitect ──► (Nucleus, Halo) ──► Projector ──► Target
           Reality     JIT Generation    Agent Definition      Compile      Executable
           Classifier
```

---

## Phase 1: CLI + Docker Integration ✅ COMPLETE

**Goal**: Wire existing CLIProjector to `kg a manifest` and add DockerProjector.
**Completed**: 2025-12-21 | **Tests**: 223 passing (33 new)

### Tasks

```
[x] Wire CLIProjector to `kg a manifest --target cli`
    Files: protocols/cli/handlers/a_gent.py, protocols/cli/commands/agent/manifest.py
    - Added --target flag accepting k8s|cli|docker
    - Routes to appropriate projector via match statement

[x] Add DockerProjector with basic Dockerfile generation
    File: impl/claude/system/projector/docker.py (NEW)
    - Implements Projector[str] protocol
    - Generates Dockerfile from agent Halo
    - Capability mappings:
      - @Stateful → VOLUME /var/lib/kgents/state
      - @Soulful → ENV KGENT_PERSONA, KGENT_MODE
      - @Observable → EXPOSE 9090
      - @Streamable → Multi-stage build
      - @TurnBased → VOLUME for weave files
    - DockerArtifact struct for composition metadata

[x] Implement DockerProjector >> K8sProjector composition
    File: impl/claude/system/projector/compose.py (NEW)
    - Added >> operator via monkey-patch in add_rshift_to_projector()
    - ComposedProjector runs upstream, injects into downstream
    - K8s manifests automatically get Docker image reference
    - IdentityProjector for composition law satisfaction

[x] Add `kg a run` enhancements
    Files: protocols/cli/handlers/a_gent.py, protocols/cli/commands/agent/run.py
    - --stream flag parsed (behavior pending)
    - --trace flag parsed (behavior pending)
```

### Success Criteria ✅
- `kg a manifest MyAgent --target cli` produces executable Python script ✅
- `kg a manifest MyAgent --target docker` produces valid Dockerfile ✅
- `DockerProjector() >> K8sProjector()` produces Dockerfile + K8s manifests with image reference ✅

### Implementation Notes

**Key Pattern**: Projector composition via monkey-patched `__rshift__`:
```python
# In compose.py, called at module import
def add_rshift_to_projector():
    def __rshift__(self, other):
        return ComposedProjector(self, other)
    setattr(Projector, "__rshift__", __rshift__)
```

**DockerArtifact** carries metadata for downstream projectors:
```python
@dataclass
class DockerArtifact:
    dockerfile: str
    image_name: str
    image_tag: str = "latest"
    exposed_ports: list[int]
    volumes: list[str]
```

---

## Phase 2: WASM Foundation (Week 1) — ✅ COMPLETE

**Goal**: Establish sandboxed browser execution for chaotic reality agents.

**Why Priority**: WASM is essential for zero-trust JIT execution. Chaotic reality agents MUST run sandboxed before being trusted.

**Completed**: 2025-12-21 | **Tests**: 264 passing (45 new target selection tests)

### Tasks

```
[x] Research Servo primitives for WASM agent execution
    - Decision: Pyodide (mature, well-tested Python-in-WASM)
    - Browser sandbox = battle-tested isolation

[x] Prototype WASMProjector with Pyodide
    File: impl/claude/system/projector/wasm.py (NEW)
    - Implements Projector[str] protocol (returns HTML bundle)
    - Generates self-contained HTML with embedded Pyodide runtime
    - Compiles agent source into Python that runs in browser
    - Supports composition via >> operator

[x] Test sandboxed execution of simple agents
    File: impl/claude/system/projector/_tests/test_wasm.py
    - 41 tests covering:
      - HTML generation, Pyodide bootstrap
      - Capability mappings (Stateful, Observable, Soulful, Streamable)
      - Sandbox security indicators
      - UI features (input/output, Ctrl+Enter, metrics)
      - Projector composition

[x] Define WASM capability mappings
    - @Stateful → localStorage/IndexedDB persistence
    - @Observable → Performance API + metrics panel
    - @Soulful → Persona badge display
    - @Streamable → Streaming capability indicator

[x] Integrate Target Selection with Chaosmonger
    File: impl/claude/agents/j/target_selector.py (NEW)
    - Target enum: LOCAL, CLI, DOCKER, K8S, WASM, MARIMO
    - select_target(): Reality × Context × Stability → Target
    - CHAOTIC reality → WASM (forced, unconditional)
    - Unstable code → WASM (forced, unconditional)
    - DETERMINISTIC → LOCAL, PROBABILISTIC → context-dependent
    - 45 tests covering all safety invariants

[x] Wire to CLI: kg a manifest --target wasm
    File: impl/claude/protocols/cli/commands/agent/manifest.py
    - Added wasm to VALID_TARGETS
    - _execute_wasm_manifest() routes to WASMProjector
```

### Success Criteria ✅ (All Met)
- ✅ Simple agent compiles to WASM and executes in browser sandbox
- ✅ Capability mappings produce functional WASM code
- ✅ Target selection maps (Reality, Context, Stability) → Target
- ✅ CHAOTIC/unstable code forces WASM unconditionally

### Demo
```bash
cd impl/claude
uv run python demos/wasm_sandbox_demo.py
# Opens browser with sandboxed agent
```

---

## Phase 3: Marimo Integration (Week 2) — ✅ COMPLETE

**Goal**: Enable interactive agent exploration via notebook cells.

**Completed**: 2025-12-21 | **Tests**: 366 passing (54 new marimo tests)

### Tasks

```
[x] Implement MarimoProjector
    File: impl/claude/system/projector/marimo.py (NEW)
    - Implements Projector[str] protocol
    - Generates marimo cell with:
      - mo.ui.text_area() for input
      - mo.ui.run_button() for execution
      - mo.vstack/mo.hstack for layout
      - mo.callout() for persona and errors
      - mo.accordion() for source viewer
    - Capability mappings:
      - @Stateful → mo.state() for persistence
      - @Soulful → Persona badge via mo.callout
      - @Observable → Metrics with start_metrics()/get_metrics()
      - @Streamable → mo.status.progress_bar() indicator

[x] Wire to `kg a manifest --target marimo`
    File: impl/claude/protocols/cli/commands/agent/manifest.py
    - Added marimo to VALID_TARGETS
    - Added _execute_marimo_manifest() function

[x] Test with 54 comprehensive tests
    File: impl/claude/system/projector/_tests/test_marimo.py
    - Cell generation, capability mappings
    - Artifact metadata, decorator stripping
    - Source viewer, import management
    - Error handling, projector composition
```

### Success Criteria ✅ (All Met)
- ✅ `kg a manifest MyAgent --target marimo` produces valid notebook cell
- ✅ Generated cell includes interactive widgets for agent capabilities
- ✅ Target selection: PROBABILISTIC + interactive=True → MARIMO

---

## Phase 4: Agent Foundry Service (Week 3) — ✅ COMPLETE

**Goal**: Create the AgentFoundry Crown Jewel that orchestrates J-gent + Alethic Projection.

**Completed**: 2025-12-21 | **Tests**: 48 new foundry tests (414 total)

### Tasks

```
[x] Create services/foundry/ Crown Jewel structure
    Directory: impl/claude/services/foundry/ (NEW)
    ├── __init__.py        # Exports
    ├── contracts.py       # Request/Response dataclasses
    ├── polynomial.py      # FOUNDRY_POLYNOMIAL (8 states)
    ├── operad.py          # FOUNDRY_OPERAD (composition grammar)
    ├── cache.py           # EphemeralAgentCache (LRU + TTL + metrics)
    ├── core.py            # AgentFoundry orchestrator
    ├── node.py            # @node("self.foundry") registration
    └── _tests/
        ├── test_core.py       # 22 tests
        ├── test_cache.py      # 15 tests
        └── test_polynomial.py # 11 tests

[x] Implement AgentFoundry orchestrator
    File: impl/claude/services/foundry/core.py
    - forge() method: check cache → classify → generate → validate → select → project → cache
    - Integration with RealityClassifier, MetaArchitect, Chaosmonger, TargetSelector
    - manifest() returns FoundryManifestResponse with stats

[x] Wire to AGENTESE (self.foundry.*)
    File: impl/claude/services/foundry/node.py
    - Register @node("self.foundry") with aspects:
      - manifest, forge, inspect, cache, promote
    - Rendering classes for each aspect

[x] Integrate RealityClassifier with Projector selection
    File: impl/claude/services/foundry/core.py
    - Uses J-gent's RealityClassifier for reality classification
    - Uses TargetSelector for target selection
    - Maps Target → Projector for artifact generation

[x] Wire to providers.py
    File: impl/claude/services/providers.py
    - Added get_foundry_service() async function
    - Registered foundry_service in container
    - Import FoundryNode for @node registration
```

### Success Criteria ✅ (All Met)
- ✅ `await logos.invoke("self.foundry.forge", umwelt, intent="...")` produces compiled agent
- ✅ Reality classification correctly determines target
- ✅ CHAOTIC reality or unstable code → forces WASM target
- ✅ Ephemeral agents cached by (intent, context) hash
- ✅ All 48 tests pass, mypy clean

---

## Phase 5: Promotion + Optimization (Week 4)

**Goal**: Enable ephemeral agents to graduate to permanence based on proven behavior.

### Tasks

```
[ ] Implement PromotionPolicy with tunable hyperparameters
    File: impl/claude/services/foundry/promotion.py
    - dataclass with tunable thresholds (invocation, success rate, diversity, age)
    - Metadata annotations for optimization

[ ] Add PromotionOptimizer for threshold learning
    File: impl/claude/services/foundry/promotion.py
    - Track promotion outcomes
    - Adjust thresholds based on usefulness feedback
    - Bayesian optimization for threshold tuning

[ ] Add metrics tracking for ephemeral agents
    File: impl/claude/services/foundry/cache.py
    - Track invocations, success/failure, unique inputs
    - Store metrics with cached agents

[ ] Create promotion workflow with Judge approval
    File: impl/claude/services/foundry/promotion.py
    - Integration with Judge for taste/ethics evaluation
    - Promotion writes to spec/ directory
    - Emits AgentPromoted/AgentPromotionRejected events
```

### Success Criteria
- Ephemeral agents accumulate metrics over invocations
- `self.foundry.promote` triggers Judge evaluation
- Promoted agents persist to spec/ with full documentation
- PromotionOptimizer adjusts thresholds based on feedback

---

## Files Summary

### Created (Phase 1) ✅
```
impl/claude/system/projector/docker.py          # DockerProjector + DockerArtifact
impl/claude/system/projector/compose.py         # ComposedProjector, IdentityProjector, >> operator
impl/claude/system/projector/_tests/test_docker.py  # 33 tests for Docker + composition
```

### Created (Phase 2) ✅
```
impl/claude/system/projector/wasm.py            # WASMProjector + WASMArtifact (397 lines)
impl/claude/system/projector/_tests/test_wasm.py   # 41 tests for WASM projector
impl/claude/demos/wasm_sandbox_demo.py          # Demo script (opens browser)
impl/claude/demos/text_transformer_sandbox.html # Generated demo HTML bundle
impl/claude/agents/j/target_selector.py         # Target Selection: (Reality, Context, Stability) → Target
impl/claude/agents/j/_tests/test_target_selector.py  # 45 tests for target selection
```

### Created (Phase 3) ✅
```
impl/claude/system/projector/marimo.py            # MarimoProjector + MarimoArtifact (350+ lines)
impl/claude/system/projector/_tests/test_marimo.py  # 54 tests for Marimo projector
```

### Modified (Phase 1) ✅
```
impl/claude/protocols/cli/handlers/a_gent.py        # --target, --stream, --trace flags
impl/claude/protocols/cli/commands/agent/__init__.py # Help text updates
impl/claude/protocols/cli/commands/agent/manifest.py # Target routing dispatch
impl/claude/protocols/cli/commands/agent/run.py      # Accept stream/trace flags
impl/claude/system/projector/__init__.py             # Export Docker, Compose, Identity
```

### Modified (Phase 2) ✅
```
impl/claude/system/projector/__init__.py             # Export WASM, WASMArtifact
impl/claude/protocols/cli/commands/agent/manifest.py # Added wasm target routing
```

### Modified (Phase 3) ✅
```
impl/claude/system/projector/__init__.py             # Export Marimo, MarimoArtifact
impl/claude/protocols/cli/commands/agent/manifest.py # Added marimo target routing
```

### Created (Phase 4) ✅
```
impl/claude/services/foundry/__init__.py        # Exports
impl/claude/services/foundry/contracts.py       # Request/Response dataclasses
impl/claude/services/foundry/polynomial.py      # FOUNDRY_POLYNOMIAL (8 states)
impl/claude/services/foundry/operad.py          # FOUNDRY_OPERAD (composition grammar)
impl/claude/services/foundry/cache.py           # EphemeralAgentCache (LRU + TTL + metrics)
impl/claude/services/foundry/core.py            # AgentFoundry orchestrator
impl/claude/services/foundry/node.py            # @node("self.foundry") registration
impl/claude/services/foundry/_tests/__init__.py
impl/claude/services/foundry/_tests/test_core.py      # 22 tests
impl/claude/services/foundry/_tests/test_cache.py     # 15 tests
impl/claude/services/foundry/_tests/test_polynomial.py # 11 tests
```

### Modified (Phase 4) ✅
```
impl/claude/services/providers.py               # Added get_foundry_service(), registered foundry_service
```

### Planned (Future Phases)
```
impl/claude/services/foundry/promotion.py       # PromotionPolicy, PromotionOptimizer (Phase 5)
impl/claude/templates/agent_exploration.marimo  # Marimo template (optional future)
```

---

## Risk Register

| Risk | Mitigation |
|------|------------|
| WASM compilation complexity | Start with Pyodide (mature), fallback to simpler agents |
| MetaArchitect quality | Leverage existing J-gent tests, add property-based tests |
| Promotion threshold tuning | Start conservative, enable per-user overrides |
| Projector composition edge cases | Verify composition laws with property-based tests |

---

## Decision Log

| Decision | Rationale | Date |
|----------|-----------|------|
| WASM as Phase 2 priority | Essential for zero-trust JIT; Servo foundation available | 2025-12-21 |
| Foundry as Crown Jewel | Service-level orchestration, not infrastructure | 2025-12-21 |
| Meta-parameterized thresholds | Learn from feedback, not hardcode | 2025-12-21 |
| Projector composition required | Composability principle; enables multi-target | 2025-12-21 |
| Monkey-patch >> operator | Avoids modifying base.py; clean separation of concerns | 2025-12-21 |
| DockerArtifact struct | Carries metadata (image, ports, volumes) for downstream composition | 2025-12-21 |
| --stream/--trace parsed not implemented | Flags wired for future; behavior requires Flux integration | 2025-12-21 |
| Pyodide over RustPython | Pyodide is more mature, has larger community, better tested | 2025-12-21 |
| HTML bundle output | Self-contained file, no server required, just open in browser | 2025-12-21 |
| localStorage for @Stateful | Simpler than IndexedDB, sufficient for demo/prototype phase | 2025-12-21 |
| Target in J-gent not Projector | Target selection is classification (J-gent's job), not projection | 2025-12-21 |
| Forced flag for safety targets | Distinguishes "safety required" from "user preference" | 2025-12-21 |
| CHAOTIC before UNSTABLE check | Reality classification is cheaper than Chaosmonger analysis | 2025-12-21 |
| EphemeralAgentCache as LRU | Bounded memory, oldest evicted, metrics for promotion decisions | 2025-12-21 |
| TTL expiration in cache | Agents stale after 24h unless accessed; prevents cruft accumulation | 2025-12-21 |
| Foundry returns cache_key | Enables later inspection, promotion, and cache coherence | 2025-12-21 |
| Unique var names per match case | Mypy requires this to track types correctly in match statements | 2025-12-21 |

---

## Voice Anchors

*"Daring, bold, creative, opinionated but not gaudy"*
- J-gent + Alethic Projection IS THE answer to dynamic agent creation
- WASM sandbox for chaotic reality — trust no one
- Promotion pipeline preserves curation — not everything becomes permanent

*"The Mirror Test: Does K-gent feel like me on my best day?"*
- Agent Factory that materializes the right agent for any task, deploys it anywhere, graduates it based on proven behavior — this is Kent's vision

*"Tasteful > feature-complete"*
- Focus on core synthesis (Foundry Crown Jewel)
- WASM is priority for safety, not feature completeness
- Defer multi-language JIT (far future)

---

*"The agent that doesn't exist yet is the agent you need most. Now we can forge it on demand, project it anywhere, and graduate it to permanence."*
