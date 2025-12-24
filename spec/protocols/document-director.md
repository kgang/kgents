# Document Director Protocol

> *"Specs become code. Code becomes evidence. Evidence feeds back to specs."*

The Document Director is a generalization of the Spec Ledger into a full-lifecycle document management system that orchestrates the journey from specification to implementation.

---

## Core Philosophy

```
Upload → Analyze → Annotate → Generate → Execute → Capture → Verify
   ↑                                                           ↓
   └───────────────── Evidence Feedback Loop ──────────────────┘
```

**Three Laws:**
1. **Law of Sovereignty**: Every document is versioned, witnessed, and possessed (not referenced)
2. **Law of Analysis**: No document enters the system without automatic parsing and claim extraction
3. **Law of Entanglement**: Specs anticipate implementations; implementations evidence specs

---

## Document Lifecycle State Machine

```
                           ┌─────────────────────────────────────┐
                           │                                     │
                           ▼                                     │
┌──────────┐    ┌──────────────┐    ┌──────────────┐    ┌───────────────┐
│ UPLOADED │───▶│  PROCESSING  │───▶│    READY     │───▶│   EXECUTED    │
└──────────┘    └──────────────┘    └──────────────┘    └───────────────┘
     │                 │                   │                    │
     │                 │                   │                    │
     ▼                 ▼                   ▼                    ▼
  Ingest          Analyze           K-Block Write         Evidence
  Mark           Overlays           Enabled               Captured
```

### States

| State | Description | Gate Condition | Frontend UI |
|-------|-------------|----------------|-------------|
| **UPLOADED** | Entity ingested, witness mark created | None | "Ingested ✓" |
| **PROCESSING** | Analysis in progress (async) | Ingest complete | "Analyzing..." spinner |
| **READY** | Analysis complete, write enabled | Analysis complete | Full editor access |
| **EXECUTED** | Code generated and captured | Ready + prompt defined | Evidence panel visible |

### Transitions

```python
class DocumentStatus(Enum):
    UPLOADED = "uploaded"       # Ingested, not yet analyzed
    PROCESSING = "processing"   # Analysis in progress
    READY = "ready"             # Full write access enabled
    EXECUTED = "executed"       # Code generation captured
    STALE = "stale"             # Content changed, re-analysis needed
    FAILED = "failed"           # Analysis failed
```

---

## Analysis-on-Upload Pipeline

When a document is uploaded, the following happens automatically:

### Phase 1: Ingest (Synchronous)

```python
async def ingest(event: IngestEvent, author: str) -> IngestResult:
    # Law 0: No Entity Without Copy
    version = await store.store_version(path, content, ingest_mark_id)

    # Law 1: No Entity Without Witness
    birth_mark = await witness.save_mark(
        action=f"Ingested: {path}",
        reasoning="Document uploaded to sovereign store",
        tags=["ingest", f"file:{path}"],
    )

    # Set initial status
    await store.set_analysis_state(path, AnalysisState(
        status=AnalysisStatus.PENDING,
        started_at=None,
    ))

    # Queue for async analysis
    await analysis_queue.enqueue(path, priority="normal")

    return IngestResult(path=path, version=version, mark_id=birth_mark.id)
```

### Phase 2: Analysis (Asynchronous)

```python
async def analyze(path: str) -> AnalysisResult:
    # Update status
    await store.set_analysis_state(path, AnalysisState(
        status=AnalysisStatus.ANALYZING,
        started_at=datetime.now(UTC).isoformat(),
    ))

    entity = await store.get_current(path)
    content = entity.content_text

    # 1. Parse spec content
    spec_record = parse_spec_content(path, content)

    # 2. Extract references (edges)
    discovered_refs = extract_references(content)

    # 3. Create placeholders for missing refs
    placeholders = []
    for ref in discovered_refs:
        if not await store.exists(ref):
            placeholder = await create_placeholder(ref, source=path)
            placeholders.append(placeholder.path)

    # 4. Store analysis as crystal overlay
    analysis_crystal = AnalysisCrystal(
        entity_path=path,
        spec_record=spec_record.to_dict(),
        discovered_refs=discovered_refs,
        placeholder_paths=placeholders,
        claims=[c.to_dict() for c in spec_record.claims],
        status="analyzed",
        analyzed_at=datetime.now(UTC).isoformat(),
    )

    # Store in overlay (not content!)
    await store.store_overlay(path, "analysis", analysis_crystal.to_dict())

    # 5. Create analysis witness mark
    analysis_mark = await witness.save_mark(
        action=f"Analyzed: {path}",
        reasoning=f"Extracted {len(spec_record.claims)} claims, {len(discovered_refs)} refs",
        tags=["analysis", f"spec:{path}"],
    )

    # 6. Update final status
    await store.set_analysis_state(path, AnalysisState(
        status=AnalysisStatus.ANALYZED,
        completed_at=datetime.now(UTC).isoformat(),
        analysis_mark_id=analysis_mark.id,
        discovered_refs=discovered_refs,
        placeholder_paths=placeholders,
    ))

    return AnalysisResult(...)
```

---

## Crystal Overlay Schema

Analysis results are stored as typed crystals in the overlay layer:

```python
@dataclass(frozen=True)
class AnalysisCrystal:
    """Stored in .kgents/sovereign/{path}/overlay/analysis.json"""

    entity_path: str
    analyzed_at: str  # ISO timestamp
    analyzer_version: str = "v1"

    # Extracted content
    title: str
    word_count: int
    heading_count: int

    # Claims (assertions, constraints, definitions)
    claims: list[dict]  # ClaimType, subject, predicate, line

    # Relationships
    discovered_refs: list[str]      # All refs found
    implementations: list[str]      # impl/ paths
    tests: list[str]                # test paths
    spec_refs: list[str]            # other spec refs

    # Placeholders created
    placeholder_paths: list[str]

    # Anticipated implementations (entanglement)
    anticipated: list[dict]  # {path, reason, phase, owner}

    # Status tracking
    status: str  # "analyzed" | "stale" | "failed"
    error: str | None = None

ANALYSIS_SCHEMA = Schema(
    name="sovereign.analysis",
    version=1,
    contract=AnalysisCrystal,
)
```

---

## Entangled Placeholder System

Specs can **anticipate** implementations before they exist:

### Placeholder Types

```python
class PlaceholderType(Enum):
    REFERENCE = "reference"        # Simple cross-ref (auto-detected)
    ANTICIPATED = "anticipated"    # Pledged future implementation
    DEFERRED = "deferred"          # Explicitly deferred
    PROOF_OF_CONCEPT = "poc"       # Experimental
```

### Anticipated Implementation Flow

```markdown
## In spec/protocols/witness.md:

<!-- @anticipated impl/claude/services/witness/evidence.py -->
The evidence engine should implement the L-∞ to L3 ladder.
<!-- @end -->
```

Parser extracts this as:
```python
{
    "path": "impl/claude/services/witness/evidence.py",
    "type": "anticipated",
    "spec_line": 42,
    "context": "The evidence engine should implement...",
    "owner": None,
    "phase": None,
}
```

This creates an **entangled placeholder** that:
1. Appears in the graph (dashed, grayed)
2. Links back to the spec section that pledges it
3. Tracks progress: `unplanned → anticipated → in_progress → implemented`
4. When code is generated/uploaded, the link becomes bidirectional evidence

### Placeholder Resolution

```python
async def resolve_placeholder(path: str, content: bytes, source: str) -> ResolveResult:
    """Called when anticipated content is finally provided."""

    placeholder = await store.get_placeholder(path)
    if not placeholder:
        # Not a placeholder - regular ingest
        return await ingest(IngestEvent.from_content(content, path, source))

    # Resolve the placeholder
    ingest_result = await ingest(IngestEvent.from_content(content, path, source))

    # Mark resolved
    await store.resolve_placeholder(path)

    # Create evidence mark linking back to specs that anticipated this
    for spec_path in placeholder.referenced_by:
        await witness.save_mark(
            action=f"Resolved anticipated: {path}",
            reasoning=f"Implementation uploaded, spec {spec_path} now has evidence",
            tags=[
                f"spec:{spec_path}",
                "evidence:impl",
                f"file:{path}",
                "placeholder-resolved",
            ],
        )

    return ResolveResult(
        path=path,
        version=ingest_result.version,
        placeholder_resolved=True,
        linked_specs=placeholder.referenced_by,
    )
```

---

## Claude Code Execution Harness

The spec-to-code generation flow:

### Phase 1: Prompt Generation

```python
async def generate_prompt(spec_path: str) -> ExecutionPrompt:
    """Generate a Claude Code execution prompt from a spec."""

    entity = await store.get_current(spec_path)
    analysis = await store.get_overlay(spec_path, "analysis")

    # Extract implementation targets from analysis
    anticipated = analysis.get("anticipated", [])
    placeholders = analysis.get("placeholder_paths", [])

    # Build the prompt
    prompt = ExecutionPrompt(
        spec_path=spec_path,
        spec_content=entity.content_text,
        targets=[
            *[a["path"] for a in anticipated],
            *placeholders,
        ],
        context={
            "claims": analysis.get("claims", []),
            "existing_refs": analysis.get("implementations", []),
        },
    )

    # Create prompt mark (L-2 evidence)
    prompt_mark = await witness.save_mark(
        action=f"Generated prompt for: {spec_path}",
        reasoning=f"Targeting {len(prompt.targets)} implementations",
        tags=["prompt", f"spec:{spec_path}", "codegen"],
    )

    prompt.mark_id = prompt_mark.id
    return prompt
```

### Phase 2: Execution via Claude Code

```python
@dataclass
class ExecutionPrompt:
    spec_path: str
    spec_content: str
    targets: list[str]  # Paths to generate
    context: dict
    mark_id: str | None = None

    def to_claude_code_task(self) -> str:
        """Format for Claude Code execution."""
        return f"""
Implement the following specification:

# Specification: {self.spec_path}

{self.spec_content}

## Implementation Targets

Generate code for the following paths:
{chr(10).join(f"- {t}" for t in self.targets)}

## Context

Claims from spec:
{json.dumps(self.context.get("claims", []), indent=2)}

Existing implementations:
{chr(10).join(f"- {r}" for r in self.context.get("existing_refs", []))}

## Requirements

1. Follow the spec's assertions and constraints exactly
2. Use the existing codebase patterns
3. Create tests for each implementation
4. Document any deviations with reasoning
"""
```

### Phase 3: Result Capture

```python
async def capture_execution_result(
    prompt: ExecutionPrompt,
    generated_files: dict[str, str],  # path → content
    test_results: TestResults,
) -> CaptureResult:
    """Capture code generation results back into the system."""

    captured = []
    for path, content in generated_files.items():
        # Ingest the generated code
        result = await resolve_placeholder(
            path=path,
            content=content.encode("utf-8"),
            source="codegen",
        )
        captured.append(result)

        # Create L-1 TRACE evidence
        trace_mark = await witness.save_mark(
            action=f"Generated: {path}",
            reasoning=f"From spec {prompt.spec_path} via Claude Code",
            tags=[
                f"spec:{prompt.spec_path}",
                "evidence:generated",
                f"file:{path}",
                "codegen",
            ],
            context={
                "prompt_mark_id": prompt.mark_id,
                "model": "claude-opus-4",
                "temperature": 0.0,
            },
        )

        # Create L1 TEST evidence if tests passed
        if test_results.passed_for(path):
            await witness.save_mark(
                action=f"Tests passed: {path}",
                reasoning=f"Generated code passes {test_results.count_for(path)} tests",
                tags=[
                    f"spec:{prompt.spec_path}",
                    "evidence:test",
                    "evidence:pass",
                    f"file:{path}",
                ],
                proof=Proof.empirical(
                    data=f"{test_results.count_for(path)} tests pass",
                    warrant="Passing tests validate implementation correctness",
                    claim=f"{path} correctly implements {prompt.spec_path}",
                ),
            )

    return CaptureResult(
        spec_path=prompt.spec_path,
        captured=captured,
        test_results=test_results,
    )
```

---

## Document Director UI

Generalization of spec ledger into a document manager:

### Views

| View | Purpose | Components |
|------|---------|------------|
| **Dashboard** | Overview metrics + live activity | Health bar, counts, recent events |
| **Directory** | Sortable/filterable document list | Table with status, claims, evidence |
| **Detail** | Single document deep-dive | Claims, evidence, relationships, actions |
| **Preview** | Quick view without full edit | Read-only rendered content |
| **Editor** | Full K-Block edit mode | Hypergraph editor integration |

### Status Rendering

```typescript
function DocumentStatusBadge({ status }: { status: DocumentStatus }) {
  const config = {
    uploaded: { label: "Uploaded", color: "blue", icon: "↑" },
    processing: { label: "Analyzing", color: "yellow", icon: "⟳", spin: true },
    ready: { label: "Ready", color: "green", icon: "✓" },
    executed: { label: "Executed", color: "purple", icon: "⚡" },
    stale: { label: "Stale", color: "orange", icon: "!" },
    failed: { label: "Failed", color: "red", icon: "✗" },
  };

  return <Badge {...config[status]} />;
}
```

### Document Actions

| Status | Available Actions |
|--------|-------------------|
| **UPLOADED** | View, Analyze (manual trigger) |
| **PROCESSING** | View, Cancel (if taking too long) |
| **READY** | View, Edit (K-Block), Annotate, Generate Prompt |
| **EXECUTED** | View, View Evidence, Re-generate, Verify Tests |

---

## AGENTESE Interface

```python
@node(
    "concept.document",
    description="Document Director - Lifecycle management for sovereign documents",
    contracts={
        "manifest": Response(DirectorManifestResponse),
        "upload": Contract(UploadRequest, UploadResponse),
        "analyze": Contract(AnalyzeRequest, AnalyzeResponse),
        "status": Contract(StatusRequest, StatusResponse),
        "prompt": Contract(PromptRequest, PromptResponse),
        "capture": Contract(CaptureRequest, CaptureResponse),
    },
)
class DocumentDirectorNode(BaseLogosNode):
    """
    Document lifecycle orchestration.

    Aspects:
    - concept.document.manifest - List all documents with status
    - concept.document.upload - Ingest new document
    - concept.document.analyze - Trigger/re-trigger analysis
    - concept.document.status - Get document status
    - concept.document.prompt - Generate execution prompt
    - concept.document.capture - Capture execution results
    """
```

---

## REST API

```
POST /api/documents/upload         - Upload document, trigger analysis
GET  /api/documents                - List documents with status
GET  /api/documents/:path          - Get document detail + analysis
GET  /api/documents/:path/preview  - Rendered preview (read-only)
POST /api/documents/:path/analyze  - Re-trigger analysis
POST /api/documents/:path/prompt   - Generate execution prompt
POST /api/documents/:path/capture  - Capture execution results
GET  /api/documents/:path/evidence - Get evidence for document
POST /api/documents/:path/evidence - Add evidence link
```

---

## Integration Points

### Witness Crown Jewel
- Birth marks on upload
- Analysis marks on completion
- Evidence marks on code capture

### Sovereign Store
- Versioned content storage
- Overlay for analysis crystals
- Placeholder tracking

### K-Block Harness
- Edit gating based on status
- WitnessedCosmos for saves

### Evidence Engine
- L-2 PROMPT capture
- L-1 TRACE capture
- L1 TEST results
- L2 ASHC proof integration

### ASHC
- Formal verification of generated code
- Proof marks for verified implementations

---

## Events (WitnessBus)

```python
class DocumentTopics:
    UPLOADED = "document.uploaded"
    ANALYSIS_STARTED = "document.analysis.started"
    ANALYSIS_COMPLETE = "document.analysis.complete"
    ANALYSIS_FAILED = "document.analysis.failed"
    STATUS_CHANGED = "document.status.changed"
    PROMPT_GENERATED = "document.prompt.generated"
    EXECUTION_CAPTURED = "document.execution.captured"
    PLACEHOLDER_RESOLVED = "document.placeholder.resolved"
```

---

## Summary

The Document Director transforms static specs into a living development workflow:

1. **Upload** → Immediate ingest + witness
2. **Analyze** → Automatic claim extraction + placeholder creation
3. **Annotate** → Enrich with principles + anticipated implementations
4. **Generate** → Create Claude Code prompts with full context
5. **Execute** → Run prompts, capture generated code
6. **Capture** → Ingest results + create evidence links
7. **Verify** → Run tests, create proof marks
8. **Loop** → Evidence feeds back, specs become living contracts

The spec is the contract. The code is the evidence. The system witnesses all.

---

*Filed: 2025-12-23*
*Status: Design Phase*
*Author: Claude + Kent (Fused)*
