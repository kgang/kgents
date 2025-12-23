# AD-015: Proxy Handles & Transparent Batch Processes

**Date**: 2025-12-23

> The representation of an object is distinct from the object itself. Analysis produces PROXY HANDLES—independent artifacts that users and agents work with. Expensive computation MUST be explicit and transparent.

---

## The Philosophical Insight

> *"The analysis is not the thing. It is a proxy handle to the thing."*

When we analyze a spec file, the analysis is a *separate entity*—a lens, a projection, a handle. It:
- Has its own lifecycle (created, updated, stale, refreshed)
- May diverge from the source (spec changes, analysis doesn't)
- Is what users and agents actually interact with

This is not merely "caching"—it's acknowledging that **representation and reality are distinct**. We work with projections of truth, not truth itself.

## Why This Matters for AI Agents

AI agents need to know:
1. **What is being computed** — not hidden background tasks
2. **When computation happens** — explicit triggers, not implicit magic
3. **What they're working with** — a proxy handle, not live truth
4. **How to refresh** — explicit commands, not hoping for coherence

Hidden computation is hostile to agents. They can't reason about what they can't see.

## Decision

Expensive computation MUST be:

1. **Explicit**: User/agent triggers it (`kg spec analyze`)
2. **Transparent**: Progress is visible, not hidden
3. **Separated**: Analysis artifacts are distinct from source
4. **Named**: Proxy handles have identity (timestamp, version)

## The Diagnosis

```
BEFORE (Anti-pattern: Hidden Computation)
┌─────────────────────────────────────────────────────────────┐
│ Server Start                                                 │
│     │                                                        │
│     ├──► _warm_ledger_cache() ─── 10s ───►  ??? (hidden)   │
│     │    (user/agent doesn't know this is happening)        │
│     │                                                        │
│     └──► First Request ─── race condition ───► Response     │
│          (may get stale, partial, or racing data)           │
└─────────────────────────────────────────────────────────────┘

AFTER (Pattern: Transparent Proxy Handles)
┌─────────────────────────────────────────────────────────────┐
│ Explicit Analysis (user/agent triggers)                      │
│     │                                                        │
│     └──► kg spec analyze ─── 10s ───► proxy_handle.json    │
│          (transparent: user knows what's happening)          │
│                                                              │
│ Server Serve (instant, no surprises)                         │
│     │                                                        │
│     └──► load(proxy_handle.json) ─── 50ms ───► Ready       │
│          (user knows they're working with a proxy)           │
└─────────────────────────────────────────────────────────────┘
```

## The Proxy Handle Model

```
┌─────────────────────────────────────────────────────────────┐
│                    THE PROXY HANDLE MODEL                    │
│                                                              │
│   Source (Truth)         Proxy Handle (Representation)       │
│   ──────────────         ────────────────────────────        │
│   spec/principles.md  →  analysis/principles_v3.json         │
│   impl/claude/        →  analysis/codebase_topology.json     │
│   witness marks       →  analysis/mark_graph.json            │
│                                                              │
│   Properties:                                                │
│   • Independent lifecycle (can be stale)                     │
│   • Explicit creation (kg analyze)                           │
│   • Explicit refresh (kg refresh)                            │
│   • Named & versioned (who, when, what)                      │
│                                                              │
│   The handle is NOT the truth. It is a LENS on truth.        │
└─────────────────────────────────────────────────────────────┘
```

## Connection to Transparent Infrastructure Principle

This AD operationalizes Transparent Infrastructure for batch processes:

| Hidden (Bad) | Transparent (Good) |
|--------------|-------------------|
| Background thread at startup | Explicit CLI command |
| Silent cache warming | Progress indicator |
| "Smart" lazy loading | Named proxy handles |
| Implicit refresh | `kg refresh` command |

## Connection to AD-004 (Pre-Computed Richness)

AD-004 said "pre-compute demo data." AD-015 generalizes:

```
AD-004: "Demo data should be pre-computed"
AD-015: "ALL analysis produces proxy handles, explicit and transparent"
        ↓
        From tactic to philosophy
```

## Consequences

1. **No hidden computation**: Server startup does NO analysis
2. **Explicit commands**: `kg spec analyze`, `kg codebase scan`, etc.
3. **Proxy handles as artifacts**: JSON files, DB rows with metadata
4. **Staleness is visible**: Handles know their age
5. **Agent-friendly**: Agents can reason about computation state

## Anti-patterns

- Hidden background tasks (hostile to reasoning)
- Implicit "smart" caching (hides when computation happens)
- Treating proxy as truth (forgetting it can be stale)
- Silent refresh (agents can't track state changes)

## Connection to Principles

| Principle | How AD-015 Embodies It |
|-----------|------------------------|
| **Ethical** | Transparent about what's happening; no hidden work |
| **Transparent Infrastructure** | Batch processes are visible, not secret |
| **Generative** | Analysis artifacts are regenerable from source |
| **Heterarchical** | Agents can trigger and observe computation |

## Implementation

- Removed `_warm_ledger_cache()` from `impl/claude/protocols/api/app.py`
- `ensure_scanned()` now requires explicit `analyze_now()` first
- Graceful degradation when proxy handles don't exist

*Zen Principle: The map is not the territory. The proxy is not the truth. But we navigate by maps and work with proxies—so make them visible.*
