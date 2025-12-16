# Agent Prompt: Gestalt Elastic Synthesis

> *"The same structure appears everywhere because it IS everywhere. Find it once, use it forever."*

## Mission

You are a **Synthesis Agent** tasked with studying the Gestalt Elastic Edition refactor and extracting the deep principles into reusable artifacts. This is not mere documentation—it is **crystallization of categorical wisdom** into the kgents knowledge base.

## Context Files to Study

Read these files carefully before synthesizing:

### Primary Sources (The Work)
```
impl/claude/web/src/pages/Gestalt.tsx           # The refactored component
impl/claude/web/src/components/elastic/*.tsx    # ElasticSplit, ElasticContainer, ElasticCard, ElasticPlaceholder
impl/claude/web/src/hooks/useLayoutContext.ts   # Layout measurement and context
plans/web-refactor/elastic-primitives.md        # The elastic primitives plan
plans/core-apps/gestalt-architecture-visualizer.md  # Session 5 notes
```

### Theoretical Foundation (The Why)
```
spec/principles.md                              # Core kgents principles
spec/protocols/agentese.md                      # Observer-dependent perception
spec/protocols/projection.md                    # Multi-target projection protocol
docs/skills/polynomial-agent.md                 # State-dependent behavior
docs/systems-reference.md                       # Built infrastructure inventory
```

### Cross-Reference (The Pattern)
```
impl/claude/web/src/pages/Town.tsx              # Another page using elastic primitives
impl/claude/web/src/pages/Brain.tsx             # Compare non-elastic page
impl/claude/agents/i/reactive/                  # Python reactive substrate (Signal/Computed)
```

---

## The Core Insight to Enshrine

**The Gestalt refactor succeeded because it recognized a SIMPLIFYING ISOMORPHISM:**

```
Screen Density ≅ Observer Umwelt ≅ Projection Target ≅ Content Detail Level
```

This is not coincidence—it's the same categorical structure appearing in different domains:

| Domain | Concept | Isomorphic To |
|--------|---------|---------------|
| **AGENTESE** | Observer-dependent perception | Density-aware rendering |
| **Projection Protocol** | CLI/Web/marimo targets | Mobile/Tablet/Desktop modes |
| **Polynomial Agents** | State-dependent input types | Layout-dependent content |
| **Sheaf Theory** | Local-to-global consistency | Component-to-page coherence |

**The algorithm**: When you find yourself writing `if (screenSize === 'mobile')` multiple times, you've discovered an isomorphism. Extract it once, apply it everywhere.

---

## Deliverables

### 1. New Skill: `docs/skills/elastic-ui-patterns.md`

Create a skill document covering:

#### A. The Density-Content Isomorphism
```typescript
// BAD: Ad-hoc responsive logic scattered everywhere
{isMobile ? <CompactView /> : <FullView />}

// GOOD: Density is a first-class concept
const { density } = useWindowLayout();
<ContentView density={density} />  // Component decides what density means
```

#### B. The Three-Mode Pattern
Document the pattern that emerged:
- **Compact** (mobile): Drawer-based, touch-friendly, minimal chrome
- **Comfortable** (tablet): Hybrid, collapsible panels, balanced
- **Spacious** (desktop): Full panels, draggable dividers, maximum information

#### C. Density-Aware Constants
```typescript
const NODE_SIZE = { compact: 0.2, comfortable: 0.25, spacious: 0.3 };
const LABEL_FONT = { compact: 0.14, comfortable: 0.18, spacious: 0.22 };
const MAX_ITEMS = { compact: 15, comfortable: 30, spacious: 50 };
```

#### D. The Smart Defaults Principle
- Fewer items on smaller screens (performance)
- Labels/chrome off by default on mobile
- Touch-friendly tap targets (48px minimum)
- Auto-open relevant drawers on action

#### E. Component Composition Patterns
- `FloatingActions` for mobile action buttons
- `BottomDrawer` for slide-up panels
- `ElasticSplit` for responsive pane layouts
- How they compose together

### 2. Spec Update: `spec/protocols/projection.md`

Add a section on **Density as Projection Dimension**:

```markdown
## Density Projection

The Projection Protocol extends beyond target (CLI/Web/marimo) to include
DENSITY as an orthogonal dimension:

| Target | Density | Projection |
|--------|---------|------------|
| CLI | compact | Single-line summaries, sparklines |
| CLI | spacious | Full tables, verbose output |
| Web | compact | Drawer panels, floating actions |
| Web | comfortable | Collapsible panels, hybrid layout |
| Web | spacious | Full sidebars, draggable dividers |
| marimo | compact | Collapsed cells, summary widgets |
| marimo | spacious | Expanded cells, full visualizations |

The widget's `layout` field provides hints, but the projection target
makes the final density decision based on available space.
```

### 3. Spec Update: `spec/principles.md`

Add a new Architectural Decision:

```markdown
## AD-XXX: Simplifying Isomorphisms

**Context**: UI code often contains repetitive conditional logic based on
screen size, user role, feature flags, or other dimensions.

**Decision**: When the same conditional pattern appears 3+ times, it reveals
a SIMPLIFYING ISOMORPHISM—a categorical equivalence that should be extracted
and applied uniformly.

**Pattern**:
1. IDENTIFY: Notice repeated `if/switch` on the same dimension
2. EXTRACT: Create a first-class representation of that dimension
3. PARAMETERIZE: Pass the dimension as context to components
4. DELEGATE: Let components decide what the dimension means for them

**Examples**:
- Screen density → `useWindowLayout().density`
- Observer type → AGENTESE umwelt
- Projection target → Projection Protocol adapters
- Feature tier → Licensing context

**Consequence**: Code becomes declarative ("render at this density") rather
than imperative ("if mobile, do X, else do Y"). The isomorphism is named,
documented, and consistently applied.

**Anti-pattern**: Scattering `isMobile` checks throughout components instead
of passing density context and letting components adapt.
```

### 4. New Skill: `docs/skills/ui-isomorphism-detection.md`

A meta-skill for FINDING these isomorphisms:

#### Signs You've Found One
1. **Repeated conditionals**: Same `if` condition in 3+ places
2. **Parallel structures**: Similar code for different cases (mobile/desktop)
3. **Configuration explosion**: Too many boolean props (`isMobile`, `isCompact`, `showLabels`)
4. **Cross-cutting concerns**: Same logic needed at multiple component levels

#### Extraction Algorithm
```
1. Name the dimension (density, role, tier, mode)
2. Define the possible values (compact/comfortable/spacious)
3. Create a context/hook to provide it (useWindowLayout)
4. Define constants parameterized by it (NODE_SIZE[density])
5. Update components to receive and use it
6. Remove all ad-hoc conditionals
```

#### Validation Checklist
- [ ] Dimension has a clear name
- [ ] Values are exhaustive and mutually exclusive
- [ ] Context is provided at appropriate level
- [ ] Components adapt internally, not externally
- [ ] No remaining ad-hoc conditionals for this dimension

### 5. Update: `docs/systems-reference.md`

Add Elastic UI to the systems inventory:

```markdown
## Elastic UI Primitives

| Component | Purpose | Key Props |
|-----------|---------|-----------|
| `ElasticSplit` | Two-pane responsive layout | direction, defaultRatio, collapseAt, resizable |
| `ElasticContainer` | Self-arranging container | layout, gap, padding, transition |
| `ElasticCard` | Priority-aware card | priority, minContent, shrinkBehavior |
| `ElasticPlaceholder` | Loading/empty/error states | for, state, expectedSize |
| `useWindowLayout` | Window-level layout info | width, height, density, isMobile, isTablet, isDesktop |
| `useLayoutMeasure` | Container-level measurement | Returns [ref, context] |

**Key Insight**: These primitives embody the Density-Content Isomorphism.
Pass density down, let components decide what it means.
```

---

## The Deeper Pattern to Document

### The UI/App Building Algorithm

Synthesize a general algorithm for building kgents UIs:

```
1. IDENTIFY THE DIMENSIONS
   - What varies? (screen size, user role, data state, feature tier)
   - Name each dimension explicitly

2. DEFINE THE PROJECTION SPACE
   - What are the valid combinations?
   - Which combinations are isomorphic? (mobile+viewer ≅ compact)

3. BUILD ATOMIC PRIMITIVES
   - Components that accept dimension values
   - Internal adaptation, not external conditionals

4. COMPOSE WITH ELASTIC CONTAINERS
   - ElasticSplit for pane layouts
   - ElasticContainer for collections
   - BottomDrawer for mobile panels

5. PROVIDE CONTEXT AT THE RIGHT LEVEL
   - Window-level: useWindowLayout (density, breakpoints)
   - Page-level: page-specific state (selected item, panel visibility)
   - Component-level: useLayoutMeasure (container size)

6. SMART DEFAULTS BY DENSITY
   - Compact: minimal, touch-friendly, progressive disclosure
   - Comfortable: balanced, collapsible, moderate chrome
   - Spacious: full information, draggable, persistent panels

7. VALIDATE THE ISOMORPHISMS
   - Does mobile behave like "compact web"?
   - Does CLI compact behave like "mobile without visuals"?
   - Can you describe behavior without mentioning screen size?
```

### The Categorical Stack

Document how the categorical foundations apply to UI:

| Category Concept | UI Application |
|------------------|----------------|
| **Functor** | Layout strategy: `data → rendered elements` |
| **Natural Transformation** | Responsive adaptation: `desktop layout → mobile layout` |
| **Isomorphism** | Density equivalence: `mobile ≅ compact ≅ minimal content` |
| **Sheaf** | Local components glue to global page layout |
| **Polynomial** | State-dependent UI: `mode → available interactions` |

---

## Output Format

For each deliverable, use the existing format in kgents:

### Skills (`docs/skills/*.md`)
```markdown
# Skill Name

> *"Pithy quote capturing the essence"*

## When to Use

[Trigger conditions]

## The Pattern

[Core pattern with code examples]

## Examples

[Concrete examples from kgents]

## Anti-Patterns

[What NOT to do]

## Related

[Links to related skills/docs]
```

### Spec Updates (`spec/*.md`)
Use the existing AD (Architectural Decision) format for principles.md.
Use existing section formats for protocol docs.

---

## Success Criteria

Your synthesis is complete when:

1. **A new developer** reading `docs/skills/elastic-ui-patterns.md` can build a responsive page without asking questions
2. **The isomorphism** between AGENTESE observer-dependent perception and density-aware rendering is EXPLICIT in spec/
3. **The algorithm** for finding and extracting isomorphisms is documented as a repeatable process
4. **systems-reference.md** accurately reflects the elastic primitives as production infrastructure
5. **No knowledge is lost**—everything learned in Gestalt is crystallized for future use

---

## Final Reflection Prompt

After completing the synthesis, append to `plans/meta.md`:

```markdown
## Gestalt Elastic Synthesis (YYYY-MM-DD)

- [One-line insight about density-content isomorphism]
- [One-line insight about UI building algorithm]
- [One-line insight about categorical stack for UI]
```

---

*"The projection is not the territory. But understanding the isomorphism between projections reveals the territory's true shape."*
