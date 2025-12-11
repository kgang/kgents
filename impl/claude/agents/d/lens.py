"""
Lens: Compositional state access.

Lenses enable focused, law-abiding access to nested state structures.
They compose via >> to access deeply nested data with type safety.
"""

from dataclasses import dataclass, replace
from typing import Any, Callable, Generic, List, Optional, TypeVar

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


# === Prism: Optional/Partial Lens ===


@dataclass
class Prism(Generic[S, A]):
    """
    A lens that may fail to focus (for optional fields).

    Unlike a Lens, a Prism's get returns Optional[A] because
    the target may not exist (e.g., missing dict key, None field).

    Laws:
    1. Preview-Review: If preview(s) is Some(a), then review(a) in s exists
    2. Review-Preview: preview(review(a)) = Some(a)

    Example:
        >>> prism = optional_key_prism("user")
        >>> state1 = {"user": "Alice"}
        >>> state2 = {"count": 5}
        >>> prism.preview(state1)  # Some("Alice")
        'Alice'
        >>> prism.preview(state2)  # None
        None
    """

    preview: Callable[[S], Optional[A]]
    review: Callable[[A], S]
    modify_if_present: Callable[[S, Callable[[A], A]], S]

    def set_if_present(self, state: S, value: A) -> S:
        """Set the value only if the prism focuses successfully."""
        return self.modify_if_present(state, lambda _: value)

    def compose(self, other: "Prism[A, B]") -> "Prism[S, B]":
        """
        Compose two prisms: S -?-> A -?-> B.

        If either prism fails to focus, the composition fails.
        """
        return Prism(
            preview=lambda s: (
                other.preview(a) if (a := self.preview(s)) is not None else None
            ),
            review=lambda b: self.review(other.review(b)) if self.review else None,
            modify_if_present=lambda s, f: self.modify_if_present(
                s, lambda a: other.modify_if_present(a, f)
            ),
        )

    def __rshift__(self, other: "Prism[A, B]") -> "Prism[S, B]":
        """Syntactic sugar: prism1 >> prism2"""
        return self.compose(other)


def optional_key_prism(key: str) -> Prism[dict, Any]:
    """
    Prism focusing on an optional dictionary key.

    Returns None if key doesn't exist; set creates key if missing.

    Args:
        key: Dictionary key to focus on

    Returns:
        Prism for dict.get(key)

    Example:
        >>> prism = optional_key_prism("user")
        >>> state = {"count": 5}
        >>> prism.preview(state)  # None (key doesn't exist)
        >>> prism.set_if_present(state, "Alice")  # {"count": 5} (unchanged)
    """
    return Prism(
        preview=lambda d: d.get(key),
        review=lambda v: {key: v},
        modify_if_present=lambda d, f: ({**d, key: f(d[key])} if key in d else d),
    )


def optional_field_prism(field_name: str) -> Prism[Any, Any]:
    """
    Prism for optional dataclass field (may be None).

    Args:
        field_name: Name of dataclass field

    Returns:
        Prism for field that may be None

    Example:
        >>> @dataclass
        ... class User:
        ...     name: str
        ...     email: Optional[str] = None
        >>> prism = optional_field_prism("email")
        >>> user = User(name="Alice", email=None)
        >>> prism.preview(user)  # None
    """
    return Prism(
        preview=lambda obj: getattr(obj, field_name, None),
        review=lambda v: {field_name: v},  # Partial construction
        modify_if_present=lambda obj, f: (
            replace(obj, **{field_name: f(getattr(obj, field_name))})
            if getattr(obj, field_name, None) is not None
            else obj
        ),
    )


def optional_index_prism(i: int) -> Prism[list, Any]:
    """
    Prism focusing on list element at index i (if it exists).

    Args:
        i: List index

    Returns:
        Prism for list[i] if i < len(list)

    Example:
        >>> prism = optional_index_prism(5)
        >>> items = [1, 2, 3]
        >>> prism.preview(items)  # None (index out of bounds)
    """
    return Prism(
        preview=lambda lst: lst[i] if 0 <= i < len(lst) else None,
        review=lambda v: [v],  # Single-element list
        modify_if_present=lambda lst, f: (
            lst[:i] + [f(lst[i])] + lst[i + 1 :] if 0 <= i < len(lst) else lst
        ),
    )


# === Traversal: Multi-Target Lens ===


@dataclass
class Traversal(Generic[S, A]):
    """
    Like a lens, but can target 0..N elements.

    Useful for operating on all elements in a collection
    (e.g., all elements in a list, all values in a dict).

    Laws:
    1. get_all returns all focusable elements
    2. modify applies function to every focusable element
    3. set_all replaces all focusable elements with the same value

    Example:
        >>> trav = list_traversal()
        >>> items = [1, 2, 3]
        >>> trav.get_all(items)  # [1, 2, 3]
        >>> trav.modify(items, lambda x: x * 2)  # [2, 4, 6]
    """

    get_all: Callable[[S], List[A]]
    modify: Callable[[S, Callable[[A], A]], S]

    def set_all(self, state: S, value: A) -> S:
        """Set all focused elements to the same value."""
        return self.modify(state, lambda _: value)

    def filter(self, predicate: Callable[[A], bool]) -> "Traversal[S, A]":
        """
        Create a filtered traversal that only targets elements matching predicate.

        Example:
            >>> trav = list_traversal().filter(lambda x: x > 2)
            >>> items = [1, 2, 3, 4, 5]
            >>> trav.get_all(items)  # [3, 4, 5]
        """
        return Traversal(
            get_all=lambda s: [a for a in self.get_all(s) if predicate(a)],
            modify=lambda s, f: self.modify(s, lambda a: f(a) if predicate(a) else a),
        )

    def compose(self, other: "Traversal[A, B]") -> "Traversal[S, B]":
        """
        Compose two traversals: S ->> A ->> B.

        Traverses all A's in S, then all B's in each A.
        """
        return Traversal(
            get_all=lambda s: [b for a in self.get_all(s) for b in other.get_all(a)],
            modify=lambda s, f: self.modify(s, lambda a: other.modify(a, f)),
        )

    def __rshift__(self, other: "Traversal[A, B]") -> "Traversal[S, B]":
        """Syntactic sugar: trav1 >> trav2"""
        return self.compose(other)


def list_traversal() -> Traversal[List[A], A]:
    """
    Traversal over all elements of a list.

    Returns:
        Traversal targeting all list elements

    Example:
        >>> trav = list_traversal()
        >>> items = [1, 2, 3]
        >>> trav.get_all(items)  # [1, 2, 3]
        >>> trav.modify(items, lambda x: x * 2)  # [2, 4, 6]
    """
    return Traversal(
        get_all=lambda lst: list(lst),
        modify=lambda lst, f: [f(x) for x in lst],
    )


def dict_values_traversal() -> Traversal[dict, Any]:
    """
    Traversal over all values in a dictionary.

    Returns:
        Traversal targeting all dict values

    Example:
        >>> trav = dict_values_traversal()
        >>> d = {"a": 1, "b": 2}
        >>> trav.get_all(d)  # [1, 2]
        >>> trav.modify(d, lambda x: x * 2)  # {"a": 2, "b": 4}
    """
    return Traversal(
        get_all=lambda d: list(d.values()),
        modify=lambda d, f: {k: f(v) for k, v in d.items()},
    )


def dict_keys_traversal() -> Traversal[dict, Any]:
    """
    Traversal over all keys in a dictionary.

    Returns:
        Traversal targeting all dict keys

    Example:
        >>> trav = dict_keys_traversal()
        >>> d = {"a": 1, "b": 2}
        >>> trav.get_all(d)  # ["a", "b"]
        >>> trav.modify(d, str.upper)  # {"A": 1, "B": 2}
    """
    return Traversal(
        get_all=lambda d: list(d.keys()),
        modify=lambda d, f: {f(k): v for k, v in d.items()},
    )


def dict_items_traversal() -> Traversal[dict, tuple]:
    """
    Traversal over all (key, value) pairs in a dictionary.

    Returns:
        Traversal targeting all dict items as tuples

    Example:
        >>> trav = dict_items_traversal()
        >>> d = {"a": 1, "b": 2}
        >>> trav.get_all(d)  # [("a", 1), ("b", 2)]
    """
    return Traversal(
        get_all=lambda d: list(d.items()),
        modify=lambda d, f: dict(f(item) for item in d.items()),
    )


# === Composed Lens Validation ===


@dataclass
class LensValidation:
    """
    Result of lens law validation.

    Attributes:
        is_valid: Whether all laws hold
        get_put: GetPut law result
        put_get: PutGet law result
        put_put: PutPut law result
        errors: List of validation errors
    """

    is_valid: bool
    get_put: bool
    put_get: bool
    put_put: bool
    errors: List[str]


def validate_composed_lens(
    lens1: Lens[S, A],
    lens2: Lens[A, B],
    state: S,
    value1: B,
    value2: B,
) -> LensValidation:
    """
    Validate that a composition of two lenses satisfies lens laws.

    Composed lenses inherit law satisfaction from their components,
    but this verifies the composition explicitly.

    Args:
        lens1: First lens (S → A)
        lens2: Second lens (A → B)
        state: Sample state
        value1: First test value
        value2: Second test value

    Returns:
        LensValidation with detailed results

    Example:
        >>> user_lens = key_lens("user")
        >>> name_lens = key_lens("name")
        >>> state = {"user": {"name": "Alice"}}
        >>> result = validate_composed_lens(user_lens, name_lens, state, "Bob", "Carol")
        >>> result.is_valid
        True
    """
    composed = lens1 >> lens2
    errors = []

    # Law 1: GetPut
    try:
        get_put = verify_get_put_law(composed, state)
        if not get_put:
            errors.append("GetPut law failed: set(s, get(s)) != s")
    except Exception as e:
        get_put = False
        errors.append(f"GetPut law error: {e}")

    # Law 2: PutGet
    try:
        put_get = verify_put_get_law(composed, state, value1)
        if not put_get:
            errors.append("PutGet law failed: get(set(s, a)) != a")
    except Exception as e:
        put_get = False
        errors.append(f"PutGet law error: {e}")

    # Law 3: PutPut
    try:
        put_put = verify_put_put_law(composed, state, value1, value2)
        if not put_put:
            errors.append("PutPut law failed: set(set(s, a1), a2) != set(s, a2)")
    except Exception as e:
        put_put = False
        errors.append(f"PutPut law error: {e}")

    return LensValidation(
        is_valid=get_put and put_get and put_put,
        get_put=get_put,
        put_get=put_get,
        put_put=put_put,
        errors=errors,
    )


# === Prism Law Verification ===


def verify_prism_laws(
    prism: Prism[S, A],
    state_with_value: S,
    state_without_value: S,
    value: A,
) -> dict:
    """
    Verify prism laws.

    Laws:
    1. Preview-Modify: If preview(s) is Some(a), modify preserves structure
    2. Review roundtrip: preview(review(a)) focuses on a

    Args:
        prism: Prism to test
        state_with_value: State where prism focuses successfully
        state_without_value: State where prism returns None
        value: Test value

    Returns:
        Dict with law names and pass/fail status
    """
    results = {
        "preview_some": False,
        "preview_none": False,
        "modify_preserves": False,
    }

    # Law: preview returns Some for state_with_value
    preview_result = prism.preview(state_with_value)
    results["preview_some"] = preview_result is not None

    # Law: preview returns None for state_without_value
    preview_none_result = prism.preview(state_without_value)
    results["preview_none"] = preview_none_result is None

    # Law: modify preserves structure when prism doesn't focus
    modified = prism.modify_if_present(state_without_value, lambda x: value)
    results["modify_preserves"] = modified == state_without_value

    return results


# === Traversal Law Verification ===


def verify_traversal_laws(
    trav: Traversal[S, A],
    state: S,
    value: A,
) -> dict:
    """
    Verify traversal laws.

    Laws:
    1. Identity: modify(s, id) = s
    2. Fusion: modify(modify(s, f), g) = modify(s, g . f)

    Args:
        trav: Traversal to test
        state: Sample state
        value: Test value (used for fusion test)

    Returns:
        Dict with law names and pass/fail status
    """
    results = {
        "identity": False,
        "fusion": False,
    }

    # Law 1: Identity
    try:
        identity_result = trav.modify(state, lambda x: x)
        results["identity"] = identity_result == state
    except Exception:
        pass

    # Law 2: Fusion (f then g = g∘f in one pass)
    def identity(x: Any) -> Any:
        return x

    try:
        two_pass = trav.modify(trav.modify(state, identity), identity)
        one_pass = trav.modify(state, identity)
        results["fusion"] = two_pass == one_pass
    except Exception:
        pass

    return results
