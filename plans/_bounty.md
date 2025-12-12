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
