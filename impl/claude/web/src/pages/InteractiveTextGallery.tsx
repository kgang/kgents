/**
 * InteractiveTextGallery: Joy Animation primitives showcase.
 *
 * Post-surgical refactor 2025-12-22: Renamed from Interactive Text Gallery.
 * Now showcases foundation joy/animation primitives instead of AGENTESE-specific
 * token rendering.
 *
 * Pilots:
 * 1. Breathing animations - Different intensities and speeds
 * 2. Pop animations - Scale effects on interaction
 * 3. Shake animations - Attention-grabbing motion
 * 4. Shimmer effects - Loading/skeleton states
 * 5. PersonalityLoading - Jewel-themed loading states
 * 6. EmpathyError - Friendly error display
 *
 * @see components/joy/ - Joy animation primitives
 */

import { useState, useEffect } from 'react';
import { useWindowLayout } from '@/components/elastic';
import {
  Breathe,
  Pop,
  Shake,
  ShimmerBlock,
  PersonalityLoading,
  EmpathyError,
  type CrownJewel,
} from '@/components/joy';
import { documentApi } from '@/api/client';
import {
  InteractiveDocument,
  PortalToken,
  PrincipleToken,
  ImageToken,
  type SceneGraph,
} from '@/membrane/tokens';

// =============================================================================
// Pilot Components
// =============================================================================

interface PilotContainerProps {
  title: string;
  subtitle: string;
  children: React.ReactNode;
  fullWidth?: boolean;
}

function PilotContainer({ title, subtitle, children, fullWidth }: PilotContainerProps) {
  return (
    <div
      className={`rounded-lg border border-sage-700/30 bg-surface-elevated overflow-hidden ${fullWidth ? '' : 'max-w-fit'}`}
    >
      <div className="px-4 py-2 bg-sage-900/30 border-b border-sage-700/30">
        <h3 className="font-medium text-sm text-sage-200">{title}</h3>
        <p className="text-xs text-sage-400/70">{subtitle}</p>
      </div>
      <div className="p-4">{children}</div>
    </div>
  );
}

/**
 * Pilot 1: Breathing Animations
 */
function BreathingPilot() {
  return (
    <PilotContainer
      title="Breathe Animation"
      subtitle="Organic pulsing motion with configurable intensity"
    >
      <div className="space-y-6">
        <div className="flex gap-8 justify-center items-center">
          <div className="text-center">
            <Breathe intensity={0.3} speed="slow">
              <div className="w-16 h-16 rounded-full bg-sage-500" />
            </Breathe>
            <div className="mt-2 text-xs text-text-muted">Slow / Low</div>
          </div>
          <div className="text-center">
            <Breathe intensity={0.5} speed="normal">
              <div className="w-16 h-16 rounded-lg bg-copper-500" />
            </Breathe>
            <div className="mt-2 text-xs text-text-muted">Normal / Medium</div>
          </div>
          <div className="text-center">
            <Breathe intensity={0.8} speed="fast">
              <div className="w-16 h-16 rounded-xl bg-slate-500" />
            </Breathe>
            <div className="mt-2 text-xs text-text-muted">Fast / High</div>
          </div>
        </div>
        <p className="text-xs text-text-muted text-center">
          <strong>Use case:</strong> Indicate active/live states, draw gentle attention
        </p>
      </div>
    </PilotContainer>
  );
}

/**
 * Pilot 2: Pop Animations
 */
function PopPilot() {
  const [triggered, setTriggered] = useState(false);

  return (
    <PilotContainer title="Pop Animation" subtitle="Scale effect for feedback and emphasis">
      <div className="space-y-6">
        <div className="flex gap-8 justify-center items-center">
          <div className="text-center">
            <Pop trigger={triggered} scale={1.1}>
              <button
                onClick={() => {
                  setTriggered(true);
                  setTimeout(() => setTriggered(false), 200);
                }}
                className="px-4 py-2 rounded bg-copper-600 hover:bg-copper-500 text-white text-sm"
              >
                Click me
              </button>
            </Pop>
            <div className="mt-2 text-xs text-text-muted">scale: 1.1</div>
          </div>
          <div className="text-center">
            <Pop trigger={true} scale={1.05}>
              <div className="w-16 h-16 rounded-lg bg-sage-600 flex items-center justify-center">
                <span className="text-white text-xl">✓</span>
              </div>
            </Pop>
            <div className="mt-2 text-xs text-text-muted">Always popped</div>
          </div>
        </div>
        <p className="text-xs text-text-muted text-center">
          <strong>Use case:</strong> Button press feedback, selection highlight
        </p>
      </div>
    </PilotContainer>
  );
}

/**
 * Pilot 3: Shake Animations
 */
function ShakePilot() {
  const [shaking, setShaking] = useState(false);

  return (
    <PilotContainer title="Shake Animation" subtitle="Attention-grabbing horizontal motion">
      <div className="space-y-6">
        <div className="flex gap-8 justify-center items-center">
          <div className="text-center">
            <Shake trigger={shaking} intensity="gentle">
              <div className="px-4 py-2 rounded bg-amber-600/50 border border-amber-500 text-amber-100 text-sm">
                Invalid input
              </div>
            </Shake>
            <button
              onClick={() => {
                setShaking(true);
                setTimeout(() => setShaking(false), 500);
              }}
              className="mt-3 text-xs text-copper-400 hover:text-copper-300"
            >
              Trigger shake
            </button>
          </div>
          <div className="text-center">
            <Shake trigger={true} intensity="urgent">
              <div className="w-12 h-12 rounded-full bg-red-600 flex items-center justify-center">
                <span className="text-white text-xl">!</span>
              </div>
            </Shake>
            <div className="mt-2 text-xs text-text-muted">Continuous</div>
          </div>
        </div>
        <p className="text-xs text-text-muted text-center">
          <strong>Use case:</strong> Form validation errors, urgent notifications
        </p>
      </div>
    </PilotContainer>
  );
}

/**
 * Pilot 4: Shimmer Effects
 */
function ShimmerPilot() {
  return (
    <PilotContainer
      title="Shimmer Effect"
      subtitle="Loading/skeleton placeholder animation"
      fullWidth
    >
      <div className="space-y-4">
        <div className="space-y-2">
          <ShimmerBlock width="w-3/4" height="h-4" />
          <ShimmerBlock width="w-full" height="h-4" />
          <ShimmerBlock width="w-5/6" height="h-4" />
        </div>
        <div className="flex gap-4">
          <ShimmerBlock width="w-16" height="h-16" rounded="full" />
          <div className="flex-1 space-y-2 py-1">
            <ShimmerBlock width="w-1/3" height="h-4" />
            <ShimmerBlock width="w-1/2" height="h-3" />
          </div>
        </div>
        <p className="text-xs text-text-muted text-center pt-2">
          <strong>Use case:</strong> Content loading placeholders, skeleton screens
        </p>
      </div>
    </PilotContainer>
  );
}

/**
 * Pilot 5: PersonalityLoading
 */
function PersonalityLoadingPilot() {
  const jewels: CrownJewel[] = ['brain', 'gestalt', 'gardener', 'forge', 'coalition'];

  return (
    <PilotContainer title="PersonalityLoading" subtitle="Jewel-themed loading indicators" fullWidth>
      <div className="space-y-6">
        <div className="flex flex-wrap gap-8 justify-center">
          {jewels.map((jewel) => (
            <div key={jewel} className="text-center">
              <PersonalityLoading jewel={jewel} size="md" />
              <div className="mt-2 text-xs text-text-muted capitalize">{jewel}</div>
            </div>
          ))}
        </div>
        <div className="flex gap-4 justify-center pt-4 border-t border-gray-800">
          <div className="text-center">
            <PersonalityLoading jewel="brain" size="sm" />
            <div className="mt-1 text-[10px] text-text-muted">sm</div>
          </div>
          <div className="text-center">
            <PersonalityLoading jewel="brain" size="md" />
            <div className="mt-1 text-[10px] text-text-muted">md</div>
          </div>
          <div className="text-center">
            <PersonalityLoading jewel="brain" size="lg" />
            <div className="mt-1 text-[10px] text-text-muted">lg</div>
          </div>
        </div>
        <p className="text-xs text-text-muted text-center">
          <strong>Use case:</strong> Context-aware loading states that match the current feature
        </p>
      </div>
    </PilotContainer>
  );
}

/**
 * Pilot 6: EmpathyError
 */
function EmpathyErrorPilot() {
  return (
    <PilotContainer
      title="EmpathyError"
      subtitle="Friendly error display with type-based messaging"
      fullWidth
    >
      <div className="space-y-4">
        <EmpathyError type="network" size="sm" />
        <EmpathyError type="timeout" size="sm" />
        <EmpathyError type="notfound" size="sm" />
        <p className="text-xs text-text-muted text-center pt-2">
          <strong>Principle:</strong> Errors should be empathetic, not alarming
        </p>
      </div>
    </PilotContainer>
  );
}

/**
 * Interactive Text Tokens - NEW!
 * Demo of the new token types: tables, code blocks, links, blockquotes, hr
 */
function InteractiveTextPilot() {
  const [sceneGraph, setSceneGraph] = useState<SceneGraph | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  // Demo markdown with all token types
  const demoMarkdown = `# Interactive Text Demo

> *"The spec is not description—it is generative."*

---

## Features Table

| Token | Description | Status |
|-------|-------------|--------|
| markdown_table | Structured data display | New! |
| code_block | Syntax-highlighted code | Fixed |
| link | Hyperlinks with preview | New! |
| blockquote | Quoted text blocks | New! |
| horizontal_rule | Section dividers | New! |

## Code Example

\`\`\`python
@semantic_token("agentese_path")
class AGENTESEPathToken:
    pattern = re.compile(r'\`world\\.path\`')
\`\`\`

## Links

Check out [the docs](https://docs.example.com) and [GitHub](https://github.com).

---

*Rendered with Interactive Text parser*
`;

  useEffect(() => {
    async function loadDemo() {
      try {
        setLoading(true);
        const result = await documentApi.parse(demoMarkdown, 'COMFORTABLE');
        setSceneGraph(result.scene_graph as SceneGraph);
      } catch (err) {
        setError(err instanceof Error ? err.message : 'Failed to parse');
      } finally {
        setLoading(false);
      }
    }
    loadDemo();
  }, [demoMarkdown]);

  return (
    <PilotContainer
      title="Interactive Text Tokens"
      subtitle="NEW: Tables, code blocks, links, blockquotes, horizontal rules"
      fullWidth
    >
      <div className="space-y-4">
        {loading ? (
          <div className="flex justify-center py-8">
            <PersonalityLoading jewel="brain" size="md" action="analyze" />
          </div>
        ) : error ? (
          <EmpathyError type="network" title="Parse Failed" subtitle={error} size="sm" />
        ) : sceneGraph ? (
          <div className="bg-surface-canvas rounded-lg p-4 border border-gray-700">
            <InteractiveDocument
              sceneGraph={sceneGraph}
              onNavigate={(path) => console.info('[Demo] Navigate to:', path)}
            />
          </div>
        ) : (
          <p className="text-text-muted text-sm">No content</p>
        )}
        <p className="text-xs text-text-muted text-center">
          <strong>Backend API:</strong> <code>POST /api/document/parse</code> →{' '}
          <strong>Frontend:</strong> <code>InteractiveDocument</code>
        </p>
      </div>
    </PilotContainer>
  );
}

/**
 * Pilot 7: Portal Token — Expandable Hyperedges
 * "The doc comes to you."
 */
function PortalPilot() {
  const demoDestinations = [
    {
      path: 'services/brain/core.py',
      title: 'Brain Core',
      preview: 'Memory crystallization service',
    },
    { path: 'services/witness/bus.py', title: 'Witness Bus', preview: 'Event streaming' },
    {
      path: 'services/k_block/cosmos.py',
      title: 'K-Block Cosmos',
      preview: 'Transactional editing',
      exists: true,
    },
  ];

  const missingDemos = [
    { path: 'services/brain/core.py', exists: true },
    { path: 'services/old/deprecated.py', exists: false, title: 'Deprecated Module' },
    { path: 'services/witness/tui.py', exists: true },
  ];

  return (
    <PilotContainer
      title="Portal Token"
      subtitle="Expandable hyperedges — 'The doc comes to you'"
      fullWidth
    >
      <div className="space-y-4">
        <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
          <div>
            <div className="text-xs text-text-muted mb-2">With previews:</div>
            <PortalToken
              edgeType="implements"
              destinations={demoDestinations}
              onNavigate={(path) => console.info('[Portal] Navigate to:', path)}
            />
          </div>
          <div>
            <div className="text-xs text-text-muted mb-2">With missing file:</div>
            <PortalToken
              edgeType="references"
              destinations={missingDemos}
              onNavigate={(path) => console.info('[Portal] Navigate to:', path)}
              defaultExpanded
            />
          </div>
        </div>
        <p className="text-xs text-text-muted text-center">
          <strong>Philosophy:</strong> Navigation without leaving context. Expand to preview, click
          to navigate.
        </p>
      </div>
    </PilotContainer>
  );
}

/**
 * Pilot 8: Principle Token — Architectural Decisions
 */
function PrinciplePilot() {
  return (
    <PilotContainer
      title="Principle Token"
      subtitle="Architectural principle references with hover tooltips"
      fullWidth
    >
      <div className="space-y-4">
        <div className="flex flex-wrap gap-3 justify-center">
          <PrincipleToken
            principle="AD-009"
            onClick={(p) => console.info('[Principle] Navigate to:', p)}
          />
          <PrincipleToken
            principle="Tasteful"
            onClick={(p) => console.info('[Principle] Navigate to:', p)}
          />
          <PrincipleToken
            principle="Composable"
            onClick={(p) => console.info('[Principle] Navigate to:', p)}
          />
          <PrincipleToken
            principle="Joy-Inducing"
            onClick={(p) => console.info('[Principle] Navigate to:', p)}
          />
        </div>
        <div className="flex flex-wrap gap-3 justify-center">
          <PrincipleToken
            principle="AD-008"
            title="Simplifying Isomorphisms"
            category="architectural"
            onClick={(p) => console.info('[Principle] Navigate to:', p)}
          />
          <PrincipleToken
            principle="Operational"
            title="Custom Principle"
            description="A custom operational principle with manual metadata."
            category="operational"
            onClick={(p) => console.info('[Principle] Navigate to:', p)}
          />
        </div>
        <p className="text-xs text-text-muted text-center">
          <strong>Color coding:</strong> Gold = architectural, Green = constitutional, Gray =
          operational
        </p>
      </div>
    </PilotContainer>
  );
}

/**
 * Pilot 9: Image Token — Images with AI Analysis
 */
function ImagePilot() {
  return (
    <PilotContainer title="Image Token" subtitle="Images with AI analysis on hover" fullWidth>
      <div className="space-y-4">
        <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
          <ImageToken
            src="https://via.placeholder.com/300x200/141418/6b8b6b?text=Diagram"
            alt="Architecture diagram"
            aiDescription="A system architecture diagram showing three layers: presentation, business logic, and data persistence. The layers are connected by bidirectional arrows indicating data flow."
            caption="System Architecture"
            onClick={(src) => console.info('[Image] View:', src)}
          />
          <ImageToken
            src="https://invalid-url.example/missing.png"
            alt="Missing image"
            onClick={(src) => console.info('[Image] View:', src)}
          />
        </div>
        <p className="text-xs text-text-muted text-center">
          <strong>Philosophy:</strong> Images are meaning tokens, not decoration. Hover to reveal
          semantic content.
        </p>
      </div>
    </PilotContainer>
  );
}

/**
 * Density Comparison - Same animations at different spacing
 */
function DensityComparisonPilot() {
  const densities = ['compact', 'comfortable', 'spacious'] as const;
  const [activeDensity, setActiveDensity] = useState<(typeof densities)[number]>('comfortable');

  const gapClasses: Record<(typeof densities)[number], string> = {
    compact: 'gap-2',
    comfortable: 'gap-4',
    spacious: 'gap-8',
  };

  const paddingClasses: Record<(typeof densities)[number], string> = {
    compact: 'p-2',
    comfortable: 'p-4',
    spacious: 'p-6',
  };

  return (
    <PilotContainer
      title="Density Modes"
      subtitle="Same components at different densities"
      fullWidth
    >
      <div className="space-y-4">
        {/* Density selector */}
        <div className="flex gap-2">
          {densities.map((density) => (
            <button
              key={density}
              onClick={() => setActiveDensity(density)}
              className={`
                px-3 py-1 rounded text-xs font-medium transition-all capitalize
                ${
                  activeDensity === density
                    ? 'bg-sage-600 text-white'
                    : 'bg-gray-800 text-gray-400 hover:bg-gray-700'
                }
              `}
            >
              {density}
            </button>
          ))}
        </div>

        {/* Content at selected density */}
        <div
          className={`rounded bg-surface-canvas border border-gray-700 ${paddingClasses[activeDensity]}`}
        >
          <div className={`flex ${gapClasses[activeDensity]} justify-center`}>
            <Breathe intensity={0.4}>
              <div className="w-12 h-12 rounded-full bg-sage-600" />
            </Breathe>
            <Breathe intensity={0.4}>
              <div className="w-12 h-12 rounded-lg bg-copper-600" />
            </Breathe>
            <Breathe intensity={0.4}>
              <div className="w-12 h-12 rounded-xl bg-slate-600" />
            </Breathe>
          </div>
        </div>

        {/* Density metrics */}
        <div className="text-xs text-text-muted grid grid-cols-3 gap-2">
          <div className="text-center">
            <div className="text-text-secondary">Gap</div>
            <div className="font-mono">
              {activeDensity === 'compact'
                ? '8px'
                : activeDensity === 'comfortable'
                  ? '16px'
                  : '32px'}
            </div>
          </div>
          <div className="text-center">
            <div className="text-text-secondary">Padding</div>
            <div className="font-mono">
              {activeDensity === 'compact'
                ? '8px'
                : activeDensity === 'comfortable'
                  ? '16px'
                  : '24px'}
            </div>
          </div>
          <div className="text-center">
            <div className="text-text-secondary">Mode</div>
            <div className="font-mono text-sage-400 capitalize">{activeDensity}</div>
          </div>
        </div>
      </div>
    </PilotContainer>
  );
}

// =============================================================================
// Main Page Component
// =============================================================================

export default function InteractiveTextGallery() {
  const { density } = useWindowLayout();

  return (
    <div className="h-[calc(100vh-64px)] flex flex-col bg-surface-canvas overflow-auto">
      {/* Header */}
      <div className="bg-sage-900/30 border-b border-sage-700/30 px-4 py-3">
        <div className="flex items-center justify-between">
          <div>
            <h1 className="text-lg font-semibold text-sage-100">Joy Animation Gallery</h1>
            <p className="text-sm text-sage-400/70">
              "Joy-inducing" — Delight in interaction, personality matters
            </p>
          </div>
          <div className="flex items-center gap-2">
            <span className="text-xs text-text-muted">Current density:</span>
            <span className="px-2 py-0.5 rounded text-xs bg-sage-800/50 text-sage-300 capitalize">
              {density}
            </span>
          </div>
        </div>
      </div>

      {/* Gallery content */}
      <div className="flex-1 overflow-auto p-6">
        <div className="max-w-6xl mx-auto space-y-8">
          {/* Breathing */}
          <section>
            <h2 className="text-sm font-semibold text-sage-300 uppercase tracking-wider mb-4">
              Organic Motion
            </h2>
            <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
              <BreathingPilot />
              <PopPilot />
            </div>
          </section>

          {/* Attention */}
          <section>
            <h2 className="text-sm font-semibold text-sage-300 uppercase tracking-wider mb-4">
              Attention & Feedback
            </h2>
            <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
              <ShakePilot />
              <ShimmerPilot />
            </div>
          </section>

          {/* Personality */}
          <section>
            <h2 className="text-sm font-semibold text-sage-300 uppercase tracking-wider mb-4">
              Personality & Empathy
            </h2>
            <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
              <PersonalityLoadingPilot />
              <EmpathyErrorPilot />
            </div>
          </section>

          {/* Interactive Text - NEW! */}
          <section>
            <h2 className="text-sm font-semibold text-copper-300 uppercase tracking-wider mb-4">
              Interactive Text Tokens
            </h2>
            <InteractiveTextPilot />
          </section>

          {/* SYNTHESIS-UI Tokens — NEW! */}
          <section>
            <h2 className="text-sm font-semibold text-copper-300 uppercase tracking-wider mb-4">
              SYNTHESIS-UI Tokens (Living Spec)
            </h2>
            <div className="space-y-6">
              <PortalPilot />
              <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                <PrinciplePilot />
                <ImagePilot />
              </div>
            </div>
          </section>

          {/* Density */}
          <section>
            <h2 className="text-sm font-semibold text-sage-300 uppercase tracking-wider mb-4">
              Density Adaptation
            </h2>
            <DensityComparisonPilot />
          </section>

          {/* Philosophy */}
          <section>
            <h2 className="text-sm font-semibold text-sage-300 uppercase tracking-wider mb-4">
              Design Philosophy
            </h2>
            <PilotContainer
              title="Joy-Inducing Principle"
              subtitle="From the kgents Constitution"
              fullWidth
            >
              <div className="prose prose-invert prose-sm max-w-none">
                <blockquote className="text-sage-300 border-l-sage-500">
                  <p>
                    <strong>Personality encouraged:</strong> Agents may have character (within
                    ethical bounds)
                  </p>
                  <p>
                    <strong>Surprise and serendipity welcome:</strong> Discovery should feel
                    rewarding
                  </p>
                  <p>
                    <strong>Warmth over coldness:</strong> Interaction should feel like
                    collaboration, not transaction
                  </p>
                  <p>
                    <strong>Humor when appropriate:</strong> Levity is valuable
                  </p>
                </blockquote>
                <p className="text-text-muted text-xs mt-4">
                  <strong>Anti-patterns:</strong> Robotic, lifeless responses; needless formality;
                  agents that feel like forms to fill out
                </p>
              </div>
            </PilotContainer>
          </section>
        </div>
      </div>
    </div>
  );
}
