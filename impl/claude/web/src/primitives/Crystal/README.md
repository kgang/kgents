# Crystal Primitives

**Memory Compression Visualization Components**

The Crystal primitives visualize crystallized witness memory—compressed insights that emerge from session marks.

## Philosophy

> "Marks are observations. Crystals are insights."

Experience Crystallization transforms ephemeral events into durable, navigable memory. A crystal is not a summary—it's a semantic compression that preserves causal structure while reducing volume.

## Components

### MoodIndicator

Displays a 7-dimensional affective signature (MoodVector) as a compact visual.

**Dimensions:**
- Warmth: Cold/clinical ↔ Warm/engaging
- Weight: Light/playful ↔ Heavy/serious
- Tempo: Slow/deliberate ↔ Fast/urgent
- Texture: Smooth/flowing ↔ Rough/struggling
- Brightness: Dim/frustrated ↔ Bright/joyful
- Saturation: Muted/routine ↔ Vivid/intense
- Complexity: Simple/focused ↔ Complex/branching

**Usage:**
```tsx
import { MoodIndicator } from '@/primitives/Crystal';

<MoodIndicator
  mood={crystal.mood}
  size="medium"
  variant="dots"
/>
```

**Props:**
- `mood: MoodVector` - The 7D mood vector
- `size?: 'small' | 'medium' | 'large'` - Visual size (default: 'medium')
- `variant?: 'dots' | 'bars'` - Display style (default: 'dots')

### CrystalCard

Displays a single crystal with its insight, significance, confidence, mood, and metadata.

**Features:**
- Level badge (SESSION/DAY/WEEK/EPOCH)
- Insight (main content)
- Significance (why it matters)
- Confidence indicator (circular ring)
- Mood visualization
- Source count
- Expandable details (principles, topics, metrics)

**Usage:**
```tsx
import { CrystalCard } from '@/primitives/Crystal';

<CrystalCard
  crystal={crystal}
  onExpand={(c) => console.log('Expanded:', c)}
  expandable={true}
/>
```

**Props:**
- `crystal: Crystal` - The crystal to display
- `onExpand?: (crystal: Crystal) => void` - Callback when expanded
- `expandable?: boolean` - Whether card is expandable (default: true)

### CrystalHierarchy

Displays crystals organized by hierarchical levels: SESSION → DAY → WEEK → EPOCH.

**Features:**
- Collapsible levels
- Timeline or tree view
- Click to expand/drill down
- Empty state handling

**Usage:**
```tsx
import { CrystalHierarchy } from '@/primitives/Crystal';

<CrystalHierarchy
  crystals={allCrystals}
  onCrystalSelect={(c) => console.log('Selected:', c)}
  initialCollapsed={['SESSION']}
  variant="timeline"
/>
```

**Props:**
- `crystals: Crystal[]` - Array of all crystals
- `onCrystalSelect?: (crystal: Crystal) => void` - Callback when crystal is selected
- `initialCollapsed?: CrystalLevel[]` - Levels to start collapsed (default: [])
- `variant?: 'timeline' | 'tree'` - Display style (default: 'timeline')

## Types

See `src/types/crystal.ts` for full TypeScript definitions:

```typescript
export type CrystalLevel = 'SESSION' | 'DAY' | 'WEEK' | 'EPOCH';

export interface MoodVector {
  warmth: number;      // 0-1
  weight: number;      // 0-1
  tempo: number;       // 0-1
  texture: number;     // 0-1
  brightness: number;  // 0-1
  saturation: number;  // 0-1
  complexity: number;  // 0-1
}

export interface Crystal {
  id: string;
  level: CrystalLevel;
  insight: string;
  significance: string;
  mood: MoodVector;
  confidence: number;
  sourceMarkIds: string[];
  sourceCrystalIds: string[];
  principles: string[];
  topics: string[];
  crystallizedAt: string; // ISO 8601
  periodStart?: string;   // ISO 8601
  periodEnd?: string;     // ISO 8601
  sessionId?: string;
  compressionRatio?: number;
}
```

## Backend Integration

### Crystallization Command

From the Hypergraph Editor (NORMAL mode), type `:crystallize` to trigger session crystallization:

```
:crystallize [optional notes]
```

This sends a POST request to `/api/witness/crystallize` and creates a level-0 (SESSION) crystal from current session marks.

### API Endpoints

- `POST /api/witness/crystallize` - Crystallize current session
- `GET /api/witness/crystals` - List crystals (with filters)
- `GET /api/witness/crystals/:id` - Get specific crystal

## Design System

All components follow the **STARK BIOME** aesthetic:
- 90% steel/gray tones
- 10% earned glow (for significant elements)
- Brutalist, clean, no decoration
- Uses design tokens from `design/tokens.css`

**Key Colors:**
- Levels: SESSION (steel-300) → DAY (life-sage) → WEEK (glow-lichen) → EPOCH (glow-amber)
- Confidence: Circular ring with glow-spore fill
- Mood: Steel to glow gradient based on intensity

## Backend Architecture

See backend implementation:
- `services/witness/crystal.py` - Crystal and MoodVector data classes
- `services/witness/crystallizer.py` - LLM-powered crystallization logic
- `services/witness/crystal_store.py` - Crystal persistence

## The Crystal Laws

1. **Mark Immutability**: Marks are never deleted—crystals are a lens, not replacement
2. **Provenance Chain**: Every crystal references its sources (marks or crystals)
3. **Level Consistency**: Level N crystals only source from level N-1 (clean DAG)
4. **Temporal Containment**: Crystal time_range contains all source time_ranges
5. **Compression Monotonicity**: Higher levels are always denser (fewer, broader)

## Example: Full Stack Flow

1. User works in session, creates marks via `:w` command
2. User triggers crystallization: `:crystallize "Completed extinction audit"`
3. Backend:
   - Fetches session marks
   - Invokes K-gent Soul with crystallization prompt
   - Derives MoodVector from marks
   - Creates level-0 Crystal
   - Stores in crystal_store
4. Frontend:
   - Receives Crystal from API
   - Displays success feedback
   - Can show in CrystalHierarchy (if integrated)

## Future Enhancements

Potential additions (not implemented yet):
- CrystallizationModal for pre-crystallization preview
- Crystal search/filter UI
- Mood-based crystal similarity search
- DAY/WEEK/EPOCH crystallization triggers
- Crystal graph visualization

---

**Version**: Stream 4 Complete | **Date**: 2025-12-25
