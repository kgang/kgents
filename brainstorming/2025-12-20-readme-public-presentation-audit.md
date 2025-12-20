# README + Public Presentation Audit (Repo-Wide)

## Request Context
- Request: Deeply audit the entire repo and propose upgrades to the README and public-facing presentation.
- Output format: Brainstorming document with further quality enhancements.

## Sources Reviewed
- `README.md`
- `mkdocs.yml`
- `docs/quickstart.md`
- `docs/architecture-overview.md`
- `docs/systems-reference.md`
- `docs/local-development.md`
- `docs/gallery/README.md`
- `CHANGELOG.md`
- `pyproject.toml`
- `impl/claude/pyproject.toml`
- Repo tree for `docs/` and `impl/claude/`
### External Inspiration (GitHub README patterns)
- https://github.com/fastapi/fastapi
- https://github.com/pydantic/pydantic
- https://github.com/psf/requests

## Executive Summary
The README and public presentation are compelling but internally inconsistent. Several referenced docs are missing, site navigation doesn’t surface key content, and versioning requirements disagree across files. The core narrative is strong (spec-first + AGENTESE + categorical composition), but it lacks a simple “why now / what you can do today” entry point and a stable public docs IA. This reduces trust and slows adoption.

## Findings (Priority Ordered)
1. Broken links to missing docs: `docs/functor-field-guide.md`, `docs/operators-guide.md`, `docs/weekly-summary/index.html`.
2. MkDocs nav points to `docs/gallery/index.md` but only `docs/gallery/README.md` exists.
3. Repo URL mismatch in clone instructions: `kgang` vs `kentgang`.
4. Python version mismatch across README/docs/pyproject files (3.11 vs 3.12).
5. Public docs site does not surface quickstart, architecture, systems reference, or local dev.
6. README “Project Structure” doesn’t reflect current docs layout and makes onboarding harder.

## README Upgrade Proposal (Quality-Enhanced)

### 1) Positioning and Narrative
Add a crisp top-of-file narrative with the following structure:
- 1-line statement: spec-first agent ecosystem + reference runtime.
- 2–3 outcomes: what a developer can accomplish in 10 minutes.
- A short “who this is for” line.

### 2) What You Can Do Today (Concrete Use Cases)
Add a short, bulleted “What you can do today” section with:
- 4–6 concrete actions tied to working commands from `README.md` and `docs/quickstart.md`.
- Example: “Spin up K-gent dialogue”, “Compose agents with functors”, “Inspect archetypes”, “Run the projection gallery”.

### 3) Requirements and Setup (Consistency)
Align minimum Python version across:
- `README.md`
- `docs/local-development.md`
- `pyproject.toml`
- `impl/claude/pyproject.toml`

### 4) Documentation Links (Fix + Simplify)
Replace broken references with living docs:
- Quickstart: `docs/quickstart.md`
- Architecture: `docs/architecture-overview.md`
- Systems: `docs/systems-reference.md`
- Local Dev: `docs/local-development.md`

### 5) Leaner Project Structure
Move the large tree to docs; keep a short “Key directories” list in README:
- `spec/` (source of truth)
- `impl/claude/` (reference implementation)
- `docs/` (guides)
- `plans/` (living roadmap)

### 6) Status and Scope (Expectation Setting)
Add a small “Status & Scope” panel:
- Spec vs implementation boundary
- What is production-ready vs experimental
- How to choose entry points (CLI, docs, spec)

### 7) Trust Signals
Add explicit links:
- `CHANGELOG.md`
- `LICENSE`
- “Contributing” (if present or stub a short section)

## Public Presentation Upgrade Proposal

### 1) Docs Landing Page
Create `docs/index.md` with:
- A 1-screen narrative (what, why, how)
- 3–5 “start here” links
- A short “core concepts” list (AGENTESE, functors, polynomial agents)

### 2) MkDocs Navigation (Expose Core Content)
Update `mkdocs.yml` to include:
- Quickstart
- Architecture Overview
- Systems Reference
- Local Development
- Gallery (point to `docs/gallery/README.md` or add `docs/gallery/index.md`)

### 3) Site Identity
Update `site_name` to “kgents” and include a short tagline.

### 4) Visual Anchor
Add a simple architectural diagram and reference it from README + docs landing.
Low-effort options:
- Mermaid diagram in docs
- PNG exported from a diagram tool

### 5) Public Marketing Layer (Optional)
Add a short “Why spec-first” page in `docs/`:
- Compare spec vs implementation (e.g., CPython analogy)
- Emphasize composability and laws

## Suggested Information Architecture (Docs)
Home
- Quickstart
- Architecture Overview
- Systems Reference
- Local Development
- Gallery
- Principles (spec)
- Specs index (spec entry point)

## Content Enhancements (Copy/UX)
- Reduce jargon on first screen; preserve depth in later sections.
- Add a “Glossary / What is AGENTESE?” mini explainer.
- Use consistent naming: “K-gent” vs “Kgent”.
- Add a “Stable vs Experimental” badge for doc pages where useful.

## Quick Wins (1–2 hours)
- Fix broken doc links in `README.md` and `docs/quickstart.md`.
- Fix mkdocs nav path for Gallery.
- Normalize Python version requirements.
- Standardize repo URL in clone instructions.

## Medium Wins (Half-day)
- Create `docs/index.md` landing page.
- Replace README structure with a more intentional narrative.
- Add diagram to docs and README.

## Longer-Term (1–2 days)
- Add a “spec-first philosophy” page.
- Create a minimal design system for documentation (tone, icons, diagrams).
- Add a public “Roadmap / Status” page linked from README.

## External Inspiration - What To Borrow (And How To Make It Kgents)

### FastAPI: Credibility + Onboarding Velocity
- Pattern: logo + one-line value proposition + high-contrast badges.
- Pattern: clear “Documentation / Source Code” anchors early.
- Pattern: benefits listed in bold verbs.
Kgents adaptation:
- Add a punchy one-line: "Spec-first agent ecosystem with verified composition laws."
- Add two top links: "Docs" and "Quickstart".
- A concise "Why it matters" bullet list: composability, alignment, runtime reality.

### Pydantic: Clarity + Minimal Example
- Pattern: short definition line and a minimal, fully working example.
- Pattern: “Help / Contributing / Security policy” links as trust signals.
Kgents adaptation:
- Keep a single, tiny agent example that executes.
- Add "Contributing" and "Security" placeholders if policy exists.
- Add "Versioning" and "Compatibility" blocks for runtime vs spec.

### Requests: Trust + Social Proof
- Pattern: download stats and dependents to build confidence.
- Pattern: feature list that is skimmable.
Kgents adaptation:
- Add “proven by tests” and “N+ tests” as a short credibility line.
- Use short, skimmable "Capabilities" list with links to spec sections.

## Creative Strategy Enhancements (Tailored to kgents)

### 1) The "Spec-First, Runtime-Real" Hook
Goal: Make the dual nature legible at a glance.
Implementation:
- Add a two-line diagram: "Spec -> Implementation -> CLI".
- Explicit sentence: "The spec is the source of truth; the runtime is proof."

### 2) The "One-Minute Tour"
Goal: Reduce cognitive load on first visit.
Implementation:
- A 4-step table: install, run, compose, govern.
- Each step references a real command (kg).

### 3) The "Aesthetic of Taste"
Goal: Show curated quality without being heavy-handed.
Implementation:
- Add a "Curated Genera" mini-grid (5-7 representative entries).
- Link to the full Alphabet Garden.

### 4) The "Proof of Composability"
Goal: Show categorical laws as real engineering.
Implementation:
- Add a tiny block: "Law verified: (a >> b) >> c == a >> (b >> c)".
- Link to test suite or law docs if available.

### 5) The "Public Storyline"
Goal: Align README and docs with a single narrative.
Implementation:
- Narrative arc: "Why (taste) -> What (spec) -> How (runtime) -> Where (docs)".
- Use consistent section names across README and docs.

## Proposed README Skeleton (Inspired, Not Copying)
1. Title + one-line promise
2. Docs + Quickstart links + badges
3. "What you can do today" (4-6 bullets)
4. 60-second example
5. Core concepts: AGENTESE, Functors, Polynomial Agents
6. Install + Quickstart
7. Key directories (short)
8. Status & Scope
9. Links: Docs, Changelog, License, Contributing

## Proposed Docs Landing Skeleton
1. Hero: "Spec-first agent ecosystem"
2. Start here: Quickstart, Architecture, Systems, Local Dev
3. Core concepts: AGENTESE, Functors, Polynomial
4. Examples: Gallery + 3 flagship demos
5. What's next: Roadmap + Status


## Risks + Mitigations
- Risk: Overwriting deep technical detail with marketing copy.
  - Mitigation: Keep README short; link into deeper docs.
- Risk: Confusion if version requirements differ.
  - Mitigation: Explicitly document runtime requirement vs dev requirement.

## Open Questions
1. Canonical GitHub org: `kgang` or `kentgang`?
2. Minimum Python version: 3.11 or 3.12?
3. Public docs priority: “examples-first” vs “getting-started-first”?

## Acceptance Criteria
- All links in README and Quickstart resolve.
- MkDocs builds without missing pages.
- Python requirement is consistent across all entry points.
- New docs landing page points to the four primary entry docs.
