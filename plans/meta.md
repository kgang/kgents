# meta.md — Mycelium

> *One insight per line. If it takes a paragraph, it's not distilled.*

**Agent Protocol**: Append atomic learnings (one line, dated). Never expand existing entries. 50-line hard cap. If overflow, prune before adding.

**Skills Protocol**: Before implementing a common task, check `plans/skills/`. After learning a novel pattern, document it there. See `plans/skills/README.md`.

## Protocol

- **Add**: One line, dated. No explanation—if unclear, delete it.
- **Prune**: Monthly. Entries that didn't resonate → delete.
- **Max**: 50 lines. Hard limit. Overflow → force prune.

---

## Learnings

```
2025-12-12  Skills are crystallized knowledge: pull before doing, push after learning
2025-12-12  Purgatory > Generator: eject state as data, not pause stack frames
2025-12-12  Mirror Protocol: observe without disturbing (zero entropy observation)
2025-12-12  Flux > Loop: streams are event-driven, not timer-driven
2025-12-12  Perturbation principle: invoke() on running flux injects, never bypasses
2025-12-12  Living Pipelines: start() returns AsyncIterator, enabling `|` composition
2025-12-12  Entropy as budget: depletion collapses to Ground, not error
2025-12-12  Genealogy enforced: concepts cannot exist ex nihilo (LineageError)
2025-12-12  Store Comonad > State Monad for context (extract/extend/duplicate)
2025-12-12  Projector is NOT a lens—compression violates Get-Put law
2025-12-12  Passive stigmergy: intensity calculated on read, not stored
2025-12-12  Cognitive probes: LLM health != HTTP 200
2025-12-12  K-gent is Governance Functor, not chatbot: invalidate violating morphisms
2025-12-12  The Four Capabilities: Gatekeeper, Fractal Expander, Holographic Constitution, Sommelier
2025-12-12  Holographic outline: change principle.md → detect drift in implementation
2025-12-11  T/U split: testing (T) vs tools (U) is categorical, not convenience
2025-12-11  OCap for trust: BypassToken is unforgeable object capability
2025-12-11  Event-sourced ledger: balance is projection, not state
2025-12-12  Symmetric lifting: every functor needs both lift() and unlift()
2025-12-12  Observation is a functor: O(f) ≅ f with pluggable sinks
2025-12-12  State threading: StateMonad.lift(agent) makes state transparent to composition
```

## Anti-Patterns (Captured Failures)

```
2025-12-12  Generator Trap: pickle can't serialize stack frames → use data ejection
2025-12-12  Head-of-line blocking: one yield shouldn't freeze the whole stream
2025-12-12  Direct WebSocket to agent: 50 observers → unbounded metabolic drain
2025-12-12  Timer-driven loops create zombies, not agents
2025-12-12  Bypassing running loops causes state schizophrenia
2025-12-11  Full ouroboros (feedback=1.0) → solipsism
2025-12-11  Context dumping: large payloads in chat history tax every turn
2025-12-12  Keyword intercept is dangerous: "delete" → "Minimalism" → auto-approve production delete
2025-12-12  Templates are fine for DORMANT/WHISPER; DIALOGUE/DEEP must use LLM
2025-12-12  Skills: 7 documented; Commands: /harden, /trace, /diff-spec, /debt for DevEx
```

## Unanswered (Parking Lot)

```
2025-12-12  Should DensityField animate at 30fps always or only when focused?
2025-12-12  How to wire Flux to existing archetypes (Consolidator, Spawner)?
2025-12-12  ModalScope: how does duplicate() map to git stash/branch?
```

---

*Lines: 32/50 | Last pruned: never*
