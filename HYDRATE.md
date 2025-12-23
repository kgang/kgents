# HYDRATE.md — The Seed

> *"To read is to invoke. There is no view from nowhere."*

Minimal context for agents. For humans: start with [README.md](README.md).

---

## Principles

**Tasteful** • **Curated** • **Ethical** • **Joy-Inducing** • **Composable** • **Heterarchical** • **Generative**

Full specification: [spec/principles.md](spec/principles.md)

---

## AGENTESE (Five Contexts)

`world.*` `self.*` `concept.*` `void.*` `time.*`

**Aspects**: `manifest` • `witness` • `refine` • `sip` • `tithe` • `lens` • `define`

```python
await logos.invoke("world.house.manifest", umwelt)  # Observer-dependent
```

---

## Built Systems (USE THESE)

| Category | Location | Purpose |
|----------|----------|---------|
| **Categorical** | `agents/poly/`, `agents/operad/`, `agents/sheaf/` | PolyAgent, composition grammar, emergence |
| **Streaming** | `agents/flux/` | Living pipelines, event-driven flows |
| **Semantics** | `protocols/agentese/` | Logos, parser, JIT, wiring |
| **SpecGraph** | `protocols/specgraph/` | Specs as navigable hypergraph |
| **Services** | `services/` | Crown Jewels (Brain, Witness, Atelier, Liminal) |
| **Soul** | `agents/k/` | LLM dialogue, hypnagogia, gatekeeper |
| **Memory** | `agents/m/` | Crystals, cartography, stigmergy |
| **UI** | `agents/i/reactive/` | Signal/Computed/Effect → multi-target |

---

## Crown Jewels (Post-Extinction)

| Jewel | Status | Purpose |
|-------|--------|---------|
| Brain | 100% | Spatial cathedral of memory + TeachingCrystal crystallization |
| Witness | 98% | Marks, crystals, streaming, promotion (678 tests) |
| Atelier | 75% | Design forge and creative workshop |
| Liminal | 50% | Transition protocols: Morning Coffee |

*Town, Park, Gestalt, Forge, Coalition, Muse, Gardener — archived 2025-12-21*

---

## Witness: Marks & Decisions

> *"The proof IS the decision. The mark IS the witness."*

### Mark Moments (`km`)

```bash
km "what happened"                         # Basic mark
km "insight" --reasoning "why it matters"  # With justification
km "gotcha" --tag gotcha --tag agentese    # Tagged for retrieval
km "action" --json                         # Machine-readable
```

**Tags**: `eureka` `gotcha` `taste` `friction` `joy` `veto` `decision` `pattern`

### Record Decisions (`kg decide`)

```bash
# Quick decision
kg decide --fast "choice" --reasoning "why"

# Full dialectic (Kent + Claude differ)
kg decide --kent "view" --kent-reasoning "why" \
          --claude "view" --claude-reasoning "why" \
          --synthesis "fusion" --why "justification"
```

### Query & Crystallize

```bash
kg witness show --today                # Today's marks
kg witness show --tag joy              # Filter by tag
kg witness crystallize                 # Marks → Session crystal
kg witness context --budget 2000       # Budget-aware context
```

**Crystal Hierarchy**: Marks → Session (L0) → Day (L1) → Week (L2) → Epoch (L3)

---

## Skills (READ THESE)

`docs/skills/` — Essential skills covering every task.

**Universal**: `metaphysical-fullstack.md` • `crown-jewel-patterns.md` • `test-patterns.md`

---

## Current Focus (2025-12-23)

**Hypergraph Emacs + Membrane**: The frontend IS the agent.

| Phase | What | Status |
|-------|------|--------|
| 1-2 | EditorPolynomial + ContextNode.follow() | ✅ Done |
| 3 | K-Block auto-creation on INSERT + `:w`/`:q!` | ✅ Done |
| 4 | WitnessedGraph Integration | ✅ Done |

**AD-015 Radical Unification** (2025-12-23): LedgerCache DELETED → ProxyHandleStore.
- `ensure_scanned()` → `proxy_store.get_or_raise(SourceType.SPEC_CORPUS)`
- `analyze_now()` → `proxy_store.compute()` with reactive invalidation
- One truth. One store. ~60 lines deleted. 98 tests pass.

See `NOW.md` for active plans.

---

## Commands

```bash
# Backend
cd impl/claude && uv run pytest -q && uv run mypy .

# Frontend
cd impl/claude/web && npm run typecheck && npm run lint
```

---

*Lines: 100. Ceiling: 120.*
