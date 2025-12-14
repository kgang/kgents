"""Tests for customer management."""

# Get the mocked stripe from sys.modules (set up in conftest.py)
import sys
from datetime import datetime
from typing import Any
from unittest.mock import MagicMock, Mock, patch

import pytest
from protocols.billing.customers import (
    Customer,
    CustomerManager,
)

mock_stripe = sys.modules["stripe"]


@pytest.fixture
def customer_manager() -> CustomerManager:
    """Create customer manager with mocked stripe."""
    with patch("protocols.billing.customers.STRIPE_AVAILABLE", True):
        return CustomerManager()


def make_stripe_customer(
    customer_id: str = "cus_test123",
    email: str = "test@example.com",
    name: str | None = "Test User",
    metadata: dict[str, str] | None = {"default": "true"},
) -> dict[str, Any]:
    """Create a mock Stripe customer object."""
    result: dict[str, Any] = {
        "id": customer_id,
        "email": email,
        "name": name,
        "object": "customer",
        "created": int(datetime.now().timestamp()),
    }
    if metadata is not None:
        result["metadata"] = metadata
    return result


class TestCustomer:
    """Tests for Customer dataclass."""

    def test_from_stripe(self) -> None:
        """Test creating Customer from Stripe object."""
        stripe_customer = make_stripe_customer(
            customer_id="cus_abc123",
            email="alice@example.com",
            name="Alice",
            metadata={"user_id": "123"},
        )

        customer = Customer.from_stripe(stripe_customer)

        assert customer.id == "cus_abc123"
        assert customer.email == "alice@example.com"
        assert customer.name == "Alice"
        assert customer.metadata == {"user_id": "123"}

    def test_from_stripe_minimal(self) -> None:
        """Test creating Customer with minimal data."""
        stripe_customer = make_stripe_customer(name=None, metadata=None)

        customer = Customer.from_stripe(stripe_customer)

        assert customer.id == "cus_test123"
        assert customer.email == "test@example.com"
        assert customer.name is None
        assert customer.metadata is None

    def test_from_stripe_no_email_raises_error(self) -> None:
        """Test that from_stripe raises ValueError when customer has no email."""
        stripe_customer = {
            "id": "cus_noemail123",
            "email": None,  # No email
            "name": "Test User",
        }

        with pytest.raises(ValueError, match="has no email"):
            Customer.from_stripe(stripe_customer)

    def test_from_stripe_empty_email_raises_error(self) -> None:
        """Test that from_stripe raises ValueError when customer has empty email."""
        stripe_customer = {
            "id": "cus_emptyemail123",
            "email": "",  # Empty email
            "name": "Test User",
        }

        with pytest.raises(ValueError, match="has no email"):
            Customer.from_stripe(stripe_customer)


class TestCustomerManager:
    """Tests for CustomerManager."""

    def test_init_without_stripe(self) -> None:
        """Test initialization fails without stripe package."""
        with patch("protocols.billing.customers.STRIPE_AVAILABLE", False):
            with pytest.raises(RuntimeError, match="stripe package not installed"):
                CustomerManager()

    def test_create_customer(self, customer_manager: CustomerManager) -> None:
        """Test creating a customer."""
        mock_stripe.Customer.create.return_value = make_stripe_customer(
            customer_id="cus_new123",
            email="new@example.com",
            name="New User",
            metadata={"source": "test"},
        )

        customer = customer_manager.create_customer(
            email="new@example.com",
            name="New User",
            metadata={"source": "test"},
        )

        assert customer.id == "cus_new123"
        assert customer.email == "new@example.com"
        assert customer.name == "New User"
        assert customer.metadata == {"source": "test"}

        mock_stripe.Customer.create.assert_called_once_with(
            email="new@example.com",
            name="New User",
            metadata={"source": "test"},
        )

    def test_create_customer_minimal(self, customer_manager: CustomerManager) -> None:
        """Test creating customer with minimal data."""
        mock_stripe.Customer.create.return_value = make_stripe_customer(
            email="minimal@example.com",
            name=None,
        )

        customer = customer_manager.create_customer(email="minimal@example.com")

        assert customer.email == "minimal@example.com"
        mock_stripe.Customer.create.assert_called_once_with(
            email="minimal@example.com",
            name=None,
            metadata={},
        )

    def test_get_customer(self, customer_manager: CustomerManager) -> None:
        """Test retrieving a customer by ID."""
        mock_stripe.Customer.retrieve.return_value = make_stripe_customer(
            customer_id="cus_get123"
        )

        customer = customer_manager.get_customer("cus_get123")

        assert customer is not None
        assert customer.id == "cus_get123"
        mock_stripe.Customer.retrieve.assert_called_once_with("cus_get123")

    def test_get_customer_not_found(self, customer_manager: CustomerManager) -> None:
        """Test retrieving non-existent customer returns None."""
        mock_stripe.error.InvalidRequestError = Exception
        mock_stripe.Customer.retrieve.side_effect = (
            mock_stripe.error.InvalidRequestError("Not found")
        )

        customer = customer_manager.get_customer("cus_nonexistent")

        assert customer is None

    def test_get_customer_by_email(self, customer_manager: CustomerManager) -> None:
        """Test retrieving customer by email."""
        mock_list = MagicMock()
        mock_list.data = [
            make_stripe_customer(customer_id="cus_email123", email="search@example.com")
        ]
        mock_stripe.Customer.list.return_value = mock_list

        customer = customer_manager.get_customer_by_email("search@example.com")

        assert customer is not None
        assert customer.id == "cus_email123"
        assert customer.email == "search@example.com"
        mock_stripe.Customer.list.assert_called_once_with(
            email="search@example.com", limit=1
        )

    def test_get_customer_by_email_not_found(
        self, customer_manager: CustomerManager
    ) -> None:
        """Test email search with no results returns None."""
        mock_list = MagicMock()
        mock_list.data = []
        mock_stripe.Customer.list.return_value = mock_list

        customer = customer_manager.get_customer_by_email("nonexistent@example.com")

        assert customer is None

    def test_update_customer_name(self, customer_manager: CustomerManager) -> None:
        """Test updating customer name."""
        mock_stripe.Customer.modify.return_value = make_stripe_customer(
            customer_id="cus_update123",
            email="update@example.com",
            name="Updated Name",
        )

        customer = customer_manager.update_customer(
            "cus_update123", name="Updated Name"
        )

        assert customer.name == "Updated Name"
        mock_stripe.Customer.modify.assert_called_once_with(
            "cus_update123", name="Updated Name"
        )

    def test_update_customer_metadata(self, customer_manager: CustomerManager) -> None:
        """Test updating customer metadata."""
        mock_stripe.Customer.modify.return_value = make_stripe_customer(
            customer_id="cus_meta123",
            metadata={"updated": "true"},
        )

        customer = customer_manager.update_customer(
            "cus_meta123", metadata={"updated": "true"}
        )

        assert customer.metadata == {"updated": "true"}
        mock_stripe.Customer.modify.assert_called_once_with(
            "cus_meta123", metadata={"updated": "true"}
        )

    def test_update_customer_both(self, customer_manager: CustomerManager) -> None:
        """Test updating both name and metadata."""
        mock_stripe.Customer.modify.return_value = make_stripe_customer(
            customer_id="cus_both123",
            name="Both Updated",
            metadata={"key": "value"},
        )

        customer = customer_manager.update_customer(
            "cus_both123",
            name="Both Updated",
            metadata={"key": "value"},
        )

        assert customer.name == "Both Updated"
        assert customer.metadata == {"key": "value"}
        mock_stripe.Customer.modify.assert_called_once_with(
            "cus_both123",
            name="Both Updated",
            metadata={"key": "value"},
        )

    def test_delete_customer(self, customer_manager: CustomerManager) -> None:
        """Test deleting a customer."""
        mock_stripe.Customer.delete.return_value = {"deleted": True, "id": "cus_del123"}

        result = customer_manager.delete_customer("cus_del123")

        assert result is True
        mock_stripe.Customer.delete.assert_called_once_with("cus_del123")

    def test_delete_customer_failed(self, customer_manager: CustomerManager) -> None:
        """Test delete returning False on failure."""
        mock_stripe.Customer.delete.return_value = {"deleted": False}

        result = customer_manager.delete_customer("cus_fail123")

        assert result is False
