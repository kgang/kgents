# Mothballed Components

> _"3D was spectacle. 2D is truth."_

**Mothballed:** 2025-12-18
**Reason:** 2D Renaissance (see `spec/protocols/2d-renaissance.md`)

---

## What's Here

Three.js visualization components that were impressive demos but hollow experiences. They didn't invoke AGENTESE, didn't call LLMs, didn't generate real user journeys.

```
three-visualizers/
├── gestalt/
│   ├── GestaltVisualization.tsx  (1060 lines)
│   ├── OrganicNode.tsx
│   ├── VineEdge.tsx
│   └── AnimatedEdge.tsx
├── brain/
│   ├── BrainCanvas.tsx           (1004 lines)
│   ├── OrganicCrystal.tsx
│   └── CrystalVine.tsx
└── town/
    └── TownCanvas3D.tsx          (383 lines)
```

---

## Why Mothballed

| Component            | Problem                                              |
| -------------------- | ---------------------------------------------------- |
| GestaltVisualization | 1060 lines of 3D complexity for a health dashboard   |
| BrainCanvas          | 1004 lines, WebGL dependency, no LLM integration     |
| TownCanvas3D         | 383 lines of pretty spheres with hardcoded positions |

These are **museums**—static exhibits that look nice but don't breathe.

---

## What Replaced Them

The 2D primitives in `gallery/{projection, layout}` are generative:

- **Mesa** (PixiJS) for 2D canvas rendering
- **ElasticSplit** + **BottomDrawer** for responsive layout
- Density-parameterized constants for mobile-first design

Each Crown Jewel now gets a `*2D.tsx` component that:

1. Uses real AGENTESE data flows
2. Integrates LLM-backed interactions
3. Responds to density changes gracefully
4. Actually breathes (Living Earth aesthetic)

---

## Revival Conditions

May revive these components for:

1. **VR/AR projections** — If we build spatial computing support
2. **3D-specific requirements** — If a visualization genuinely needs depth
3. **Performance comparison** — To benchmark 2D vs 3D

**To revive:** Move back to original directory, re-export from index.ts, update imports.

---

## What's Preserved Elsewhere

The 3D infrastructure remains available:

| Location                       | Purpose                                    |
| ------------------------------ | ------------------------------------------ |
| `components/three/`            | Reusable primitives (TopologyNode3D, etc.) |
| `components/three/primitives/` | Low-level 3D building blocks               |
| `utils/three/`                 | Shadow bounds, layout math                 |
| `docs/skills/`                 | 3D skills documentation                    |

These are skills and tools—always useful. The mothballed components are _products_—specific visualizations that weren't earning their complexity.

---

_"The garden tends itself, but only because we planted it together."_
