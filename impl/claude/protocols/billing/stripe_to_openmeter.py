"""
Stripe to OpenMeter Event Translation.

Translates Stripe webhook events into OpenMeter usage events for billing reconciliation.

Event Mapping:
    - checkout.session.completed → subscription.started
    - customer.subscription.updated → subscription.updated
    - customer.subscription.deleted → subscription.ended
    - invoice.paid → payment.success
    - invoice.payment_failed → payment.failed

Usage:
    from protocols.billing.stripe_to_openmeter import StripeToOpenMeterBridge

    bridge = StripeToOpenMeterBridge(openmeter_client)
    await bridge.process_event(webhook_event)
"""

from __future__ import annotations

import logging
from dataclasses import dataclass, field
from datetime import UTC, datetime
from enum import Enum
from typing import TYPE_CHECKING, Any, Optional
from uuid import uuid4

if TYPE_CHECKING:
    from .openmeter_client import OpenMeterClient

from .webhooks import WebhookEvent, WebhookEventType

logger = logging.getLogger(__name__)


class SubscriptionEventType(str, Enum):
    """OpenMeter event types for subscription lifecycle."""

    SUBSCRIPTION_STARTED = "subscription.started"
    SUBSCRIPTION_UPDATED = "subscription.updated"
    SUBSCRIPTION_ENDED = "subscription.ended"
    PAYMENT_SUCCESS = "payment.success"
    PAYMENT_FAILED = "payment.failed"


@dataclass
class SubscriptionEvent:
    """
    Subscription event for OpenMeter.

    CloudEvents-compatible format for OpenMeter ingestion.
    """

    id: str
    source: str
    type: str
    subject: str  # Customer ID (tenant)
    time: str
    data: dict[str, Any]

    def to_dict(self) -> dict[str, Any]:
        """Convert to OpenMeter event format."""
        return {
            "id": self.id,
            "source": self.source,
            "type": self.type,
            "subject": self.subject,
            "time": self.time,
            "data": self.data,
        }

    @classmethod
    def create(
        cls,
        event_type: SubscriptionEventType,
        customer_id: str,
        data: dict[str, Any],
        source: str = "kgents-stripe-bridge",
    ) -> "SubscriptionEvent":
        """Create a subscription event."""
        return cls(
            id=str(uuid4()),
            source=source,
            type=event_type.value,
            subject=customer_id,
            time=datetime.now(UTC).isoformat(),
            data=data,
        )


# Legacy IdempotencyStore kept for backwards compatibility
# New code should use protocols.billing.idempotency.get_idempotency_store()
@dataclass
class IdempotencyStore:
    """
    In-memory idempotency store for webhook events.

    DEPRECATED: Use protocols.billing.idempotency.get_idempotency_store()
    for Redis-backed storage in production.

    Prevents duplicate processing of webhook events.
    """

    _processed: dict[str, datetime] = field(default_factory=dict, init=False)
    max_age_seconds: int = 86400  # 24 hours

    def is_processed(self, event_id: str) -> bool:
        """Check if event has been processed."""
        self._cleanup()
        return event_id in self._processed

    def mark_processed(self, event_id: str) -> None:
        """Mark event as processed."""
        self._processed[event_id] = datetime.now(UTC)

    def _cleanup(self) -> None:
        """Remove expired entries."""
        now = datetime.now(UTC)
        expired = [
            eid
            for eid, ts in self._processed.items()
            if (now - ts).total_seconds() > self.max_age_seconds
        ]
        for eid in expired:
            del self._processed[eid]

    async def check_and_set(self, event_id: str) -> bool:
        """
        Async-compatible check-and-set for interface compatibility.

        Returns True if event is new, False if duplicate.
        """
        if self.is_processed(event_id):
            return False
        self.mark_processed(event_id)
        return True


@dataclass
class StripeToOpenMeterBridge:
    """
    Bridge for translating Stripe events to OpenMeter.

    Processes Stripe webhook events and forwards them as
    usage events to OpenMeter for billing reconciliation.
    """

    openmeter_client: Optional["OpenMeterClient"] = None
    idempotency_store: IdempotencyStore = field(default_factory=IdempotencyStore)

    # Metrics
    _events_processed: int = field(default=0, init=False)
    _events_skipped: int = field(default=0, init=False)
    _events_failed: int = field(default=0, init=False)

    async def process_event(self, event: WebhookEvent) -> bool:
        """
        Process a Stripe webhook event.

        Args:
            event: Stripe webhook event

        Returns:
            True if event was processed, False if skipped
        """
        # Check idempotency
        if self.idempotency_store.is_processed(event.id):
            logger.debug(f"Skipping duplicate event: {event.id}")
            self._events_skipped += 1
            return False

        # Translate event
        subscription_event = self._translate_event(event)
        if subscription_event is None:
            logger.debug(f"Unhandled event type: {event.type}")
            self._events_skipped += 1
            return False

        # Send to OpenMeter
        try:
            if self.openmeter_client is not None:
                # Use the client's event buffer
                await self._send_to_openmeter(subscription_event)
            else:
                # No client, just log
                logger.info(
                    f"OpenMeter event (no client): {subscription_event.type} "
                    f"for {subscription_event.subject}"
                )

            self.idempotency_store.mark_processed(event.id)
            self._events_processed += 1
            return True

        except Exception as e:
            logger.error(f"Failed to process Stripe event {event.id}: {e}")
            self._events_failed += 1
            return False

    def _translate_event(self, event: WebhookEvent) -> Optional[SubscriptionEvent]:
        """
        Translate Stripe event to OpenMeter event.

        Returns None for unhandled event types.
        """
        # Get customer ID from event data
        customer_id = self._extract_customer_id(event)
        if not customer_id:
            logger.warning(f"No customer ID in event {event.id}")
            return None

        # Checkout session completed
        if event.type == WebhookEventType.CHECKOUT_SESSION_COMPLETED.value:
            return self._translate_checkout_completed(event, customer_id)

        # Subscription created
        if event.type == WebhookEventType.SUBSCRIPTION_CREATED.value:
            return self._translate_subscription_created(event, customer_id)

        # Subscription updated
        if event.type == WebhookEventType.SUBSCRIPTION_UPDATED.value:
            return self._translate_subscription_updated(event, customer_id)

        # Subscription deleted
        if event.type == WebhookEventType.SUBSCRIPTION_DELETED.value:
            return self._translate_subscription_deleted(event, customer_id)

        # Invoice paid
        if event.type == WebhookEventType.INVOICE_PAID.value:
            return self._translate_invoice_paid(event, customer_id)

        # Invoice payment failed
        if event.type == WebhookEventType.INVOICE_PAYMENT_FAILED.value:
            return self._translate_invoice_failed(event, customer_id)

        return None

    def _extract_customer_id(self, event: WebhookEvent) -> Optional[str]:
        """Extract customer ID from event data."""
        # Direct customer field
        if "customer" in event.data:
            return str(event.data["customer"])

        # Customer object
        if "customer" in event.data and isinstance(event.data["customer"], dict):
            return event.data["customer"].get("id")

        return None

    def _translate_checkout_completed(
        self, event: WebhookEvent, customer_id: str
    ) -> SubscriptionEvent:
        """Translate checkout.session.completed to subscription.started."""
        session = event.data
        return SubscriptionEvent.create(
            event_type=SubscriptionEventType.SUBSCRIPTION_STARTED,
            customer_id=customer_id,
            data={
                "stripe_event_id": event.id,
                "checkout_session_id": session.get("id"),
                "subscription_id": session.get("subscription"),
                "mode": session.get("mode"),
                "amount_total": session.get("amount_total", 0)
                / 100,  # cents to dollars
                "currency": session.get("currency", "usd"),
            },
        )

    def _translate_subscription_created(
        self, event: WebhookEvent, customer_id: str
    ) -> SubscriptionEvent:
        """Translate customer.subscription.created to subscription.started."""
        subscription = event.data
        return SubscriptionEvent.create(
            event_type=SubscriptionEventType.SUBSCRIPTION_STARTED,
            customer_id=customer_id,
            data={
                "stripe_event_id": event.id,
                "subscription_id": subscription.get("id"),
                "status": subscription.get("status"),
                "plan_id": self._extract_plan_id(subscription),
                "quantity": self._extract_quantity(subscription),
                "trial_end": subscription.get("trial_end"),
            },
        )

    def _translate_subscription_updated(
        self, event: WebhookEvent, customer_id: str
    ) -> SubscriptionEvent:
        """Translate customer.subscription.updated to subscription.updated."""
        subscription = event.data
        return SubscriptionEvent.create(
            event_type=SubscriptionEventType.SUBSCRIPTION_UPDATED,
            customer_id=customer_id,
            data={
                "stripe_event_id": event.id,
                "subscription_id": subscription.get("id"),
                "status": subscription.get("status"),
                "plan_id": self._extract_plan_id(subscription),
                "quantity": self._extract_quantity(subscription),
                "cancel_at_period_end": subscription.get("cancel_at_period_end", False),
            },
        )

    def _translate_subscription_deleted(
        self, event: WebhookEvent, customer_id: str
    ) -> SubscriptionEvent:
        """Translate customer.subscription.deleted to subscription.ended."""
        subscription = event.data
        return SubscriptionEvent.create(
            event_type=SubscriptionEventType.SUBSCRIPTION_ENDED,
            customer_id=customer_id,
            data={
                "stripe_event_id": event.id,
                "subscription_id": subscription.get("id"),
                "canceled_at": subscription.get("canceled_at"),
                "ended_at": subscription.get("ended_at"),
            },
        )

    def _translate_invoice_paid(
        self, event: WebhookEvent, customer_id: str
    ) -> SubscriptionEvent:
        """Translate invoice.paid to payment.success."""
        invoice = event.data
        return SubscriptionEvent.create(
            event_type=SubscriptionEventType.PAYMENT_SUCCESS,
            customer_id=customer_id,
            data={
                "stripe_event_id": event.id,
                "invoice_id": invoice.get("id"),
                "subscription_id": invoice.get("subscription"),
                "amount_paid": invoice.get("amount_paid", 0) / 100,
                "currency": invoice.get("currency", "usd"),
                "billing_reason": invoice.get("billing_reason"),
            },
        )

    def _translate_invoice_failed(
        self, event: WebhookEvent, customer_id: str
    ) -> SubscriptionEvent:
        """Translate invoice.payment_failed to payment.failed."""
        invoice = event.data
        return SubscriptionEvent.create(
            event_type=SubscriptionEventType.PAYMENT_FAILED,
            customer_id=customer_id,
            data={
                "stripe_event_id": event.id,
                "invoice_id": invoice.get("id"),
                "subscription_id": invoice.get("subscription"),
                "amount_due": invoice.get("amount_due", 0) / 100,
                "currency": invoice.get("currency", "usd"),
                "attempt_count": invoice.get("attempt_count", 0),
                "next_payment_attempt": invoice.get("next_payment_attempt"),
            },
        )

    def _extract_plan_id(self, subscription: dict[str, Any]) -> Optional[str]:
        """Extract plan ID from subscription items."""
        items = subscription.get("items", {}).get("data", [])
        if items:
            plan_id: str | None = items[0].get("price", {}).get("id")
            return plan_id
        return None

    def _extract_quantity(self, subscription: dict[str, Any]) -> int:
        """Extract quantity from subscription items."""
        items = subscription.get("items", {}).get("data", [])
        if items:
            quantity: int = items[0].get("quantity", 1)
            return quantity
        return 1

    async def _send_to_openmeter(self, event: SubscriptionEvent) -> None:
        """
        Send subscription event to OpenMeter.

        Uses the OpenMeterClient's buffer for batching.
        """
        if self.openmeter_client is None:
            return

        # Import here to avoid circular dependency
        from .openmeter_client import UsageEventSchema

        # Convert to OpenMeter format
        usage_event = UsageEventSchema(
            id=event.id,
            source=event.source,
            type=event.type,
            subject=event.subject,
            time=event.time,
            data=event.data,
        )

        # Add to buffer (uses internal method)
        await self.openmeter_client._buffer_event(usage_event)

        logger.debug(f"Sent subscription event to OpenMeter: {event.type}")

    def get_metrics(self) -> dict[str, Any]:
        """Get bridge metrics."""
        return {
            "events_processed": self._events_processed,
            "events_skipped": self._events_skipped,
            "events_failed": self._events_failed,
            "idempotency_store_size": len(self.idempotency_store._processed),
        }
