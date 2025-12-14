"""
Billing infrastructure for kgents.

Stripe integration with subscription management, customer handling, and webhooks.
"""

from protocols.billing.customers import (
    CustomerManager,
    CustomerManagerProtocol,
)
from protocols.billing.openmeter_client import (
    OpenMeterClient,
    OpenMeterConfig,
    UsageEventSchema,
)
from protocols.billing.stripe_client import (
    StripeClient,
    StripeClientProtocol,
    StripeConfig,
    get_stripe_config,
)
from protocols.billing.subscriptions import (
    SubscriptionManager,
    SubscriptionManagerProtocol,
)
from protocols.billing.webhooks import (
    WebhookEvent,
    WebhookHandler,
    WebhookHandlerProtocol,
)

__all__ = [
    "StripeConfig",
    "get_stripe_config",
    "StripeClient",
    "StripeClientProtocol",
    "CustomerManager",
    "CustomerManagerProtocol",
    "SubscriptionManager",
    "SubscriptionManagerProtocol",
    "WebhookHandler",
    "WebhookHandlerProtocol",
    "WebhookEvent",
    "OpenMeterClient",
    "OpenMeterConfig",
    "UsageEventSchema",
]
