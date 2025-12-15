"""
Webhook endpoints for kgents SaaS API.

Handles external webhooks from:
- Stripe (subscription lifecycle events)

Security:
- Signature verification for all webhooks
- Idempotency handling to prevent duplicate processing
- Non-blocking processing via asyncio.create_task

Integration:
- Updates BudgetStore on payment events (unified-v2.md Track C)
- Forwards events to OpenMeter for billing reconciliation

Usage:
    from protocols.api.webhooks import create_webhooks_router

    router = create_webhooks_router()
    app.include_router(router)
"""

from __future__ import annotations

import asyncio
import logging
from typing import TYPE_CHECKING, Any, Optional

# Graceful FastAPI import
try:
    from fastapi import APIRouter, Header, HTTPException, Request

    HAS_FASTAPI = True
except ImportError:
    HAS_FASTAPI = False
    APIRouter = None  # type: ignore[misc, assignment]
    Header = None  # type: ignore[assignment]
    HTTPException = None  # type: ignore[misc, assignment]
    Request = None  # type: ignore[misc, assignment]

logger = logging.getLogger(__name__)

# BudgetStore import for payment → credits wiring
try:
    from agents.town.budget_store import BudgetStore, InMemoryBudgetStore

    HAS_BUDGET_STORE = True
except ImportError:
    HAS_BUDGET_STORE = False
    BudgetStore = None  # type: ignore[misc, assignment]
    InMemoryBudgetStore = None  # type: ignore[misc, assignment]

# Payment handlers import
try:
    from protocols.api.payments import (
        handle_payment_succeeded,
        handle_subscription_created,
        handle_subscription_deleted,
        handle_subscription_updated,
    )

    HAS_PAYMENT_HANDLERS = True
except ImportError:
    HAS_PAYMENT_HANDLERS = False
    handle_payment_succeeded = None  # type: ignore[assignment]
    handle_subscription_created = None  # type: ignore[assignment]
    handle_subscription_deleted = None  # type: ignore[assignment]
    handle_subscription_updated = None  # type: ignore[assignment]

# Stripe webhook handling
try:
    from protocols.billing.stripe_to_openmeter import StripeToOpenMeterBridge
    from protocols.billing.webhooks import WebhookEvent, create_webhook_handler

    HAS_BILLING = True
except ImportError:
    HAS_BILLING = False
    WebhookEvent = None  # type: ignore[misc, assignment]
    create_webhook_handler = None  # type: ignore[assignment]
    StripeToOpenMeterBridge = None  # type: ignore[misc, assignment]

# Stripe SDK
try:
    import stripe
    from stripe.error import SignatureVerificationError

    HAS_STRIPE = True
except ImportError:
    HAS_STRIPE = False
    stripe = None
    SignatureVerificationError = Exception  # noqa: N816

# OpenMeter client for bridging
try:
    from protocols.config import get_saas_clients

    HAS_SAAS_CONFIG = True
except ImportError:
    HAS_SAAS_CONFIG = False
    get_saas_clients = None  # type: ignore[assignment]

# Singleton instances
_stripe_bridge: Optional["StripeToOpenMeterBridge"] = None
_budget_store: Optional["BudgetStore"] = None
_telegram_notifier: Optional[Any] = None  # TelegramNotifier (lazy import)


def _get_budget_store() -> Optional["BudgetStore"]:
    """Get or create BudgetStore singleton."""
    global _budget_store

    if _budget_store is not None:
        return _budget_store

    if not HAS_BUDGET_STORE:
        logger.warning("BudgetStore not available, payment → credits disabled")
        return None

    _budget_store = InMemoryBudgetStore()
    logger.info("BudgetStore initialized for webhook processing")
    return _budget_store


def set_budget_store(store: "BudgetStore") -> None:
    """Set the BudgetStore instance (for dependency injection)."""
    global _budget_store
    _budget_store = store


def _get_telegram_notifier() -> Optional[Any]:
    """Get or create TelegramNotifier singleton."""
    global _telegram_notifier

    if _telegram_notifier is not None:
        return _telegram_notifier

    try:
        from agents.town.telegram_notifier import get_telegram_notifier

        _telegram_notifier = get_telegram_notifier()
        if _telegram_notifier.is_enabled:
            logger.info("TelegramNotifier initialized for webhook notifications")
        else:
            logger.debug("TelegramNotifier available but not enabled")
        return _telegram_notifier
    except ImportError:
        logger.debug("TelegramNotifier not available")
        return None


def set_telegram_notifier(notifier: Any) -> None:
    """Set the TelegramNotifier instance (for dependency injection/testing)."""
    global _telegram_notifier
    _telegram_notifier = notifier


def _get_stripe_bridge() -> Optional["StripeToOpenMeterBridge"]:
    """Get or create Stripe to OpenMeter bridge singleton."""
    global _stripe_bridge

    if _stripe_bridge is not None:
        return _stripe_bridge

    if not HAS_BILLING:
        logger.warning("Billing module not available, Stripe bridge disabled")
        return None

    # Try to get OpenMeter client from SaaS infrastructure
    openmeter_client = None
    if HAS_SAAS_CONFIG and get_saas_clients is not None:
        try:
            clients = get_saas_clients()
            openmeter_client = clients.openmeter
        except Exception as e:
            logger.warning(f"Could not get OpenMeter client: {e}")

    _stripe_bridge = StripeToOpenMeterBridge(openmeter_client=openmeter_client)
    logger.info("Stripe to OpenMeter bridge initialized")
    return _stripe_bridge


def create_webhooks_router() -> Optional["APIRouter"]:
    """
    Create webhooks router.

    Returns:
        APIRouter if FastAPI is available, None otherwise
    """
    if not HAS_FASTAPI:
        return None

    router = APIRouter(prefix="/webhooks", tags=["webhooks"])

    @router.post("/stripe")
    async def stripe_webhook(
        request: Request,
        stripe_signature: str = Header(None, alias="Stripe-Signature"),
    ) -> dict[str, Any]:
        """
        Handle Stripe webhook events.

        Processes subscription lifecycle events and forwards them to OpenMeter
        for billing reconciliation.

        Security:
        - Signature verification using STRIPE_WEBHOOK_SECRET
        - Idempotency to prevent duplicate processing

        Headers:
            Stripe-Signature: Stripe signature header

        Body:
            Raw Stripe webhook payload

        Returns:
            Processing status
        """
        import os

        # Get webhook secret
        webhook_secret = os.environ.get("STRIPE_WEBHOOK_SECRET")
        if not webhook_secret:
            logger.error("STRIPE_WEBHOOK_SECRET not configured")
            raise HTTPException(
                status_code=500,
                detail="Webhook secret not configured",
            )

        # Require signature header
        if not stripe_signature:
            raise HTTPException(
                status_code=400,
                detail="Missing Stripe-Signature header",
            )

        # Read raw body
        try:
            payload = await request.body()
        except Exception as e:
            logger.error(f"Failed to read request body: {e}")
            raise HTTPException(status_code=400, detail="Invalid request body")

        # Verify signature and construct event
        if not HAS_STRIPE:
            raise HTTPException(
                status_code=500,
                detail="Stripe SDK not installed",
            )

        try:
            stripe_event = stripe.Webhook.construct_event(
                payload,
                stripe_signature,
                webhook_secret,
            )
        except SignatureVerificationError as e:
            logger.warning(f"Invalid Stripe signature: {e}")
            raise HTTPException(status_code=400, detail="Invalid signature")
        except Exception as e:
            logger.error(f"Failed to construct Stripe event: {e}")
            raise HTTPException(status_code=400, detail="Invalid payload")

        # Convert to our WebhookEvent
        if not HAS_BILLING:
            logger.warning("Billing module not available")
            return {"status": "skipped", "reason": "billing_not_available"}

        webhook_event = WebhookEvent.from_stripe(dict(stripe_event))

        # Process event asynchronously (non-blocking)
        bridge = _get_stripe_bridge()
        if bridge is not None:
            # Fire-and-forget to OpenMeter
            asyncio.create_task(
                _process_stripe_event(bridge, webhook_event),
                name=f"stripe-webhook-{webhook_event.id}",
            )

        # Log event type
        logger.info(
            f"Received Stripe webhook: {webhook_event.type} ({webhook_event.id})"
        )

        # Always return 200 to acknowledge receipt
        return {
            "status": "received",
            "event_id": webhook_event.id,
            "event_type": webhook_event.type,
        }

    @router.get("/stripe/health")
    async def stripe_webhook_health() -> dict[str, Any]:
        """
        Check Stripe webhook bridge health.

        Returns metrics and configuration status.
        """
        import os

        response: dict[str, Any] = {
            "stripe_sdk": HAS_STRIPE,
            "billing_module": HAS_BILLING,
            "webhook_secret_configured": bool(os.environ.get("STRIPE_WEBHOOK_SECRET")),
        }

        bridge = _get_stripe_bridge()
        if bridge is not None:
            response["bridge_metrics"] = bridge.get_metrics()
            response["openmeter_connected"] = bridge.openmeter_client is not None
        else:
            response["bridge_status"] = "not_initialized"

        return response

    return router


async def _process_stripe_event(
    bridge: "StripeToOpenMeterBridge",
    event: "WebhookEvent",
) -> None:
    """
    Process Stripe event asynchronously.

    Handles:
    1. BudgetStore updates (payment → credits, subscription → tier)
    2. OpenMeter forwarding (for billing reconciliation)

    Errors are handled gracefully without affecting webhook response.
    """
    # Process BudgetStore updates
    await _process_budget_update(event)

    # Forward to OpenMeter
    try:
        processed = await bridge.process_event(event)
        if processed:
            logger.debug(f"Processed Stripe event via OpenMeter: {event.id}")
        else:
            logger.debug(f"Skipped Stripe event via OpenMeter: {event.id}")
    except Exception as e:
        logger.error(f"Failed to process Stripe event via OpenMeter {event.id}: {e}")


async def _process_budget_update(event: "WebhookEvent") -> None:
    """
    Process payment events and update BudgetStore.

    Per unified-v2.md Track C: Wire webhook → BudgetStore.
    Also sends Telegram notifications for Kent's motivation loop.
    """
    if not HAS_PAYMENT_HANDLERS or not HAS_BUDGET_STORE:
        logger.debug(
            "Payment handlers or BudgetStore not available, skipping budget update"
        )
        return

    budget_store = _get_budget_store()
    if budget_store is None:
        return

    # Get Telegram notifier (may be None if not configured)
    telegram = _get_telegram_notifier()

    event_type = event.type
    event_data = {"object": event.data}

    try:
        if event_type == "customer.subscription.created":
            result = handle_subscription_created(event_data)
            if result.get("user_id"):
                await budget_store.get_or_create(
                    result["user_id"], result.get("tier", "RESIDENT")
                )
                await budget_store.update_subscription(
                    result["user_id"],
                    result["tier"],
                    result["renews_at"],
                )
                logger.info(
                    f"BudgetStore: Created/updated subscription for {result['user_id']} → {result['tier']}"
                )

                # Kent's motivation loop: Telegram notification
                if telegram:
                    tier_prices = {"RESIDENT": 9.99, "CITIZEN": 29.99, "FOUNDER": 99.99}
                    amount = tier_prices.get(result["tier"], 0.0)
                    await telegram.notify_subscription(
                        user_id=result["user_id"],
                        tier=result["tier"],
                        renews_at=result["renews_at"],
                    )
                    if amount > 0:
                        await telegram.notify_payment(
                            user_id=result["user_id"],
                            amount=amount,
                            tier=result["tier"],
                        )

        elif event_type == "customer.subscription.updated":
            result = handle_subscription_updated(event_data)
            if result.get("user_id"):
                # Handle status changes (e.g., cancel, pause)
                if result.get("status") in ("canceled", "unpaid"):
                    await budget_store.update_subscription(
                        result["user_id"],
                        "TOURIST",
                        result["renews_at"],
                    )
                    logger.info(
                        f"BudgetStore: Downgraded {result['user_id']} → TOURIST (status={result['status']})"
                    )
                else:
                    await budget_store.update_subscription(
                        result["user_id"],
                        result["tier"],
                        result["renews_at"],
                    )
                    logger.info(
                        f"BudgetStore: Updated subscription for {result['user_id']} → {result['tier']}"
                    )

        elif event_type == "customer.subscription.deleted":
            result = handle_subscription_deleted(event_data)
            if result.get("user_id"):
                # Downgrade to TOURIST on subscription cancellation
                from datetime import datetime

                await budget_store.update_subscription(
                    result["user_id"],
                    "TOURIST",
                    datetime.now(),
                )
                logger.info(
                    f"BudgetStore: Subscription deleted, downgraded {result['user_id']} → TOURIST"
                )

                # Telegram notification for cancellation (awareness, not celebration)
                if telegram:
                    await telegram.notify_cancellation(
                        user_id=result["user_id"],
                        tier=result.get("tier", "UNKNOWN"),
                    )

        elif event_type == "payment_intent.succeeded":
            result = handle_payment_succeeded(event_data)
            if result.get("user_id") and result.get("credits", 0) > 0:
                # Add credits from credit pack purchase
                await budget_store.get_or_create(
                    result["user_id"]
                )  # Ensure user exists
                await budget_store.add_credits(result["user_id"], result["credits"])
                logger.info(
                    f"BudgetStore: Added {result['credits']} credits to {result['user_id']} (pack={result.get('pack')})"
                )

                # Kent's motivation loop: Credit pack sold!
                if telegram:
                    pack_prices = {
                        "STARTER": 5.00,
                        "EXPLORER": 20.00,
                        "ADVENTURER": 60.00,
                    }
                    amount = pack_prices.get(result.get("pack", ""), 0.0)
                    await telegram.notify_payment(
                        user_id=result["user_id"],
                        amount=amount,
                        tier="CREDITS",
                        pack=result.get("pack"),
                        credits=result["credits"],
                    )

    except Exception as e:
        logger.error(f"Failed to update BudgetStore for {event_type}: {e}")


def reset_stripe_bridge() -> None:
    """
    Reset Stripe bridge singleton.

    For testing only.
    """
    global _stripe_bridge
    _stripe_bridge = None


def reset_budget_store() -> None:
    """
    Reset BudgetStore singleton.

    For testing only.
    """
    global _budget_store
    _budget_store = None


def reset_telegram_notifier() -> None:
    """
    Reset TelegramNotifier singleton.

    For testing only.
    """
    global _telegram_notifier
    _telegram_notifier = None


def reset_all() -> None:
    """
    Reset all singletons.

    For testing only.
    """
    reset_stripe_bridge()
    reset_budget_store()
    reset_telegram_notifier()
