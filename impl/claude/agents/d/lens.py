"""
Lens: Compositional state access.

Lenses enable focused, law-abiding access to nested state structures.
They compose via >> to access deeply nested data with type safety.
"""

from typing import TypeVar, Generic, Callable, Any
from dataclasses import dataclass, replace

S = TypeVar("S")  # Whole state
A = TypeVar("A")  # Sub-state (focus)
B = TypeVar("B")  # Deeper sub-state


@dataclass
class Lens(Generic[S, A]):
    """
    A composable getter/setter for accessing sub-state.

    A lens focuses on part of a larger structure, providing:
    - get: S → A (extract sub-state)
    - set: S × A → S (update sub-state, return new whole)

    Laws (must be satisfied):
    1. GetPut: set(s, get(s)) = s
    2. PutGet: get(set(s, a)) = a
    3. PutPut: set(set(s, a1), a2) = set(s, a2)

    Example:
        >>> name_lens = key_lens("name")
        >>> state = {"name": "Alice", "age": 30}
        >>> name_lens.get(state)
        'Alice'
        >>> name_lens.set(state, "Bob")
        {'name': 'Bob', 'age': 30}
    """

    get: Callable[[S], A]
    set: Callable[[S, A], S]

    def compose(self, other: "Lens[A, B]") -> "Lens[S, B]":
        """
        Compose two lenses to access deeply nested state.

        If self: S → A and other: A → B, returns: S → B

        Args:
            other: Lens from A to B

        Returns:
            Composed lens from S to B

        Example:
            >>> user_lens = key_lens("user")
            >>> name_lens = key_lens("name")
            >>> full_lens = user_lens >> name_lens
            >>> state = {"user": {"name": "Alice"}}
            >>> full_lens.get(state)
            'Alice'
        """
        return Lens(
            get=lambda s: other.get(self.get(s)),
            set=lambda s, b: self.set(s, other.set(self.get(s), b)),
        )

    def __rshift__(self, other: "Lens[A, B]") -> "Lens[S, B]":
        """Syntactic sugar: lens1 >> lens2"""
        return self.compose(other)


# === Lens Factories ===


def identity_lens() -> Lens[S, S]:
    """
    Identity lens (focuses on whole state).

    Satisfies: id >> lens = lens = lens >> id

    Returns:
        Lens that returns state unchanged
    """
    return Lens(get=lambda s: s, set=lambda s, a: a)


def key_lens(key: str) -> Lens[dict, Any]:
    """
    Lens focusing on a dictionary key.

    Args:
        key: Dictionary key to focus on

    Returns:
        Lens for dict[key]

    Example:
        >>> lens = key_lens("user")
        >>> state = {"user": "Alice", "count": 5}
        >>> lens.get(state)
        'Alice'
        >>> lens.set(state, "Bob")
        {'user': 'Bob', 'count': 5}
    """
    return Lens(get=lambda d: d.get(key), set=lambda d, v: {**d, key: v})


def field_lens(field_name: str) -> Lens[Any, Any]:
    """
    Lens for dataclass field.

    Args:
        field_name: Name of dataclass field

    Returns:
        Lens for field

    Example:
        >>> from dataclasses import dataclass
        >>> @dataclass
        ... class User:
        ...     name: str
        ...     age: int
        >>> lens = field_lens("name")
        >>> user = User(name="Alice", age=30)
        >>> lens.get(user)
        'Alice'
        >>> lens.set(user, "Bob")
        User(name='Bob', age=30)
    """
    return Lens(
        get=lambda obj: getattr(obj, field_name),
        set=lambda obj, val: replace(obj, **{field_name: val}),
    )


def index_lens(i: int) -> Lens[list, Any]:
    """
    Lens focusing on list element at index i.

    Args:
        i: List index

    Returns:
        Lens for list[i]

    Example:
        >>> lens = index_lens(0)
        >>> items = [1, 2, 3]
        >>> lens.get(items)
        1
        >>> lens.set(items, 10)
        [10, 2, 3]
    """
    return Lens(get=lambda lst: lst[i], set=lambda lst, v: lst[:i] + [v] + lst[i + 1 :])


def attr_lens(attr_name: str) -> Lens[Any, Any]:
    """
    Lens for object attribute (mutable objects).

    WARNING: This lens mutates the object, violating lens laws.
    Use field_lens for dataclasses instead (immutable).

    Args:
        attr_name: Attribute name

    Returns:
        Lens for obj.attr

    Example:
        >>> class Mutable:
        ...     def __init__(self, value):
        ...         self.value = value
        >>> lens = attr_lens("value")
        >>> obj = Mutable(42)
        >>> lens.get(obj)
        42
    """

    # WARNING: Violates laws if used with mutation
    def setter(obj: Any, val: Any) -> Any:
        # Create shallow copy
        import copy

        new_obj = copy.copy(obj)
        setattr(new_obj, attr_name, val)
        return new_obj

    return Lens(get=lambda obj: getattr(obj, attr_name), set=setter)


# === Lens Law Verification ===


def verify_get_put_law(lens: Lens[S, A], state: S) -> bool:
    """
    Verify GetPut law: set(s, get(s)) = s

    Args:
        lens: Lens to test
        state: Sample state

    Returns:
        True if law holds
    """
    current = lens.get(state)
    unchanged = lens.set(state, current)
    return unchanged == state


def verify_put_get_law(lens: Lens[S, A], state: S, value: A) -> bool:
    """
    Verify PutGet law: get(set(s, a)) = a

    Args:
        lens: Lens to test
        state: Sample state
        value: Value to set

    Returns:
        True if law holds
    """
    new_state = lens.set(state, value)
    retrieved = lens.get(new_state)
    return retrieved == value


def verify_put_put_law(lens: Lens[S, A], state: S, a1: A, a2: A) -> bool:
    """
    Verify PutPut law: set(set(s, a1), a2) = set(s, a2)

    Args:
        lens: Lens to test
        state: Sample state
        a1: First value
        a2: Second value

    Returns:
        True if law holds
    """
    result1 = lens.set(lens.set(state, a1), a2)
    result2 = lens.set(state, a2)
    return result1 == result2


def verify_lens_laws(lens: Lens[S, A], state: S, value1: A, value2: A) -> dict:
    """
    Verify all three lens laws.

    Args:
        lens: Lens to test
        state: Sample state
        value1: First test value
        value2: Second test value

    Returns:
        Dict with law names and pass/fail status

    Example:
        >>> lens = key_lens("name")
        >>> state = {"name": "Alice", "age": 30}
        >>> results = verify_lens_laws(lens, state, "Bob", "Carol")
        >>> results
        {'get_put': True, 'put_get': True, 'put_put': True}
    """
    return {
        "get_put": verify_get_put_law(lens, state),
        "put_get": verify_put_get_law(lens, state, value1),
        "put_put": verify_put_put_law(lens, state, value1, value2),
    }
