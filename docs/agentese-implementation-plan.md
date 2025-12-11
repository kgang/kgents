# AGENTESE Implementation Plan

**Status**: COMPLETE - All 8 phases implemented with 559 passing tests.

**Spec**: `spec/protocols/agentese.md` (v2.0)
**Target**: `impl/claude/protocols/agentese/`
**Dependencies**: J-gent (JIT), L-gent (Registry), G-gent (Grammar), D-gent (State), Umwelt (Observer)

---

## Executive Summary

AGENTESE is a verb-first ontology that transforms how agents interact with the world. Instead of querying a database of nouns, agents grasp **handles** that yield **affordances** based on who is grasping. This plan outlines how to implement the AGENTESE protocol in phases, with each phase delivering testable, usable functionality.

**Core Equation**: `H(Context) ──Logos──▶ Interaction`

---

## Phase 1: Foundation (Core Protocol)

**Goal**: Establish the LogosNode protocol and basic resolver infrastructure.

### 1.1 Create Package Structure

```
impl/claude/protocols/agentese/
├── __init__.py              # Public API exports
├── logos.py                 # Logos resolver
├── node.py                  # LogosNode protocol + base classes
├── exceptions.py            # Sympathetic error types
└── contexts/
    └── __init__.py          # Context registry
```

### 1.2 Implement Core Types

**File**: `node.py`

```python
# Core types to implement:
- LogosNode (Protocol)
- AffordanceSet (dataclass)
- Renderable (Protocol)
- JITLogosNode (base implementation for generated nodes)
```

**Key Invariants**:
- LogosNode must be stateless (Symbiont pattern)
- State access via D-gent Lens only
- All methods require observer context (no view from nowhere)

### 1.3 Implement Exceptions

**File**: `exceptions.py`

```python
# Sympathetic error types:
- PathNotFoundError       # With suggestions for resolution
- PathSyntaxError         # With grammar hint
- AffordanceError         # Lists available affordances
- ObserverRequiredError   # No view from nowhere
- TastefulnessError       # Spec validation failure
- BudgetExhaustedError    # Accursed Share depleted
```

**Key Invariant**: All errors must explain *why* and suggest *what to do*.

### 1.4 Implement Basic Logos Resolver

**File**: `logos.py`

```python
# Methods to implement:
- resolve(path, observer) -> LogosNode
- invoke(path, observer, **kwargs) -> Any
- lift(path) -> Agent[Umwelt, Any]  # For composition
```

**Key Invariants**:
- invoke() requires observer (raises ObserverRequiredError if None)
- Lazy hydration (only instantiate on observation)
- Cache resolved nodes

### 1.5 Tests

```
tests/protocols/agentese/
├── test_node.py           # Protocol compliance
├── test_logos.py          # Resolver logic
├── test_exceptions.py     # Error messages are sympathetic
└── conftest.py            # Fixtures (mock observers, nodes)
```

**Test Cases**:
- [ ] LogosNode protocol compliance
- [ ] Path parsing (context.holon.aspect)
- [ ] Observer requirement enforcement
- [ ] Sympathetic error messages
- [ ] Cache behavior

---

## Phase 2: Five Contexts

**Goal**: Implement all five strict contexts with basic affordances.

### 2.1 World Context

**File**: `contexts/world.py`

```python
# Implement:
- WorldContextResolver
- Generic world.* node with:
  - manifest: Polymorphic rendering
  - witness: History via N-gent
  - affordances: List available verbs
  - define: Autopoiesis (creates new entities)
```

**Integration**: L-gent registry for known entities, spec/ for generative.

### 2.2 Self Context

**File**: `contexts/self_.py` (self is reserved)

```python
# Implement:
- SelfContextResolver
- self.memory node:
  - manifest: Current memory state
  - consolidate: Hypnagogic cycle
  - prune: Garbage collection
  - checkpoint: Snapshot
- self.capabilities node:
  - affordances: What can this agent do?
```

**Integration**: D-gent for memory access.

### 2.3 Concept Context

**File**: `contexts/concept.py`

```python
# Implement:
- ConceptContextResolver
- Generic concept.* node with:
  - manifest: Definition/description
  - refine: Dialectical challenge (spawns critique)
  - relate: Find connections to other concepts
  - define: Create new concept
```

**Integration**: G-gent for grammar validation.

### 2.4 Void Context (Accursed Share)

**File**: `contexts/void.py`

```python
# Implement:
- VoidContextResolver
- EntropyPool (manages Accursed Share budget)
- void.entropy node:
  - sip: Draw randomness
  - pour: Return unused randomness
- void.gratitude node:
  - tithe: Pay for order (noop sacrifice)
  - thank: Express gratitude
- void.serendipity node:
  - sip: Request tangent
```

**Key Invariant**: Everyone can interact with the void.

### 2.5 Time Context

**File**: `contexts/time.py`

```python
# Implement:
- TimeContextResolver
- time.trace node:
  - witness: View temporal trace (N-gent)
- time.past node:
  - project: View state at timestamp (D-gent temporal lens)
- time.future node:
  - forecast: Probabilistic forecast (B-gent)
- time.schedule node:
  - defer: Schedule future action (Kairos)
```

**Integration**: N-gent for traces, D-gent for temporal lens, Kairos for scheduling.

### 2.6 Tests

```
tests/protocols/agentese/contexts/
├── test_world.py
├── test_self.py
├── test_concept.py
├── test_void.py
└── test_time.py
```

**Test Cases**:
- [ ] Each context resolves correctly
- [ ] Invalid context raises PathNotFoundError
- [ ] Only five contexts allowed (no sixth)
- [ ] Void context always available

---

## Phase 3: Polymorphic Affordances ✅ COMPLETE

**Goal**: Implement observer-dependent affordance filtering.
**Status**: Implemented (244 total tests)
**Files**: `affordances.py` (560 lines), `renderings.py` (320 lines)

### 3.1 Affordance Protocol ✅

**File**: `affordances.py`

```python
# Implemented:
- AffordanceRegistry: Central registry for archetype → affordances mappings
- StandardAffordanceMatcher: Pattern-based affordance resolution
- CapabilityAffordanceMatcher: Capability-based grants
- ArchetypeDNA: DNA type for archetype-based configuration
- UmweltAdapter: Extract affordance-relevant info from Umwelt
- ContextAffordanceSet: Per-context affordance configuration
```

### 3.2 Archetypes Defined ✅

```
architect  → renovate, measure, blueprint, demolish, design
developer  → build, deploy, debug, test, refactor
scientist  → analyze, measure, experiment, hypothesize, validate, forecast
admin      → configure, monitor, audit, provision
poet       → describe, metaphorize, inhabit, contemplate
philosopher → refine, dialectic, synthesize, critique
economist  → appraise, forecast, compare, trade
inhabitant → inhabit, repair, transform
default    → (core only: manifest, witness, affordances)
```

### 3.3 Rendering Protocol ✅

**File**: `renderings.py`

```python
# Implemented (7 new types):
- ScientificRendering: measurements, observations, hypotheses, confidence
- DeveloperRendering: language, dependencies, build_status, test_coverage
- AdminRendering: status, health, metrics, config, alerts
- PhilosopherRendering: concept, thesis/antithesis/synthesis, related_concepts
- MemoryRendering: memory_count, consolidated, temporary, checkpoints
- EntropyRendering: remaining, total, history_length, gratitude_balance
- TemporalRendering: trace_count, scheduled_count, horizon
- StandardRenderingFactory: Polymorphic rendering creation
```

### 3.4 Tests ✅

**File**: `_tests/test_affordances.py` (66 tests)

**Test Cases** (all passing):
- [x] Same path, different observer, different affordances
- [x] AffordanceError when accessing unavailable aspect
- [x] Error message lists available affordances
- [x] manifest() returns archetype-appropriate rendering
- [x] Polymorphic manifest tests for all archetypes
- [x] Rendering factory tests
- [x] UmweltAdapter integration tests

---

## Phase 4: Generative Collapse (JIT) ✅ COMPLETE

**Goal**: Implement spec → implementation generation via J-gent.
**Status**: Implemented (283 total tests, 39 Phase 4 specific)
**Files**: `jit.py` (600 lines), `spec/world/README.md`, `spec/world/library.md`

### 4.1 Spec Layer Integration ✅

**File**: `jit.py`

```python
# Implemented:
- SpecParser: Parse YAML front matter + markdown specs
- SpecCompiler: Generate Python source from ParsedSpec
- JITCompiler: Full pipeline (parse → compile → validate → JITLogosNode)
```

### 4.2 JIT Node ✅

**File**: `node.py` (extended)

```python
# Implemented:
- JITLogosNode:
  - Wraps generated source
  - Tracks usage_count, success_count for promotion
  - Stores original spec for reference
  - should_promote() method
```

### 4.3 Autopoiesis (define aspect) ✅

**File**: `logos.py` (extended)

```python
# Implemented:
- define_concept(handle, observer, spec) -> LogosNode
  1. Validate handle syntax
  2. Validate observer affordance (architect/developer/admin)
  3. Compile via JITCompiler
  4. Track in _jit_nodes registry
  5. Cache and return
```

### 4.4 Promotion Protocol ✅

**File**: `logos.py` + `jit.py`

```python
# Implemented:
- promote_concept(handle, threshold=100, success_threshold=0.8) -> PromotionResult
  - Check usage_count >= threshold
  - Check success_rate >= success_threshold
  - Write to impl/generated/ if JITLogosNode
  - Return PromotionResult with status and details
- get_jit_status(handle) -> dict  # Get node status
- list_jit_nodes() -> list[dict]  # List all JIT nodes
```

### 4.5 Create spec/world/ Structure ✅

```
spec/world/
├── README.md              # How to write world.* specs (JIT pipeline diagram)
└── library.md             # Full reference spec with all affordances/manifest
```

### 4.6 Tests ✅

**File**: `_tests/test_jit.py` (39 tests)

**Test Cases** (all passing):
- [x] SpecParser parses YAML front matter + markdown
- [x] SpecCompiler generates valid Python source
- [x] Generated source includes affordances mapping
- [x] JITCompiler full pipeline works
- [x] define_concept creates node and tracks in registry
- [x] define_concept unauthorized for non-architects
- [x] promote_concept succeeds when threshold met
- [x] promote_concept fails when not ready
- [x] get_jit_status returns node status
- [x] list_jit_nodes returns all JIT nodes

---

## Phase 5: Composition & Category Laws ✅ COMPLETE

**Goal**: Implement the >> operator and verify category laws.
**Status**: Implemented (363 total tests, 80 Phase 5 specific)
**Files**: `laws.py` (450 lines), enhanced `logos.py`

### 5.1 ComposedPath ✅

**File**: `logos.py` (extended)

```python
# Implemented:
- ComposedPath:
  - __rshift__ for composition with strings and other ComposedPaths
  - __rrshift__ for string >> ComposedPath
  - invoke(observer, initial_input) -> Any with Minimal Output enforcement
  - lift_all() -> list[Agent] for getting all morphisms
  - without_enforcement() for relaxed mode
  - __len__, __iter__, __eq__ for usability
```

### 5.2 IdentityPath ✅

**File**: `logos.py` (new class)

```python
# Implemented:
- IdentityPath:
  - Identity morphism for AGENTESE paths
  - Id >> path == path (via __rshift__)
  - path >> Id == path (via __rrshift__)
  - invoke() returns input unchanged
```

### 5.3 Category Law Verification ✅

**File**: `laws.py` (new file)

```python
# Implemented:
- Identity / Id / IDENTITY: Global identity morphism
- Composed: Composition of two morphisms (right-associative)
- CategoryLawVerifier:
  - verify_left_identity(f, input) -> LawVerificationResult
  - verify_right_identity(f, input) -> LawVerificationResult
  - verify_identity(f, input) -> LawVerificationResult
  - verify_associativity(f, g, h, input) -> LawVerificationResult
  - verify_all(f, g, h, input) -> list[LawVerificationResult]
- LawVerificationResult: Result type with passed, left_result, right_result, error
```

### 5.4 Minimal Output Principle Enforcement ✅

```python
# Implemented in laws.py:
- is_single_logical_unit(value) -> bool
  - True for: single values, Renderables, iterators/generators
  - False for: list, tuple, set, frozenset
- enforce_minimal_output(value, context) -> value
  - Returns value if valid
  - Raises CompositionViolationError if array
```

### 5.5 Helper Functions ✅

```python
# Implemented in laws.py:
- compose(*morphisms) -> Composable  # Left-to-right composition
- pipe(input, *morphisms) -> Any  # Pipe value through morphisms
- LawEnforcingComposition  # Wrapper that checks output
- SimpleMorphism  # Test helper
- @morphism decorator  # Create morphism from function
- create_verifier()  # Factory for CategoryLawVerifier
- create_enforcing_composition()  # Factory for law-enforcing composition
```

### 5.6 Logos Enhancements ✅

```python
# New methods in Logos:
- compose(*paths, enforce_output=True) -> ComposedPath
- identity() -> IdentityPath
- path(p) -> ComposedPath  # Single-path for chaining
```

### 5.7 Tests ✅

**File**: `_tests/test_laws.py` (80 tests)

**Test Cases** (all passing):
- [x] Identity morphism returns input unchanged
- [x] Identity >> f == f (left identity)
- [x] f >> Id == f (right identity)
- [x] (f >> g) >> h == f >> (g >> h) (associativity)
- [x] CategoryLawVerifier verifies all laws
- [x] Single values are valid (is_single_logical_unit)
- [x] Lists/tuples/sets raise CompositionViolationError
- [x] Generators/iterators allowed (lazy sequences)
- [x] ComposedPath composition works
- [x] IdentityPath behavior
- [x] compose() helper
- [x] pipe() helper
- [x] LawEnforcingComposition checks output
- [x] SimpleMorphism and @morphism decorator
- [x] Parameterized law tests for multiple inputs

---

## Phase 6: Integration

**Goal**: Wire AGENTESE into existing kgents infrastructure.

### 6.1 Umwelt Integration

```python
# In logos.py:
- All invoke() calls receive observer Umwelt
- DNA archetype determines affordances
- Lens scope determines visible state
- Gravity applies constraints
```

### 6.2 Membrane Integration

```python
# In impl/claude/protocols/membrane/:
- Map CLI commands to AGENTESE paths:
  - "kgents observe" → world.project.manifest
  - "kgents sense" → world.project.sense
  - "kgents trace X" → time.trace.witness
  - "kgents dream" → self.memory.consolidate
```

### 6.3 L-gent Integration

```python
# In logos.py:
- resolve() checks L-gent registry first
- define_concept() registers in L-gent
- promote_concept() updates L-gent status
```

### 6.4 G-gent Integration

```python
# Create AGENTESE grammar:
- domain="agentese"
- level=GrammarLevel.COMMAND
- BNF for path syntax
```

### 6.5 Tests

**Test Cases**:
- [ ] Umwelt observer determines affordances
- [ ] Membrane commands resolve to AGENTESE
- [ ] L-gent registry lookup works
- [ ] G-gent grammar validates paths

---

## Phase 7: Adapter (Drop-In)

**Goal**: Enable legacy system integration via natural language translation.

### 7.1 AgentesAdapter

**File**: `adapter.py`

```python
# Implement:
- AgentesAdapter:
  - __init__(logos, translator)
  - execute(natural_input, observer) -> Any
    1. Translate via LLM
    2. Validate syntax
    3. Invoke via Logos
```

### 7.2 Translation Examples

```python
# Training data for translator:
"Get server status" → "world.server.status.manifest"
"Show me the logs" → "world.logs.witness"
"Create a new user" → "world.user.define"
"What happened yesterday?" → "time.past.project"
"Give me something random" → "void.entropy.sip"
```

### 7.3 Tests

**Test Cases**:
- [ ] Natural language translates to valid AGENTESE
- [ ] Invalid translations raise appropriate errors
- [ ] Adapter invokes Logos correctly

---

## Success Metrics

| Metric | Target | Measurement |
|--------|--------|-------------|
| **Test Coverage** | >90% | pytest-cov |
| **Observer Enforcement** | 100% | No invoke() without observer |
| **Sympathetic Errors** | 100% | All errors explain why + suggest fix |
| **Category Laws** | Pass | Runtime verification |
| **JIT Success Rate** | >80% | L-gent metrics |
| **Composition** | Works | >> operator tests |

---

## Risk Mitigation

| Risk | Mitigation |
|------|------------|
| J-gent JIT failures | Graceful fallback to PathNotFoundError with spec suggestion |
| Performance (lazy hydration) | Aggressive caching, LRU eviction |
| Category law violations | Runtime verification in laws.py |
| Context creep (sixth context) | Hard-coded whitelist in resolve() |
| Array returns breaking composition | Type enforcement in lens() |

---

## Dependencies

| Phase | Depends On |
|-------|------------|
| 1 (Foundation) | D-gent (Lens), Umwelt |
| 2 (Contexts) | N-gent, D-gent, B-gent, Kairos |
| 3 (Affordances) | K-gent (observer archetypes) |
| 4 (JIT) | J-gent (MetaArchitect), G-gent, L-gent |
| 5 (Composition) | C-gent (Agent protocol) |
| 6 (Integration) | Membrane, L-gent, G-gent |
| 7 (Adapter) | LLM translator |

---

## Implementation Status

| Phase | Focus | Status | Tests |
|-------|-------|--------|-------|
| 1. Foundation | LogosNode, Logos, Exceptions | ✅ COMPLETE | 113 |
| 2. Five Contexts | world, self, concept, void, time | ✅ COMPLETE | 178 |
| 3. Affordances | Polymorphic perception | ✅ COMPLETE | 244 |
| 4. JIT | Generative collapse (spec → impl) | ✅ COMPLETE | 283 |
| 5. Composition | >> operator, category laws | ✅ COMPLETE | 363 |
| 6. Integration | Umwelt, Membrane, L-gent, G-gent | ✅ COMPLETE | 444 |
| 7. Wire to Logos | WiredLogos production resolver | ✅ COMPLETE | 488 |
| 8. Adapter | Natural language → AGENTESE | ✅ COMPLETE | 559 |

---

## Phase 1 Deliverables (COMPLETE - 2025-12-10)

### Files Created

```
impl/claude/protocols/agentese/
├── __init__.py         # Public API exports
├── logos.py            # Logos resolver functor
├── node.py             # LogosNode protocol + types
├── exceptions.py       # Sympathetic errors
└── contexts/
    └── __init__.py     # VALID_CONTEXTS registry
```

### Test Files

```
impl/claude/protocols/agentese/_tests/
├── conftest.py           # MockUmwelt, MockNode, fixtures
├── test_exceptions.py    # 39 tests
├── test_node.py          # 31 tests
└── test_logos.py         # 43 tests
```

### Key Implementations

| Component | Description |
|-----------|-------------|
| `LogosNode` | Protocol for resolvable entities (handle, affordances, lens, manifest, invoke) |
| `Logos` | Resolver functor with caching, context validation, JIT stub |
| `AgentMeta` | Observer metadata for affordance filtering |
| `AffordanceSet` | Observer-specific verb list |
| `JITLogosNode` | JIT-generated node with usage tracking |
| `Renderable` | Protocol + 4 implementations (Basic, Blueprint, Poetic, Economic) |
| `ComposedPath` | Path composition for pipelines |
| 7 Exception types | All sympathetic (explain why + suggest fix) |

---

---

## Phase 2 Deliverables (COMPLETE - 2025-12-10)

### Files Created

```
impl/claude/protocols/agentese/contexts/
├── __init__.py     # Exports + create_context_resolvers()
├── world.py        # WorldNode, WorldContextResolver (287 lines)
├── self_.py        # MemoryNode, CapabilitiesNode, StateNode, IdentityNode (268 lines)
├── concept.py      # ConceptNode, ConceptContextResolver (426 lines)
├── void.py         # EntropyPool, EntropyNode, SerendipityNode, GratitudeNode (422 lines)
└── time.py         # TraceNode, PastNode, FutureNode, ScheduleNode (424 lines)
```

### Test File

```
impl/claude/protocols/agentese/_tests/
└── test_contexts.py   # 65 tests
```

### Key Implementations

| Context | Nodes | Key Features |
|---------|-------|--------------|
| `world.*` | WorldNode | Archetype-specific affordances (architect, poet, scientist) |
| `self.*` | MemoryNode, CapabilitiesNode, StateNode, IdentityNode | Memory consolidation, capability management |
| `concept.*` | ConceptNode | Dialectic, refine, synthesize, relate |
| `void.*` | EntropyNode, SerendipityNode, GratitudeNode | Shared EntropyPool, tithe regeneration |
| `time.*` | TraceNode, PastNode, FutureNode, ScheduleNode | Kairos scheduling, temporal projection |

### Integration with Logos

- Context resolvers wired via `create_context_resolvers()`
- Logos `__post_init__` initializes all five resolvers
- Resolvers create placeholder nodes for unknown holons (exploration-friendly)
- Factory: `create_logos(narrator=..., d_gent=..., b_gent=..., grammarian=...)`

---

## Phase 7 Deliverables (COMPLETE - 2025-12-10)

### Files Created

```
impl/claude/protocols/agentese/
└── wiring.py         # WiredLogos + factory functions (400 lines)
```

### Test Files

```
impl/claude/protocols/agentese/_tests/
└── test_wiring.py    # 44 tests - WiredLogos, integration wiring
```

### Key Implementations

| Component | Description |
|-----------|-------------|
| `WiredLogos` | Production resolver with all integrations wired |
| `create_wired_logos()` | Factory with full integration support |
| `wire_existing_logos()` | Wire integrations to existing Logos |
| `create_minimal_wired_logos()` | Minimal wiring for testing |
| Path validation | G-gent BNF validation before resolve/invoke |
| Usage tracking | L-gent metrics after every invocation |
| Observer meta | UmweltIntegration for archetype extraction |
| Membrane bridge | CLI commands → AGENTESE paths |

### Wiring Architecture

```
User Request: "world.house.manifest"
       │
       ▼
┌─────────────────────┐
│   GgentIntegration  │  ← Validates path syntax against BNF
│   (Path Validation) │
└─────────────────────┘
       │
       ▼
┌─────────────────────┐
│   LgentIntegration  │  ← Semantic lookup in registry
│   (Registry Lookup) │    (embeddings, usage tracking)
└─────────────────────┘
       │
       ▼
┌─────────────────────┐
│  UmweltIntegration  │  ← Extract AgentMeta from observer DNA
│   (Observer Meta)   │    (archetype → affordances)
└─────────────────────┘
       │
       ▼
┌─────────────────────┐
│       Logos         │  ← Resolve node, check affordances, invoke
│     (Resolver)      │
└─────────────────────┘
```

### Usage

```python
from protocols.agentese import create_wired_logos, WiredLogos

# Create fully wired production resolver
wired = create_wired_logos(
    lgent_registry=registry,    # L-gent for semantic lookup
    grammarian=g_gent,          # G-gent for path validation
    validate_paths=True,        # Enable path validation
    track_usage=True,           # Track invocations
)

# Invoke AGENTESE path
result = await wired.invoke("world.house.manifest", observer)

# Execute Membrane command via AGENTESE
result = await wired.execute_membrane_command("observe", observer)

# Check integration status
status = wired.integration_status()
# {'umwelt': True, 'lgent': True, 'ggent': True, 'membrane': True}
```

---

## Phase 8 Deliverables (COMPLETE - 2025-12-10)

### Files Created

```
impl/claude/protocols/agentese/
└── adapter.py         # Natural language adapter (500 lines)
```

### Test Files

```
impl/claude/protocols/agentese/_tests/
└── test_adapter.py    # 71 tests - pattern translation, LLM fallback, adapter
```

### Key Implementations

| Component | Description |
|-----------|-------------|
| `TranslationResult` | Immutable result with path, confidence, source, matched_pattern |
| `TranslationError` | Sympathetic error with suggestions |
| `PatternTranslator` | Fast path - rule-based pattern matching |
| `LLMTranslator` | Slow path - LLM fallback with few-shot examples |
| `AgentesAdapter` | Unified adapter orchestrating both translators |
| `TRANSLATION_PATTERNS` | 35+ patterns covering all 5 contexts |
| `LLM_TRANSLATION_EXAMPLES` | 20+ few-shot examples for LLM |

### Adapter Architecture

```
User Input: "show me the house"
       │
       ▼
┌─────────────────────┐
│  PatternTranslator  │  ← Rule-based patterns (fast, no LLM)
│   (Fast Path)       │    "show me" → manifest, "what happened" → witness
└─────────────────────┘
       │ (if no match)
       ▼
┌─────────────────────┐
│   LLMTranslator     │  ← LLM-based translation (slow, fallback)
│    (Slow Path)      │    Few-shot prompting with examples
└─────────────────────┘
       │
       ▼
┌─────────────────────┐
│  GgentIntegration   │  ← Validates output is valid AGENTESE
│    (Validation)     │
└─────────────────────┘
       │
       ▼
┌─────────────────────┐
│      WiredLogos     │  ← Execute the translated path
│     (Execution)     │
└─────────────────────┘
```

### Usage

```python
from protocols.agentese import create_adapter, AgentesAdapter

# Create adapter
adapter = create_adapter(
    logos=wired_logos,
    llm=my_llm,              # Optional LLM for fallback
    min_confidence=0.5,      # Minimum confidence threshold
    use_llm_fallback=True,   # Enable LLM fallback
)

# Translate natural language to AGENTESE
result = await adapter.translate("show me the house")
# TranslationResult(path='world.house.manifest', confidence=0.9, source='pattern')

# Translate and execute in one step
result = await adapter.execute("what happened to the server?", observer)

# Direct AGENTESE paths pass through
result = await adapter.translate("world.server.manifest")
# TranslationResult(path='world.server.manifest', confidence=1.0, source='direct')
```

### Pattern Coverage

| Context | Example Patterns |
|---------|-----------------|
| `world.*` | "show me the X", "get X", "describe X", "create X" |
| `self.*` | "show my memory", "dream", "what can I do?" |
| `concept.*` | "think about X", "refine X", "define X" |
| `void.*` | "give me randomness", "surprise me", "tithe", "thanks" |
| `time.*` | "show logs", "trace X", "forecast X", "schedule X" |

---

## Summary

AGENTESE is now fully implemented with 559 passing tests across 8 phases:

1. **Foundation** - LogosNode protocol, resolver, sympathetic errors
2. **Five Contexts** - world, self, concept, void, time
3. **Affordances** - Polymorphic perception per archetype
4. **JIT** - Generative collapse from spec → implementation
5. **Composition** - Category laws, >> operator
6. **Integration** - Umwelt, Membrane, L-gent, G-gent wiring
7. **Wire to Logos** - WiredLogos production resolver
8. **Adapter** - Natural language → AGENTESE translation

*"The handle you grasp shapes what you hold."*
