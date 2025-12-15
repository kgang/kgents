# Environment Variables Reference

> Complete reference for kgents SaaS infrastructure configuration.

## NATS Configuration

| Variable | Default | Required | Description |
|----------|---------|----------|-------------|
| `NATS_SERVERS` | `nats://localhost:4222` | No | Comma-separated list of NATS server URLs |
| `NATS_ENABLED` | `false` | No | Enable NATS streaming (`true`/`false`) |
| `NATS_STREAM_NAME` | `kgent-events` | No | JetStream stream name |
| `NATS_MAX_RECONNECT` | `10` | No | Maximum reconnection attempts |

### Example

```bash
# Single server
NATS_SERVERS=nats://nats.kgents-agents.svc.cluster.local:4222
NATS_ENABLED=true

# Multiple servers (HA)
NATS_SERVERS=nats://nats-0.nats.svc:4222,nats://nats-1.nats.svc:4222,nats://nats-2.nats.svc:4222
```

### Notes

- When `NATS_ENABLED=false` or NATS is unavailable, the system uses an in-memory fallback queue
- JetStream stream is auto-created on first publish
- Circuit breaker opens after 5 consecutive failures and recovers after 30 seconds

---

## OpenMeter Configuration

| Variable | Default | Required | Description |
|----------|---------|----------|-------------|
| `OPENMETER_API_KEY` | *(empty)* | Yes* | OpenMeter API key (starts with `om_`) |
| `OPENMETER_BASE_URL` | `https://openmeter.cloud` | No | OpenMeter API endpoint |
| `OPENMETER_ENABLED` | `false` | No | Enable usage metering (`true`/`false`) |
| `OPENMETER_BATCH_SIZE` | `100` | No | Events to buffer before auto-flush |
| `OPENMETER_FLUSH_INTERVAL` | `1.0` | No | Seconds between automatic flushes |

*Required when `OPENMETER_ENABLED=true`

### Example

```bash
OPENMETER_API_KEY=om_live_xxxxxxxxxxxx
OPENMETER_ENABLED=true
OPENMETER_BATCH_SIZE=100
OPENMETER_FLUSH_INTERVAL=1.0
```

### Notes

- Events are buffered and flushed either when batch size is reached or on interval
- On shutdown, remaining events are flushed
- When `OPENMETER_ENABLED=false`, events are counted locally but not sent

---

## Stripe Configuration

| Variable | Default | Required | Description |
|----------|---------|----------|-------------|
| `STRIPE_API_KEY` | *(empty)* | Yes* | Stripe secret key (starts with `sk_`) |
| `STRIPE_WEBHOOK_SECRET` | *(empty)* | Yes* | Webhook signing secret (starts with `whsec_`) |
| `STRIPE_PRICE_PRO_MONTHLY` | *(empty)* | No | Pro monthly price ID |
| `STRIPE_PRICE_PRO_YEARLY` | *(empty)* | No | Pro yearly price ID |
| `STRIPE_PRICE_TEAMS_MONTHLY` | *(empty)* | No | Teams monthly price ID |

*Required for Stripe integration

### Example

```bash
STRIPE_API_KEY=sk_live_xxxxxxxxxxxx
STRIPE_WEBHOOK_SECRET=whsec_xxxxxxxxxxxx
```

### Notes

- Use test keys (`sk_test_`, `whsec_test_`) for development
- Webhook secret is obtained from Stripe Dashboard → Developers → Webhooks
- All webhook events are signature-verified before processing

---

## API Configuration

| Variable | Default | Required | Description |
|----------|---------|----------|-------------|
| `API_HOST` | `0.0.0.0` | No | API server bind host |
| `API_PORT` | `8000` | No | API server port |
| `CORS_ORIGINS` | `*` | No | Allowed CORS origins (comma-separated) |

### Example

```bash
API_HOST=0.0.0.0
API_PORT=8000
CORS_ORIGINS=https://app.kgents.io,https://dashboard.kgents.io
```

---

## Observability Configuration

| Variable | Default | Required | Description |
|----------|---------|----------|-------------|
| `KGENTS_TELEMETRY_ENABLED` | `false` | No | Enable OpenTelemetry tracing |
| `OTEL_EXPORTER_OTLP_ENDPOINT` | *(empty)* | No | OTLP endpoint for traces |
| `LOG_LEVEL` | `INFO` | No | Logging level |

### Example

```bash
KGENTS_TELEMETRY_ENABLED=true
OTEL_EXPORTER_OTLP_ENDPOINT=http://jaeger:4317
LOG_LEVEL=DEBUG
```

---

## Kubernetes ConfigMap Example

```yaml
apiVersion: v1
kind: ConfigMap
metadata:
  name: kgents-api-config
  namespace: kgents-agents
data:
  NATS_SERVERS: "nats://nats.kgents-agents.svc.cluster.local:4222"
  NATS_ENABLED: "true"
  NATS_STREAM_NAME: "kgent-events"
  OPENMETER_BASE_URL: "https://openmeter.cloud"
  OPENMETER_ENABLED: "true"
  OPENMETER_BATCH_SIZE: "100"
  OPENMETER_FLUSH_INTERVAL: "1.0"
```

## Kubernetes Secret Example

```yaml
apiVersion: v1
kind: Secret
metadata:
  name: kgents-api-secrets
  namespace: kgents-agents
type: Opaque
stringData:
  OPENMETER_API_KEY: "om_live_xxxxxxxxxxxx"
  STRIPE_API_KEY: "sk_live_xxxxxxxxxxxx"
  STRIPE_WEBHOOK_SECRET: "whsec_xxxxxxxxxxxx"
```

---

## Configuration Loading Order

1. Environment variables (highest priority)
2. `.env` file (if present)
3. Default values (lowest priority)

The `SaaSConfig` class in `impl/claude/protocols/config/saas.py` handles loading and validation.
