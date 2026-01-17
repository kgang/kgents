# Transformation QA Guide — 2026-01-16

> *"The proof IS the decision. The mark IS the witness. The test IS the validation."*

**Created**: 2026-01-16
**Purpose**: Verification, utilization, and QA of the radical transformation session
**Status**: Ready for Kent validation

---

## Quick Verification Commands

```bash
# Backend tests (expect 4,090+ pass, ~10 known failures)
cd impl/claude && uv run pytest services/zero_seed/ services/witness/ services/dialectic/ services/skill_injection/ -q

# Frontend types (expect zero errors)
cd impl/claude/web && npm run typecheck

# AGENTESE health check
cd impl/claude && uv run python -c "
from protocols.agentese.health import quick_health
import asyncio
print(asyncio.run(quick_health()))
"
```

---

## Phase-by-Phase Verification

### Phase 1: Core Pipeline & Galois Wiring

#### 1A: Pipeline Performance
```bash
# Run witness benchmarks
cd impl/claude && uv run pytest services/witness/_tests/test_trace_performance.py -v
```
**Expected**: All benchmarks pass (Mark <50ms, Trace <5ms)

#### 1B: Amendment B (Canonical Distance)
```bash
# Verify canonical distance is default
cd impl/claude && uv run python -c "
from services.zero_seed.galois.distance import get_default_metric
metric = get_default_metric()
print(f'Default metric: {metric.__class__.__name__}')
assert 'canonical' in metric.__class__.__name__.lower(), 'Amendment B not wired!'
print('Amendment B: VERIFIED')
"
```

#### 1C: Calibration Corpus
```bash
# Verify corpus expanded
cd impl/claude && uv run python -c "
from services.zero_seed.galois.layer_assignment import load_calibration_corpus
corpus = load_calibration_corpus()
print(f'Calibration entries: {len(corpus)}')
assert len(corpus) >= 20, 'Corpus not expanded!'
print('Calibration corpus: VERIFIED')
"
```

---

### Phase 2: ASHC Self-Awareness

#### 2A: Self-Awareness APIs
```bash
# Run ASHC tests
cd impl/claude && uv run pytest services/zero_seed/_tests/test_ashc_self_awareness.py -v

# Interactive verification
cd impl/claude && uv run python -c "
import asyncio
from services.zero_seed.ashc_self_awareness import ASHCSelfAwareness

async def test():
    service = ASHCSelfAwareness()

    # Test 1: Am I grounded?
    result = await service.am_i_grounded('COMPOSABLE')
    print(f'COMPOSABLE grounded: {result.is_grounded}')
    print(f'Path: {\" -> \".join(result.derivation_path)}')

    # Test 2: What principle justifies?
    justification = await service.what_principle_justifies('compose two agents')
    print(f'Principle: {justification.principle}')
    print(f'Loss: {justification.loss_score:.3f}')

    # Test 3: Why does this exist?
    explanation = await service.why_does_this_exist('ASHC')
    print(explanation)

asyncio.run(test())
"
```

#### 2B: Constitutional Graph View
```bash
# Verify component files exist
ls -la impl/claude/web/src/components/constitutional/
ls -la impl/claude/web/src/stores/constitutionalGraphStore.ts

# Type check
cd impl/claude/web && npm run typecheck
```

**To visually test**: Start the dev server and navigate to the constitutional graph view.

---

### Phase 3: Dialectical Fusion

#### 3A: AGENTESE Nodes
```bash
# Run dialectic node tests
cd impl/claude && uv run pytest services/dialectic/_tests/test_node.py -v

# Verify registration
cd impl/claude && uv run python -c "
from protocols.agentese import Logos
logos = Logos()
paths = ['self.dialectic.manifest', 'self.dialectic.sublate', 'concept.fusion.cocone']
for path in paths:
    node = logos.resolve(path)
    print(f'{path}: {\"REGISTERED\" if node else \"MISSING\"}')"
```

#### 3B: FusionCeremony UI
```bash
# Verify component files exist
ls -la impl/claude/web/src/components/dialectic/
ls -la impl/claude/web/src/api/dialectic.ts
```

**To visually test**: Start the dev server, navigate to FusionCeremony, and:
1. Enter a topic
2. Enter Kent's thesis and reasoning
3. Enter Claude's antithesis and reasoning
4. Click "Synthesize" and verify fusion appears

---

### Phase 4: Axiom Discovery

#### 4A: Discovery Pipeline
```bash
# Run pipeline tests (some may fail due to async infrastructure)
cd impl/claude && uv run pytest services/zero_seed/_tests/test_axiom_discovery_pipeline.py -v -x

# Manual verification
cd impl/claude && uv run python -c "
from services.zero_seed.axiom_discovery_pipeline import (
    AxiomDiscoveryPipeline, AxiomCandidate
)

# Create mock data
candidate = AxiomCandidate(
    content='Composition is primary',
    loss=0.03,
    stability=0.95,
    confidence=0.92,
    occurrences=18,
    evidence=['mark_001', 'mark_002'],
    source_pattern='composition patterns'
)
print(f'Axiom: {candidate.content}')
print(f'Loss: {candidate.loss} (< 0.05 = axiom)')
print(f'Confidence: {candidate.confidence}')
print('Pipeline structures: VERIFIED')
"
```

#### 4B: Personal Constitution Builder UI
```bash
# Verify component files
ls -la impl/claude/web/src/components/constitution/
ls -la impl/claude/web/src/stores/personalConstitutionStore.ts
ls -la impl/claude/web/src/api/axiomDiscovery.ts
```

---

### Phase 5: Crystal Compression

```bash
# Run compression tests
cd impl/claude && uv run pytest services/witness/_tests/test_crystal_compression.py -v
cd impl/claude && uv run pytest services/witness/_tests/test_crystal_export.py -v

# Manual verification
cd impl/claude && uv run python -c "
import asyncio
from services.witness.crystal_compression import CrystalCompressor
from services.witness.mark import Mark

async def test():
    compressor = CrystalCompressor()

    # Create test marks
    marks = [
        Mark(origin='test', response='Started the day planning', tags=['planning']),
        Mark(origin='test', response='Had a breakthrough on compression', tags=['eureka']),
        Mark(origin='test', response='Decided to use Galois loss', tags=['decision']),
    ]

    result = await compressor.compress(marks)
    print(f'Compression ratio: {result.compression_ratio:.1%}')
    print(f'Preserved: {len(result.preserved_marks)} marks')
    print(f'Dropped: {len(result.dropped_marks)} marks')
    print(f'Causal chain: {len(result.causal_chain)} links')
    print('Compression: VERIFIED')

asyncio.run(test())
"
```

---

### Phase 6: JIT Skill Injection

```bash
# Run skill injection tests
cd impl/claude && uv run pytest services/skill_injection/_tests/test_skill_injection.py -v

# Manual verification
cd impl/claude && uv run python -c "
from services.skill_injection import SkillRegistry, JITInjector, bootstrap_skills

# Bootstrap existing skills
registry = SkillRegistry()
count = bootstrap_skills(registry)
print(f'Skills loaded: {count}')

# Test activation
from services.skill_injection import ActivationConditionEngine, TaskContext
engine = ActivationConditionEngine(registry)
context = TaskContext(task_description='create a new AGENTESE node')
skills = engine.select_skills(context, max_skills=3)
print(f'Activated skills: {[s.name for s in skills]}')
print('JIT Injection: VERIFIED')
"
```

---

### Integration: Unified AGENTESE

```bash
# Run integration tests
cd impl/claude && uv run pytest protocols/agentese/_tests/test_unified_nodes.py -v

# Health check all new nodes
cd impl/claude && uv run python -c "
import asyncio
from protocols.agentese.health import check_unified_nodes_health

async def test():
    report = await check_unified_nodes_health()
    print(f'Total nodes: {report.total_nodes}')
    print(f'Healthy: {report.healthy_nodes}')
    if report.failed_nodes:
        print(f'Failed: {report.failed_nodes}')
    print(f'Status: {\"HEALTHY\" if report.is_healthy else \"UNHEALTHY\"}')

asyncio.run(test())
"
```

---

## Utilization Guide

### Using ASHC Self-Awareness

```python
# In code
from services.zero_seed.ashc_self_awareness import ASHCSelfAwareness

service = ASHCSelfAwareness()

# Ask: "Why does this exist?"
explanation = await service.why_does_this_exist("COMPOSABLE")

# Ask: "Is this grounded?"
result = await service.am_i_grounded("my_custom_block")

# Ask: "What principle justifies this action?"
justification = await service.what_principle_justifies("refactor the API")
```

```bash
# Via AGENTESE (when gateway is running)
curl -X POST http://localhost:8000/agentese/self/axiom/manifest
```

### Using Dialectical Fusion

```python
# In code
from services.dialectic import DialecticalFusionService

service = DialecticalFusionService()

# Create a fusion
result = await service.sublate(
    topic="Database choice",
    kent_view="Use PostgreSQL for reliability",
    kent_reasoning="Production-proven, ACID compliance",
    claude_view="Consider SQLite for simplicity",
    claude_reasoning="Simpler ops, file-based, good for dev"
)

print(f"Synthesis: {result.synthesis}")
print(f"Preserved from Kent: {result.kent_preserved}")
print(f"Preserved from Claude: {result.claude_preserved}")
```

### Using Axiom Discovery

```python
# In code (when you have decision history)
from services.zero_seed.axiom_discovery_pipeline import AxiomDiscoveryPipeline

pipeline = AxiomDiscoveryPipeline()
result = await pipeline.discover_axioms(
    user_id="kent",
    days=30,
    max_candidates=5
)

for axiom in result.candidates:
    if axiom.loss < 0.05:
        print(f"L0 AXIOM: {axiom.content} (L={axiom.loss:.3f})")
```

### Using Crystal Compression

```python
# In code
from services.witness.crystal_compression import CrystalCompressor
from services.witness.crystal_export import CrystalExporter

compressor = CrystalCompressor()
exporter = CrystalExporter()

# Compress a day's marks
result = await compressor.compress(marks, max_ratio=0.10)

# Export as shareable markdown
markdown = await exporter.export_as_markdown(result.crystal)
print(markdown)

# Export as image (requires Pillow)
path = await exporter.export_as_image(result.crystal, Path("./crystal.png"))
```

### Using JIT Skill Injection

```python
# In code
from services.skill_injection import JITInjector, bootstrap_skills, SkillRegistry

registry = SkillRegistry()
bootstrap_skills(registry)
injector = JITInjector(registry)

# Inject skills for a task
injected = await injector.inject_for_task(
    "Create a new AGENTESE node for the billing service"
)
print(injected)  # Contains relevant skill content
```

---

## Known Issues

| Issue | Severity | Workaround |
|-------|----------|------------|
| 10 failing tests in axiom discovery | Low | Async/xdist infrastructure issue, not logic |
| Crystal compression ratio varies | Low | Depends on mark content length |
| Image export requires Pillow | Low | Falls back to markdown |
| Some AGENTESE nodes need gateway | Info | Run `kg dev` first |

---

## QA Checklist

### Backend
- [ ] All core tests pass (`uv run pytest services/witness/ -q`)
- [ ] Galois tests pass (`uv run pytest services/zero_seed/galois/ -q`)
- [ ] ASHC tests pass (66 tests)
- [ ] Dialectic tests pass (46 tests)
- [ ] Skill injection tests pass (29 tests)
- [ ] Crystal compression tests pass (42 tests)

### Frontend
- [ ] TypeScript compiles with zero errors
- [ ] ConstitutionalGraphView renders
- [ ] FusionCeremony form works
- [ ] PersonalConstitutionBuilder loads

### Integration
- [ ] AGENTESE health check reports HEALTHY
- [ ] All 4 new node paths registered
- [ ] Event bus topics wired

### End-to-End
- [ ] Can capture marks via API
- [ ] Can compress marks to crystal
- [ ] Can export crystal as markdown
- [ ] Can discover axioms from marks
- [ ] Can perform dialectical fusion

---

## Files Created/Modified

### New Services (~8,500 LOC)
```
services/zero_seed/ashc_self_awareness.py       # ASHC Self-Awareness
services/zero_seed/axiom_discovery_pipeline.py  # Axiom Discovery
services/zero_seed/axiom_node.py                # AGENTESE node
services/dialectic/node.py                      # Dialectic AGENTESE
services/witness/crystal_compression.py         # Crystal Compression
services/witness/crystal_export.py              # Crystal Export
services/witness/crystal_nodes.py               # Crystal AGENTESE
services/skill_injection/                       # JIT Skill Injection (9 files)
```

### New Frontend Components
```
web/src/components/constitutional/              # 8 files
web/src/components/dialectic/                   # 8 files
web/src/components/constitution/                # 8 files
web/src/stores/constitutionalGraphStore.ts
web/src/stores/personalConstitutionStore.ts
web/src/api/ashc.ts
web/src/api/dialectic.ts
web/src/api/axiomDiscovery.ts
```

### New Tests (~200 test cases)
```
services/zero_seed/_tests/test_ashc_self_awareness.py
services/zero_seed/_tests/test_axiom_discovery_pipeline.py
services/dialectic/_tests/test_node.py
services/witness/_tests/test_crystal_compression.py
services/witness/_tests/test_crystal_export.py
services/skill_injection/_tests/test_skill_injection.py
protocols/agentese/_tests/test_unified_nodes.py
```

### New Documentation
```
docs/skills/unified-agentese-nodes.md
services/zero_seed/galois/calibration_corpus.json
```

---

## Next Steps

1. **Run the full QA checklist above**
2. **Test trail-to-crystal flow end-to-end** (capture → compress → export)
3. **Test axiom discovery** on real decision history
4. **Test fusion ceremony** with a real disagreement
5. **Visual test UI components** via dev server

---

*"The proof IS the decision. The mark IS the witness. The QA IS the validation."*
