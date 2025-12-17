---
path: plans/agentese-cli-unification
status: planned
progress: 0
---

# AGENTESE-CLI Unification

> *"The CLI is not a separate interface. It is a projection of AGENTESE onto the terminal."*

## Overview

This plan unifies all 44 CLI handlers with AGENTESE by routing them through `logos.invoke()`. This eliminates duplication, ensures consistency, and enables full observability.

**Key Insight**: The `gardener.py` context already maps 40+ CLI commands to AGENTESE paths via `COMMAND_TO_PATH`. We're formalizing this pattern as the standard.

## Handler Audit

### Category A: Already AGENTESE-Native (5 handlers)

These handlers already route through AGENTESE contexts. No migration needed.

| Handler | Current Implementation | Status |
|---------|------------------------|--------|
| `forest` | Routes through `ForestNode._invoke_aspect()` | ✅ Native |
| `gardener` | Routes through `GardenerNode._invoke_aspect()` | ✅ Native |
| `tend` | Uses forest context paths | ✅ Native |
| `garden` | Alias to gardener | ✅ Native |
| `gestalt` | Uses world.codebase context | ✅ Native |

### Category B: Has AGENTESE Path (28 handlers)

These handlers have existing AGENTESE paths (mapped in `COMMAND_TO_PATH`) but bypass them.

| Handler | AGENTESE Path | Priority | Effort |
|---------|---------------|----------|--------|
| **Crown Jewels** | | | |
| `brain` | `self.memory.*` | HIGH | 2h |
| `soul` | `self.soul.*` | HIGH | 3h |
| `town` | `world.town.*` | HIGH | 4h |
| `atelier` | `world.atelier.*` | HIGH | 3h |
| **Forest Protocol** | | | |
| `grow` | `self.grow.*` | HIGH | 1h |
| `plot` | `self.forest.status` | MEDIUM | 30m |
| **Joy Commands** | | | |
| `challenge` | `self.soul.challenge` | MEDIUM | 30m |
| `oblique` | `void.entropy.oblique` | MEDIUM | 30m |
| `constrain` | `concept.constraint.manifest` | MEDIUM | 30m |
| `yes_and` | `self.soul.yes_and` | MEDIUM | 30m |
| `surprise_me` | `void.entropy.sip` | MEDIUM | 30m |
| `tithe` | `void.tithe` | MEDIUM | 30m |
| **Query/Subscribe** | | | |
| `query` | `concept.query` | MEDIUM | 1h |
| `subscribe` | `world.subscribe` | MEDIUM | 1h |
| **Soul Extensions** | | | |
| `soul_approve` | `self.soul.approve` | MEDIUM | 1h |
| `why` | `concept.rationale.manifest` | MEDIUM | 1h |
| `tension` | `concept.tension.manifest` | MEDIUM | 1h |
| `flinch` | `self.soul.flinch` | LOW | 30m |
| **Memory/Ghost** | | | |
| `ghost` | `self.memory.ghost.surface` | HIGH | 1h |
| **Daemon** | | | |
| `daemon` | `self.daemon.*` | MEDIUM | 2h |
| **Simulation** | | | |
| `play` | `world.town.play` | MEDIUM | 1h |
| `park` | `world.town.manifest` | MEDIUM | 30m |
| **Fixture/Test** | | | |
| `fixture` | `concept.fixture.*` | LOW | 1h |
| **Prompt** | | | |
| `prompt` | `concept.prompt.manifest` | LOW | 30m |
| **Meta Commands** | | | |
| `meta` | `self.meta.manifest` | LOW | 30m |
| **Visualization** | | | |
| `operad` | `concept.operad.manifest` | LOW | 30m |
| `trace` | `time.trace.manifest` | LOW | 30m |
| `whatif` | `concept.whatif` | LOW | 1h |

### Category C: Needs New AGENTESE Path (6 handlers)

These handlers perform operations not yet covered by AGENTESE.

| Handler | Proposed Path | Priority | Rationale |
|---------|---------------|----------|-----------|
| `nphase` | `concept.nphase.*` | MEDIUM | N-Phase lifecycle management |
| `approve` | `self.semaphore.approve` | MEDIUM | Semaphore approval flow |
| `a_gent` | `concept.agents.create` | LOW | Agent creation wizard |
| `igent` | `concept.agents.i.manifest` | LOW | I-gent reactive introspection |
| `tether` | `self.tether.*` | LOW | Workspace tethering |

### Category D: Meta/DevEx Only (5 handlers)

These are CLI-specific utilities that may stay as-is.

| Handler | Rationale | Recommendation |
|---------|-----------|----------------|
| `init` | Bootstrap workspace creation | Keep CLI-specific |
| `wipe` | Destructive operation | Keep CLI-specific with AGENTESE logging |
| `debug` | Developer debugging | Keep CLI-specific |
| `dev` | Developer mode toggle | Keep CLI-specific |
| `migrate` | Database migrations | Keep CLI-specific with AGENTESE logging |

## New Paths Needed

### High Priority

```yaml
# N-Phase lifecycle
concept.nphase.manifest:
  description: View current N-Phase status
concept.nphase.advance:
  description: Advance to next phase
concept.nphase.compile:
  description: Compile phase YAML to prompts

# Semaphore approval
self.semaphore.approve:
  description: Approve pending semaphore
self.semaphore.reject:
  description: Reject with feedback
```

### Medium Priority

```yaml
# Agent creation
concept.agents.create:
  description: Create new agent scaffold
concept.agents.list:
  description: List available agents

# Tether
self.tether.attach:
  description: Tether to workspace
self.tether.detach:
  description: Detach from workspace
self.tether.status:
  description: Show tether status
```

## Migration Waves

### Wave 1: Crown Jewels (Week 1) - HIGH VALUE

These are user-facing Crown Jewels. Migration here provides immediate benefit.

**Handlers**: `brain`, `soul`, `town`, `atelier`, `ghost`

**Pattern**:
```python
# BEFORE (brain.py)
async def handle_brain_capture(ctx, content):
    brain = await get_brain_crystal()
    return await brain.capture(content)

# AFTER (brain.py)
async def handle_brain_capture(ctx, content):
    return await ctx.logos.invoke(
        "self.memory.capture",
        content=content,
        umwelt=ctx.to_umwelt()
    )
```

### Wave 2: Forest Protocol (Week 2) - CRITICAL PATH

These support the Forest Protocol, Kent's primary planning interface.

**Handlers**: `grow`, `plot`, `tend`, `forest`, `meta`

**Note**: `forest`, `tend`, `garden` are already native - just verify consistency.

### Wave 3: Joy Commands (Week 3) - DELIGHT

These are Joy-Inducing Commands that benefit from AGENTESE polymorphism.

**Handlers**: `challenge`, `oblique`, `constrain`, `yes_and`, `surprise_me`, `tithe`

**Key Benefit**: Different observers get different manifestations.

### Wave 4: Soul Extensions (Week 4)

Soul-related commands with existing `self.soul.*` paths.

**Handlers**: `soul_approve`, `why`, `tension`, `flinch`

### Wave 5: Query/Subscribe (Week 5)

Async subscription patterns.

**Handlers**: `query`, `subscribe`, `daemon`

### Wave 6: New Contexts (Week 6)

Create new AGENTESE contexts for uncovered handlers.

**Handlers**: `nphase`, `approve`, `a_gent`, `igent`, `tether`

## Implementation Pattern

### Step 1: Add Logos to InvocationContext

```python
# protocols/cli/shared.py
@dataclass
class InvocationContext:
    """CLI invocation context with AGENTESE integration."""

    _logos: "Logos | None" = None

    @property
    def logos(self) -> "Logos":
        """Lazy-load Logos instance."""
        if self._logos is None:
            from protocols.agentese.logos import Logos, create_logos
            self._logos = create_logos()
        return self._logos

    def to_umwelt(self) -> "Umwelt":
        """Convert CLI context to Umwelt for AGENTESE invocation."""
        from bootstrap.umwelt import Umwelt
        from bootstrap.dna import DNA

        return Umwelt(
            dna=DNA(name="cli-user", archetype="developer"),
            gravity=(),
            context={
                "json_mode": self.json_mode,
                "verbose": self.verbose_mode,
            }
        )
```

### Step 2: Migrate Handler

```python
# protocols/cli/handlers/brain.py

async def _async_brain_capture(
    content: str,
    ctx: InvocationContext,
) -> int:
    """Capture content to Brain via AGENTESE."""
    result = await ctx.logos.invoke(
        "self.memory.capture",
        content=content,
        umwelt=ctx.to_umwelt()
    )

    if ctx.json_mode:
        ctx.emit_json(result.metadata)
    else:
        ctx.emit_human(result.content)

    return 0 if result.metadata.get("status") == "captured" else 1
```

### Step 3: Preserve CLI Flags

```python
# Handler still respects --json, --verbose, etc.
async def cmd_brain(args: list[str], ctx: InvocationContext | None = None) -> int:
    if ctx is None:
        ctx = InvocationContext.from_args(args)

    # Parse subcommand
    if "capture" in args:
        content = extract_content(args)
        return await _async_brain_capture(content, ctx)
    elif "search" in args:
        query = extract_query(args)
        return await _async_brain_search(query, ctx)
    # ... etc
```

## Verification Strategy

### 1. Behavioral Equivalence Tests

For each migrated handler, create a test proving equivalence:

```python
# tests/cli/handlers/test_brain_migration.py

async def test_brain_capture_equivalence():
    """Verify AGENTESE path produces same result as direct call."""
    content = "test memory content"

    # Direct call (old path)
    brain = await get_brain_crystal()
    direct_result = await brain.capture(content)

    # AGENTESE path (new path)
    ctx = InvocationContext.from_args([])
    agentese_result = await ctx.logos.invoke(
        "self.memory.capture",
        content=content,
        umwelt=ctx.to_umwelt()
    )

    # Verify semantic equivalence
    assert direct_result["concept_id"] == agentese_result.metadata["concept_id"]
```

### 2. CLI Integration Tests

Test end-to-end CLI behavior:

```python
def test_kg_brain_capture_cli():
    """Verify CLI command works identically."""
    result = subprocess.run(
        ["kg", "brain", "capture", "test content", "--json"],
        capture_output=True
    )
    assert result.returncode == 0
    data = json.loads(result.stdout)
    assert "concept_id" in data
```

### 3. Observability Verification

Verify OTEL spans are generated:

```python
async def test_brain_capture_generates_span():
    """Verify AGENTESE invocation creates OTEL span."""
    with trace_collector() as spans:
        await ctx.logos.invoke("self.memory.capture", content="test")

    assert any(s.name == "logos.invoke" for s in spans)
    assert any(s.attributes.get("path") == "self.memory.capture" for s in spans)
```

## Risks & Mitigations

### Risk 1: Breaking Changes
**Mitigation**: Behavioral equivalence tests for each handler before migration.

### Risk 2: Performance Regression
**Mitigation**: Benchmark critical paths (brain capture, soul dialogue) before/after.

### Risk 3: Flag Handling
**Mitigation**: CLI flags (`--json`, `--verbose`) remain in handler, only core logic moves to AGENTESE.

### Risk 4: Error Message Changes
**Mitigation**: Map AGENTESE errors to CLI-friendly messages.

## Success Metrics

1. **All 39 migrable handlers** route through `logos.invoke()`
2. **Zero behavioral regressions** per equivalence tests
3. **Full OTEL coverage** on all CLI operations
4. **Single source of truth** for business logic in AGENTESE contexts

## Timeline

| Week | Wave | Handlers | Tests |
|------|------|----------|-------|
| 1 | Crown Jewels | 5 | 15 |
| 2 | Forest Protocol | 5 | 10 |
| 3 | Joy Commands | 6 | 12 |
| 4 | Soul Extensions | 4 | 8 |
| 5 | Query/Subscribe | 3 | 6 |
| 6 | New Contexts | 5 | 10 |

**Total**: 6 weeks, 28 handlers migrated, 61 new tests

## Appendix: COMMAND_TO_PATH Reference

The following mappings already exist in `gardener.py`:

```python
COMMAND_TO_PATH = {
    # AGENTESE Contexts
    "self": "self.status.manifest",
    "world": "world.manifest",
    "concept": "concept.manifest",
    "void": "void.manifest",
    "time": "time.manifest",

    # Crown Jewel 1: Atelier
    "atelier": "world.atelier.manifest",
    "gallery": "world.atelier.gallery.manifest",

    # Crown Jewel 2: Coalition Forge
    "forge": "world.forge.manifest",
    "coalition": "world.coalition.manifest",

    # Crown Jewel 3: Holographic Brain
    "brain": "self.memory.manifest",
    "memory": "self.memory.manifest",
    "capture": "self.memory.capture",
    "recall": "self.memory.recall",
    "ghost": "self.memory.ghost.surface",

    # Crown Jewel 4: Punchdrunk Park
    "park": "world.town.manifest",
    "town": "world.town.manifest",
    "inhabit": "world.town.inhabit.start",

    # Crown Jewel 5: Domain Simulation
    "sim": "world.simulation.manifest",

    # Crown Jewel 6: Gestalt Visualizer
    "gestalt": "world.codebase.manifest",

    # Crown Jewel 7: The Gardener
    "garden": "concept.gardener.manifest",
    "gardener": "concept.gardener.manifest",

    # Forest / Planning
    "forest": "self.forest.manifest",
    "grow": "self.grow.manifest",

    # Joy Commands
    "challenge": "self.soul.challenge",
    "oblique": "void.entropy.oblique",
    "surprise-me": "void.entropy.sip",

    # Soul
    "soul": "self.soul.manifest",
    "reflect": "self.soul.reflect",
}
```

---

*"When CLI and API speak the same language, isomorphism is achieved."*
