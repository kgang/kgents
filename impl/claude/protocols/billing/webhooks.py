"""
Webhook handler for Stripe events.

Processes various Stripe webhook events for subscription lifecycle management.
"""

from dataclasses import dataclass
from enum import Enum
from typing import Any, Callable, Optional, Protocol

try:
    import stripe
    from stripe import StripeError

    STRIPE_AVAILABLE = True
except ImportError:
    STRIPE_AVAILABLE = False
    StripeError = Exception  # noqa: N816


class WebhookEventType(Enum):
    """Stripe webhook event types we handle."""

    CUSTOMER_CREATED = "customer.created"
    CUSTOMER_UPDATED = "customer.updated"
    CUSTOMER_DELETED = "customer.deleted"
    SUBSCRIPTION_CREATED = "customer.subscription.created"
    SUBSCRIPTION_UPDATED = "customer.subscription.updated"
    SUBSCRIPTION_DELETED = "customer.subscription.deleted"
    INVOICE_PAID = "invoice.paid"
    INVOICE_PAYMENT_FAILED = "invoice.payment_failed"
    CHECKOUT_SESSION_COMPLETED = "checkout.session.completed"


@dataclass(frozen=True)
class WebhookEvent:
    """Represents a Stripe webhook event."""

    id: str
    type: str
    data: dict[str, Any]
    created: int

    @classmethod
    def from_stripe(cls, stripe_event: dict[str, Any]) -> "WebhookEvent":
        """Create WebhookEvent from Stripe event object."""
        return cls(
            id=stripe_event["id"],
            type=stripe_event["type"],
            data=stripe_event["data"]["object"],
            created=stripe_event["created"],
        )


# Type alias for webhook handlers
WebhookHandlerFunc = Callable[[WebhookEvent], None]


class WebhookHandlerProtocol(Protocol):
    """Protocol for webhook handling operations."""

    def register_handler(self, event_type: WebhookEventType, handler: WebhookHandlerFunc) -> None:
        """Register a handler for a specific event type."""
        ...

    def handle_event(self, event: WebhookEvent) -> bool:
        """Handle a webhook event."""
        ...

    def construct_event(self, payload: bytes, sig_header: str) -> WebhookEvent:
        """Construct and verify a webhook event."""
        ...


class WebhookHandler:
    """
    Handles Stripe webhook events.

    Provides event registration and dispatching with proper signature verification.
    """

    def __init__(self, webhook_secret: str) -> None:
        """
        Initialize webhook handler.

        Args:
            webhook_secret: Stripe webhook signing secret
        """
        if not STRIPE_AVAILABLE:
            raise RuntimeError("stripe package not installed. Install with: pip install stripe")

        self._webhook_secret = webhook_secret
        self._handlers: dict[str, list[WebhookHandlerFunc]] = {}

    def register_handler(self, event_type: WebhookEventType, handler: WebhookHandlerFunc) -> None:
        """
        Register a handler for a specific event type.

        Args:
            event_type: Type of event to handle
            handler: Handler function to call when event occurs
        """
        event_type_str = event_type.value
        if event_type_str not in self._handlers:
            self._handlers[event_type_str] = []
        self._handlers[event_type_str].append(handler)

    def handle_event(self, event: WebhookEvent) -> bool:
        """
        Handle a webhook event by dispatching to registered handlers.

        Args:
            event: Webhook event to handle

        Returns:
            True if at least one handler was called, False otherwise
        """
        handlers = self._handlers.get(event.type, [])
        if not handlers:
            return False

        for handler in handlers:
            try:
                handler(event)
            except Exception as e:
                # Log error but continue processing other handlers
                print(f"Error in webhook handler for {event.type}: {e}")

        return True

    def construct_event(self, payload: bytes, sig_header: str) -> WebhookEvent:
        """
        Construct and verify a webhook event from raw request data.

        Args:
            payload: Raw request body as bytes
            sig_header: Value of Stripe-Signature header

        Returns:
            Verified WebhookEvent

        Raises:
            stripe.error.SignatureVerificationError: If signature is invalid
        """
        event = stripe.Webhook.construct_event(payload, sig_header, self._webhook_secret)
        return WebhookEvent.from_stripe(dict(event))


class DefaultWebhookHandlers:
    """
    Collection of default webhook handlers.

    These handlers can be registered with a WebhookHandler to process
    common subscription lifecycle events.
    """

    @staticmethod
    def on_customer_created(event: WebhookEvent) -> None:
        """Handle customer.created event."""
        customer = event.data
        print(f"Customer created: {customer['id']} ({customer['email']})")

    @staticmethod
    def on_customer_updated(event: WebhookEvent) -> None:
        """Handle customer.updated event."""
        customer = event.data
        print(f"Customer updated: {customer['id']}")

    @staticmethod
    def on_customer_deleted(event: WebhookEvent) -> None:
        """Handle customer.deleted event."""
        customer = event.data
        print(f"Customer deleted: {customer['id']}")

    @staticmethod
    def on_subscription_created(event: WebhookEvent) -> None:
        """Handle customer.subscription.created event."""
        subscription = event.data
        print(f"Subscription created: {subscription['id']} for customer {subscription['customer']}")

    @staticmethod
    def on_subscription_updated(event: WebhookEvent) -> None:
        """Handle customer.subscription.updated event."""
        subscription = event.data
        print(f"Subscription updated: {subscription['id']} - status: {subscription['status']}")

    @staticmethod
    def on_subscription_deleted(event: WebhookEvent) -> None:
        """Handle customer.subscription.deleted event."""
        subscription = event.data
        print(f"Subscription deleted: {subscription['id']} for customer {subscription['customer']}")

    @staticmethod
    def on_invoice_paid(event: WebhookEvent) -> None:
        """Handle invoice.paid event."""
        invoice = event.data
        print(
            f"Invoice paid: {invoice['id']} for customer {invoice['customer']} - amount: ${invoice['amount_paid'] / 100}"
        )

    @staticmethod
    def on_invoice_payment_failed(event: WebhookEvent) -> None:
        """Handle invoice.payment_failed event."""
        invoice = event.data
        print(f"Invoice payment failed: {invoice['id']} for customer {invoice['customer']}")

    @staticmethod
    def on_checkout_session_completed(event: WebhookEvent) -> None:
        """Handle checkout.session.completed event."""
        session = event.data
        print(f"Checkout session completed: {session['id']} - customer: {session.get('customer')}")


def create_webhook_handler(webhook_secret: str) -> WebhookHandler:
    """
    Factory function to create a webhook handler with default handlers registered.

    Args:
        webhook_secret: Stripe webhook signing secret

    Returns:
        Configured WebhookHandler instance
    """
    handler = WebhookHandler(webhook_secret)

    # Register default handlers
    handler.register_handler(
        WebhookEventType.CUSTOMER_CREATED, DefaultWebhookHandlers.on_customer_created
    )
    handler.register_handler(
        WebhookEventType.CUSTOMER_UPDATED, DefaultWebhookHandlers.on_customer_updated
    )
    handler.register_handler(
        WebhookEventType.CUSTOMER_DELETED, DefaultWebhookHandlers.on_customer_deleted
    )
    handler.register_handler(
        WebhookEventType.SUBSCRIPTION_CREATED,
        DefaultWebhookHandlers.on_subscription_created,
    )
    handler.register_handler(
        WebhookEventType.SUBSCRIPTION_UPDATED,
        DefaultWebhookHandlers.on_subscription_updated,
    )
    handler.register_handler(
        WebhookEventType.SUBSCRIPTION_DELETED,
        DefaultWebhookHandlers.on_subscription_deleted,
    )
    handler.register_handler(WebhookEventType.INVOICE_PAID, DefaultWebhookHandlers.on_invoice_paid)
    handler.register_handler(
        WebhookEventType.INVOICE_PAYMENT_FAILED,
        DefaultWebhookHandlers.on_invoice_payment_failed,
    )
    handler.register_handler(
        WebhookEventType.CHECKOUT_SESSION_COMPLETED,
        DefaultWebhookHandlers.on_checkout_session_completed,
    )

    return handler
