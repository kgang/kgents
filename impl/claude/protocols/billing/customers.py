"""
Customer management for Stripe billing.

Handles customer creation, retrieval, and updates.
"""

from dataclasses import dataclass
from typing import Any, Optional, Protocol

try:
    import stripe
    from stripe import StripeError

    STRIPE_AVAILABLE = True
except ImportError:
    STRIPE_AVAILABLE = False
    StripeError = Exception


@dataclass(frozen=True)
class Customer:
    """Represents a Stripe customer."""

    id: str
    email: str
    name: Optional[str] = None
    metadata: Optional[dict[str, str]] = None

    @classmethod
    def from_stripe(cls, stripe_customer: dict[str, Any]) -> "Customer":
        """Create Customer from Stripe customer object.

        Raises:
            ValueError: If customer has no email (required field)
        """
        email = stripe_customer.get("email")
        if not email:
            raise ValueError(
                f"Customer {stripe_customer.get('id', 'unknown')} has no email"
            )
        return cls(
            id=stripe_customer["id"],
            email=email,
            name=stripe_customer.get("name"),
            metadata=stripe_customer.get("metadata"),
        )


class CustomerManagerProtocol(Protocol):
    """Protocol for customer management operations."""

    def create_customer(
        self,
        email: str,
        name: Optional[str] = None,
        metadata: Optional[dict[str, str]] = None,
    ) -> Customer:
        """Create a new customer."""
        ...

    def get_customer(self, customer_id: str) -> Optional[Customer]:
        """Retrieve a customer by ID."""
        ...

    def get_customer_by_email(self, email: str) -> Optional[Customer]:
        """Retrieve a customer by email."""
        ...

    def update_customer(
        self,
        customer_id: str,
        name: Optional[str] = None,
        metadata: Optional[dict[str, str]] = None,
    ) -> Customer:
        """Update customer information."""
        ...

    def delete_customer(self, customer_id: str) -> bool:
        """Delete a customer."""
        ...


class CustomerManager:
    """
    Manages Stripe customer operations.

    Provides a clean interface for creating, retrieving, updating, and
    deleting customers.
    """

    def __init__(self) -> None:
        """Initialize customer manager."""
        if not STRIPE_AVAILABLE:
            raise RuntimeError(
                "stripe package not installed. Install with: pip install stripe"
            )

    def create_customer(
        self,
        email: str,
        name: Optional[str] = None,
        metadata: Optional[dict[str, str]] = None,
    ) -> Customer:
        """
        Create a new Stripe customer.

        Args:
            email: Customer's email address
            name: Customer's name (optional)
            metadata: Additional metadata (optional)

        Returns:
            Created Customer object

        Raises:
            StripeError: If the API call fails
        """
        stripe_customer = stripe.Customer.create(
            email=email,
            name=name,
            metadata=metadata or {},
        )
        return Customer.from_stripe(dict(stripe_customer))

    def get_customer(self, customer_id: str) -> Optional[Customer]:
        """
        Retrieve a customer by ID.

        Args:
            customer_id: Stripe customer ID

        Returns:
            Customer object if found, None otherwise

        Raises:
            StripeError: If the API call fails (except for NotFound)
        """
        try:
            stripe_customer = stripe.Customer.retrieve(customer_id)
            return Customer.from_stripe(dict(stripe_customer))
        except stripe.error.InvalidRequestError:
            return None

    def get_customer_by_email(self, email: str) -> Optional[Customer]:
        """
        Retrieve a customer by email.

        Args:
            email: Customer's email address

        Returns:
            Customer object if found, None otherwise

        Raises:
            StripeError: If the API call fails
        """
        customers = stripe.Customer.list(email=email, limit=1)
        if customers.data:
            return Customer.from_stripe(dict(customers.data[0]))
        return None

    def update_customer(
        self,
        customer_id: str,
        name: Optional[str] = None,
        metadata: Optional[dict[str, str]] = None,
    ) -> Customer:
        """
        Update customer information.

        Args:
            customer_id: Stripe customer ID
            name: New name (optional)
            metadata: New metadata (optional)

        Returns:
            Updated Customer object

        Raises:
            StripeError: If the API call fails
        """
        update_params: dict[str, Any] = {}
        if name is not None:
            update_params["name"] = name
        if metadata is not None:
            update_params["metadata"] = metadata

        stripe_customer = stripe.Customer.modify(customer_id, **update_params)
        return Customer.from_stripe(dict(stripe_customer))

    def delete_customer(self, customer_id: str) -> bool:
        """
        Delete a customer.

        Args:
            customer_id: Stripe customer ID

        Returns:
            True if deleted successfully

        Raises:
            StripeError: If the API call fails
        """
        result = stripe.Customer.delete(customer_id)
        return bool(result.get("deleted", False))
