/**
 * FileInspector - Center panel file viewer
 *
 * Features:
 * - Syntax highlighting for code files
 * - K-Block overlay (hover to see K-Block info)
 * - Git blame integration
 * - Derivation chain sidebar
 * - Linked spec/impl toggle
 *
 * STARK BIOME aesthetic: 90% steel, 10% earned glow.
 */

import { memo, useState, useEffect, useMemo } from 'react';
import {
  FileText,
  FileCode,
  GitBranch,
  Layers,
  ExternalLink,
  Copy,
  Check,
  User,
  Clock,
  Eye,
  EyeOff,
} from 'lucide-react';
import type { KBlockInfo, BlameLine, DerivationStep } from './types';
import { LAYER_COLORS, LAYER_NAMES } from './types';

// =============================================================================
// Types
// =============================================================================

export interface FileInspectorProps {
  path: string;
  showBlame?: boolean;
  showKBlock?: boolean;
  showDerivation?: boolean;
  onNavigateToFile?: (path: string) => void;
  onKBlockHover?: (kblockId: string, position: { x: number; y: number }) => void;
}

// =============================================================================
// Mock Data
// =============================================================================

const MOCK_FILE_CONTENT = `# Witness Protocol

> "Every action leaves a mark. The mark IS the witness."

## Overview

The Witness Crown Jewel provides comprehensive action tracing,
decision recording, and accountability surfaces.

## Core Concepts

### Marks

A Mark is the atomic unit of witnessed behavior:
- Every action leaves a mark
- Marks are immutable once created
- Marks can have reasoning and principles

\`\`\`python
@dataclass
class Mark:
    id: str
    action: str
    reasoning: Optional[str]
    principles: List[str]
    author: Literal["kent", "claude", "system"]
    timestamp: datetime
\`\`\`

### Evidence Ladder

Confidence flows upward through evidence:

| Level | Type | Description |
|-------|------|-------------|
| L-∞ | Orphan | Artifacts without lineage |
| L-2 | Prompt | PromptAncestor count |
| L-1 | Trace | TraceWitness count |
| L0 | Mark | Human marks |
| L1 | Test | Test artifacts |
| L2 | Proof | Formal proofs |
| L3 | Bet | Economic bets |

## Implementation Status

- [x] Mark creation and retrieval
- [x] Causal lineage (parent_mark_id)
- [x] SSE streaming
- [ ] Evidence ladder computation
- [ ] Garden visualization
`;

const MOCK_KBLOCK: KBlockInfo = {
  id: 'kb-4',
  path: 'spec/protocols/witness.md',
  title: 'Witness Protocol',
  layer: 2,
  layerName: 'SPEC',
  derivedFrom: ['kb-6', 'kb-7'],
  groundedBy: ['kb-9'],
  witnesses: [
    {
      markId: 'm-1',
      action: 'Created witness spec',
      author: 'kent',
      timestamp: '2025-12-20T10:00:00Z',
      principles: ['composable'],
    },
    {
      markId: 'm-2',
      action: 'Added evidence ladder',
      author: 'claude',
      timestamp: '2025-12-21T14:30:00Z',
      principles: ['generative'],
    },
  ],
  galoisLoss: 0.12,
  createdAt: '2025-12-15T09:00:00Z',
  modifiedAt: '2025-12-21T14:30:00Z',
};

const MOCK_BLAME: BlameLine[] = [
  {
    lineNumber: 1,
    content: '# Witness Protocol',
    commitSha: 'abc123',
    author: 'Kent',
    date: '2025-12-15',
  },
  { lineNumber: 2, content: '', commitSha: 'abc123', author: 'Kent', date: '2025-12-15' },
  {
    lineNumber: 3,
    content: '> "Every action leaves a mark..."',
    commitSha: 'def456',
    author: 'Claude',
    date: '2025-12-18',
  },
];

const MOCK_DERIVATION: DerivationStep[] = [
  {
    id: 'kb-6',
    title: 'COMPOSABLE',
    layer: 0,
    layerName: 'AXIOM',
    galoisLoss: 0,
    path: 'spec/principles/composable.md',
  },
  {
    id: 'kb-1',
    title: 'Joy-Inducing',
    layer: 1,
    layerName: 'VALUE',
    galoisLoss: 0.05,
    path: 'spec/values/joy.md',
  },
  {
    id: 'kb-4',
    title: 'Witness Protocol',
    layer: 2,
    layerName: 'SPEC',
    galoisLoss: 0.12,
    path: 'spec/protocols/witness.md',
  },
];

// =============================================================================
// Subcomponents
// =============================================================================

interface DerivationSidebarProps {
  steps: DerivationStep[];
  currentId: string;
  onNavigate: (path: string) => void;
}

const DerivationSidebar = memo(function DerivationSidebar({
  steps,
  currentId,
  onNavigate,
}: DerivationSidebarProps) {
  return (
    <div className="file-inspector__derivation">
      <div className="file-inspector__derivation-header">
        <Layers size={12} />
        <span>Derivation Chain</span>
      </div>
      <div className="file-inspector__derivation-steps">
        {steps.map((step, index) => (
          <button
            key={step.id}
            className="file-inspector__derivation-step"
            data-current={step.id === currentId}
            onClick={() => step.path && onNavigate(step.path)}
            style={{ '--step-color': LAYER_COLORS[step.layer] } as React.CSSProperties}
          >
            {index > 0 && <div className="file-inspector__derivation-line" />}
            <div className="file-inspector__derivation-node">
              <span className="file-inspector__derivation-layer">L{step.layer}</span>
              <span className="file-inspector__derivation-title">{step.title}</span>
              {step.galoisLoss > 0 && (
                <span className="file-inspector__derivation-loss">
                  -{(step.galoisLoss * 100).toFixed(0)}%
                </span>
              )}
            </div>
          </button>
        ))}
      </div>
    </div>
  );
});

interface KBlockSidebarProps {
  kblock: KBlockInfo;
  onNavigateToFile?: (path: string) => void;
}

const KBlockSidebar = memo(function KBlockSidebar({
  kblock,
  onNavigateToFile,
}: KBlockSidebarProps) {
  return (
    <div className="file-inspector__kblock">
      <div className="file-inspector__kblock-header">
        <span
          className="file-inspector__kblock-layer"
          style={{ color: LAYER_COLORS[kblock.layer] }}
        >
          L{kblock.layer} {kblock.layerName}
        </span>
        <span className="file-inspector__kblock-title">{kblock.title}</span>
      </div>

      {kblock.galoisLoss !== undefined && (
        <div className="file-inspector__kblock-stat">
          <span className="file-inspector__kblock-label">Galois Loss</span>
          <span className="file-inspector__kblock-value">
            {(kblock.galoisLoss * 100).toFixed(1)}%
          </span>
        </div>
      )}

      {kblock.witnesses && kblock.witnesses.length > 0 && (
        <div className="file-inspector__kblock-section">
          <span className="file-inspector__kblock-label">
            Witnesses ({kblock.witnesses.length})
          </span>
          <div className="file-inspector__kblock-witnesses">
            {kblock.witnesses.map((w) => (
              <div key={w.markId} className="file-inspector__witness">
                <span className="file-inspector__witness-action">{w.action}</span>
                <span className="file-inspector__witness-meta">
                  {w.author} - {new Date(w.timestamp).toLocaleDateString()}
                </span>
              </div>
            ))}
          </div>
        </div>
      )}

      {kblock.derivedFrom && kblock.derivedFrom.length > 0 && (
        <div className="file-inspector__kblock-section">
          <span className="file-inspector__kblock-label">Derived From</span>
          <div className="file-inspector__kblock-links">
            {kblock.derivedFrom.map((id) => (
              <button key={id} className="file-inspector__kblock-link">
                {id}
              </button>
            ))}
          </div>
        </div>
      )}
    </div>
  );
});

// =============================================================================
// Main Component
// =============================================================================

export const FileInspector = memo(function FileInspector({
  path,
  showBlame = false,
  showKBlock = true,
  showDerivation = true,
  onNavigateToFile,
  onKBlockHover,
}: FileInspectorProps) {
  const [content, setContent] = useState<string>('');
  const [kblock, setKblock] = useState<KBlockInfo | null>(null);
  const [blame, setBlame] = useState<BlameLine[]>([]);
  const [derivation, setDerivation] = useState<DerivationStep[]>([]);
  const [copied, setCopied] = useState(false);
  const [blameVisible, setBlameVisible] = useState(showBlame);

  // Determine file type
  const isSpec = path.startsWith('spec/');
  const linkedPath = isSpec
    ? path.replace('spec/', 'impl/claude/')
    : path.replace('impl/', 'spec/');

  // Load file content (mock for now)
  useEffect(() => {
    // In real implementation: fetch from API
    setContent(MOCK_FILE_CONTENT);
    setKblock(MOCK_KBLOCK);
    setBlame(MOCK_BLAME);
    setDerivation(MOCK_DERIVATION);
  }, [path]);

  // Parse content into lines
  const lines = useMemo(() => content.split('\n'), [content]);

  // Copy path to clipboard
  const handleCopyPath = async () => {
    await navigator.clipboard.writeText(path);
    setCopied(true);
    setTimeout(() => setCopied(false), 2000);
  };

  // Format relative date
  const formatDate = (dateStr: string) => {
    const date = new Date(dateStr);
    const now = new Date();
    const diffMs = now.getTime() - date.getTime();
    const diffDays = Math.floor(diffMs / (1000 * 60 * 60 * 24));

    if (diffDays === 0) return 'today';
    if (diffDays === 1) return 'yesterday';
    if (diffDays < 7) return `${diffDays}d ago`;
    return date.toLocaleDateString();
  };

  if (!path) {
    return (
      <div className="file-inspector file-inspector--empty">
        <FileText size={32} className="file-inspector__empty-icon" />
        <p className="file-inspector__empty-text">Select a file to view</p>
        <p className="file-inspector__empty-hint">Use j/k to navigate, Enter to select</p>
      </div>
    );
  }

  return (
    <div className="file-inspector">
      {/* Header */}
      <div className="file-inspector__header">
        <div className="file-inspector__path">
          {isSpec ? <FileText size={14} /> : <FileCode size={14} />}
          <span className="file-inspector__path-text">{path}</span>
          <button className="file-inspector__copy-btn" onClick={handleCopyPath} title="Copy path">
            {copied ? <Check size={12} /> : <Copy size={12} />}
          </button>
        </div>

        <div className="file-inspector__actions">
          {/* Toggle blame */}
          <button
            className={`file-inspector__action-btn ${blameVisible ? 'active' : ''}`}
            onClick={() => setBlameVisible(!blameVisible)}
            title={blameVisible ? 'Hide blame' : 'Show blame'}
          >
            {blameVisible ? <EyeOff size={14} /> : <Eye size={14} />}
            <span>Blame</span>
          </button>

          {/* Navigate to linked file */}
          <button
            className="file-inspector__action-btn"
            onClick={() => onNavigateToFile?.(linkedPath)}
            title={`Go to ${isSpec ? 'implementation' : 'spec'}`}
          >
            <ExternalLink size={14} />
            <span>{isSpec ? 'View Impl' : 'View Spec'}</span>
          </button>
        </div>
      </div>

      {/* Main content area */}
      <div className="file-inspector__content">
        {/* Derivation sidebar (left) */}
        {showDerivation && derivation.length > 0 && (
          <DerivationSidebar
            steps={derivation}
            currentId={kblock?.id || ''}
            onNavigate={(p) => onNavigateToFile?.(p)}
          />
        )}

        {/* File content */}
        <div className="file-inspector__code">
          <div className="file-inspector__lines">
            {lines.map((line, index) => {
              const lineNum = index + 1;
              const blameLine = blame.find((b) => b.lineNumber === lineNum);

              return (
                <div key={index} className="file-inspector__line">
                  {/* Blame column */}
                  {blameVisible && (
                    <div className="file-inspector__blame">
                      {blameLine && (
                        <>
                          <span className="file-inspector__blame-author">{blameLine.author}</span>
                          <span className="file-inspector__blame-date">{blameLine.date}</span>
                        </>
                      )}
                    </div>
                  )}

                  {/* Line number */}
                  <span className="file-inspector__line-num">{lineNum}</span>

                  {/* Line content */}
                  <pre className="file-inspector__line-content">{line || ' '}</pre>
                </div>
              );
            })}
          </div>
        </div>

        {/* K-Block sidebar (right) */}
        {showKBlock && kblock && (
          <KBlockSidebar kblock={kblock} onNavigateToFile={onNavigateToFile} />
        )}
      </div>

      {/* Footer with metadata */}
      {kblock && (
        <div className="file-inspector__footer">
          <div className="file-inspector__meta">
            <span className="file-inspector__meta-item">
              <User size={12} />
              {kblock.witnesses?.[0]?.author || 'unknown'}
            </span>
            <span className="file-inspector__meta-item">
              <Clock size={12} />
              {kblock.modifiedAt ? formatDate(kblock.modifiedAt) : 'unknown'}
            </span>
            <span className="file-inspector__meta-item">
              <GitBranch size={12} />
              {kblock.witnesses?.length || 0} witnesses
            </span>
          </div>
        </div>
      )}
    </div>
  );
});

export default FileInspector;
