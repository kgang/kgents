# Lenses: Compositional State Access

Lenses enable focused, composable access to nested state structures.

---

## Motivation

**Problem**: Agents often need access to only a *portion* of system state.

**Bad Solution**: Pass entire state, trust agent to access only relevant parts
- No type safety
- Difficult to enforce boundaries
- Agents see more than needed (violates least privilege)

**Good Solution**: Use **Lenses** to project state
- Agent receives only the sub-state it needs
- Type-checked at compile time
- Composable: lenses chain to access deeply nested structures

---

## Definition

A **Lens** is a pair of functions that focus on a sub-part of a larger structure:

```python
from typing import TypeVar, Generic, Callable
from dataclasses import dataclass

S = TypeVar("S")  # Whole state
A = TypeVar("A")  # Sub-state (focus)

@dataclass
class Lens(Generic[S, A]):
    """
    A composable getter/setter for accessing sub-state.

    Laws:
    1. GetPut: set(s, get(s)) = s
    2. PutGet: get(set(s, a)) = a
    3. PutPut: set(set(s, a1), a2) = set(s, a2)
    """

    get: Callable[[S], A]
    set: Callable[[S, A], S]

    def compose(self, other: "Lens[A, B]") -> "Lens[S, B]":
        """
        Compose two lenses to access deeply nested state.

        If self: S → A and other: A → B, returns: S → B
        """
        return Lens(
            get=lambda s: other.get(self.get(s)),
            set=lambda s, b: self.set(s, other.set(self.get(s), b))
        )

    def __rshift__(self, other: "Lens[A, B]") -> "Lens[S, B]":
        """Syntactic sugar: lens1 >> lens2"""
        return self.compose(other)
```

---

## The Lens Laws

Lenses must satisfy three laws to be considered "well-behaved":

### Law 1: GetPut (You Get What You Set)

```python
lens.set(state, lens.get(state)) == state
```

Setting a value to what you just got leaves state unchanged.

**Example**:
```python
state = {"user": {"name": "Alice"}}
name_lens = Lens(
    get=lambda s: s["user"]["name"],
    set=lambda s, n: {**s, "user": {**s["user"], "name": n}}
)

# Get current name, set it back → no change
name = name_lens.get(state)
new_state = name_lens.set(state, name)
assert new_state == state  # ✓ GetPut satisfied
```

### Law 2: PutGet (You Set What You Get)

```python
lens.get(lens.set(state, value)) == value
```

After setting a value, getting it returns that value.

**Example**:
```python
state = {"user": {"name": "Alice"}}
new_state = name_lens.set(state, "Bob")
assert name_lens.get(new_state) == "Bob"  # ✓ PutGet satisfied
```

### Law 3: PutPut (Last Set Wins)

```python
lens.set(lens.set(state, a), b) == lens.set(state, b)
```

Setting twice is equivalent to setting once with the final value.

**Example**:
```python
state = {"user": {"name": "Alice"}}
result1 = name_lens.set(name_lens.set(state, "Bob"), "Carol")
result2 = name_lens.set(state, "Carol")
assert result1 == result2  # ✓ PutPut satisfied
```

---

## Basic Lens Examples

### Lens 1: Dictionary Key

```python
def key_lens(key: str) -> Lens[dict, Any]:
    """Lens focusing on a dictionary key."""
    return Lens(
        get=lambda d: d.get(key),
        set=lambda d, v: {**d, key: v}
    )

# Usage
user_lens = key_lens("user")
state = {"user": "Alice", "count": 5}

user = user_lens.get(state)  # "Alice"
new_state = user_lens.set(state, "Bob")  # {"user": "Bob", "count": 5}
```

### Lens 2: Dataclass Field

```python
from dataclasses import dataclass, replace

@dataclass
class User:
    name: str
    age: int

def field_lens(field_name: str) -> Lens[Any, Any]:
    """Lens for dataclass field."""
    return Lens(
        get=lambda obj: getattr(obj, field_name),
        set=lambda obj, val: replace(obj, **{field_name: val})
    )

# Usage
name_lens = field_lens("name")
user = User(name="Alice", age=30)

name = name_lens.get(user)  # "Alice"
new_user = name_lens.set(user, "Bob")  # User(name="Bob", age=30)
```

### Lens 3: List Index

```python
def index_lens(i: int) -> Lens[list, Any]:
    """Lens focusing on list element at index i."""
    return Lens(
        get=lambda lst: lst[i],
        set=lambda lst, v: lst[:i] + [v] + lst[i+1:]
    )

# Usage
first_lens = index_lens(0)
items = [1, 2, 3]

first = first_lens.get(items)  # 1
new_items = first_lens.set(items, 10)  # [10, 2, 3]
```

---

## Lens Composition

The power of lenses: they **compose** to access deeply nested structures.

### Example: Nested State Access

```python
from dataclasses import dataclass

@dataclass
class Address:
    city: str
    zip: str

@dataclass
class User:
    name: str
    address: Address

@dataclass
class State:
    user: User
    settings: dict

# Build lenses for each level
user_lens = field_lens("user")
address_lens = field_lens("address")
city_lens = field_lens("city")

# Compose: State → User → Address → city
city_in_state = user_lens >> address_lens >> city_lens

# Usage
state = State(
    user=User(name="Alice", address=Address(city="NYC", zip="10001")),
    settings={}
)

city = city_in_state.get(state)  # "NYC"
new_state = city_in_state.set(state, "SF")
# State(user=User(name="Alice", address=Address(city="SF", zip="10001")), ...)
```

**Without lenses**, this would be:
```python
# Getter (ugly)
city = state.user.address.city

# Setter (very ugly - easy to forget immutability)
new_state = replace(
    state,
    user=replace(
        state.user,
        address=replace(state.user.address, city="SF")
    )
)
```

---

## LensAgent: D-gent with Focused Access

A `LensAgent` wraps a parent D-gent and a lens to provide focused state access:

```python
from typing import Generic, TypeVar

S = TypeVar("S")  # Parent state
A = TypeVar("A")  # Sub-state

@dataclass
class LensAgent(Generic[S, A]):
    """
    A D-gent that provides a focused view into parent state.

    Reads and writes are projected through the lens.
    """

    parent: DataAgent[S]
    lens: Lens[S, A]

    async def load(self) -> A:
        """Load parent state, project to sub-state."""
        full_state = await self.parent.load()
        return self.lens.get(full_state)

    async def save(self, sub_state: A) -> None:
        """Update sub-state within parent state."""
        full_state = await self.parent.load()
        new_full_state = self.lens.set(full_state, sub_state)
        await self.parent.save(new_full_state)

    async def history(self, limit: int | None = None) -> list[A]:
        """Project historical states through lens."""
        full_history = await self.parent.history(limit)
        return [self.lens.get(s) for s in full_history]
```

---

## Use Case: Multi-Agent Shared State

**Scenario**: Multiple agents share global state, but each should only access their domain.

```python
@dataclass
class GlobalState:
    users: dict
    products: dict
    orders: dict

# Create lenses for each domain
users_lens = key_lens("users")
products_lens = key_lens("products")
orders_lens = key_lens("orders")

# Global D-gent
global_dgent = PersistentAgent[GlobalState]("global.json", GlobalState)

# Create focused D-gents for each agent
user_dgent = LensAgent(global_dgent, users_lens)
product_dgent = LensAgent(global_dgent, products_lens)
order_dgent = LensAgent(global_dgent, orders_lens)

# Agents with restricted access
user_agent = Symbiont(user_logic, user_dgent)      # Sees only users
product_agent = Symbiont(product_logic, product_dgent)  # Sees only products
order_agent = Symbiont(order_logic, order_dgent)    # Sees only orders

# Each agent operates on full global state, but lens restricts view
await user_agent.invoke("create_user")    # Modifies users only
await product_agent.invoke("add_item")    # Modifies products only
```

**Benefits**:
- **Least Privilege**: Each agent sees minimal state
- **Type Safety**: Compiler ensures agent accesses correct structure
- **Coordination**: All agents share consistent global state
- **Testability**: Can test agent with isolated sub-state

---

## Advanced: Traversals and Prisms

### Traversal: Lens for Multiple Targets

A **Traversal** is a generalized lens that focuses on *multiple* elements.

```python
@dataclass
class Traversal(Generic[S, A]):
    """
    Like a lens, but can target 0..N elements.

    Example: All elements in a list, all values in a dict
    """

    get_all: Callable[[S], list[A]]
    modify: Callable[[S, Callable[[A], A]], S]

# Example: Traverse all list elements
def list_traversal() -> Traversal[list[A], A]:
    return Traversal(
        get_all=lambda lst: lst,
        modify=lambda lst, f: [f(x) for x in lst]
    )

# Usage
trav = list_traversal()
items = [1, 2, 3]
doubled = trav.modify(items, lambda x: x * 2)  # [2, 4, 6]
```

### Prism: Lens for Optional Targets

A **Prism** is a lens that may fail to focus (e.g., accessing a dictionary key that doesn't exist).

```python
from typing import Optional

@dataclass
class Prism(Generic[S, A]):
    """
    A lens that may fail to focus.

    Example: Accessing optional dict key, parsing string to int
    """

    get_opt: Callable[[S], Optional[A]]
    set_if_present: Callable[[S, A], S]

# Example: Optional dictionary key
def optional_key_prism(key: str) -> Prism[dict, Any]:
    return Prism(
        get_opt=lambda d: d.get(key),
        set_if_present=lambda d, v: {**d, key: v} if key in d else d
    )

# Usage
prism = optional_key_prism("user")
state1 = {"user": "Alice"}
state2 = {"count": 5}

prism.get_opt(state1)  # Some("Alice")
prism.get_opt(state2)  # None

prism.set_if_present(state1, "Bob")  # {"user": "Bob"}
prism.set_if_present(state2, "Bob")  # {"count": 5} (unchanged)
```

---

## Performance Considerations

### Trade-off: Convenience vs. Copies

Lenses that satisfy the laws must return *new* structures (immutability). This means:
- **Benefit**: No hidden mutation, easy reasoning
- **Cost**: Copying data on every `set`

For large state structures, consider:
1. **Structural Sharing**: Use persistent data structures (e.g., `pyrsistent`)
2. **Mutable Lenses**: Opt-out of immutability for hot paths (but lose guarantees)
3. **Lens Batching**: Apply multiple updates, copy once

### Optimization: Lens Fusion

When composing many lenses, intermediate allocations can add up:

```python
# Naive: Creates 3 intermediate copies
state1 = lens1.set(state, v1)
state2 = lens2.set(state1, v2)
state3 = lens3.set(state2, v3)

# Optimized: Batch updates
state_final = batch_set(state, [
    (lens1, v1),
    (lens2, v2),
    (lens3, v3)
])  # Single copy at end
```

---

## Testing Lenses

All lenses should be tested for the three laws:

```python
def test_lens_laws(lens: Lens[S, A], state: S, value: A):
    """Verify lens satisfies GetPut, PutGet, PutPut."""

    # Law 1: GetPut
    current = lens.get(state)
    unchanged = lens.set(state, current)
    assert unchanged == state

    # Law 2: PutGet
    new_state = lens.set(state, value)
    retrieved = lens.get(new_state)
    assert retrieved == value

    # Law 3: PutPut
    other_value = ...  # Some other valid value
    result1 = lens.set(lens.set(state, value), other_value)
    result2 = lens.set(state, other_value)
    assert result1 == result2
```

---

## Anti-patterns

### Anti-pattern 1: Lens Abuse

```python
# BAD: Lens chain so deep it's unreadable
deeply_nested = (
    lens1 >> lens2 >> lens3 >> lens4 >> lens5 >> lens6
)

# BETTER: Flatten state structure, or use direct access if truly needed
```

### Anti-pattern 2: Mutable Lenses

```python
# BAD: Lens violates laws by mutating
bad_lens = Lens(
    get=lambda d: d["key"],
    set=lambda d, v: d.update({"key": v}) or d  # MUTATES!
)

# GOOD: Return new structure
good_lens = Lens(
    get=lambda d: d["key"],
    set=lambda d, v: {**d, "key": v}
)
```

### Anti-pattern 3: Lens for Everything

```python
# BAD: Using lens when direct access is clearer
name = user_lens.get(state)  # Overkill if state is simple

# GOOD: Use lens when you need composition or abstraction
name = state["user"]  # Direct access is fine for simple cases
```

---

## Relationship to Category Theory

Lenses are **comonads** in the category of states:

- **Objects**: State types $S$, $A$
- **Morphisms**: Lenses $\text{Lens}[S, A]$
- **Composition**: `lens1 >> lens2`
- **Identity**: $\text{id}_S = \text{Lens}(\text{get}=\lambda s: s, \text{set}=\lambda s, a: a)$

The lens laws correspond to:
- **GetPut**: Counit law
- **PutGet**: Unit law
- **PutPut**: Associativity

This makes lenses **composable** in the same sense that agents are composable (via C-gents).

---

## See Also

- [README.md](README.md) - D-gents overview
- [protocols.md](protocols.md) - DataAgent interface
- [symbiont.md](symbiont.md) - Using lenses with Symbiont pattern
- [../c-gents/functors.md](../c-gents/functors.md) - Structure-preserving transformations
