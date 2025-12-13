# Cluster-Native Runtime Migration

> *"The noun is a lie. There is only the rate of change."*
>
> Agents are morphisms that transform. The cluster is the **membrane** through
> which transformation flows. Infrastructure should be invisible—not theatrical.

**Progress**: 100% ✅ (All phases complete)

## Vision

Build a **principled** cluster-native runtime where:

1. **Morpheus Gateway** serves standard OpenAI/Anthropic API (not custom gRPC)
2. **K-gent Soul** is a library imported in-process, not a separate microservice
3. **Credentials** injected via K8s Secrets, not hostPath mounts
4. **ClaudeCLIRuntime** wrapped via Adapter pattern with concurrency control

The insight: kgents already has 90% of the infrastructure. What's missing is
**principled wiring**—not infrastructure theatrics.

---

## Critical Analysis Applied

This plan incorporates feedback from critical analysis that identified:

| Anti-Pattern | Problem | Solution |
|--------------|---------|----------|
| Subprocess per request | 200-500ms spawn latency | Adapter pattern with semaphore |
| HostPath mounts | Breaks cluster abstraction | K8s Secrets from bootstrap |
| Custom gRPC protocol | Lock-in, non-portable agents | OpenAI-compatible HTTP API |
| Soul as microservice | Network latency + failure modes | Soul as importable library |

---

## Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│                      KIND CLUSTER                                │
│                                                                  │
│  ┌──────────────────────────────────────┐    ┌──────────────┐  │
│  │        Morpheus Gateway              │    │  Terrarium   │  │
│  │                                       │    │  (Gateway)   │  │
│  │  POST /v1/chat/completions           │    │  HTTP :8080  │  │
│  │  (OpenAI-compatible schema)          │    │              │  │
│  │                                       │    │  - Mirror    │  │
│  │  Internal:                            │    │  - Purgatory │  │
│  │  - asyncio.Semaphore (concurrency)   │    │  - Observe   │  │
│  │  - ClaudeCLIAdapter                  │    └──────▲───────┘  │
│  │  - Prometheus metrics                │           │          │
│  └──────────────▲────────────────────────┘           │          │
│                 │ HTTP (standard SDK)               │ WS       │
│                 │                                    │          │
│  ┌──────────────┴────────────────────────────────────┴────────┐ │
│  │                    Agent Pods                               │ │
│  │                                                             │ │
│  │  ┌─────────────────────────────────────────────────────┐   │ │
│  │  │  Robin Pod                                          │   │ │
│  │  │                                                     │   │ │
│  │  │  import anthropic                                   │   │ │
│  │  │  client = anthropic.Client(base_url="morpheus")     │   │ │
│  │  │                                                     │   │ │
│  │  │  from kgents.soul import Soul  # LIBRARY, not RPC   │   │ │
│  │  │  soul.intercept(decision)  # Zero-latency           │   │ │
│  │  │                                                     │   │ │
│  │  │  [D-gent Sidecar] → Memory persistence              │   │ │
│  │  └─────────────────────────────────────────────────────┘   │ │
│  │                                                             │ │
│  │  ┌─────────────────┐  ┌─────────────────┐                  │ │
│  │  │  U-gent Pod     │  │  K-gent Pod     │                  │ │
│  │  │  + Soul Library │  │  (if standalone │                  │ │
│  │  │  + D-gent       │  │   needed later) │                  │ │
│  │  └─────────────────┘  └─────────────────┘                  │ │
│  └─────────────────────────────────────────────────────────────┘ │
│                                                                   │
│  ┌───────────────────────────────────────────────────────────┐   │
│  │  K8s Secrets                                               │   │
│  │  - claude-auth (config.json, credentials.json)            │   │
│  └───────────────────────────────────────────────────────────┘   │
│                                                                   │
└───────────────────────────────────────────────────────────────────┘
```

---

## Key Design Decisions

### 1. Morpheus Speaks Standard API

Morpheus serves the **OpenAI-compatible** `/v1/chat/completions` endpoint.

**Why**:
- Agents use standard `anthropic` or `openai` SDKs
- Swap backends (Claude API, vLLM, Ollama) by changing one env var
- No custom `K8sRuntime` class to maintain

```python
# Agent code - completely standard
import anthropic

client = anthropic.Anthropic(
    base_url=os.environ.get("LLM_ENDPOINT", "http://morpheus:8080"),
    api_key="not-needed-morpheus-handles-it",
)

response = client.messages.create(
    model="claude-3-sonnet",
    messages=[{"role": "user", "content": "..."}],
)
```

### 2. K-gent Soul as Library

The Soul is middleware—a functor that wraps agent decisions. Making it a
separate microservice adds latency and failure modes for no benefit.

```python
# Inside any agent
from kgents.soul import Soul, KENT_EIGENVECTORS

soul = Soul(eigenvectors=KENT_EIGENVECTORS)

# Zero-latency conscience check (in-process, no network)
result = await soul.intercept(decision_token)
if not result.handled:
    await purgatory.eject(decision_token, result.annotation)
```

The Soul's logs flow to Terrarium via the D-gent sidecar—observation without
network hops.

### 3. Credentials via K8s Secrets

**Not** hostPath mounts. Bootstrap creates Secret from host `~/.claude/`:

```bash
kubectl create secret generic claude-auth \
  --from-file=config.json=$HOME/.claude/config.json \
  --from-file=credentials.json=$HOME/.claude/credentials.json
```

**Why**:
- Works identically on Kind, EKS, GKE
- Cloud deployment: update Secret from AWS Secrets Manager
- Manifests never change between environments

### 4. ClaudeCLIAdapter with Concurrency Control

Wraps `ClaudeCLIRuntime` with semaphore for concurrency control:

```python
class ClaudeCLIAdapter:
    def __init__(self, max_concurrent: int = 3):
        self._semaphore = asyncio.Semaphore(max_concurrent)

    async def complete(self, request) -> Response:
        async with self._semaphore:
            runtime = ClaudeCLIRuntime(timeout=120.0)
            text, metadata = await runtime.raw_completion(...)
            return self._to_response(text, metadata)
```

**Future**: Keep persistent `claude` REPL open via `pexpect` for lower latency.

---

## Implementation Phases

### Phase 0: Bootstrap & Secrets

**Exit**: `kubectl get secret claude-auth` returns secret

- `scripts/cluster-bootstrap.sh` - Creates Kind cluster, installs CRDs
- `scripts/create-claude-secret.sh` - Creates Secret from `~/.claude/`

### Phase 1: Morpheus Gateway

**Exit**: `curl morpheus:8080/v1/chat/completions` returns response

- `impl/claude/infra/morpheus/server.py` - FastAPI with OpenAI schema
- `impl/claude/infra/morpheus/adapter.py` - ClaudeCLIAdapter
- `impl/claude/infra/morpheus/Dockerfile` - Image with claude CLI
- `impl/claude/infra/morpheus/k8s/` - Deployment, Service, Secret mount

### Phase 2: Soul as Library ✅

**Exit**: `from kgents.soul import Soul` works, tests pass

**Completed**:
- ✅ K-gent LLM client prefers `MorpheusLLMClient` when `MORPHEUS_URL` set
- ✅ Graceful fallback to `ClaudeLLMClient` for local dev
- ✅ `morpheus_available()` function for environment detection
- ✅ `create_llm_client(prefer_morpheus=True)` for explicit control
- ✅ 9 new integration tests in `TestMorpheusIntegration`
- ✅ All 115 K-agent tests pass

**Usage**:
```python
# In-cluster (automatic)
export MORPHEUS_URL=http://morpheus-gateway:8080/v1
llm = create_llm_client()  # Returns MorpheusLLMClient

# Local dev (automatic fallback)
unset MORPHEUS_URL
llm = create_llm_client()  # Returns ClaudeLLMClient

# Force CLI for debugging
llm = create_llm_client(prefer_morpheus=False)
```

### Phase 3: Agent Pods (Robin, U-gent)

**Exit**: `kubectl get pods -l app.kubernetes.io/part-of=kgents` shows agents

- Each agent: Dockerfile, FastAPI server, K8s manifests
- Standard `anthropic` SDK pointing to Morpheus
- Soul library imported in-process
- D-gent sidecar for persistence

### Phase 4: Terrarium Integration

**Exit**: Agents auto-register, observable via `/observe`

- Agent registration on startup
- `/invoke/{genus}` routes to agent pods
- Soul logs via D-gent sidecar to Mirror

### Phase 5: Observability

**Exit**: Grafana dashboard shows LLM latencies

- Prometheus scraping Morpheus `/metrics`
- Dashboard for request latency, queue depth, error rates

---

## What Exists (Leverage)

| Component | Status | Path |
|-----------|--------|------|
| Runtime abstraction | ✅ | `runtime/base.py`, `runtime/cli.py` |
| K8s CRDs | ✅ | `infra/k8s/crds/` |
| Operators | ✅ | `infra/k8s/operators/` |
| Terrarium | ✅ | `protocols/terrarium/` |
| Semaphores | ✅ | `agents/flux/semaphore/` |
| Soul (needs refactor) | ✅ | `agents/k/soul.py` |

---

## Principles Honored

- **Tasteful**: No infrastructure theatrics. Standard APIs.
- **Heterarchical**: Agents are portable. No lock-in to custom protocols.
- **Generative**: Spec compresses impl. Morpheus is thin adapter layer.
- **Ethical**: Soul is zero-latency middleware, not bureaucratic checkpoint.

---

## Risk Mitigations

| Risk | Mitigation |
|------|------------|
| OAuth token expiry | Document re-auth; Secret update script |
| CLI spawn latency | Semaphore limits concurrency; future warm pool |
| Soul coupling | Clean interface, dependency injection |

---

## Continuation

See: `plans/_epilogues/2025-12-12-cluster-native-runtime.md`
