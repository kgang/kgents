# Ghost ↔ Substrate Galois Link (Phase 8 Delta)

> *"Ghost cache and substrate allocation are two views of the same truth."*

This delta captures the Phase 8 memory drift: the bidirectional sync between the ghost cache and substrate allocations. The sync is a **Galois connection**:

- **floor ⊣ ceiling**: allocation → ghost (floor), ghost → allocation (ceiling)
- **Law**: `floor(ceiling(a)) ≅ a` up to serialization fidelity
- **Minimal Output**: ghost entries carry metadata only (no content payloads)

## Handles
- `self.memory.ghost_link.floor[law_check=true]`: allocation → ghost projection
- `self.memory.ghost_link.ceiling[law_check=true]`: ghost access → allocation touch
- `time.memory.sync_span`: observability span for each sync step
- `concept.memory.galois_link.verify`: law check on floor ∘ ceiling ≅ id

## Invariants
1) **Coherence**: Every allocation with `lifecycle.ttl` has a matching ghost key; ghost invalidation removes the key.  
2) **Non-lossy metadata**: Ghost entries MUST NOT store full content; only `concept_id`, `agent_id`, type, timestamps, namespace, sync_source.  
3) **Order**: Invalidate ghost → THEN reap allocation. Reverse order is a violation.  
4) **Law checks**: `law_check=true` emits `law: "galois_link"`, `result: pass|fail`, `locus: ghost_key`, `allocation_id`, `concept_id`. Failures surface to Law Enforcer dash.

## Observability (Spans/Metrics)
- Spans: `m.ghost_sync.store`, `m.ghost_sync.access`, `m.ghost_sync.invalidate`
  - Payload: `{agent_id, concept_id, ghost_key, namespace, ttl_ms, success, reason, latency_ms, law_check}`  
  - Failure propagation: mark `success=false`, emit `ghost_sync.error` metric, schedule reconciliation.
- Metrics: `ghost_sync.events_total{event_type}`, `ghost_sync.failures_total{event_type}`, `ghost_sync.drift_ms` (lag between ghost touch and allocation access).

## Failure Handling
- Ghost write failure MUST NOT roll back allocation persistence; record event with `success=false` + reason, emit span + metric, and enqueue reconciliation.  
- Missing allocation on ghost access records `success=false`, emits law check `result=fail` (ceiling missing floor).  
- Invalidation best-effort; failures keep event trail for observability.

## Success Criteria
- Spec law recorded; spans + metrics defined; failure pathways explicit.  
- Docs updated in `docs/impl-guide.md` (or `docs/cognitive-loom-implementation.md`) to mirror protocol.  
- Law Enforcer observes `law_check` payloads; Observability Engineer can trace sync drift.
