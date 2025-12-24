# Saved Compositions

Pre-configured `kg compose` workflows for common tasks.

## Available Compositions

### `pre-commit`
**Purpose**: Validate system health before committing
**When**: Before every commit
**Usage**:
```bash
kg compose --run "pre-commit"
```

**Steps**:
1. Health check all Crown Jewels
2. Audit all specs (continues on failure)

**Exit Code**: 1 if health check fails

---

### `validate-spec`
**Purpose**: Comprehensive spec review before modification
**When**: Before editing any spec file
**Usage**:
```bash
kg compose --run "validate-spec" spec/protocols/witness.md
```

**Steps**:
1. Full audit (principles + drift + coverage)
2. Show all annotations

**Exit Code**: 0 (non-blocking, informational)

---

### `full-check`
**Purpose**: System-wide validation
**When**: After major refactoring, before PRs
**Usage**:
```bash
kg compose --run "full-check"
```

**Steps**:
1. Audit all Crown Jewel specs
2. Health check all Crown Jewels
3. Identity law verification for services

**Exit Code**: 1 if health check fails

---

### `post-impl`
**Purpose**: Link implementation to spec and validate
**When**: After implementing a spec section
**Usage**:
```bash
kg compose --run "post-impl" \
  spec/protocols/witness.md \
  "MarkStore" \
  services/witness/store.py:MarkStore \
  witness
```

**Steps**:
1. Annotate spec with implementation link
2. Health check the relevant Crown Jewel
3. Audit for remaining drift

**Exit Code**: 1 if health check fails

---

## Creating Custom Compositions

### Ad-Hoc
```bash
kg compose "cmd1" "cmd2" "cmd3"
```

### Save for Reuse
```bash
kg compose --save "my-workflow" "cmd1" "cmd2"
```

### With Parameters
Create a `.composition` file in this directory following the format above.

---

## Composition Philosophy

> *"A single kg command is atomic. A composition is molecular."*

- Every composition creates a **unified witness trace**
- Steps can continue on failure (`continue_on_failure: true`)
- Exit codes follow Unix conventions (0 = success, 1 = failure)
- Traces provide causal narrative from stimulus to outcome

View traces:
```bash
kg compose --history
kg witness show --trace <trace_id>
```

---

*For full documentation, see: `docs/skills/cli-strategy-tools.md`*
