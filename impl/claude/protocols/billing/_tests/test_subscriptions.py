"""Tests for subscription management."""

# Get the mocked stripe from sys.modules (set up in conftest.py)
import sys
from datetime import datetime, timedelta
from typing import Any
from unittest.mock import MagicMock, patch

import pytest

from protocols.billing.subscriptions import (
    Subscription,
    SubscriptionManager,
    SubscriptionStatus,
)

mock_stripe = sys.modules["stripe"]


@pytest.fixture
def subscription_manager() -> SubscriptionManager:
    """Create subscription manager with mocked stripe."""
    with patch("protocols.billing.subscriptions.STRIPE_AVAILABLE", True):
        return SubscriptionManager()


def make_stripe_subscription(
    subscription_id: str = "sub_test123",
    customer_id: str = "cus_test123",
    status: str = "active",
    price_id: str = "price_test123",
    cancel_at_period_end: bool = False,
    canceled_at: int | None = None,
    metadata: dict[str, str] | None = None,
) -> dict[str, Any]:
    """Create a mock Stripe subscription object."""
    now = datetime.now()
    period_start = int(now.timestamp())
    period_end = int((now + timedelta(days=30)).timestamp())

    return {
        "id": subscription_id,
        "customer": customer_id,
        "status": status,
        "items": {
            "data": [
                {
                    "id": "si_test123",
                    "price": {
                        "id": price_id,
                        "object": "price",
                    },
                }
            ]
        },
        "current_period_start": period_start,
        "current_period_end": period_end,
        "cancel_at_period_end": cancel_at_period_end,
        "canceled_at": canceled_at,
        "metadata": metadata or {},
        "object": "subscription",
    }


class TestSubscriptionStatus:
    """Tests for SubscriptionStatus enum."""

    def test_from_str(self) -> None:
        """Test converting string to enum."""
        assert SubscriptionStatus.from_str("active") == SubscriptionStatus.ACTIVE
        assert SubscriptionStatus.from_str("trialing") == SubscriptionStatus.TRIALING
        assert SubscriptionStatus.from_str("canceled") == SubscriptionStatus.CANCELED

    def test_all_statuses(self) -> None:
        """Test all subscription statuses."""
        statuses = [
            "incomplete",
            "incomplete_expired",
            "trialing",
            "active",
            "past_due",
            "canceled",
            "unpaid",
        ]
        for status_str in statuses:
            status = SubscriptionStatus.from_str(status_str)
            assert status.value == status_str


class TestSubscription:
    """Tests for Subscription dataclass."""

    def test_from_stripe(self) -> None:
        """Test creating Subscription from Stripe object."""
        stripe_sub = make_stripe_subscription(
            subscription_id="sub_abc123",
            customer_id="cus_abc123",
            status="active",
            price_id="price_pro",
            metadata={"plan": "pro"},
        )

        sub = Subscription.from_stripe(stripe_sub)

        assert sub.id == "sub_abc123"
        assert sub.customer_id == "cus_abc123"
        # Compare by value to avoid enum identity issues after module reload
        assert sub.status.value == "active"
        assert sub.price_id == "price_pro"
        assert sub.cancel_at_period_end is False
        assert sub.canceled_at is None
        assert sub.metadata == {"plan": "pro"}

    def test_from_stripe_with_cancellation(self) -> None:
        """Test subscription with cancellation scheduled."""
        canceled_at = int(datetime.now().timestamp())
        stripe_sub = make_stripe_subscription(
            cancel_at_period_end=True,
            canceled_at=canceled_at,
        )

        sub = Subscription.from_stripe(stripe_sub)

        assert sub.cancel_at_period_end is True
        assert sub.canceled_at is not None
        assert isinstance(sub.canceled_at, datetime)

    def test_is_active_when_active(self) -> None:
        """Test is_active returns True for active subscription."""
        stripe_sub = make_stripe_subscription(status="active")
        sub = Subscription.from_stripe(stripe_sub)

        assert sub.is_active is True

    def test_is_active_when_trialing(self) -> None:
        """Test is_active returns True for trialing subscription."""
        stripe_sub = make_stripe_subscription(status="trialing")
        sub = Subscription.from_stripe(stripe_sub)

        assert sub.is_active is True

    def test_is_active_when_canceled(self) -> None:
        """Test is_active returns False for canceled subscription."""
        stripe_sub = make_stripe_subscription(status="canceled")
        sub = Subscription.from_stripe(stripe_sub)

        assert sub.is_active is False

    def test_is_active_when_past_due(self) -> None:
        """Test is_active returns False for past_due subscription."""
        stripe_sub = make_stripe_subscription(status="past_due")
        sub = Subscription.from_stripe(stripe_sub)

        assert sub.is_active is False

    def test_from_stripe_no_items_raises_error(self) -> None:
        """Test that from_stripe raises ValueError when subscription has no items."""
        stripe_sub = {
            "id": "sub_empty123",
            "customer": "cus_test",
            "status": "active",
            "items": {"data": []},  # Empty items
            "current_period_start": 1000000,
            "current_period_end": 2000000,
            "cancel_at_period_end": False,
            "canceled_at": None,
            "metadata": {},
        }

        with pytest.raises(ValueError, match="has no items"):
            Subscription.from_stripe(stripe_sub)

    def test_from_stripe_missing_items_key_raises_error(self) -> None:
        """Test that from_stripe raises ValueError when items key is missing."""
        stripe_sub = {
            "id": "sub_noitems123",
            "customer": "cus_test",
            "status": "active",
            # No "items" key at all
            "current_period_start": 1000000,
            "current_period_end": 2000000,
            "cancel_at_period_end": False,
            "canceled_at": None,
            "metadata": {},
        }

        with pytest.raises(ValueError, match="has no items"):
            Subscription.from_stripe(stripe_sub)


class TestSubscriptionManager:
    """Tests for SubscriptionManager."""

    def test_init_without_stripe(self) -> None:
        """Test initialization fails without stripe package."""
        with patch("protocols.billing.subscriptions.STRIPE_AVAILABLE", False):
            with pytest.raises(RuntimeError, match="stripe package not installed"):
                SubscriptionManager()

    def test_get_subscription(self, subscription_manager: SubscriptionManager) -> None:
        """Test retrieving a subscription by ID."""
        mock_stripe.Subscription.retrieve.return_value = make_stripe_subscription(
            subscription_id="sub_get123"
        )

        sub = subscription_manager.get_subscription("sub_get123")

        assert sub is not None
        assert sub.id == "sub_get123"
        mock_stripe.Subscription.retrieve.assert_called_once_with("sub_get123")

    def test_get_subscription_not_found(self, subscription_manager: SubscriptionManager) -> None:
        """Test retrieving non-existent subscription returns None."""
        mock_stripe.error.InvalidRequestError = Exception
        mock_stripe.Subscription.retrieve.side_effect = mock_stripe.error.InvalidRequestError(
            "Not found"
        )

        sub = subscription_manager.get_subscription("sub_nonexistent")

        assert sub is None

    def test_get_customer_subscriptions(self, subscription_manager: SubscriptionManager) -> None:
        """Test retrieving all customer subscriptions."""
        mock_list = MagicMock()
        mock_list.data = [
            make_stripe_subscription(subscription_id="sub_1", customer_id="cus_abc"),
            make_stripe_subscription(subscription_id="sub_2", customer_id="cus_abc"),
        ]
        mock_stripe.Subscription.list.return_value = mock_list

        subs = subscription_manager.get_customer_subscriptions("cus_abc")

        assert len(subs) == 2
        assert subs[0].id == "sub_1"
        assert subs[1].id == "sub_2"
        mock_stripe.Subscription.list.assert_called_once_with(customer="cus_abc")

    def test_get_customer_subscriptions_active_only(
        self, subscription_manager: SubscriptionManager
    ) -> None:
        """Test retrieving only active customer subscriptions."""
        mock_list = MagicMock()
        mock_list.data = [make_stripe_subscription(subscription_id="sub_active", status="active")]
        mock_stripe.Subscription.list.return_value = mock_list

        subs = subscription_manager.get_customer_subscriptions("cus_abc", active_only=True)

        assert len(subs) == 1
        # Compare by value to avoid enum identity issues after module reload
        assert subs[0].status.value == "active"
        mock_stripe.Subscription.list.assert_called_once_with(customer="cus_abc", status="active")

    def test_update_subscription_price(self, subscription_manager: SubscriptionManager) -> None:
        """Test updating subscription price."""
        # Mock retrieve to get current subscription
        mock_stripe.Subscription.retrieve.return_value = make_stripe_subscription(
            subscription_id="sub_update123"
        )

        # Mock modify to return updated subscription
        mock_stripe.Subscription.modify.return_value = make_stripe_subscription(
            subscription_id="sub_update123",
            price_id="price_new",
        )

        sub = subscription_manager.update_subscription("sub_update123", price_id="price_new")

        assert sub.price_id == "price_new"
        mock_stripe.Subscription.modify.assert_called_once()
        call_args = mock_stripe.Subscription.modify.call_args
        assert call_args[0][0] == "sub_update123"
        assert "items" in call_args[1]

    def test_update_subscription_metadata(self, subscription_manager: SubscriptionManager) -> None:
        """Test updating subscription metadata."""
        mock_stripe.Subscription.modify.return_value = make_stripe_subscription(
            subscription_id="sub_meta123",
            metadata={"updated": "true"},
        )

        sub = subscription_manager.update_subscription("sub_meta123", metadata={"updated": "true"})

        assert sub.metadata == {"updated": "true"}
        mock_stripe.Subscription.modify.assert_called_once_with(
            "sub_meta123", metadata={"updated": "true"}
        )

    def test_cancel_subscription_at_period_end(
        self, subscription_manager: SubscriptionManager
    ) -> None:
        """Test canceling subscription at period end."""
        mock_stripe.Subscription.modify.return_value = make_stripe_subscription(
            subscription_id="sub_cancel123",
            cancel_at_period_end=True,
        )

        sub = subscription_manager.cancel_subscription("sub_cancel123", at_period_end=True)

        assert sub.cancel_at_period_end is True
        mock_stripe.Subscription.modify.assert_called_once_with(
            "sub_cancel123", cancel_at_period_end=True
        )

    def test_cancel_subscription_immediately(
        self, subscription_manager: SubscriptionManager
    ) -> None:
        """Test canceling subscription immediately."""
        mock_stripe.Subscription.cancel.return_value = make_stripe_subscription(
            subscription_id="sub_immediate123",
            status="canceled",
        )

        sub = subscription_manager.cancel_subscription("sub_immediate123", at_period_end=False)

        # Compare by value to avoid enum identity issues after module reload
        assert sub.status.value == "canceled"
        mock_stripe.Subscription.cancel.assert_called_once_with("sub_immediate123")

    def test_reactivate_subscription(self, subscription_manager: SubscriptionManager) -> None:
        """Test reactivating a subscription."""
        mock_stripe.Subscription.modify.return_value = make_stripe_subscription(
            subscription_id="sub_reactivate123",
            cancel_at_period_end=False,
        )

        sub = subscription_manager.reactivate_subscription("sub_reactivate123")

        assert sub.cancel_at_period_end is False
        mock_stripe.Subscription.modify.assert_called_once_with(
            "sub_reactivate123", cancel_at_period_end=False
        )

    def test_update_subscription_no_items_raises_error(
        self, subscription_manager: SubscriptionManager
    ) -> None:
        """Test that updating subscription with no items raises ValueError."""
        # Mock retrieve to return subscription with empty items
        mock_stripe.Subscription.retrieve.return_value = {
            "id": "sub_empty123",
            "items": {"data": []},
        }

        with pytest.raises(ValueError, match="has no items to update"):
            subscription_manager.update_subscription("sub_empty123", price_id="price_new")
