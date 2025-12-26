# Run 001 - Archive Manifest

| Field | Value |
|-------|-------|
| Timestamp | 2025-12-26T18:00:00Z |
| Git SHA | cf2543d3e45ad80e (checkpoint from CLAUDE.md) |
| Status | Initial generation |
| PROTO_SPEC Version | 1.0 |

## Reason for Generation

Initial implementation of the wasm-survivors-witnessed-run-lab pilot following the witnessed-regeneration protocol. This pilot validates the Galois Loss theory by applying drift detection to game runs.

## Core Theory Being Validated

**Galois Loss predicts drift**: The run is the proof. The build is the claim. The ghost is the road not taken.

Key formulas:
- L(P) = d(P, C(R(P))) - Galois loss measures semantic distance after restructure/reconstitute
- Super-additive loss indicates contradiction: L(A U B) > L(A) + L(B) + tau

## Laws to Implement

1. **L1 Run Coherence Law**: Every major build shift must be marked and justified
2. **L2 Build Drift Law**: If Galois loss exceeds threshold, surface the drift
3. **L3 Ghost Commitment Law**: Unchosen upgrades recorded as ghost alternatives
4. **L4 Risk Transparency Law**: High-risk choices marked BEFORE effects resolve
5. **L5 Proof Compression Law**: Run crystal reduces trace while preserving causal rationale

## Qualitative Assertions to Validate

- **QA-1**: Game must feel FASTER because witnessing reduces indecision
- **QA-2**: Players feel style is SEEN, not judged
- **QA-3**: Failure runs produce CLEARER crystals than success runs
- **QA-4**: Ghost layer feels like alternate timeline, not error log

## Anti-Success Patterns to Avoid

- Surveillance creep (player notices latency)
- Judgment leakage (compass feels punitive)
- Highlight theater (crystals = cool moments, not proofs)
- Ghost-as-error (unchosen paths feel like mistakes)
- Speed tax (any perceptible slowdown)

## kgents Integrations Required

| Primitive | Source | Role |
|-----------|--------|------|
| Mark | services/witness/mark.py | Captures micro-decisions with context |
| Crystal | services/witness/crystal.py | Compressive proof of run |
| Galois Loss | services/zero_seed/galois/ | Drift and coherence signal |
| GaloisLossResponse | shared-primitives/contracts/galois.ts | Frontend contract |
| ContradictionResponse | shared-primitives/contracts/galois.ts | Contradiction detection |

## Expected Artifacts

- [ ] MANIFEST.md (this file)
- [ ] CONTRACT_AUDIT.md (Stage 2 - contract verification)
- [ ] contracts/ (snapshot of required contracts)
- [ ] impl/ (generated implementation - if contracts GO)
- [ ] LEARNINGS.md (Stage 5 - insights from run)
- [ ] witness-marks/ (mark IDs by stage)

## Canary Success Criteria (From PROTO_SPEC)

1. Player can explain a run in under 30 seconds using crystal + trail
2. Player can name the build's core proof claim in one sentence
3. System shows at least one ghost alternative per major build pivot
4. Witness layer adds zero perceptible latency to game loop
