# CLI Strategy Tools - Native kgents Operations

> *"Claude Code should feel like a native kgents citizen, not a visitor."*

This skill teaches you WHEN and HOW to use the five CLI strategy tools: `audit`, `annotate`, `experiment`, `probe`, and `compose`.

---

## Philosophy

**Evidence over intuition. Traces over reflexes. Composition over repetition.**

Every kgents operation should:
1. **Witness** - Leave a mark for traceability
2. **Validate** - Check against principles and laws
3. **Document** - Capture gotchas and mappings
4. **Compose** - Chain operations, not repeat them

---

## The Five Tools

| Tool | Purpose | When to Use | Output |
|------|---------|-------------|--------|
| `kg audit` | Validate spec against principles/impl | Before modifying specs, during PR review | Scores + drift report + witness mark |
| `kg annotate` | Link principles to impl, capture gotchas | After implementing spec sections, fixing bugs | Annotation + witness mark |
| `kg experiment` | Gather evidence with Bayesian rigor | Uncertain code generation, testing hypotheses | Evidence bundle + witness marks |
| `kg probe` | Fast categorical law checks | Session start, after compositions, in CI | Pass/fail + mark on failure only |
| `kg compose` | Chain operations with unified trace | Pre-commit workflows, saved procedures | Unified trace linking all steps |

---

## 1. `kg audit` - Spec Validation

### When to Use

**MANDATORY**:
- Before modifying any spec file in `spec/`
- Before creating PRs that touch specs
- When asked "does this spec make sense?"
- During design reviews

**RECOMMENDED**:
- At session start for specs you'll work with
- After major refactoring of a Crown Jewel
- When system-wide health check needed (`--system`)

### Automatic Triggers

Claude Code should automatically run `kg audit` when:

1. **Pre-commit hook** - Any commit touching `spec/**/*.md`
   ```bash
   # Before commit, if spec files changed:
   kg audit --system --json
   ```

2. **Pre-PR creation** - When creating PR with spec changes
   ```bash
   # Before gh pr create:
   kg audit spec/protocols/witness.md --full
   ```

3. **Asked about spec health** - User queries like:
   - "Is the Witness spec good?"
   - "Check the Brain spec"
   - "Audit our specs"

### Usage Patterns

```bash
# Quick principle check
kg audit spec/protocols/witness.md --principles

# Detect spec/impl drift
kg audit spec/agents/brain/brain.md --impl

# Full audit (default)
kg audit spec/protocols/witness.md --full

# System-wide health dashboard
kg audit --system
```

### Integration with Workflow

**Before spec modification**:
```bash
# 1. Audit first
kg audit spec/protocols/witness.md --full

# 2. Make changes
# ... edit spec ...

# 3. Audit again
kg audit spec/protocols/witness.md --full

# 4. Compare results
```

**In PR creation** (see Git Safety Protocol in CLAUDE.md):
```bash
# After all changes, before PR:
kg compose --save "pr-validation" \
  "audit --system" \
  "probe health --all"

kg compose --run "pr-validation"
```

---

## 2. `kg annotate` - Capture Knowledge

### When to Use

**MANDATORY**:
- After fixing a non-obvious bug (add `--gotcha`)
- After implementing a spec section (add `--impl` link)
- When making design decisions linked to principles

**RECOMMENDED**:
- After discovering subtle behavior
- When finding aesthetic judgments ("this feels right")
- When linking Kent's decisions to spec sections

### Automatic Triggers

Claude Code should automatically run `kg annotate` when:

1. **After implementing spec section**:
   ```bash
   # Just implemented MarkStore from spec/protocols/witness.md
   kg annotate spec/protocols/witness.md --impl \
     --section "MarkStore" \
     --link "services/witness/store.py:MarkStore"
   ```

2. **After fixing bug with gotcha**:
   ```bash
   # Fixed subtle bus fire-and-forget issue
   kg annotate spec/protocols/witness.md --gotcha \
     --section "Event Emission" \
     --note "Bus publish is fire-and-forget, don't await"
   ```

3. **After taste decision**:
   ```bash
   # Kent said "this feels right" about signal aggregation
   kg annotate spec/agents/brain/brain.md --taste \
     --section "Signal Aggregation" \
     --note "Use Signal not state variables - Kent's preference"
   ```

4. **Linking fusion decisions**:
   ```bash
   # After kg decide creates fusion-abc123
   kg annotate spec/protocols/witness.md --decision fusion-abc123 \
     --section "Storage Strategy" \
     --note "Decided to use Postgres over SQLite"
   ```

### Usage Patterns

```bash
# Add principle link
kg annotate spec/protocols/witness.md --principle composable \
  --section "Mark Structure" \
  --note "Single output per mark (not arrays)"

# Add impl link (bidirectional graph)
kg annotate spec/protocols/witness.md --impl \
  --section "Event Bus Integration" \
  --link "services/witness/bus.py:WitnessEventBridge"

# Add gotcha (save future pain)
kg annotate spec/protocols/agentese.md --gotcha \
  --section "@node decorator" \
  --note "Runs at import time - must import module to register"

# View all annotations
kg annotate spec/protocols/witness.md --show

# Export as structured data
kg annotate spec/protocols/witness.md --export --json
```

### Integration with Workflow

**Standard implementation flow**:
1. Read spec section
2. Implement code
3. Annotate spec with `--impl` link
4. Write tests
5. If gotcha discovered, annotate with `--gotcha`

**Bug fix flow**:
1. Reproduce bug
2. Find root cause
3. Fix bug
4. **Annotate spec with `--gotcha`** (prevent recurrence)
5. Add regression test

---

## 3. `kg experiment` - Evidence Gathering

### When to Use

**MANDATORY**:
- When uncertain about code generation approach
- When testing new VoidHarness strategies
- When validating categorical law adherence

**RECOMMENDED**:
- Before committing to architecture decision
- When exploring multiple implementation paths
- When validating robustness of parsing/generation

### Automatic Triggers

Claude Code should automatically run `kg experiment` when:

1. **User expresses uncertainty**:
   - "I'm not sure if..."
   - "Should we try..."
   - "What if we..."

2. **Before risky code generation**:
   ```bash
   # Uncertain about best generation strategy
   kg experiment generate \
     --spec "def complex_parser(ast: AST) -> Result" \
     --adaptive --confidence 0.95
   ```

3. **Testing new harness/strategy**:
   ```bash
   # Validating new VoidHarness repair strategy
   kg experiment generate \
     --spec "..." --strategy lazy_validation --n 100
   ```

4. **Law verification**:
   ```bash
   # After creating new tool composition
   kg experiment laws \
     --target "services/tooling/new_tool.py:NewTool" \
     --laws identity,associativity
   ```

### Usage Patterns

```bash
# Fixed-N experiment
kg experiment generate --spec "def add(a, b): return a + b" --n 10

# Adaptive Bayesian stopping
kg experiment generate \
  --spec "def parse_agentese(path: str) -> Node" \
  --adaptive --confidence 0.95

# View experiment history
kg experiment history --today

# Resume interrupted experiment
kg experiment resume exp-abc123
```

### Integration with Workflow

**Hypothesis-driven development**:
1. Form hypothesis ("lazy validation will improve robustness")
2. Design experiment
3. Run `kg experiment` with adaptive stopping
4. Review evidence bundle
5. Make decision based on evidence tier
6. Record decision with `kg decide`

**VoidHarness integration**:
```bash
# Generate N candidates, measure success rate
kg experiment generate \
  --spec "$(cat spec/snippet.py)" \
  --harness void \
  --adaptive

# If success rate >= 95%, use strategy
# If < 95%, try different approach
```

---

## 4. `kg probe` - Fast Checks

### When to Use

**MANDATORY**:
- At session start (health check)
- After creating tool compositions
- In CI pipelines (exit code 0/1)

**RECOMMENDED**:
- Before committing composition code
- When debugging Crown Jewel issues
- After refactoring categorical infrastructure

### Automatic Triggers

Claude Code should automatically run `kg probe` when:

1. **Session start**:
   ```bash
   # First command in new session
   kg probe health --all
   ```

2. **After creating composition**:
   ```bash
   # Just wrote: tool_a >> tool_b >> tool_c
   kg probe associativity --pipeline "tool_a >> tool_b >> tool_c"
   ```

3. **After implementing Tool**:
   ```bash
   # Implemented services/tooling/read.py:ReadTool
   kg probe identity --target "services/tooling/read.py:ReadTool"
   ```

4. **Pre-commit (in composition)**:
   ```bash
   kg probe health --all
   # Exit code 1 = block commit
   ```

### Usage Patterns

```bash
# Quick health check all Crown Jewels
kg probe health --all

# Health check specific jewel
kg probe health --jewel brain

# Identity law check
kg probe identity --target "services/witness/node.py:WitnessNode"

# Associativity check
kg probe associativity --pipeline "read >> grep >> summarize"

# JSON output for CI
kg probe health --all --json
```

### Integration with Workflow

**Session start protocol**:
```bash
# 1. Health check
kg probe health --all

# 2. If failures, investigate
kg probe health --jewel brain --verbose

# 3. Fix issues before proceeding
```

**CI integration**:
```yaml
# .github/workflows/validate.yml
- name: Probe categorical laws
  run: |
    kg probe health --all --json
    kg probe identity --target services/tooling/
```

---

## 5. `kg compose` - Pipeline Witnessing

### When to Use

**MANDATORY**:
- For repeated multi-step workflows (save with `--save`)
- Pre-commit validation chains
- PR creation workflows

**RECOMMENDED**:
- Any time you run 3+ kg commands in sequence
- When documenting procedures
- For onboarding new contributors

### Automatic Triggers

Claude Code should automatically run `kg compose` when:

1. **Pre-commit hook**:
   ```bash
   # Saved composition "pre-commit"
   kg compose --run "pre-commit"
   # Includes: audit + probe + tests
   ```

2. **PR creation**:
   ```bash
   # Saved composition "pr-validation"
   kg compose --run "pr-validation"
   # Includes: audit --system + probe health --all
   ```

3. **User repeats pattern**:
   - If user runs same 3+ commands in sequence
   - Claude suggests: "Should I save this as a composition?"

### Usage Patterns

```bash
# Ad-hoc composition
kg compose \
  "audit spec/witness.md --full" \
  "probe health --jewel witness"

# Save for reuse
kg compose --save "validate-witness" \
  "audit spec/protocols/witness.md --full" \
  "probe identity --target services/witness" \
  "probe health --jewel witness"

# Run saved composition
kg compose --run "validate-witness"

# Continue on failure (audit all specs even if some fail)
kg compose --continue \
  "audit spec/a.md" \
  "audit spec/b.md" \
  "audit spec/c.md"

# View history
kg compose --history
kg compose --list
```

### Pre-Saved Compositions

These compositions should be pre-configured:

#### `pre-commit`
```bash
kg compose --save "pre-commit" \
  "probe health --all" \
  "audit --system --json"
```

**When**: Before any commit

#### `validate-spec`
```bash
kg compose --save "validate-spec" \
  "audit \$1 --full" \
  "annotate \$1 --show"
```

**When**: Before modifying spec, during review

#### `full-check`
```bash
kg compose --save "full-check" \
  "audit --system" \
  "probe health --all" \
  "probe identity --target services/"
```

**When**: After major refactoring, before PR

#### `post-impl`
```bash
kg compose --save "post-impl" \
  "annotate \$1 --impl --section '\$2' --link '\$3'" \
  "probe health --jewel \$4"
```

**When**: After implementing spec section

### Integration with Workflow

**Standard commit flow**:
```bash
# 1. Make changes
git add .

# 2. Run pre-commit composition
kg compose --run "pre-commit"

# 3. If passes, commit
git commit -m "..."
```

**PR creation flow**:
```bash
# 1. Ensure all tests pass
cd impl/claude && uv run pytest -q && uv run mypy .
cd impl/claude/web && npm run typecheck && npm run lint

# 2. Run full validation
kg compose --run "full-check"

# 3. Create PR
gh pr create --title "..." --body "..."
```

---

## Integration with CLAUDE.md

These commands should be added to the "Working Protocol" section:

```markdown
## Working Protocol

1. **ANTI-SAUSAGE FIRST** — Ground in voice anchors before suggesting work
2. **HEALTH CHECK** — Run `kg probe health --all` at session start
3. **READ SKILLS** — `docs/skills/` has the answer
4. **CHECK SYSTEMS** — `docs/systems-reference.md` before building new
5. **AUDIT SPECS** — Run `kg audit <spec> --full` before modifying
6. **ANNOTATE DISCOVERIES** — Capture gotchas with `kg annotate --gotcha`
7. **EXPERIMENT WHEN UNCERTAIN** — Use `kg experiment` not guesses
8. **TYPECHECK FRONTEND** — Run `npm run typecheck` after any `.tsx` changes
9. **PRE-COMMIT COMPOSITION** — Run `kg compose --run "pre-commit"`
10. **UPDATE NOW.md** — At session end, update the living document
11. **USE AGENTESE** — The protocol IS the API
```

---

## Decision Trees

### Should I audit?

```
Are you about to modify a spec?
├─ YES → kg audit <spec> --full
└─ NO
    └─ Did spec files change in commit?
        ├─ YES → kg audit --system
        └─ NO → skip
```

### Should I annotate?

```
Did you just implement a spec section?
├─ YES → kg annotate --impl
└─ NO
    └─ Did you fix a non-obvious bug?
        ├─ YES → kg annotate --gotcha
        └─ NO
            └─ Did you make a taste decision?
                ├─ YES → kg annotate --taste
                └─ NO → skip
```

### Should I experiment?

```
Are you uncertain about approach?
├─ YES
│   └─ Is this code generation?
│       ├─ YES → kg experiment generate --adaptive
│       └─ NO → kg experiment laws
└─ NO → skip
```

### Should I probe?

```
Is this session start?
├─ YES → kg probe health --all
└─ NO
    └─ Did you create a composition?
        ├─ YES → kg probe associativity
        └─ NO
            └─ Are you about to commit?
                ├─ YES → kg probe health --all
                └─ NO → skip
```

### Should I compose?

```
Are you running 3+ commands in sequence?
├─ YES
│   └─ Is this a one-time workflow?
│       ├─ YES → kg compose (ad-hoc)
│       └─ NO → kg compose --save
└─ NO
    └─ Is this pre-commit or pre-PR?
        ├─ YES → kg compose --run "pre-commit"
        └─ NO → skip
```

---

## Common Patterns

### Pattern: Spec-First Development

```bash
# 1. Design phase
# Edit spec/agents/new/new.md

# 2. Audit spec
kg audit spec/agents/new/new.md --full

# 3. Implement
# Edit services/new/core.py

# 4. Link impl to spec
kg annotate spec/agents/new/new.md --impl \
  --section "Core Logic" \
  --link "services/new/core.py"

# 5. Test implementation
kg probe identity --target services/new/core.py

# 6. Validate composition
kg compose \
  "audit spec/agents/new/new.md --full" \
  "probe health --jewel new"
```

### Pattern: Bug Fix with Documentation

```bash
# 1. Reproduce bug
# 2. Identify root cause
# 3. Fix bug

# 4. Document gotcha
kg annotate spec/relevant.md --gotcha \
  --section "Problematic Section" \
  --note "Don't do X, it causes Y"

# 5. Write regression test
# 6. Commit with witness
git add . && git commit -m "fix: ..."
km "Fixed bug X" --reasoning "Root cause was Y, added gotcha annotation"
```

### Pattern: Experiment-Driven Development

```bash
# 1. Form hypothesis
# "Lazy validation will improve VoidHarness success rate"

# 2. Run baseline experiment
kg experiment generate \
  --spec "$(cat spec/snippet.py)" \
  --strategy default \
  --n 100

# 3. Run treatment experiment
kg experiment generate \
  --spec "$(cat spec/snippet.py)" \
  --strategy lazy_validation \
  --n 100

# 4. Compare evidence
kg experiment history --today

# 5. Record decision
kg decide --fast "Use lazy_validation" \
  --reasoning "95% success vs 70% baseline"
```

### Pattern: Pre-Commit Workflow

```bash
# Save once
kg compose --save "pre-commit" \
  "probe health --all" \
  "audit --system --json"

# Use forever
git add .
kg compose --run "pre-commit"
git commit -m "..."
```

---

## Philosophy

**The proof IS the decision.**

Every command in this skill enforces the kgents philosophy:
- `audit` - Tasteful, Curated, Composable
- `annotate` - Generative (spec is compression)
- `experiment` - Evidence tier hierarchy
- `probe` - Categorical rigor
- `compose` - Heterarchical workflows

**Depth over breadth. Traces over reflexes. Joy-inducing rigor.**

---

*Lines: 524*
