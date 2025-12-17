# Skill: Writing Spec Files

> *"Spec is compression. If you can't compress it, you don't understand it."* — principles.md

## The Generative Principle

A well-formed spec is **smaller than its implementation** but contains enough information to regenerate it. The spec is the compression; the impl is the decompression.

## Spec Structure (200-400 lines max)

### Required Sections

```markdown
# {Agent/Protocol Name}

**Status:** {Proposal|Draft|Standard|Canonical}
**Implementation:** `impl/claude/{path}/` ({N} tests)

## Purpose
{1 paragraph - why this exists}

## Core Insight
{1 sentence - the key idea that makes this work}

## Type Signatures
{Protocol definitions, dataclass signatures - NO method bodies}

## Laws/Invariants
{Algebraic laws that must hold - NOT test code}

## Integration
{AGENTESE paths, composition with other agents}

## Anti-Patterns
{3-5 bullets - what NOT to do}

## Implementation Reference
See: `impl/claude/{path}/`
```

### Optional Sections

- **Theoretical Foundation**: Category theory, type theory references
- **Biological Parallels**: If applicable (B-gents especially)
- **Design Decisions**: Brief rationale for key choices

## Forbidden in Specs

| Don't Include | Why | Where It Goes |
|---------------|-----|---------------|
| Full function implementations | Not compression | `impl/` |
| SQL queries | Implementation detail | `impl/` |
| Implementation roadmaps | Temporal, not conceptual | `plans/` |
| Week-by-week schedules | Not specification | `plans/` |
| >10 line code examples | Show USAGE not IMPL | Keep brief |
| Framework comparisons | Not spec content | `docs/` |
| Test code | Tests belong with impl | `impl/` |

## Code Example Rules

### Good: Type Signatures

```python
@dataclass
class Tool(Generic[A, B]):
    """A morphism in the tool category."""
    meta: ToolMeta
    # Methods defined in impl
```

### Good: Usage (Not Implementation)

```python
# Composition (what), not implementation (how)
pipeline = parse_query >> search_tool >> format_results
```

### Bad: Full Implementation

```python
# DON'T put this in specs
async def execute(self, input: A) -> Result[B, ToolError]:
    if not self._validate_schema(input):
        return err(ToolError(...))
    try:
        raw = await self._invoke(input)
        return ok(self._parse_output(raw))
    except Exception as e:
        return err(ToolError(...))
```

## Distillation Checklist

When distilling an existing spec:

1. [ ] Identify all code blocks >10 lines
2. [ ] For each: Is this USAGE or IMPLEMENTATION?
3. [ ] Extract implementations to `impl/`
4. [ ] Replace with type signatures or brief usage
5. [ ] Move roadmaps to `plans/`
6. [ ] Move comparisons to `docs/`
7. [ ] Verify spec < impl (compression achieved)
8. [ ] Verify spec is generative (can regenerate impl)

## Line Count Guidelines

| Spec Type | Target Lines | Hard Limit |
|-----------|--------------|------------|
| Simple agent | 100-200 | 300 |
| Complex agent | 200-300 | 400 |
| Protocol | 300-400 | 500 |
| Core system | 400-500 | 600 |

If a spec exceeds these limits, it likely contains implementation.

## The Compression Test

Ask yourself:

1. **Can I regenerate the impl from this spec?** If yes, it's generative.
2. **Is the spec smaller than the impl?** If yes, compression achieved.
3. **Does the spec contain WHAT not HOW?** If yes, it's a spec.

## Cross-References

- `spec/principles.md` §7 (Generative Principle)
- `docs/impl-guide.md` (Where impl goes)
- `docs/skills/plan-file.md` (Where roadmaps go)

---

*"The master's touch was always just compressed experience. Now we can share the compression."*
