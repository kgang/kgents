# Health Endpoints Documentation

> Health check endpoints for monitoring kgents SaaS infrastructure.

## Endpoints

| Endpoint | Auth | Description |
|----------|------|-------------|
| `GET /health` | None | Basic API health check |
| `GET /health/saas` | None | SaaS infrastructure health |
| `GET /webhooks/stripe/health` | None | Stripe webhook bridge health |
| `GET /metrics` | None | Prometheus metrics |

---

## GET /health

Basic API health check. Returns overall service status.

### Response

```json
{
  "status": "ok",
  "version": "v1",
  "has_llm": true,
  "components": {
    "soul": "ok",
    "llm": "ok",
    "auth": "ok",
    "metering": "ok"
  }
}
```

### Status Values

| Status | Meaning |
|--------|---------|
| `ok` | All components healthy |
| `degraded` | Some components unavailable but service functional |
| `error` | Critical components failing |

### Component Status

| Component | Description |
|-----------|-------------|
| `soul` | K-gent Soul instantiation |
| `llm` | LLM provider availability |
| `auth` | Authentication middleware |
| `metering` | Usage metering middleware |

---

## GET /health/saas

SaaS infrastructure health. Returns status of NATS and OpenMeter.

### Response

```json
{
  "status": "ok",
  "started": true,
  "openmeter": {
    "configured": true,
    "status": "healthy",
    "metrics": {
      "events_sent": 1234,
      "events_failed": 0,
      "events_buffered": 5,
      "last_flush": "2025-12-14T10:30:00Z",
      "configured": true,
      "running": true
    }
  },
  "nats": {
    "configured": true,
    "status": "healthy",
    "mode": "jetstream"
  }
}
```

### Status Values

| Status | Meaning |
|--------|---------|
| `ok` | All infrastructure healthy |
| `degraded` | Some components unavailable |
| `not_started` | Infrastructure not initialized |
| `not_configured` | SaaS infrastructure not available |

### NATS Status

| Status | Meaning |
|--------|---------|
| `healthy` | Connected to JetStream |
| `disconnected` | Not connected to NATS |
| `circuit_open` | Circuit breaker open, using fallback |
| `disabled` | NATS_ENABLED=false |

### NATS Modes

| Mode | Meaning |
|------|---------|
| `jetstream` | Connected to JetStream |
| `fallback` | Using in-memory queue |

### OpenMeter Status

| Status | Meaning |
|--------|---------|
| `healthy` | Connected to OpenMeter API |
| `unhealthy` | API errors |
| `degraded` | httpx not installed |
| `disabled` | OPENMETER_ENABLED=false |

---

## GET /webhooks/stripe/health

Stripe webhook bridge health. Returns metrics and configuration status.

### Response

```json
{
  "stripe_sdk": true,
  "billing_module": true,
  "webhook_secret_configured": true,
  "openmeter_connected": true,
  "bridge_metrics": {
    "events_processed": 42,
    "events_skipped": 3,
    "events_failed": 0,
    "idempotency_store_size": 45
  }
}
```

### Fields

| Field | Description |
|-------|-------------|
| `stripe_sdk` | Stripe Python SDK installed |
| `billing_module` | Billing module available |
| `webhook_secret_configured` | STRIPE_WEBHOOK_SECRET set |
| `openmeter_connected` | OpenMeter client available |
| `bridge_metrics` | Processing statistics |

---

## GET /metrics

Prometheus metrics endpoint. Returns metrics in text format.

### Example Response

```
# HELP kgents_nats_circuit_state Circuit breaker state (0=closed, 1=open, 2=half_open)
# TYPE kgents_nats_circuit_state gauge
kgents_nats_circuit_state 0

# HELP kgents_nats_messages_published_total Total messages published to NATS
# TYPE kgents_nats_messages_published_total counter
kgents_nats_messages_published_total{subject_type="chunk"} 1234

# HELP kgents_openmeter_events_buffered Events currently in OpenMeter buffer
# TYPE kgents_openmeter_events_buffered gauge
kgents_openmeter_events_buffered 5

# HELP kgents_stripe_webhooks_received_total Total Stripe webhooks received
# TYPE kgents_stripe_webhooks_received_total counter
kgents_stripe_webhooks_received_total{event_type="invoice.paid"} 42
```

### Available Metrics

| Metric | Type | Description |
|--------|------|-------------|
| `kgents_nats_circuit_state` | Gauge | Circuit breaker state (0/1/2) |
| `kgents_nats_messages_published_total` | Counter | Messages published to NATS |
| `kgents_nats_publish_errors_total` | Counter | NATS publish errors |
| `kgents_nats_fallback_queue_depth` | Gauge | Fallback queue depth |
| `kgents_openmeter_events_buffered` | Gauge | OpenMeter buffer depth |
| `kgents_openmeter_events_sent_total` | Counter | Events sent to OpenMeter |
| `kgents_openmeter_flush_errors_total` | Counter | OpenMeter flush errors |
| `kgents_openmeter_flush_latency_seconds` | Histogram | Flush latency |
| `kgents_stripe_webhooks_received_total` | Counter | Webhooks received |
| `kgents_stripe_webhooks_processed_total` | Counter | Webhooks processed |
| `kgents_stripe_webhooks_errors_total` | Counter | Webhook errors |
| `kgents_api_requests_total` | Counter | API requests |
| `kgents_api_request_latency_seconds` | Histogram | API latency |

---

## Usage with Kubernetes

### Liveness Probe

```yaml
livenessProbe:
  httpGet:
    path: /health
    port: 8000
  initialDelaySeconds: 10
  periodSeconds: 30
```

### Readiness Probe

```yaml
readinessProbe:
  httpGet:
    path: /health/saas
    port: 8000
  initialDelaySeconds: 5
  periodSeconds: 10
```

### Prometheus ServiceMonitor

```yaml
apiVersion: monitoring.coreos.com/v1
kind: ServiceMonitor
metadata:
  name: kgents-api
spec:
  selector:
    matchLabels:
      app: kgents-api
  endpoints:
    - port: http
      path: /metrics
      interval: 30s
```
