# kgents SaaS Billing & Metering Architecture

**Date**: December 14, 2025
**Phase**: DEVELOP
**Status**: Design Complete

---

## Executive Summary

This document defines the billing and metering architecture for kgents SaaS. Based on research in `research-market.md` and `research-architecture.md`, we implement a hybrid pricing model with usage-based components, powered by OpenMeter for real-time metering and Lago for billing orchestration, with Stripe for payment processing.

---

## 1. Pricing Model

### 1.1 Tier Structure

| Tier | Monthly Price | Target Segment | Key Limits |
|------|---------------|----------------|------------|
| **Free** | $0 | Indie developers, prototypes | 10K tokens, 1 agent, 100 API calls/day |
| **Starter** | $29/month | Solo developers | 100K tokens, 5 agents, 1K API calls/day |
| **Pro** | $149/month | Small teams (5 seats) | 500K tokens, 25 agents, 10K API calls/day |
| **Team** | $499/month | Growing teams (unlimited seats) | 2M tokens, 100 agents, 50K API calls/day |
| **Enterprise** | Custom | Large organizations | Unlimited, SLA, dedicated support |

### 1.2 Usage-Based Components

Beyond base tier limits, usage is billed at:

| Resource | Overage Rate | Notes |
|----------|--------------|-------|
| **AGENTESE Tokens** | $0.01 / 1K tokens | Input + output combined |
| **K-Gent Sessions** | $0.05 / session | Per active session |
| **API Calls** | $0.001 / call | Beyond tier limit |
| **Storage** | $0.10 / GB/month | Agent state, memory |
| **GPU Compute** | $0.50 / GPU-hour | Fine-tuning, custom models |

### 1.3 Annual Commitment Discount

- 10% discount for annual prepayment
- 20% discount for 2-year commitment (Enterprise only)

---

## 2. Architecture Overview

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                           BILLING ARCHITECTURE                               │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                              │
│  ┌─────────────────────────────────────────────────────────────────────┐   │
│  │                        APPLICATION LAYER                             │   │
│  │  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐                  │   │
│  │  │  AGENTESE   │  │   K-Gent    │  │   Other     │                  │   │
│  │  │   Service   │  │   Service   │  │  Services   │                  │   │
│  │  └──────┬──────┘  └──────┬──────┘  └──────┬──────┘                  │   │
│  └─────────┼────────────────┼────────────────┼──────────────────────────┘   │
│            │                │                │                               │
│            └────────────────┴────────────────┘                               │
│                             │ Usage Events                                   │
│                             ▼                                                │
│  ┌─────────────────────────────────────────────────────────────────────┐   │
│  │                     METERING LAYER (OpenMeter)                       │   │
│  │  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐                  │   │
│  │  │   Event     │  │  Metering   │  │   Usage     │                  │   │
│  │  │   Ingestion │─▶│   Engine    │─▶│   API       │                  │   │
│  │  │   (NATS)    │  │ (ClickHouse)│  │             │                  │   │
│  │  └─────────────┘  └─────────────┘  └─────────────┘                  │   │
│  └────────────────────────────┬────────────────────────────────────────┘   │
│                               │ Aggregated Usage                            │
│                               ▼                                             │
│  ┌─────────────────────────────────────────────────────────────────────┐   │
│  │                     BILLING LAYER (Lago)                             │   │
│  │  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐                  │   │
│  │  │ Subscription│  │   Invoice   │  │   Wallet/   │                  │   │
│  │  │  Management │  │  Generation │  │   Credits   │                  │   │
│  │  └─────────────┘  └─────────────┘  └─────────────┘                  │   │
│  └────────────────────────────┬────────────────────────────────────────┘   │
│                               │ Charges                                     │
│                               ▼                                             │
│  ┌─────────────────────────────────────────────────────────────────────┐   │
│  │                     PAYMENT LAYER (Stripe)                           │   │
│  │  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐                  │   │
│  │  │   Payment   │  │   Invoice   │  │   Customer  │                  │   │
│  │  │   Methods   │  │   Payment   │  │   Portal    │                  │   │
│  │  └─────────────┘  └─────────────┘  └─────────────┘                  │   │
│  └─────────────────────────────────────────────────────────────────────┘   │
│                                                                              │
└─────────────────────────────────────────────────────────────────────────────┘
```

---

## 3. Metering Pipeline (OpenMeter)

### 3.1 Event Schema

```json
{
  "$schema": "http://json-schema.org/draft-07/schema#",
  "title": "kgents Usage Event",
  "type": "object",
  "required": ["id", "source", "type", "subject", "time", "data"],
  "properties": {
    "id": {
      "type": "string",
      "description": "Unique event ID (UUID v7 for time-ordering)"
    },
    "source": {
      "type": "string",
      "description": "Service that generated the event",
      "enum": ["agentese", "kgent", "storage", "compute"]
    },
    "type": {
      "type": "string",
      "description": "Event type for metering",
      "enum": [
        "agentese.tokens",
        "agentese.invoke",
        "kgent.session_start",
        "kgent.session_end",
        "api.request",
        "storage.write",
        "compute.gpu_seconds"
      ]
    },
    "subject": {
      "type": "string",
      "description": "Tenant ID (billing subject)"
    },
    "time": {
      "type": "string",
      "format": "date-time",
      "description": "Event timestamp (ISO 8601)"
    },
    "data": {
      "type": "object",
      "properties": {
        "tokens_input": { "type": "integer" },
        "tokens_output": { "type": "integer" },
        "model": { "type": "string" },
        "agent_id": { "type": "string" },
        "session_id": { "type": "string" },
        "duration_seconds": { "type": "number" },
        "bytes": { "type": "integer" }
      }
    }
  }
}
```

### 3.2 Event Examples

```json
// AGENTESE token consumption
{
  "id": "0191f1c4-3d5a-7000-8000-000000000001",
  "source": "agentese",
  "type": "agentese.tokens",
  "subject": "tenant_abc123",
  "time": "2025-12-14T10:30:00Z",
  "data": {
    "tokens_input": 1250,
    "tokens_output": 850,
    "model": "claude-3-5-sonnet",
    "agent_id": "agent_xyz",
    "path": "world.house.manifest"
  }
}

// K-Gent session
{
  "id": "0191f1c4-3d5a-7000-8000-000000000002",
  "source": "kgent",
  "type": "kgent.session_start",
  "subject": "tenant_abc123",
  "time": "2025-12-14T10:30:00Z",
  "data": {
    "session_id": "session_001",
    "persona": "kgent_default"
  }
}
```

### 3.3 OpenMeter Configuration

```yaml
# OpenMeter meter definitions
meters:
  - slug: agentese_tokens
    description: AGENTESE token consumption
    eventType: agentese.tokens
    valueProperty: $.data.tokens_input + $.data.tokens_output
    aggregation: SUM
    groupBy:
      model: $.data.model
      agent_id: $.data.agent_id

  - slug: kgent_sessions
    description: K-Gent active sessions
    eventType: kgent.session_start
    aggregation: COUNT
    groupBy:
      persona: $.data.persona

  - slug: api_requests
    description: API request count
    eventType: api.request
    aggregation: COUNT
    groupBy:
      endpoint: $.data.endpoint
      method: $.data.method

  - slug: storage_bytes
    description: Storage consumption
    eventType: storage.write
    valueProperty: $.data.bytes
    aggregation: SUM

  - slug: gpu_seconds
    description: GPU compute time
    eventType: compute.gpu_seconds
    valueProperty: $.data.duration_seconds
    aggregation: SUM
    groupBy:
      gpu_type: $.data.gpu_type
```

### 3.4 Real-Time Processing Pipeline

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                         METERING PIPELINE                                    │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                              │
│   Services                 NATS                 OpenMeter                    │
│   ┌──────┐             ┌─────────┐         ┌─────────────────┐              │
│   │AGENTE│──▶ events ──▶│  JetSt  │─────────▶│  Event Ingestion │              │
│   │SE    │              │  ream   │         │  (HTTP/Kafka)   │              │
│   └──────┘             └─────────┘         └────────┬────────┘              │
│   ┌──────┐                  │                       │                        │
│   │K-Gent│──▶ events ───────┘                       ▼                        │
│   └──────┘                              ┌─────────────────────┐              │
│   ┌──────┐                              │    ClickHouse       │              │
│   │Other │──▶ events ───────────────────▶│  (Time-series DB)  │              │
│   └──────┘                              │  - Aggregations     │              │
│                                          │  - Real-time queries│              │
│                                          └─────────┬───────────┘              │
│                                                    │                          │
│                                                    ▼                          │
│                                          ┌─────────────────────┐              │
│                                          │   Usage API         │              │
│                                          │  - Query meters     │              │
│                                          │  - Customer portal  │              │
│                                          │  - Lago webhook     │              │
│                                          └─────────────────────┘              │
│                                                                              │
└─────────────────────────────────────────────────────────────────────────────┘
```

---

## 4. Billing Orchestration (Lago)

### 4.1 Plan Configuration

```yaml
# Lago Plan: Starter
plans:
  - name: starter
    code: starter_monthly
    interval: monthly
    amount_cents: 2900
    amount_currency: USD
    pay_in_advance: true
    charges:
      # Included tokens (100K)
      - billable_metric_code: agentese_tokens
        charge_model: graduated
        properties:
          graduated_ranges:
            - from_value: 0
              to_value: 100000
              per_unit_amount: "0"
              flat_amount: "0"
            - from_value: 100001
              to_value: null
              per_unit_amount: "0.00001"  # $0.01/1K
              flat_amount: "0"

      # Included K-Gent sessions (100)
      - billable_metric_code: kgent_sessions
        charge_model: graduated
        properties:
          graduated_ranges:
            - from_value: 0
              to_value: 100
              per_unit_amount: "0"
              flat_amount: "0"
            - from_value: 101
              to_value: null
              per_unit_amount: "0.05"
              flat_amount: "0"

      # Included API calls (1K/day = 30K/month)
      - billable_metric_code: api_requests
        charge_model: graduated
        properties:
          graduated_ranges:
            - from_value: 0
              to_value: 30000
              per_unit_amount: "0"
              flat_amount: "0"
            - from_value: 30001
              to_value: null
              per_unit_amount: "0.001"
              flat_amount: "0"

  - name: pro
    code: pro_monthly
    interval: monthly
    amount_cents: 14900
    amount_currency: USD
    pay_in_advance: true
    charges:
      # Same structure with higher limits
      - billable_metric_code: agentese_tokens
        charge_model: graduated
        properties:
          graduated_ranges:
            - from_value: 0
              to_value: 500000
              per_unit_amount: "0"
            - from_value: 500001
              to_value: null
              per_unit_amount: "0.000008"  # Volume discount
```

### 4.2 Subscription Lifecycle

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                      SUBSCRIPTION LIFECYCLE                                  │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                              │
│  ┌────────┐    ┌────────┐    ┌────────┐    ┌────────┐    ┌────────┐        │
│  │ Trial  │───▶│ Active │───▶│ Pending│───▶│ Past   │───▶│Canceled│        │
│  │ (14d)  │    │        │    │ Cancel │    │  Due   │    │        │        │
│  └────────┘    └────────┘    └────────┘    └────────┘    └────────┘        │
│       │             │             │             │             │             │
│       │             │             │             │             │             │
│  Create       Upgrade/       Schedule     Payment      Final              │
│  Customer     Downgrade      Cancel       Failed       Cancellation       │
│                                                                              │
└─────────────────────────────────────────────────────────────────────────────┘
```

### 4.3 Invoice Generation

```python
# Lago invoice webhook handler
from lago_python import Client
from datetime import datetime

class InvoiceHandler:
    def __init__(self, lago_client: Client, stripe_client):
        self.lago = lago_client
        self.stripe = stripe_client

    async def handle_invoice_created(self, event: dict):
        """Process new invoice from Lago"""
        invoice = event['invoice']
        customer_id = invoice['customer']['external_id']

        # Create Stripe invoice
        stripe_invoice = self.stripe.invoices.create(
            customer=customer_id,
            auto_advance=True,
            collection_method='charge_automatically',
            metadata={
                'lago_invoice_id': invoice['lago_id'],
                'tenant_id': invoice['customer']['external_id']
            }
        )

        # Add line items
        for fee in invoice['fees']:
            self.stripe.invoice_items.create(
                customer=customer_id,
                invoice=stripe_invoice.id,
                amount=fee['amount_cents'],
                currency='usd',
                description=fee['item']['name']
            )

        # Finalize and charge
        self.stripe.invoices.finalize_invoice(stripe_invoice.id)

        return stripe_invoice
```

---

## 5. Stripe Integration

### 5.1 Customer Sync

```python
# Customer lifecycle management
from stripe import Customer, Subscription
from lago_python import Client as LagoClient

class CustomerManager:
    def __init__(self, stripe, lago: LagoClient):
        self.stripe = stripe
        self.lago = lago

    async def create_customer(self, tenant: dict) -> dict:
        """Create customer in Stripe and Lago"""
        # Create Stripe customer
        stripe_customer = self.stripe.customers.create(
            email=tenant['admin_email'],
            name=tenant['company_name'],
            metadata={
                'tenant_id': tenant['id'],
                'tier': tenant['tier']
            }
        )

        # Sync to Lago
        lago_customer = self.lago.customers.create({
            'external_id': tenant['id'],
            'name': tenant['company_name'],
            'email': tenant['admin_email'],
            'billing_configuration': {
                'payment_provider': 'stripe',
                'provider_customer_id': stripe_customer.id
            }
        })

        return {
            'stripe_id': stripe_customer.id,
            'lago_id': lago_customer.lago_id,
            'tenant_id': tenant['id']
        }

    async def start_subscription(self, tenant_id: str, plan_code: str):
        """Start subscription in Lago"""
        subscription = self.lago.subscriptions.create({
            'external_customer_id': tenant_id,
            'external_id': f"{tenant_id}_sub",
            'plan_code': plan_code
        })
        return subscription
```

### 5.2 Payment Methods

```python
# Stripe payment method handling
class PaymentMethodHandler:
    async def attach_payment_method(
        self,
        customer_id: str,
        payment_method_id: str
    ):
        """Attach and set as default payment method"""
        # Attach to customer
        self.stripe.payment_methods.attach(
            payment_method_id,
            customer=customer_id
        )

        # Set as default
        self.stripe.customers.modify(
            customer_id,
            invoice_settings={
                'default_payment_method': payment_method_id
            }
        )

    async def handle_payment_failed(self, event: dict):
        """Handle failed payment webhook"""
        invoice = event['data']['object']
        customer_id = invoice['customer']

        # Get tenant
        customer = self.stripe.customers.retrieve(customer_id)
        tenant_id = customer.metadata.get('tenant_id')

        # Notify and apply grace period
        await self.notify_payment_failed(tenant_id, invoice)
        await self.apply_grace_period(tenant_id, days=7)
```

### 5.3 Webhook Handlers

```python
# Stripe webhook router
from fastapi import APIRouter, Request, HTTPException
import stripe

router = APIRouter()

@router.post("/webhooks/stripe")
async def handle_stripe_webhook(request: Request):
    payload = await request.body()
    sig_header = request.headers.get('stripe-signature')

    try:
        event = stripe.Webhook.construct_event(
            payload, sig_header, STRIPE_WEBHOOK_SECRET
        )
    except ValueError:
        raise HTTPException(400, "Invalid payload")
    except stripe.error.SignatureVerificationError:
        raise HTTPException(400, "Invalid signature")

    handlers = {
        'invoice.paid': handle_invoice_paid,
        'invoice.payment_failed': handle_payment_failed,
        'customer.subscription.updated': handle_subscription_updated,
        'customer.subscription.deleted': handle_subscription_deleted,
    }

    handler = handlers.get(event['type'])
    if handler:
        await handler(event)

    return {"status": "ok"}
```

---

## 6. Credit System

### 6.1 Credit Types

| Credit Type | Use Case | Expiration |
|-------------|----------|------------|
| **Promotional** | Sign-up bonus, referrals | 90 days |
| **Prepaid** | Purchased token packs | 1 year |
| **Rollover** | Unused tier allocation | 1 month |
| **Compensation** | Service credits | 1 year |

### 6.2 Credit Wallet

```python
# Lago wallet management
class CreditWallet:
    def __init__(self, lago: LagoClient):
        self.lago = lago

    async def create_wallet(
        self,
        tenant_id: str,
        credits: int,
        credit_type: str = "promotional"
    ):
        """Create credit wallet for tenant"""
        wallet = self.lago.wallets.create({
            'external_customer_id': tenant_id,
            'name': f"{credit_type}_credits",
            'rate_amount': '1',  # 1 credit = $0.01
            'currency': 'USD',
            'paid_credits': str(credits),
            'granted_credits': '0',
            'expiration_at': self._get_expiration(credit_type)
        })
        return wallet

    async def add_credits(self, wallet_id: str, credits: int):
        """Top up existing wallet"""
        transaction = self.lago.wallet_transactions.create({
            'wallet_id': wallet_id,
            'paid_credits': str(credits)
        })
        return transaction

    async def get_balance(self, tenant_id: str) -> dict:
        """Get total credit balance"""
        wallets = self.lago.wallets.find_all({
            'external_customer_id': tenant_id
        })
        total = sum(
            float(w.balance_cents) / 100
            for w in wallets
            if not self._is_expired(w)
        )
        return {'total_credits': total, 'wallets': wallets}
```

### 6.3 Credit Application Order

```
1. Promotional credits (FIFO by expiration)
2. Rollover credits
3. Prepaid credits (FIFO by expiration)
4. Compensation credits
5. Usage-based billing (if credits exhausted)
```

---

## 7. Quota Enforcement

### 7.1 Real-Time Quota Check

```python
# Quota enforcement middleware
from fastapi import Request, HTTPException
from redis import Redis

class QuotaEnforcer:
    def __init__(self, redis: Redis, openmeter):
        self.redis = redis
        self.openmeter = openmeter

    async def check_quota(
        self,
        tenant_id: str,
        resource: str,
        amount: int = 1
    ) -> bool:
        """Check if tenant has quota for resource"""
        # Get cached quota
        quota_key = f"quota:{tenant_id}:{resource}"
        cached = self.redis.get(quota_key)

        if cached is None:
            # Fetch from OpenMeter
            usage = await self.openmeter.query_meter(
                meter_slug=resource,
                subject=tenant_id,
                window_size='MONTH'
            )
            limit = await self._get_tier_limit(tenant_id, resource)
            remaining = limit - usage.value

            # Cache for 60 seconds
            self.redis.setex(quota_key, 60, remaining)
            cached = remaining

        return int(cached) >= amount

    async def enforce(
        self,
        tenant_id: str,
        resource: str,
        amount: int = 1
    ):
        """Enforce quota, raise if exceeded"""
        if not await self.check_quota(tenant_id, resource, amount):
            tier = await self._get_tenant_tier(tenant_id)
            raise HTTPException(
                status_code=429,
                detail={
                    'error': 'quota_exceeded',
                    'resource': resource,
                    'tier': tier,
                    'upgrade_url': f'/billing/upgrade?tier={tier}'
                }
            )
```

### 7.2 Tier Limits

```python
# Tier limit configuration
TIER_LIMITS = {
    'free': {
        'agentese_tokens': 10_000,
        'kgent_sessions': 10,
        'api_requests_daily': 100,
        'agents': 1,
        'storage_gb': 0.1,
    },
    'starter': {
        'agentese_tokens': 100_000,
        'kgent_sessions': 100,
        'api_requests_daily': 1_000,
        'agents': 5,
        'storage_gb': 1,
    },
    'pro': {
        'agentese_tokens': 500_000,
        'kgent_sessions': 500,
        'api_requests_daily': 10_000,
        'agents': 25,
        'storage_gb': 10,
    },
    'team': {
        'agentese_tokens': 2_000_000,
        'kgent_sessions': 2_000,
        'api_requests_daily': 50_000,
        'agents': 100,
        'storage_gb': 100,
    },
    'enterprise': {
        # Custom, no hard limits
        'agentese_tokens': float('inf'),
        'kgent_sessions': float('inf'),
        'api_requests_daily': float('inf'),
        'agents': float('inf'),
        'storage_gb': float('inf'),
    }
}
```

---

## 8. Customer Portal

### 8.1 Usage Dashboard

```typescript
// Usage dashboard component
interface UsageDashboard {
  // Current period usage
  currentUsage: {
    agentese_tokens: {
      used: number;
      limit: number;
      percentage: number;
    };
    kgent_sessions: {
      used: number;
      limit: number;
      percentage: number;
    };
    api_requests: {
      used: number;
      limit: number;
      percentage: number;
    };
  };

  // Cost breakdown
  costs: {
    base_subscription: number;
    overage_tokens: number;
    overage_sessions: number;
    overage_api: number;
    total: number;
  };

  // Usage history (last 30 days)
  history: Array<{
    date: string;
    tokens: number;
    sessions: number;
    api_calls: number;
  }>;
}
```

### 8.2 API Endpoints

```python
# Billing API endpoints
from fastapi import APIRouter, Depends
from typing import Optional

router = APIRouter(prefix="/v1/billing")

@router.get("/usage")
async def get_usage(
    tenant: Tenant = Depends(get_current_tenant),
    period: str = "current"  # current, previous, or YYYY-MM
):
    """Get usage metrics for billing period"""
    return await billing_service.get_usage(tenant.id, period)

@router.get("/invoices")
async def list_invoices(
    tenant: Tenant = Depends(get_current_tenant),
    limit: int = 10,
    offset: int = 0
):
    """List invoices for tenant"""
    return await billing_service.list_invoices(tenant.id, limit, offset)

@router.get("/invoices/{invoice_id}/pdf")
async def download_invoice(
    invoice_id: str,
    tenant: Tenant = Depends(get_current_tenant)
):
    """Download invoice PDF"""
    return await billing_service.get_invoice_pdf(tenant.id, invoice_id)

@router.post("/subscription/upgrade")
async def upgrade_subscription(
    request: UpgradeRequest,
    tenant: Tenant = Depends(get_current_tenant)
):
    """Upgrade subscription tier"""
    return await billing_service.upgrade(tenant.id, request.plan_code)

@router.post("/credits/purchase")
async def purchase_credits(
    request: CreditPurchase,
    tenant: Tenant = Depends(get_current_tenant)
):
    """Purchase additional credits"""
    return await billing_service.purchase_credits(
        tenant.id,
        request.amount,
        request.payment_method_id
    )

@router.get("/subscription")
async def get_subscription(
    tenant: Tenant = Depends(get_current_tenant)
):
    """Get current subscription details"""
    return await billing_service.get_subscription(tenant.id)
```

---

## 9. Enterprise Features

### 9.1 Volume Discounts

| Monthly Usage | Discount |
|---------------|----------|
| $1K - $5K | 5% |
| $5K - $10K | 10% |
| $10K - $25K | 15% |
| $25K+ | Custom |

### 9.2 Custom Contracts

```python
# Enterprise contract management
class EnterpriseContract:
    tenant_id: str
    contract_start: datetime
    contract_end: datetime

    # Committed spend
    annual_commitment: Decimal
    monthly_minimum: Decimal

    # Custom rates
    custom_rates: dict = {
        'agentese_tokens': Decimal('0.000008'),  # $0.008/1K
        'kgent_sessions': Decimal('0.04'),
        'gpu_hours': Decimal('0.40')
    }

    # Features
    features: list = [
        'dedicated_support',
        'custom_sla',
        'on_premise_option',
        'custom_encryption_keys',
        'soc2_audit_support'
    ]

    # SLA
    sla_uptime: Decimal = Decimal('99.95')
    sla_response_time_hours: int = 4
```

### 9.3 SLA Credits

```python
# SLA credit calculation
class SLAMonitor:
    async def calculate_sla_credits(
        self,
        tenant_id: str,
        period: str
    ) -> Decimal:
        """Calculate SLA credits for downtime"""
        contract = await self.get_contract(tenant_id)
        uptime = await self.get_uptime(tenant_id, period)

        if uptime >= contract.sla_uptime:
            return Decimal('0')

        # Credit schedule
        if uptime >= Decimal('99.9'):
            credit_pct = Decimal('0.10')  # 10%
        elif uptime >= Decimal('99.0'):
            credit_pct = Decimal('0.25')  # 25%
        elif uptime >= Decimal('95.0'):
            credit_pct = Decimal('0.50')  # 50%
        else:
            credit_pct = Decimal('1.00')  # 100%

        monthly_spend = await self.get_monthly_spend(tenant_id, period)
        return monthly_spend * credit_pct
```

---

## 10. Implementation Checklist

### Phase 1: Foundation (Weeks 1-2)
- [ ] Deploy OpenMeter (self-hosted)
- [ ] Configure NATS for event streaming
- [ ] Create meter definitions
- [ ] Implement event emission in services
- [ ] Basic usage API

### Phase 2: Billing (Weeks 3-4)
- [ ] Deploy Lago (self-hosted)
- [ ] Configure plans and pricing
- [ ] Stripe integration
- [ ] Subscription lifecycle
- [ ] Webhook handlers

### Phase 3: Portal (Weeks 5-6)
- [ ] Usage dashboard UI
- [ ] Invoice management
- [ ] Payment method management
- [ ] Subscription self-service
- [ ] Credit purchase flow

### Phase 4: Enterprise (Weeks 7-8)
- [ ] Volume discount engine
- [ ] Contract management
- [ ] SLA monitoring
- [ ] Custom invoicing
- [ ] Enterprise portal features

---

## 11. Technology Stack

| Component | Technology | Deployment |
|-----------|-----------|------------|
| **Metering** | OpenMeter | Self-hosted (Kubernetes) |
| **Time-Series DB** | ClickHouse | Managed or self-hosted |
| **Event Streaming** | NATS JetStream | Self-hosted |
| **Billing** | Lago | Self-hosted |
| **Payments** | Stripe | SaaS |
| **Cache** | Redis | Self-hosted |
| **Portal** | React + Tailwind | SPA |

---

## References

- [research-market.md](./research-market.md) - Pricing research
- [research-architecture.md](./research-architecture.md) - Technical architecture
- [OpenMeter Documentation](https://openmeter.io/docs)
- [Lago Documentation](https://getlago.com/docs)
- [Stripe API Reference](https://stripe.com/docs/api)

---

**Document Status**: Design Complete
**Next Phase**: BUILD
**Owner**: Billing Team
