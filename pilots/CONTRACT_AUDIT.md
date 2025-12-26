# Contract Audit: Zero-Seed Personal Governance Lab (run-001)

> *"The interface IS the proof. Drift IS the contradiction."*

**Auditor**: Contract Auditor Agent
**Date**: 2025-12-26
**Status**: **GO** (with required actions)

---

## Executive Summary

The Zero Seed Personal Governance pilot requires TypeScript contracts for two API modules:
1. **galois.py** - Galois loss computation, contradiction detection, fixed points
2. **zero_seed.py** - Epistemic graph navigation, personal governance

Currently, **no TypeScript contracts exist** for these endpoints in `shared-primitives/src/contracts/`. All contracts must be created to satisfy CONTRACT_COHERENCE.md (L6, QA-5/6/7).

**Decision: GO** - All required contracts can be created. No blocking mismatches exist.

---

## Analysis

### 1. galois.py Response Types

| Endpoint | Python Model | TypeScript Contract | Status |
|----------|--------------|---------------------|--------|
| `POST /api/galois/loss` | `GaloisLossResponse` | MISSING | **CREATE** |
| `POST /api/galois/contradiction` | `ContradictionResponse` | MISSING | **CREATE** |
| `POST /api/galois/fixed-point` | `FixedPointResponse` | MISSING | **CREATE** |
| `POST /api/layer/assign` | `LayerAssignResponse` | MISSING | **CREATE** |

**Request Models (also needed)**:
- `GaloisLossRequest`
- `ContradictionRequest`
- `FixedPointRequest`
- `LayerAssignRequest`

### 2. zero_seed.py Response Types

| Endpoint | Python Model | TypeScript Contract | Status |
|----------|--------------|---------------------|--------|
| `GET /api/zero-seed/axioms` | `AxiomExplorerResponse` | MISSING | **CREATE** |
| `GET /api/zero-seed/proofs` | `ProofDashboardResponse` | MISSING | **CREATE** |
| `GET /api/zero-seed/health` | `GraphHealthResponse` | MISSING | **CREATE** |
| `GET /api/zero-seed/telescope` | `TelescopeResponse` | MISSING | **CREATE** |
| `POST /api/zero-seed/navigate` | `NavigateResponse` | MISSING | **CREATE** |
| `GET /api/zero-seed/nodes/{id}` | `NodeDetailResponse` | MISSING | **CREATE** |
| `GET /api/zero-seed/layers/{layer}` | `LayerNodesResponse` | MISSING | **CREATE** |
| `GET /api/zero-seed/nodes/{id}/analysis` | `NodeAnalysisResponse` | MISSING | **CREATE** |
| `POST /api/zero-seed/nodes` | `ZeroNode` | MISSING | **CREATE** |
| `PUT /api/zero-seed/nodes/{id}` | `ZeroNode` | MISSING | **CREATE** |
| `DELETE /api/zero-seed/nodes/{id}` | `{status, node_id}` | MISSING | **CREATE** |
| `POST /api/zero-seed/edges/from-mark` | `ZeroEdge` | MISSING | **CREATE** |
| `POST /api/zero-seed/discover-axioms` | `dict` (DiscoveryReport) | MISSING | **CREATE** |
| `POST /api/zero-seed/validate-axiom` | `dict` (ValidationResult) | MISSING | **CREATE** |
| `GET /api/zero-seed/constitution` | `dict` (Constitution) | MISSING | **CREATE** |
| `POST /api/zero-seed/constitution/add` | `dict` (Constitution) | MISSING | **CREATE** |
| `POST /api/zero-seed/detect-contradictions` | `dict` (ContradictionReport) | MISSING | **CREATE** |

**Shared Data Models (required)**:
- `ZeroNode`
- `ZeroEdge`
- `ToulminProof`
- `GhostAlternative`
- `ProofQuality`
- `Contradiction`
- `InstabilityIndicator`
- `GraphHealth`
- `TelescopeState`
- `GradientVector`
- `NavigationSuggestion`
- `PolicyArrow`
- `NodeLoss`
- `GaloisLossComponents`
- `AnalysisQuadrant`
- `AnalysisItem`

---

## Contract Files to Create

### File 1: `shared-primitives/src/contracts/galois.ts`

```typescript
/**
 * Galois API Contracts
 *
 * CANONICAL SOURCE OF TRUTH for Galois loss computation API.
 *
 * @layer L4 (Specification)
 * @backend protocols/api/galois.py
 * @see pilots/CONTRACT_COHERENCE.md
 */

// Request types
export interface GaloisLossRequest {
  content: string;       // 3-100,000 chars
  use_cache?: boolean;   // default: true
}

export interface ContradictionRequest {
  content_a: string;     // 3-100,000 chars
  content_b: string;     // 3-100,000 chars
  tolerance?: number;    // default: 0.1, range [0,1]
}

export interface FixedPointRequest {
  content: string;       // 3-100,000 chars
  max_iterations?: number;      // default: 7, range [1,20]
  stability_threshold?: number; // default: 0.05, range [0,1]
}

export interface LayerAssignRequest {
  content: string;       // 3-100,000 chars
}

// Response types
export interface GaloisLossResponse {
  loss: number;          // [0,1]
  method: string;        // 'llm' | 'fallback'
  metric_name: string;
  cached: boolean;
  evidence_tier: string; // 'categorical' | 'empirical' | 'aesthetic' | 'somatic'
}

export interface ContradictionResponse {
  is_contradiction: boolean;
  strength: number;           // super-additive excess
  loss_a: number;             // [0,1]
  loss_b: number;             // [0,1]
  loss_combined: number;      // [0,1]
  contradiction_type: string; // 'none' | 'weak' | 'moderate' | 'strong'
  synthesis_hint?: string;
}

export interface FixedPointResponse {
  is_fixed_point: boolean;
  is_axiom: boolean;          // loss < 0.01
  final_loss: number;         // [0,1]
  iterations_to_converge: number; // -1 if not converged
  loss_history: number[];
  stability_achieved: boolean;
}

export interface LayerAssignResponse {
  layer: number;              // 1-7
  layer_name: string;
  loss: number;               // [0,1]
  confidence: number;         // [0,1]
  loss_by_layer: Record<number, number>;
  insight: string;
  rationale: string;
}

// Invariants
export const GALOIS_LOSS_INVARIANTS = {
  'loss in range': (r: GaloisLossResponse) => r.loss >= 0 && r.loss <= 1,
  'has method': (r: GaloisLossResponse) => typeof r.method === 'string',
  'has evidence_tier': (r: GaloisLossResponse) =>
    ['categorical', 'empirical', 'aesthetic', 'somatic'].includes(r.evidence_tier),
} as const;
```

### File 2: `shared-primitives/src/contracts/zero-seed.ts`

```typescript
/**
 * Zero Seed API Contracts
 *
 * CANONICAL SOURCE OF TRUTH for Zero Seed epistemic graph API.
 *
 * @layer L4 (Specification)
 * @backend protocols/api/zero_seed.py
 * @see pilots/CONTRACT_COHERENCE.md
 */

// =============================================================================
// Core Data Models
// =============================================================================

export interface GaloisLossComponents {
  content_loss: number;
  proof_loss: number;
  edge_loss: number;
  metadata_loss: number;
  total: number;
}

export interface NodeLoss {
  node_id: string;
  loss: number;
  components: GaloisLossComponents;
  health_status: 'healthy' | 'warning' | 'critical';
}

export interface ZeroNode {
  id: string;
  path: string;
  layer: number;       // 1-7
  kind: string;
  title: string;
  content: string;
  confidence: number;  // [0,1]
  created_at: string;  // ISO timestamp
  created_by: string;
  tags: string[];
  lineage: string[];
  has_proof: boolean;
}

export interface ToulminProof {
  data: string;
  warrant: string;
  claim: string;
  backing: string;
  qualifier: string;
  rebuttals: string[];
  tier: string;
  principles: string[];
}

export interface ZeroEdge {
  id: string;
  source: string;
  target: string;
  kind: string;
  context: string;
  confidence: number;  // [0,1]
  created_at: string;
  mark_id?: string;
  proof?: ToulminProof;
  evidence_tier?: string;
}

export interface GhostAlternative {
  id: string;
  warrant: string;
  confidence: number;
  reasoning: string;
}

export interface ProofQuality {
  node_id: string;
  proof: ToulminProof;
  coherence_score: number;
  warrant_strength: number;
  backing_coverage: number;
  rebuttal_count: number;
  quality_tier: 'strong' | 'moderate' | 'weak';
  ghost_alternatives: GhostAlternative[];
}

export interface Contradiction {
  id: string;
  node_a: string;
  node_b: string;
  edge_id: string;
  description: string;
  severity: 'low' | 'medium' | 'high';
  is_resolved: boolean;
  resolution_id?: string;
}

export interface InstabilityIndicator {
  type: 'orphan' | 'weak_proof' | 'edge_drift' | 'layer_skip' | 'contradiction';
  node_id: string;
  description: string;
  severity: number;  // [0,1]
  suggested_action: string;
}

export interface GraphHealth {
  total_nodes: number;
  total_edges: number;
  by_layer: Record<number, number>;
  healthy_count: number;
  warning_count: number;
  critical_count: number;
  contradictions: Contradiction[];
  instability_indicators: InstabilityIndicator[];
  super_additive_loss_detected: boolean;
}

export interface TelescopeState {
  focal_distance: number;  // [0,1]
  focal_point?: string;
  show_loss: boolean;
  show_gradient: boolean;
  loss_threshold: number;
  visible_layers: number[];
  preferred_layer: number;
}

export interface GradientVector {
  x: number;
  y: number;
  magnitude: number;
  target_node: string;
}

export interface NavigationSuggestion {
  target: string;
  action: 'focus' | 'follow_gradient' | 'investigate';
  value_score: number;
  reasoning: string;
}

export interface PolicyArrow {
  from: string;
  to: string;
  value: number;
  is_optimal: boolean;
}

// =============================================================================
// API Response Models
// =============================================================================

export interface AxiomExplorerResponse {
  axioms: ZeroNode[];
  values: ZeroNode[];
  losses: NodeLoss[];
  total_axiom_count: number;
  total_value_count: number;
  fixed_points: string[];
}

export interface ProofDashboardResponse {
  proofs: ProofQuality[];
  average_coherence: number;
  by_quality_tier: Record<string, number>;
  needs_improvement: string[];
}

export interface GraphHealthResponse {
  health: GraphHealth;
  timestamp: string;
  trend: 'improving' | 'stable' | 'degrading';
}

export interface TelescopeResponse {
  state: TelescopeState;
  gradients: Record<string, GradientVector>;
  suggestions: NavigationSuggestion[];
  visible_nodes: ZeroNode[];
  policy_arrows: PolicyArrow[];
}

export interface NavigateResponse {
  previous?: string;
  current: string;
  loss: number;
  gradient?: GradientVector;
}

export interface NodeDetailResponse {
  node: ZeroNode;
  loss: NodeLoss;
  proof?: ToulminProof;
  incoming_edges: ZeroEdge[];
  outgoing_edges: ZeroEdge[];
  witnessed_edges: ZeroEdge[];
}

export interface LayerNodesResponse {
  nodes: ZeroNode[];
  losses: NodeLoss[];
  count: number;
}

// =============================================================================
// Analysis Models
// =============================================================================

export interface AnalysisItem {
  label: string;
  value: string;
  status: 'pass' | 'warning' | 'fail' | 'info';
}

export interface AnalysisQuadrant {
  status: 'pass' | 'issues' | 'unknown';
  summary: string;
  items: AnalysisItem[];
}

export interface NodeAnalysisResponse {
  nodeId: string;  // Note: aliased from node_id in Python
  categorical: AnalysisQuadrant;
  epistemic: AnalysisQuadrant;
  dialectical: AnalysisQuadrant;
  generative: AnalysisQuadrant;
}

// =============================================================================
// Request Models
// =============================================================================

export interface NavigateRequest {
  node_id: string;
  action: 'focus' | 'follow_gradient' | 'go_lowest_loss' | 'go_highest_loss';
}

export interface CreateWitnessedEdgeRequest {
  mark_id: string;
  source_node_id: string;
  target_node_id: string;
  context?: string;
}

export interface CreateNodeRequest {
  layer: number;  // 1-7
  title: string;
  content: string;
  lineage?: string[];
  confidence?: number;
  tags?: string[];
  created_by?: string;
}

export interface UpdateNodeRequest {
  title?: string;
  content?: string;
  confidence?: number;
  tags?: string[];
}

// =============================================================================
// Personal Governance Models
// =============================================================================

export interface DiscoveredAxiom {
  content: string;
  loss: number;
  stability: number;
  iterations: number;
  confidence: number;
}

export interface DiscoveryReport {
  discovered_axioms: DiscoveredAxiom[];
  patterns_analyzed: number;
  decisions_processed: number;
  min_loss: number;
  max_loss: number;
}

export interface ValidationResult {
  is_axiom: boolean;
  is_fixed_point: boolean;
  loss: number;
  stability: number;
  iterations: number;
  losses: number[];
}

export interface ConstitutionAxiom {
  id: string;
  content: string;
  loss: number;
  status: 'active' | 'suspended' | 'archived';
  added_at: string;
  conflicts: string[];  // IDs of conflicting axioms
}

export interface Constitution {
  id: string;
  name: string;
  axioms: ConstitutionAxiom[];
  active_count: number;
  created_at: string;
  updated_at: string;
}

export interface ConstitutionContradiction {
  axiom_a_id: string;
  axiom_b_id: string;
  strength: number;
  description: string;
}

export interface ContradictionReport {
  contradictions: ConstitutionContradiction[];
  total_axioms: number;
  pairs_checked: number;
}

// =============================================================================
// Invariants
// =============================================================================

export const ZERO_NODE_INVARIANTS = {
  'has id': (n: ZeroNode) => typeof n.id === 'string' && n.id.length > 0,
  'layer in range': (n: ZeroNode) => n.layer >= 1 && n.layer <= 7,
  'has content': (n: ZeroNode) => typeof n.content === 'string',
  'confidence in range': (n: ZeroNode) => n.confidence >= 0 && n.confidence <= 1,
  'tags is array': (n: ZeroNode) => Array.isArray(n.tags),
} as const;

export const AXIOM_EXPLORER_INVARIANTS = {
  'axioms is array': (r: AxiomExplorerResponse) => Array.isArray(r.axioms),
  'values is array': (r: AxiomExplorerResponse) => Array.isArray(r.values),
  'losses is array': (r: AxiomExplorerResponse) => Array.isArray(r.losses),
  'counts match': (r: AxiomExplorerResponse) =>
    r.total_axiom_count === r.axioms.length &&
    r.total_value_count === r.values.length,
} as const;
```

### File 3: Update `shared-primitives/src/contracts/index.ts`

```typescript
export * from './daily-lab';
export * from './galois';
export * from './zero-seed';
```

---

## Required Actions (Checklist)

### Immediate (Before Pilot Run)

- [ ] Create `shared-primitives/src/contracts/galois.ts`
- [ ] Create `shared-primitives/src/contracts/zero-seed.ts`
- [ ] Update `shared-primitives/src/contracts/index.ts` to export new modules
- [ ] Add backend contract verification tests to `protocols/api/_tests/test_galois_contracts.py`
- [ ] Add backend contract verification tests to `protocols/api/_tests/test_zero_seed_contracts.py`
- [ ] Add frontend contract verification tests (when frontend exists)

### Post-Pilot (Hardening)

- [ ] Add CI workflow check for contract drift (per CONTRACT_COHERENCE.md)
- [ ] Consider auto-generation of TypeScript from Python Pydantic models
- [ ] Add type guards and normalization functions for defensive coding

---

## Risk Assessment

| Risk | Severity | Mitigation |
|------|----------|------------|
| Contract drift during development | Medium | Add contract tests BEFORE frontend work |
| Missing fields in responses | High | Use invariants to verify all required fields |
| Type mismatches (e.g., number vs string) | High | Use strict TypeScript + runtime validation |
| Aliased fields (`nodeId` vs `node_id`) | Medium | Document aliases explicitly in contracts |

---

## Decision

**GO** - All required contracts can be created from the existing Python Pydantic models. No blocking architectural issues detected.

**Rationale**:
1. Python models are well-defined and comprehensive
2. Contract Coherence Protocol provides clear structure for contracts
3. No type system incompatibilities between Python and TypeScript
4. Existing infrastructure (`shared-primitives/`) already supports contract pattern

**Required for GO**:
- Create the two contract files listed above
- Update index.ts to export them
- Verify TypeScript compiles without errors

---

*Filed: 2025-12-26 | Witnessed by: Contract Auditor Agent | Run: zero-seed-personal-governance-lab-001*
