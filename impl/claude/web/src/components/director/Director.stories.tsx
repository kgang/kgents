/**
 * Director Component Stories
 *
 * STARK BIOME Design System Demo
 *
 * These stories showcase the Document Director components:
 * - DirectorDashboard: Three-column master-detail document viewer
 * - DocumentTable: Sortable, filterable document list
 * - DocumentDetail: Full document analysis view
 * - CaptureDialog: Execution results capture modal
 *
 * Philosophy: "The canvas breathes. Documents arrive, analyze, become ready."
 */

import type { Meta, StoryObj } from '@storybook/react-vite';
import { useState } from 'react';
import { CaptureDialog } from './CaptureDialog';
import { DocumentStatusBadge } from './DocumentStatus';
import type { DocumentEntry, DocumentStatus, DocumentDetail as DocumentDetailType, ClaimDetail, EvidenceMark } from '../../api/director';

// Import component CSS
import './DocumentTable.css';
import './DocumentDetail.css';
import './CaptureDialog.css';
import './DocumentStatus.css';

// =============================================================================
// Mock Data - Documents
// =============================================================================

const now = new Date();
const oneHourAgo = new Date(now.getTime() - 60 * 60 * 1000).toISOString();
const oneDayAgo = new Date(now.getTime() - 24 * 60 * 60 * 1000).toISOString();
const threeDaysAgo = new Date(now.getTime() - 3 * 24 * 60 * 60 * 1000).toISOString();
const oneWeekAgo = new Date(now.getTime() - 7 * 24 * 60 * 60 * 1000).toISOString();

/** Sample documents in various workflow states */
const mockDocuments: DocumentEntry[] = [
  {
    path: 'spec/protocols/agentese.md',
    title: 'AGENTESE Protocol',
    status: 'ready',
    version: 3,
    word_count: 2450,
    claim_count: 24,
    impl_count: 18,
    test_count: 12,
    placeholder_count: 2,
    analyzed_at: oneHourAgo,
    uploaded_at: oneDayAgo,
  },
  {
    path: 'spec/protocols/witness.md',
    title: 'Witness Service',
    status: 'ready',
    version: 2,
    word_count: 1890,
    claim_count: 18,
    impl_count: 14,
    test_count: 9,
    placeholder_count: 0,
    analyzed_at: oneHourAgo,
    uploaded_at: oneDayAgo,
  },
  {
    path: 'spec/agents/polynomial.md',
    title: 'PolyAgent Core',
    status: 'executed',
    version: 5,
    word_count: 3200,
    claim_count: 32,
    impl_count: 28,
    test_count: 24,
    placeholder_count: 0,
    analyzed_at: threeDaysAgo,
    uploaded_at: oneWeekAgo,
  },
  {
    path: 'spec/protocols/zero-seed.md',
    title: 'Zero Seed Protocol',
    status: 'processing',
    version: 1,
    word_count: 1200,
    claim_count: 0,
    impl_count: 0,
    test_count: 0,
    placeholder_count: 0,
    analyzed_at: null,
    uploaded_at: now.toISOString(),
  },
  {
    path: 'spec/services/director.md',
    title: 'Document Director',
    status: 'uploaded',
    version: 1,
    word_count: 890,
    claim_count: 0,
    impl_count: 0,
    test_count: 0,
    placeholder_count: 0,
    analyzed_at: null,
    uploaded_at: now.toISOString(),
  },
  {
    path: 'spec/old/deprecated-api.md',
    title: 'Deprecated API',
    status: 'stale',
    version: 8,
    word_count: 450,
    claim_count: 6,
    impl_count: 2,
    test_count: 0,
    placeholder_count: 4,
    analyzed_at: oneWeekAgo,
    uploaded_at: oneWeekAgo,
  },
  {
    path: 'spec/broken/invalid.md',
    title: 'Invalid Spec',
    status: 'failed',
    version: 1,
    word_count: 120,
    claim_count: 0,
    impl_count: 0,
    test_count: 0,
    placeholder_count: 0,
    analyzed_at: oneHourAgo,
    uploaded_at: oneHourAgo,
  },
  {
    path: 'spec/referenced/missing-impl.md',
    title: 'Missing Implementation',
    status: 'ghost',
    version: 0,
    word_count: 0,
    claim_count: 0,
    impl_count: 0,
    test_count: 0,
    placeholder_count: 0,
    analyzed_at: null,
    uploaded_at: null,
    is_ghost: true,
    ghost_metadata: {
      origin: 'parsed_reference',
      created_by_path: 'spec/protocols/agentese.md',
      created_at: oneHourAgo,
      context: 'Referenced in AGENTESE spec but file does not exist',
      user_content: '',
      is_empty: true,
      has_draft_content: false,
    },
  },
];

/** Sample claims for document detail */
const mockClaims: ClaimDetail[] = [
  { type: 'MUST', subject: 'AGENTESE paths', predicate: 'be places, not just identifiers', line: 42 },
  { type: 'SHOULD', subject: 'Observer', predicate: 'receive umwelt-specific projections', line: 58 },
  { type: 'MUST', subject: 'Node registration', predicate: 'happen at import time via @node decorator', line: 89 },
  { type: 'SHALL', subject: 'Context discovery', predicate: 'walk up the hierarchy', line: 112 },
  { type: 'MAY', subject: 'Caching', predicate: 'be enabled for repeated traversals', line: 145 },
];

/** Sample evidence marks */
const mockEvidenceMarks: EvidenceMark[] = [
  {
    mark_id: 'mark-001',
    action: 'Implemented @node decorator with import-time registration',
    reasoning: 'Ensures nodes are discoverable before invocation',
    author: 'claude',
    timestamp: oneHourAgo,
    tags: ['implementation', 'agentese'],
  },
  {
    mark_id: 'mark-002',
    action: 'Added gateway._import_node_modules() to ensure registration',
    reasoning: 'Fixed node discovery issue where modules were not imported',
    author: 'kent',
    timestamp: oneHourAgo,
    tags: ['fix', 'discovery'],
  },
];

/** Full document detail mock */
const mockDocumentDetail: DocumentDetailType = {
  path: 'spec/protocols/agentese.md',
  title: 'AGENTESE Protocol',
  status: 'ready',
  uploaded_at: oneDayAgo,
  analyzed_at: oneHourAgo,
  analysis: {
    entity_path: 'spec/protocols/agentese.md',
    analyzed_at: oneHourAgo,
    title: 'AGENTESE Protocol',
    word_count: 2450,
    heading_count: 8,
    claims: mockClaims,
    discovered_refs: [
      'impl/claude/protocols/agentese/gateway.py',
      'impl/claude/protocols/agentese/node.py',
      'impl/claude/protocols/agentese/contexts/',
    ],
    implementations: [
      'protocols/agentese/gateway.py',
      'protocols/agentese/node.py',
    ],
    tests: [
      'protocols/agentese/_tests/test_gateway.py',
      'protocols/agentese/_tests/test_node.py',
    ],
    spec_refs: [
      'spec/agents/polynomial.md',
      'spec/protocols/witness.md',
    ],
    placeholder_paths: [
      'impl/claude/protocols/agentese/jit.py',
      'impl/claude/protocols/agentese/cache.py',
    ],
    anticipated: [
      {
        path: 'impl/claude/protocols/agentese/jit.py',
        type: 'python',
        spec_line: 145,
        context: 'JIT compilation for AGENTESE paths',
        owner: null,
        phase: 'Phase 3',
      },
    ],
    status: 'analyzed',
    error: null,
  },
  evidence_marks: mockEvidenceMarks,
};

// =============================================================================
// DocumentStatusBadge Stories
// =============================================================================

const statusMeta: Meta<typeof DocumentStatusBadge> = {
  title: 'Components/Director/DocumentStatusBadge',
  component: DocumentStatusBadge,
  tags: ['autodocs'],
  parameters: {
    docs: {
      description: {
        component: `
## DocumentStatusBadge - Status Indicator

Visual indicator for document lifecycle status.

**Statuses:**
- **Uploaded** (blue): Document received, awaiting analysis
- **Processing** (yellow, spinning): Analysis in progress
- **Ready** (green): Analysis complete, ready for execution
- **Executed** (purple): Implementation generated
- **Stale** (orange): Needs re-analysis
- **Failed** (red): Analysis failed
- **Ghost** (gray): Referenced but not uploaded

**STARK BIOME Design:**
- Status-specific accent colors
- Spinning icon for processing state
- Minimal footprint with clear meaning
        `,
      },
    },
  },
};

export default statusMeta;

type StatusStory = StoryObj<typeof DocumentStatusBadge>;

export const AllStatuses: StatusStory = {
  name: 'All Status Variants',
  render: () => (
    <div style={{ display: 'flex', flexDirection: 'column', gap: '12px' }}>
      {(['uploaded', 'processing', 'ready', 'executed', 'stale', 'failed', 'ghost'] as DocumentStatus[]).map((status) => (
        <div key={status} style={{ display: 'flex', alignItems: 'center', gap: '16px' }}>
          <span style={{ color: '#8A8A94', fontSize: '12px', width: '80px', textTransform: 'capitalize' }}>
            {status}
          </span>
          <DocumentStatusBadge status={status} />
          <DocumentStatusBadge status={status} size="sm" />
        </div>
      ))}
    </div>
  ),
  parameters: {
    docs: {
      description: {
        story: 'All seven status variants in both md and sm sizes.',
      },
    },
  },
};

export const StatusUploaded: StatusStory = {
  name: 'Uploaded',
  args: { status: 'uploaded' },
};

export const StatusProcessing: StatusStory = {
  name: 'Processing (Animated)',
  args: { status: 'processing' },
  parameters: {
    docs: {
      description: {
        story: 'Processing status shows a spinning icon to indicate active analysis.',
      },
    },
  },
};

export const StatusReady: StatusStory = {
  name: 'Ready',
  args: { status: 'ready' },
};

export const StatusGhost: StatusStory = {
  name: 'Ghost',
  args: { status: 'ghost' },
  parameters: {
    docs: {
      description: {
        story: 'Ghost status for referenced-but-missing documents. The negative space of the graph.',
      },
    },
  },
};

// =============================================================================
// DocumentTable Stories
// =============================================================================

export const TableDefault: StoryObj = {
  name: 'Document Table - Default',
  render: () => (
    <div style={{ height: '500px', background: '#0A0A0C', padding: '16px' }}>
      <div
        style={{
          height: '100%',
          background: '#141418',
          borderRadius: '4px',
          overflow: 'hidden',
        }}
      >
        {/* Mock table since real component needs API */}
        <div style={{ padding: '16px' }}>
          <div style={{ display: 'flex', gap: '12px', marginBottom: '16px' }}>
            <select
              style={{
                background: '#1C1C22',
                border: '1px solid #28282F',
                borderRadius: '4px',
                color: '#E5E7EB',
                padding: '8px 12px',
                fontSize: '13px',
              }}
            >
              <option>All Documents</option>
              <option>Uploaded</option>
              <option>Processing</option>
              <option>Ready</option>
              <option>Executed</option>
              <option>Stale</option>
              <option>Failed</option>
            </select>
            <input
              type="text"
              placeholder="Search documents..."
              style={{
                background: '#1C1C22',
                border: '1px solid #28282F',
                borderRadius: '4px',
                color: '#E5E7EB',
                padding: '8px 12px',
                fontSize: '13px',
                flex: 1,
              }}
            />
            <span style={{ color: '#8A8A94', fontSize: '12px', alignSelf: 'center' }}>
              {mockDocuments.length} documents
            </span>
          </div>

          <table style={{ width: '100%', borderCollapse: 'collapse' }}>
            <thead>
              <tr style={{ borderBottom: '1px solid #28282F' }}>
                <th style={{ padding: '8px', textAlign: 'left', color: '#8A8A94', fontSize: '11px', textTransform: 'uppercase' }}>Path</th>
                <th style={{ padding: '8px', textAlign: 'left', color: '#8A8A94', fontSize: '11px', textTransform: 'uppercase' }}>Status</th>
                <th style={{ padding: '8px', textAlign: 'right', color: '#8A8A94', fontSize: '11px', textTransform: 'uppercase' }}>Claims</th>
                <th style={{ padding: '8px', textAlign: 'right', color: '#8A8A94', fontSize: '11px', textTransform: 'uppercase' }}>Refs</th>
                <th style={{ padding: '8px', textAlign: 'left', color: '#8A8A94', fontSize: '11px', textTransform: 'uppercase' }}>Actions</th>
              </tr>
            </thead>
            <tbody>
              {mockDocuments.slice(0, 6).map((doc) => (
                <tr key={doc.path} style={{ borderBottom: '1px solid #1C1C22' }}>
                  <td style={{ padding: '12px 8px' }}>
                    <div style={{ color: '#E5E7EB', fontSize: '13px' }}>{doc.title}</div>
                    <div style={{ color: '#8A8A94', fontSize: '11px' }}>{doc.path}</div>
                  </td>
                  <td style={{ padding: '12px 8px' }}>
                    <DocumentStatusBadge status={doc.status} size="sm" />
                  </td>
                  <td style={{ padding: '12px 8px', textAlign: 'right', color: '#E5E7EB', fontSize: '13px' }}>
                    {doc.claim_count ?? 0}
                  </td>
                  <td style={{ padding: '12px 8px', textAlign: 'right', color: '#10B981', fontSize: '13px' }}>
                    {(doc.impl_count ?? 0) + (doc.test_count ?? 0)}
                  </td>
                  <td style={{ padding: '12px 8px' }}>
                    <button
                      style={{
                        background: '#28282F',
                        border: 'none',
                        borderRadius: '4px',
                        color: '#E5E7EB',
                        padding: '4px 8px',
                        fontSize: '11px',
                        cursor: 'pointer',
                      }}
                    >
                      View
                    </button>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </div>
    </div>
  ),
  parameters: {
    layout: 'fullscreen',
    docs: {
      description: {
        story: 'Document table with sorting, filtering, and action buttons. Shows documents in various workflow states.',
      },
    },
  },
};

export const TableEmpty: StoryObj = {
  name: 'Document Table - Empty',
  render: () => (
    <div
      style={{
        display: 'flex',
        flexDirection: 'column',
        alignItems: 'center',
        justifyContent: 'center',
        height: '300px',
        background: '#141418',
        borderRadius: '4px',
        padding: '48px',
      }}
    >
      <span style={{ fontSize: '32px', marginBottom: '16px' }}>
        &#128196;
      </span>
      <h3 style={{ color: '#E5E7EB', margin: '0 0 8px 0', fontSize: '16px' }}>
        No documents yet
      </h3>
      <p style={{ color: '#8A8A94', margin: '0 0 24px 0', fontSize: '13px' }}>
        Upload documents to get started.
      </p>
      <button
        style={{
          background: '#10B981',
          border: 'none',
          borderRadius: '4px',
          color: '#0A0A0C',
          padding: '10px 20px',
          fontSize: '13px',
          fontWeight: 500,
          cursor: 'pointer',
        }}
      >
        Upload First Document
      </button>
    </div>
  ),
  parameters: {
    docs: {
      description: {
        story: 'Empty state when no documents have been uploaded.',
      },
    },
  },
};

export const TableLoading: StoryObj = {
  name: 'Document Table - Loading',
  render: () => (
    <div
      style={{
        display: 'flex',
        alignItems: 'center',
        justifyContent: 'center',
        height: '200px',
        background: '#141418',
        borderRadius: '4px',
        color: '#8A8A94',
        fontSize: '13px',
      }}
    >
      Loading...
    </div>
  ),
  parameters: {
    docs: {
      description: {
        story: 'Loading state while fetching documents.',
      },
    },
  },
};

// =============================================================================
// DocumentDetail Stories
// =============================================================================

export const DetailReady: StoryObj = {
  name: 'Document Detail - Ready',
  render: () => (
    <div
      style={{
        maxWidth: '800px',
        background: '#141418',
        borderRadius: '4px',
        padding: '24px',
      }}
    >
      {/* Header */}
      <div style={{ display: 'flex', alignItems: 'center', gap: '16px', marginBottom: '16px' }}>
        <button
          style={{
            background: 'transparent',
            border: 'none',
            color: '#8A8A94',
            fontSize: '14px',
            cursor: 'pointer',
          }}
        >
          &larr; Back
        </button>
        <button
          style={{
            background: 'transparent',
            border: '1px solid #28282F',
            borderRadius: '4px',
            color: '#8A8A94',
            padding: '4px 8px',
            fontSize: '12px',
            cursor: 'pointer',
          }}
        >
          &#9000; Edit
        </button>
      </div>

      <div style={{ display: 'flex', alignItems: 'center', gap: '12px', marginBottom: '8px' }}>
        <h1 style={{ color: '#E5E7EB', fontSize: '20px', margin: 0 }}>
          {mockDocumentDetail.title}
        </h1>
        <DocumentStatusBadge status={mockDocumentDetail.status} />
      </div>

      <p style={{ color: '#8A8A94', fontSize: '12px', margin: '0 0 24px 0' }}>
        {mockDocumentDetail.path}
      </p>

      {/* Stats */}
      <div style={{ display: 'grid', gridTemplateColumns: 'repeat(4, 1fr)', gap: '12px', marginBottom: '24px' }}>
        {[
          { label: 'Claims', value: mockDocumentDetail.analysis?.claims.length ?? 0 },
          { label: 'Refs', value: mockDocumentDetail.analysis?.discovered_refs.length ?? 0 },
          { label: 'Placeholders', value: mockDocumentDetail.analysis?.placeholder_paths.length ?? 0 },
          { label: 'Evidence', value: mockDocumentDetail.evidence_marks.length },
        ].map((stat) => (
          <div
            key={stat.label}
            style={{
              background: '#1C1C22',
              borderRadius: '4px',
              padding: '12px',
              textAlign: 'center',
            }}
          >
            <div style={{ color: '#E5E7EB', fontSize: '20px', fontWeight: 600 }}>
              {stat.value}
            </div>
            <div style={{ color: '#8A8A94', fontSize: '11px', textTransform: 'uppercase' }}>
              {stat.label}
            </div>
          </div>
        ))}
      </div>

      {/* Actions */}
      <div style={{ marginBottom: '24px' }}>
        <button
          style={{
            background: '#8B5CF6',
            border: 'none',
            borderRadius: '4px',
            color: '#FFFFFF',
            padding: '10px 20px',
            fontSize: '13px',
            fontWeight: 500,
            cursor: 'pointer',
          }}
        >
          Generate Prompt
        </button>
      </div>

      {/* Claims Section */}
      <section style={{ marginBottom: '24px' }}>
        <h2 style={{ color: '#8A8A94', fontSize: '11px', textTransform: 'uppercase', letterSpacing: '0.05em', margin: '0 0 12px 0' }}>
          CLAIMS
        </h2>
        <ul style={{ listStyle: 'none', margin: 0, padding: 0 }}>
          {mockClaims.map((claim, i) => (
            <li
              key={i}
              style={{
                display: 'flex',
                alignItems: 'center',
                gap: '8px',
                padding: '8px 0',
                borderBottom: '1px solid #1C1C22',
              }}
            >
              <span
                style={{
                  background: claim.type === 'MUST' ? '#EF4444' : claim.type === 'SHOULD' ? '#F59E0B' : '#8A8A94',
                  color: '#0A0A0C',
                  fontSize: '10px',
                  fontWeight: 600,
                  padding: '2px 6px',
                  borderRadius: '2px',
                }}
              >
                {claim.type}
              </span>
              <span style={{ color: '#E5E7EB', fontSize: '13px' }}>
                {claim.subject}
              </span>
              <span style={{ color: '#8A8A94', fontSize: '13px' }}>
                {claim.predicate}
              </span>
              <span style={{ color: '#6B7280', fontSize: '11px', marginLeft: 'auto' }}>
                L{claim.line}
              </span>
            </li>
          ))}
        </ul>
      </section>

      {/* Evidence Section */}
      <section>
        <h2 style={{ color: '#8A8A94', fontSize: '11px', textTransform: 'uppercase', letterSpacing: '0.05em', margin: '0 0 12px 0' }}>
          EVIDENCE MARKS
        </h2>
        <ul style={{ listStyle: 'none', margin: 0, padding: 0 }}>
          {mockEvidenceMarks.map((mark) => (
            <li
              key={mark.mark_id}
              style={{
                background: '#1C1C22',
                borderRadius: '4px',
                padding: '12px',
                marginBottom: '8px',
              }}
            >
              <div style={{ color: '#E5E7EB', fontSize: '13px', marginBottom: '4px' }}>
                {mark.action}
              </div>
              <div style={{ display: 'flex', gap: '12px', fontSize: '11px', color: '#8A8A94' }}>
                <span>{mark.author}</span>
                <span>{mark.timestamp ? new Date(mark.timestamp).toLocaleString() : ''}</span>
              </div>
            </li>
          ))}
        </ul>
      </section>
    </div>
  ),
  parameters: {
    docs: {
      description: {
        story: 'Document detail view for a Ready document showing claims, references, and evidence marks.',
      },
    },
  },
};

export const DetailFirstView: StoryObj = {
  name: 'Document Detail - First View Modal',
  render: () => (
    <div
      style={{
        position: 'relative',
        height: '500px',
        background: '#0A0A0C',
        display: 'flex',
        alignItems: 'center',
        justifyContent: 'center',
      }}
    >
      {/* Modal Overlay */}
      <div
        style={{
          position: 'absolute',
          inset: 0,
          background: 'rgba(10, 10, 12, 0.85)',
          display: 'flex',
          alignItems: 'center',
          justifyContent: 'center',
        }}
      >
        {/* Modal */}
        <div
          style={{
            background: '#141418',
            border: '1px solid #28282F',
            borderRadius: '8px',
            padding: '32px',
            maxWidth: '400px',
            textAlign: 'center',
          }}
        >
          <div style={{ fontSize: '24px', color: '#10B981', marginBottom: '16px' }}>
            &#10023;
          </div>
          <h3 style={{ color: '#E5E7EB', fontSize: '18px', margin: '0 0 8px 0' }}>
            Analysis Complete
          </h3>
          <p style={{ color: '#8A8A94', fontSize: '13px', margin: '0 0 24px 0' }}>
            Here&apos;s what was extracted from <strong style={{ color: '#E5E7EB' }}>AGENTESE Protocol</strong>
          </p>

          <div style={{ display: 'grid', gridTemplateColumns: 'repeat(4, 1fr)', gap: '8px', marginBottom: '24px' }}>
            {[
              { label: 'Claims', value: 24 },
              { label: 'References', value: 12 },
              { label: 'Anticipated', value: 3 },
              { label: 'Placeholders', value: 2 },
            ].map((stat) => (
              <div key={stat.label}>
                <div style={{ color: '#10B981', fontSize: '20px', fontWeight: 600 }}>
                  {stat.value}
                </div>
                <div style={{ color: '#8A8A94', fontSize: '10px', textTransform: 'uppercase' }}>
                  {stat.label}
                </div>
              </div>
            ))}
          </div>

          <div style={{ marginBottom: '24px', textAlign: 'left' }}>
            <h4 style={{ color: '#8A8A94', fontSize: '10px', textTransform: 'uppercase', margin: '0 0 8px 0' }}>
              Claim Types
            </h4>
            <div style={{ display: 'flex', gap: '8px', flexWrap: 'wrap' }}>
              <span style={{ color: '#EF4444', fontSize: '12px' }}>MUST: 8</span>
              <span style={{ color: '#F59E0B', fontSize: '12px' }}>SHOULD: 10</span>
              <span style={{ color: '#8A8A94', fontSize: '12px' }}>MAY: 6</span>
            </div>
          </div>

          <button
            style={{
              background: '#28282F',
              border: 'none',
              borderRadius: '4px',
              color: '#E5E7EB',
              padding: '10px 24px',
              fontSize: '13px',
              cursor: 'pointer',
            }}
          >
            Got it
          </button>
        </div>
      </div>
    </div>
  ),
  parameters: {
    layout: 'fullscreen',
    docs: {
      description: {
        story: 'First-view modal shown when opening a document for the first time after analysis.',
      },
    },
  },
};

export const DetailProcessing: StoryObj = {
  name: 'Document Detail - Processing',
  render: () => (
    <div
      style={{
        maxWidth: '600px',
        background: '#141418',
        borderRadius: '4px',
        padding: '48px',
        textAlign: 'center',
      }}
    >
      <div
        style={{
          fontSize: '32px',
          marginBottom: '16px',
          animation: 'spin 1s linear infinite',
        }}
      >
        &#8635;
      </div>
      <h2 style={{ color: '#E5E7EB', fontSize: '16px', margin: '0 0 8px 0' }}>
        Analyzing Document
      </h2>
      <p style={{ color: '#8A8A94', fontSize: '13px', margin: 0 }}>
        Extracting claims, references, and implementations...
      </p>
      <style>
        {`@keyframes spin { from { transform: rotate(0deg); } to { transform: rotate(360deg); } }`}
      </style>
    </div>
  ),
  parameters: {
    docs: {
      description: {
        story: 'Detail view during document analysis.',
      },
    },
  },
};

// =============================================================================
// CaptureDialog Stories
// =============================================================================

export const CaptureDefault: StoryObj = {
  name: 'Capture Dialog - Default',
  render: () => {
    const [showDialog, setShowDialog] = useState(true);

    if (!showDialog) {
      return (
        <button
          onClick={() => setShowDialog(true)}
          style={{
            background: '#8B5CF6',
            border: 'none',
            borderRadius: '4px',
            color: '#FFFFFF',
            padding: '10px 20px',
            fontSize: '13px',
            cursor: 'pointer',
          }}
        >
          Open Capture Dialog
        </button>
      );
    }

    return (
      <div
        style={{
          position: 'relative',
          height: '600px',
          background: '#0A0A0C',
        }}
      >
        <CaptureDialog
          specPath="spec/protocols/agentese.md"
          onClose={() => setShowDialog(false)}
          onSuccess={() => {
            console.log('Capture success');
            setShowDialog(false);
          }}
        />
      </div>
    );
  },
  parameters: {
    layout: 'fullscreen',
    docs: {
      description: {
        story: 'Capture dialog for uploading execution results. Supports drag-and-drop file upload and test result entry.',
      },
    },
  },
};

export const CaptureWithFiles: StoryObj = {
  name: 'Capture Dialog - With Files',
  render: () => (
    <div
      style={{
        maxWidth: '500px',
        background: '#141418',
        border: '1px solid #28282F',
        borderRadius: '8px',
        padding: '24px',
      }}
    >
      <h2 style={{ color: '#E5E7EB', fontSize: '14px', margin: '0 0 24px 0', textTransform: 'uppercase', letterSpacing: '0.05em' }}>
        CAPTURE EXECUTION RESULTS
      </h2>

      <div style={{ marginBottom: '24px' }}>
        <label style={{ color: '#8A8A94', fontSize: '11px', textTransform: 'uppercase', display: 'block', marginBottom: '8px' }}>
          Spec Path
        </label>
        <div style={{ color: '#E5E7EB', fontSize: '13px', background: '#1C1C22', padding: '8px 12px', borderRadius: '4px' }}>
          spec/protocols/agentese.md
        </div>
      </div>

      <div style={{ marginBottom: '24px' }}>
        <label style={{ color: '#8A8A94', fontSize: '11px', textTransform: 'uppercase', display: 'block', marginBottom: '8px' }}>
          Generated Files
        </label>
        <ul style={{ listStyle: 'none', margin: 0, padding: 0 }}>
          {[
            { path: 'protocols/agentese/gateway.py', size: '12.4 KB' },
            { path: 'protocols/agentese/node.py', size: '8.2 KB' },
            { path: 'protocols/agentese/_tests/test_gateway.py', size: '5.1 KB' },
          ].map((file) => (
            <li
              key={file.path}
              style={{
                display: 'flex',
                alignItems: 'center',
                gap: '8px',
                padding: '8px',
                background: '#1C1C22',
                borderRadius: '4px',
                marginBottom: '4px',
              }}
            >
              <input
                type="text"
                value={file.path}
                readOnly
                style={{
                  flex: 1,
                  background: 'transparent',
                  border: 'none',
                  color: '#E5E7EB',
                  fontSize: '13px',
                }}
              />
              <span style={{ color: '#8A8A94', fontSize: '11px' }}>{file.size}</span>
              <button style={{ background: 'transparent', border: 'none', color: '#8A8A94', cursor: 'pointer' }}>
                &times;
              </button>
            </li>
          ))}
        </ul>
      </div>

      <div style={{ marginBottom: '24px' }}>
        <label style={{ color: '#8A8A94', fontSize: '11px', textTransform: 'uppercase', display: 'block', marginBottom: '8px' }}>
          Preview
        </label>
        <div style={{ background: '#1C1C22', borderRadius: '4px', padding: '12px', fontSize: '13px' }}>
          <p style={{ color: '#E5E7EB', margin: '0 0 4px 0' }}><strong>3</strong> files will be captured</p>
          <p style={{ color: '#10B981', margin: '0 0 4px 0' }}><strong>12</strong> passed tests</p>
          <p style={{ color: '#EF4444', margin: 0 }}><strong>0</strong> failed tests</p>
        </div>
      </div>

      <div style={{ display: 'flex', gap: '8px' }}>
        <button
          style={{
            flex: 1,
            background: '#28282F',
            border: 'none',
            borderRadius: '4px',
            color: '#E5E7EB',
            padding: '10px',
            fontSize: '13px',
            cursor: 'pointer',
          }}
        >
          Cancel
        </button>
        <button
          style={{
            flex: 1,
            background: '#8B5CF6',
            border: 'none',
            borderRadius: '4px',
            color: '#FFFFFF',
            padding: '10px',
            fontSize: '13px',
            cursor: 'pointer',
          }}
        >
          Capture
        </button>
      </div>
    </div>
  ),
  parameters: {
    docs: {
      description: {
        story: 'Capture dialog with files already added and ready for submission.',
      },
    },
  },
};

export const CaptureSuccess: StoryObj = {
  name: 'Capture Dialog - Success',
  render: () => (
    <div
      style={{
        maxWidth: '400px',
        background: '#141418',
        border: '1px solid #28282F',
        borderRadius: '8px',
        padding: '48px',
        textAlign: 'center',
      }}
    >
      <div style={{ fontSize: '48px', color: '#10B981', marginBottom: '16px' }}>
        &#10003;
      </div>
      <h3 style={{ color: '#E5E7EB', fontSize: '18px', margin: '0 0 24px 0' }}>
        Captured Successfully
      </h3>

      <div style={{ display: 'flex', justifyContent: 'center', gap: '48px', marginBottom: '24px' }}>
        <div>
          <div style={{ color: '#10B981', fontSize: '24px', fontWeight: 600 }}>3</div>
          <div style={{ color: '#8A8A94', fontSize: '11px', textTransform: 'uppercase' }}>Files Captured</div>
        </div>
        <div>
          <div style={{ color: '#10B981', fontSize: '24px', fontWeight: 600 }}>5</div>
          <div style={{ color: '#8A8A94', fontSize: '11px', textTransform: 'uppercase' }}>Evidence Marks</div>
        </div>
      </div>

      <p style={{ color: '#8A8A94', fontSize: '13px', margin: 0 }}>
        Results for <code style={{ color: '#E5E7EB' }}>spec/protocols/agentese.md</code> have been captured.
      </p>
    </div>
  ),
  parameters: {
    docs: {
      description: {
        story: 'Success state after capture completion.',
      },
    },
  },
};

// =============================================================================
// Combined Dashboard Story
// =============================================================================

export const FullDirectorDashboard: StoryObj = {
  name: 'Full Director Dashboard',
  render: () => (
    <div
      style={{
        display: 'grid',
        gridTemplateColumns: '200px 1fr 300px',
        height: '600px',
        background: '#0A0A0C',
        gap: '1px',
      }}
    >
      {/* Sidebar */}
      <aside
        style={{
          background: '#141418',
          padding: '16px',
          display: 'flex',
          flexDirection: 'column',
          gap: '24px',
        }}
      >
        <div>
          <h3 style={{ color: '#8A8A94', fontSize: '10px', textTransform: 'uppercase', margin: '0 0 12px 0' }}>
            METRICS
          </h3>
          <div style={{ fontSize: '32px', fontWeight: 600, color: '#E5E7EB' }}>
            {mockDocuments.length}
          </div>
          <div style={{ color: '#8A8A94', fontSize: '12px' }}>Documents</div>
        </div>

        <div>
          <h3 style={{ color: '#8A8A94', fontSize: '10px', textTransform: 'uppercase', margin: '0 0 8px 0' }}>
            BY STATUS
          </h3>
          {(['ready', 'processing', 'uploaded', 'executed', 'stale', 'failed'] as DocumentStatus[]).map((status) => (
            <div
              key={status}
              style={{
                display: 'flex',
                alignItems: 'center',
                justifyContent: 'space-between',
                padding: '4px 0',
              }}
            >
              <DocumentStatusBadge status={status} size="sm" />
              <span style={{ color: '#8A8A94', fontSize: '12px' }}>
                {mockDocuments.filter((d) => d.status === status).length}
              </span>
            </div>
          ))}
        </div>

        <button
          style={{
            marginTop: 'auto',
            background: '#10B981',
            border: 'none',
            borderRadius: '4px',
            color: '#0A0A0C',
            padding: '10px',
            fontSize: '13px',
            fontWeight: 500,
            cursor: 'pointer',
          }}
        >
          + Upload
        </button>
      </aside>

      {/* Main List */}
      <main style={{ background: '#141418', overflow: 'hidden', display: 'flex', flexDirection: 'column' }}>
        <div style={{ padding: '12px 16px', borderBottom: '1px solid #28282F', display: 'flex', gap: '8px' }}>
          <span style={{ color: '#8A8A94', fontSize: '12px' }}>/</span>
          <input
            type="text"
            placeholder="Search documents..."
            style={{
              flex: 1,
              background: 'transparent',
              border: 'none',
              color: '#E5E7EB',
              fontSize: '13px',
              outline: 'none',
            }}
          />
          <span style={{ color: '#8A8A94', fontSize: '12px' }}>
            {mockDocuments.length} / {mockDocuments.length}
          </span>
        </div>

        <div style={{ flex: 1, overflow: 'auto' }}>
          {mockDocuments.slice(0, 6).map((doc, idx) => (
            <div
              key={doc.path}
              style={{
                display: 'grid',
                gridTemplateColumns: '1fr 80px 60px 80px',
                gap: '8px',
                padding: '12px 16px',
                borderBottom: '1px solid #1C1C22',
                borderLeft: idx === 0 ? '2px solid #10B981' : '2px solid transparent',
                background: idx === 0 ? 'rgba(16, 185, 129, 0.05)' : 'transparent',
                cursor: 'pointer',
              }}
            >
              <div>
                <div style={{ color: '#E5E7EB', fontSize: '13px' }}>{doc.title}</div>
                <div style={{ color: '#8A8A94', fontSize: '11px' }}>{doc.path}</div>
              </div>
              <div><DocumentStatusBadge status={doc.status} size="sm" /></div>
              <div style={{ color: '#E5E7EB', fontSize: '13px', textAlign: 'right' }}>{doc.claim_count ?? 0}</div>
              <div style={{ color: '#8A8A94', fontSize: '11px', textAlign: 'right' }}>
                {doc.analyzed_at ? new Date(doc.analyzed_at).toLocaleDateString() : '--'}
              </div>
            </div>
          ))}
        </div>
      </main>

      {/* Detail Panel */}
      <aside style={{ background: '#1C1C22', padding: '16px', overflow: 'auto' }}>
        <div style={{ display: 'flex', alignItems: 'center', gap: '8px', marginBottom: '16px' }}>
          <h2 style={{ color: '#E5E7EB', fontSize: '14px', margin: 0, flex: 1 }}>
            AGENTESE Protocol
          </h2>
          <DocumentStatusBadge status="ready" size="sm" />
        </div>

        <div style={{ color: '#8A8A94', fontSize: '11px', marginBottom: '16px', padding: '8px', background: '#141418', borderRadius: '4px' }}>
          spec/protocols/agentese.md
        </div>

        <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '8px', marginBottom: '16px' }}>
          {[
            { label: 'Claims', value: 24 },
            { label: 'Impls', value: 18 },
            { label: 'Tests', value: 12 },
            { label: 'Placeholders', value: 2 },
          ].map((stat) => (
            <div
              key={stat.label}
              style={{
                background: '#141418',
                borderRadius: '4px',
                padding: '12px',
                textAlign: 'center',
              }}
            >
              <div style={{ color: '#E5E7EB', fontSize: '16px', fontWeight: 600 }}>{stat.value}</div>
              <div style={{ color: '#8A8A94', fontSize: '10px', textTransform: 'uppercase' }}>{stat.label}</div>
            </div>
          ))}
        </div>

        <div style={{ color: '#8A8A94', fontSize: '11px', marginBottom: '16px' }}>
          Analyzed: {new Date().toLocaleString()}
        </div>

        <button
          style={{
            width: '100%',
            background: '#8B5CF6',
            border: 'none',
            borderRadius: '4px',
            color: '#FFFFFF',
            padding: '10px',
            fontSize: '13px',
            fontWeight: 500,
            cursor: 'pointer',
            marginBottom: '8px',
          }}
        >
          Open Document &rarr;
        </button>

        <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '8px' }}>
          <button
            style={{
              background: '#28282F',
              border: '1px solid #3E3E46',
              borderRadius: '4px',
              color: '#E5E7EB',
              padding: '8px',
              fontSize: '11px',
              cursor: 'pointer',
            }}
          >
            <kbd style={{ fontSize: '10px', marginRight: '4px' }}>R</kbd> Rename
          </button>
          <button
            style={{
              background: '#28282F',
              border: '1px solid #3E3E46',
              borderRadius: '4px',
              color: '#E5E7EB',
              padding: '8px',
              fontSize: '11px',
              cursor: 'pointer',
            }}
          >
            <kbd style={{ fontSize: '10px', marginRight: '4px' }}>d</kbd> Delete
          </button>
        </div>
      </aside>
    </div>
  ),
  parameters: {
    layout: 'fullscreen',
    docs: {
      description: {
        story: `
# Full Director Dashboard

Three-column master-detail layout for document lifecycle management.

**Layout:**
- Sidebar: Metrics and status filters
- Main: Searchable, sortable document list
- Detail: Selected document info and actions

**STARK BIOME Design:**
- Steel frame on obsidian background
- Status-colored accents (green = ready, purple = executed)
- Keyboard-first navigation (j/k, Enter, /, d, R)

Philosophy: "The canvas breathes. Documents arrive, analyze, become ready."
        `,
      },
    },
  },
};
