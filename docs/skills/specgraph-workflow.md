# SpecGraph Workflow Skill

> *"The system that can describe itself can regenerate itself."*

## Purpose

This skill teaches how to use SpecGraph for spec-driven development with the Discovery Mode (Option C) workflow.

---

## The Philosophy: Tool, Not Tyrant

> *"SpecGraph serves creativity; creativity does not serve SpecGraph."*

SpecGraph is an **alignment tool**, not an **enforcement system**. It helps you see gaps and track progress. It does **not** dictate how you work.

### The Three Modes

| Mode | Behavior | When to Use |
|------|----------|-------------|
| **Advisory** (default) | Report gaps, never block | Exploration, creative sessions |
| **Gatekeeping** (opt-in) | Block CI on critical gaps | Pre-release, stabilization |
| **Aspirational** | Track gaps as roadmap TODOs | Planning, tech debt |

See `vertical-slice-pattern.md` for detailed mode documentation.

### The Bidirectional Contract

```
Compile ⊣ Reflect

Spec ←──Reflect──← Impl
  │                  ↑
  └───Compile───────→┘
```

Neither direction is privileged:
- **Spec → Impl**: When you know what you want
- **Impl → Spec**: When you're discovering what exists

---

## The Coherence Goal

A healthy system satisfies **coherence**, not rigid conformance:

```python
coherence_report = audit(spec/, impl/)
# Returns:
#   - aligned: components that match
#   - gaps_in_impl: spec defines, impl lacks
#   - gaps_in_spec: impl exists, spec doesn't document (also valuable!)
```

The goal is not "no gaps" but "understood gaps". Some gaps are intentional (in-progress work). Some gaps reveal undocumented impl that should become spec.

---

## Quick Reference: The `kg spec.*` Commands

> *"The fastest path to spec-impl alignment."*

The `self.system.spec.*` AGENTESE paths provide convenient DevEx commands:

| Command | Purpose |
|---------|---------|
| `kg self.system.spec.manifest` | View available spec commands |
| `kg self.system.spec.audit` | Run full spec-impl audit |
| `kg self.system.spec.reflect holon=<name>` | Reflect a holon to extract spec |
| `kg self.system.spec.gaps [severity=<level>]` | Show only gaps in actionable format |
| `kg self.system.spec.health` | Crown Jewel health dashboard |

### Usage Examples

```bash
# Check Crown Jewel health (most common)
kg self.system.spec.health

# Run full audit with alignment score
kg self.system.spec.audit

# Reflect a specific holon to extract YAML
kg self.system.spec.reflect holon=town

# Show only critical gaps
kg self.system.spec.gaps severity=critical
```

### Programmatic API

```python
from protocols.agentese.specgraph import (
    # Discovery (Option C)
    discover_from_spec,
    audit_impl,
    full_audit,
    generate_stubs,
    print_audit_report,
    # Reflect
    reflect_jewel,
    reflect_crown_jewels,
    # Core types
    GapSeverity,
    ComponentType,
    # Spec types (for building specs programmatically)
    SpecNode,
    PolynomialSpec,
    OperadSpec,
    OperationSpec,
    LawSpec,
    AgentesePath,
    AspectSpec,
    AspectCategory,
    ServiceSpec,
)
from pathlib import Path

# One-liner audit
discovery, audit = full_audit(Path("spec/"), Path("impl/claude/"))
print(print_audit_report(audit))

# Verbose audit with file paths
print(print_audit_report(audit, verbose=True))

# Crown Jewel health check
results = reflect_crown_jewels(Path("impl/claude/"))
for holon, result in results.items():
    print(f"{holon}: {result.confidence:.0%}")
```

---

## Workflow Steps

### Step 1: Discover What Spec Defines

```python
from protocols.agentese.specgraph import discover_from_spec
from pathlib import Path

discovery = discover_from_spec(Path("spec/"))

print(f"Total specs: {discovery.total_specs}")
print(f"With polynomial: {discovery.specs_with_polynomial}")
print(f"With operad: {discovery.specs_with_operad}")
print(f"With AGENTESE node: {discovery.specs_with_node}")
```

### Step 2: Audit Impl Against Spec

```python
from protocols.agentese.specgraph import audit_impl

audit = audit_impl(Path("impl/claude/"), discovery)

print(f"Alignment score: {audit.alignment_score:.1%}")
print(f"Critical gaps: {len(audit.critical_gaps)}")
print(f"Aligned components: {len(audit.aligned)}")
```

### Step 3: Review Gaps

```python
from protocols.agentese.specgraph import print_audit_report

print(print_audit_report(audit))
```

Output:
```
============================================================
SPECGRAPH AUDIT REPORT
============================================================

Total components specified: 15
Aligned: 12 (80.0%)
Missing: 3
Critical gaps: 2

------------------------------------------------------------
GAPS:
------------------------------------------------------------
🔴 [CRITICAL] world.coalition
   Component: polynomial
   polynomial.py missing (spec defines 4 positions)

🔴 [CRITICAL] world.coalition
   Component: operad
   operad.py missing (spec defines 6 operations, 3 laws)

🟡 [IMPORTANT] world.coalition
   Component: node
   node.py missing (spec defines path world.coalition with 3 aspects)
```

### Step 4: Generate Stubs for Gaps

```python
from protocols.agentese.specgraph import generate_stubs

# Preview (dry_run=True)
result = generate_stubs(audit.gaps, Path("impl/claude/"), dry_run=True)
print(f"Would generate: {result.files_generated}")

# Actually generate (dry_run=False)
result = generate_stubs(audit.gaps, Path("impl/claude/"), dry_run=False)
print(f"Generated: {result.files_generated}")
```

### Step 5: Choose Your Mode

```bash
# Advisory (default): See gaps, don't block
uv run python -c "
from protocols.agentese.specgraph import full_audit, print_audit_report
from pathlib import Path
_, audit = full_audit(Path('spec/'), Path('impl/claude/'))
print(print_audit_report(audit))
"

# Gatekeeping (opt-in): Block on critical gaps
uv run pytest protocols/agentese/specgraph/_tests/test_ci_gate.py -v
```

---

## YAML Frontmatter Format (Extended)

```yaml
---
domain: world           # world, self, concept, void, time
holon: coalition        # Unique identifier

polynomial:
  positions: [idle, forming, negotiating, active, dissolved]
  transition: coalition_transition
  directions: coalition_directions

operad:
  operations:
    propose:
      arity: 2
      signature: "Citizen × Citizen → CoalitionDraft"
    vote:
      arity: 1
      signature: "Citizen → Vote"
    merge:
      arity: -1
      variadic: true  # NEW: explicit variadic flag
      signature: "Coalition* → Coalition"
  laws:
    quorum: "vote_count(c) >= threshold(c) implies active(c)"
  extends: AGENT_OPERAD

agentese:
  path: world.coalition
  aspects:
    - manifest        # Simple format (backward compatible)
    - name: propose   # NEW: Rich format with category
      category: generation
      effects: [state_mutation]
    - name: vote
      category: mutation
      effects: [state_mutation, event_emit]

service:              # NEW: Layer 4 metadata
  crown_jewel: true
  adapters: [crystals, streaming]
  frontend: true
  persistence: d-gent

dependencies: [world.town, self.memory]
---
```

---

## Gap Severities

| Severity | What's Missing | CI Gate |
|----------|---------------|---------|
| `CRITICAL` | polynomial or operad | **FAILS** |
| `IMPORTANT` | AGENTESE node | **FAILS** |
| `MINOR` | sheaf | Warns only |

---

## Common Patterns

### Pattern 1: Add New Agent

```bash
# 1. Write spec with YAML frontmatter
vim spec/world/new-agent.md

# 2. Run audit to see gaps
python -c "
from protocols.agentese.specgraph import full_audit, print_audit_report
from pathlib import Path
_, audit = full_audit(Path('spec/'), Path('impl/claude/'))
print(print_audit_report(audit))
"

# 3. Generate stubs
python -c "
from protocols.agentese.specgraph import full_audit, generate_stubs
from pathlib import Path
_, audit = full_audit(Path('spec/'), Path('impl/claude/'))
result = generate_stubs(audit.gaps, Path('impl/claude/'), dry_run=False)
print(f'Generated: {result.files_generated}')
"

# 4. Fill in TODOs in generated files
vim impl/claude/agents/new-agent/polynomial.py
```

### Pattern 2: Verify Before Commit (Gatekeeping Mode Only)

Only use this if you've explicitly chosen Gatekeeping mode:

```bash
# Pre-commit hook content (only for Gatekeeping projects)
uv run pytest protocols/agentese/specgraph/_tests/test_ci_gate.py::TestCIGate::test_no_critical_gaps -v

# Alternative: Advisory check that shows but doesn't block
uv run python -c "
from protocols.agentese.specgraph import full_audit, print_audit_report
from pathlib import Path
_, audit = full_audit(Path('spec/'), Path('impl/claude/'))
print(print_audit_report(audit))
# Note: This exits 0 even with gaps (Advisory mode)
"
```

### Pattern 3: Impl-First Discovery (Creative Sessions)

When exploring, let impl teach spec:

```python
from protocols.agentese.specgraph import reflect_impl, generate_frontmatter
from pathlib import Path

# 1. Build your exploratory implementation
#    (Do this first! Creativity before specification.)

# 2. Reflect impl to get spec structure
result = reflect_impl(Path("impl/claude/agents/my-exploration/"))

# 3. Generate YAML frontmatter
if result.spec_node:
    yaml = generate_frontmatter(result.spec_node)
    print(yaml)
    # Copy to spec/<domain>/<holon>.md

# 4. Refine the generated spec with your learnings
# 5. Iterate: impl teaches spec, spec documents intent
```

**Why Impl-First?**
- Preserves the Accursed Share (creative entropy)
- Spec emerges from discovery, not the reverse
- Useful when you don't yet know the final shape

### Pattern 4: Extract Spec from Orphan Impl

For existing impl that was never documented:

```python
from protocols.agentese.specgraph import reflect_impl, generate_frontmatter
from pathlib import Path

# Reflect impl to get spec structure
result = reflect_impl(Path("impl/claude/agents/orphan/"))

# Generate YAML frontmatter
if result.spec_node:
    yaml = generate_frontmatter(result.spec_node)
    print(yaml)
    # Copy to spec/<domain>/<holon>.md
```

---

## Integration with self.system

The SpecGraph is exposed via AGENTESE paths:

### Core System Paths (Autopoietic Kernel)

```
self.system.audit     # Run full audit, show gaps
self.system.compile   # Compile spec → impl (with spec_path= arg)
self.system.reflect   # Reflect impl → spec (with holon= arg)
self.system.witness   # Show evolution history
```

### DevEx Paths (`kg spec.*`)

```
self.system.spec.manifest   # View available spec commands
self.system.spec.audit      # Run full spec-impl audit
self.system.spec.reflect    # Reflect a specific holon (with holon= arg)
self.system.spec.gaps       # Show only gaps (with optional severity= filter)
self.system.spec.health     # Crown Jewel health dashboard
```

**Recommended for daily use**: The `self.system.spec.*` paths provide a streamlined interface focused on common DevEx workflows. Use these for quick health checks and gap analysis.

---

## Reference Implementation: Town Crown Jewel

> *"Town is the canonical example. If you understand Town's structure, you understand all Crown Jewels."*

**Town** demonstrates the complete spec ↔ impl roundtrip with 100% alignment:

### Structure

| Component | Spec Location | Impl Location | Status |
|-----------|---------------|---------------|--------|
| Polynomial | `spec/town/town.md` | `agents/town/polynomial.py` | ✅ 5 positions |
| Operad | `spec/town/town.md` | `agents/town/operad.py` | ✅ 8 operations, 3 laws |
| Node | `spec/town/town.md` | `services/town/node.py` | ✅ 11 aspects |

> **Note**: Spec files should be named `<holon>.md` (e.g., `town.md`), not `index.md`. The parser skips `index.md` files. See Troubleshooting section for details.

### Verification Commands

```bash
# Quick health check (recommended)
kg self.system.spec.health

# Reflect Town specifically
kg self.system.spec.reflect holon=town

# Run roundtrip tests
cd impl/claude && uv run pytest protocols/agentese/specgraph/_tests/test_specgraph.py::TestTownRoundtrip -v
```

### The Roundtrip Property

```
Reflect(Parse(spec/town/town.md)) ≅ Reflect(impl)
```

This is verified by `TestTownRoundtrip`:
- `test_town_spec_impl_alignment`: Domain, positions, operations match
- `test_town_polynomial_positions`: 5 positions exactly
- `test_town_operad_operations`: 8 operations exactly
- `test_town_operad_laws`: 3 laws exactly
- `test_town_full_audit_aligned`: Full audit passes

### Key Files

| Purpose | Path |
|---------|------|
| **Canonical Spec** | `spec/town/town.md` |
| **Polynomial** | `impl/claude/agents/town/polynomial.py` |
| **Operad** | `impl/claude/agents/town/operad.py` |
| **AGENTESE Node** | `impl/claude/services/town/node.py` |
| **Roundtrip Tests** | `impl/claude/protocols/agentese/specgraph/_tests/test_specgraph.py`

---

## Troubleshooting

### "No specs with YAML frontmatter"

Add frontmatter to your spec files:

```yaml
---
domain: world
holon: my-agent
polynomial:
  positions: [idle, active]
  transition: my_transition
---

# My Agent Spec

...
```

### "Parser skips my index.md file"

**Important**: The parser skips files named `index.md`. Name your spec files `<holon>.md` instead:

| ❌ Wrong | ✅ Correct |
|----------|------------|
| `spec/town/index.md` | `spec/town/town.md` |
| `spec/atelier/index.md` | `spec/atelier/atelier.md` |

This is intentional — `index.md` files are often navigation/README files, not specs with YAML frontmatter.

### "Alignment score is 0%"

This is normal if no specs have frontmatter yet. The score only counts specs that define components.

Check which specs have frontmatter:
```bash
kg self.system.spec.audit verbose=true
```

### "Crown Jewel shows 0% confidence"

Run a specific reflect to see what's missing:
```bash
kg self.system.spec.reflect holon=<name>
```

Common causes:
1. Missing `polynomial.py` — add Phase Enum and PolyAgent
2. Missing `operad.py` — add operations dict and Law instances
3. Missing `node.py` — add @node decorator

### "Import errors in generated code"

Check that generated imports match your project structure. The compiler assumes:
- `from agents.poly.protocol import PolyAgent`
- `from agents.operad.core import ...`

Adjust `compile.py` if your structure differs.

### Quick diagnostic commands

```bash
# See overall health
kg self.system.spec.health

# See specific gaps
kg self.system.spec.gaps

# See only critical gaps
kg self.system.spec.gaps severity=critical

# Reflect specific holon
kg self.system.spec.reflect holon=town
```

---

## CI Integration (Gatekeeping Mode)

If you've opted into Gatekeeping mode, use these tests in your CI pipeline:

### Pre-Push Hook

Add to `.git/hooks/pre-push`:

```bash
#!/bin/bash
cd impl/claude
uv run pytest protocols/agentese/specgraph/_tests/test_ci_gate.py::TestCIGate::test_no_critical_gaps -v
```

### CI Pipeline

```yaml
# .github/workflows/specgraph.yml (example)
- name: Check Spec-Impl Alignment
  run: |
    cd impl/claude
    uv run pytest protocols/agentese/specgraph/_tests/test_ci_gate.py -v
```

### What the CI Gate Tests

| Test | Behavior |
|------|----------|
| `test_no_critical_gaps` | **FAILS** if polynomial or operad missing |
| `test_warn_on_minor_gaps` | Warns but passes on missing sheaf |
| `test_alignment_score_threshold` | Configurable alignment threshold |

### Skipping CI Gate (Escape Hatch)

```bash
# Set env var to skip
SPECGRAPH_SKIP_CI_GATE=1 git push
```

---

## Anti-Patterns

| Anti-Pattern | Why It's Harmful | Alternative |
|--------------|------------------|-------------|
| **Gatekeeping by default** | Blocks creative exploration | Default to Advisory |
| **"No gaps" as success metric** | Some gaps are intentional | Track "understood gaps" |
| **Spec-only authority** | Ignores emergent impl | Bidirectional Compile ⊣ Reflect |
| **CI gate without consent** | Surprise friction | Explicit opt-in per project |
| **Ignoring gaps_in_spec** | Undocumented impl is a gap too | Reflect orphan impl into spec |

---

## Related

- `vertical-slice-pattern.md` — The three modes (Advisory/Gatekeeping/Aspirational)
- `autopoietic-architecture.md` — Source plan (AD-009)
- `spec/principles.md` — The Accursed Share meta-principle

---

*Reference: plans/autopoietic-architecture.md (AD-009)*
