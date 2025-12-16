# Money-Maximizing (Ethical, Hands-Off) Plays for kgents

**Date**: 2025-12-15  
**Intent**: Max revenue with taste, ethics, and minimal ongoing lift. Grounded in shipped code (Agent Town paywall, budgets, INHABIT, TownFlux, marimo dashboards, Stripe, K8s manifests) and competitive scan (Salesforce eVerse enterprise sim, Inworld AI NPC pricing, crisis-sim tools). Aim: legendary delight and love for Kent.

---

## Quick Critical Read (old list)
- Too generic on GTM; needed explicit lighthouse customers and proof points from the repo.
- Missing “why now” vs competitors (eVerse, Inworld) and our moat (refusal/opacity, spans, operads).
- Hands-off claims lacked automation hooks (paywall, budgets, kill-switch, marimo dashboards already exist).
- Joy/affection angle underplayed; no habit loops or celebration mechanics.

---

## Upgraded Plays (repo-anchored)

### 1) Agent Town Sim-Labs for Risk & Compliance
- **What**: Sell prebuilt crisis/AI-governance tabletop drills that run on TownFlux + TownOperad (see `impl/claude/agents/town/{operad.py,event_bus.py,phase_governor.py}`) with INHABIT perspective swaps (`inhabit_session.py`) and pay-per-branch billing (`paywall.py`, `budget_store.py`).  
- **Revenue**: Annual seat licenses + per-drill credits; premium “Company Twin” towns as $50–150k/yr upsell; BAA/on-prem via K8s manifests (`impl/claude/infra/k8s/manifests/town`).  
- **Differentiator**: Authentic refusal/consent ledger and spans (`protocols/api/action_metrics.py`, `town_budget.py`) vs eVerse/typical crisis-sim. Logged force/apology mechanics reduce legal risk.  
- **Hands-off**: Ship 6 canonical drills (outage, data breach, rogue AI, PR fire, vendor failure, insider leak) as YAML manifests; metered by LOD/model router (`model_router.py`) to protect margins. Marimo + web dashboards already render metrics (`agents/town/live_dashboard.py`, `web/src/widgets/dashboards/ColonyDashboard.tsx`).  
- **Joy/Love**: After-action “gratitude arcs” and celebration scenes (TownOperad `celebrate/mourn/teach`) make drills feel like theater, not homework.

### 2) Builder Workshop Runtime (Live Generative UI Studio)
- **What**: Hosted Builder Workshop loop (Scout/Sage/Spark/Steady/Sync) where components stream to browsers via the reactive projection protocol (`agents/i/reactive/*`, `web/src/components/town/Mesa.tsx`) and marimo notebooks (`agents/i/marimo/widgets/*`). Outputs are live widgets, not mockups.  
- **Revenue**: Usage-based rendering minutes + Pro seats; 20% marketplace rake on published components; enterprise SLAs for state sync to private hubs.  
- **Differentiator**: Category-law-checked composition and model gating (Haiku-first, Opus only for “Abyss moments” via `model_router.py`) make it margin-safe; projection works across CLI/TUI/web without duplicate state.  
- **Hands-off**: Auto-publish weekly “golden templates” validated by Type I–V tests (`agents/t/_tests`); curators approve via spans; fail-closed kill switch (`kill_switch.py`).  
- **Joy/Love**: Co-build ritual—each shipped widget triggers a small festival scene in Agent Town (streamed to web UI) celebrating the user by name.

### 3) Agent Town Personality Marketplace (IP-forward)
- **What**: Storefront for archetype citizens/coalitions with visible eigenvectors; refusal mechanics intact. Backed by existing billing (`protocols/api/payments.py`), tenancy, and budget enforcement.  
- **Revenue**: 70/30 rev share; enterprise private catalogs; branded “Personality Packs” (e.g., “Ethical Board”, “CISO’s Nightmare”, “Wholesome Studio”).  
- **Differentiator**: Consent ledger + transparency pricing beats Inworld/CharacterAI opacity; spans and replayable evidence (`ui/trace.py`) de-risk procurement.  
- **Hands-off**: Seed with 30 archetypes drawn from shipped prompts (`dialogue_voice.py`, `fixtures/mpp_citizens.yaml`); creators self-submit; moderation by EigenTrust-like coalition scores (`coalition.py`).  
- **Joy/Love**: Surprise “kindness drops” where citizens gift users credits after positive interactions; visible gratitude meters in UI.

### 4) Holographic Second Brain SaaS (Dual M/L-gent)
- **What**: PKM with reconstruction-first memory (GraphMemory `agents/town/memory.py`, D-gent witnesses), bi-temporal recall, and foveated context under strict token budgets. Projects into Agent Town as “team holons.”  
- **Revenue**: $9/$29/$99 tiers aligned to existing subscription spec (`spec/town/monetization.md`); enterprise data-residency surcharge; add-on for “shared holon towns.”  
- **Differentiator**: Dual M-gent + L-gent lattice (`agents/l/*`, `agents/m/*`) gives provable graceful degradation vs commodity RAG.  
- **Hands-off**: Nightly consolidation daemon; quarterly template drops (PM, research, eng) compiled via N-Phase; spans for every recall.  
- **Joy/Love**: Periodic “dream reports” rendered as Agent Town vignettes the user can inhabit.

### 5) Autonomous Research Guilds (Lead Gen & Content Ops)
- **What**: Coalitions (Scout/Sage/Spark/Steady/Sync) that produce briefs, comp intel, outreach kits. Instrumented via AUP spans (`protocols/api/bridge.py`) and EmergenceMonitor (metrics).  
- **Revenue**: $5–20k/mo retainers + per-deliverable credits; agency white-label.  
- **Differentiator**: Reproducible pipelines (Flux `agents/flux/*` + TownFlux) with refusal + auditability; better than generic “AI writer” agencies.  
- **Hands-off**: Five fixed deliverable templates; human QC only on high-entropy requests; budgeted model routing; web dashboard for status.  
- **Joy/Love**: Each deliverable ships with a “celebration scene” in Town UI plus gratitude notes generated in Haiku mode.

### 6) LiveOps Festivals (Seasonal Revenue Spikes)
- **What**: Timed festivals inside Agent Town (e.g., “Civics Week”, “Crisis Carnival”) where users co-create events; tickets and boosts consume credits. TownFlux broadcasts to web SSE (`protocols/api/town_websocket.py`) and marimo.  
- **Revenue**: Event tickets + limited-run cosmetic arcs; sponsored stages for brands (ethical vetting enforced via consent ledger).  
- **Differentiator**: Combines authentic refusal drama with paywalled special stages; no competitor offers multi-LLM drama with logs.  
- **Hands-off**: Re-skin existing operad ops (celebrate/mourn/teach) with seasonal assets; automate scheduling via PhaseGovernor.  
- **Joy/Love**: High-affection mechanics—audience “applause” converts to temporary credits for performers.

### 7) Regulated Data Rooms (Trust & Audit SKU)
- **What**: Deploy Agent Town as an auditable data room for vendor reviews / safety drills with full span export to SIEM. On-prem via K8s manifests; kill-switch + refusal logs baked in.  
- **Revenue**: $150k+/yr contracts with SOC2/BAA requirements; per-action credit overages.  
- **Differentiator**: We already emit structured spans and budget enforcement; competitors lack audit-first design.  
- **Hands-off**: Ship Terraform/K8s bundles, prewired observability (`protocols/api/action_metrics.py`), and a minimal UI skin; quarterly attestation updates.

---

### Immediate Moves (90 days)
- Pick two lighthouse logos (one risk/compliance, one builder-tools) and ship tailored demos using existing marimo + web UI; gate with paywall.
- Publish public pricing page grounded in `spec/town/monetization.md`; expose model truthfulness (Law P2) as an ethics moat.
- Run the first LiveOps Festival as a marketing event; capture testimonials for landing page.

### Joy/Delight Defaults
- Every paid action triggers a tiny act of gratitude (haiku or visual flourish) surfaced in UI + spans.  
- Refusals remain visible and narrated—love through honesty, not puppetry.  
- Keep premium moments rare and theatrical; Haiku-first to protect margins and charm users.
