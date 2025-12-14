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
GRIPE | 2025-12-12 | [MED] | functor registration tests fail in full suite but pass alone—isolation issue | #testing
GRIPE | 2025-12-12 | [LOW] | K8s e2e tests require active cluster—should be marked @pytest.mark.e2e | #testing
IDEA | 2025-12-12 | [HIGH] | self.soul.* AGENTESE paths exist but CLI doesn't use them—unify API | #k-gent #agentese
WIN | 2025-12-12 | [HIGH] | if KgentFlux caches LLM responses per-eigenvector, could reduce cost 5-10x | #k-gent #performance
IDEA | 2025-12-12 | [MED] | terrarium metrics widget could show bounty board status | #devex #meta
IDEA | 2025-12-12 | [HIGH] | C-gent functors (Maybe/Either/List) lack unlift()—can't escape monad nesting | #arch #c-gent
IDEA | 2025-12-12 | [HIGH] | 15+ CLI handlers bypass AGENTESE—route soul/semaphore/status through Logos | #agentese #cli
GRIPE | 2025-12-12 | [HIGH] | void.dream only in MetabolicNode—should be standalone void.dream.* path | #agentese #void
IDEA | 2025-12-12 | [HIGH] | Unify O-gent, N-gent, T-gent observers into single ObserverFunctor | #arch #functor
WIN | 2025-12-12 | [HIGH] | D-gent protocol → StateMonad functor would enable Flux(State(agent)) composition | #arch #d-gent
IDEA | 2025-12-12 | [HIGH] | FunctorRegistry exists but unused—register all functors for declarative composition | #arch #functor
GRIPE | 2025-12-12 | [MED] | FluxAgent.invoke() semantics change based on _state (DORMANT vs FLOWING)—violates functor laws | #flux #testing
IDEA | 2025-12-12 | [MED] | Add void.slop.* path for noise-as-resource operations (generate/absorb/transmute) | #agentese #void
WIN | 2025-12-12 | [MED] | Natural language adapter exists but unused—wire to CLI for "kgents sip from the void" | #agentese #devex
IDEA | 2025-12-12 | [MED] | 12 implicit functors in spec—formalize in spec/c-gents/functors.md with laws | #spec #functor
GRIPE | 2025-12-12 | [MED] | K-gent access control specified (lines 193-208) but not implemented—security gap | #k-gent #spec
IDEA | 2025-12-12 | [MED] | T-gent Type IV JudgeAgent needs formalized evaluation criteria algebra | #t-gent #spec
WIN | 2025-12-12 | [MED] | Soul context is sticky—parameterize Persona type for Soul[A, P] generics | #k-gent #arch
IDEA | 2025-12-12 | [MED] | pytest fixture `isolated_registry` would fix functor test isolation anti-pattern | #testing #devex
IDEA | 2025-12-12 | [LOW] | parallel()/fan_out()/branch() should be proper functors, not special-case agents | #c-gent #arch
WIN | 2025-12-12 | [LOW] | Cross-functor law tests (Soul >> Flux != Flux >> Soul)—composition matrix | #testing #functor
IDEA | 2025-12-14 | [MED] | FluxStream.pipe() returns FluxStream[Any]—preserve generics through operator chain | #k-gent #flux #types
IDEA | 2025-12-14 | [MED] | Pipe streaming lacks backpressure—add async queue limits + consumer signaling | #k-gent #flux #perf
IDEA | 2025-12-14 | [HIGH] | WebSocket + NDJSON merge—C18 endpoint emits NDJSON instead of raw text | #k-gent #streaming
IDEA | 2025-12-14 | [MED] | FluxStream.merge() multi-source streaming—fan-in from multiple flux sources | #flux #arch
```

---

## Claimed

```
(none yet)
```

---

## Resolved

```
(none yet)
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
