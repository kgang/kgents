Hydrate context from HYDRATE.md. Apply spec/principles.md rigorously.

## Agent Protocol

1. **Read first**: `plans/_focus.md` (human intent—NEVER overwrite)
2. **Read second**: `plans/_forest.md` (canopy view—auto-generated)
3. **Read third**: `plans/meta.md` (learnings—append only, 50-line cap)
4. **Read fourth**: `HYDRATE.md` (project state—keep terse)

## Boundaries (from spec/principles.md)

| File | Agent May | Agent Must NOT |
|------|-----------|----------------|
| `_focus.md` | Read for direction | Overwrite (Kent's voice) |
| `_forest.md` | Regenerate from plan headers | Add prose |
| `meta.md` | Append atomic learnings | Add paragraphs (one line per insight) |
| `HYDRATE.md` | Update stale facts | Bloat (compress, don't expand) |
| `_epilogues/` | Write new epilogues | Modify existing |

## The Molasses Test (spec/principles.md §9)

Before adding to ANY meta file:
1. Is this one atomic insight or a compound? → If compound, distill first
2. Will future-me understand without context? → If no, rewrite
3. Can this be deleted in 30 days if unused? → If no, it's not meta—it's spec

## If HYDRATE.md is stale

Update facts (test counts, phase status). Do NOT add new sections. Compress, don't expand.

## Phase Detection

Based on session activity, suggest current phase:

| Activity Pattern | Suggested Phase |
|------------------|-----------------|
| Many file reads, no writes | **UNDERSTAND** |
| Code changes, tests running | **ACT** |
| Tests pass, writing notes/epilogue | **REFLECT** |

Include suggested phase in hydration output when pattern is clear.

## Arguments

If user provides arguments, treat them as focus guidance for the session.
