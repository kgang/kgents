Compare implementation against specification. Find spec/impl drift.

## Target: $ARGUMENTS

If no arguments provided, scan all spec/ vs impl/ for drift.

## Protocol

### Phase 1: Identify Spec-Impl Pairs

Map specification files to their implementations:

| Spec | Impl |
|------|------|
| `spec/agents/flux.md` | `impl/claude/agents/flux/` |
| `spec/protocols/agentese.md` | `impl/claude/protocols/agentese/` |
| ... | ... |

### Phase 2: Extract Claims

From the spec, extract testable claims:

```
CLAIM: FluxAgent.start() returns AsyncIterator[B]
SOURCE: spec/agents/flux.md line 45
```

### Phase 3: Verify Claims

Check each claim against implementation:

- **Implemented**: Claim is satisfied
- **Partial**: Claim is partially implemented
- **Missing**: Claim is not implemented
- **Divergent**: Implementation contradicts spec

### Phase 4: Report

```
[DIFF-SPEC] Target: <target>

Spec: <spec_file>
Impl: <impl_dir>

Claims Verified: <N>/<total>

Status:
- [x] <Claim 1>: Implemented
- [~] <Claim 2>: Partial — <what's missing>
- [ ] <Claim 3>: Missing — <not implemented>
- [!] <Claim 4>: Divergent — <how it differs>

Recommendations:
1. <action to align spec/impl>
2. <action to update spec if impl is correct>
```

## Drift Categories

| Category | Action |
|----------|--------|
| **Spec ahead** | Implement missing features |
| **Impl ahead** | Update spec to reflect reality |
| **Divergent** | Decide which is authoritative, align |
| **Ambiguous** | Clarify spec language |

## Arguments

- `<path>` — Check specific spec or impl
- `--all` — Full spec/impl audit
- `--summary` — Just counts, no details
- `--fix` — Suggest fixes (don't auto-apply)

## Examples

```
/diff-spec spec/agents/flux.md
/diff-spec agents/flux
/diff-spec --all --summary
```
