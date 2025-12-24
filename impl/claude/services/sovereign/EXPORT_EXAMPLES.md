# Law 3: Witnessed Export Examples

This document demonstrates how to use the Law 3 witnessed export functionality added to SovereignStore.

## Overview

Law 3 guarantees that every export operation has a witness mark:

```
∀ export operation o on entity e:
  ∃ mark m such that m.action = "sovereign.export" ∧ m.entity_path = e.path
```

## Three Ways to Export

### 1. witnessed_export() - Recommended (Complete Law 3 Pattern)

The `witnessed_export()` method handles everything:
- Creates witness mark BEFORE gathering content
- Gathers entities with provenance
- Returns ExportBundle with mark_id

```python
from services.sovereign.store import SovereignStore
from services.witness.persistence import WitnessPersistence

# Setup
store = SovereignStore()
witness = WitnessPersistence(session_factory, dgent)

# Export with full Law 3 compliance
bundle = await store.witnessed_export(
    paths=["spec/protocols/k-block.md", "spec/protocols/sovereign.md"],
    witness=witness,
    author="kent",
    reasoning="Archiving Crown Jewel specifications for Q4 2025",
    format="json",
)

# Bundle includes:
# - export_mark_id: The witness mark
# - entities: List of ExportedEntity with content, hash, provenance
# - exported_at: Timestamp
# - entity_count: Number of entities

print(f"Exported {bundle.entity_count} entities")
print(f"Export mark: {bundle.export_mark_id}")

# Convert to JSON for serialization
bundle_dict = bundle.to_dict()
import json
json_output = json.dumps(bundle_dict, indent=2)
```

### 2. export_entity() / export_bundle() with Witness (Manual Pattern)

If you need to create the mark yourself (for custom reasoning or tags):

```python
# Create export mark FIRST (Law 3)
mark_result = await witness.save_mark(
    action="sovereign.export: spec/protocols/k-block.md",
    reasoning="Emergency backup before refactor",
    principles=["ethical"],
    tags=["export", "backup", "emergency"],
    author="kent",
)

# Then export with mark_id
export_data = await store.export_entity(
    "spec/protocols/k-block.md",
    include_overlay=True,
    include_history=True,
    witness=witness,
    export_mark_id=mark_result.mark_id,
)

# export_data includes:
# - path, content (base64), content_hash, metadata
# - overlay (annotations, edges, analysis)
# - versions (if include_history=True)
# - export_mark_id
```

Or for multiple entities:

```python
# Create mark
mark_result = await witness.save_mark(
    action="sovereign.export: 5 entities",
    reasoning="Weekly backup",
    tags=["export", "backup", "weekly"],
)

# Export bundle
bundle_bytes = await store.export_bundle(
    paths=["spec/a.md", "spec/b.md", "spec/c.md"],
    format="json",  # or "zip"
    witness=witness,
    export_mark_id=mark_result.mark_id,
)

# For JSON format:
import json
bundle = json.loads(bundle_bytes.decode("utf-8"))
print(bundle["export_mark_id"])

# For ZIP format, manifest.json contains export_mark_id
```

### 3. export_entity() / export_bundle() WITHOUT Witness (Legacy)

For backward compatibility, you can still export without witness:

```python
# No witness, no mark - backward compatible
export_data = await store.export_entity("spec/test.md")

# Works, but DOES NOT satisfy Law 3
# Use only when witness is unavailable
```

## Law 3 Enforcement

If you provide `witness` parameter but forget `export_mark_id`, you get an error:

```python
# This FAILS with ValueError
try:
    await store.export_entity(
        "spec/test.md",
        witness=witness,
        export_mark_id=None,  # ❌ Missing mark_id!
    )
except ValueError as e:
    print(e)  # "Law 3: witness provided but no export_mark_id. Create mark first!"
```

This enforces that marks are created BEFORE export, preserving causal order.

## Verification Protocol

To verify Law 3 compliance:

```python
# 1. Export creates mark BEFORE gathering content
bundle = await store.witnessed_export(paths=["spec/test.md"], witness=witness)

# 2. Mark exists and has correct action
mark = await witness.get_mark(bundle.export_mark_id)
assert "sovereign.export" in mark.action

# 3. Bundle includes mark_id
assert bundle.export_mark_id is not None

# 4. Entities have content hashes for integrity verification
for entity in bundle.entities:
    import hashlib
    computed_hash = hashlib.sha256(entity.content).hexdigest()
    assert computed_hash == entity.content_hash  # Theorem 1: Integrity
```

## Integration with AGENTESE

Export can be exposed via AGENTESE:

```python
# Example AGENTESE node for export
@node("world.sovereign.export")
class SovereignExportNode:
    def __init__(self, store: SovereignStore, witness: WitnessPersistence):
        self.store = store
        self.witness = witness

    async def invoke(
        self,
        paths: list[str],
        observer: Observer,
        author: str = "kent",
        reasoning: str | None = None,
    ) -> ExportBundle:
        """Export entities with Law 3 compliance."""
        bundle = await self.store.witnessed_export(
            paths=paths,
            witness=self.witness,
            author=author,
            reasoning=reasoning,
        )

        # Emit progress via observer
        await observer.emit_progress(f"Exported {bundle.entity_count} entities")
        await observer.emit_mark(bundle.export_mark_id)

        return bundle
```

## Best Practices

1. **Always use `witnessed_export()` when witness is available** - it's the complete pattern
2. **Create marks BEFORE export** - preserves causal order (Law 3)
3. **Include reasoning** - helps future you understand why export happened
4. **Use ethical principle** - data leaving our control requires ethical tag
5. **Verify content hashes** - Theorem 1 integrity guarantee

## See Also

- `spec/protocols/sovereign-data-guarantees.md` - Formal specification
- `services/sovereign/_tests/test_law3_witnessed_export.py` - Comprehensive tests
- `services/witness/persistence.py` - WitnessPersistence interface
