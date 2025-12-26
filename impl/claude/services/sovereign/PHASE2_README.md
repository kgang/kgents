# Phase 2: Zero Seed Genesis Grand Strategy

**Implementation Date**: 2025-12-25
**Status**: Complete
**Reference**: `plans/zero-seed-genesis-grand-strategy.md` (Phase 2)

---

## Overview

This implementation provides the Sovereign Uploads and File Explorer backend for the Zero Seed Genesis Grand Strategy. It enables users to stage files in `uploads/`, analyze them for integration, and move them into the kgents cosmos with full witnessing and edge discovery.

---

## Architecture

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                    SOVEREIGN UPLOADS ARCHITECTURE                            │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                             │
│  uploads.py         →  Upload staging & file explorer                       │
│  integration.py     →  9-step integration protocol                          │
│  splitting.py       →  K-Block splitting heuristics                         │
│                                                                             │
│  Flow:                                                                      │
│    1. User drops file into uploads/                                         │
│    2. UploadService scans and returns staged files                          │
│    3. User initiates integration (moves file to destination)                │
│    4. IntegrationService executes 9-step protocol                           │
│    5. SplittingService analyzes for multi-K-Block suggestion                │
│    6. File enters cosmos with full witness trail                            │
│                                                                             │
└─────────────────────────────────────────────────────────────────────────────┘
```

---

## Components

### 1. `uploads.py` - Upload Staging & File Explorer

**Purpose**: Manage the `uploads/` staging area and provide file tree exploration.

**Key Classes**:
- `UploadedFile` - A file in the uploads/ staging area
- `FileExplorerEntry` - A file or directory in the file explorer
- `UploadService` - Service for managing uploads/
- `FileExplorerService` - Service for exploring the kgents file tree

**Key Functions**:
- `scan_uploads()` - Scan uploads/ directory and return all staged files
- `get_upload()` - Get a specific uploaded file by path
- `get_tree()` - Get the complete directory tree
- `get_directory()` - Get a specific directory entry

**Example Usage**:
```python
from services.sovereign.uploads import get_upload_service

service = get_upload_service()
uploads = await service.scan_uploads()

for upload in uploads:
    print(f"{upload.path}: {upload.size_bytes} bytes, {upload.status}")
```

---

### 2. `integration.py` - Integration Protocol

**Purpose**: Execute the 9-step integration protocol when moving files from uploads/ to their destination.

**The 9 Steps**:
1. Create witness mark for the integration
2. Analyze content for layer assignment (use Galois)
3. Create K-Block (one doc = one K-Block heuristic)
4. Discover edges (what does this relate to?)
5. Attach portal tokens
6. Identify concepts (axioms, constructs)
7. Check for contradictions with existing content
8. Move file to destination
9. Add to cosmos feed

**Key Classes**:
- `DiscoveredEdge` - An edge discovered during integration
- `PortalToken` - A portal token extracted from content (e.g., `[[concept.entity]]`)
- `IdentifiedConcept` - A concept identified in the content (axiom, law, principle)
- `Contradiction` - A contradiction detected during integration
- `IntegrationResult` - Result of integrating a file
- `IntegrationService` - Service for integrating files

**Example Usage**:
```python
from services.sovereign.integration import get_integration_service

service = get_integration_service()
result = await service.integrate(
    source_path="my-doc.md",  # In uploads/
    destination_path="spec/protocols/my-doc.md"
)

if result.success:
    print(f"Integration complete!")
    print(f"  K-Block ID: {result.kblock_id}")
    print(f"  Layer: {result.layer}")
    print(f"  Edges discovered: {len(result.edges)}")
    print(f"  Contradictions: {len(result.contradictions)}")
```

---

### 3. `splitting.py` - K-Block Splitting Heuristics

**Purpose**: Detect when a single document should be split into multiple K-Blocks.

**The 4 Heuristics**:
1. **Multiple distinct concepts** - Too many headings at the same level
2. **Internal contradiction** - Sections contradict each other (super-additive loss)
3. **Size threshold** - Document exceeds 5000 tokens
4. **Layer mixing** - Mixing L3 goals with L5 implementations

**Key Classes**:
- `SplitReasonType` - Enum of split reason types
- `SplitReason` - A reason to split a document
- `SplitSection` - A section that would become its own K-Block
- `SplitPlan` - A plan for how to split a document
- `SplitRecommendation` - A recommendation to split a document
- `SplittingService` - Service for analyzing documents and recommending splits

**Example Usage**:
```python
from services.sovereign.splitting import get_splitting_service

service = get_splitting_service()
recommendation = await service.analyze_for_splitting(
    content=file_content,
    path="spec/my-large-doc.md",
    galois_loss=0.6
)

if recommendation.should_split:
    print(f"Split recommended!")
    print(f"  Reasons: {len(recommendation.reasons)}")
    for reason in recommendation.reasons:
        print(f"    - {reason.description} (confidence: {reason.confidence:.2f})")

    if recommendation.plan:
        print(f"  Proposed split into {recommendation.plan.num_sections} sections:")
        for section, path in zip(recommendation.plan.sections, recommendation.plan.recommended_paths):
            print(f"    - {section.title} → {path}")
```

---

## Directory Structure Supported

```
/                           # Root of user's kgents space
├── uploads/                # SOVEREIGN STAGING (unmapped)
│   └── [incoming files]    # Await integration
│
├── spec/                   # SPECIFICATIONS (L3-L4)
│   ├── agents/             # Agent specifications
│   ├── protocols/          # Protocol specifications
│   └── principles/         # Principle specifications
│
├── impl/                   # IMPLEMENTATION (L5)
│   └── [code files]        # Mapped to K-Blocks
│
├── docs/                   # DOCUMENTATION (L6-L7)
│   ├── skills/             # How-to guides
│   └── theory/             # Theoretical foundations
│
└── .kgents/                # SYSTEM (hidden)
    ├── cosmos.db           # Append-only log
    ├── feeds/              # User's feed configurations
    └── zero-seed.json      # Genesis (readonly)
```

---

## Integration Points

### With K-Block Service

The integration service creates K-Blocks for markdown files during integration:

```python
# Step 3 in integration.py
kblock_id = await self._create_kblock(
    path=destination_path,
    content=content,
    layer=layer,
    galois_loss=galois_loss
)
```

**TODO**: Integrate with real K-Block service (`services/k_block/`)

### With Galois Service

The integration service uses Galois for layer assignment and contradiction detection:

```python
# Step 2 in integration.py
layer, galois_loss = await self._assign_layer(content)

# Step 7 in integration.py
contradictions = await self._find_contradictions(content, path)
```

**TODO**: Integrate with real Galois service (`services/zero_seed/galois/`)

### With Witness Service

Every integration creates a witness mark:

```python
# Step 1 in integration.py
witness_mark_id = await self._create_witness_mark(
    source_path, destination_path, content
)
```

**TODO**: Integrate with real witness service (`services/witness/`)

---

## Design Philosophy

### Linear Adaptation

> *"The system adapts to user wants and needs. The system does NOT change behavior against user will."*

**Key Principles**:
- Splitting is **suggested**, never forced
- Contradictions are **surfaced**, not blocked
- Integration **guides**, doesn't dictate
- User approval required for all major operations

### Evidence-Driven

Every recommendation is backed by evidence:

```python
SplitReason(
    type=SplitReasonType.INTERNAL_CONTRADICTION,
    description="Sections contradict each other (loss: 0.42)",
    confidence=0.9,
    evidence={
        "internal_loss": 0.42,
        "threshold": 0.4,
    }
)
```

### Witness Everything

Every file crossing the membrane is witnessed:

```python
# Integration creates marks for:
# - The integration event itself
# - Each discovered edge
# - Each identified concept
# - Each detected contradiction
```

---

## Current Status

### ✅ Complete

- [x] `uploads.py` - Upload staging and file explorer
- [x] `integration.py` - 9-step integration protocol
- [x] `splitting.py` - K-Block splitting heuristics
- [x] All dataclasses and types defined
- [x] Service factory patterns implemented
- [x] Basic tests written

### 🚧 TODO (Integration Points)

- [ ] Integrate with K-Block service for real K-Block creation
- [ ] Integrate with Galois service for real loss computation
- [ ] Integrate with witness service for real mark creation
- [ ] Integrate with cosmos feed service for feed updates
- [ ] Add edge discovery using existing SpecParser
- [ ] Add portal token resolution
- [ ] Add concept identification using LLM

### 📋 TODO (UI/UX)

- [ ] Create React components for file explorer
- [ ] Create React components for upload zone
- [ ] Create React components for integration dialog
- [ ] Create React components for split recommendation UI
- [ ] Add SSE streaming for real-time integration progress

---

## Testing

Run the Phase 2 tests:

```bash
cd impl/claude
pytest services/sovereign/_tests/test_phase2_uploads.py -v
```

Expected output:
```
test_uploaded_file_creation PASSED
test_file_explorer_entry_creation PASSED
test_integration_result_creation PASSED
test_split_recommendation_creation PASSED
test_upload_service_factory PASSED
test_integration_service_factory PASSED
test_splitting_service_factory PASSED
test_splitting_service_extract_sections PASSED
test_integration_layer_assignment PASSED
test_splitting_contradiction_detection PASSED
```

---

## Next Steps

1. **Complete Integration Points** - Wire up K-Block, Galois, and witness services
2. **Build Frontend** - Create React components for the upload and integration UX
3. **Add AGENTESE Nodes** - Expose services via AGENTESE protocol
4. **Implement Feed Integration** - Add integrated K-Blocks to cosmos feed
5. **Add Real-Time Updates** - SSE streaming for integration progress

---

## Philosophy

> *"Moving a file is not a file operation. It's an epistemological event.
> The file crosses from potential to actual, from unmapped to witnessed."*

Every file in `uploads/` is a seed waiting to grow. Integration is the act of planting that seed in the garden of the cosmos. Splitting is the gardener's suggestion: "This tree might flourish better as two saplings."

The system never forces. It suggests, shows evidence, and trusts the user to decide.

This is the Linear philosophy applied to knowledge management.

---

**End of Phase 2 Implementation**

*"The seed IS the garden."*
