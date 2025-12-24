# Document Director Service

> *"Specs become code. Code becomes evidence. Evidence feeds back to specs."*

The Document Director orchestrates the full lifecycle from specification to implementation, implementing the protocol defined in `spec/protocols/document-director.md`.

## Architecture

```
Upload → Analyze → Annotate → Generate → Execute → Capture → Verify
   ↑                                                           ↓
   └───────────────── Evidence Feedback Loop ──────────────────┘
```

## Components

### `types.py` - Core Data Structures

- **DocumentStatus**: Lifecycle state machine (UPLOADED → PROCESSING → READY → EXECUTED)
- **AnalysisCrystal**: Immutable analysis result stored in overlay
- **ExecutionPrompt**: Claude Code execution harness input
- **CaptureResult**: Code generation capture with evidence
- **TestResults**: Test execution results
- **DocumentTopics**: Event topics for WitnessBus

### `director.py` - Main Orchestrator

The `DocumentDirector` class composes:
- **SovereignStore**: Entity storage and versioning
- **SovereignAnalyzer**: Reference discovery and placeholders
- **Ingestor**: File ingestion with witness marks
- **WitnessPersistence**: Witness mark creation
- **WitnessSynergyBus**: Event publishing

#### Key Methods

1. **`async def analyze_deep(path, force=False) -> AnalysisCrystal`**
   - Runs basic sovereign analysis (refs, placeholders)
   - Parses spec content for claims using `parse_spec_content()`
   - Extracts anticipated implementations via `@anticipated` markers
   - Stores AnalysisCrystal in overlay/analysis_crystal.json
   - Emits ANALYSIS_COMPLETE event

2. **`async def extract_anticipated(path, content) -> list[dict]`**
   - Parses `<!-- @anticipated impl/path.py -->` markers
   - Returns list of {path, context, spec_line}
   - Creates entangled placeholders for future code

3. **`async def generate_prompt(spec_path) -> ExecutionPrompt`**
   - Gets entity and analysis crystal
   - Builds ExecutionPrompt with spec + targets + claims
   - Creates L-2 PROMPT witness mark
   - Emits PROMPT_GENERATED event

4. **`async def capture_execution(prompt, generated_files, test_results) -> CaptureResult`**
   - For each generated file: calls `resolve_placeholder()`
   - Creates L-1 TRACE evidence marks
   - If tests passed: creates L1 TEST evidence marks
   - Emits EXECUTION_CAPTURED event

5. **`async def resolve_placeholder(path, content, source) -> ResolveResult`**
   - Checks if path was a placeholder
   - Ingests content via `Ingestor.ingest()`
   - If placeholder: marks resolved + creates evidence links
   - Emits PLACEHOLDER_RESOLVED event

6. **`async def get_status(path) -> dict`**
   - Returns full status: entity info, analysis state, crystal, counts
   - Includes: claims, refs, placeholders, anticipated, implementations, tests

## Evidence Ladder

The Director creates evidence marks following the witness ladder:

- **L-2 PROMPT**: Prompt generation mark (before execution)
- **L-1 TRACE**: Generated code mark (after execution)
- **L1 TEST**: Test passing mark (validated implementation)

Each level builds on the previous, creating a causal chain.

## Event Flow

```
DocumentDirector ──publish──▶ WitnessSynergyBus ──▶ Subscribers
                                    │
                                    └─► DocumentTopics.ANALYSIS_COMPLETE
                                    └─► DocumentTopics.PROMPT_GENERATED
                                    └─► DocumentTopics.EXECUTION_CAPTURED
                                    └─► DocumentTopics.PLACEHOLDER_RESOLVED
```

## Integration Points

### Sovereign Store
- Versioned content storage
- Overlay for analysis crystals (`overlay/analysis_crystal.json`)
- Placeholder tracking and resolution

### Living Spec Analyzer
- `parse_spec_content()` for claim extraction
- SpecRecord with assertions, constraints, definitions

### Witness Crown Jewel
- Birth marks on upload
- Analysis marks on completion
- Evidence marks on code capture (PROMPT, TRACE, TEST)

### K-Block Harness
- Edit gating based on DocumentStatus
- WitnessedCosmos for saves

## Usage Example

```python
from services.director import DocumentDirector
from services.sovereign import SovereignStore
from services.witness import WitnessPersistence, get_synergy_bus

# Initialize
store = SovereignStore()
witness = WitnessPersistence()
bus = get_synergy_bus()

director = DocumentDirector(store, witness, bus)

# 1. Ingest and analyze a spec
crystal = await director.analyze_deep("spec/protocols/my-spec.md")
print(f"Found {len(crystal.claims)} claims, {len(crystal.anticipated)} anticipated")

# 2. Generate execution prompt
prompt = await director.generate_prompt("spec/protocols/my-spec.md")
print(f"Prompt targets {len(prompt.targets)} implementations")

# 3. (Execute with Claude Code - external step)
generated_files = {
    "impl/my_service.py": "# Generated code...",
}
test_results = TestResults(results={
    "impl/my_service.py": {"passed": True, "count": 5},
})

# 4. Capture results
result = await director.capture_execution(prompt, generated_files, test_results)
print(f"Captured {len(result.captured)} files with {len(result.mark_ids)} evidence marks")

# 5. Get full status
status = await director.get_status("spec/protocols/my-spec.md")
print(f"Status: {status['analysis_status']}, {status['counts']}")
```

## Three Laws

1. **Law of Sovereignty**: Every document is versioned, witnessed, and possessed
   - All content stored in sovereign store with witness marks
   - No direct filesystem access - everything flows through ingest

2. **Law of Analysis**: No document enters without automatic parsing and claim extraction
   - Every upload triggers deep analysis
   - AnalysisCrystal captures all derived data

3. **Law of Entanglement**: Specs anticipate implementations; implementations evidence specs
   - `@anticipated` markers create entangled placeholders
   - When code is uploaded, bidirectional evidence links are created
   - The spec-impl relationship is witnessed and traced

## Next Steps

- [ ] Create AGENTESE node interface (`node.py`)
- [ ] Build REST API endpoints
- [ ] Implement UI components (Dashboard, Directory, Detail views)
- [ ] Add async analysis queue for long-running operations
- [ ] Integrate with K-Block editor for status-based gating

---

*Created: 2025-12-23*
*See: spec/protocols/document-director.md*
