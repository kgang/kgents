# Living Docs Backfill Strategy

> *"Docs are not description—they are projection."*
> *— Living Docs Spec*

**Last Updated**: 2025-12-21
**Conformance**: `spec/protocols/living-docs.md`
**Sessions Estimated**: 4-5 sessions

---

## Current State (Audited 2025-12-21)

### Coverage Summary

```
Teaching: Coverage by Service (Updated 2025-12-21)
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
services/living_docs/     ████████████████████████████████  100% (10/10)
services/ashc/            ████████████████████████████████  100% (3/3)
services/interactive_text ██████████████████████████░░░░░░   80% (5/6 core)
services/brain/           ████████████████░░░░░░░░░░░░░░░░   50% (2/4)
services/liminal/         ████░░░░░░░░░░░░░░░░░░░░░░░░░░░░   18% (2/11)
protocols/agentese/       ████░░░░░░░░░░░░░░░░░░░░░░░░░░░░    5% (5/100+)
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
```

### Completed (Session 1 — 2025-12-21)

| File | Status | Notes |
|------|--------|-------|
| `services/brain/persistence.py` | ✅ | 3 gotchas, evidence verified |
| `services/brain/node.py` | ✅ | Has Teaching sections |
| `protocols/agentese/gateway.py` | ✅ | Evidence refs updated |
| `protocols/agentese/registry.py` | ✅ | Evidence refs updated |
| `protocols/agentese/logos.py` | ✅ | Has Teaching sections |
| `protocols/agentese/node.py` | ✅ | Has Teaching sections |
| `services/ashc/*` | ✅ | All 3 files covered |
| `services/living_docs/*` | ✅ | Self-referential, complete |
| `docs/local-development.md` | ✅ | URLs updated for /_/ paths |
| `docs/systems-reference.md` | ✅ | Added pruning note |

---

## The Impact Matrix

```
                        HIGH USAGE              LOW USAGE
                    ┌─────────────────────┬─────────────────────┐
HIGH COMPLEXITY     │ 🔴 CRITICAL          │ 🟠 HIGH             │
(gotchas likely)    │ • container.py       │ • interactive_text/ │
                    │ • providers.py       │ • sheaf.py          │
                    │ • wiring.py          │ • polynomial.py     │
                    ├─────────────────────┼─────────────────────┤
LOW COMPLEXITY      │ ✅ DONE              │ 🟡 DEFER            │
(stable patterns)   │ • registry.py        │ • contexts/*        │
                    │ • node.py            │ • projectors/*      │
                    │ • gateway.py         │                     │
                    └─────────────────────┴─────────────────────┘
```

---

## Session Execution Plan

### Session 2: DI & Wiring (The Silent Skip Origin) ✅ COMPLETE

**Goal**: Document the DI system where silent failures originate.

**Completed**: 2025-12-21

**Files** (~3 files, ~1400 lines):

| File | Lines | Gotchas Added |
|------|-------|---------------|
| `protocols/agentese/container.py` | 415 | ✅ 3 gotchas: silent skip, singleton default, case-sensitive names |
| `services/providers.py` | ~500 | ✅ 3 gotchas: setup order, cache behavior, naming convention |
| `protocols/agentese/wiring.py` | 550 | ✅ 4 gotchas: path validation, graceful degradation, auto bridge, None observer |

**Tests Verified**:
```bash
pytest protocols/agentese/_tests/test_container.py -v  # 26 passed
pytest protocols/agentese/_tests/test_wiring.py -v     # 42 passed
pytest services/_tests/test_bootstrap.py -v            # 21 passed
```

**Success Criteria**:
- [x] Each file has ≥2 `Teaching:` gotchas with evidence
- [x] DI silent skip gotcha is documented at its SOURCE (container.py)
- [x] Evidence links point to actual test names

**Additional Fix**: Removed broken import of deleted `chat_resolver.py` from `self_soul.py`.

---

### Session 3: Interactive Text (New Crown Jewel) ✅ COMPLETE

**Goal**: Add Teaching sections to the completely undocumented Interactive Text service.

**Completed**: 2025-12-21

**Files** (~5 files, ~3000 lines):

| File | Lines | Gotchas Added |
|------|-------|---------------|
| `services/interactive_text/service.py` | 526 | ✅ 3 gotchas: toggle modes, 1-indexed lines, TraceWitness always captured |
| `services/interactive_text/parser.py` | 773 | ✅ 4 gotchas: token priority, roundtrip fidelity, empty docs, incremental parsing |
| `services/interactive_text/polynomial.py` | 553 | ✅ 4 gotchas: NoOp on invalid, stateless design, fixed directions, frozen outputs |
| `services/interactive_text/sheaf.py` | 713 | ✅ 5 gotchas: glue raises, metadata ignored, symmetric ops, single view, doc path match |
| `services/interactive_text/node.py` | 244 | ✅ 3 gotchas: DI silent skip, archetype affordances, dict return |

**Tests Verified**:
```bash
pytest services/interactive_text/_tests/test_parser.py -q       # 40 passed
pytest services/interactive_text/_tests/test_properties.py -q   # 63 passed
```

**Success Criteria**:
- [x] Core 5 files have Teaching sections (19 gotchas total)
- [x] Parser gotchas document token precedence (priority overlap handling)
- [x] Polynomial gotchas document mode transitions (NoOp, stateless, directions)
- [x] Sheaf gotchas document coherence conditions (glue, compatible, verify)

---

### Session 4: Liminal/Coffee (Personality Preservation)

**Goal**: Document the personality-rich liminal protocols.

**Files** (~5 files, ~2700 lines):

| File | Lines | Gotchas to Capture |
|------|-------|-------------------|
| `services/liminal/coffee/core.py` | 765 | Mood composition, personality blending |
| `services/liminal/coffee/node.py` | 534 | AGENTESE integration, observer handling |
| `services/liminal/coffee/types.py` | 577 | Type contracts, mood enum usage |
| `services/liminal/coffee/weather.py` | 460 | Weather pattern composition |
| `services/liminal/coffee/garden.py` | 377 | Garden metaphor gotchas |

**Already Done**:
- `stigmergy.py` ✅
- `circadian.py` ✅

**Success Criteria**:
- [ ] Anti-sausage gotchas documented (voice preservation)
- [ ] Circadian phase detection gotchas
- [ ] Weather composition rules

---

### Session 5: AGENTESE Core (Remaining Public APIs)

**Goal**: Complete AGENTESE public API coverage.

**Files** (~5 files, ~3500 lines):

| File | Lines | Gotchas to Capture |
|------|-------|-------------------|
| `protocols/agentese/parser.py` | 924 | Path parsing rules, context detection |
| `protocols/agentese/laws.py` | 704 | Law verification, violation handling |
| `protocols/agentese/subscription.py` | 1058 | Subscription lifecycle, cleanup |
| `protocols/agentese/jit.py` | 704 | JIT compilation gotchas |
| `protocols/agentese/affordances.py` | 1264 | Affordance resolution |

**Success Criteria**:
- [ ] Parser gotchas document path syntax
- [ ] Laws gotchas document verification patterns
- [ ] Subscription gotchas document cleanup requirements

---

## Deferred (Future Sessions)

### Context Resolvers (~70 files)
The `protocols/agentese/contexts/` directory has 70+ files totaling ~45,000 lines. These are lower priority because:
1. They follow established patterns
2. Most are implementation details
3. The critical gotchas live in the core files

**Strategy**: Add Teaching sections opportunistically when touching these files.

### Projectors & Tokens (~15 files)
The `services/interactive_text/tokens/` and `projectors/` subdirectories are implementation details. Cover them after core files.

---

## Evidence Verification Pattern

Every `Teaching:` gotcha MUST reference evidence:

```python
"""
Teaching:
    gotcha: Description of the gotcha.
            (Evidence: test_file.py::TestClass::test_method)
"""
```

**Verification Command**:
```bash
# Check if evidence test exists
grep -r "TestClass" protocols/agentese/_tests/test_file.py
```

**If Evidence Missing**: Write the test first, then add the Teaching section.

---

## Metrics Dashboard

Track progress with:

```bash
# Count files with Teaching sections
for dir in services/brain services/ashc services/interactive_text services/liminal protocols/agentese; do
  total=$(find $dir -name "*.py" -not -path "*/_tests/*" -not -name "__init__.py" | wc -l)
  covered=$(grep -rl "Teaching:" $dir --include="*.py" 2>/dev/null | grep -v "_tests" | wc -l)
  echo "$dir: $covered/$total"
done
```

**Target Coverage**:
| Tier | Target | Current |
|------|--------|---------|
| Crown Jewels (brain, ashc, interactive_text, living_docs) | 80% | ~40% |
| Liminal | 50% | 18% |
| AGENTESE Core (container, wiring, registry, gateway, logos, node) | 100% | 100% |
| AGENTESE Contexts | 10% | ~1% |

---

## Session Checklist Template

Copy for each session:

```markdown
## Session N: [Target]

### Pre-Work
- [ ] Read target files
- [ ] Run relevant tests to understand behavior
- [ ] Identify 2-3 gotchas per file

### Execution
- [ ] Add Teaching sections with evidence
- [ ] Verify evidence references are correct
- [ ] Run tests to confirm understanding

### Post-Work
- [ ] Update this strategy with completion status
- [ ] Run coverage metrics
- [ ] Note any discovered gotchas for other files
```

---

## Anti-Patterns to Avoid

| Anti-Pattern | Why Wrong | Do This Instead |
|--------------|-----------|-----------------|
| Gotchas without evidence | Claims rot without verification | Always link to test |
| Over-documenting | Teaching fatigue | 2-4 gotchas per file max |
| Documenting obvious things | Wastes attention | Focus on non-obvious gotchas |
| Writing tests after docs | Evidence should exist first | Test → Teaching |
| Batch updates | Context lost between sessions | Session-sized chunks |

---

## Connection to Principles

| Principle | How This Strategy Embodies It |
|-----------|------------------------------|
| **Tasteful** | Prioritized by impact, not completeness |
| **Curated** | Explicit defer for low-value files |
| **Generative** | Evidence-backed, reproducible |
| **Composable** | Session-sized, can be parallelized |
| **Joy-Inducing** | Prevents silent failures before they frustrate |

---

*"The proof is not in the prose. The proof is in the functor."*
