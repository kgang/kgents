# K-Terrarium: Kubernetes-Native Agent Physics

**Status**: Phases 1-4 Complete | **Date**: 2025-12-10

---

## The Vision

A **Terrarium**—a self-contained, observable, resource-constrained ecosystem where:

- **Isolation is physics**, not policy (container boundaries)
- **Economics are enforced**, not honored (ResourceQuotas)
- **Topology is invariant** (DNS service discovery)
- **Failures are contained** (Pod-level blast radius)

---

## What's Built (Phases 1-4)

### Foundation

```bash
kgents infra init       # Create Kind cluster (~45s, idempotent)
kgents infra status     # Show cluster state + pods
kgents infra stop       # Pause cluster
kgents infra start      # Resume cluster
kgents infra destroy    # Remove cluster
kgents infra deploy     # Deploy ping-agent POC
```

### Q-gent (Quartermaster)

Disposable code execution with graceful fallback:

```bash
kgents exec --code "print('hello')"     # Execute Python
kgents exec --code "echo hi" --lang shell
kgents exec --file script.py --timeout 60
```

- K8s Job execution when cluster available
- Subprocess fallback when not
- Security: runAsNonRoot, readOnlyRootFilesystem, no privileged

### Agent Operator

CRD-driven deployment from spec:

```bash
kgents infra crd              # Install Agent CRD
kgents infra apply b-gent     # Deploy from spec/agents/b-gent.md
kgents infra apply --all      # Deploy all agents
```

Spec frontmatter → CRD → Deployment + Service (automatic).

### Live Reload Dev Mode

Edit code, see changes immediately. No rebuild, no redeploy.

```bash
kgents dev b-gent              # Start B-gent in dev mode
kgents dev b-gent --attach     # Attach for interactive debugging
kgents dev --status            # Show dev mode status
kgents dev --stop              # Stop all dev pods
```

The tight loop:
```
save file → container detects → hot reload → output visible
     ~1s            ~1s             ~1s
```

**Implementation** (complete):
- `infra/k8s/dev_mode.py` - DevMode, DevPodSpec, file watcher
- `protocols/cli/handlers/dev.py` - CLI handler
- Volume mount `impl/claude/agents/` into dev pods
- Automatic reload on file changes via polling watcher
- Streaming logs to terminal
- `--attach` for interactive debugging shell

---

## Next: The Interaction Loop

The remaining phases shift focus from infrastructure to **developer experience**. The terrarium should feel like an extension of thought, not a deployment target.

### Phase 5: The Conversation Loop

> Talk to agents, see their state, adjust in real-time.

```bash
kgents chat b-gent             # Open conversation with B-gent
> What's your current token budget?
< I have 8,432 tokens remaining. Usage rate: 12/min.
> Increase budget to 20,000
< Budget updated. New balance: 20,000 tokens.
```

**Key Insight**: Agents should be conversational, not just API endpoints. The CLI becomes a REPL for agent interaction.

**Implementation**:
- gRPC streaming for real-time conversation
- State inspection via AGENTESE paths (`self.budget.manifest`)
- Mutation via conversation, not YAML edits
- History persistence for session continuity

### Phase 6: The Feedback Loop

> Agents observe you observing them. Mutual awareness.

```bash
kgents observe                 # Real-time dashboard
┌─────────────────────────────────────────────────────────┐
│ TERRARIUM                                    12:34:56   │
├─────────────────────────────────────────────────────────┤
│ B-gent  ████████░░  80% budget   │ Processing invoice   │
│ L-gent  ██████████ 100% memory   │ Indexing embeddings  │
│ F-gent  ██░░░░░░░░  20% CPU      │ Idle                 │
├─────────────────────────────────────────────────────────┤
│ Recent Events:                                          │
│ • B-gent requested budget increase (approved)           │
│ • L-gent triggered neurogenesis (3 new clusters)        │
│ • F-gent completed inference batch (42ms avg)           │
└─────────────────────────────────────────────────────────┘
```

**Key Insight**: O-gent (Observer) should aggregate signals from all agents into a coherent view. The developer's attention becomes a resource that agents can bid for.

**Implementation**:
- O-gent runs in `kgents-system` namespace
- Prometheus metrics from all pods
- Custom events via SemanticField
- TUI dashboard (Rich or Textual)
- Attention routing: urgent signals surface first

### Phase 7: The Learning Loop

> The terrarium remembers what worked.

```bash
kgents dream                   # Run maintenance cycle
> Analyzing last 24 hours...
> Found 3 recurring patterns:
>   1. B-gent budget exhaustion at 3pm daily
>   2. L-gent memory pressure during batch indexing
>   3. F-gent idle 80% of time
> Recommendations:
>   1. Schedule budget refresh at 2:45pm
>   2. Add memory burst allowance for L-gent
>   3. Consider scaling F-gent to 0 when idle
> Apply recommendations? [y/n]
```

**Key Insight**: LucidDreamer already exists for memory consolidation. Extend it to operational patterns. The terrarium should get smarter over time.

**Implementation**:
- Pattern detection from Prometheus time series
- Anomaly detection via Synapse surprise thresholds
- Recommendation engine (rule-based initially, ML later)
- One-click application of recommendations
- Rollback if recommendations degrade performance

---

## The Interaction Manifold

These loops compose:

```
┌──────────────────────────────────────────────────────────────┐
│                    DEVELOPER                                  │
│                        │                                      │
│    ┌──────────────────┼──────────────────┐                   │
│    │                  │                  │                   │
│    ▼                  ▼                  ▼                   │
│ ┌──────┐         ┌──────┐          ┌──────┐                 │
│ │ Edit │ ──────▶ │ Chat │ ──────▶  │Observe│                │
│ │ Code │         │Agent │          │ State │                 │
│ └──┬───┘         └──┬───┘          └──┬───┘                 │
│    │                │                  │                     │
│    ▼                ▼                  ▼                     │
│ ┌──────────────────────────────────────────┐                │
│ │              TERRARIUM                    │                │
│ │  ┌─────┐  ┌─────┐  ┌─────┐  ┌─────┐     │                │
│ │  │B-gent│  │L-gent│  │F-gent│  │O-gent│    │                │
│ │  └─────┘  └─────┘  └─────┘  └─────┘     │                │
│ └──────────────────────────────────────────┘                │
│                        │                                     │
│                        ▼                                     │
│                   ┌──────┐                                   │
│                   │Dream │ (learns patterns)                 │
│                   └──────┘                                   │
└──────────────────────────────────────────────────────────────┘
```

Every loop tightens the feedback:
- **Live Reload**: sub-second code → behavior
- **Conversation**: natural language → agent action
- **Observation**: agent state → developer awareness
- **Learning**: patterns → automated optimization

---

## Remaining Infrastructure

### B-gent Economics (deferred)

ResourceQuota integration can wait. The honor system works for now. Revisit when:
- Multiple developers share a terrarium
- Agents start competing for resources
- Cost optimization becomes important

### Service Mesh (deferred)

NetworkPolicy and CoreDNS configuration can wait. Direct pod-to-pod works for now. Revisit when:
- Security boundaries matter
- Multi-tenant deployments
- Production hardening

---

## Success Criteria (Revised)

### Interaction Quality

| Loop | Target Latency | Current |
|------|----------------|---------|
| Edit → See change | < 2s | ~2-3s (Phase 4 complete) |
| Question → Answer | < 1s | N/A (Phase 5 pending) |
| Event → Dashboard | < 500ms | N/A (Phase 6 pending) |
| Pattern → Recommendation | < 1 min | N/A (Phase 7 pending) |

### Developer Happiness

- "I forget I'm working with containers"
- "Talking to agents feels natural"
- "The system anticipates what I need"
- "I trust the recommendations"

### Anti-Criteria

- Latency that breaks flow state
- YAML files that need manual editing
- Logs that require `kubectl` to read
- Recommendations that feel random

---

## The Democratization Thesis

K-Terrarium proves that Kubernetes—historically requiring weeks to learn—is now at everyone's fingertips. An AI agent that understands the spec can:

1. Bootstrap a local cluster
2. Write custom resource definitions
3. Deploy operators
4. Debug networking issues
5. Optimize resource allocation

All in a single session.

This isn't AI replacing expertise. It's AI **compressing the path to capability**. The spec becomes not just documentation, but democratization.

*"A universe in a bottle. Shake well before observing."*
