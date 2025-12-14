"""Pytest configuration for billing tests."""

import sys
from unittest.mock import MagicMock

import pytest

# Create comprehensive stripe mocks before any imports
_stripe_mock = MagicMock()
_stripe_error_mock = MagicMock()

# Set up error classes that the code expects
_stripe_error_mock.InvalidRequestError = type("InvalidRequestError", (Exception,), {})
_stripe_error_mock.SignatureVerificationError = type(
    "SignatureVerificationError", (Exception,), {}
)

# Set stripe.error on the main mock
_stripe_mock.error = _stripe_error_mock

# Inject into sys.modules BEFORE billing modules are imported
sys.modules["stripe"] = _stripe_mock
sys.modules["stripe.error"] = _stripe_error_mock

# Make stripe mock accessible as a global
stripe = _stripe_mock


@pytest.fixture
def mock_stripe() -> MagicMock:
    """Provide the stripe mock as a fixture for tests that need it."""
    return _stripe_mock


@pytest.fixture(scope="session", autouse=True)
def mock_stripe_globally() -> None:
    """Ensure stripe is mocked for all tests in this directory.

    We need to reload billing modules so they pick up the mocked stripe
    from sys.modules. This is necessary because the modules may have been
    imported before conftest.py ran.
    """
    import importlib

    # Remove any cached billing modules that might have bad stripe references
    modules_to_reload = [
        "protocols.billing.customers",
        "protocols.billing.subscriptions",
        "protocols.billing.webhooks",
        "protocols.billing.stripe_client",
    ]

    for mod_name in modules_to_reload:
        if mod_name in sys.modules:
            importlib.reload(sys.modules[mod_name])


@pytest.fixture(autouse=True)
def reset_stripe_mocks() -> None:
    """Reset all stripe mocks between tests."""
    _stripe_mock.reset_mock()
    _stripe_error_mock.reset_mock()
    # Also clear side_effects that may have been set by previous tests
    _stripe_mock.Subscription.retrieve.side_effect = None
    _stripe_mock.Subscription.list.side_effect = None
    _stripe_mock.Subscription.modify.side_effect = None
    _stripe_mock.Subscription.cancel.side_effect = None
    _stripe_mock.Customer.create.side_effect = None
    _stripe_mock.Customer.retrieve.side_effect = None
