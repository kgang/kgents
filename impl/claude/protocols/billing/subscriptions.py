"""
Subscription lifecycle management for Stripe billing.

Handles subscription creation, retrieval, updates, and cancellations.
"""

from dataclasses import dataclass
from datetime import datetime
from enum import Enum
from typing import Any, Optional, Protocol

try:
    import stripe
    from stripe import StripeError

    STRIPE_AVAILABLE = True
except ImportError:
    STRIPE_AVAILABLE = False
    StripeError = Exception  # noqa: N816


class SubscriptionStatus(Enum):
    """Stripe subscription status."""

    INCOMPLETE = "incomplete"
    INCOMPLETE_EXPIRED = "incomplete_expired"
    TRIALING = "trialing"
    ACTIVE = "active"
    PAST_DUE = "past_due"
    CANCELED = "canceled"
    UNPAID = "unpaid"

    @classmethod
    def from_str(cls, status: str) -> "SubscriptionStatus":
        """Convert string to enum."""
        return cls(status)


@dataclass(frozen=True)
class Subscription:
    """Represents a Stripe subscription."""

    id: str
    customer_id: str
    status: SubscriptionStatus
    price_id: str
    current_period_start: datetime
    current_period_end: datetime
    cancel_at_period_end: bool = False
    canceled_at: Optional[datetime] = None
    metadata: Optional[dict[str, str]] = None

    @classmethod
    def from_stripe(cls, stripe_subscription: dict[str, Any]) -> "Subscription":
        """Create Subscription from Stripe subscription object.

        Raises:
            ValueError: If subscription has no items (should never happen in normal Stripe usage)
        """
        items_data = stripe_subscription.get("items", {}).get("data", [])
        if not items_data:
            raise ValueError(
                f"Subscription {stripe_subscription.get('id', 'unknown')} has no items"
            )

        return cls(
            id=stripe_subscription["id"],
            customer_id=stripe_subscription["customer"],
            status=SubscriptionStatus.from_str(stripe_subscription["status"]),
            price_id=items_data[0]["price"]["id"],
            current_period_start=datetime.fromtimestamp(
                stripe_subscription["current_period_start"]
            ),
            current_period_end=datetime.fromtimestamp(stripe_subscription["current_period_end"]),
            cancel_at_period_end=stripe_subscription["cancel_at_period_end"],
            canceled_at=(
                datetime.fromtimestamp(stripe_subscription["canceled_at"])
                if stripe_subscription.get("canceled_at")
                else None
            ),
            metadata=stripe_subscription.get("metadata"),
        )

    @property
    def is_active(self) -> bool:
        """Check if subscription is active."""
        return self.status in {SubscriptionStatus.ACTIVE, SubscriptionStatus.TRIALING}


class SubscriptionManagerProtocol(Protocol):
    """Protocol for subscription management operations."""

    def get_subscription(self, subscription_id: str) -> Optional[Subscription]:
        """Retrieve a subscription by ID."""
        ...

    def get_customer_subscriptions(self, customer_id: str) -> list[Subscription]:
        """Retrieve all subscriptions for a customer."""
        ...

    def update_subscription(
        self,
        subscription_id: str,
        price_id: Optional[str] = None,
        metadata: Optional[dict[str, str]] = None,
    ) -> Subscription:
        """Update a subscription."""
        ...

    def cancel_subscription(self, subscription_id: str, at_period_end: bool = True) -> Subscription:
        """Cancel a subscription."""
        ...

    def reactivate_subscription(self, subscription_id: str) -> Subscription:
        """Reactivate a canceled subscription."""
        ...


class SubscriptionManager:
    """
    Manages Stripe subscription operations.

    Provides a clean interface for retrieving, updating, and canceling
    subscriptions.
    """

    def __init__(self) -> None:
        """Initialize subscription manager."""
        if not STRIPE_AVAILABLE:
            raise RuntimeError("stripe package not installed. Install with: pip install stripe")

    def get_subscription(self, subscription_id: str) -> Optional[Subscription]:
        """
        Retrieve a subscription by ID.

        Args:
            subscription_id: Stripe subscription ID

        Returns:
            Subscription object if found, None otherwise

        Raises:
            StripeError: If the API call fails (except for NotFound)
        """
        try:
            stripe_subscription = stripe.Subscription.retrieve(subscription_id)
            return Subscription.from_stripe(dict(stripe_subscription))
        except stripe.error.InvalidRequestError:
            return None

    def get_customer_subscriptions(
        self, customer_id: str, active_only: bool = False
    ) -> list[Subscription]:
        """
        Retrieve all subscriptions for a customer.

        Args:
            customer_id: Stripe customer ID
            active_only: If True, only return active subscriptions

        Returns:
            List of Subscription objects

        Raises:
            StripeError: If the API call fails
        """
        params: dict[str, Any] = {"customer": customer_id}
        if active_only:
            params["status"] = "active"

        subscriptions = stripe.Subscription.list(**params)
        return [Subscription.from_stripe(dict(sub)) for sub in subscriptions.data]

    def update_subscription(
        self,
        subscription_id: str,
        price_id: Optional[str] = None,
        metadata: Optional[dict[str, str]] = None,
    ) -> Subscription:
        """
        Update a subscription.

        Args:
            subscription_id: Stripe subscription ID
            price_id: New price ID (optional)
            metadata: New metadata (optional)

        Returns:
            Updated Subscription object

        Raises:
            StripeError: If the API call fails
        """
        update_params: dict[str, Any] = {}

        if price_id is not None:
            # Get current subscription to get the item ID
            current_sub = stripe.Subscription.retrieve(subscription_id)
            items_data = current_sub.get("items", {}).get("data", [])
            if not items_data:
                raise ValueError(f"Subscription {subscription_id} has no items to update")
            item_id = items_data[0]["id"]
            update_params["items"] = [{"id": item_id, "price": price_id}]

        if metadata is not None:
            update_params["metadata"] = metadata

        stripe_subscription = stripe.Subscription.modify(subscription_id, **update_params)
        return Subscription.from_stripe(dict(stripe_subscription))

    def cancel_subscription(self, subscription_id: str, at_period_end: bool = True) -> Subscription:
        """
        Cancel a subscription.

        Args:
            subscription_id: Stripe subscription ID
            at_period_end: If True, cancel at period end. If False, cancel immediately.

        Returns:
            Canceled Subscription object

        Raises:
            StripeError: If the API call fails
        """
        if at_period_end:
            # Schedule cancellation at period end
            stripe_subscription = stripe.Subscription.modify(
                subscription_id, cancel_at_period_end=True
            )
        else:
            # Cancel immediately
            stripe_subscription = stripe.Subscription.cancel(subscription_id)

        return Subscription.from_stripe(dict(stripe_subscription))

    def reactivate_subscription(self, subscription_id: str) -> Subscription:
        """
        Reactivate a subscription that was scheduled for cancellation.

        Args:
            subscription_id: Stripe subscription ID

        Returns:
            Reactivated Subscription object

        Raises:
            StripeError: If the API call fails
        """
        stripe_subscription = stripe.Subscription.modify(
            subscription_id, cancel_at_period_end=False
        )
        return Subscription.from_stripe(dict(stripe_subscription))
