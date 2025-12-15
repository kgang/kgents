---
path: plans/agent-town/plan-review
status: active
last_touched: 2025-12-15
touched_by: codex-gpt5
blocking: []
enables:
  - agent-town/grand-strategy
  - agent-town/monetization-mvp
  - agent-town/phase8-inhabit
session_notes: |
  Critical read of all Agent Town plans using spec/principles, _focus.md, and
  refreshed market data. Highlights shaky assumptions and proposes corrections
  before more build.
---

# Agent Town Plan Review (Critical)

> *"Tasteful and monetizable, or not worth building."*

## Quick Reading of the Plans
- **grand-strategy.md**: Ambitious and evocative but leans on unverified market figures; exits are not costed against LLM spend.
- **monetization-mvp.md**: Pricing ladders look generous but omit CAC/retention and Haiku/Sonnet/Opus unit economics; paywall logic solid but needs guardrails.
- **phase5* docs**: Visualization/streaming plans are strong; NATS risk already noted. Missing metrics/observability to support monetization.
- **phase7-llm-dialogue.md**: Deep design, but budget math is back-of-envelope and doesn’t integrate pay-to-zoom tiers.
- **phase8/9 stubs**: Inhabit + web are underspecified for money/ethics; resistance mechanic not tied to billing or user safety.

## Internet Spot-Checks
- `webpronews.com/ai-companion-apps-surge-to-120m-revenue-by-2025-amid-growth-boom` (2025-08-12) cites ~$120M market size; TechCrunch link in grand-strategy blocks anonymous fetch (451), so treat the figure as **unverified** until a second source corroborates.
- RevenueCat “State of Subscription Apps 2025” (2025-03-14) confirms hybrid monetization growth but does **not** give AI-companion-specific ARPU; current plans assume generous ARPU without source.
- Claude pricing (public Anthropic docs, 2024-10): Haiku ~$0.25/M in, $1.25/M out; Sonnet ~$3/M in, $15/M out; Opus ~$15/M in, $75/M out. These materially affect LOD margins.

## Critical Gaps vs Principles
- **Tasteful/Curated**: 5 archetypes good, but Phase 12 “mystery packs” risk feature sprawl; prune to 1-2 premium scenarios that embody opacity + drama.
- **Ethical**: Resistance mechanic isn’t paired with safety/consent; pay-to-override (“force resistance”) could violate “augment, don’t replace judgment.”
- **Composable**: Monetization tiers aren’t wired into operad/polynomial model; costs/pricing exist outside the composition grammar.
- **Joy-Inducing**: LOD 5 “opacity” sells mystery but could feel like a paywall for nothing; needs visible value (e.g., evocative prose, not just a black box).
- **Generative**: Plans cite tests counts but not regenerability; monetization prompts/flows lack spec-first compression.
- **Heterarchical**: Branching/time travel is planned, but governance is hierarchical (paywall gate) without perturbation hooks in flux.

## Unit Economics Reality Check (align to _focus: “MAKE MONEY WITH AGENT TOWN”)
- If LOD 3 uses Haiku with ~300 input/output tokens, marginal cost ≈ $0.00045. Charging $0.001/view leaves ~55% gross margin **before** infra/Stripe fees.
- LOD 4 with Sonnet at ~800 tokens costs ≈ $0.014 (in+out). Current price at 50 credits ($0.005–$0.01) could be **loss-making** for Explorer/Adventurer packs.
- LOD 5 with Opus at ~1,200 tokens costs ≈ $0.108. Price at 200 credits ($0.05–$0.20) is break-even at best; needs higher price or smaller output.
- INHABIT sessions (multiple turns) will dominate cost; no cap per session is specified.

## Recommended Corrections (actionable deltas)
- **Price/Credit Table**: Recompute credit costs from published Claude rates. Raise LOD4 to 80–100 credits and LOD5 to 300–400 credits, or shift LOD4 to Sonnet-lite/Haiku+context to keep margins.
- **Safety + Consent**: Make “force resistance” opt-in, logged, and expensive; add “consent debt” meter that cools over time. Align with Ethical principle.
- **Instrumentation First**: Add Phase 5.1 milestone: metrics spine (per-action cost, latency, user path, drop-off). Without it, monetization hypotheses are untestable.
- **Pay-to-Zoom Value Proof**: For LOD5, guarantee an **artifact** (e.g., short vignette, hidden coalition tension) rather than pure opacity to avoid dark-pattern perception.
- **CAC/Retention Check**: Add assumptions (paid conversion %, churn) sourced from RevenueCat report; set “kill switch” if CAC > 30% of LTV.
- **Haiku Everywhere**: Default to Haiku for background/observer views; Sonnet/Opus only when user explicitly requests depth (aligns with _focus “use lots of Haiku tokens”).
- **Branching as SKU**: Move branching into premium scenarios (Founder/Citizen bundles) to avoid costly state duplication for free tiers.
- **Regenerate-from-Spec**: For monetization flows, add a spec stub (pricing + paywall contract) and derive UI/API from it to satisfy the Generative principle.

## Small Edits to Existing Plans (apply next)
- `plans/agent-town/monetization-mvp.md`: Replace credit costs with margin-safe numbers, add CAC/retention assumptions, mark TechCrunch figure as unverified, add LOD cost table with Haiku/Sonnet/Opus pricing.
- `plans/agent-town/grand-strategy.md`: Add “Safety/Consent” to Part VIII; tie INHABIT resistance to billing + ethics; prune scenario list to 2 flagship mysteries.
- `plans/agent-town/phase8-inhabit.md`: Specify budget caps per session and consent logging; align resistance with pay-to-override rules.
- `plans/agent-town/phase9-web-ui.md`: Instrumentation widgets (cost/latency per LOD) before Stripe UI.

## Next Actions
- Approve price/cost recomputation and update the two plan files above.
- Insert Phase 5.1 instrumentation milestone and per-action cost logging contract.
- Add “consent debt” + “artifact guarantee” to INHABIT/LOD5 specs.

*Continuation hint: `/hydrate plans/agent-town/plan-review.md` then patch the named plan files with the corrections above.*
