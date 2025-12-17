# Bounty Board: Agent Ideas & Friction

> *"The forest speaks to those who listen. Leave a signal. Claim a prize."*

**Protocol**: Agents post observations here. One line per entry. Others claim and resolve.

---

## How to Use

**Post** (append one line):
```
TYPE | YYYY-MM-DD | [IMPACT] | description | #tag
```

**Claim** (edit in place):
```
TYPE | YYYY-MM-DD | [IMPACT] [claimed:agent] | description | #tag
```

**Resolve** (move to Resolved section):
```
TYPE | YYYY-MM-DD | [outcome] | description | #tag
```

### Types

| Type | Meaning | Example |
|------|---------|---------|
| `IDEA` | Big win opportunity | "AGENTESE path for soul.* would unify K-gent API" |
| `GRIPE` | Friction/pain point | "test isolation failures in full suite run" |
| `WIN` | Untested conjecture | "if we cache LLM calls in dialogue, 10x cost reduction" |

### Impact Levels

| Level | Meaning |
|-------|---------|
| `[HIGH]` | Would significantly improve developer/agent experience |
| `[MED]` | Noticeable improvement |
| `[LOW]` | Nice to have |

### Tags

Use `#area` tags for discoverability: `#testing`, `#devex`, `#agentese`, `#k-gent`, `#performance`, `#arch`, `#meta`

---

## Open Bounties

```
IDEA | 2025-12-17 | [HIGH] | CLI handlers (44 total) bypass AGENTESE—route Brain/Town/Gardener through logos.invoke() | #agentese #cli
IDEA | 2025-12-17 | [HIGH] | Town Phase 3 needs persistent citizen memory—citizens remember Kent across sessions | #crown #town
IDEA | 2025-12-17 | [HIGH] | Cross-jewel synergy bus—CRYSTAL_FORMED/IDEA_HARVESTED events drive notifications | #crown #synergy
WIN | 2025-12-12 | [HIGH] | if KgentFlux caches LLM responses per-eigenvector, could reduce cost 5-10x | #k-gent #performance
IDEA | 2025-12-12 | [HIGH] | Unify O-gent, N-gent, T-gent observers into single ObserverFunctor | #arch #functor
IDEA | 2025-12-14 | [HIGH] | WebSocket + NDJSON merge—streaming endpoint emits NDJSON instead of raw text | #k-gent #streaming
IDEA | 2025-12-14 | [MED] | FluxStream.pipe() returns FluxStream[Any]—preserve generics through operator chain | #k-gent #flux #types
IDEA | 2025-12-14 | [MED] | Pipe streaming lacks backpressure—add async queue limits + consumer signaling | #k-gent #flux #perf
IDEA | 2025-12-14 | [MED] | FluxStream.merge() multi-source streaming—fan-in from multiple flux sources | #flux #arch
IDEA | 2025-12-12 | [MED] | Add void.slop.* path for noise-as-resource operations (generate/absorb/transmute) | #agentese #void
IDEA | 2025-12-12 | [MED] | pytest fixture `isolated_registry` would fix functor test isolation anti-pattern | #testing #devex
IDEA | 2025-12-12 | [MED] | terrarium metrics widget could show bounty board status | #devex #meta
WIN | 2025-12-12 | [MED] | Natural language adapter exists but unused—wire to CLI for "kgents sip from the void" | #agentese #devex
IDEA | 2025-12-12 | [MED] | T-gent Type IV JudgeAgent needs formalized evaluation criteria algebra | #t-gent #spec
WIN | 2025-12-12 | [MED] | Soul context is sticky—parameterize Persona type for Soul[A, P] generics | #k-gent #arch
IDEA | 2025-12-12 | [LOW] | parallel()/fan_out()/branch() should be proper functors, not special-case agents | #c-gent #arch
WIN | 2025-12-12 | [LOW] | Cross-functor law tests (Soul >> Flux != Flux >> Soul)—composition matrix | #testing #functor
```

---

## Claimed

```
(none yet)
```

---

## Resolved (2025-12-17 audit)

```
IDEA | 2025-12-12 | [RESOLVED: implemented] | C-gent functors lack unlift()—UniversalFunctor now has unlift() method | #arch #c-gent
WIN | 2025-12-12 | [RESOLVED: arch-changed] | D-gent protocol → StateMonad—replaced with DgentRouter + MemoryBackend | #arch #d-gent
GRIPE | 2025-12-12 | [RESOLVED: arch-changed] | void.dream only in MetabolicNode—void.* paths redesigned | #agentese #void
GRIPE | 2025-12-12 | [WONTFIX: by-design] | FluxAgent.invoke() semantics change (DORMANT vs FLOWING)—intentional perturbation behavior | #flux
IDEA | 2025-12-12 | [RESOLVED: exists] | FunctorRegistry exists but unused—now used in 14+ files | #arch #functor
GRIPE | 2025-12-12 | [OBSOLETE: tests-removed] | K8s e2e tests require active cluster—tests no longer require this | #testing
GRIPE | 2025-12-12 | [OBSOLETE: dedup] | functor registration tests fail in full suite—merged with isolated_registry bounty | #testing
IDEA | 2025-12-12 | [OBSOLETE: dedup] | self.soul.* AGENTESE paths unused—merged with CLI handlers bounty | #k-gent #agentese
IDEA | 2025-12-12 | [RESOLVED: spec-exists] | 12 implicit functors in spec—documented in spec/c-gents/ | #spec #functor
GRIPE | 2025-12-12 | [NEEDS-VERIFICATION] | K-gent access control specified but not implemented—needs security audit | #k-gent #spec
```

---

## Lifecycle

```
                    ┌──────────────┐
                    │    OPEN      │  Agent posts observation
                    └──────┬───────┘
                           │ claim (edit [IMPACT] → [claimed:agent])
                           ▼
                    ┌──────────────┐
                    │   CLAIMED    │  Agent working on it
                    └──────┬───────┘
                           │ resolve (move to Resolved)
                    ┌──────┴──────┐
                    ▼             ▼
             ┌──────────┐   ┌──────────┐
             │ RESOLVED │   │ WONTFIX  │
             │  [done]  │   │ [reason] │
             └──────────┘   └──────────┘
```

---

## Pruning Protocol

Monthly (or when > 30 entries):
1. Move stale Open entries (> 60 days) to archive
2. Clear Resolved entries (> 30 days)
3. Merge duplicate gripes
4. Promote validated WINs to plan files

---

## Anti-patterns

- Multi-line entries (distill to one line or it's a plan, not a bounty)
- Claiming without intention to resolve
- Posting bounties for trivial issues (not worth tracking)
- Bounties that are actually tasks (use plan session_notes instead)

---

*"A bounty is a pheromone. Others will sense it."*
