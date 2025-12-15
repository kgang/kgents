"""
Stripe payment integration for Agent Town monetization.

Handles:
- Subscription creation and management (RESIDENT, CITIZEN, FOUNDER)
- Credit pack purchases (one-time payments)
- Checkout session creation
- Customer management

Per unified-v2.md Track C: Stripe test mode integration with margin-safe pricing.
"""

from __future__ import annotations

import logging
import os
from dataclasses import dataclass
from datetime import datetime, timedelta
from typing import Any

logger = logging.getLogger(__name__)

# Graceful Stripe import
try:
    import stripe

    HAS_STRIPE = True
except ImportError:
    HAS_STRIPE = False
    stripe = None  # type: ignore[assignment, unused-ignore]


# =============================================================================
# Stripe Configuration
# =============================================================================


# Stripe API key (test mode by default)
STRIPE_SECRET_KEY = os.environ.get("STRIPE_SECRET_KEY", "")
STRIPE_PUBLISHABLE_KEY = os.environ.get("STRIPE_PUBLISHABLE_KEY", "")
STRIPE_WEBHOOK_SECRET = os.environ.get("STRIPE_WEBHOOK_SECRET", "")

# Initialize Stripe
if HAS_STRIPE and STRIPE_SECRET_KEY:
    stripe.api_key = STRIPE_SECRET_KEY


# Subscription Price IDs (from Stripe Dashboard)
# NOTE: These should be set in environment variables in production
SUBSCRIPTION_PRICE_IDS = {
    "RESIDENT": os.environ.get("STRIPE_PRICE_RESIDENT", "price_resident_monthly"),
    "CITIZEN": os.environ.get("STRIPE_PRICE_CITIZEN", "price_citizen_monthly"),
    "FOUNDER": os.environ.get("STRIPE_PRICE_FOUNDER", "price_founder_monthly"),
}

# Credit Pack Price IDs (one-time payments)
CREDIT_PACK_PRICE_IDS = {
    "STARTER": os.environ.get("STRIPE_PRICE_STARTER", "price_credits_500"),
    "EXPLORER": os.environ.get("STRIPE_PRICE_EXPLORER", "price_credits_2500"),
    "ADVENTURER": os.environ.get("STRIPE_PRICE_ADVENTURER", "price_credits_10000"),
}

# Credit amounts for packs
CREDIT_PACK_AMOUNTS = {
    "STARTER": 500,
    "EXPLORER": 2500,
    "ADVENTURER": 10000,
}


# =============================================================================
# Data Structures
# =============================================================================


@dataclass
class CheckoutSession:
    """Result of creating a Stripe checkout session."""

    session_id: str
    session_url: str
    expires_at: datetime


@dataclass
class SubscriptionInfo:
    """Stripe subscription information."""

    subscription_id: str
    customer_id: str
    tier: str
    status: str  # active, past_due, canceled, etc.
    current_period_end: datetime
    cancel_at_period_end: bool


@dataclass
class PaymentResult:
    """Result of a payment operation."""

    success: bool
    message: str
    data: dict[str, Any] | None = None


# =============================================================================
# Payment Client
# =============================================================================


class PaymentClient:
    """
    Client for Stripe payment operations.

    Handles subscriptions, credit packs, and customer management.
    """

    def __init__(self, api_key: str | None = None, webhook_secret: str | None = None):
        """
        Initialize payment client.

        Args:
            api_key: Stripe API key (defaults to STRIPE_SECRET_KEY env var)
            webhook_secret: Webhook signing secret (defaults to env var)
        """
        if not HAS_STRIPE:
            raise ImportError(
                "stripe package not installed. Install with: pip install stripe"
            )

        self.api_key = api_key or STRIPE_SECRET_KEY
        self.webhook_secret = webhook_secret or STRIPE_WEBHOOK_SECRET

        if not self.api_key:
            logger.warning("STRIPE_SECRET_KEY not set, payment operations will fail")

        stripe.api_key = self.api_key

    # =========================================================================
    # Customer Management
    # =========================================================================

    def create_customer(self, user_id: str, email: str, name: str | None = None) -> str:
        """
        Create a Stripe customer.

        Args:
            user_id: Internal user ID
            email: Customer email
            name: Customer name (optional)

        Returns:
            Stripe customer ID
        """
        try:
            customer = stripe.Customer.create(
                email=email,
                name=name,
                metadata={"user_id": user_id},
            )
            logger.info(f"Created Stripe customer {customer.id} for user {user_id}")
            return str(customer.id)
        except Exception as e:
            logger.error(f"Failed to create customer: {e}")
            raise

    def get_customer(self, customer_id: str) -> Any:
        """Get customer details."""
        try:
            return stripe.Customer.retrieve(customer_id)
        except Exception as e:
            logger.error(f"Failed to retrieve customer {customer_id}: {e}")
            raise

    # =========================================================================
    # Subscription Management
    # =========================================================================

    def create_subscription_checkout(
        self,
        user_id: str,
        tier: str,
        customer_id: str | None = None,
        success_url: str = "https://agenttown.ai/success",
        cancel_url: str = "https://agenttown.ai/cancel",
    ) -> CheckoutSession:
        """
        Create a Stripe Checkout session for subscription.

        Args:
            user_id: Internal user ID
            tier: Subscription tier (RESIDENT, CITIZEN, FOUNDER)
            customer_id: Existing Stripe customer ID (optional)
            success_url: URL to redirect on success
            cancel_url: URL to redirect on cancel

        Returns:
            CheckoutSession with session URL
        """
        if tier not in SUBSCRIPTION_PRICE_IDS:
            raise ValueError(f"Invalid tier: {tier}")

        price_id = SUBSCRIPTION_PRICE_IDS[tier]

        try:
            session_params: dict[str, Any] = {
                "mode": "subscription",
                "line_items": [
                    {
                        "price": price_id,
                        "quantity": 1,
                    }
                ],
                "success_url": success_url + "?session_id={CHECKOUT_SESSION_ID}",
                "cancel_url": cancel_url,
                "metadata": {
                    "user_id": user_id,
                    "tier": tier,
                },
                "subscription_data": {
                    "metadata": {
                        "user_id": user_id,
                        "tier": tier,
                    }
                },
            }

            if customer_id:
                session_params["customer"] = customer_id
            else:
                session_params["customer_creation"] = "always"

            session = stripe.checkout.Session.create(**session_params)

            logger.info(
                f"Created subscription checkout session {session.id} for user {user_id}, tier {tier}"
            )

            return CheckoutSession(
                session_id=session.id,
                session_url=session.url,
                expires_at=datetime.fromtimestamp(session.expires_at),
            )
        except Exception as e:
            logger.error(f"Failed to create subscription checkout: {e}")
            raise

    def get_subscription_info(self, subscription_id: str) -> SubscriptionInfo:
        """Get subscription details."""
        try:
            sub = stripe.Subscription.retrieve(subscription_id)

            # Extract tier from metadata
            tier = sub.metadata.get("tier", "RESIDENT")

            return SubscriptionInfo(
                subscription_id=sub.id,
                customer_id=sub.customer,
                tier=tier,
                status=sub.status,
                current_period_end=datetime.fromtimestamp(sub.current_period_end),
                cancel_at_period_end=sub.cancel_at_period_end,
            )
        except Exception as e:
            logger.error(f"Failed to retrieve subscription {subscription_id}: {e}")
            raise

    def cancel_subscription(
        self, subscription_id: str, at_period_end: bool = True
    ) -> PaymentResult:
        """
        Cancel a subscription.

        Args:
            subscription_id: Stripe subscription ID
            at_period_end: If True, cancel at end of billing period (default)

        Returns:
            PaymentResult
        """
        try:
            if at_period_end:
                # Cancel at end of period (user keeps access until renewal date)
                sub = stripe.Subscription.modify(
                    subscription_id,
                    cancel_at_period_end=True,
                )
                message = f"Subscription will cancel at {datetime.fromtimestamp(sub.current_period_end)}"
            else:
                # Cancel immediately
                sub = stripe.Subscription.delete(subscription_id)
                message = "Subscription canceled immediately"

            logger.info(
                f"Canceled subscription {subscription_id} (at_period_end={at_period_end})"
            )

            return PaymentResult(
                success=True,
                message=message,
                data={"subscription_id": subscription_id},
            )
        except Exception as e:
            logger.error(f"Failed to cancel subscription {subscription_id}: {e}")
            return PaymentResult(success=False, message=str(e))

    # =========================================================================
    # Credit Pack Purchases
    # =========================================================================

    def create_credit_pack_checkout(
        self,
        user_id: str,
        pack: str,
        customer_id: str | None = None,
        success_url: str = "https://agenttown.ai/success",
        cancel_url: str = "https://agenttown.ai/cancel",
    ) -> CheckoutSession:
        """
        Create a Stripe Checkout session for one-time credit purchase.

        Args:
            user_id: Internal user ID
            pack: Pack name (STARTER, EXPLORER, ADVENTURER)
            customer_id: Existing Stripe customer ID (optional)
            success_url: URL to redirect on success
            cancel_url: URL to redirect on cancel

        Returns:
            CheckoutSession with session URL
        """
        if pack not in CREDIT_PACK_PRICE_IDS:
            raise ValueError(f"Invalid pack: {pack}")

        price_id = CREDIT_PACK_PRICE_IDS[pack]
        credits = CREDIT_PACK_AMOUNTS[pack]

        try:
            session_params: dict[str, Any] = {
                "mode": "payment",
                "line_items": [
                    {
                        "price": price_id,
                        "quantity": 1,
                    }
                ],
                "success_url": success_url + "?session_id={CHECKOUT_SESSION_ID}",
                "cancel_url": cancel_url,
                "metadata": {
                    "user_id": user_id,
                    "pack": pack,
                    "credits": str(credits),
                },
                "payment_intent_data": {
                    "metadata": {
                        "user_id": user_id,
                        "pack": pack,
                        "credits": str(credits),
                    }
                },
            }

            if customer_id:
                session_params["customer"] = customer_id

            session = stripe.checkout.Session.create(**session_params)

            logger.info(
                f"Created credit pack checkout session {session.id} for user {user_id}, pack {pack}"
            )

            return CheckoutSession(
                session_id=session.id,
                session_url=session.url,
                expires_at=datetime.fromtimestamp(session.expires_at),
            )
        except Exception as e:
            logger.error(f"Failed to create credit pack checkout: {e}")
            raise

    # =========================================================================
    # Webhook Handling
    # =========================================================================

    def construct_webhook_event(self, payload: bytes, sig_header: str) -> Any:
        """
        Verify and construct webhook event from Stripe.

        Args:
            payload: Raw request body
            sig_header: Stripe-Signature header value

        Returns:
            Verified Stripe event

        Raises:
            ValueError: If signature verification fails
        """
        if not self.webhook_secret:
            logger.warning(
                "STRIPE_WEBHOOK_SECRET not set, skipping signature verification"
            )
            import json

            return json.loads(payload)

        try:
            event = stripe.Webhook.construct_event(
                payload, sig_header, self.webhook_secret
            )
            return event
        except ValueError as e:
            logger.error(f"Invalid webhook payload: {e}")
            raise
        except stripe.error.SignatureVerificationError as e:
            logger.error(f"Invalid webhook signature: {e}")
            raise ValueError("Invalid signature") from e


# =============================================================================
# Webhook Event Handlers
# =============================================================================


def handle_subscription_created(event_data: dict[str, Any]) -> dict[str, Any]:
    """
    Handle subscription.created webhook.

    Returns user_id, tier, and subscription_id for BudgetStore update.
    """
    subscription = event_data["object"]
    user_id = subscription["metadata"].get("user_id")
    tier = subscription["metadata"].get("tier", "RESIDENT")
    subscription_id = subscription["id"]
    current_period_end = subscription["current_period_end"]

    logger.info(
        f"Subscription created: {subscription_id} for user {user_id}, tier {tier}"
    )

    return {
        "user_id": user_id,
        "tier": tier,
        "subscription_id": subscription_id,
        "renews_at": datetime.fromtimestamp(current_period_end),
    }


def handle_subscription_updated(event_data: dict[str, Any]) -> dict[str, Any]:
    """
    Handle subscription.updated webhook.

    Returns updated subscription info.
    """
    subscription = event_data["object"]
    user_id = subscription["metadata"].get("user_id")
    tier = subscription["metadata"].get("tier", "RESIDENT")
    status = subscription["status"]
    current_period_end = subscription["current_period_end"]

    logger.info(
        f"Subscription updated: {subscription['id']} for user {user_id}, status={status}"
    )

    return {
        "user_id": user_id,
        "tier": tier,
        "subscription_id": subscription["id"],
        "status": status,
        "renews_at": datetime.fromtimestamp(current_period_end),
    }


def handle_subscription_deleted(event_data: dict[str, Any]) -> dict[str, Any]:
    """
    Handle subscription.deleted webhook.

    Returns user_id to downgrade to TOURIST tier.
    """
    subscription = event_data["object"]
    user_id = subscription["metadata"].get("user_id")

    logger.info(f"Subscription deleted: {subscription['id']} for user {user_id}")

    return {
        "user_id": user_id,
        "tier": "TOURIST",
        "subscription_id": subscription["id"],
    }


def handle_payment_succeeded(event_data: dict[str, Any]) -> dict[str, Any]:
    """
    Handle payment_intent.succeeded webhook (for credit packs).

    Returns user_id and credits to add.
    """
    payment_intent = event_data["object"]
    metadata = payment_intent.get("metadata", {})
    user_id = metadata.get("user_id")
    credits = int(metadata.get("credits", 0))
    pack = metadata.get("pack")

    logger.info(
        f"Payment succeeded: {payment_intent['id']} for user {user_id}, {credits} credits (pack {pack})"
    )

    return {
        "user_id": user_id,
        "credits": credits,
        "pack": pack,
        "payment_intent_id": payment_intent["id"],
    }


# =============================================================================
# Mock Client (for testing without Stripe)
# =============================================================================


class MockPaymentClient:
    """Mock payment client for testing."""

    def __init__(self, api_key: str | None = None, webhook_secret: str | None = None):
        """Initialize mock client."""
        self.api_key = api_key or "mock_key"
        self.webhook_secret = webhook_secret or "mock_secret"
        logger.info("Using MockPaymentClient (Stripe not available)")

    def create_customer(self, user_id: str, email: str, name: str | None = None) -> str:
        """Mock customer creation."""
        return f"cus_mock_{user_id}"

    def get_customer(self, customer_id: str) -> dict[str, Any]:
        """Mock get customer."""
        return {"id": customer_id, "email": "mock@example.com"}

    def create_subscription_checkout(
        self,
        user_id: str,
        tier: str,
        customer_id: str | None = None,
        success_url: str = "https://agenttown.ai/success",
        cancel_url: str = "https://agenttown.ai/cancel",
    ) -> CheckoutSession:
        """Mock subscription checkout."""
        return CheckoutSession(
            session_id=f"cs_mock_{user_id}_{tier}",
            session_url=f"https://mock-checkout.stripe.com/pay/{user_id}_{tier}",
            expires_at=datetime.now() + timedelta(hours=1),
        )

    def create_credit_pack_checkout(
        self,
        user_id: str,
        pack: str,
        customer_id: str | None = None,
        success_url: str = "https://agenttown.ai/success",
        cancel_url: str = "https://agenttown.ai/cancel",
    ) -> CheckoutSession:
        """Mock credit pack checkout."""
        return CheckoutSession(
            session_id=f"cs_mock_{user_id}_{pack}",
            session_url=f"https://mock-checkout.stripe.com/pay/{user_id}_{pack}",
            expires_at=datetime.now() + timedelta(hours=1),
        )

    def get_subscription_info(self, subscription_id: str) -> SubscriptionInfo:
        """Mock get subscription."""
        return SubscriptionInfo(
            subscription_id=subscription_id,
            customer_id="cus_mock",
            tier="RESIDENT",
            status="active",
            current_period_end=datetime.now() + timedelta(days=30),
            cancel_at_period_end=False,
        )

    def cancel_subscription(
        self, subscription_id: str, at_period_end: bool = True
    ) -> PaymentResult:
        """Mock cancel subscription."""
        return PaymentResult(
            success=True,
            message="Mock subscription canceled",
            data={"subscription_id": subscription_id},
        )

    def construct_webhook_event(self, payload: bytes, sig_header: str) -> Any:
        """Mock webhook event construction."""
        import json

        return json.loads(payload)


# =============================================================================
# Factory Function
# =============================================================================


def create_payment_client(use_stripe: bool = True) -> PaymentClient | MockPaymentClient:
    """
    Create a payment client.

    Args:
        use_stripe: If True, use Stripe if available, else mock

    Returns:
        PaymentClient or MockPaymentClient
    """
    if use_stripe and HAS_STRIPE and STRIPE_SECRET_KEY:
        return PaymentClient()
    else:
        logger.info("Using MockPaymentClient (Stripe not configured)")
        return MockPaymentClient()


# =============================================================================
# Exports
# =============================================================================


__all__ = [
    "CheckoutSession",
    "PaymentClient",
    "PaymentResult",
    "SubscriptionInfo",
    "create_payment_client",
    "handle_payment_succeeded",
    "handle_subscription_created",
    "handle_subscription_deleted",
    "handle_subscription_updated",
]
