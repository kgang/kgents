"""
Stripe client wrapper with configuration management.

Handles graceful degradation if stripe package is not installed.
"""

import os
from dataclasses import dataclass
from typing import Any, Optional, Protocol

# Try to import stripe, but don't fail if it's not installed
try:
    import stripe  # type: ignore[import-not-found]
    from stripe import StripeError

    STRIPE_AVAILABLE = True
except ImportError:
    STRIPE_AVAILABLE = False
    StripeError = Exception  # noqa: N816


@dataclass(frozen=True)
class StripeConfig:
    """Stripe configuration loaded from environment."""

    api_key: str
    webhook_secret: str
    price_ids: dict[str, str]  # tier -> stripe price ID

    @property
    def is_configured(self) -> bool:
        """Check if Stripe is properly configured."""
        return bool(self.api_key and self.webhook_secret and self.price_ids)


def get_stripe_config() -> StripeConfig:
    """
    Load Stripe config from environment.

    Environment variables:
    - STRIPE_API_KEY: Stripe secret key
    - STRIPE_WEBHOOK_SECRET: Webhook signing secret
    - STRIPE_PRICE_PRO_MONTHLY: Pro monthly price ID
    - STRIPE_PRICE_PRO_YEARLY: Pro yearly price ID
    - STRIPE_PRICE_TEAMS_MONTHLY: Teams monthly price ID
    """
    return StripeConfig(
        api_key=os.environ.get("STRIPE_API_KEY", ""),
        webhook_secret=os.environ.get("STRIPE_WEBHOOK_SECRET", ""),
        price_ids={
            "pro_monthly": os.environ.get("STRIPE_PRICE_PRO_MONTHLY", ""),
            "pro_yearly": os.environ.get("STRIPE_PRICE_PRO_YEARLY", ""),
            "teams_monthly": os.environ.get("STRIPE_PRICE_TEAMS_MONTHLY", ""),
        },
    )


class StripeClientProtocol(Protocol):
    """Protocol for Stripe client operations."""

    @property
    def config(self) -> StripeConfig:
        """Get the Stripe configuration."""
        ...

    def create_checkout_session(
        self,
        customer_email: str,
        price_id: str,
        success_url: str,
        cancel_url: str,
        metadata: Optional[dict[str, str]] = None,
    ) -> dict[str, Any]:
        """Create a Stripe checkout session."""
        ...

    def create_portal_session(
        self, customer_id: str, return_url: str
    ) -> dict[str, Any]:
        """Create a Stripe customer portal session."""
        ...

    def construct_webhook_event(
        self, payload: bytes, sig_header: str
    ) -> dict[str, Any]:
        """Construct and verify a webhook event."""
        ...


class StripeClient:
    """
    Wrapper around Stripe SDK.

    Provides a clean interface for common Stripe operations with proper
    error handling and configuration management.
    """

    def __init__(self, config: Optional[StripeConfig] = None) -> None:
        """
        Initialize Stripe client.

        Args:
            config: Stripe configuration. If None, loads from environment.

        Raises:
            RuntimeError: If stripe package is not installed.
        """
        if not STRIPE_AVAILABLE:
            raise RuntimeError(
                "stripe package not installed. Install with: pip install stripe"
            )

        self._config = config or get_stripe_config()

        if not self._config.is_configured:
            raise ValueError(
                "Stripe not properly configured. Set STRIPE_API_KEY, "
                "STRIPE_WEBHOOK_SECRET, and price IDs in environment."
            )

        # Configure the stripe library
        stripe.api_key = self._config.api_key

    @property
    def config(self) -> StripeConfig:
        """Get the Stripe configuration."""
        return self._config

    def create_checkout_session(
        self,
        customer_email: str,
        price_id: str,
        success_url: str,
        cancel_url: str,
        metadata: Optional[dict[str, str]] = None,
    ) -> dict[str, Any]:
        """
        Create a Stripe checkout session.

        Args:
            customer_email: Customer's email address
            price_id: Stripe price ID for the subscription
            success_url: URL to redirect to on success
            cancel_url: URL to redirect to on cancel
            metadata: Optional metadata to attach to the session

        Returns:
            Checkout session object as dict

        Raises:
            StripeError: If the API call fails
        """
        session = stripe.checkout.Session.create(
            customer_email=customer_email,
            line_items=[{"price": price_id, "quantity": 1}],
            mode="subscription",
            success_url=success_url,
            cancel_url=cancel_url,
            metadata=metadata or {},
            allow_promotion_codes=True,
            billing_address_collection="auto",
            payment_method_types=["card"],
        )
        return dict(session)

    def create_portal_session(
        self, customer_id: str, return_url: str
    ) -> dict[str, Any]:
        """
        Create a Stripe customer portal session.

        Args:
            customer_id: Stripe customer ID
            return_url: URL to redirect to when leaving the portal

        Returns:
            Portal session object as dict

        Raises:
            StripeError: If the API call fails
        """
        session = stripe.billing_portal.Session.create(
            customer=customer_id,
            return_url=return_url,
        )
        return dict(session)

    def construct_webhook_event(
        self, payload: bytes, sig_header: str
    ) -> dict[str, Any]:
        """
        Construct and verify a webhook event.

        Args:
            payload: Raw request body as bytes
            sig_header: Value of Stripe-Signature header

        Returns:
            Webhook event object as dict

        Raises:
            stripe.error.SignatureVerificationError: If signature is invalid
        """
        event = stripe.Webhook.construct_event(
            payload, sig_header, self._config.webhook_secret
        )
        return dict(event)


def create_stripe_client(config: Optional[StripeConfig] = None) -> StripeClient:
    """
    Factory function to create a Stripe client.

    Args:
        config: Optional Stripe configuration. If None, loads from environment.

    Returns:
        Configured StripeClient instance

    Raises:
        RuntimeError: If stripe package is not installed
        ValueError: If configuration is invalid
    """
    return StripeClient(config)
