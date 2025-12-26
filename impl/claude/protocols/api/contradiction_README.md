# Contradiction Engine API

**Phase 4 of Zero Seed Genesis** - Super-additive loss detection and resolution.

## Philosophy

> "Surfacing, interrogating, and systematically interacting with personal beliefs, values, and contradictions is ONE OF THE MOST IMPORTANT PARTS of the system."
> — Zero Seed Grand Strategy, LAW 4

The Contradiction Engine detects contradictions between K-Blocks using **super-additive loss**:

```
Formula: strength = loss_combined - (loss_a + loss_b)
If strength > τ (threshold): contradiction detected
```

When two K-Blocks contradict, their combined Galois loss is **greater** than the sum of their individual losses. This super-additivity is the signature of contradiction.

## Endpoints

### 1. Detect Contradictions
```http
POST /api/contradictions/detect
```

**Request:**
```json
{
  "k_block_ids": ["kb-001", "kb-002", "kb-003"],
  "threshold": 0.1
}
```

**Response:**
```json
{
  "contradictions": [
    {
      "id": "contradiction_kb-001_kb-002",
      "type": "PRODUCTIVE",
      "severity": 0.35,
      "k_block_a": {
        "id": "kb-001",
        "content": "All agents should be stateless.",
        "layer": 2,
        "title": "Stateless Agents"
      },
      "k_block_b": {
        "id": "kb-002",
        "content": "Agents maintain internal state for memory.",
        "layer": 2,
        "title": "Stateful Agents"
      },
      "super_additive_loss": 0.35,
      "loss_a": 0.15,
      "loss_b": 0.15,
      "loss_combined": 0.65,
      "detected_at": "2025-12-25T12:00:00Z",
      "suggested_strategy": "SYNTHESIZE",
      "classification": {
        "type": "PRODUCTIVE",
        "strength": 0.35,
        "confidence": 0.7,
        "reasoning": "This tension could drive synthesis..."
      }
    }
  ],
  "total": 1,
  "analyzed_pairs": 3,
  "threshold": 0.1
}
```

**Note:** Analyzes all pairs using upper-triangle iteration: `n(n-1)/2` pairs for `n` K-Blocks.

---

### 2. List Contradictions
```http
GET /api/contradictions?limit=50&offset=0&type=PRODUCTIVE&min_severity=0.3
```

**Query Parameters:**
- `limit` (default: 50, max: 200) - Number of results
- `offset` (default: 0) - Pagination offset
- `type` - Filter by type: `APPARENT`, `PRODUCTIVE`, `TENSION`, `FUNDAMENTAL`
- `min_severity` - Filter by minimum severity (0-1)

**Response:**
```json
{
  "contradictions": [...],
  "total": 42,
  "has_more": true
}
```

Results are sorted by severity (highest first).

---

### 3. Get Resolution Prompt
```http
GET /api/contradictions/{contradiction_id}
```

**Response:**
```json
{
  "contradiction_id": "contradiction_kb-001_kb-002",
  "k_block_a": {...},
  "k_block_b": {...},
  "strength": 0.35,
  "classification": {...},
  "suggested_strategy": "SYNTHESIZE",
  "reasoning": "This tension could drive synthesis. Try finding a higher truth that honors both.",
  "available_strategies": [
    {
      "value": "SYNTHESIZE",
      "description": "Find a higher truth that resolves both",
      "action_verb": "Synthesize",
      "icon": "merge"
    },
    {
      "value": "SCOPE",
      "description": "Clarify that these apply in different contexts",
      "action_verb": "Scope",
      "icon": "scope"
    },
    {
      "value": "CHOOSE",
      "description": "Decide which you actually believe",
      "action_verb": "Choose",
      "icon": "check-circle"
    },
    {
      "value": "TOLERATE",
      "description": "Keep both — productive tension is valuable",
      "action_verb": "Tolerate",
      "icon": "balance"
    },
    {
      "value": "IGNORE",
      "description": "I'll think about this later",
      "action_verb": "Ignore",
      "icon": "clock"
    }
  ]
}
```

---

### 4. Apply Resolution Strategy
```http
POST /api/contradictions/{contradiction_id}/resolve
```

**Request (SYNTHESIZE):**
```json
{
  "strategy": "SYNTHESIZE",
  "new_content": "Agents use functional state management with persistent data structures."
}
```

**Request (SCOPE):**
```json
{
  "strategy": "SCOPE",
  "scope_note": "Stateless for API handlers, stateful for long-running workflows."
}
```

**Request (CHOOSE):**
```json
{
  "strategy": "CHOOSE",
  "chosen_k_block_id": "kb-001"
}
```

**Response:**
```json
{
  "contradiction_id": "contradiction_kb-001_kb-002",
  "strategy": "SYNTHESIZE",
  "resolved_at": "2025-12-25T12:05:00Z",
  "witness_mark_id": "mark-resolution-abc123",
  "new_k_block_id": "kb-synth-001",
  "outcome": {
    "strategy": "SYNTHESIZE",
    "resolved_at": "2025-12-25T12:05:00Z",
    "witness_mark": "mark-resolution-abc123",
    "new_kblock_id": "kb-synth-001"
  }
}
```

**Every resolution creates a Witness mark** for traceability.

---

### 5. Summary Statistics
```http
GET /api/contradictions/stats
```

**Response:**
```json
{
  "total": 42,
  "by_type": {
    "APPARENT": 5,
    "PRODUCTIVE": 20,
    "TENSION": 12,
    "FUNDAMENTAL": 5
  },
  "by_severity": {
    "low": 8,
    "medium": 24,
    "high": 10
  },
  "resolved_count": 30,
  "unresolved_count": 12,
  "average_strength": 0.38,
  "most_common_strategy": "SYNTHESIZE"
}
```

---

## Contradiction Types

Classified by strength (super-additive loss):

| Type | Strength Range | Description | Suggested Strategy |
|------|----------------|-------------|-------------------|
| **APPARENT** | < 0.2 | Likely different scopes/contexts | SCOPE |
| **PRODUCTIVE** | 0.2 - 0.4 | Could drive synthesis | SYNTHESIZE |
| **TENSION** | 0.4 - 0.6 | Real conflict needing attention | TOLERATE or CHOOSE |
| **FUNDAMENTAL** | ≥ 0.6 | Deep inconsistency | CHOOSE |

---

## Resolution Strategies

Five ways to resolve contradictions:

1. **SYNTHESIZE**: Create a new K-Block that resolves both
   - Produces a synthesis K-Block in layer 3 (Goals)
   - Lineage tracks both parent K-Blocks

2. **SCOPE**: Clarify these apply in different contexts
   - Adds scope notes to both K-Blocks
   - Example: "Applies to X, not Y"

3. **CHOOSE**: Decide which K-Block to keep
   - Marks one as superseded
   - Retains both for historical traceability

4. **TOLERATE**: Accept as productive tension
   - Marks contradiction as "accepted"
   - Productive tensions can drive future synthesis

5. **IGNORE**: Defer decision for later
   - Marks contradiction as "deferred"
   - Can set future review date

---

## Implementation Notes

### Current Status (Phase 4: 95% Complete)

**Backend Logic**: ✅ Complete
- Detection: `services/contradiction/detection.py`
- Classification: `services/contradiction/classification.py`
- Resolution: `services/contradiction/resolution.py`

**API Endpoints**: ✅ Complete (as of 2025-12-25)
- Mounted at `/api/contradictions`
- All 5 endpoints implemented
- 16 tests passing (unit + integration)

**Pending Work**:
- [ ] Integrate real Galois loss (currently mock)
- [ ] Persist contradictions to D-gent (currently in-memory)
- [ ] Add SSE streaming for real-time detection
- [ ] Frontend UI components

### Dependencies

- **K-Block Storage**: `services/k_block/zero_seed_storage.py`
- **Galois Loss**: `services/zero_seed/galois/galois_loss.py` (mock for now)
- **Witness Protocol**: `services/witness/` (for resolution marks)

### Testing

```bash
# Unit tests
cd impl/claude
uv run pytest protocols/api/_tests/test_contradiction.py -v

# Integration tests (requires --run-llm-tests flag)
uv run pytest protocols/api/_tests/test_contradiction_integration.py -v --run-llm-tests

# All tests
uv run pytest protocols/api/_tests/test_contradiction*.py -v --run-llm-tests
```

---

## Philosophy: The Mirror Test

> "Mirrors don't tell you to change. Mirrors show you what is."
> — Zero Seed Grand Strategy, Part II, LAW 4

The Contradiction Engine **never forces resolution**. It:
- Surfaces contradictions
- Classifies by strength
- Suggests strategies
- Respects user autonomy

The user chooses the path forward. The system witnesses the decision.

**"The proof IS the decision. The mark IS the witness."**

---

## See Also

- `spec/protocols/zero-seed1/galois.md` - Galois loss theory
- `plans/zero-seed-genesis-grand-strategy.md` - Full strategy (Part VIII)
- `services/contradiction/` - Backend implementation
- `protocols/api/witness.py` - Witness API (marks)
