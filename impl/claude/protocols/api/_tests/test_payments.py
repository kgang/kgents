"""
Tests for Stripe payment integration.

Covers:
- Checkout session creation (subscriptions + credit packs)
- Webhook event handling
- Customer management
- Mock client for testing
"""

from datetime import datetime, timedelta

import pytest

from protocols.api.payments import (
    MockPaymentClient,
    create_payment_client,
    handle_payment_succeeded,
    handle_subscription_created,
    handle_subscription_deleted,
    handle_subscription_updated,
)

# =============================================================================
# Mock Client Tests
# =============================================================================


def test_mock_client_create_customer():
    """Test mock customer creation."""
    client = MockPaymentClient()

    customer_id = client.create_customer("user1", "user1@example.com", "Test User")

    assert customer_id.startswith("cus_mock_")
    assert "user1" in customer_id


def test_mock_client_create_subscription_checkout():
    """Test mock subscription checkout session."""
    client = MockPaymentClient()

    session = client.create_subscription_checkout(
        user_id="user1",
        tier="RESIDENT",
        success_url="https://example.com/success",
        cancel_url="https://example.com/cancel",
    )

    assert session.session_id.startswith("cs_mock_")
    assert "user1" in session.session_id
    assert "RESIDENT" in session.session_id
    assert session.session_url.startswith("https://")
    assert session.expires_at > datetime.now()


def test_mock_client_create_credit_pack_checkout():
    """Test mock credit pack checkout session."""
    client = MockPaymentClient()

    session = client.create_credit_pack_checkout(
        user_id="user1",
        pack="EXPLORER",
        success_url="https://example.com/success",
        cancel_url="https://example.com/cancel",
    )

    assert session.session_id.startswith("cs_mock_")
    assert "EXPLORER" in session.session_id


def test_mock_client_get_subscription_info():
    """Test mock get subscription info."""
    client = MockPaymentClient()

    info = client.get_subscription_info("sub_mock_123")

    assert info.subscription_id == "sub_mock_123"
    assert info.status == "active"
    assert info.tier == "RESIDENT"


def test_mock_client_cancel_subscription():
    """Test mock cancel subscription."""
    client = MockPaymentClient()

    result = client.cancel_subscription("sub_mock_123", at_period_end=True)

    assert result.success
    assert "canceled" in result.message.lower()


# =============================================================================
# Webhook Handler Tests
# =============================================================================


def test_handle_subscription_created():
    """Test subscription.created webhook handler."""
    event_data = {
        "object": {
            "id": "sub_123",
            "metadata": {
                "user_id": "user1",
                "tier": "RESIDENT",
            },
            "current_period_end": int((datetime.now() + timedelta(days=30)).timestamp()),
        }
    }

    result = handle_subscription_created(event_data)

    assert result["user_id"] == "user1"
    assert result["tier"] == "RESIDENT"
    assert result["subscription_id"] == "sub_123"
    assert "renews_at" in result


def test_handle_subscription_updated():
    """Test subscription.updated webhook handler."""
    event_data = {
        "object": {
            "id": "sub_123",
            "metadata": {
                "user_id": "user1",
                "tier": "CITIZEN",
            },
            "status": "active",
            "current_period_end": int((datetime.now() + timedelta(days=30)).timestamp()),
        }
    }

    result = handle_subscription_updated(event_data)

    assert result["user_id"] == "user1"
    assert result["tier"] == "CITIZEN"
    assert result["status"] == "active"


def test_handle_subscription_deleted():
    """Test subscription.deleted webhook handler."""
    event_data = {
        "object": {
            "id": "sub_123",
            "metadata": {
                "user_id": "user1",
            },
        }
    }

    result = handle_subscription_deleted(event_data)

    assert result["user_id"] == "user1"
    assert result["tier"] == "TOURIST"  # Downgrade to free


def test_handle_payment_succeeded():
    """Test payment_intent.succeeded webhook handler."""
    event_data = {
        "object": {
            "id": "pi_123",
            "metadata": {
                "user_id": "user1",
                "credits": "500",
                "pack": "STARTER",
            },
        }
    }

    result = handle_payment_succeeded(event_data)

    assert result["user_id"] == "user1"
    assert result["credits"] == 500
    assert result["pack"] == "STARTER"


# =============================================================================
# Factory Tests
# =============================================================================


def test_create_payment_client_returns_mock():
    """Test factory returns mock when Stripe not configured."""
    client = create_payment_client(use_stripe=False)

    assert isinstance(client, MockPaymentClient)


# =============================================================================
# Integration Tests (would use Stripe test mode)
# =============================================================================


@pytest.mark.skip(reason="Requires Stripe test API keys")
def test_real_stripe_create_customer():
    """Test real Stripe customer creation (requires API keys)."""
    from protocols.api.payments import PaymentClient

    client = PaymentClient()
    customer_id = client.create_customer("test_user", "test@example.com", "Test User")

    assert customer_id.startswith("cus_")


@pytest.mark.skip(reason="Requires Stripe test API keys")
def test_real_stripe_create_checkout_session():
    """Test real Stripe checkout session (requires API keys)."""
    from protocols.api.payments import PaymentClient

    client = PaymentClient()
    session = client.create_subscription_checkout(
        user_id="test_user",
        tier="RESIDENT",
        success_url="https://example.com/success",
        cancel_url="https://example.com/cancel",
    )

    assert session.session_id.startswith("cs_")
    assert session.session_url.startswith("https://checkout.stripe.com")
