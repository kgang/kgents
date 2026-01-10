# Skills Quick Reference

> Compressed reference for Claude Code context. For full documentation, read the linked skill files.

---

## Universal Skills (Start Here)

### [cli-strategy-tools.md](cli-strategy-tools.md)
**Use for**: Evidence-driven development with five native operations
**Key gotcha**: Always run `kg probe health --all` at session start
**Trigger**: "audit", "annotate", "experiment", "probe", "compose", "pre-commit"

### [metaphysical-fullstack.md](metaphysical-fullstack.md)
**Use for**: Building any feature (the core architecture pattern)
**Key gotcha**: AGENTESE IS the API; no explicit backend routes needed
**Trigger**: "add feature", "new service", "fullstack", "vertical slice"

### [crown-jewel-patterns.md](crown-jewel-patterns.md)
**Use for**: Implementing service logic (14 battle-tested patterns)
**Key gotcha**: Adapters live in service modules, not infrastructure
**Trigger**: "service pattern", "brain", "town", "persistence"

### [test-patterns.md](test-patterns.md)
**Use for**: Writing tests (T-gent Types I-V, property-based, chaos)
**Key gotcha**: DI injection > mocking; use `set_soul()` pattern
**Trigger**: "add tests", "property-based", "hypothesis", "chaos test"

### [elastic-ui-patterns.md](elastic-ui-patterns.md)
**Use for**: Responsive UI with three-mode pattern
**Key gotcha**: Use density-parameterized constants, not scattered conditionals
**Trigger**: "responsive", "mobile", "density", "compact/comfortable/spacious"

---

## Foundation (Categorical Ground)

### [polynomial-agent.md](polynomial-agent.md)
**Use for**: State machines with mode-dependent inputs
**Key gotcha**: `PolyAgent[S,A,B] > Agent[A,B]` -- mode enables state
**Trigger**: "state machine", "mode-dependent", "add agent", "phases"

### [building-agent.md](building-agent.md)
**Use for**: Agent composition, functors, D-gent memory patterns
**Key gotcha**: Always test instance isolation; global state causes shared memory
**Trigger**: "compose agents", "functor", "D-gent", "memory agent"

---

## Protocol (AGENTESE)

### [agentese-path.md](agentese-path.md)
**Use for**: Adding paths to the five contexts
**Key gotcha**: Always have a default case in match statements for unknown aspects
**Trigger**: "add path", "self.", "world.", "concept.", "void.", "time."

### [agentese-node-registration.md](agentese-node-registration.md)
**Use for**: @node decorator, discovery, BE/FE type sync
**Key gotcha**: `@node` runs at import time; must import module in `gateway.py`
**Trigger**: "@node", "discovery", "node not appearing", "DependencyNotFoundError"

---

## Architecture (Vertical Slice)

### [data-bus-integration.md](data-bus-integration.md)
**Use for**: DataBus, SynergyBus, EventBus patterns
**Key gotcha**: Three buses: DataBus (storage) > SynergyBus (cross-jewel) > EventBus (fan-out)
**Trigger**: "event-driven", "bus", "reactive", "cross-jewel coordination"

### [hypergraph-editor.md](hypergraph-editor.md)
**Use for**: Six-mode modal editing, graph navigation, K-Block
**Key gotcha**: The file is a lie; there is only the graph (focus nodes, traverse edges)
**Trigger**: "editor", "hypergraph", "modal editing", "K-Block"

---

## Witness (Evidence & Derivation)

### [witness-for-agents.md](witness-for-agents.md)
**Use for**: Marks, decisions, context budgets for programmatic agents
**Key gotcha**: Always use `--json` for machine-readable output in agents
**Trigger**: "mark", "witness", "km", "decision", "context budget"

### [derivation-edges.md](derivation-edges.md)
**Use for**: Edge evidence tracking for derivation relationships
**Key gotcha**: Marks prove agents work; edges prove derivations work
**Trigger**: "derivation", "edge evidence", "stigmergy", "confidence"

---

## Process (N-Phase & Research)

### [research-protocol.md](research-protocol.md)
**Use for**: Four-phase experimentation (A toy > B trace > C proof > D scale)
**Key gotcha**: Never skip phases; Phase A catches 80% of setup bugs
**Trigger**: "experiment", "hypothesis", "A/B test", "LLM evaluation"

### [witnessed-regeneration.md](witnessed-regeneration.md)
**Use for**: 5-stage pilot regeneration with witnessing
**Key gotcha**: Stage 3 is BUILD, not verify; generate fresh from spec
**Trigger**: "regenerate", "pilot", "PROTO_SPEC", "contract coherence"

### [plan-file.md](plan-file.md)
**Use for**: Forest Protocol YAML headers, chunks, status lifecycle
**Key gotcha**: Valid statuses are dormant, active, blocked, complete only
**Trigger**: "plan file", "forest", "multi-session", "blockers"

### [spec-template.md](spec-template.md)
**Use for**: Writing generative specs (200-400 lines)
**Key gotcha**: Spec < impl (compression); no function bodies >10 lines
**Trigger**: "write spec", "new spec", "spec structure"

### [spec-hygiene.md](spec-hygiene.md)
**Use for**: 7 bloat patterns to avoid, 5 compression patterns
**Key gotcha**: Laws as algebraic equations, not test code
**Trigger**: "distill spec", "spec too long", "bloat", "compression"

---

## Projection (Multi-Target)

### [projection-target.md](projection-target.md)
**Use for**: Custom targets (CLI/TUI/JSON/marimo/WebGL)
**Key gotcha**: Register projectors at import time for thread safety
**Trigger**: "projection", "render target", "fidelity", "custom target"

### [marimo-projection.md](marimo-projection.md)
**Use for**: marimo notebooks with state, callbacks, late-binding traps
**Key gotcha**: `mo.state()` returns getter function; CALL it with `()`
**Trigger**: "marimo", "notebook", "mo.state", "callback"

---

## Quick Decision Trees

**Before modifying spec?** > `kg audit <spec> --full`

**After implementing spec section?** > `kg annotate --impl --link`

**After fixing non-obvious bug?** > `kg annotate --gotcha`

**Uncertain about approach?** > `kg experiment --adaptive`

**Before commit?** > `kg compose --run "pre-commit"`

**Node not appearing in discovery?** > Check `gateway.py` imports

**DependencyNotFoundError?** > Add provider to `services/providers.py`

**"Objects not valid as React child"?** > Use Pydantic request models (HQ-1)

---

## Key Gotchas Cheat Sheet

| Issue | Cause | Fix |
|-------|-------|-----|
| Node not discovered | Module not imported | Add to `_import_node_modules()` |
| Missing dependency | Provider not registered | Add to `setup_providers()` |
| Shared state bugs | Global state | Use factory with instance isolation |
| API validation errors leak | Bare list params | Use Pydantic request models |
| marimo callback fails | Getter not called | Use `get_state()` not `get_state` |
| Spec too long | Implementation creep | Extract to impl/, keep signatures |
| Test isolation fails | Shared singletons | Use DI over mocking |

---

*Generated: 2026-01-10 | Skills: 24 active | Compressed Reference Edition*
