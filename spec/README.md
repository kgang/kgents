# The kgents Specification

This directory contains the conceptual specification for kgents—implementation-agnostic definitions of what agents should be.

---

## Implementation Validation

The spec/impl relationship is bidirectional:
- **Spec → Impl**: Specifications prescribe behavior
- **Impl → Spec**: Successful patterns inform specification refinement

See `impl/claude/` for the reference implementation. Key validations:
- All 7 bootstrap agents implemented and law-verified
- 14 agent genera with cross-pollination
- 666+ passing tests validating spec compliance

The synthesis is valid: implementation wisdom has been elevated to spec-level principles while preserving the original vision.

---

## Reading Order

1. **[principles.md](principles.md)** - Core design principles (start here)
2. **[anatomy.md](anatomy.md)** - What constitutes an agent
3. **[bootstrap.md](bootstrap.md)** - The irreducible kernel (7 agents)
4. **[agents/composition.md](agents/composition.md)** - The `>>` operator as primary abstraction
5. **[testing.md](testing.md)** - T-gents taxonomy (testing as first-class)
6. **[reliability.md](reliability.md)** - Multi-layer reliability patterns
7. **[archetypes.md](archetypes.md)** - Emergent behavioral patterns
8. **Agent Genera** - Explore specific agent types:
   - [a-gents/](a-gents/) - Abstract + Art
   - [b-gents/](b-gents/) - Bio + Banker (resource-constrained systems)
   - [agents/](agents/) - Categorical Foundations (composition, functors, monads)
   - [d-gents/](d-gents/) - Data Agents (state, memory, persistence)
   - [f-gents/](f-gents/) - Function/Flux (streaming, continuous agents)
   - [h-gents/](h-gents/) - Hegelian/Dialectic (introspection)
   - [i-gents/](i-gents/) - Interface (Living Codex Garden visualization)
   - [j-gents/](j-gents/) - JIT Agent Intelligence (lazy evaluation, JIT compilation)
   - [k-gent/](k-gent/) - Personalization Functor (system's fix)
   - [l-gents/](l-gents/) - Library (knowledge curation, semantic discovery)
   - [m-gents/](m-gents/) - Memory (holographic associative memory, memory as morphism)
   - [n-gents/](n-gents/) - Narrator (story-telling, time-travel debugging)
   - [o-gents/](o-gents/) - Observability (system-wide telemetry, bootstrap witness)
   - [p-gents/](p-gents/) - Parser (multi-strategy parsing, structured output)
   - [r-gents/](r-gents/) - Refinery (prompt optimization, DSPy/TextGrad/OPRO integration)
   - [t-gents/](t-gents/) - Testing (algebraic reliability, Types I-V)
   - [u-gents/](u-gents/) - Utility (tool use, MCP integration)
   - [v-gents/](v-gents/) - Vector (semantic geometry, similarity search, embedding infrastructure)
   - [w-gents/](w-gents/) - Wire (ephemeral process observation, stigmergic coordination)

---

## Cross-Pollination Graph

Agents don't exist in isolation. Key integration points:

| Integration | Description |
|-------------|-------------|
| J+F | F-gent artifacts can be JIT-instantiated via J-gent |
| T+* | T-gents can test any agent via Spy/Mock patterns |
| T+U | T-gents test U-gent tools (MockAgent, SpyAgent, FlakyAgent) |
| U+P | U-gent Tool parsing uses P-gent strategies |
| U+D | U-gent tools use D-gent caching (90% cost reduction) |
| U+L | L-gent indexes U-gent tool registry |
| U+W | W-gent traces U-gent tool execution |
| K+* | K-gent functor lifts any agent into personalized space |
| P+T | T-gent Tool parsing uses P-gent strategies |
| W+I | W-gent observation feeds I-gent visualization |
| M+D | M-gent holographic memory composes with D-gent persistence |
| V+L | L-gent catalog delegates vector operations to V-gent |
| V+M | M-gent uses V-gent for associative recall similarity |
| V+D | V-gent can use D-gent as a persistence backend |
| V+K | K-gent uses V-gent for belief/topic similarity search |
| O+* | O-gents observe all agents including bootstrap |
| N+O | N-gent stories feed O-gent metrics |
| B+B | B-Banker controls B-Bio's resource allocation |
| B+O | O-gent ValueLedgerObserver monitors B-Banker economic health |
| B+W | W-gent renders B-Banker RoC dashboard and Value Tensor |
| R+F | R-gent optimizes F-gent prototypes before crystallization |
| R+T | T-gent provides loss signals for R-gent optimization |
| R+B | B-gent gates R-gent budget (ROI check) |
| R+L | L-gent indexes R-gent optimization metadata |

See `impl/claude/agents/*/` `__init__.py` files for explicit cross-pollination labels.

---

## The Spec/Impl Distinction

```
spec/           ← You are here (what agents should be)
impl/           ← Reference implementations (how agents are built)
```

The specification is **prescriptive**: it defines the contract that any implementation must fulfill. An agent claiming to be a "B-gent" must satisfy the specification in `b-gents/`.

---

## Spec Hygiene

> *"Spec is compression. If you can't compress it, you don't understand it."*

### The Generative Principle

A well-formed spec is **smaller than its implementation** but contains enough information to regenerate it. The spec is the compression; the impl is the decompression.

### Seven Bloat Patterns (Avoid These)

| Pattern | Signal | Fix |
|---------|--------|-----|
| **Implementation Creep** | Functions >10 lines | Extract to `impl/` |
| **Roadmap Drift** | Week-by-week plans | Move to `plans/` |
| **Framework Comparisons** | Decision matrices | Move to `docs/` |
| **Gap Analyses** | Current vs Desired | Delete |
| **Session Artifacts** | Continuation prompts | Move to `plans/_continuations/` |
| **File Listings** | Directory trees | One-line reference |
| **Test Code as Laws** | pytest functions | Algebraic equations |

### Five Compression Patterns (Use These)

1. **Type signatures with `...`** - Show shape, hide body
2. **Laws as equations** - `F.map(g . f) = F.map(g) . F.map(f)`
3. **AGENTESE path chains** - `self.memory.crystallize → concept.association.emerge`
4. **ASCII diagrams** - Worth 100 lines of prose
5. **Summary tables** - Compress enumeration

### Line Limits

| Spec Type | Target | Hard Limit |
|-----------|--------|------------|
| Simple agent | 100-200 | 300 |
| Complex agent | 200-300 | 400 |
| Protocol | 300-400 | 500 |
| Core system | 400-500 | 600 |

**Full guide**: `docs/skills/spec-hygiene.md` | **Template**: `docs/skills/spec-template.md`

## Contributing New Agents

1. Does this agent serve a clear, justified purpose? (Tasteful)
2. Does it fill a gap, or duplicate something existing? (Curated)
3. Does it augment human capability? (Ethical)
4. Would interacting with it bring delight? (Joy-Inducing)
5. Can it compose with other agents? (Composable)

If yes to all, draft the spec and propose it.

## Notation Conventions

- **MUST** / **SHALL**: Absolute requirement
- **SHOULD**: Recommended but not required
- **MAY**: Optional
- `code blocks`: Refer to implementation artifacts
- *italics*: Defined terms (see glossary)
