# Keybinding Registry

The keybinding system for the Hypergraph Editor, implementing the four-layer keybinding grammar from the spec.

## Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                    KeybindingRegistry                       │
│  Maps key sequences → EditorInput (mode-aware)              │
└─────────────────────────────────────────────────────────────┘
                           ▲
                           │
        ┌──────────────────┴──────────────────┐
        │                                     │
   ┌────────────┐                      ┌─────────────┐
   │  Registry  │                      │  Defaults   │
   │    Core    │                      │  (4 Layers) │
   └────────────┘                      └─────────────┘
   - resolve()                         - Layer 1: Vim
   - is_prefix()                       - Layer 2: Graph
   - register()                        - Layer 3: Modes
                                       - Layer 4: AST
```

## Usage

### Basic Resolution

```python
from services.hypergraph_editor.keybindings import (
    create_default_registry,
    KeybindingRegistry,
)
from services.hypergraph_editor.core.types import EditorMode

# Create registry with defaults
registry = create_default_registry()

# Resolve key sequence
input = registry.resolve("gh", EditorMode.NORMAL)
# → NavigateInput(direction="parent")

input = registry.resolve("i", EditorMode.NORMAL)
# → ModeEnterInput(target_mode=EditorMode.INSERT)

input = registry.resolve("<Esc>", EditorMode.INSERT)
# → ModeExitInput()
```

### Multi-Key Sequences

The registry supports multi-key sequences with prefix detection:

```python
# Check if partial sequence is valid
is_valid = registry.is_prefix("g", EditorMode.NORMAL)
# → True (could be "gh", "gl", "gj", "gk", etc.)

# After second key
input = registry.resolve("gh", EditorMode.NORMAL)
# → NavigateInput(direction="parent")
```

### Custom Bindings

```python
from services.hypergraph_editor.keybindings import KeyBinding

# Create custom registry
registry = KeybindingRegistry()

# Register custom binding
registry.register(KeyBinding(
    keys="<Leader>e",
    modes=frozenset([EditorMode.NORMAL]),
    input_factory=lambda: ModeEnterInput(target_mode=EditorMode.PORTAL),
    description="Quick portal entry"
))
```

### Mode-Specific Bindings

Same key can have different meanings in different modes:

```python
# 'j' in NORMAL → move down
input = registry.resolve("j", EditorMode.NORMAL)
# → NavigateInput(direction="down")

# 'j' in VISUAL → extend selection down
input = registry.resolve("j", EditorMode.VISUAL)
# → SelectExtendInput(direction="down")

# 'j' in GRAPH → pan down
input = registry.resolve("j", EditorMode.GRAPH)
# → PanInput(direction="down")
```

## The Four Layers

### Layer 1: Traditional Vim (Within Node)

```python
j/k         # Line down/up → NavigateInput(direction="down"/"up")
h/l         # Column left/right
w/b/e       # Word motions
gg/G        # Node start/end
0/$         # Line start/end
```

### Layer 2: Graph Navigation (g-prefix)

```python
gh          # Parent → NavigateInput(direction="parent")
gl          # Child → NavigateInput(direction="child")
gj/gk       # Next/prev sibling
gd          # Definition
gr          # References
gt          # Tests
gf          # Follow edge under cursor
```

### Layer 3: Mode Entry

```python
i/a         # INSERT mode → ModeEnterInput(target_mode=INSERT)
v/V         # VISUAL mode
:           # COMMAND mode
e           # PORTAL mode
g           # GRAPH mode
<Leader>k   # KBLOCK mode
<Esc>       # Exit → NORMAL (universal)
```

### Layer 4: Structural Selection (Tree-sitter)

```python
(/)         # Expand/shrink to parent/child AST node
[/]         # Previous/next sibling AST node
{/}         # Function/class boundaries
```

## Integration with Editor

The keybinding registry is used by the editor's input handler:

```python
class EditorInputHandler:
    def __init__(self):
        self.registry = create_default_registry()
        self.pending = PendingSequence()

    def handle_key(self, key: str, mode: EditorMode) -> EditorInput | None:
        # Accumulate keys
        self.pending.keys += key

        # Try to resolve
        input = self.registry.resolve(self.pending.keys, mode)
        if input:
            self.pending.keys = ""  # Reset
            return input

        # Check if prefix (wait for more keys)
        if self.registry.is_prefix(self.pending.keys, mode):
            return None  # Keep waiting

        # Invalid sequence
        self.pending.keys = ""  # Reset
        return None
```

## Design Principles

1. **Mode Awareness**: Same key can mean different things in different modes
2. **Prefix Detection**: Multi-key sequences are supported with timeout
3. **Immutability**: KeyBinding is frozen dataclass
4. **Composition**: Factory functions create inputs (allows parameterization)
5. **Discoverability**: All bindings expose descriptions for help/docs

## File Structure

```
keybindings/
├── __init__.py          # Package exports
├── registry.py          # Core registry implementation
├── defaults.py          # Default 4-layer bindings
└── README.md            # This file
```

## Testing

```python
# Example test
def test_graph_navigation():
    registry = create_default_registry()

    # Test all graph navigation keys
    assert isinstance(
        registry.resolve("gh", EditorMode.NORMAL),
        NavigateInput
    )
    assert registry.resolve("gh", EditorMode.NORMAL).direction == "parent"

    assert registry.resolve("gl", EditorMode.NORMAL).direction == "child"
    assert registry.resolve("gj", EditorMode.NORMAL).direction == "next_sibling"
    assert registry.resolve("gk", EditorMode.NORMAL).direction == "prev_sibling"
```

## Future Enhancements

- [ ] Configurable leader key (Space, comma, etc.)
- [ ] User-defined keybinding overlays
- [ ] Keybinding persistence (save custom bindings)
- [ ] Help system integration (show available keys in mode)
- [ ] Recording/replay of key sequences
- [ ] Timeout configuration per sequence

---

*See: spec/surfaces/hypergraph-editor.md § Keybindings*
