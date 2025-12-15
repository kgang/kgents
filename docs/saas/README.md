# kgents SaaS Infrastructure

> Production infrastructure for multi-tenant kgents API with usage-based billing.

## Overview

The kgents SaaS infrastructure provides:

- **NATS JetStream**: Real-time event streaming for SSE and inter-agent communication
- **OpenMeter**: Usage-based billing with event aggregation
- **Stripe Integration**: Subscription management and payment processing
- **Observability**: Prometheus metrics and Grafana dashboards

## Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│                      kgents SaaS API                            │
├─────────────────────────────────────────────────────────────────┤
│                                                                 │
│  ┌─────────────┐   ┌─────────────┐   ┌─────────────┐           │
│  │   Soul API  │   │  AGENTESE   │   │  Sessions   │           │
│  │  Endpoints  │   │  Endpoints  │   │  Endpoints  │           │
│  └──────┬──────┘   └──────┬──────┘   └──────┬──────┘           │
│         │                 │                 │                   │
│         └────────────┬────┴────────────────┘                    │
│                      ▼                                          │
│              ┌───────────────┐                                  │
│              │ SaaSClients   │                                  │
│              │  Singleton    │                                  │
│              └───────┬───────┘                                  │
│                      │                                          │
│         ┌────────────┼────────────┐                             │
│         ▼            ▼            ▼                             │
│  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐             │
│  │ NATSBridge  │  │ OpenMeter   │  │   Stripe    │             │
│  │ (streaming) │  │  Client     │  │  Webhooks   │             │
│  └──────┬──────┘  └──────┬──────┘  └──────┬──────┘             │
│         │                │                │                     │
└─────────┼────────────────┼────────────────┼─────────────────────┘
          │                │                │
          ▼                ▼                ▼
    ┌───────────┐    ┌───────────┐    ┌───────────┐
    │   NATS    │    │ OpenMeter │    │  Stripe   │
    │ JetStream │    │   Cloud   │    │   API     │
    │  Cluster  │    │           │    │           │
    └───────────┘    └───────────┘    └───────────┘
```

## Components

### NATSBridge

Real-time event streaming with:
- JetStream for durable message delivery
- Circuit breaker for resilience
- In-memory fallback when NATS unavailable
- Multi-consumer support (SSE, metering, observability)

**Location**: `impl/claude/protocols/streaming/nats_bridge.py`

### OpenMeterClient

Usage-based billing with:
- Event buffering and batching
- Automatic flush on interval/count
- CloudEvents format
- Non-blocking async operation

**Location**: `impl/claude/protocols/billing/openmeter_client.py`

### Stripe Integration

Subscription lifecycle management:
- Webhook endpoint for Stripe events
- Event translation to OpenMeter
- Idempotency handling
- Signature verification

**Location**: `impl/claude/protocols/api/webhooks.py`, `impl/claude/protocols/billing/stripe_to_openmeter.py`

### SaaSClients Singleton

Centralized lifecycle management:
- Lazy initialization
- Graceful startup/shutdown
- Health check aggregation

**Location**: `impl/claude/protocols/config/clients.py`

## Quick Start

### Local Development

```bash
# Start NATS (optional, will use fallback)
docker run -d --name nats -p 4222:4222 -p 8222:8222 nats:2.10-alpine --jetstream

# Set environment variables
export NATS_ENABLED=true
export NATS_SERVERS=nats://localhost:4222

# Run API
uv run uvicorn protocols.api.app:create_app --factory --reload
```

### Kubernetes Deployment

```bash
# Deploy NATS cluster
kubectl apply -k impl/claude/infra/k8s/manifests/nats/

# Or use the deploy script
./impl/claude/infra/k8s/scripts/deploy-nats.sh
```

## Documentation

| Document | Description |
|----------|-------------|
| [environment-variables.md](environment-variables.md) | Complete environment variable reference |
| [health-endpoints.md](health-endpoints.md) | Health check endpoint documentation |
| [runbook.md](runbook.md) | Operational runbook for common scenarios |

## Related Documentation

- `docs/skills/n-phase-cycle/saas-phase3-integrate-ship.md` - Phase 3 implementation details
- `docs/skills/n-phase-cycle/saas-phase4-deploy.md` - Phase 4 deployment details
- `impl/claude/protocols/config/` - Configuration module
- `impl/claude/infra/k8s/manifests/nats/` - Kubernetes manifests
