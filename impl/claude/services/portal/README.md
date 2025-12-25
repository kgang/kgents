# Portal Resource System

**Status:** Phase 1 Complete (Core Infrastructure)
**Date:** 2025-12-25
**Spec:** `spec/protocols/portal-resource-system.md`

## Overview

The Portal Resource System provides universal resource addressing and expansion for all kgents concepts.

> *"Every kgents concept is addressable. Every address is expandable."*

## What's Implemented (Phase 1)

### 1. URI Parser (`uri.py`)

```python
from services.portal import PortalURI

# Parse URIs
uri = PortalURI.parse("file:spec/protocols/witness.md")
uri = PortalURI.parse("chat:session-abc123#turn-5")
uri = PortalURI.parse("spec/README.md")  # Implicit file: prefix

# Roundtrip
assert uri.render() == original_uri
```

**Features:**
- Parses 10 resource types (file, chat, mark, crystal, trace, evidence, constitutional, witness, node, turn)
- Fragment support (`#turn-5`, `#mark-xyz`)
- Implicit `file:` prefix for paths without type
- Roundtrip guarantee: `render(parse(uri)) ≡ uri`

### 2. Resolver Registry (`resolver.py`)

```python
from services.portal import PortalResolverRegistry, FileResolver

registry = PortalResolverRegistry()
registry.register(FileResolver())

# Resolve URIs
resource = await registry.resolve("file:README.md", observer)
print(resource.title)       # "README.md"
print(resource.exists)      # True
print(resource.preview)     # First 200 chars
```

**Features:**
- Protocol-based resolver system
- Type-based dispatch
- Observer-dependent resolution (for access control)
- `ResolvedResource` with metadata, preview, and actions

### 3. File Resolver (`resolvers/file.py`)

```python
from services.portal.resolvers import FileResolver

resolver = FileResolver(base_path=Path.cwd())
resource = await resolver.resolve(uri, observer)
```

**Features:**
- Resolves file paths (absolute or relative)
- Binary file detection
- File metadata (size, modified time)
- Action suggestions (expand, view, edit)

## Architecture

```
services/portal/
├── __init__.py              # Public API
├── uri.py                   # PortalURI parser
├── resolver.py              # Registry and protocol
├── resolvers/
│   ├── __init__.py
│   └── file.py              # FileResolver (Phase 1)
└── _tests/
    ├── test_uri.py          # 32 passing tests
    └── test_registry.py     # 19 passing tests
```

## Laws (from spec §VIII)

1. **URI Parsing Roundtrip:** `render(parse(uri)) ≡ uri` ✅
2. **Resolver Completeness:** Every registered resource type has a resolver ✅
3. **Observer-Dependent Expansion:** Same resource, different observers → different expansions (ready for Phase 3+)

## What's Next (Future Phases)

### Phase 2: Resolver Registry
- ✅ Complete

### Phase 3: Chat Resolvers
- `ChatResolver` - resolve chat sessions
- `MarkResolver` - resolve ChatMarks with constitutional scores
- `TraceResolver` - resolve PolicyTraces

### Phase 4: Evidence Resolvers
- `EvidenceResolver` - resolve evidence bundles
- `ConstitutionalResolver` - resolve constitutional scores with radar data

### Phase 5: Crystal Resolver
- `CrystalResolver` - resolve memory crystals

### Phase 6: Frontend
- Resource-aware `PortalToken` component
- Type-specific renderers (chat, mark, trace, etc.)

### Phase 7: Typeahead
- Resource type selection
- Resource-specific search

## Usage

### Basic URI Parsing

```python
from services.portal import PortalURI

# Explicit types
uri = PortalURI.parse("chat:session-abc123#turn-5")
print(uri.resource_type)  # "chat"
print(uri.resource_path)  # "session-abc123"
print(uri.fragment)       # "turn-5"

# Implicit file: prefix
uri = PortalURI.parse("spec/protocols/witness.md")
print(uri.resource_type)  # "file"
```

### Registry and Resolution

```python
from services.portal import PortalResolverRegistry, FileResolver

# Setup
registry = PortalResolverRegistry()
registry.register(FileResolver())

# Resolve
resource = await registry.resolve("file:README.md", observer=None)

# Access metadata
print(f"Title: {resource.title}")
print(f"Exists: {resource.exists}")
print(f"Preview: {resource.preview}")
print(f"Actions: {resource.actions}")
print(f"Content: {resource.content}")
```

### Custom Resolvers

```python
from services.portal import PortalResolver, ResolvedResource, PortalURI

class MyResolver:
    @property
    def resource_type(self) -> str:
        return "mytype"

    def can_resolve(self, uri: PortalURI) -> bool:
        return uri.resource_type == "mytype"

    async def resolve(self, uri: PortalURI, observer: Any) -> ResolvedResource:
        return ResolvedResource(
            uri=uri.render(),
            resource_type="mytype",
            exists=True,
            title="My Resource",
            preview="Preview text...",
            content={"data": "..."},
            actions=["expand", "view"],
            metadata={"custom": "metadata"},
        )

# Register it
registry.register(MyResolver())
```

## Testing

```bash
# Run all tests
pytest services/portal/_tests/ -v

# Run specific test file
pytest services/portal/_tests/test_uri.py -v
pytest services/portal/_tests/test_registry.py -v

# Type check
mypy services/portal/
```

## Design Principles

1. **Tasteful** - Limited resource types (10), each justified
2. **Curated** - Quality over quantity
3. **Composable** - Resolvers compose; URIs compose
4. **Heterarchical** - Any resource can reference any other
5. **Generative** - This spec generates the implementation

## Connection to Metaphysical Fullstack

Portal Resources integrate with the Metaphysical Fullstack pattern (AD-009):

- **Layer 0 (Persistence):** Resources stored via D-gent/StorageProvider
- **Layer 5 (AGENTESE Node):** `self.portal.resolve` node (Phase 9+)
- **Layer 7 (Projection):** Resource-aware PortalToken in web UI (Phase 6)

---

**Philosophy:**
> *"The portal is the universal reference. The resource comes to you."*
> *"You don't navigate to the resource. The resource comes to you."*

**Filed:** 2025-12-25
**Status:** Phase 1 Complete (Core Infrastructure)
