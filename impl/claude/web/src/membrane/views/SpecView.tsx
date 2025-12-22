/**
 * SpecView — Display a specification with SpecGraph integration
 *
 * Renders spec with:
 * - Tier badge and confidence bar (from SpecGraph)
 * - Expandable edge portals (extends, implements, tests, etc.)
 * - Interactive token counts
 * - Raw markdown content
 *
 * "The spec is not description—it is generative."
 */

import { useCallback, useEffect, useState } from 'react';

import { EmpathyError } from '../../components/joy/EmpathyError';
import { PersonalityLoading } from '../../components/joy/PersonalityLoading';
import { GrowingContainer } from '../../components/genesis/GrowingContainer';

import { useSpecQuery, type EdgeType } from '../useSpecNavigation';

import './SpecView.css';

// =============================================================================
// Types
// =============================================================================

interface SpecViewProps {
  path: string;
  onNavigate?: (path: string) => void;
  onEdgeClick?: (target: string, edge: EdgeType) => void;
}

// =============================================================================
// Sub-components
// =============================================================================

interface ConfidenceBarProps {
  confidence: number;
}

function ConfidenceBar({ confidence }: ConfidenceBarProps) {
  const percent = Math.round(confidence * 100);
  const filled = Math.round(confidence * 10);
  const bar = '\u2588'.repeat(filled) + '\u2591'.repeat(10 - filled);

  return (
    <span className="spec-view__confidence" title={`Confidence: ${percent}%`}>
      <span className="spec-view__confidence-bar">{bar}</span>
      <span className="spec-view__confidence-value">{percent}%</span>
    </span>
  );
}

interface EdgePortalsProps {
  edges: Record<string, string[]>;
  onEdgeClick?: (target: string, edge: EdgeType) => void;
  onNavigate?: (path: string) => void;
}

function EdgePortals({ edges, onEdgeClick, onNavigate }: EdgePortalsProps) {
  const [expanded, setExpanded] = useState<Record<string, boolean>>({});

  // Hooks must be called before any early returns
  const handleTargetClick = useCallback(
    (target: string, edge: EdgeType) => {
      // Navigate to spec files directly
      if (target.startsWith('spec/') && target.endsWith('.md')) {
        onNavigate?.(target);
      } else {
        onEdgeClick?.(target, edge);
      }
    },
    [onNavigate, onEdgeClick]
  );

  const edgeTypes = Object.keys(edges).filter((k) => edges[k].length > 0);

  if (edgeTypes.length === 0) return null;

  return (
    <div className="spec-view__edges">
      <h3 className="spec-view__edges-title">Portal Edges</h3>
      {edgeTypes.map((edgeType) => {
        const targets = edges[edgeType];
        const isExpanded = expanded[edgeType];

        return (
          <div key={edgeType} className="spec-view__edge-group">
            <button
              className="spec-view__edge-toggle"
              onClick={() => setExpanded((prev) => ({ ...prev, [edgeType]: !prev[edgeType] }))}
              data-expanded={isExpanded}
            >
              <span className="spec-view__edge-icon">{isExpanded ? '\u25BC' : '\u25B6'}</span>
              <span className="spec-view__edge-type">[{edgeType}]</span>
              <span className="spec-view__edge-count">({targets.length})</span>
            </button>

            {isExpanded && (
              <GrowingContainer>
                <ul className="spec-view__edge-list">
                  {targets.slice(0, 10).map((target) => (
                    <li key={target} className="spec-view__edge-item">
                      <button
                        className="spec-view__edge-link"
                        onClick={() => handleTargetClick(target, edgeType as EdgeType)}
                      >
                        {target}
                      </button>
                    </li>
                  ))}
                  {targets.length > 10 && (
                    <li className="spec-view__edge-more">+{targets.length - 10} more</li>
                  )}
                </ul>
              </GrowingContainer>
            )}
          </div>
        );
      })}
    </div>
  );
}

interface TokenBadgesProps {
  tokens: Record<string, number>;
}

function TokenBadges({ tokens }: TokenBadgesProps) {
  const types = Object.keys(tokens).filter((k) => tokens[k] > 0);

  if (types.length === 0) return null;

  return (
    <div className="spec-view__tokens">
      {types.map((type) => (
        <span key={type} className="spec-view__token-badge" data-type={type}>
          {type}: {tokens[type]}
        </span>
      ))}
    </div>
  );
}

// =============================================================================
// Main Component
// =============================================================================

export function SpecView({ path, onNavigate, onEdgeClick }: SpecViewProps) {
  const { spec, loading, error, query } = useSpecQuery();
  const [content, setContent] = useState<string | null>(null);
  const [contentLoading, setContentLoading] = useState(false);

  // Query SpecGraph for metadata
  useEffect(() => {
    if (path) {
      query(path);
    }
  }, [path, query]);

  // Fetch raw content separately
  useEffect(() => {
    let cancelled = false;

    async function fetchContent() {
      setContentLoading(true);
      try {
        const response = await fetch(`/api/files/read?path=${encodeURIComponent(path)}`);
        if (response.ok) {
          const data = await response.json();
          if (!cancelled) {
            setContent(data.content);
          }
        }
      } catch {
        // Content fetch failed, will show metadata only
      } finally {
        if (!cancelled) {
          setContentLoading(false);
        }
      }
    }

    fetchContent();
    return () => {
      cancelled = true;
    };
  }, [path]);

  // Loading state
  if (loading) {
    return (
      <div className="spec-view spec-view--loading">
        <PersonalityLoading jewel="gestalt" action="analyzing" size="md" />
      </div>
    );
  }

  // Error state
  if (error) {
    return (
      <div className="spec-view spec-view--error">
        <EmpathyError type="notfound" title="Spec not accessible" subtitle={error} />
      </div>
    );
  }

  // No spec found
  if (!spec) {
    return (
      <div className="spec-view spec-view--empty">
        <div className="spec-view__empty">
          <p>Spec not found in SpecGraph</p>
          <p className="spec-view__empty-hint">{path}</p>
        </div>
      </div>
    );
  }

  const { node, edges, tokens } = spec;

  return (
    <div className="spec-view">
      {/* Header with tier and confidence */}
      <header className="spec-view__header">
        <div className="spec-view__title-row">
          <h2 className="spec-view__title">{node.title || node.path}</h2>
          <span className="spec-view__tier" data-tier={node.tier}>
            {node.tier}
          </span>
        </div>

        <div className="spec-view__meta">
          <span className="spec-view__path">{node.agentese_path || path}</span>
          <ConfidenceBar confidence={node.confidence} />
        </div>

        {node.derives_from.length > 0 && (
          <div className="spec-view__derives">
            <span className="spec-view__derives-label">Derives from:</span>
            {node.derives_from.map((d) => (
              <button
                key={d}
                className="spec-view__derives-link"
                onClick={() => onNavigate?.(`spec/${d}.md`)}
              >
                {d}
              </button>
            ))}
          </div>
        )}
      </header>

      {/* Token badges */}
      <TokenBadges tokens={tokens} />

      {/* Edge portals */}
      <EdgePortals edges={edges} onNavigate={onNavigate} onEdgeClick={onEdgeClick} />

      {/* Content */}
      <div className="spec-view__content">
        {contentLoading ? (
          <div className="spec-view__content-loading">Loading content...</div>
        ) : content ? (
          <pre className="spec-view__markdown">{content}</pre>
        ) : (
          <div className="spec-view__content-empty">
            <p>Content not available</p>
            <p className="spec-view__content-hint">
              Use edge portals above to navigate the spec graph
            </p>
          </div>
        )}
      </div>
    </div>
  );
}
