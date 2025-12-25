# Frontend Flow Overhaul (Greenfield)

Goal: Radically re-architect the entire frontend flow around a single coherent loop, derived from registry truth and the Zero Seed graph. No backwards compatibility.

This is a conceptual and structural redesign. Visual design choices are deferred to the taste interview.

---

## 1) Product spine: the core loop

Primary loop (single mental model):

1. Grounding (Dawn)
2. Explore (Habitat)
3. Shape (Graph + K-Block)
4. Execute (Ops)
5. Verify (Proof + Evidence)
6. Reflect (Synthesis)

Every screen must be a phase in this loop. No dead ends.

---

## 2) Primary surfaces (new global IA)

All navigation is derived from AGENTESE registry. There is no static nav tree.

1. Dawn
- Entry ritual and today context
- Pulls from NOW.md, plans/, current K-blocks, and current livelihood score

2. Habitat
- Universal path explorer with guaranteed minimal projection
- Every node has a habitat panel

3. Graph Studio
- Hypergraph editor as primary workspace
- Edges and hyperedges are first-class and editable

4. K-Block Editor
- The default editing surface for all documents
- Shows provenance, witness marks, and evidence

5. Proof Theater
- Live proof obligations, statuses, contradictions, and disputes
- The home of composability law checks

6. Livelihood Intelligence
- A living view of scores, trajectories, and causality documents

7. Atlas
- A panoramic ontology map derived from the Zero Seed hierarchy

---

## 3) Zero Seed as the startup state

On first launch, the system opens at the Zero Seed Atlas, not a dashboard. The user sees the minimal seed graph and can edit it immediately.

Default first-run flow:

- Step 1: Dawn ritual (read 5 lines, see intent)
- Step 2: Zero Seed Atlas (edit the hierarchy)
- Step 3: Habitat (open a node; minimal habitat already exists)

---

## 4) Global interaction model

- Cursor-driven: everything is a node, every node has a path
- Graph-first: documents are just another projection
- Multi-view: Graph on left, Habitat or K-Block on right
- Temporal threading: history, diffs, and evidence are always one click away

Interaction rules:
- No dead end: every view links back to its node in the graph
- No hidden registry: all paths are discoverable and navigable
- No blank pages: habitat guarantee enforced
- No orphan data: each artifact must attach to a node or edge

---

## 5) Experience loop per surface

Dawn
- Purpose: orient and choose your next node
- Primary actions: open, pin, witness, set intention

Habitat
- Purpose: understand any node with minimal friction
- Primary actions: explore, invoke, edit, annotate

Graph Studio
- Purpose: rewire the system
- Primary actions: add node, add edge, reroute, dispute

K-Block
- Purpose: edit the reality
- Primary actions: write, comment, witness, crystallize

Proof Theater
- Purpose: verify and surface contradictions
- Primary actions: run proofs, inspect failures, add evidence

Livelihood
- Purpose: track and edit intelligence
- Primary actions: dispute causality, track trends, crystallize

Atlas
- Purpose: show the system as a coherent whole
- Primary actions: zoom, filter by hierarchy, jump to habitat

---

## 6) Core UI components (greenfield)

- NodeRibbon: compact node header with path, type, and status
- EdgeInspector: shows incoming/outgoing morphisms with tags
- HyperEdgeComposer: add multi-source edges visually
- EvidenceStrata: stacks evidence layers for a node or edge
- HabitatPanel: minimal, standard, rich projection in one component
- ProofTicker: proofs and contradictions stream in real time
- LivelihoodBadge: always-on current score
- DisputeMarker: explicit user override with reason

---

## 7) Data and state model (frontend)

- Registry is the single source of truth for all paths
- View functors are pure projections (no logic forks)
- All edits are events that create witness marks
- All surfaces reflect graph state in real time

View flow:

Registry -> Node -> Projection (Habitat / K-Block / Graph / Proof / Livelihood)

---

## 8) System coherence and principle alignment

- Tasteful: the flow only includes surfaces with strong purpose
- Curated: avoid a list of endless tabs, only core surfaces
- Ethical: explicit provenance, disputes are visible
- Joy-inducing: discovery is a first-class action
- Composable: everything is a morphism and can be reused
- Heterarchical: no fixed top-down flow, the user can jump
- Generative: the registry and seed specs generate the UI

---

## 9) Suggested design directions (awaiting taste interview)

Direction A: Monastic Lab
- Visual: quiet, neutral background, highly structured grid
- Typography: Fraunces (serif) + Space Grotesk (sans)
- Mood: clarity, precision, ritual

Direction B: Cathedral of Graph
- Visual: high-contrast architectural geometry, visible axes
- Typography: Spectral (serif) + IBM Plex Sans
- Mood: awe, structural depth, cathedral of knowledge

Direction C: Field Research
- Visual: textured layers, handwritten annotations, material overlays
- Typography: Barlow Condensed + Newsreader
- Mood: exploratory, alive, tactile

---

## 10) Migration stance

We do not preserve any existing flow or component. Every screen is rebuilt around the registry truth and Zero Seed. The only continuity is conceptual: paths, nodes, and proofs.

---

## 11) Open decisions (for Kent)

- Which surface should be the default landing view after Dawn?
- Should Graph Studio be full screen by default or always paired with Habitat?
- How aggressive should motion be in Graph Studio (none, moderate, or expressive)?
- How visible should proof failures be (always on, or only in Proof Theater)?

