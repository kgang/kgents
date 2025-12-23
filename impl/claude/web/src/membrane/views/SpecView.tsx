/**
 * SpecView — Display a specification with SpecGraph integration
 *
 * Renders spec with:
 * - Tier badge and confidence bar (from SpecGraph)
 * - Expandable edge portals (extends, implements, tests, etc.)
 * - Interactive token counts
 * - Interactive content (AGENTESE paths, task checkboxes)
 *
 * "The spec is not description—it is generative."
 * "Specs stop being documentation and become live control surfaces."
 */

import { useCallback, useEffect, useState } from 'react';

import { documentApi, fileApi } from '../../api/client';
import { EmpathyError } from '../../components/joy/EmpathyError';
import { GrowingContainer } from '../../components/genesis/GrowingContainer';
import { PersonalityLoading } from '../../components/joy/PersonalityLoading';

import { InteractiveDocument, type SceneGraph } from '../tokens';
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
  const [sceneGraph, setSceneGraph] = useState<SceneGraph | null>(null);
  const [contentLoading, setContentLoading] = useState(false);
  const [contentError, setContentError] = useState<string | null>(null);

  // Query SpecGraph for metadata
  useEffect(() => {
    if (path) {
      query(path);
    }
  }, [path, query]);

  // Fetch content and parse to SceneGraph
  useEffect(() => {
    let cancelled = false;

    async function fetchAndParse() {
      setContentLoading(true);
      setContentError(null);

      try {
        // Step 1: Read file via AGENTESE world.file.read
        const fileData = await fileApi.read(path);

        if (cancelled) return;

        // Step 2: Parse content to SceneGraph via AGENTESE self.document.parse
        const parsed = await documentApi.parse(fileData.content, 'COMFORTABLE');

        if (cancelled) return;

        // Cast the scene_graph to our SceneGraph type
        setSceneGraph(parsed.scene_graph as SceneGraph);
      } catch (err) {
        if (!cancelled) {
          console.error('[SpecView] Failed to load content:', err);
          setContentError(err instanceof Error ? err.message : 'Failed to load content');
        }
      } finally {
        if (!cancelled) {
          setContentLoading(false);
        }
      }
    }

    fetchAndParse();
    return () => {
      cancelled = true;
    };
  }, [path]);

  // Handle AGENTESE path navigation
  const handleTokenNavigate = useCallback(
    (agentesePath: string) => {
      // Parse AGENTESE path to determine target
      // Format: context.service.aspect (e.g., self.brain, world.house.manifest)
      const parts = agentesePath.split('.');
      const context = parts[0]; // self, world, concept, void, time

      if (context === 'concept' && parts[1]) {
        // Navigate to concept view
        onNavigate?.(`concept/${parts.slice(1).join('/')}`);
      } else {
        // For now, log and let parent handle
        console.log('[SpecView] Navigate to AGENTESE path:', agentesePath);
        onNavigate?.(agentesePath);
      }
    },
    [onNavigate]
  );

  // Handle task toggle
  const handleTaskToggle = useCallback(
    async (_newState: boolean, taskId?: string) => {
      if (!taskId) return;

      try {
        // Call self.document.task.toggle via AGENTESE
        await documentApi.toggleTask({
          file_path: path,
          task_id: taskId,
        });

        // Refresh the SceneGraph after toggle
        const fileData = await fileApi.read(path);
        const parsed = await documentApi.parse(fileData.content, 'COMFORTABLE');
        setSceneGraph(parsed.scene_graph as SceneGraph);
      } catch (err) {
        console.error('[SpecView] Failed to toggle task:', err);
        throw err; // Re-throw so TaskCheckboxToken can revert
      }
    },
    [path]
  );

  // If SpecGraph fails but we have content, show it anyway
  // This allows testing Interactive Text before SpecGraph is wired
  const hasContent = sceneGraph !== null;
  const showMetadata = spec !== null;

  // Only show error if we have neither spec nor content
  if (error && !hasContent && !contentLoading) {
    return (
      <div className="spec-view spec-view--error">
        <EmpathyError type="notfound" title="Spec not accessible" subtitle={error} />
      </div>
    );
  }

  // Loading state - show if loading and no content yet
  if (loading && !hasContent) {
    return (
      <div className="spec-view spec-view--loading">
        <PersonalityLoading jewel="gestalt" action="analyzing" size="md" />
      </div>
    );
  }

  // Destructure only if spec exists
  const node = spec?.node;
  const edges = spec?.edges ?? {};
  const tokens = spec?.tokens ?? {};

  return (
    <div className="spec-view">
      {/* Header with tier and confidence - only show if we have spec metadata */}
      {showMetadata && node && (
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
      )}

      {/* Fallback header when no spec metadata */}
      {!showMetadata && (
        <header className="spec-view__header">
          <div className="spec-view__title-row">
            <h2 className="spec-view__title">{path.split('/').pop()}</h2>
          </div>
          <div className="spec-view__meta">
            <span className="spec-view__path">{path}</span>
          </div>
        </header>
      )}

      {/* Token badges - only if we have tokens from SpecGraph */}
      {showMetadata && <TokenBadges tokens={tokens} />}

      {/* Edge portals - only if we have edges from SpecGraph */}
      {showMetadata && (
        <EdgePortals edges={edges} onNavigate={onNavigate} onEdgeClick={onEdgeClick} />
      )}

      {/* Content */}
      <div className="spec-view__content">
        {contentLoading ? (
          <div className="spec-view__content-loading">Loading content...</div>
        ) : contentError ? (
          <div className="spec-view__content-error">
            <p>Failed to load content</p>
            <p className="spec-view__content-hint">{contentError}</p>
          </div>
        ) : sceneGraph ? (
          <InteractiveDocument
            sceneGraph={sceneGraph}
            onNavigate={handleTokenNavigate}
            onToggle={handleTaskToggle}
            className="spec-view__interactive"
          />
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
