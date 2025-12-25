# K-Block Components

Unified editing components for all K-Block types: file-based content, Zero Seed epistemic graph nodes, and dialogue K-Blocks.

## Philosophy

> "The K-Block is not where you edit a document.
>  It's where you edit a possible world."

All K-Block types share the same isolation semantics:
- **PRISTINE**: No changes yet (quantum superposition)
- **DIRTY**: Changes in progress (partial collapse)
- **STALE**: External changes detected (decoherence)

## Components

### UnifiedKBlockEditor

The main editor component that works for all K-Block types.

**Features**:
- Automatic type detection (File / Zero Seed / Dialogue)
- Isolation state indicator
- Derivation chain navigation (for Zero Seed nodes)
- Collapsible Toulmin proof panel
- Witness reasoning input
- Save/Discard controls

**Usage**:

```typescript
import { useKBlock } from '../../hypergraph/useKBlock';
import { UnifiedKBlockEditor } from '../kblock';

function MyEditor() {
  const kblock = useKBlock();

  // File K-Block
  const handleOpenFile = async () => {
    await kblock.create('/path/to/file.md');
  };

  // Zero Seed K-Block
  const handleCreateNode = async () => {
    await kblock.createZeroSeed(
      1,                          // Layer (1-7)
      'axiom',                    // Kind
      'All agents are morphisms', // Content
      []                          // Lineage (parent IDs)
    );
  };

  if (!kblock.state) {
    return <div>No K-Block active</div>;
  }

  return (
    <UnifiedKBlockEditor
      state={kblock.state}
      onContentChange={kblock.updateContent}
      onSave={kblock.save}
      onDiscard={kblock.discard}
      onProofUpdate={kblock.setProof}
      onNavigateToParent={kblock.goToParent}
      onNavigateToChild={kblock.goToChild}
    />
  );
}
```

## Hook: useKBlock

The unified hook for managing K-Block lifecycle.

### File K-Blocks

```typescript
const kblock = useKBlock();

// Create for file
const result = await kblock.create('/path/to/file.md');

// Edit content
kblock.updateContent('New content...');

// Save with reasoning
await kblock.save('Updated documentation');

// Discard changes
await kblock.discard();
```

### Zero Seed K-Blocks

```typescript
const kblock = useKBlock();

// Create epistemic graph node
const result = await kblock.createZeroSeed(
  2,            // Layer 2 (Values)
  'value',      // Kind
  'Joy-inducing agents are better than functional agents',
  ['axiom-123'] // Derives from axiom
);

// Add proof
await kblock.setProof({
  claim: 'Joy-inducing agents are better',
  data: 'User feedback shows 80% preference',
  warrant: 'User experience drives adoption',
  backing: 'Nielsen Norman Group research',
  qualifier: 'Empirical',
  rebuttals: ['What about critical systems?'],
  tier: 'empirical',
  principles: ['joy-inducing', 'ethical'],
});

// Add derivation link
await kblock.addDerivation('parent-block-id');

// Navigate to parent
kblock.goToParent(0);
```

### Dialogue K-Blocks

```typescript
const kblock = useKBlock({
  sessionId: 'my-session',
  autoCreate: true,
});

// Append thoughts
await kblock.appendThought('User thought...', 'user');
await kblock.appendThought('Assistant response...', 'assistant');

// Crystallize (save)
await kblock.save('Completed conversation about X');
```

## State Fields

### Common Fields (All Types)

```typescript
blockId: string;           // K-Block ID
path: string | null;       // File path (null for non-file)
content: string;           // Current content
baseContent: string;       // Original content
isolation: IsolationState; // PRISTINE | DIRTY | STALE
isDirty: boolean;          // Has unsaved changes
```

### Zero Seed Fields

```typescript
zeroSeedLayer?: 1 | 2 | 3 | 4 | 5 | 6 | 7;  // Layer
zeroSeedKind?: string;                       // Kind (axiom, value, etc.)
lineage: string[];                           // Conceptual parents
hasProof: boolean;                           // Has Toulmin proof
toulminProof?: ToulminProof;                 // Proof structure
confidence: number;                          // 0-1 score
parentBlocks: string[];                      // Structural parents
childBlocks: string[];                       // Structural children
```

### File K-Block Fields

```typescript
activeViews: KBlockViewType[];  // Active view types
checkpoints: Checkpoint[];      // Named checkpoints
analysisStatus?: string;        // Sovereign analysis status
isReadOnly?: boolean;           // Read-only flag
```

### Dialogue K-Block Fields

```typescript
sessionId?: string;    // Session ID
contentLength: number; // Message count
```

## Methods

### Core Methods (All Types)

- `create(path)` - Create file K-Block
- `updateContent(content)` - Update content locally
- `save(reasoning?)` - Save/crystallize with optional reasoning
- `discard()` - Discard changes
- `reset()` - Reset hook state

### Zero Seed Methods

- `createZeroSeed(layer, kind, content, lineage)` - Create Zero Seed node
- `addDerivation(parentId)` - Add derivation link
- `removeDerivation(parentId)` - Remove derivation link
- `setProof(proof)` - Attach Toulmin proof
- `goToParent(index)` - Navigate to parent (callback)
- `goToChild(index)` - Navigate to child (callback)

### File K-Block Methods

- `viewEdit(view, content, reasoning?)` - Edit via specific view
- `refresh()` - Refresh from backend
- `checkpoint(name)` - Create named checkpoint
- `rewind(checkpointId)` - Restore checkpoint
- `getReferences()` - Get file references

### Dialogue K-Block Methods

- `appendThought(content, role?)` - Append to dialogue

## Toulmin Proof Structure

```typescript
interface ToulminProof {
  claim: string;           // What you're asserting
  data: string;            // Evidence supporting claim
  warrant: string;         // Why data supports claim
  backing: string;         // Foundation for warrant
  qualifier: string;       // Certainty level
  rebuttals: string[];     // Counter-arguments
  tier: 'categorical' | 'empirical' | 'aesthetic' | 'somatic';
  principles: string[];    // kgents principles applied
}
```

### Evidence Tiers

- **Categorical**: Logical/mathematical proof (confidence: 1.0)
- **Empirical**: Data-driven evidence (confidence: 0.9)
- **Aesthetic**: Design/UX principles (confidence: 0.7)
- **Somatic**: Embodied/intuitive knowledge (confidence: 0.6)

## Derivation vs Lineage

- **Lineage**: Conceptual/historical (which ideas led to this?)
- **Parent Blocks**: Structural (which K-Blocks does this depend on?)

Both are tracked, but serve different purposes:
- Lineage: For provenance and citation
- Parent Blocks: For navigation and dependency tracking

## Styling

Component uses CSS custom properties for theming:

```css
--bg-primary
--bg-secondary
--border-color
--text-primary
```

Type-specific colors are hardcoded for consistency:
- Zero Seed: Blue (#e3f2fd, #1976d2)
- File: Purple (#f3e5f5, #7b1fa2)
- Dialogue: Green (#e8f5e9, #388e3c)

## Examples

### Example 1: Axiom Editor

```typescript
function AxiomEditor() {
  const kblock = useKBlock();

  const handleCreate = async () => {
    const result = await kblock.createZeroSeed(
      1,
      'axiom',
      'The agent is the unit of composition',
      []
    );

    if (result.success) {
      await kblock.setProof({
        claim: 'Agents are compositional units',
        data: 'Category theory defines composition of morphisms',
        warrant: 'Agents are morphisms in AGENTESE operad',
        backing: 'Mac Lane, Categories for the Working Mathematician',
        qualifier: 'Categorical proof',
        rebuttals: [],
        tier: 'categorical',
        principles: ['composable'],
      });
    }
  };

  return kblock.state ? (
    <UnifiedKBlockEditor
      state={kblock.state}
      onContentChange={kblock.updateContent}
      onSave={kblock.save}
      onDiscard={kblock.discard}
      onProofUpdate={kblock.setProof}
    />
  ) : (
    <button onClick={handleCreate}>Create Axiom</button>
  );
}
```

### Example 2: Spec Editor with Proof

```typescript
function SpecEditor({ specPath }: { specPath: string }) {
  const kblock = useKBlock();

  React.useEffect(() => {
    kblock.create(specPath);
  }, [specPath]);

  const handleAttachProof = async () => {
    await kblock.setProof({
      claim: 'This spec implements the design correctly',
      data: 'All tests pass, coverage 95%',
      warrant: 'Test coverage correlates with correctness',
      backing: 'TDD best practices (Beck)',
      qualifier: 'Empirical validation',
      rebuttals: ['Tests could have gaps'],
      tier: 'empirical',
      principles: ['tasteful', 'composable'],
    });
  };

  if (!kblock.state) return <div>Loading...</div>;

  return (
    <>
      <UnifiedKBlockEditor
        state={kblock.state}
        onContentChange={kblock.updateContent}
        onSave={kblock.save}
        onDiscard={kblock.discard}
      />
      {!kblock.state.hasProof && (
        <button onClick={handleAttachProof}>
          Attach Proof
        </button>
      )}
    </>
  );
}
```

## Backend Integration

The component expects these backend endpoints:

```
POST /api/kblock/zero-seed
  → { block_id, path, parent_blocks, child_blocks }

POST /api/kblock/{id}/derivations
  → { success }

DELETE /api/kblock/{id}/derivations/{parent_id}
  → { success }

PUT /api/kblock/{id}/proof
  → { success, confidence }
```

See `/Users/kentgang/git/kgents/PHASE3_KBLOCK_UNIFICATION.md` for full backend specification.

---

*Last Updated: 2025-12-24*
*Phase 3: K-Block/Document Unification*
