"""Tests for Stripe client wrapper."""

import os

# Get the mocked stripe from sys.modules (set up in conftest.py)
import sys
from typing import Any
from unittest.mock import MagicMock, patch

import pytest

from protocols.billing.stripe_client import (
    StripeClient,
    StripeConfig,
    create_stripe_client,
    get_stripe_config,
)

mock_stripe = sys.modules["stripe"]


@pytest.fixture
def stripe_config() -> StripeConfig:
    """Create a test Stripe config."""
    return StripeConfig(
        api_key="sk_test_123",
        webhook_secret="whsec_test_123",
        price_ids={
            "pro_monthly": "price_pro_monthly_123",
            "pro_yearly": "price_pro_yearly_123",
            "teams_monthly": "price_teams_monthly_123",
        },
    )


@pytest.fixture
def stripe_client(stripe_config: StripeConfig) -> StripeClient:
    """Create a Stripe client with mocked stripe."""
    with patch("protocols.billing.stripe_client.STRIPE_AVAILABLE", True):
        return StripeClient(stripe_config)


class TestStripeConfig:
    """Tests for StripeConfig."""

    def test_is_configured_with_all_values(self) -> None:
        """Test is_configured returns True when all values are set."""
        config = StripeConfig(
            api_key="sk_test_123",
            webhook_secret="whsec_test_123",
            price_ids={"pro_monthly": "price_123"},
        )

        assert config.is_configured is True

    def test_is_configured_missing_api_key(self) -> None:
        """Test is_configured returns False when api_key is missing."""
        config = StripeConfig(
            api_key="",
            webhook_secret="whsec_test_123",
            price_ids={"pro_monthly": "price_123"},
        )

        assert config.is_configured is False

    def test_is_configured_missing_webhook_secret(self) -> None:
        """Test is_configured returns False when webhook_secret is missing."""
        config = StripeConfig(
            api_key="sk_test_123",
            webhook_secret="",
            price_ids={"pro_monthly": "price_123"},
        )

        assert config.is_configured is False

    def test_is_configured_empty_price_ids(self) -> None:
        """Test is_configured returns False when price_ids is empty."""
        config = StripeConfig(
            api_key="sk_test_123",
            webhook_secret="whsec_test_123",
            price_ids={},
        )

        assert config.is_configured is False


class TestGetStripeConfig:
    """Tests for get_stripe_config."""

    def test_get_stripe_config_from_env(self) -> None:
        """Test loading config from environment variables."""
        env = {
            "STRIPE_API_KEY": "sk_test_env",
            "STRIPE_WEBHOOK_SECRET": "whsec_env",
            "STRIPE_PRICE_PRO_MONTHLY": "price_pro_m",
            "STRIPE_PRICE_PRO_YEARLY": "price_pro_y",
            "STRIPE_PRICE_TEAMS_MONTHLY": "price_teams_m",
        }

        with patch.dict(os.environ, env, clear=False):
            config = get_stripe_config()

            assert config.api_key == "sk_test_env"
            assert config.webhook_secret == "whsec_env"
            assert config.price_ids["pro_monthly"] == "price_pro_m"
            assert config.price_ids["pro_yearly"] == "price_pro_y"
            assert config.price_ids["teams_monthly"] == "price_teams_m"

    def test_get_stripe_config_defaults(self) -> None:
        """Test config defaults when env vars are not set."""
        with patch.dict(os.environ, {}, clear=True):
            config = get_stripe_config()

            assert config.api_key == ""
            assert config.webhook_secret == ""
            assert config.price_ids["pro_monthly"] == ""
            assert config.price_ids["pro_yearly"] == ""
            assert config.price_ids["teams_monthly"] == ""


class TestStripeClient:
    """Tests for StripeClient."""

    def test_init_without_stripe_package(self) -> None:
        """Test initialization fails without stripe package."""
        with patch("protocols.billing.stripe_client.STRIPE_AVAILABLE", False):
            with pytest.raises(RuntimeError, match="stripe package not installed"):
                StripeClient()

    def test_init_with_invalid_config(self) -> None:
        """Test initialization fails with invalid config."""
        invalid_config = StripeConfig(
            api_key="",
            webhook_secret="",
            price_ids={},
        )

        with patch("protocols.billing.stripe_client.STRIPE_AVAILABLE", True):
            with pytest.raises(ValueError, match="Stripe not properly configured"):
                StripeClient(invalid_config)

    def test_init_configures_stripe_api_key(
        self, mock_stripe: MagicMock, stripe_config: StripeConfig
    ) -> None:
        """Test initialization sets stripe.api_key."""
        with patch("protocols.billing.stripe_client.STRIPE_AVAILABLE", True):
            StripeClient(stripe_config)

            assert mock_stripe.api_key == "sk_test_123"

    def test_config_property(
        self, stripe_client: StripeClient, stripe_config: StripeConfig
    ) -> None:
        """Test config property returns the config."""
        assert stripe_client.config == stripe_config

    def test_create_checkout_session(self, stripe_client: StripeClient) -> None:
        """Test creating a checkout session."""
        mock_session = {
            "id": "cs_test123",
            "url": "https://checkout.stripe.com/pay/cs_test123",
            "customer_email": "test@example.com",
        }
        mock_stripe.checkout.Session.create.return_value = mock_session

        session = stripe_client.create_checkout_session(
            customer_email="test@example.com",
            price_id="price_123",
            success_url="https://example.com/success",
            cancel_url="https://example.com/cancel",
            metadata={"user_id": "123"},
        )

        assert session["id"] == "cs_test123"
        mock_stripe.checkout.Session.create.assert_called_once_with(
            customer_email="test@example.com",
            line_items=[{"price": "price_123", "quantity": 1}],
            mode="subscription",
            success_url="https://example.com/success",
            cancel_url="https://example.com/cancel",
            metadata={"user_id": "123"},
            allow_promotion_codes=True,
            billing_address_collection="auto",
            payment_method_types=["card"],
        )

    def test_create_checkout_session_no_metadata(self, stripe_client: StripeClient) -> None:
        """Test creating checkout session without metadata."""
        mock_session = {"id": "cs_test123"}
        mock_stripe.checkout.Session.create.return_value = mock_session

        session = stripe_client.create_checkout_session(
            customer_email="test@example.com",
            price_id="price_123",
            success_url="https://example.com/success",
            cancel_url="https://example.com/cancel",
        )

        assert session["id"] == "cs_test123"
        call_args = mock_stripe.checkout.Session.create.call_args
        assert call_args[1]["metadata"] == {}

    def test_create_portal_session(self, stripe_client: StripeClient) -> None:
        """Test creating a customer portal session."""
        mock_session = {
            "id": "bps_test123",
            "url": "https://billing.stripe.com/session/bps_test123",
        }
        mock_stripe.billing_portal.Session.create.return_value = mock_session

        session = stripe_client.create_portal_session(
            customer_id="cus_123",
            return_url="https://example.com/account",
        )

        assert session["id"] == "bps_test123"
        assert session["url"] == "https://billing.stripe.com/session/bps_test123"
        mock_stripe.billing_portal.Session.create.assert_called_once_with(
            customer="cus_123",
            return_url="https://example.com/account",
        )

    def test_construct_webhook_event(self, stripe_client: StripeClient) -> None:
        """Test constructing and verifying webhook event."""
        mock_event = {
            "id": "evt_test123",
            "type": "customer.created",
            "data": {"object": {"id": "cus_123"}},
        }
        mock_stripe.Webhook.construct_event.return_value = mock_event

        event = stripe_client.construct_webhook_event(
            payload=b'{"type": "customer.created"}',
            sig_header="t=123,v1=sig",
        )

        assert event["id"] == "evt_test123"
        assert event["type"] == "customer.created"
        mock_stripe.Webhook.construct_event.assert_called_once_with(
            b'{"type": "customer.created"}',
            "t=123,v1=sig",
            "whsec_test_123",
        )


class TestCreateStripeClient:
    """Tests for create_stripe_client factory."""

    def test_create_stripe_client_with_config(self, stripe_config: StripeConfig) -> None:
        """Test factory creates client with provided config."""
        with patch("protocols.billing.stripe_client.STRIPE_AVAILABLE", True):
            client = create_stripe_client(stripe_config)

            assert client.config == stripe_config

    def test_create_stripe_client_loads_from_env(self) -> None:
        """Test factory loads config from environment when not provided."""
        env = {
            "STRIPE_API_KEY": "sk_test_env",
            "STRIPE_WEBHOOK_SECRET": "whsec_env",
            "STRIPE_PRICE_PRO_MONTHLY": "price_pro",
        }

        with patch.dict(os.environ, env, clear=False):
            with patch("protocols.billing.stripe_client.STRIPE_AVAILABLE", True):
                client = create_stripe_client()

                assert client.config.api_key == "sk_test_env"
                assert client.config.webhook_secret == "whsec_env"
