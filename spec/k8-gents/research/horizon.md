# K8-gents Horizon: 10-Month Production Scale Roadmap

> **"The cluster is not a computer; it is a body. At scale, it becomes a civilization."**

This document specifies the **speculative extensions** to K8-gents for production scale, spanning a 10-month horizon. These ideas are conservatively speculative—grounded in emerging industry patterns but not yet validated in our codebase.

**Version**: 3.1-horizon
**Confidence**: Speculative (research-backed, implementation unproven)
**Dependencies**: v3.1 core features must be complete first

---

## The Production Scale Challenge

K8-gents v3.1 works for a single developer with a local Kind cluster. Production scale introduces new problems:

| Challenge | Local (v3.1) | Production |
|-----------|--------------|------------|
| Cold starts | ~2s acceptable | Unacceptable for real-time |
| Discovery | L-gent in-process | Cross-cluster federation |
| Identity | Trust local SPIFFE | Zero-trust multi-tenant |
| Observability | Terrarium TUI | Enterprise dashboards |
| Governance | T-gent reviews | Compliance, audit trails |

---

## Phase 1: Agent Mesh Foundation (Months 1-3)

### 1.1 The Agent Mesh Pattern

Based on [Solo.io's Agent Mesh](https://www.solo.io/blog/agent-mesh-for-enterprise-agents) and the [Agent Mesh integration renaissance](https://dev.to/webmethodman/the-agent-mesh-building-the-integration-layer-for-the-ai-renaissance-5io).

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                         AGENT MESH ARCHITECTURE                              │
│                                                                              │
│   ┌─────────────────────────────────────────────────────────────────────┐   │
│   │                      CONTROL PLANE                                   │   │
│   │  ┌───────────┐  ┌───────────┐  ┌───────────┐  ┌───────────┐        │   │
│   │  │ Discovery │  │ Policy    │  │ Telemetry │  │ Identity  │        │   │
│   │  │ Registry  │  │ Engine    │  │ Collector │  │ Provider  │        │   │
│   │  └───────────┘  └───────────┘  └───────────┘  └───────────┘        │   │
│   └─────────────────────────────────────────────────────────────────────┘   │
│                                    │                                         │
│                            [A2A + MCP Protocols]                            │
│                                    │                                         │
│   ┌─────────────────────────────────────────────────────────────────────┐   │
│   │                      DATA PLANE (Per-Agent Sidecar)                  │   │
│   │                                                                      │   │
│   │   Agent Pod                                                          │   │
│   │   ┌─────────────┐  ┌─────────────────────────────────────────────┐  │   │
│   │   │   Agent     │  │              Mesh Sidecar                    │  │   │
│   │   │   Logic     │◀─┤  • Semantic routing (embedding cache)       │  │   │
│   │   │             │  │  • mTLS termination (SPIFFE)                │  │   │
│   │   │             │  │  • Rate limiting (B-gent policy)            │  │   │
│   │   │             │  │  • Audit logging (N-gent trace)             │  │   │
│   │   └─────────────┘  └─────────────────────────────────────────────┘  │   │
│   └─────────────────────────────────────────────────────────────────────┘   │
└─────────────────────────────────────────────────────────────────────────────┘
```

**Why a sidecar now?** In v3.1, we rejected sidecars as overkill. At scale, the sidecar provides:
- **Embedding cache**: Don't re-embed the same capability query per request
- **Local policy enforcement**: B-gent budget checks without network hop
- **Audit trail**: Every agent interaction logged for compliance

### 1.2 Protocol Support: A2A + MCP

Based on [Google's A2A (Agent-to-Agent) protocol](https://opensource.googleblog.com/2025/11/unleashing-autonomous-ai-agents-why-kubernetes-needs-a-new-standard-for-agent-execution.html) and Anthropic's MCP.

```yaml
# Agent capability manifest (A2A format)
apiVersion: a2a.kgents.io/v1
kind: AgentCard
metadata:
  name: b-gent
spec:
  name: "Budget Agent"
  description: "Token economics and resource allocation"
  capabilities:
    - name: "check_budget"
      description: "Check remaining token budget"
      input_schema: { ... }
      output_schema: { ... }
    - name: "allocate_tokens"
      description: "Allocate tokens to a task"
      input_schema: { ... }
  mcp_tools:
    - "kgents_check_balance"
    - "kgents_allocate"
  protocols:
    - "a2a/v1"
    - "mcp/1.0"
```

**Implementation**:
- L-gent becomes the **Agent Card Registry** (like DNS for agents)
- Mesh sidecar caches Agent Cards for fast capability lookup
- Cross-cluster federation via Agent Card sync

### 1.3 Semantic Routing at Scale

Building on [Aurelio AI's Semantic Router](https://www.aurelio.ai/semantic-router) and [Red Hat's vLLM Semantic Router](https://developers.redhat.com/articles/2025/09/11/vllm-semantic-router-improving-efficiency-ai-reasoning).

```python
# impl/claude/agents/l/semantic_router_scaled.py
class ScaledSemanticRouter:
    """Production semantic routing with caching and fallback."""

    def __init__(
        self,
        registry: SemanticRegistry,
        cache: EmbeddingCache,
        fallback: str = "default-handler"
    ):
        self.registry = registry
        self.cache = cache  # Redis/Valkey cluster
        self.fallback = fallback
        self.classifier = ModernBERTClassifier()  # Fast, local classification

    async def resolve(self, query: str, context: RequestContext) -> RoutingDecision:
        """Route with caching, classification, and fallback."""

        # 1. Check hot cache (sub-ms)
        cache_key = self.cache.hash(query)
        if cached := await self.cache.get(cache_key):
            return cached

        # 2. Fast classification (is this a known pattern?)
        if known_route := self.classifier.classify(query):
            await self.cache.set(cache_key, known_route, ttl=3600)
            return known_route

        # 3. Full embedding search (slower but accurate)
        results = await self.registry.search(query, limit=3)
        if results and results[0].score > 0.8:
            decision = RoutingDecision(
                agent=results[0].agent_name,
                confidence=results[0].score,
                alternatives=[r.agent_name for r in results[1:]]
            )
            await self.cache.set(cache_key, decision, ttl=300)
            return decision

        # 4. Fallback
        return RoutingDecision(agent=self.fallback, confidence=0.0)
```

**Metrics**:
- P99 latency target: <10ms for cached routes
- P99 latency target: <100ms for embedding search
- Cache hit rate target: >80% in steady state

---

## Phase 2: SpinKube Integration (Months 4-5)

### 2.1 Wasm Nanites Reconsidered

In v3.1, we deferred Wasm as premature optimization. At production scale, the calculus changes:

| Metric | Container | SpinKube Wasm |
|--------|-----------|---------------|
| Cold start | ~2000ms | ~1ms |
| Memory footprint | ~200MB | ~2MB |
| Density | ~50 pods/node | ~5000 apps/node |

Based on [SpinKube](https://www.spinkube.dev/) achieving [75M RPS at KubeCon 2025](https://www.efficientlyconnected.com/wasm-breaks-out-at-kubecon-fermyon-akamai-push-serverless-to-75m-rps/).

### 2.2 The Hybrid Cell (Revised)

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                         HYBRID CELL ARCHITECTURE                             │
│                                                                              │
│   Agent Pod                                                                  │
│   ┌─────────────────────────────────────────────────────────────────────┐   │
│   │                                                                      │   │
│   │  ┌─────────────────┐     ┌─────────────────────────────────────────┐│   │
│   │  │    NUCLEUS      │     │              CYTOPLASM                   ││   │
│   │  │   (Container)   │     │            (SpinKube Wasm)               ││   │
│   │  │                 │     │                                          ││   │
│   │  │  • Python/LLM   │     │  ┌─────┐ ┌─────┐ ┌─────┐ ┌─────┐       ││   │
│   │  │  • Deep reason  │◀───▶│  │ rfl │ │ rfl │ │ rfl │ │ rfl │       ││   │
│   │  │  • State mgmt   │     │  │ 001 │ │ 002 │ │ 003 │ │ ... │       ││   │
│   │  │                 │     │  └─────┘ └─────┘ └─────┘ └─────┘       ││   │
│   │  │  ~2s cold start │     │                                          ││   │
│   │  │  ~200MB memory  │     │  • Reflex handlers (Rust→Wasm)          ││   │
│   │  │                 │     │  • Pheromone sensors                     ││   │
│   │  │                 │     │  • Fast routing decisions                ││   │
│   │  │                 │     │                                          ││   │
│   │  │                 │     │  ~1ms cold start, ~2MB per reflex        ││   │
│   │  └─────────────────┘     └─────────────────────────────────────────┘│   │
│   │                                                                      │   │
│   └─────────────────────────────────────────────────────────────────────┘   │
└─────────────────────────────────────────────────────────────────────────────┘
```

**When to use Wasm reflexes**:
- Pheromone sensing loops (check field every 100ms)
- Simple routing decisions (if X, call Y)
- Rate limiting enforcement
- Health checks

**When to use Container nucleus**:
- LLM inference
- Complex reasoning
- State management (D-gent)
- Any Python-only dependencies

### 2.3 Reflex Compilation (J-gent Extension)

J-gent already does JIT compilation. Extend it to target Wasm:

```python
# impl/claude/agents/j/wasm_compiler.py
class ReflexCompiler:
    """Compile agent reflexes to Wasm for fast execution."""

    async def compile_reflex(self, reflex: ReflexSpec) -> WasmBinary:
        """Compile a reflex specification to Wasm.

        Reflexes are simple condition → action rules that don't need
        full Python/LLM reasoning.
        """
        # 1. Validate reflex is simple enough for Wasm
        if not self._is_wasm_compatible(reflex):
            raise ReflexTooComplexError(
                f"Reflex {reflex.name} requires Python runtime"
            )

        # 2. Generate Rust source
        rust_src = self._reflex_to_rust(reflex)

        # 3. Compile to Wasm via cargo/wasm-pack
        wasm_binary = await self._compile_rust_to_wasm(rust_src)

        # 4. Register with SpinKube
        await self._register_spin_app(reflex.name, wasm_binary)

        return wasm_binary

    def _is_wasm_compatible(self, reflex: ReflexSpec) -> bool:
        """Check if reflex can be compiled to Wasm."""
        # No LLM calls
        # No Python-specific libraries
        # No file I/O beyond K8s API
        # No network calls except to mesh sidecar
        return (
            not reflex.requires_llm and
            not reflex.requires_python_libs and
            reflex.io_pattern in ("k8s-api", "mesh-only", "none")
        )
```

**Principle Alignment**: *Generative*. The spec (ReflexSpec) generates the implementation (Wasm binary).

---

## Phase 3: Federated Discovery (Months 6-7)

### 3.1 Cross-Cluster Agent Registry

For enterprises with multiple K8s clusters:

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                      FEDERATED AGENT DISCOVERY                               │
│                                                                              │
│   Cluster A (US-West)         Cluster B (EU)          Cluster C (APAC)      │
│   ┌─────────────────────┐    ┌─────────────────────┐ ┌─────────────────────┐│
│   │ L-gent (Primary)    │    │ L-gent (Replica)    │ │ L-gent (Replica)    ││
│   │ • Full registry     │───▶│ • Read replica      │ │ • Read replica      ││
│   │ • Writes accepted   │    │ • Local cache       │ │ • Local cache       ││
│   │                     │    │ • Async sync        │ │ • Async sync        ││
│   └─────────────────────┘    └─────────────────────┘ └─────────────────────┘│
│            │                          │                        │             │
│            └──────────────────────────┴────────────────────────┘             │
│                                    │                                         │
│                            [Gossip Protocol]                                 │
│                                    │                                         │
│   ┌─────────────────────────────────────────────────────────────────────┐   │
│   │                      GLOBAL CAPABILITY INDEX                         │   │
│   │                                                                      │   │
│   │   Query: "Who handles GDPR compliance?"                             │   │
│   │   Result: [                                                          │   │
│   │     { agent: "compliance-gent", cluster: "EU", score: 0.95 },       │   │
│   │     { agent: "legal-gent", cluster: "US-West", score: 0.78 }        │   │
│   │   ]                                                                  │   │
│   └─────────────────────────────────────────────────────────────────────┘   │
└─────────────────────────────────────────────────────────────────────────────┘
```

### 3.2 Locality-Aware Routing

```python
# impl/claude/agents/l/federated_router.py
class FederatedRouter:
    """Route requests with locality awareness."""

    async def resolve(
        self,
        query: str,
        context: RequestContext
    ) -> RoutingDecision:
        """Find best agent, preferring local cluster."""

        # 1. Search local registry first
        local_results = await self.local_registry.search(query, limit=3)

        # 2. If good local match, use it (avoid cross-cluster latency)
        if local_results and local_results[0].score > 0.85:
            return RoutingDecision(
                agent=local_results[0].agent_name,
                cluster="local",
                confidence=local_results[0].score
            )

        # 3. Search federated index
        global_results = await self.federated_index.search(
            query,
            limit=5,
            exclude_cluster=context.cluster  # Already searched local
        )

        # 4. Apply locality penalty to remote results
        scored_results = []
        for r in local_results + global_results:
            score = r.score
            if r.cluster != context.cluster:
                score *= self.locality_penalty  # e.g., 0.9
            scored_results.append((r, score))

        # 5. Return best overall
        best = max(scored_results, key=lambda x: x[1])
        return RoutingDecision(
            agent=best[0].agent_name,
            cluster=best[0].cluster,
            confidence=best[1]
        )
```

---

## Phase 4: Governance & Compliance (Months 8-9)

### 4.1 Audit Trail (N-gent Extension)

Based on [AgentField's approach to cryptographic agent identity](https://siliconangle.com/2025/12/10/agentfield-tries-fix-agentic-ais-identity-crisis-cryptographic-ids-kubernetes-style-orchestration/).

```yaml
# Audit event schema
apiVersion: audit.kgents.io/v1
kind: AgentAuditEvent
metadata:
  name: evt-2025-12-11-143052-b7d9f
spec:
  timestamp: "2025-12-11T14:30:52Z"
  agent:
    name: b-gent
    svid: "spiffe://kgents.io/agents/b-gent"  # Cryptographic identity
    cluster: us-west-1
  action:
    type: INVOKE
    target: l-gent
    method: search
    input_hash: "sha256:abc123..."  # Hash, not content (privacy)
  decision:
    outcome: ALLOWED
    policy: "default-allow"
    latency_ms: 47
  trace:
    trace_id: "4bf92f3577b34da6a3ce929d0e0e4736"
    span_id: "00f067aa0ba902b7"
```

### 4.2 Policy Engine (T-gent Extension)

```python
# impl/claude/agents/t/policy_engine.py
class PolicyEngine:
    """Evaluate agent actions against governance policies."""

    async def evaluate(
        self,
        action: AgentAction,
        context: PolicyContext
    ) -> PolicyDecision:
        """Evaluate an action against all applicable policies."""

        applicable_policies = await self.get_applicable_policies(
            agent=action.agent,
            action_type=action.type,
            target=action.target
        )

        for policy in applicable_policies:
            decision = await self._evaluate_policy(policy, action, context)
            if decision.effect == "DENY":
                return PolicyDecision(
                    allowed=False,
                    reason=f"Denied by policy: {policy.name}",
                    policy=policy.name,
                    audit_required=True
                )

        return PolicyDecision(
            allowed=True,
            policies_checked=[p.name for p in applicable_policies],
            audit_required=any(p.audit for p in applicable_policies)
        )
```

### 4.3 Compliance Reporting

```bash
# Generate compliance report
kgents compliance report --start 2025-12-01 --end 2025-12-11

# Output:
# K8-GENTS COMPLIANCE REPORT
# Period: 2025-12-01 to 2025-12-11
#
# AGENT INTERACTIONS
# Total: 1,247,892
# Cross-cluster: 12,847 (1.03%)
# Policy denials: 47 (0.004%)
#
# DATA RESIDENCY
# EU data processed in EU: 100%
# GDPR deletion requests: 3 (all completed)
#
# AUDIT TRAIL
# Events logged: 1,247,892
# Events with full trace: 1,247,892 (100%)
#
# ANOMALIES DETECTED
# Unusual access patterns: 2
# - 2025-12-05: b-gent accessed l-gent 10x normal rate
# - 2025-12-08: unknown-agent attempted access (blocked)
```

---

## Phase 5: Observability at Scale (Month 10)

### 5.1 Enterprise Dashboard

Beyond Terrarium TUI—Grafana dashboards for ops teams:

```
┌─────────────────────────────────────────────────────────────────────────────┐
│ K8-GENTS OPERATIONS DASHBOARD                              us-west-1 │ EU │ │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                             │
│  AGENT HEALTH                              SEMANTIC ROUTING                 │
│  ┌─────────────────────────────────┐      ┌─────────────────────────────┐  │
│  │ Healthy: 47/50 (94%)            │      │ Cache hit rate: 87%         │  │
│  │ Degraded: 2 (L-gent, M-gent)    │      │ P99 latency: 8ms            │  │
│  │ Failed: 1 (test-agent)          │      │ Fallback rate: 2.1%         │  │
│  └─────────────────────────────────┘      └─────────────────────────────┘  │
│                                                                             │
│  TOKEN ECONOMY (All Clusters)              PROPOSAL ACTIVITY                │
│  ┌─────────────────────────────────┐      ┌─────────────────────────────┐  │
│  │ Daily budget: 10M tokens        │      │ Pending: 3                  │  │
│  │ Used: 7.2M (72%)                │      │ Auto-merged today: 12       │  │
│  │ Projected EOD: 9.1M             │      │ Rejected: 1                 │  │
│  │ Top consumer: L-gent (34%)      │      │ Human review queue: 2       │  │
│  └─────────────────────────────────┘      └─────────────────────────────┘  │
│                                                                             │
│  CROSS-CLUSTER TRAFFIC                     ALERTS                           │
│  ┌─────────────────────────────────┐      ┌─────────────────────────────┐  │
│  │ US→EU: 1,247 req/min            │      │ ⚠ L-gent memory pressure    │  │
│  │ EU→US: 89 req/min               │      │ ⚠ Proposal backlog > 5      │  │
│  │ APAC↔*: 234 req/min             │      │ ✓ All policies passing      │  │
│  └─────────────────────────────────┘      └─────────────────────────────┘  │
│                                                                             │
└─────────────────────────────────────────────────────────────────────────────┘
```

### 5.2 Distributed Tracing

Full OpenTelemetry integration:

```python
# Every agent interaction traced
with tracer.start_as_current_span("agent.invoke") as span:
    span.set_attribute("agent.source", self.name)
    span.set_attribute("agent.target", target)
    span.set_attribute("routing.method", "semantic")
    span.set_attribute("routing.score", decision.confidence)

    result = await self._invoke_agent(target, payload)

    span.set_attribute("result.success", result.success)
    span.set_attribute("result.tokens", result.tokens_used)
```

---

## Deferred Ideas (Beyond 10 Months)

Ideas considered but not included in this roadmap:

| Idea | Why Deferred | Revisit When |
|------|--------------|--------------|
| **Full Active Inference** | Requires deeper research; current surprise metrics sufficient | Year 2 |
| **Agent Dreaming** | Fascinating but not production-critical | Year 2 |
| **Cross-org Federation** | Trust model too complex | Multi-tenant proven |
| **Custom Scheduler** | Pod Priority still sufficient at scale | >1000 agents/cluster |
| **FUSE Filesystem** | MCP + Ghost sufficient | Never (architectural dead-end) |

---

## Implementation Dependencies

```
Month 1-3: Agent Mesh
├── Requires: v3.1 complete (Semantic Router, Proposal CRD, MCP)
├── New: Mesh sidecar, A2A protocol, embedding cache
└── Risk: Medium (new infrastructure component)

Month 4-5: SpinKube
├── Requires: Agent Mesh (sidecar for Wasm dispatch)
├── New: Reflex compiler, Spin integration
└── Risk: High (new runtime, Rust expertise needed)

Month 6-7: Federation
├── Requires: Agent Mesh (for cross-cluster routing)
├── New: Gossip protocol, global index
└── Risk: Medium (distributed systems complexity)

Month 8-9: Governance
├── Requires: Federation (for global audit)
├── New: Policy engine, compliance reporting
└── Risk: Low (builds on existing T-gent)

Month 10: Observability
├── Requires: All above (for full visibility)
├── New: Grafana dashboards, full OTel
└── Risk: Low (integration work)
```

---

## Principle Alignment

| Principle | Horizon Manifestation |
|-----------|----------------------|
| **Tasteful** | Five focused phases, not ten sprawling ones |
| **Curated** | Explicit "deferred" section for ideas that didn't make the cut |
| **Ethical** | Compliance and audit trails are first-class |
| **Joy-Inducing** | Terrarium TUI evolves, doesn't get replaced by boring dashboards |
| **Composable** | Agent Mesh enables composition across clusters |
| **Heterarchical** | Federation has no central authority; gossip protocol |
| **Generative** | RefleSpec → Wasm binary; this spec → implementation |

---

## Risk Assessment

| Risk | Likelihood | Impact | Mitigation |
|------|------------|--------|------------|
| SpinKube immaturity | Medium | High | Phase 2 is optional; can skip if unstable |
| A2A protocol changes | Medium | Medium | Abstract behind AgentCard CRD |
| Federation complexity | High | Medium | Start with 2 clusters, not N |
| Rust expertise gap | High | High | Hire or partner; don't do Wasm in-house |
| Scope creep | High | High | This document is the scope; reject additions |

---

## Sources

- [SpinKube - Wasm on Kubernetes](https://www.spinkube.dev/)
- [Fermyon Wasm Functions GA at KubeCon 2025](https://www.efficientlyconnected.com/wasm-breaks-out-at-kubecon-fermyon-akamai-push-serverless-to-75m-rps/)
- [Solo.io Agent Mesh](https://www.solo.io/blog/agent-mesh-for-enterprise-agents)
- [Aurelio AI Semantic Router](https://www.aurelio.ai/semantic-router)
- [Red Hat vLLM Semantic Router](https://developers.redhat.com/articles/2025/09/11/vllm-semantic-router-improving-efficiency-ai-reasoning)
- [Google Agent Sandbox / A2A Protocol](https://opensource.googleblog.com/2025/11/unleashing-autonomous-ai-agents-why-kubernetes-needs-a-new-standard-for-agent-execution.html)
- [Kagent CNCF Sandbox](https://kagent.dev/)
- [AgentField Cryptographic Identity](https://siliconangle.com/2025/12/10/agentfield-tries-fix-agentic-ais-identity-crisis-cryptographic-ids-kubernetes-style-orchestration/)

---

*"A single cell can live alone. A civilization requires infrastructure. K8-gents at scale is the infrastructure for agent civilization."*
