"""
Webhook endpoints for kgents SaaS API.

Handles external webhooks from:
- Stripe (subscription lifecycle events)

Security:
- Signature verification for all webhooks
- Idempotency handling to prevent duplicate processing
- Non-blocking processing via asyncio.create_task

Usage:
    from protocols.api.webhooks import create_webhooks_router

    router = create_webhooks_router()
    app.include_router(router)
"""

from __future__ import annotations

import asyncio
import logging
from typing import Any, Optional

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

# Singleton bridge instance
_stripe_bridge: Optional["StripeToOpenMeterBridge"] = None


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

    Handles errors gracefully without affecting webhook response.
    """
    try:
        processed = await bridge.process_event(event)
        if processed:
            logger.debug(f"Processed Stripe event: {event.id}")
        else:
            logger.debug(f"Skipped Stripe event: {event.id}")
    except Exception as e:
        logger.error(f"Failed to process Stripe event {event.id}: {e}")


def reset_stripe_bridge() -> None:
    """
    Reset Stripe bridge singleton.

    For testing only.
    """
    global _stripe_bridge
    _stripe_bridge = None
