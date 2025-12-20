# Operational Principles

> *Tactical guidance for day-to-day implementation work.*

---

## Transparent Infrastructure

> Infrastructure should communicate what it's doing. Users should never wonder "what just happened?"

This principle applies to all infrastructure work: CLI startup, database initialization, background processes, maintenance tasks.

### The Communication Hierarchy

| Level | When | Message Style | Example |
|-------|------|---------------|---------|
| **First Run** | Infrastructure created | Celebratory, informative | `[kgents] First run! Created cortex at ~/.local/share/kgents/` |
| **Warning** | Degraded mode | Yellow, actionable | `[kgents] Running in DB-less mode. Database will be created...` |
| **Verbose** | `--verbose/-v` flag | Full details | `[cortex] Initialized: global DB | instance=36d0984c` |
| **Error** | Failure | Red, sympathetic | `[kgents] Bootstrap failed: {reason}` |
| **Silent** | Normal success | No output | (nothing) |

### Key Behaviors

1. **First-run is special**: Users should know where their data lives
2. **Degraded mode is visible**: If something isn't working, say so
3. **Normal operation is quiet**: Don't spam users with success messages
4. **Verbose mode exists**: Power users can opt into details
5. **Errors are sympathetic**: Don't just dump stack traces

**Anti-patterns**: Silent first-run that creates files without telling user; verbose output on every run (noise); error messages that just say "failed"; hiding degraded mode from users

*Zen Principle: The well-designed tool feels silent, but speaks when something important happens.*

---

## Graceful Degradation

> When the full system is unavailable, degrade gracefully. Never fail completely.

Systems should detect their environment and adapt. Q-gent exemplifies this: when Kubernetes is unavailable, it falls back to subprocess execution. The user's code still runs.

- **Feature detection over configuration**: Don't require users to specify mode
- **Transparent degradation**: Tell users when running in fallback mode
- **Functional equivalence**: Fallback should produce same results (within limits)

| System | Primary | Fallback |
|--------|---------|----------|
| Code execution | K8s Job | Subprocess |
| Agent discovery | CoreDNS | In-process registry |
| State persistence | D-gent sidecar | SQLite in-process |

*Zen Principle: The stream finds a way around the boulder.*

---

## Spec-Driven Infrastructure

> YAML is generated, not written. The spec is the source of truth.

Infrastructure manifests should be derived from specs, not hand-crafted. When `spec/agents/b-gent.md` changes, the CRD, Deployment, and Service regenerate automatically.

```
spec/agents/*.md  →  Generator  →  K8s Manifests  →  Running Pods
```

**Anti-patterns**: Hand-editing generated YAML (will be overwritten); deployment config that diverges from spec (spec rot); infrastructure that can't be regenerated from scratch

*Zen Principle: Write the spec once, generate the infrastructure forever.*

---

## Event-Driven Streaming

> Flux > Loop: Streams are event-driven, not timer-driven.

This principle governs all agent streaming and asynchronous behavior. Agents that process continuous data should react to events, not poll on timers.

### The Three Truths

1. **Streams are event-driven**: Process events as they arrive, not on schedule
2. **Perturbation over bypass**: `invoke()` on a running flux injects into the stream, never bypasses it
3. **Streaming ≠ mutability**: Ephemeral chunks project immutable Turns; state remains coherent

### The Perturbation Principle

When a FluxAgent is **FLOWING**, calling `invoke()` doesn't bypass the stream—it **perturbs** it. The invocation becomes a high-priority event injected into the flux.

**Why?** If the agent has Symbiont memory, bypassing would cause:
- State loaded twice (race condition)
- Inconsistent updates ("schizophrenia")

Perturbation preserves **State Integrity**.

**Anti-patterns**: Timer-driven loops that poll (creates zombies); bypassing running loops (causes state schizophrenia); treating streaming output as mutable (violates immutability); generator frames that hold state (can't serialize; use Purgatory pattern)

*Zen Principle: The river doesn't ask the clock when to flow.*

---

*See also: `spec/agents/flux.md`, `docs/skills/crown-jewel-patterns.md`*
