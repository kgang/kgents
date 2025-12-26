/**
 * Analysis Components Stories
 *
 * STARK BIOME: "Analysis is not one thing but four."
 *
 * The Analysis Operad provides four complementary modes of understanding:
 *
 * | Mode         | Question                              | Icon | Pass Condition              |
 * |--------------|---------------------------------------|------|------------------------------|
 * | Categorical  | Does X satisfy its composition laws?  | (C)  | No FAILED law verifications  |
 * | Epistemic    | What layer is X? How is it justified? | (o)  | Grounding terminates at axiom|
 * | Dialectical  | What tensions exist? Are they resolved?| <=>  | No PROBLEMATIC tensions      |
 * | Generative   | Can X be regenerated from axioms?     | (*)  | Regeneration test passed     |
 *
 * ## Design Philosophy
 *
 * - **Four-Panel Grid**: Each mode occupies one quadrant for simultaneous view
 * - **Status at Glance**: Pass/fail icons in header, overall status in footer
 * - **Evidence Visible**: Summaries, chains, and metrics are always accessible
 * - **Coherence Score**: Overall validity requires ALL four modes passing
 */

import type { Meta, StoryObj } from '@storybook/react-vite';
import { CategoricalPanel } from './CategoricalPanel';
import { EpistemicPanel } from './EpistemicPanel';
import { DialecticalPanel } from './DialecticalPanel';
import { GenerativePanel } from './GenerativePanel';
import type {
  CategoricalReport,
  EpistemicReport,
  DialecticalReport,
  GenerativeReport,
  LawStatus,
  EvidenceTier,
  ContradictionType,
} from './useAnalysis';

// =============================================================================
// Meta
// =============================================================================

const meta: Meta = {
  title: 'Analysis/Four-Mode Operad',
  tags: ['autodocs'],
  parameters: {
    docs: {
      description: {
        component: `
# Analysis Operad

The Analysis Operad provides four complementary verification modes derived from
the kgents specification's "four modes of verification":

## The Four Modes

### Categorical (Top-Left)
**Question**: Does X satisfy its own composition laws?

Verifies that the target adheres to categorical laws (identity, associativity,
functoriality). Shows:
- Law verifications with PASSED/STRUCTURAL/FAILED/UNDECIDABLE status
- Fixed point analysis for self-referential structures
- Law count summary

### Epistemic (Top-Right)
**Question**: What layer is X? How is it justified?

Traces the epistemic grounding of claims through the seven-layer hierarchy.
Shows:
- Layer assignment (L1-L7)
- Evidence tier (Somatic, Aesthetic, Empirical, Categorical, Derived)
- Grounding chain with termination status

### Dialectical (Bottom-Left)
**Question**: What tensions exist? How are they resolved?

Identifies contradictions and their classifications. Shows:
- Tension count with breakdown (Productive vs Problematic)
- Thesis/antithesis pairs
- Resolution status

### Generative (Bottom-Right)
**Question**: Can X be regenerated from its axioms?

Tests if the target can be reconstructed from a minimal kernel. Shows:
- Compression ratio with quality indicator
- Minimal kernel axioms
- Regeneration test result

## STARK BIOME Design

- **Steel Frame**: \`steel-carbon\` panel backgrounds
- **Status Indicators**: Green checkmark for pass, red X for fail
- **Earned Glow**: Only valid states earn accent coloring
        `,
      },
    },
  },
};

export default meta;

// =============================================================================
// Mock Data Factories
// =============================================================================

function createCategoricalReport(overrides: Partial<CategoricalReport> = {}): CategoricalReport {
  return {
    target: 'spec/agents/k-gent.md',
    laws_extracted: [
      { name: 'Identity', equation: 'id . f = f = f . id', source: 'Category Theory', tier: 'CATEGORICAL' as EvidenceTier },
      { name: 'Associativity', equation: '(f . g) . h = f . (g . h)', source: 'Category Theory', tier: 'CATEGORICAL' as EvidenceTier },
      { name: 'Functoriality', equation: 'F(f . g) = F(f) . F(g)', source: 'Category Theory', tier: 'CATEGORICAL' as EvidenceTier },
    ],
    law_verifications: [
      { law_name: 'Identity', status: 'PASSED' as LawStatus, evidence: 'All identity compositions verified', passed: true },
      { law_name: 'Associativity', status: 'PASSED' as LawStatus, evidence: 'Composition is associative', passed: true },
      { law_name: 'Functoriality', status: 'PASSED' as LawStatus, evidence: 'Functor laws hold', passed: true },
    ],
    fixed_point: null,
    summary: 'All categorical laws verified. The structure is well-formed.',
    ...overrides,
  };
}

function createEpistemicReport(overrides: Partial<EpistemicReport> = {}): EpistemicReport {
  return {
    target: 'spec/agents/k-gent.md',
    layer: 4,
    toulmin: {
      claim: 'K-gent is the soul of the kgents system',
      grounds: ['Specification in spec/agents/k-gent.md', 'Implementation in services/soul/'],
      warrant: 'Documented specification with reference implementation',
      backing: 'Witnessed marks and evidence trail',
      qualifier: 'definitely',
      rebuttals: [],
      tier: 'EMPIRICAL' as EvidenceTier,
    },
    grounding: {
      steps: [
        [4, 'spec/agents/k-gent.md', 'defines'],
        [3, 'spec/protocols/witness.md', 'grounds'],
        [2, 'spec/principles/design.md', 'derives'],
        [1, 'spec/axioms/core.md', 'terminates'],
      ],
      terminates_at_axiom: true,
    },
    bootstrap: null,
    summary: 'Grounded through axiom chain. Layer 4 specification with empirical evidence.',
    ...overrides,
  };
}

function createDialecticalReport(overrides: Partial<DialecticalReport> = {}): DialecticalReport {
  return {
    target: 'spec/agents/k-gent.md',
    tensions: [
      {
        thesis: 'K-gent should be opinionated',
        antithesis: 'K-gent should be flexible',
        classification: 'PRODUCTIVE' as ContradictionType,
        synthesis: 'Opinionated defaults with escape hatches',
        is_resolved: true,
      },
      {
        thesis: 'Mirror the user faithfully',
        antithesis: 'Challenge the user constructively',
        classification: 'PRODUCTIVE' as ContradictionType,
        synthesis: 'Faithful mirror with dialectical prompts',
        is_resolved: true,
      },
    ],
    summary: 'Two productive tensions identified and resolved through synthesis.',
    ...overrides,
  };
}

function createGenerativeReport(overrides: Partial<GenerativeReport> = {}): GenerativeReport {
  return {
    target: 'spec/agents/k-gent.md',
    grammar: {
      primitives: ['PolyAgent', 'Operad', 'Sheaf'],
      operations: ['compose', 'parallel', 'sequential'],
      laws: ['identity', 'associativity', 'distributivity'],
    },
    compression_ratio: 0.25,
    regeneration: {
      axioms_used: ['Core Axiom 1', 'Core Axiom 2', 'Design Principle 3'],
      structures_regenerated: ['PolyAgent definition', 'Operad grammar', 'Crown Jewel interface'],
      missing_elements: [],
      passed: true,
    },
    minimal_kernel: [
      'The persona is a garden, not a museum',
      'Tasteful > feature-complete',
      'Agents are morphisms in a category',
      'Witness everything that matters',
    ],
    summary: 'Excellent compression (0.25). Fully regenerable from 4 axioms.',
    ...overrides,
  };
}

// =============================================================================
// Panel Style Wrapper
// =============================================================================

const PanelWrapper = ({ children }: { children: React.ReactNode }) => (
  <div
    style={{
      width: '350px',
      background: '#141418',
      borderRadius: '4px',
      border: '1px solid #28282F',
      overflow: 'hidden',
    }}
  >
    {children}
  </div>
);

// =============================================================================
// CategoricalPanel Stories
// =============================================================================

export const CategoricalAllPassing: StoryObj = {
  name: 'Categorical - All Laws Pass',
  render: () => (
    <PanelWrapper>
      <CategoricalPanel report={createCategoricalReport()} loading={false} />
    </PanelWrapper>
  ),
  parameters: {
    docs: {
      description: {
        story: `
All three categorical laws verified:
- **Identity**: \`id . f = f = f . id\`
- **Associativity**: \`(f . g) . h = f . (g . h)\`
- **Functoriality**: \`F(f . g) = F(f) . F(g)\`

Status shows green checkmark when no FAILED verifications.
        `,
      },
    },
  },
};

export const CategoricalWithFailures: StoryObj = {
  name: 'Categorical - Law Failures',
  render: () => (
    <PanelWrapper>
      <CategoricalPanel
        report={createCategoricalReport({
          law_verifications: [
            { law_name: 'Identity', status: 'PASSED' as LawStatus, evidence: 'Verified', passed: true },
            { law_name: 'Associativity', status: 'FAILED' as LawStatus, evidence: 'Composition order matters in imperative code', passed: false },
            { law_name: 'Functoriality', status: 'UNDECIDABLE' as LawStatus, evidence: 'Cannot verify without runtime', passed: false },
          ],
          summary: 'Associativity violation detected. Structure may have side effects.',
        })}
        loading={false}
      />
    </PanelWrapper>
  ),
  parameters: {
    docs: {
      description: {
        story: `
Mixed law verification results:
- **PASSED**: Law holds
- **FAILED**: Law violated (problematic)
- **UNDECIDABLE**: Cannot determine at analysis time

Status shows red X when any FAILED verification exists.
        `,
      },
    },
  },
};

export const CategoricalWithFixedPoint: StoryObj = {
  name: 'Categorical - Fixed Point Analysis',
  render: () => (
    <PanelWrapper>
      <CategoricalPanel
        report={createCategoricalReport({
          fixed_point: {
            is_self_referential: true,
            fixed_point_description: 'The witness protocol witnesses itself',
            is_valid: true,
            implications: ['Bootstrap paradox resolved', 'Self-description consistent'],
          },
          summary: 'All laws pass. Valid fixed point detected: self-witnessing protocol.',
        })}
        loading={false}
      />
    </PanelWrapper>
  ),
  parameters: {
    docs: {
      description: {
        story: `
When a structure references itself (like the witness protocol witnessing itself),
fixed point analysis determines if the self-reference is valid or paradoxical.

Shows the fixed point indicator with validation status.
        `,
      },
    },
  },
};

export const CategoricalLoading: StoryObj = {
  name: 'Categorical - Loading State',
  render: () => (
    <PanelWrapper>
      <CategoricalPanel report={null} loading={true} />
    </PanelWrapper>
  ),
};

// =============================================================================
// EpistemicPanel Stories
// =============================================================================

export const EpistemicGrounded: StoryObj = {
  name: 'Epistemic - Grounded at Axiom',
  render: () => (
    <PanelWrapper>
      <EpistemicPanel report={createEpistemicReport()} loading={false} />
    </PanelWrapper>
  ),
  parameters: {
    docs: {
      description: {
        story: `
The target is grounded through a chain that terminates at an axiom:

\`L4 (Spec) -> L3 (Protocol) -> L2 (Principle) -> L1 (Axiom)\`

Evidence tier is EMPIRICAL (observed and documented).
Anchor icon indicates successful grounding.
        `,
      },
    },
  },
};

export const EpistemicUngrounded: StoryObj = {
  name: 'Epistemic - Floating (Ungrounded)',
  render: () => (
    <PanelWrapper>
      <EpistemicPanel
        report={createEpistemicReport({
          layer: 6,
          grounding: {
            steps: [
              [6, 'impl/temp/experiment.py', 'implements'],
              [5, 'docs/notes/idea.md', 'references'],
            ],
            terminates_at_axiom: false,
          },
          summary: 'Warning: Floating structure. No axiom grounding found.',
        })}
        loading={false}
      />
    </PanelWrapper>
  ),
  parameters: {
    docs: {
      description: {
        story: `
An ungrounded structure has a grounding chain that does NOT terminate at an axiom.

Shows infinity icon instead of anchor.
Status is red X - floating structures are epistemically suspect.
        `,
      },
    },
  },
};

export const EpistemicHighLayer: StoryObj = {
  name: 'Epistemic - L7 Representation',
  render: () => (
    <PanelWrapper>
      <EpistemicPanel
        report={createEpistemicReport({
          layer: 7,
          toulmin: {
            claim: 'This is a UI representation of the K-gent',
            grounds: ['React component', 'Design system integration'],
            warrant: 'Implemented according to spec',
            backing: 'Type-checked and tested',
            qualifier: 'probably',
            rebuttals: ['UI may diverge from spec if not maintained'],
            tier: 'DERIVED' as EvidenceTier,
          },
          summary: 'Layer 7 representation with derived evidence.',
        })}
        loading={false}
      />
    </PanelWrapper>
  ),
  parameters: {
    docs: {
      description: {
        story: `
Layer 7 is the representation layer (UI, CLI, API).

Evidence tier is DERIVED (computed from other evidence).
Higher layers depend on grounding through lower layers.
        `,
      },
    },
  },
};

export const EpistemicLoading: StoryObj = {
  name: 'Epistemic - Loading State',
  render: () => (
    <PanelWrapper>
      <EpistemicPanel report={null} loading={true} />
    </PanelWrapper>
  ),
};

// =============================================================================
// DialecticalPanel Stories
// =============================================================================

export const DialecticalProductiveTensions: StoryObj = {
  name: 'Dialectical - Productive Tensions',
  render: () => (
    <PanelWrapper>
      <DialecticalPanel report={createDialecticalReport()} loading={false} />
    </PanelWrapper>
  ),
  parameters: {
    docs: {
      description: {
        story: `
Productive tensions are healthy contradictions that drive evolution.

Both tensions shown are:
- **Classified as PRODUCTIVE**: Drives design decisions
- **Resolved through synthesis**: Has a resolution

Status is green - no problematic tensions.
        `,
      },
    },
  },
};

export const DialecticalProblematicTensions: StoryObj = {
  name: 'Dialectical - Problematic Tensions',
  render: () => (
    <PanelWrapper>
      <DialecticalPanel
        report={createDialecticalReport({
          tensions: [
            {
              thesis: 'System should be fast',
              antithesis: 'System should be accurate',
              classification: 'PRODUCTIVE' as ContradictionType,
              synthesis: 'Fast by default, accurate on demand',
              is_resolved: true,
            },
            {
              thesis: 'All state is immutable',
              antithesis: 'Some state must mutate for performance',
              classification: 'PROBLEMATIC' as ContradictionType,
              synthesis: null,
              is_resolved: false,
            },
            {
              thesis: 'Specification is complete',
              antithesis: 'Implementation has undocumented features',
              classification: 'PROBLEMATIC' as ContradictionType,
              synthesis: null,
              is_resolved: false,
            },
          ],
          summary: 'Warning: 2 problematic tensions require resolution.',
        })}
        loading={false}
      />
    </PanelWrapper>
  ),
  parameters: {
    docs: {
      description: {
        story: `
Problematic tensions are unresolved contradictions that indicate issues:

| Type         | Meaning                              |
|--------------|--------------------------------------|
| APPARENT     | Seems contradictory but isn't        |
| PRODUCTIVE   | Healthy tension driving evolution    |
| PROBLEMATIC  | Unresolved issue needing attention   |
| PARACONSISTENT| Accepts both sides as true          |

Status is red X when any PROBLEMATIC tensions exist.
        `,
      },
    },
  },
};

export const DialecticalNoTensions: StoryObj = {
  name: 'Dialectical - No Tensions',
  render: () => (
    <PanelWrapper>
      <DialecticalPanel
        report={createDialecticalReport({
          tensions: [],
          summary: 'No tensions detected. Structure is internally consistent.',
        })}
        loading={false}
      />
    </PanelWrapper>
  ),
};

export const DialecticalLoading: StoryObj = {
  name: 'Dialectical - Loading State',
  render: () => (
    <PanelWrapper>
      <DialecticalPanel report={null} loading={true} />
    </PanelWrapper>
  ),
};

// =============================================================================
// GenerativePanel Stories
// =============================================================================

export const GenerativeExcellent: StoryObj = {
  name: 'Generative - Excellent Compression',
  render: () => (
    <PanelWrapper>
      <GenerativePanel report={createGenerativeReport()} loading={false} />
    </PanelWrapper>
  ),
  parameters: {
    docs: {
      description: {
        story: `
Excellent generative analysis:
- **Compression ratio**: 0.25 (excellent - colored green)
- **Minimal kernel**: 4 axioms
- **Regeneration**: PASSED

The structure can be fully regenerated from its axioms.
        `,
      },
    },
  },
};

export const GenerativeGood: StoryObj = {
  name: 'Generative - Good Compression',
  render: () => (
    <PanelWrapper>
      <GenerativePanel
        report={createGenerativeReport({
          compression_ratio: 0.55,
          minimal_kernel: [
            'Core principle 1',
            'Core principle 2',
            'Core principle 3',
            'Core principle 4',
            'Core principle 5',
            'Core principle 6',
          ],
          summary: 'Good compression (0.55). Regenerable from 6 axioms.',
        })}
        loading={false}
      />
    </PanelWrapper>
  ),
  parameters: {
    docs: {
      description: {
        story: `
Good compression (0.30 - 0.70):
- Requires more axioms than excellent
- Still fully regenerable
- Yellow-ish color indicator
        `,
      },
    },
  },
};

export const GenerativePoor: StoryObj = {
  name: 'Generative - Poor Compression (Failed)',
  render: () => (
    <PanelWrapper>
      <GenerativePanel
        report={createGenerativeReport({
          compression_ratio: 0.85,
          regeneration: {
            axioms_used: ['A1', 'A2', 'A3', 'A4', 'A5', 'A6', 'A7', 'A8'],
            structures_regenerated: ['PolyAgent', 'Operad'],
            missing_elements: ['Crown Jewel interface', 'Witness protocol bindings'],
            passed: false,
          },
          minimal_kernel: [
            'Axiom 1', 'Axiom 2', 'Axiom 3', 'Axiom 4',
            'Axiom 5', 'Axiom 6', 'Axiom 7', 'Axiom 8',
          ],
          summary: 'Poor compression (0.85). Missing elements prevent full regeneration.',
        })}
        loading={false}
      />
    </PanelWrapper>
  ),
  parameters: {
    docs: {
      description: {
        story: `
Poor generative analysis:
- **Compression ratio**: 0.85 (poor - colored red)
- **Missing elements**: Cannot fully regenerate
- **Regeneration**: FAILED

Indicates the structure has grown beyond its axiomatic foundation.
        `,
      },
    },
  },
};

export const GenerativeLoading: StoryObj = {
  name: 'Generative - Loading State',
  render: () => (
    <PanelWrapper>
      <GenerativePanel report={null} loading={true} />
    </PanelWrapper>
  ),
};

// =============================================================================
// Full Quadrant Stories
// =============================================================================

const QuadrantGrid = ({ children }: { children: React.ReactNode }) => (
  <div
    style={{
      display: 'grid',
      gridTemplateColumns: 'repeat(2, 1fr)',
      gap: '8px',
      background: '#141418',
      padding: '16px',
      borderRadius: '8px',
      border: '1px solid #28282F',
      maxWidth: '800px',
    }}
  >
    {children}
  </div>
);

export const QuadrantAllPassing: StoryObj = {
  name: 'Full Quadrant - All Modes Pass',
  render: () => (
    <QuadrantGrid>
      <CategoricalPanel report={createCategoricalReport()} loading={false} />
      <EpistemicPanel report={createEpistemicReport()} loading={false} />
      <DialecticalPanel report={createDialecticalReport()} loading={false} />
      <GenerativePanel report={createGenerativeReport()} loading={false} />
    </QuadrantGrid>
  ),
  parameters: {
    docs: {
      description: {
        story: `
Complete four-mode analysis with all modes passing:

| Mode        | Status | Key Finding                    |
|-------------|--------|--------------------------------|
| Categorical | PASS   | 3/3 laws verified              |
| Epistemic   | PASS   | Grounded at L1 axiom           |
| Dialectical | PASS   | 2 productive tensions resolved |
| Generative  | PASS   | 0.25 compression, regenerable  |

**Overall**: Structure is coherent, grounded, and generative.
        `,
      },
    },
  },
};

export const QuadrantMixedResults: StoryObj = {
  name: 'Full Quadrant - Mixed Results',
  render: () => (
    <QuadrantGrid>
      <CategoricalPanel
        report={createCategoricalReport({
          law_verifications: [
            { law_name: 'Identity', status: 'PASSED' as LawStatus, evidence: 'OK', passed: true },
            { law_name: 'Associativity', status: 'FAILED' as LawStatus, evidence: 'Violation found', passed: false },
          ],
          summary: 'Associativity violation detected.',
        })}
        loading={false}
      />
      <EpistemicPanel report={createEpistemicReport()} loading={false} />
      <DialecticalPanel
        report={createDialecticalReport({
          tensions: [
            {
              thesis: 'A',
              antithesis: 'B',
              classification: 'PROBLEMATIC' as ContradictionType,
              synthesis: null,
              is_resolved: false,
            },
          ],
          summary: 'Unresolved tension.',
        })}
        loading={false}
      />
      <GenerativePanel report={createGenerativeReport()} loading={false} />
    </QuadrantGrid>
  ),
  parameters: {
    docs: {
      description: {
        story: `
Mixed analysis results - some modes passing, some failing:

| Mode        | Status | Issue                          |
|-------------|--------|--------------------------------|
| Categorical | FAIL   | Associativity violated         |
| Epistemic   | PASS   | -                              |
| Dialectical | FAIL   | Unresolved problematic tension |
| Generative  | PASS   | -                              |

**Overall**: Structure needs attention. Two modes require remediation.
        `,
      },
    },
  },
};

export const QuadrantLoading: StoryObj = {
  name: 'Full Quadrant - Loading State',
  render: () => (
    <QuadrantGrid>
      <CategoricalPanel report={null} loading={true} />
      <EpistemicPanel report={null} loading={true} />
      <DialecticalPanel report={null} loading={true} />
      <GenerativePanel report={null} loading={true} />
    </QuadrantGrid>
  ),
};

// =============================================================================
// Philosophy Story
// =============================================================================

export const PhilosophyOverview: StoryObj = {
  name: 'Analysis Philosophy',
  render: () => (
    <div style={{ padding: '32px', background: '#141418', maxWidth: '800px' }}>
      <h2 style={{ color: '#E5E7EB', marginBottom: '24px' }}>
        The Four Modes of Verification
      </h2>
      <div style={{ color: '#9CA3AF', lineHeight: 1.7 }}>
        <p style={{ marginBottom: '16px', fontSize: '18px', color: '#C4A77D' }}>
          "Analysis is not one thing but four: verification of laws, grounding of claims,
          resolution of tensions, and regeneration from axioms."
        </p>

        <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '24px', marginTop: '24px' }}>
          <div>
            <h3 style={{ color: '#6cf', marginBottom: '8px' }}>Categorical</h3>
            <p style={{ fontSize: '14px' }}>
              Does the structure obey composition laws? A system that violates
              categorical laws is incoherent at its foundation.
            </p>
          </div>
          <div>
            <h3 style={{ color: '#22c55e', marginBottom: '8px' }}>Epistemic</h3>
            <p style={{ fontSize: '14px' }}>
              Is the claim grounded through justification chains that terminate
              at axioms? Floating claims are epistemically suspect.
            </p>
          </div>
          <div>
            <h3 style={{ color: '#f97316', marginBottom: '8px' }}>Dialectical</h3>
            <p style={{ fontSize: '14px' }}>
              What tensions exist? Productive tensions drive evolution.
              Problematic tensions indicate unresolved conflicts.
            </p>
          </div>
          <div>
            <h3 style={{ color: '#a855f7', marginBottom: '8px' }}>Generative</h3>
            <p style={{ fontSize: '14px' }}>
              Can the structure be regenerated from a minimal kernel?
              High compression indicates a well-founded abstraction.
            </p>
          </div>
        </div>

        <div style={{ marginTop: '32px', padding: '16px', background: '#1a1a1f', borderRadius: '4px' }}>
          <h3 style={{ color: '#E5E7EB', marginBottom: '12px' }}>Coherence Score</h3>
          <p style={{ fontSize: '14px' }}>
            A structure is <strong style={{ color: '#22c55e' }}>coherent</strong> when all four modes pass:
          </p>
          <ul style={{ paddingLeft: '20px', marginTop: '8px', fontSize: '14px' }}>
            <li>No FAILED categorical law verifications</li>
            <li>Grounding chain terminates at axiom</li>
            <li>No PROBLEMATIC unresolved tensions</li>
            <li>Regeneration test passes</li>
          </ul>
        </div>
      </div>
    </div>
  ),
  parameters: {
    layout: 'centered',
    docs: {
      description: {
        story: 'The philosophical foundation of the four-mode analysis operad.',
      },
    },
  },
};
