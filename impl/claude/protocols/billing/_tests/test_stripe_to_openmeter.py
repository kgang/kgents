"""
Tests for Stripe to OpenMeter bridge.

Tests event translation and idempotency handling.
"""

import pytest

from protocols.billing.stripe_to_openmeter import (
    IdempotencyStore,
    StripeToOpenMeterBridge,
    SubscriptionEvent,
    SubscriptionEventType,
)
from protocols.billing.webhooks import WebhookEvent

# --- Test Fixtures ---


@pytest.fixture
def bridge() -> StripeToOpenMeterBridge:
    """Create bridge without OpenMeter client."""
    return StripeToOpenMeterBridge()


@pytest.fixture
def idempotency_store() -> IdempotencyStore:
    """Create idempotency store."""
    return IdempotencyStore()


@pytest.fixture
def checkout_completed_event() -> WebhookEvent:
    """Create checkout.session.completed event."""
    return WebhookEvent(
        id="evt_checkout_123",
        type="checkout.session.completed",
        created=1702560000,
        data={
            "id": "cs_test_123",
            "customer": "cus_test_456",
            "subscription": "sub_test_789",
            "mode": "subscription",
            "amount_total": 9900,  # $99.00
            "currency": "usd",
        },
    )


@pytest.fixture
def subscription_updated_event() -> WebhookEvent:
    """Create customer.subscription.updated event."""
    return WebhookEvent(
        id="evt_sub_update_123",
        type="customer.subscription.updated",
        created=1702560000,
        data={
            "id": "sub_test_789",
            "customer": "cus_test_456",
            "status": "active",
            "cancel_at_period_end": False,
            "items": {
                "data": [
                    {
                        "price": {"id": "price_pro_monthly"},
                        "quantity": 1,
                    }
                ]
            },
        },
    )


@pytest.fixture
def subscription_deleted_event() -> WebhookEvent:
    """Create customer.subscription.deleted event."""
    return WebhookEvent(
        id="evt_sub_delete_123",
        type="customer.subscription.deleted",
        created=1702560000,
        data={
            "id": "sub_test_789",
            "customer": "cus_test_456",
            "canceled_at": 1702560000,
            "ended_at": 1702560000,
        },
    )


@pytest.fixture
def invoice_paid_event() -> WebhookEvent:
    """Create invoice.paid event."""
    return WebhookEvent(
        id="evt_invoice_paid_123",
        type="invoice.paid",
        created=1702560000,
        data={
            "id": "in_test_123",
            "customer": "cus_test_456",
            "subscription": "sub_test_789",
            "amount_paid": 9900,
            "currency": "usd",
            "billing_reason": "subscription_cycle",
        },
    )


@pytest.fixture
def invoice_failed_event() -> WebhookEvent:
    """Create invoice.payment_failed event."""
    return WebhookEvent(
        id="evt_invoice_failed_123",
        type="invoice.payment_failed",
        created=1702560000,
        data={
            "id": "in_test_456",
            "customer": "cus_test_456",
            "subscription": "sub_test_789",
            "amount_due": 9900,
            "currency": "usd",
            "attempt_count": 1,
            "next_payment_attempt": 1702646400,
        },
    )


# --- Idempotency Store Tests ---


class TestIdempotencyStore:
    """Tests for IdempotencyStore."""

    def test_is_processed_returns_false_for_new_event(
        self, idempotency_store: IdempotencyStore
    ) -> None:
        """New event should not be marked as processed."""
        assert not idempotency_store.is_processed("evt_new")

    def test_mark_processed_makes_is_processed_return_true(
        self, idempotency_store: IdempotencyStore
    ) -> None:
        """Marked event should return True."""
        idempotency_store.mark_processed("evt_test")
        assert idempotency_store.is_processed("evt_test")

    def test_multiple_events_tracked_independently(
        self, idempotency_store: IdempotencyStore
    ) -> None:
        """Multiple events tracked independently."""
        idempotency_store.mark_processed("evt_1")
        idempotency_store.mark_processed("evt_2")

        assert idempotency_store.is_processed("evt_1")
        assert idempotency_store.is_processed("evt_2")
        assert not idempotency_store.is_processed("evt_3")


# --- Subscription Event Tests ---


class TestSubscriptionEvent:
    """Tests for SubscriptionEvent."""

    def test_create_generates_unique_id(self) -> None:
        """Each event should have unique ID."""
        event1 = SubscriptionEvent.create(
            SubscriptionEventType.SUBSCRIPTION_STARTED,
            "cus_123",
            {"test": "data"},
        )
        event2 = SubscriptionEvent.create(
            SubscriptionEventType.SUBSCRIPTION_STARTED,
            "cus_123",
            {"test": "data"},
        )

        assert event1.id != event2.id

    def test_to_dict_returns_cloudevents_format(self) -> None:
        """to_dict should return CloudEvents-compatible format."""
        event = SubscriptionEvent.create(
            SubscriptionEventType.PAYMENT_SUCCESS,
            "cus_test",
            {"amount": 99.0},
        )

        d = event.to_dict()

        assert "id" in d
        assert "source" in d
        assert "type" in d
        assert "subject" in d
        assert "time" in d
        assert "data" in d

        assert d["type"] == "payment.success"
        assert d["subject"] == "cus_test"
        assert d["data"]["amount"] == 99.0


# --- Bridge Translation Tests ---


class TestStripeToOpenMeterBridge:
    """Tests for StripeToOpenMeterBridge."""

    @pytest.mark.anyio
    async def test_process_checkout_completed(
        self, bridge: StripeToOpenMeterBridge, checkout_completed_event: WebhookEvent
    ) -> None:
        """Checkout completed should translate to subscription.started."""
        result = await bridge.process_event(checkout_completed_event)

        assert result is True
        assert bridge._events_processed == 1

    @pytest.mark.anyio
    async def test_process_subscription_updated(
        self, bridge: StripeToOpenMeterBridge, subscription_updated_event: WebhookEvent
    ) -> None:
        """Subscription updated should translate to subscription.updated."""
        result = await bridge.process_event(subscription_updated_event)

        assert result is True
        assert bridge._events_processed == 1

    @pytest.mark.anyio
    async def test_process_subscription_deleted(
        self, bridge: StripeToOpenMeterBridge, subscription_deleted_event: WebhookEvent
    ) -> None:
        """Subscription deleted should translate to subscription.ended."""
        result = await bridge.process_event(subscription_deleted_event)

        assert result is True
        assert bridge._events_processed == 1

    @pytest.mark.anyio
    async def test_process_invoice_paid(
        self, bridge: StripeToOpenMeterBridge, invoice_paid_event: WebhookEvent
    ) -> None:
        """Invoice paid should translate to payment.success."""
        result = await bridge.process_event(invoice_paid_event)

        assert result is True
        assert bridge._events_processed == 1

    @pytest.mark.anyio
    async def test_process_invoice_failed(
        self, bridge: StripeToOpenMeterBridge, invoice_failed_event: WebhookEvent
    ) -> None:
        """Invoice payment failed should translate to payment.failed."""
        result = await bridge.process_event(invoice_failed_event)

        assert result is True
        assert bridge._events_processed == 1

    @pytest.mark.anyio
    async def test_idempotency_prevents_duplicate_processing(
        self, bridge: StripeToOpenMeterBridge, checkout_completed_event: WebhookEvent
    ) -> None:
        """Same event should only be processed once."""
        result1 = await bridge.process_event(checkout_completed_event)
        result2 = await bridge.process_event(checkout_completed_event)

        assert result1 is True
        assert result2 is False
        assert bridge._events_processed == 1
        assert bridge._events_skipped == 1

    @pytest.mark.anyio
    async def test_unhandled_event_type_skipped(self, bridge: StripeToOpenMeterBridge) -> None:
        """Unhandled event types should be skipped."""
        event = WebhookEvent(
            id="evt_unknown",
            type="unknown.event.type",
            created=1702560000,
            data={"customer": "cus_test"},
        )

        result = await bridge.process_event(event)

        assert result is False
        assert bridge._events_skipped == 1

    @pytest.mark.anyio
    async def test_event_without_customer_id_skipped(self, bridge: StripeToOpenMeterBridge) -> None:
        """Events without customer ID should be skipped."""
        event = WebhookEvent(
            id="evt_no_customer",
            type="checkout.session.completed",
            created=1702560000,
            data={"id": "cs_test"},  # No customer field
        )

        result = await bridge.process_event(event)

        assert result is False
        assert bridge._events_skipped == 1

    def test_get_metrics(self, bridge: StripeToOpenMeterBridge) -> None:
        """get_metrics should return all metrics."""
        metrics = bridge.get_metrics()

        assert "events_processed" in metrics
        assert "events_skipped" in metrics
        assert "events_failed" in metrics
        assert "idempotency_store_size" in metrics
