"""Tests for webhook handling."""

# Get the mocked stripe from sys.modules (set up in conftest.py)
import sys
from typing import Any
from unittest.mock import MagicMock, patch

import pytest

from protocols.billing.webhooks import (
    DefaultWebhookHandlers,
    WebhookEvent,
    WebhookEventType,
    WebhookHandler,
    create_webhook_handler,
)

mock_stripe = sys.modules["stripe"]


@pytest.fixture
def webhook_handler() -> WebhookHandler:
    """Create webhook handler with mocked stripe."""
    with patch("protocols.billing.webhooks.STRIPE_AVAILABLE", True):
        return WebhookHandler("whsec_test123")


def make_stripe_event(
    event_id: str = "evt_test123",
    event_type: str = "customer.created",
    data: dict[str, Any] | None = None,
    created: int = 1234567890,
) -> dict[str, Any]:
    """Create a mock Stripe event object."""
    return {
        "id": event_id,
        "type": event_type,
        "data": {"object": data or {"id": "obj_test123"}},
        "created": created,
        "object": "event",
    }


class TestWebhookEvent:
    """Tests for WebhookEvent dataclass."""

    def test_from_stripe(self) -> None:
        """Test creating WebhookEvent from Stripe object."""
        stripe_event = make_stripe_event(
            event_id="evt_abc123",
            event_type="customer.subscription.created",
            data={"id": "sub_abc123", "customer": "cus_abc123"},
            created=1234567890,
        )

        event = WebhookEvent.from_stripe(stripe_event)

        assert event.id == "evt_abc123"
        assert event.type == "customer.subscription.created"
        assert event.data == {"id": "sub_abc123", "customer": "cus_abc123"}
        assert event.created == 1234567890


class TestWebhookHandler:
    """Tests for WebhookHandler."""

    def test_init_without_stripe(self) -> None:
        """Test initialization fails without stripe package."""
        with patch("protocols.billing.webhooks.STRIPE_AVAILABLE", False):
            with pytest.raises(RuntimeError, match="stripe package not installed"):
                WebhookHandler("whsec_test123")

    def test_register_handler(self, webhook_handler: WebhookHandler) -> None:
        """Test registering a handler for an event type."""
        handler_called = False

        def test_handler(event: WebhookEvent) -> None:
            nonlocal handler_called
            handler_called = True

        webhook_handler.register_handler(WebhookEventType.CUSTOMER_CREATED, test_handler)

        # Verify handler is registered
        assert WebhookEventType.CUSTOMER_CREATED.value in webhook_handler._handlers
        assert len(webhook_handler._handlers[WebhookEventType.CUSTOMER_CREATED.value]) == 1

    def test_register_multiple_handlers(self, webhook_handler: WebhookHandler) -> None:
        """Test registering multiple handlers for same event type."""

        def handler1(event: WebhookEvent) -> None:
            pass

        def handler2(event: WebhookEvent) -> None:
            pass

        webhook_handler.register_handler(WebhookEventType.CUSTOMER_CREATED, handler1)
        webhook_handler.register_handler(WebhookEventType.CUSTOMER_CREATED, handler2)

        handlers = webhook_handler._handlers[WebhookEventType.CUSTOMER_CREATED.value]
        assert len(handlers) == 2
        assert handler1 in handlers
        assert handler2 in handlers

    def test_handle_event(self, webhook_handler: WebhookHandler) -> None:
        """Test handling an event calls registered handlers."""
        handler_called = False
        received_event = None

        def test_handler(event: WebhookEvent) -> None:
            nonlocal handler_called, received_event
            handler_called = True
            received_event = event

        webhook_handler.register_handler(WebhookEventType.CUSTOMER_CREATED, test_handler)

        event = WebhookEvent(
            id="evt_test",
            type=WebhookEventType.CUSTOMER_CREATED.value,
            data={"id": "cus_test"},
            created=1234567890,
        )

        result = webhook_handler.handle_event(event)

        assert result is True
        assert handler_called is True
        assert received_event == event

    def test_handle_event_no_handlers(self, webhook_handler: WebhookHandler) -> None:
        """Test handling event with no registered handlers returns False."""
        event = WebhookEvent(
            id="evt_test",
            type="unknown.event",
            data={},
            created=1234567890,
        )

        result = webhook_handler.handle_event(event)

        assert result is False

    def test_handle_event_multiple_handlers(self, webhook_handler: WebhookHandler) -> None:
        """Test all handlers are called for an event."""
        handler1_called = False
        handler2_called = False

        def handler1(event: WebhookEvent) -> None:
            nonlocal handler1_called
            handler1_called = True

        def handler2(event: WebhookEvent) -> None:
            nonlocal handler2_called
            handler2_called = True

        webhook_handler.register_handler(WebhookEventType.CUSTOMER_CREATED, handler1)
        webhook_handler.register_handler(WebhookEventType.CUSTOMER_CREATED, handler2)

        event = WebhookEvent(
            id="evt_test",
            type=WebhookEventType.CUSTOMER_CREATED.value,
            data={},
            created=1234567890,
        )

        webhook_handler.handle_event(event)

        assert handler1_called is True
        assert handler2_called is True

    def test_handle_event_handler_exception(
        self, webhook_handler: WebhookHandler, capsys: pytest.CaptureFixture[str]
    ) -> None:
        """Test handler exception doesn't stop other handlers."""
        handler2_called = False

        def failing_handler(event: WebhookEvent) -> None:
            raise ValueError("Handler failed")

        def handler2(event: WebhookEvent) -> None:
            nonlocal handler2_called
            handler2_called = True

        webhook_handler.register_handler(WebhookEventType.CUSTOMER_CREATED, failing_handler)
        webhook_handler.register_handler(WebhookEventType.CUSTOMER_CREATED, handler2)

        event = WebhookEvent(
            id="evt_test",
            type=WebhookEventType.CUSTOMER_CREATED.value,
            data={},
            created=1234567890,
        )

        result = webhook_handler.handle_event(event)

        assert result is True
        assert handler2_called is True

        # Check error was printed
        captured = capsys.readouterr()
        assert "Error in webhook handler" in captured.out

    def test_construct_event(self, webhook_handler: WebhookHandler) -> None:
        """Test constructing and verifying webhook event."""
        stripe_event = make_stripe_event(
            event_id="evt_construct",
            event_type="invoice.paid",
        )
        mock_stripe.Webhook.construct_event.return_value = stripe_event

        event = webhook_handler.construct_event(b"payload", "sig_header")

        assert event.id == "evt_construct"
        assert event.type == "invoice.paid"
        mock_stripe.Webhook.construct_event.assert_called_once_with(
            b"payload", "sig_header", "whsec_test123"
        )


class TestDefaultWebhookHandlers:
    """Tests for DefaultWebhookHandlers."""

    def test_on_customer_created(self, capsys: pytest.CaptureFixture[str]) -> None:
        """Test customer.created handler."""
        event = WebhookEvent(
            id="evt_test",
            type="customer.created",
            data={"id": "cus_123", "email": "test@example.com"},
            created=1234567890,
        )

        DefaultWebhookHandlers.on_customer_created(event)

        captured = capsys.readouterr()
        assert "Customer created: cus_123 (test@example.com)" in captured.out

    def test_on_customer_updated(self, capsys: pytest.CaptureFixture[str]) -> None:
        """Test customer.updated handler."""
        event = WebhookEvent(
            id="evt_test",
            type="customer.updated",
            data={"id": "cus_123"},
            created=1234567890,
        )

        DefaultWebhookHandlers.on_customer_updated(event)

        captured = capsys.readouterr()
        assert "Customer updated: cus_123" in captured.out

    def test_on_customer_deleted(self, capsys: pytest.CaptureFixture[str]) -> None:
        """Test customer.deleted handler."""
        event = WebhookEvent(
            id="evt_test",
            type="customer.deleted",
            data={"id": "cus_123"},
            created=1234567890,
        )

        DefaultWebhookHandlers.on_customer_deleted(event)

        captured = capsys.readouterr()
        assert "Customer deleted: cus_123" in captured.out

    def test_on_subscription_created(self, capsys: pytest.CaptureFixture[str]) -> None:
        """Test customer.subscription.created handler."""
        event = WebhookEvent(
            id="evt_test",
            type="customer.subscription.created",
            data={"id": "sub_123", "customer": "cus_123"},
            created=1234567890,
        )

        DefaultWebhookHandlers.on_subscription_created(event)

        captured = capsys.readouterr()
        assert "Subscription created: sub_123 for customer cus_123" in captured.out

    def test_on_subscription_updated(self, capsys: pytest.CaptureFixture[str]) -> None:
        """Test customer.subscription.updated handler."""
        event = WebhookEvent(
            id="evt_test",
            type="customer.subscription.updated",
            data={"id": "sub_123", "status": "active"},
            created=1234567890,
        )

        DefaultWebhookHandlers.on_subscription_updated(event)

        captured = capsys.readouterr()
        assert "Subscription updated: sub_123 - status: active" in captured.out

    def test_on_subscription_deleted(self, capsys: pytest.CaptureFixture[str]) -> None:
        """Test customer.subscription.deleted handler."""
        event = WebhookEvent(
            id="evt_test",
            type="customer.subscription.deleted",
            data={"id": "sub_123", "customer": "cus_123"},
            created=1234567890,
        )

        DefaultWebhookHandlers.on_subscription_deleted(event)

        captured = capsys.readouterr()
        assert "Subscription deleted: sub_123 for customer cus_123" in captured.out

    def test_on_invoice_paid(self, capsys: pytest.CaptureFixture[str]) -> None:
        """Test invoice.paid handler."""
        event = WebhookEvent(
            id="evt_test",
            type="invoice.paid",
            data={"id": "in_123", "customer": "cus_123", "amount_paid": 2999},
            created=1234567890,
        )

        DefaultWebhookHandlers.on_invoice_paid(event)

        captured = capsys.readouterr()
        assert "Invoice paid: in_123 for customer cus_123 - amount: $29.99" in captured.out

    def test_on_invoice_payment_failed(self, capsys: pytest.CaptureFixture[str]) -> None:
        """Test invoice.payment_failed handler."""
        event = WebhookEvent(
            id="evt_test",
            type="invoice.payment_failed",
            data={"id": "in_123", "customer": "cus_123"},
            created=1234567890,
        )

        DefaultWebhookHandlers.on_invoice_payment_failed(event)

        captured = capsys.readouterr()
        assert "Invoice payment failed: in_123 for customer cus_123" in captured.out

    def test_on_checkout_session_completed(self, capsys: pytest.CaptureFixture[str]) -> None:
        """Test checkout.session.completed handler."""
        event = WebhookEvent(
            id="evt_test",
            type="checkout.session.completed",
            data={"id": "cs_123", "customer": "cus_123"},
            created=1234567890,
        )

        DefaultWebhookHandlers.on_checkout_session_completed(event)

        captured = capsys.readouterr()
        assert "Checkout session completed: cs_123 - customer: cus_123" in captured.out


class TestCreateWebhookHandler:
    """Tests for create_webhook_handler factory."""

    def test_create_webhook_handler(self) -> None:
        """Test factory creates handler with default handlers registered."""
        with patch("protocols.billing.webhooks.STRIPE_AVAILABLE", True):
            handler = create_webhook_handler("whsec_test123")

            # Verify all default handlers are registered
            expected_events = [
                WebhookEventType.CUSTOMER_CREATED,
                WebhookEventType.CUSTOMER_UPDATED,
                WebhookEventType.CUSTOMER_DELETED,
                WebhookEventType.SUBSCRIPTION_CREATED,
                WebhookEventType.SUBSCRIPTION_UPDATED,
                WebhookEventType.SUBSCRIPTION_DELETED,
                WebhookEventType.INVOICE_PAID,
                WebhookEventType.INVOICE_PAYMENT_FAILED,
                WebhookEventType.CHECKOUT_SESSION_COMPLETED,
            ]

            for event_type in expected_events:
                assert event_type.value in handler._handlers
                assert len(handler._handlers[event_type.value]) >= 1
