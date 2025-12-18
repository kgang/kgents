# Skill: SaaS Infrastructure Patterns

> Operational patterns for production-grade SaaS infrastructure

**Difficulty**: Medium
**Prerequisites**: K8s basics, FastAPI, async Python
**Files Touched**: `protocols/api/`, `protocols/billing/`, `infra/k8s/manifests/`

---

## Overview

This skill documents patterns learned from building kgents SaaS infrastructure across 11 phases. These patterns apply to any production API service with multi-tenancy, webhooks, and Kubernetes deployment.

---

## Pattern 1: Non-Blocking Webhook Processing

Fire-and-forget pattern for webhook ingestion that doesn't block the response.

**When to use**: External webhooks (Stripe, GitHub, etc.) where acknowledgment must be fast.

**File**: `protocols/api/webhooks.py`
**Pattern**:
```python
from asyncio import create_task

async def webhook_handler(payload: WebhookPayload) -> Response:
    # Verify signature FIRST (security-critical)
    if not verify_signature(payload):
        raise HTTPException(400, "Invalid signature")

    # Acknowledge immediately, process async
    create_task(process_webhook(payload))
    return Response(status_code=200)

async def process_webhook(payload: WebhookPayload) -> None:
    """Fire-and-forget processing with error handling."""
    try:
        await translate_and_forward(payload)
    except Exception as e:
        logger.error(f"Webhook processing failed: {e}")
        # Consider dead-letter queue for retries
```

**Key insight**: `asyncio.create_task()` returns immediately while processing continues in background.

---

## Pattern 2: Idempotency with Graceful Degradation

In-memory store for MVP, Redis for production, with automatic fallback.

**When to use**: Any operation that must not be executed twice (webhooks, payments, state transitions).

**File**: `protocols/billing/idempotency.py`
**Pattern**:
```python
from abc import ABC, abstractmethod
from datetime import timedelta

class IdempotencyStore(ABC):
    @abstractmethod
    async def check_and_set(self, key: str, ttl: timedelta) -> bool:
        """Return True if key is new (proceed), False if duplicate (skip)."""
        ...

class InMemoryIdempotencyStore(IdempotencyStore):
    """MVP: In-memory with TTL. Loses state on restart."""
    def __init__(self):
        self._seen: dict[str, float] = {}

    async def check_and_set(self, key: str, ttl: timedelta) -> bool:
        now = time.time()
        self._cleanup(now)
        if key in self._seen:
            return False  # Duplicate
        self._seen[key] = now + ttl.total_seconds()
        return True  # New

class RedisIdempotencyStore(IdempotencyStore):
    """Production: Redis with atomic SETNX."""
    async def check_and_set(self, key: str, ttl: timedelta) -> bool:
        return await self.redis.set(key, "1", nx=True, ex=int(ttl.total_seconds()))

# Factory with graceful degradation
_store: IdempotencyStore | None = None

def get_idempotency_store() -> IdempotencyStore:
    global _store
    if _store is None:
        try:
            _store = RedisIdempotencyStore()
        except Exception:
            logger.warning("Redis unavailable, using in-memory store")
            _store = InMemoryIdempotencyStore()
    return _store
```

**Key insight**: In-memory → Redis progression with TTL. Singleton caching avoids repeated connection attempts.

---

## Pattern 3: Memory Leak Detection via Latency Proxy

Use latency growth as a proxy for memory leaks in soak tests.

**When to use**: Long-running soak tests (1h, 4h, 24h) where direct memory measurement is complex.

**File**: `tests/load/saas-soak.js` (k6)
**Pattern**:
```javascript
// Track latency percentiles over time
const latencyTrend = new Trend('response_latency');

export default function() {
    const start = Date.now();
    const res = http.get(`${BASE_URL}/health`);
    latencyTrend.add(Date.now() - start);
}

// In summary, check for drift
export function handleSummary(data) {
    const p95_start = data.metrics.response_latency.values['p(95)'];
    // Compare early vs late percentiles
    // Significant growth indicates memory pressure
}
```

**Key insight**: Latency growth over time correlates with memory pressure. Simpler than direct measurement, works across languages.

---

## Pattern 4: PodDisruptionBudget for HA

Prevent all-pod eviction during node drains.

**When to use**: Any StatefulSet or Deployment with 2+ replicas where availability matters.

**File**: `infra/k8s/manifests/api/pdb.yaml`
**Pattern**:
```yaml
apiVersion: policy/v1
kind: PodDisruptionBudget
metadata:
  name: api-pdb
spec:
  minAvailable: 1  # Or use maxUnavailable: 1
  selector:
    matchLabels:
      app: kgent-api
```

**Key insight**: PDB is essential for preventing all-pod eviction during `kubectl drain`. Without it, all replicas can be evicted simultaneously.

---

## Pattern 5: Runbook URLs in Alerts

Reduce MTTR by linking alerts directly to runbook procedures.

**When to use**: Any Prometheus alerting rule.

**File**: `infra/k8s/manifests/observability/prometheus/alerting-rules.yaml`
**Pattern**:
```yaml
groups:
  - name: kgents-api
    rules:
      - alert: APIHighLatency
        expr: histogram_quantile(0.95, rate(http_request_duration_seconds_bucket[5m])) > 0.5
        for: 5m
        labels:
          severity: warning
        annotations:
          summary: "API p95 latency > 500ms"
          runbook_url: "https://docs.kgents.io/runbook#api-high-latency"
```

**Key insight**: On-call engineers click directly to procedure instead of searching. Reduces MTTR significantly.

---

## Pattern 6: 404 for Cross-Tenant Access

Return 404 (not 403) for cross-tenant resource access.

**When to use**: Any multi-tenant API where tenant isolation is enforced.

**File**: `protocols/api/sessions.py`
**Pattern**:
```python
async def get_session(session_id: UUID, tenant: Tenant) -> Session:
    session = await session_store.get(session_id)

    # Return 404 even if session exists but belongs to different tenant
    # This prevents tenant enumeration attacks
    if session is None or session.tenant_id != tenant.id:
        raise HTTPException(404, "Session not found")

    return session
```

**Key insight**: 403 reveals that a resource exists. 404 provides no information to attackers attempting tenant enumeration.

---

## Pattern 7: NATS JetStream with Graceful Degradation

Configure NATS JetStream with circuit breaker and fallback queues.

**When to use**: Real-time event streaming where availability matters more than consistency.

**File**: `protocols/streaming/nats_bridge.py`
**Pattern**:
```python
@dataclass
class NATSBridge:
    config: NATSBridgeConfig
    _circuit: CircuitBreaker = field(default_factory=CircuitBreaker)
    _fallback_queues: dict[str, asyncio.Queue] = field(default_factory=dict)

    async def connect(self) -> None:
        try:
            self._nc = await nats.connect(servers=self.config.servers)
            self._js = self._nc.jetstream()

            # Check if stream exists first
            try:
                await self._js.stream_info(self.config.stream_name)
            except Exception:
                # Create with MINIMAL config - avoid max_age issues
                config = StreamConfig(
                    name=self.config.stream_name,
                    subjects=self.config.stream_subjects,
                    # Don't specify max_age - let NATS use defaults
                )
                await self._js.add_stream(config)

            self._connected = True
        except Exception as e:
            logger.warning(f"NATS unavailable, using fallback: {e}")
            self._connected = False  # Graceful degradation

    async def publish(self, subject: str, payload: dict) -> None:
        if not self._circuit.should_allow_request():
            await self._fallback_publish(subject, payload)
            return
        # ... publish with circuit breaker tracking
```

**Key insight**: NATS JetStream `StreamConfig` with large `max_age` values (nanoseconds) can fail with "invalid JSON" error (10025). Use minimal config and let NATS apply defaults.

---

## Pattern 8: Cross-Namespace NetworkPolicy

Allow traffic from API namespace to NATS namespace via label selectors.

**When to use**: Microservices in different namespaces that need to communicate through NetworkPolicy.

**File**: `infra/k8s/manifests/nats/network-policy.yaml`
**Pattern**:
```yaml
apiVersion: networking.k8s.io/v1
kind: NetworkPolicy
metadata:
  name: nats-access
  namespace: kgents-agents  # NATS namespace
spec:
  podSelector:
    matchLabels:
      app.kubernetes.io/name: nats
  policyTypes:
    - Ingress
  ingress:
    - from:
        - namespaceSelector:
            matchLabels:
              kgents.io/tier: gateway  # Label on SOURCE namespace
      ports:
        - port: 4222
          protocol: TCP
```

Then label the source namespace:
```bash
kubectl label namespace kgents-triad kgents.io/tier=gateway
```

**Key insight**: NetworkPolicy `namespaceSelector` matches labels on the SOURCE namespace, not the target. Label the namespace containing the pods that need access.

---

## Pattern 9: Kind Image Loading with Versioned Tags

Force pod recreation when updating images in Kind clusters.

**When to use**: Local Kubernetes development with Kind where `imagePullPolicy: IfNotPresent` caches aggressively.

**Commands**:
```bash
# Build with versioned tag (not :latest)
docker build -t kgents/api:v3 --no-cache -f Dockerfile .

# Load into Kind cluster
kind load docker-image kgents/api:v3 --name kgents-triad

# Update deployment to use new tag
kubectl set image deployment/kgent-api api=kgents/api:v3 -n kgents-triad
```

**Key insight**: Kind's `imagePullPolicy: IfNotPresent` caches images. Using `:latest` won't pull new versions. Increment version tags (v1, v2, v3) to force new image usage and pod recreation.

---

## Pattern 10: Built-in Dev API Keys

Provide development API keys for testing without external auth service.

**When to use**: Local development and CI testing before production auth is configured.

**File**: `protocols/api/auth.py`
**Pattern**:
```python
# In-memory store for development/testing
_API_KEY_STORE: dict[str, ApiKeyData] = {
    "kg_dev_alice": ApiKeyData(
        key="kg_dev_alice",
        user_id="user_alice",
        tier="FREE",
        rate_limit=100,
        scopes=("read",),
    ),
    "kg_dev_bob": ApiKeyData(
        key="kg_dev_bob",
        user_id="user_bob",
        tier="PRO",
        rate_limit=1000,
        scopes=("read", "write"),
    ),
    "kg_dev_carol": ApiKeyData(
        key="kg_dev_carol",
        user_id="user_carol",
        tier="ENTERPRISE",
        rate_limit=10000,
        scopes=("read", "write", "admin"),
    ),
}
```

Usage:
```bash
curl -X POST http://localhost:8000/api/v1/town/demo/init \
  -H "X-API-Key: kg_dev_bob"
```

**Key insight**: Prefix dev keys with `kg_dev_` for easy identification. Include multiple tiers (FREE/PRO/ENTERPRISE) for testing tier-specific behavior.

---

## Verification

After applying these patterns:

1. **Webhook pattern**: Check logs for "Webhook processing" entries appearing after response sent
2. **Idempotency**: Send same webhook twice, verify only processed once
3. **Soak test**: Run 1h test, verify latency stable within 10%
4. **PDB**: `kubectl get pdb` shows `disruptionsAllowed: 1`
5. **Runbook URLs**: Click alert link in Grafana, verify reaches correct runbook section
6. **404 pattern**: Access other tenant's resource, verify 404 (not 403)
7. **NATS**: `curl /health/saas` shows `"nats":{"status":"healthy","mode":"jetstream"}`
8. **NetworkPolicy**: `kubectl exec -n source-ns -- curl nats.target-ns:4222` succeeds
9. **Kind images**: `kubectl get pods -o jsonpath='{.items[*].spec.containers[*].image}'` shows new tag
10. **Dev keys**: `curl -H "X-API-Key: kg_dev_bob" /api/v1/health` returns 200

---

## Common Pitfalls

- **Webhook signature verification after processing**: Always verify BEFORE any processing
- **In-memory idempotency in horizontal scaling**: Use Redis when running multiple replicas
- **PDB with minAvailable = replicas**: Blocks all drains; use minAvailable = replicas - 1
- **403 leaking tenant existence**: Always use 404 for cross-tenant access denial
- **NATS StreamConfig max_age in nanoseconds**: Large values cause "invalid JSON" (10025); use defaults
- **NetworkPolicy namespace labels**: Labels go on SOURCE namespace, not target; easy to confuse
- **Kind :latest tag**: Doesn't trigger pull; use versioned tags (v1, v2, v3) instead
- **Dev keys in production**: Gate behind environment check; never ship to production

---

## Related Skills

- [handler-patterns](handler-patterns.md) - API handler patterns
- [test-patterns](test-patterns.md) - Testing patterns including load tests
- [harden-module](harden-module.md) - Security hardening patterns

---

## Changelog

- 2025-12-15: Added patterns 7-10 (NATS, NetworkPolicy, Kind images, Dev keys) from Kind deployment session
- 2025-12-14: Initial version synthesized from SaaS phases 0-11
