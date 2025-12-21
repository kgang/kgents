# Alethic Architecture & Projector Robustification

> *"The Nucleus holds truth. The Halo declares potential. The Projector manifests reality."*

**Session Type**: Hardening / Enhancement
**Prerequisites**: Read `spec/a-gents/alethic.md`, `spec/protocols/projection.md`

---

## Context

The Alethic Architecture was just refactored (2025-12-21) to focus purely on truth-preserving structure. The core triad:

```
┌─────────────────────────────────────────────────────────────────────┐
│  NUCLEUS         Pure Agent[A, B] logic (what it does)              │
├─────────────────────────────────────────────────────────────────────┤
│  HALO            @Capability.* decorators (what it could become)    │
├─────────────────────────────────────────────────────────────────────┤
│  PROJECTOR       Target-specific compilation (how it manifests)     │
└─────────────────────────────────────────────────────────────────────┘
```

**Current State**:
- ✅ `AlethicAgent` polynomial state machine (GROUNDING→DELIBERATING→JUDGING→SYNTHESIZING)
- ✅ `@Capability.*` Halo decorators (Stateful, Soulful, Observable, Streamable)
- ✅ Archetypes (Kappa, Lambda, Delta)
- ✅ `spec/a-gents/alethic.md` deep dive
- ⚠️ Projectors exist but need robustification (`system/projector/`)
- ⚠️ `spec/protocols/projection.md` covers UI projection, not agent compilation

---

## Mission

**Robustify the Alethic Architecture** by:
1. Strengthening the Projector implementations (Local, K8s)
2. Adding missing projector types (CLI, marimo, WASM?)
3. Creating `spec/protocols/alethic-projection.md` for agent compilation (distinct from UI projection)
4. Verifying the full Nucleus→Halo→Projector pipeline with tests
5. Advocating for usage via CLI `kg a manifest/run` improvements

---

## Phase 1: Audit Current Projector State

### Files to Examine

```
impl/claude/system/projector/
├── base.py           # BaseProjector protocol
├── local.py          # LocalProjector (in-process)
├── k8s.py            # K8sProjector (Kubernetes YAML)
├── k8s_database.py   # K8s + database considerations
└── _tests/
```

### Audit Questions

1. **Does BaseProjector define a clean protocol?**
   - `project(agent_class, halo) → Output`
   - Are outputs typed properly?

2. **Does LocalProjector handle all Halo capabilities?**
   - Stateful → inject MemoryStore?
   - Soulful → inject K-gent mediation?
   - Observable → wire metrics?
   - Streamable → enable SSE?

3. **Does K8sProjector generate correct manifests?**
   - Stateful → StatefulSet vs Deployment?
   - Replicated → HorizontalPodAutoscaler?
   - Secrets/ConfigMaps for configuration?

4. **What's missing?**
   - CLIProjector (shell-executable agent)?
   - MarimoProjector (notebook cell)?
   - WASMProjector (browser-runnable)?

---

## Phase 2: Spec Enhancement

### Create `spec/protocols/alethic-projection.md`

This should cover **agent compilation** (Nucleus+Halo→Target), distinct from **UI projection** (State→Renderable).

```markdown
# Alethic Projection Protocol

> Projectors compile agents to targets. Not rendering—compilation.

## The Projection Functor

```
Projector[T] : (Nucleus, Halo) → Executable[T]

Where:
- Nucleus = Agent[A, B] (pure logic)
- Halo = Set[Capability] (declarative metadata)
- T = Target (Local, K8s, CLI, marimo, WASM)
- Executable[T] = Target-specific runnable
```

## Target Registry

| Target | Output | Reads From Halo |
|--------|--------|-----------------|
| Local | Python callable | Stateful→MemoryStore, Soulful→K-gent |
| K8s | YAML manifests | All capabilities → K8s resources |
| CLI | Shell script | Stateful→persistence, Streamable→stdout |
| marimo | Cell template | Observable→reactive |
| WASM | .wasm binary | Future: sandboxed agents |

## Projector Laws

1. **Determinism**: Same (Nucleus, Halo) → Same output
2. **Capability Preservation**: Halo capabilities map to target features
3. **Composability**: Projectors compose (K8s ∘ Local = K8s with local fallback)
```

### Update `spec/protocols/projection.md`

Add section clarifying the distinction:

```markdown
## Two Projection Domains

| Domain | Protocol | Functor | Purpose |
|--------|----------|---------|---------|
| **UI Projection** | This document | State → Renderable[T] | Display agent state |
| **Agent Compilation** | `alethic-projection.md` | (Nucleus, Halo) → Executable[T] | Deploy agents |

The Alethic Architecture uses both:
- Agents are COMPILED via alethic-projection
- Agent STATE is RENDERED via ui-projection
```

---

## Phase 3: Implementation Hardening

### LocalProjector Enhancements

```python
class LocalProjector(BaseProjector[LocalAgent]):
    """Compile agent to in-process callable."""

    def project(self, agent_cls: type[Agent], halo: Halo) -> LocalAgent:
        # 1. Wrap nucleus
        nucleus = agent_cls()

        # 2. Apply Halo capabilities
        if halo.has(StatefulCapability):
            cap = halo.get(StatefulCapability)
            nucleus = self._inject_memory(nucleus, cap.schema)

        if halo.has(SoulfulCapability):
            cap = halo.get(SoulfulCapability)
            nucleus = self._inject_soul(nucleus, cap.persona)

        if halo.has(ObservableCapability):
            cap = halo.get(ObservableCapability)
            nucleus = self._inject_metrics(nucleus, cap.metrics)

        return LocalAgent(nucleus)
```

### K8sProjector Enhancements

```python
class K8sProjector(BaseProjector[str]):
    """Compile agent to Kubernetes YAML."""

    def project(self, agent_cls: type[Agent], halo: Halo) -> str:
        manifests = []

        # Base deployment
        base = self._base_deployment(agent_cls)

        # Apply capabilities
        if halo.has(StatefulCapability):
            base = self._convert_to_statefulset(base)
            manifests.append(self._pvc_template())

        if halo.has(ReplicatedCapability):
            manifests.append(self._hpa_manifest())

        if halo.has(ObservableCapability):
            manifests.append(self._servicemonitor())

        manifests.insert(0, base)
        return "\n---\n".join(manifests)
```

### New: CLIProjector

```python
class CLIProjector(BaseProjector[str]):
    """Compile agent to shell-executable script."""

    def project(self, agent_cls: type[Agent], halo: Halo) -> str:
        return f'''#!/usr/bin/env python
from agents.a import {agent_cls.__name__}

if __name__ == "__main__":
    import asyncio
    import sys

    agent = {agent_cls.__name__}()
    input_data = sys.stdin.read() if not sys.stdin.isatty() else sys.argv[1]
    result = asyncio.run(agent.invoke(input_data))
    print(result)
'''
```

---

## Phase 4: CLI Advocacy

### Improve `kg a` Commands

```bash
# Current
kg a manifest MyAgent    # Generates K8s YAML

# Enhanced
kg a manifest MyAgent --target k8s      # K8s YAML (default)
kg a manifest MyAgent --target docker   # Dockerfile
kg a manifest MyAgent --target cli      # Shell script
kg a manifest MyAgent --target marimo   # Notebook cell

kg a run MyAgent --input "hello"        # Run locally
kg a run MyAgent --stream               # SSE streaming mode
kg a run MyAgent --trace                # Show state transitions

kg a inspect MyAgent                    # Show Halo + capabilities
kg a inspect MyAgent --polynomial       # Show state machine diagram
```

### Add `kg a validate`

```bash
kg a validate MyAgent                   # Verify Halo is consistent
# Checks:
# - Stateful has schema
# - Soulful has persona
# - Observable has metrics
# - No conflicting capabilities
```

---

## Phase 5: Test Coverage

### Required Tests

```python
# test_projector_laws.py

class TestProjectorLaws:
    def test_determinism(self):
        """Same input → same output."""
        p = LocalProjector()
        result1 = p.project(MyAgent, halo)
        result2 = p.project(MyAgent, halo)
        assert result1 == result2

    def test_capability_preservation(self):
        """Halo capabilities map to features."""
        halo = Halo({StatefulCapability(schema=MySchema)})
        agent = LocalProjector().project(MyAgent, halo)
        assert hasattr(agent, '_memory_store')

    def test_empty_halo(self):
        """Empty halo produces minimal agent."""
        agent = LocalProjector().project(MyAgent, Halo())
        assert not hasattr(agent, '_memory_store')
```

### Property-Based Tests

```python
from hypothesis import given, strategies as st

@given(capabilities=st.lists(st.sampled_from([
    StatefulCapability(schema=dict),
    SoulfulCapability(persona="test"),
    ObservableCapability(metrics=["latency"]),
])))
def test_halo_projection_never_crashes(capabilities):
    """Any valid Halo can be projected."""
    halo = Halo(set(capabilities))
    result = LocalProjector().project(MyAgent, halo)
    assert result is not None
```

---

## Success Criteria

| Criterion | Metric |
|-----------|--------|
| LocalProjector handles all 4 capabilities | Tests pass |
| K8sProjector generates valid YAML | `kubectl --dry-run=client` passes |
| CLIProjector generates runnable script | Script executes |
| `spec/protocols/alethic-projection.md` created | Spec complete |
| `spec/protocols/projection.md` updated | Distinction clear |
| `kg a validate` command works | CLI functional |
| 90%+ projector test coverage | Coverage report |

---

## Voice Anchors

*"Daring, bold, creative, opinionated but not gaudy"*

This work is opinionated:
- Projectors are NOT optional—they're how agents manifest
- Capabilities are NOT runtime—they're compile-time metadata
- The distinction between UI projection and agent compilation is CLEAR

*"Tasteful > feature-complete"*

Don't add WASMProjector just because we can. Focus on:
1. LocalProjector (must be solid)
2. K8sProjector (production path)
3. CLIProjector (developer experience)

---

## Files to Touch

```
# Spec
spec/protocols/alethic-projection.md    # NEW
spec/protocols/projection.md            # UPDATE (distinction)
spec/a-gents/alethic.md                 # UPDATE (cross-ref)

# Impl
impl/claude/system/projector/base.py    # HARDEN
impl/claude/system/projector/local.py   # HARDEN
impl/claude/system/projector/k8s.py     # HARDEN
impl/claude/system/projector/cli.py     # NEW
impl/claude/protocols/cli/handlers/a_gent.py  # ENHANCE

# Tests
impl/claude/system/projector/_tests/test_laws.py  # NEW
impl/claude/system/projector/_tests/test_cli.py   # NEW
```

---

*"The Projector is the bridge between potential and reality."*
