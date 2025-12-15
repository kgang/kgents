# kgents SaaS Launch Announcement

> Production-ready AGENTESE and K-gent Soul API now available.

## What's Launching

**kgents SaaS** provides cloud-hosted access to the AGENTESE protocol and K-gent Soul, enabling developers to build tasteful, ethical AI agent applications.

### Core Capabilities

1. **AGENTESE Protocol** - Universal agent-world interaction ontology
   - Five contexts: `world.*`, `self.*`, `concept.*`, `void.*`, `time.*`
   - Handle-based invocation with observer-dependent affordances
   - Composable agent morphisms via `>>`

2. **K-gent Soul API** - Multi-tenant agent persona service
   - Governance system with principles
   - Dialogue with memory integration
   - Session management

3. **Usage-Based Billing** - Fair, transparent metering
   - OpenMeter integration for precise token tracking
   - Stripe payment processing
   - Real-time usage dashboards

---

## API Endpoints

| Endpoint | Purpose |
|----------|---------|
| `/v1/agentese/invoke` | Execute AGENTESE paths |
| `/v1/agentese/resolve` | Resolve handles to values |
| `/v1/soul/dialogue` | Converse with K-gent |
| `/v1/soul/governance` | Query governance principles |
| `/v1/kgent/sessions` | Manage conversation sessions |

Full API documentation: `/docs`

---

## Infrastructure

### Production-Ready

- Network-isolated NATS cluster (3 replicas)
- Pod Disruption Budget ensures availability
- Default-deny network policies
- Circuit breaker patterns for resilience

### Observability

- Prometheus metrics at `/metrics`
- Grafana dashboards pre-configured
- Distributed tracing via Tempo
- 8 active alerts monitoring health

### Performance Baseline

| Metric | Value |
|--------|-------|
| Throughput | 478 req/s (4.8x target) |
| p95 Latency | 6.95ms |
| Error Rate | 0% |

---

## Getting Started

### 1. Obtain API Key

Contact the kgents team to request access.

### 2. Test Connection

```bash
curl -H "Authorization: Bearer $API_KEY" \
  https://api.kgents.io/health
```

### 3. Invoke AGENTESE

```bash
curl -X POST https://api.kgents.io/v1/agentese/invoke \
  -H "Authorization: Bearer $API_KEY" \
  -H "Content-Type: application/json" \
  -d '{"path": "self.soul.principles.manifest"}'
```

### 4. Start a Session

```bash
curl -X POST https://api.kgents.io/v1/kgent/sessions \
  -H "Authorization: Bearer $API_KEY" \
  -H "Content-Type: application/json" \
  -d '{"title": "My First Session"}'
```

---

## Pricing

Usage-based billing via OpenMeter:
- **Tokens processed**: $X per 1M tokens
- **API calls**: $Y per 1K calls
- **Sessions**: $Z per session-hour

See billing documentation for details.

---

## Support

- Documentation: https://docs.kgents.io
- Issues: https://github.com/kgents/kgents/issues
- Status: https://status.kgents.io

---

## Roadmap

**Phase 8+**:
- Loki log aggregation
- Multi-region deployment
- HPA auto-scaling
- Enhanced security audits

---

*"To read is to invoke. There is no view from nowhere."*

**kgents SaaS v1.0.0** | 2025-12-14
