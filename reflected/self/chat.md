# Chat Agent (Reflected)

> *Automatically extracted from `impl/claude/agents/f/`*

**Confidence**: 33%
**Domain**: world
**AGENTESE Path**: world.f

---

## Extracted Structure

| Component | Status | Details |
|-----------|--------|---------|
| Polynomial | ❌ | 0 positions |
| Operad | ✅ | 14 operations, 7 laws |
| AGENTESE Node | ❌ | none |

---

## YAML Frontmatter (SpecGraph Format)

```yaml
---
domain: world
holon: f
operad:
  operations:
    start:
      arity: 1
      signature: Agent[A,B] -> Flow[A] -> Flow[B]
    stop:
      arity: 0
      signature: Flow[_] -> ()
    perturb:
      arity: 1
      signature: (Flow[A], A) -> B
    turn:
      arity: 1
      signature: Message -> Response
    summarize:
      arity: 1
      signature: Context -> CompressedContext
    inject_context:
      arity: 1
      signature: Context -> Flow[_]
    research_branch:
      arity: 1
      signature: Hypothesis -> [Hypothesis]
    merge:
      arity: 2
      signature: (Hypothesis, Hypothesis) -> Synthesis
    prune:
      arity: 1
      signature: '[Hypothesis] -> [Hypothesis]'
    evaluate:
      arity: 1
      signature: Hypothesis -> Score
    post:
      arity: 1
      signature: Contribution -> Blackboard
    read:
      arity: 1
      signature: Query -> [Contribution]
    vote:
      arity: 2
      signature: (Proposal, Agents) -> Decision
    moderate:
      arity: 1
      signature: '[Contribution] -> Resolution'
  laws:
    start_identity: start(Id) = Id_Flow
    start_composition: start(f >> g) = start(f) >> start(g)
    perturbation_integrity: perturb(flowing, x) = inject_priority(x)
    branch_merge: merge(branch(h)) >= essence(h)
    prune_idempotent: prune(prune(hs)) = prune(hs)
    post_read: read(all, post(c, board)) = [c] ++ read(all, board)
    consensus_threshold: vote(p, agents) = decide if votes >= threshold
  extends: AGENT_OPERAD
---
```

---

## Component Details

### Operad: F_OPERAD

**Operations**:
| Name | Arity | Signature |
|------|-------|-----------|
| `start` | 1 | Agent[A,B] -> Flow[A] -> Flow[B] |
| `stop` | 0 | Flow[_] -> () |
| `perturb` | 1 | (Flow[A], A) -> B |
| `turn` | 1 | Message -> Response |
| `summarize` | 1 | Context -> CompressedContext |
| `inject_context` | 1 | Context -> Flow[_] |
| `research_branch` | 1 | Hypothesis -> [Hypothesis] |
| `merge` | 2 | (Hypothesis, Hypothesis) -> Synthesis |
| `prune` | 1 | [Hypothesis] -> [Hypothesis] |
| `evaluate` | 1 | Hypothesis -> Score |
| `post` | 1 | Contribution -> Blackboard |
| `read` | 1 | Query -> [Contribution] |
| `vote` | 2 | (Proposal, Agents) -> Decision |
| `moderate` | 1 | [Contribution] -> Resolution |

**Laws**:
- **start_identity**: `start(Id) = Id_Flow`
- **start_composition**: `start(f >> g) = start(f) >> start(g)`
- **perturbation_integrity**: `perturb(flowing, x) = inject_priority(x)`
- **branch_merge**: `merge(branch(h)) >= essence(h)`
- **prune_idempotent**: `prune(prune(hs)) = prune(hs)`
- **post_read**: `read(all, post(c, board)) = [c] ++ read(all, board)`
- **consensus_threshold**: `vote(p, agents) = decide if votes >= threshold`

**Extends**: `AGENT_OPERAD`

---

## Source Files

- `impl/claude/agents/f/polynomial.py`
- `impl/claude/agents/f/operad.py`
- `impl/claude/agents/f/node.py` (or `services/chat/node.py`)

---

*Reflected by SpecGraph | 33% confidence*
