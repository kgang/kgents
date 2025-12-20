# Design Document: Kiro-kgents Deep Integration

## Overview

The Kiro-kgents Integration system creates a **bidirectional bridge** between two complementary configuration ecosystems:

- **Kiro** (`~/.kiro`): IDE-level infrastructure — specs, steering, powers, extensions
- **kgents** (`~/.kgents`): Agent-level infrastructure — soul, brain, witness, telemetry, data

This integration embodies the **Metaphysical Fullstack** principle (AD-009) where specifications flow down into agent behavior and agent insights flow back up to refine specifications. The system treats:

- Kiro specs as **compression morphisms** from human intent to agent behavior
- kgents witnesses as **constructive proofs** that validate spec compliance
- Brain patterns as **emergent knowledge** that suggests spec refinements
- Soul eigenvectors as **personalization lenses** that filter spec interpretation

**Semantic Linking Requirement**: All specifications MUST be semantically linked and synced with corresponding files in `spec/`. This ensures the kgents metatheory remains coherent across all documentation layers.

```
┌─────────────────────────────────────────────────────────────────┐
│                    THE GENERATIVE LOOP                          │
│                                                                 │
│   ┌──────────┐    Compile    ┌──────────┐    Execute    ┌─────┐│
│   │Kiro Spec │──────────────▶│ AGENTESE │──────────────▶│Agent││
│   └──────────┘               └──────────┘               └─────┘│
│        ▲                                                   │    │
│        │                                                   │    │
│   Refine                                              Witness   │
│        │                                                   │    │
│        │    ┌──────────┐    Analyze    ┌──────────┐       │    │
│        └────│ Pattern  │◀─────────────│  Trace   │◀──────┘    │
│             └──────────┘               └──────────┘            │
│                                                                 │
└─────────────────────────────────────────────────────────────────┘
```

## Architecture

### Directory Structure Mapping

```
~/.kiro/                          ~/.kgents/
├── argv.json                     ├── config.yaml
├── extensions/                   ├── data/
│   └── extensions.json           │   └── *.db
├── powers/                       ├── brain/
│   └── registry.json             │   └── patterns.json
├── steering/                     ├── soul/
│   └── *.md                      │   ├── soul.json
└── (workspace)                   │   ├── crystals/
    └── .kiro/                    │   └── history.json
        ├── specs/                ├── prompt-history/
        │   └── {feature}/        │   ├── checkpoints/
        │       ├── requirements  │   └── index.json
        │       ├── design.md     ├── witness.json
        │       └── tasks.md      ├── witness.log
        └── steering/             ├── telemetry.yaml
            └── *.md              └── garden/
```

### Core Components

```
┌─────────────────────────────────────────────────────────────────┐
│                    INTEGRATION LAYER                            │
│                                                                 │
│  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐             │
│  │   Spec      │  │  Steering   │  │   Power     │             │
│  │  Compiler   │  │   Syncer    │  │  Mapper     │             │
│  └──────┬──────┘  └──────┬──────┘  └──────┬──────┘             │
│         │                │                │                     │
│         ▼                ▼                ▼                     │
│  ┌─────────────────────────────────────────────────────┐       │
│  │              AGENTESE Protocol Layer                 │       │
│  │   world.* │ self.* │ concept.* │ void.* │ time.*    │       │
│  └─────────────────────────────────────────────────────┘       │
│         │                │                │                     │
│         ▼                ▼                ▼                     │
│  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐             │
│  │   Witness   │  │    Soul     │  │   Brain     │             │
│  │   System    │  │    Lens     │  │  Patterns   │             │
│  └─────────────┘  └─────────────┘  └─────────────┘             │
│                                                                 │
└─────────────────────────────────────────────────────────────────┘
```

## Components and Interfaces

### 1. Integration Service

The central coordinator that manages the bidirectional bridge.

```python
@dataclass
class IntegrationService:
    """Coordinates Kiro-kgents integration."""
    
    kiro_root: Path  # ~/.kiro or workspace .kiro/
    kgents_root: Path  # ~/.kgents
    registry: SpecRegistry
    compiler: SpecCompiler
    syncer: SteeringSyncer
    mapper: PowerMapper
    
    async def initialize(self) -> IntegrationState:
        """Discover and index both directory structures."""
        
    async def sync_spec(self, spec_path: Path) -> SyncResult:
        """Synchronize a Kiro spec with spec/ files."""
        
    async def compile_to_agentese(self, spec: KiroSpec) -> List[AgentesePath]:
        """Compile spec requirements to AGENTESE paths."""
        
    async def process_witness(self, trace: WitnessTrace) -> Optional[SpecRefinement]:
        """Process witness trace and suggest spec refinements."""
```

### 2. Spec Compiler

Transforms Kiro specs into AGENTESE paths.

```python
@dataclass
class SpecCompiler:
    """Compiles Kiro specs to AGENTESE paths."""
    
    async def compile_requirement(
        self, 
        requirement: Requirement
    ) -> List[AgentesePath]:
        """Compile a single requirement to AGENTESE paths."""
        
    async def compile_ears_pattern(
        self, 
        pattern: EarsPattern
    ) -> NodeHandler:
        """Translate EARS pattern to AGENTESE node handler."""
        
    async def verify_categorical_laws(
        self, 
        paths: List[AgentesePath]
    ) -> LawVerificationResult:
        """Verify generated paths satisfy categorical laws."""
```

### 3. Steering Syncer

Synchronizes steering files between Kiro and kgents.

```python
@dataclass
class SteeringSyncer:
    """Synchronizes steering files across contexts."""
    
    async def sync_steering(
        self, 
        source: Path, 
        target: Path
    ) -> SyncResult:
        """Sync steering file from source to target."""
        
    async def resolve_references(
        self, 
        content: str, 
        context: SteeringContext
    ) -> str:
        """Resolve #[[file:...]] references in both contexts."""
        
    async def apply_precedence(
        self, 
        configs: List[SteeringConfig]
    ) -> SteeringConfig:
        """Apply precedence: workspace > user > global."""
```

### 4. Power Mapper

Maps Kiro powers to kgents services.

```python
@dataclass
class PowerMapper:
    """Maps Kiro powers to AGENTESE paths."""
    
    async def register_power(
        self, 
        power: KiroPower
    ) -> List[AgentesePath]:
        """Register power's MCP servers as AGENTESE paths."""
        
    async def expose_tools(
        self, 
        power: KiroPower
    ) -> List[AgentesePath]:
        """Expose power tools under world.power.{name}.*"""
        
    async def verify_compatibility(
        self, 
        power: KiroPower, 
        compositions: List[AgentComposition]
    ) -> CompatibilityResult:
        """Verify power compatibility with existing compositions."""
```

### 5. Soul Lens

Personalizes spec interpretation through eigenvectors.

```python
@dataclass
class SoulLens:
    """Personalizes spec interpretation through soul eigenvectors."""
    
    eigenvectors: Dict[str, float]  # aesthetic, categorical, joy, etc.
    persona: Persona
    
    async def prioritize_requirements(
        self, 
        requirements: List[Requirement]
    ) -> List[Tuple[Requirement, float]]:
        """Apply eigenvector weights to prioritize requirements."""
        
    async def filter_implementations(
        self, 
        implementations: List[Implementation]
    ) -> List[Implementation]:
        """Filter implementations by persona preferences."""
        
    async def detect_conflicts(
        self, 
        spec: KiroSpec
    ) -> List[SoulConflict]:
        """Detect conflicts between spec and soul values."""
```

### 6. Brain Pattern Integrator

Integrates brain patterns with spec evolution.

```python
@dataclass
class BrainPatternIntegrator:
    """Integrates brain patterns with spec evolution."""
    
    async def correlate_pattern(
        self, 
        pattern: Pattern, 
        specs: List[KiroSpec]
    ) -> List[PatternCorrelation]:
        """Check if pattern relates to existing specs."""
        
    async def suggest_refinements(
        self, 
        patterns: List[Pattern]
    ) -> List[SpecRefinement]:
        """Suggest spec refinements based on patterns."""
        
    async def find_similar_specs(
        self, 
        spec: KiroSpec
    ) -> List[Tuple[KiroSpec, float]]:
        """Find similar specs for pattern suggestions."""
```

### 7. Witness Integrator

Integrates witness traces with spec validation.

```python
@dataclass
class WitnessIntegrator:
    """Integrates witness traces with spec validation."""
    
    async def capture_trace(
        self, 
        execution: AgentExecution
    ) -> WitnessTrace:
        """Capture witness trace linked to source requirement."""
        
    async def validate_compliance(
        self, 
        trace: WitnessTrace, 
        requirement: Requirement
    ) -> ComplianceResult:
        """Validate trace satisfies requirement."""
        
    async def detect_violations(
        self, 
        traces: List[WitnessTrace]
    ) -> List[Violation]:
        """Detect behavioral violations with counter-examples."""
```

## Data Models

### Spec Registry

```python
@dataclass
class SpecRegistry:
    """Unified registry mapping Kiro specs to kgents spec/ files."""
    
    entries: Dict[str, SpecEntry]
    
    @dataclass
    class SpecEntry:
        kiro_path: Path  # .kiro/specs/{feature}/
        spec_paths: List[Path]  # spec/{category}/{file}.md
        agentese_paths: List[str]  # Generated AGENTESE paths
        last_sync: datetime
        drift_status: DriftStatus
```

### Integration State

```python
@dataclass
class IntegrationState:
    """Current state of Kiro-kgents integration."""
    
    kiro_available: bool
    kgents_available: bool
    specs_synced: int
    specs_drifted: int
    steering_synced: int
    powers_registered: int
    last_sync: datetime
    errors: List[IntegrationError]
```

### Sync Result

```python
@dataclass
class SyncResult:
    """Result of a synchronization operation."""
    
    success: bool
    source: Path
    target: Path
    changes: List[Change]
    conflicts: List[Conflict]
    suggestions: List[str]
```

## Correctness Properties

*A property is a characteristic or behavior that should hold true across all valid executions of a system—essentially, a formal statement about what the system should do. Properties serve as the bridge between human-readable specifications and machine-verifiable correctness guarantees.*

### Property 1: Spec Sync Round-Trip

*For any* Kiro spec created in `.kiro/specs/`, creating a corresponding entry in `spec/` with semantic links and then reading back should produce an equivalent specification structure.

**Validates: Requirements 1.2, 8.1, 8.3**

### Property 2: Drift Detection Consistency

*For any* modification to a kgents spec file in `spec/`, the system should detect divergence from the corresponding Kiro spec and flag it for reconciliation.

**Validates: Requirements 1.3, 8.2**

### Property 3: Registry Bidirectional Consistency

*For any* spec in the unified registry, the mapping from Kiro spec to kgents spec/ files should be bidirectional and complete — following the link in either direction should return to the original.

**Validates: Requirements 1.4**

### Property 4: Compilation Traceability

*For any* Kiro spec requirement compiled to AGENTESE paths, each generated path should reference its source requirement, and following that reference should return the original requirement.

**Validates: Requirements 2.1, 2.4**

### Property 5: EARS Pattern Translation Preservation

*For any* acceptance criterion using EARS patterns, translating to an AGENTESE node handler and then extracting the pattern should produce an equivalent EARS structure.

**Validates: Requirements 2.2**

### Property 6: Glossary Term Resolution

*For any* spec that references a glossary term, the term must be defined in the AGENTESE context before the spec can be compiled.

**Validates: Requirements 2.3**

### Property 7: Breaking Change Detection

*For any* spec update that changes the signature or semantics of generated AGENTESE paths, the system should flag it as a breaking change.

**Validates: Requirements 2.5**

### Property 8: Categorical Law Preservation

*For any* AGENTESE paths generated from specs:
- Composition associativity: (f ∘ g) ∘ h = f ∘ (g ∘ h)
- Identity laws: f ∘ id = f and id ∘ f = f
- Functor laws: F(f ∘ g) = F(f) ∘ F(g) and F(id) = id

**Validates: Requirements 2.6, 13.1, 13.2, 13.3, 13.4**

### Property 9: Witness Trace Capture Completeness

*For any* agent execution of an AGENTESE path, a witness trace should be captured that:
- Links to the source requirement
- Contains execution details sufficient for debugging
- Is stored in `~/.kgents/witness.log`

**Validates: Requirements 3.1, 9.1, 9.2, 9.3, 9.5**

### Property 10: Feedback Loop Closure

*For any* complete cycle through Spec → Impl → Trace → Pattern → Refined Spec, the essential structure of the original spec should be preserved (isomorphic up to refinement).

**Validates: Requirements 3.6**

### Property 11: Soul Eigenvector Prioritization Consistency

*For any* spec and eigenvector configuration, applying eigenvector weights to prioritize requirements should produce a consistent ordering — the same inputs should always produce the same prioritization.

**Validates: Requirements 4.1, 4.2**

### Property 12: Soul Conflict Detection

*For any* spec that contains content matching soul "dislikes" (unnecessary jargon, feature creep, surveillance capitalism), the system should flag a conflict.

**Validates: Requirements 4.3, 4.4**

### Property 13: Soul Audit Trail Completeness

*For any* personalization decision made by the Soul Lens, an audit entry should exist that records the decision, its justification, and the eigenvector weights used.

**Validates: Requirements 4.6**

### Property 14: Brain Pattern Correlation

*For any* pattern captured by the brain, checking correlation with existing specs should:
- Return all specs that semantically relate to the pattern
- Flag contradictions between patterns and requirements
- Respect the holographic principle (patterns distributed, not localized)

**Validates: Requirements 5.1, 5.3, 5.5, 5.6**

### Property 15: Steering Synchronization

*For any* steering file in `.kiro/steering/`:
- It should sync to `~/.kgents/steering/` if that directory exists
- `#[[file:...]]` references should resolve in both contexts
- Precedence should be: workspace > user > global
- Conditional inclusion patterns should match correctly

**Validates: Requirements 6.1, 6.2, 6.3, 6.4, 6.5, 6.6**

### Property 16: Power Registration Completeness

*For any* installed Kiro power:
- Its MCP servers should be registered with kgents
- Its tools should be exposed as AGENTESE paths under `world.power.*`
- Invocations should capture witness traces
- Updates should verify compatibility with existing compositions

**Validates: Requirements 7.1, 7.2, 7.3, 7.5**

### Property 17: Semantic Link Integrity

*For any* semantic link using `#[[file:...]]` syntax:
- The link should be bidirectional
- Broken links should trigger repair suggestions
- Semantic search should find content in both Kiro specs and spec/ files

**Validates: Requirements 8.4, 8.5, 8.6**

### Property 18: Configuration Resolution

*For any* configuration request:
- Both `.kgents/config.yaml` and `.kiro/` settings should be checked
- Precedence should be: workspace > user > defaults
- Environment variables should override file configuration
- Changes should notify affected components
- Configuration should validate against schema

**Validates: Requirements 10.1, 10.2, 10.3, 10.4, 10.5, 10.6**

### Property 19: History Management

*For any* Kiro session:
- Relevant context should be archived to `~/.kgents/prompt-history/`
- Similar prompts should trigger historical context suggestions
- Checkpoints should support rollback
- Retention policies should be applied when history grows large
- No PII should be stored in history

**Validates: Requirements 11.1, 11.2, 11.3, 11.4, 11.5, 11.6**

### Property 20: Graceful Reconnection

*For any* component that disconnects and reconnects:
- State should be reconciled automatically
- Data integrity should be prioritized over feature availability

**Validates: Requirements 14.5, 14.6**

## Error Handling

### Error Categories

1. **Sync Errors**: Failures during spec/steering synchronization
2. **Compilation Errors**: Failures during spec-to-AGENTESE compilation
3. **Validation Errors**: Categorical law violations, schema validation failures
4. **Integration Errors**: Component unavailability, network failures
5. **Conflict Errors**: Spec drift, steering conflicts, soul conflicts

### Error Recovery Strategies

```python
@dataclass
class ErrorRecoveryStrategy:
    """Strategy for recovering from integration errors."""
    
    async def recover_sync_error(self, error: SyncError) -> RecoveryResult:
        """Recover from sync error by queuing for retry."""
        
    async def recover_compilation_error(self, error: CompilationError) -> RecoveryResult:
        """Recover from compilation error by suggesting fixes."""
        
    async def recover_validation_error(self, error: ValidationError) -> RecoveryResult:
        """Recover from validation error by generating counter-examples."""
        
    async def recover_integration_error(self, error: IntegrationError) -> RecoveryResult:
        """Recover from integration error by graceful degradation."""
```

### Graceful Degradation Matrix

| Component Unavailable | Degraded Functionality | Preserved Functionality |
|----------------------|------------------------|------------------------|
| `~/.kiro` | No IDE-level specs | kgents-only operation |
| `~/.kgents` | No agent state | Kiro-only operation |
| Network | No remote sync | Local operation with queue |
| Brain | No pattern suggestions | Direct spec compilation |
| Soul | No personalization | Default prioritization |
| Witness | No trace capture | Execution without observability |

## Testing Strategy

### Dual Testing Approach

The system uses both unit tests and property-based tests:

- **Unit tests**: Verify specific examples, edge cases, and error conditions
- **Property tests**: Verify universal properties across all inputs using Hypothesis

### Property-Based Testing Configuration

- **Framework**: Hypothesis (Python)
- **Minimum iterations**: 100 per property test
- **Tag format**: `**Feature: kiro-kgents-integration, Property {number}: {property_text}**`

### Test Categories

1. **Sync Tests**: Verify bidirectional synchronization
2. **Compilation Tests**: Verify spec-to-AGENTESE compilation
3. **Validation Tests**: Verify categorical law preservation
4. **Integration Tests**: Verify component interaction
5. **Degradation Tests**: Verify graceful degradation

### Example Property Test

```python
from hypothesis import given, strategies as st

@given(st.builds(KiroSpec, ...))
def test_spec_sync_round_trip(spec: KiroSpec):
    """
    **Feature: kiro-kgents-integration, Property 1: Spec Sync Round-Trip**
    **Validates: Requirements 1.2, 8.1, 8.3**
    """
    # Create spec in .kiro/specs/
    kiro_path = create_kiro_spec(spec)
    
    # Sync to spec/
    sync_result = integration_service.sync_spec(kiro_path)
    assert sync_result.success
    
    # Read back from spec/
    spec_paths = sync_result.target_paths
    reconstructed = read_spec_from_paths(spec_paths)
    
    # Verify equivalence
    assert spec.is_equivalent_to(reconstructed)
```

## Semantic Linking Strategy

All Kiro specs MUST maintain semantic links with `spec/` files:

### Link Format

```markdown
<!-- In .kiro/specs/{feature}/requirements.md -->
**Semantic Links:**
- #[[file:spec/{category}/{feature}.md]]
- #[[file:spec/principles.md]] (for principle references)
```

### Sync Rules

1. **Creation**: When a Kiro spec is created, create/update corresponding `spec/` files
2. **Modification**: When either side is modified, detect drift and flag for reconciliation
3. **Deletion**: When a Kiro spec is deleted, archive (don't delete) corresponding `spec/` files
4. **Conflict**: When both sides are modified, require human resolution

### Verification

The system continuously verifies semantic link integrity:

```python
async def verify_semantic_links(spec: KiroSpec) -> LinkVerificationResult:
    """Verify all semantic links are valid and bidirectional."""
    for link in spec.semantic_links:
        target = resolve_link(link)
        if not target.exists():
            yield BrokenLink(link, suggestion=suggest_repair(link))
        elif not has_backlink(target, spec):
            yield MissingBacklink(target, spec)
```

