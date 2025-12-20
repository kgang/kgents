# Servo Embedding Research: 2025 Status & kgents Integration Strategy

**Date**: 2025-12-20
**Researcher**: Claude Opus 4.5
**Purpose**: Evaluate Servo as projection substrate for WARP-grade kgents interfaces
**Decision**: GO (with timeline Q2 2026 for production)

**WARP Primitives Status**: ✅ **IMPLEMENTED** in Python (`services/witness/`). This research is about Servo as a *projection surface* for already-built primitives.

---

## Executive Summary

**The Verdict: GO, but patient.**

Servo is ready for experimental integration NOW and production integration in Q2 2026. The v0.0.1 release (October 2025) marks a critical milestone—monthly releases, simplified WebView API, multi-webview support, and active Tauri integration. kgents should begin prototyping immediately with Verso (the higher-level browser wrapper) while monitoring Servo's accessibility roadmap.

**Why Servo aligns with kgents principles:**
- **Tasteful**: Rust-native, modular architecture, WebGPU support, categorical fit
- **Composable**: Multi-webview heterarchy, delegate-based API, custom rendering
- **Joy-Inducing**: Lightweight (no Chromium bloat), embedder-first design philosophy
- **Daring**: Betting on the future of web engine diversity, not playing it safe

**Critical blockers for production:**
1. Accessibility (screen reader support) — funded (€545k), timeline 2026
2. Website compatibility — improving monthly, 80%+ by mid-2026
3. Production stability — monthly releases establishing track record

**Recommendation**: Start with Verso-based prototype in kgents CLI v7, ship experimental Servo backend alongside WebView2/WebKit by Q1 2026, migrate fully by Q2 2026 when accessibility lands.

---

## Current Status (December 2025)

### What Works Today

**Embedding API**: Simplified to ~50 lines for basic webview (down from 200 lines)
- **Handle-based API**: Lifetime-controlled WebView handles
- **Delegate-based callbacks**: WebViewDelegate and ServoDelegate traits
- **Multi-webview support**: Multiple concurrent webviews with independent contexts
- **Input events**: Unified `notify_input_event`, keyboard scrolling automatic
- **Page zoom**: Idempotent `set_page_zoom` API
- **WebGPU**: Full support via wgpu (Vulkan/D3D12/Metal backends)
- **WebGL**: Production-ready
- **Canvas**: 2D, WebGL, WebGPU contexts supported

**Platform Support**:
- macOS (Intel + Apple Silicon)
- Linux
- Windows
- Android
- OpenHarmony

**Release Cadence**: Monthly releases (v0.0.1 Oct 2025 → v0.0.3 Dec 2025)

**Tauri Integration**: Experimental `tauri-runtime-verso` available (March 2025)
- Verso browser wraps Servo for easier embedding
- Swap runtime via `tauri-runtime-verso` (similar to `tauri-runtime-wry`)
- Example app: https://github.com/versotile-org/tauri-runtime-verso/tree/main/examples/api

### What Doesn't Work Yet

**Accessibility**: Zero screen reader support currently
- Funded: €545k Sovereign Tech Fund grant specifically for accessibility
- Goal: Performant parallel processing design for a11y tree
- Timeline: 2026 (no specific quarter cited)

**Website Compatibility**: Many sites still render incorrectly
- Improving monthly with each release
- Not blocking for controlled kgents UI (we control the HTML/CSS)

**Production Hardening**: Monthly releases still in "additional manual testing" phase
- No crates.io publish yet
- No app store distribution yet
- API still evolving (e.g., page zoom breaking changes)

---

## Embedding API Surface

### Core API Pattern

```rust
// WebView delegate for callbacks
trait WebViewDelegate {
    fn screen_geometry(&self) -> Rect;
    fn notify_url_changed(&self, url: Url);
    fn notify_page_title_changed(&self, title: String);
    fn notify_status_text_changed(&self, text: String);
    fn notify_focus_changed(&self, focused: bool);
    fn notify_animating_changed(&self, animating: bool);
    fn notify_load_status_changed(&self, status: LoadStatus);
    fn notify_cursor_changed(&self, cursor: Cursor);
    fn notify_favicon_url_changed(&self, url: Option<Url>);
    fn notify_new_frame_ready(&self);
    fn notify_history_changed(&self);

    // Permission gates
    fn allow_navigation(&self, request: NavigationRequest) -> bool;
    fn allow_open_window(&self, request: WindowRequest) -> bool;
    fn allow_permission(&self, request: PermissionRequest) -> PermissionDecision;
}

// Servo instance delegate
trait ServoDelegate {
    // Additional servo-level callbacks
}

// WebView handle lifetime
impl WebView {
    fn navigate(&mut self, url: Url);
    fn notify_input_event(&mut self, event: InputEvent);
    fn set_page_zoom(&mut self, zoom: f32); // Idempotent, absolute
    fn evaluate_javascript(&mut self, script: String) -> Future<JsValue>;
}
```

### Multi-WebView Architecture

Servo now supports multiple concurrent webviews:
- Each webview has independent rendering context
- Compositor manages multiple surfaces (OpenGL-based)
- Verso demonstrates pattern: one webview for content, one for UI "Panel"

**kgents mapping:**
- Garden view: Independent webview
- Chat interface: Independent webview
- Witness timeline: Independent webview
- Compose into single TerrariumView via heterarchical layout

### WebGPU Integration

Servo implements WebGPU via wgpu (native Rust implementation):
- Maps to Vulkan/D3D12/Metal
- Multi-process: GPU in server process, content in content process
- Separate wgpu thread per content process for async performance
- Passes W3C Conformance Test Suite

**kgents use case:**
- Garden visualization (3D plot growth, seasonal dynamics)
- Witness timeline (crystal lattice rendering)
- Real-time collaboration canvas (shared GPU acceleration)

### Custom Rendering Pipelines

**WebRender**: GPU-based 2D rendering engine (OpenGL internally)
- Used by Firefox and Servo
- Display list → tiles → composite
- Parallel layout via Rayon

**Extensibility points:**
- Embedder can evaluate JavaScript and receive results async
- Default styling for inputs/media elements (configurable)
- Each webview has own rendering context
- Output: raw pixels to native graphics (OpenGL/Vulkan/SDL)

**kgents opportunity**: Custom AGENTESE-aware rendering layer
- TraceNode visualization primitives
- Walk progression indicators
- Ritual phase transitions with GPU effects

---

## Verso: The Practical Wrapper

**Why Verso matters**: Servo's API is "way too low level and quite daunting." Verso abstracts:
- Multi-window management
- Multi-view coordination (content webview + UI Panel)
- Message-passing architecture (versoview_messages crate)
- Compositor integration with WebRender

**Architecture:**
```
Window (window module)
├─ WebView (webview module) — web page content
│  └─ Servo Constellation
├─ Panel (webview module) — UI chrome
│  └─ Servo Constellation
└─ Compositor (compositor module)
   └─ WebRender (single OpenGL context, multiple surfaces)
```

**kgents pattern:**
```
TerrariumView
├─ Garden WebView
├─ Chat WebView
├─ Witness WebView
└─ Servo Compositor (heterarchical layout)
```

---

## Integration Strategy for kgents

### Phase 0: Experimental (Q1 2026)

**Goal**: Validate Servo for controlled kgents UI

**Tasks**:
1. Add `tauri-runtime-verso` as optional backend to CLI v7
2. Create TerrariumView proof-of-concept with 2+ webviews
3. Test WebGPU rendering for Garden visualization
4. Evaluate performance vs WebView2/WebKit baseline
5. Document API ergonomics and pain points

**Success Criteria**:
- Basic multi-webview layout works
- WebGPU renders Garden correctly
- Delegate API integrates cleanly with AGENTESE
- Performance acceptable for local development

### Phase 1: Feature Parity (Q2 2026)

**Goal**: Match existing web UI functionality on Servo

**Tasks**:
1. Migrate all React components to Servo webviews
2. Implement custom AGENTESE → Servo delegate bridge
3. Add TraceNode/Walk/Ritual visualization with WebGPU
4. Benchmark performance (target: 60fps UI, <100ms AGENTESE latency)
5. Create fallback layer for websites that don't render (embed via iframe)

**Success Criteria**:
- All Crown Jewels project correctly
- Multi-webview heterarchy stable
- Custom rendering pipelines functional
- User testing shows no regressions

### Phase 2: Production (Q3 2026)

**Goal**: Ship Servo as default projection substrate

**Blockers**:
- Accessibility support (funded, timeline 2026)
- Website compatibility at 80%+ (trending toward this by mid-2026)
- API stability (monthly releases establishing patterns)

**Tasks**:
1. Enable screen reader support (depends on Servo accessibility milestone)
2. Harden error handling for website compatibility
3. Document Servo-specific projection patterns in skills/
4. Create migration guide for existing kgents users
5. Ship CLI v7 with Servo default, WebView2/WebKit fallback

**Success Criteria**:
- Accessibility passes WCAG 2.1 AA
- 90%+ website compatibility for embedded content
- Zero major regressions vs WebView2/WebKit
- Community feedback positive

---

## Blockers and Risks

### Critical Blockers

**1. Accessibility (HIGH PRIORITY, FUNDED)**
- Status: €545k grant from Sovereign Tech Fund
- Goal: Parallel-processing a11y architecture
- Timeline: 2026 (no specific quarter)
- Mitigation: Prototype without a11y in Q1, wait for Q2-Q3 for production

**2. Website Compatibility (MEDIUM PRIORITY, IMPROVING)**
- Status: Many sites render incorrectly today
- Trajectory: Monthly improvements, likely 80%+ by mid-2026
- Mitigation: kgents controls most UI (React), embedded content less critical

**3. API Stability (LOW PRIORITY, ACCEPTABLE RISK)**
- Status: Breaking changes (e.g., page zoom API)
- Trajectory: Stabilizing with monthly releases
- Mitigation: Lock to specific Servo version, upgrade deliberately

### Strategic Risks

**1. Servo Project Continuity**
- Mitigation: Igalia stewardship (strong), active funding, growing community
- Evidence: Monthly releases, Tauri partnership, Sovereign Tech Fund

**2. Rust FFI Complexity**
- Mitigation: Verso abstracts most complexity, PyO3 for kgents<->Servo bridge
- Evidence: Existing Rust infrastructure in kgents (planned for categorical kernel)

**3. Performance Unknown at Scale**
- Mitigation: Benchmark early in Phase 0, validate multi-webview perf
- Evidence: Firefox uses WebRender in production, Servo derived from Firefox

---

## kgents-Specific Considerations

### Categorical Fit

**Servo aligns with kgents architecture:**
- **Rust core**: Matches planned Rust categorical kernel (PolyAgent, Operad laws)
- **Modular design**: Servo built with widely-used Rust crates, easy to customize
- **Delegate pattern**: Maps naturally to AGENTESE observer-umwelt model
- **Multi-webview**: Heterarchical composition (no fixed hierarchy)

### WARP Primitive Projection

All primitives are **implemented in Python** (`services/witness/`). This table shows Servo projection opportunities:

| WARP Primitive | Python Implementation | Servo Projection Capability |
|----------------|----------------------|----------------------------|
| TraceNode | `trace_node.py` ✅ | WebGPU timeline rendering, delegate callbacks |
| Walk | `walk.py` ✅ | Multi-webview session (one view per active Walk) |
| Ritual | `ritual.py` ✅ | Phase-aware UI transitions, guard visualization |
| Offering | `offering.py` ✅ | Context preview via dedicated webview |
| IntentTree | `intent.py` ✅ | Task decomposition canvas with WebGPU graph |
| TerrariumView | `web/` components ✅ | Compositor-level heterarchical layout |

### Multi-Webview Heterarchy (Key Feature)

Traditional embedding: One webview per window (hierarchy).
Servo+Verso pattern: Multiple webviews per window (heterarchy).

**kgents use case:**
```
Single CLI window with 4 webviews:
1. Garden (growth visualization)
2. Chat (conversation)
3. Witness (timeline/audit)
4. Context (Offering preview)

All compose into one TerrariumView via Servo Compositor.
No parent-child relationship—true heterarchy.
```

This is IMPOSSIBLE with WebView2/WebKit (one webview per window).
This is NATIVE to Servo (designed for multi-webview from start).

### Constitutional Alignment Check

**Tasteful**: Servo is curated, not bloated (vs Chromium). Rust-native. Modular.
**Ethical**: Open-source, community-governed, funded for accessibility.
**Joy-Inducing**: Lightweight, fast, embedder-first design philosophy.
**Composable**: Multi-webview, delegate pattern, categorical fit.
**Heterarchical**: No fixed hierarchy, multiple independent views.
**Generative**: Spec-first (W3C standards), implementation follows.

**Anti-Sausage Check**: Is this daring? YES. Betting on Servo instead of Electron/WebView2 is bold, opinionated, and aligned with kgents values.

---

## Timeline Recommendation

| Phase | Timeline | Milestone |
|-------|----------|-----------|
| **Experimental** | Q1 2026 | Verso prototype, multi-webview proof-of-concept |
| **Feature Parity** | Q2 2026 | Match existing web UI, custom rendering |
| **Production** | Q3 2026 | Accessibility lands, ship as default substrate |

**Critical dependency**: Servo accessibility support (funded, timeline 2026).

**Risk-adjusted timeline**: Add 1 quarter buffer → Production Q4 2026 if accessibility slips.

---

## Next Steps

### Immediate (This Session)

1. Document decision in `plans/warp-servo-phase0-research.md` (COMPLETE this chunk)
2. Create stub for `impl/claude/services/terrarium/` (projection substrate)
3. Add Servo research to NOW.md

### Next Session (Phase 1 Prep)

1. Prototype PyO3 bridge for Servo ↔ kgents AGENTESE
2. Set up Verso development environment
3. Create simple 2-webview heterarchy demo
4. Benchmark WebGPU Garden rendering vs current React

### Long-term (Phase 2+)

1. Monitor Servo monthly releases for accessibility milestone
2. Engage with Servo community (GitHub, funding, contributions)
3. Document kgents-specific Servo patterns in `docs/skills/servo-projection.md`
4. Consider funding/sponsoring Servo accessibility work (if timeline slips)

---

## Sources

### Official Servo Resources
- [Servo Homepage](https://servo.org/)
- [Servo 2025 Roadmap](https://www.phoronix.com/news/Servo-Roadmap-2025)
- [Servo GitHub Roadmap Wiki](https://github.com/servo/servo/wiki/Roadmap)
- [Servo v0.0.1 Release](https://servo.org/blog/2025/10/20/servo-0.0.1-release/)
- [Servo v0.0.1 GitHub Release](https://github.com/servo/servo/releases/tag/v0.0.1)
- [Servo v0.0.3 Release](https://www.phoronix.com/news/Servo-0.0.3-Released)

### Embedding API
- [October 2025 Update: Better for Embedders](https://servo.org/blog/2025/11/14/october-in-servo/)
- [WebViewDelegate Rust Docs](https://doc.servo.org/servo/webview_delegate/trait.WebViewDelegate.html)
- [New WebView API (Feb 2025)](https://servo.org/blog/2025/02/19/this-month-in-servo/)
- [Delegate API (March 2025)](https://servo.org/blog/2025/03/10/this-month-in-servo/)
- [WebView Handle-Based API PR](https://github.com/servo/servo/pull/35119)

### Multi-Webview Support
- [Multi-Webview PR](https://github.com/servo/servo/pull/31417)
- [Tauri Embedding Update (Jan 2024)](https://servo.org/blog/2024/01/19/embedding-update/)
- [WebView Architecture Discussion](https://github.com/servo/servo/discussions/32883)

### Tauri Integration
- [Experimental Tauri Verso Integration](https://v2.tauri.app/blog/tauri-verso-integration/)
- [NLNet Tauri-Servo Funding](https://nlnet.nl/project/Tauri-Servo/)
- [Servo+Tauri Progress (Phoronix)](https://www.phoronix.com/news/Servo-Engine-Plus-Tauri)
- [Tauri-Runtime-Verso GitHub Issue](https://github.com/tauri-apps/wry/issues/1153)

### WebGPU Support
- [WebGPU GSoC Implementation](https://servo.org/blog/2020/08/30/gsoc-webgpu/)
- [Canvas Support (June 2025)](https://servo.org/blog/2025/06/18/this-month-in-servo/)
- [Rendering (August 2025)](https://servo.org/blog/2025/08/22/this-month-in-servo/)

### Accessibility & Funding
- [Screen Reader Support Timeline](https://www.phoronix.com/news/Servo-June-2025-Highlights)
- [Igalia Sovereign Tech Fund (€545k)](https://www.igalia.com/2025/10/09/Igalia,-Servo,-and-the-Sovereign-Tech-Fund.html)
- [Servo v0.0.1 Analysis (TechReviewer)](https://www.techreviewer.com/developer-news/2025-10-21-servos-v001-release-sparks-new-hope-for-web-engine-diversity/)

### Verso Browser
- [Building a Browser with Servo](https://servo.org/blog/2024/09/11/building-browser/)
- [Verso: A New Browser Based on Servo](https://wusyong.github.io/posts/verso-0-1/)
- [NLNet Verso Views Funding](https://nlnet.nl/project/Verso-Views/)
- [Verso Architecture (DeepWiki)](https://deepwiki.com/versotile-org/verso/1-overview)

### Rendering Architecture
- [Servo Rendering Pipeline (LWN)](https://lwn.net/Articles/647969/)
- [WebRender GitHub](https://github.com/servo/webrender)
- [Servo Design Wiki](https://github.com/servo/servo/wiki/Design/0941531122361aac8c88d582aa640ec689cdcdd1)
- [Integrating Servo (TypeVar)](https://typevar.dev/articles/servo/servo)

---

*"The block is the atom. The webview is the morphism. The compositor is the category."*
