/**
 * SpecView — Display and EDIT specifications with K-Block integration
 *
 * THE EDITING MEMBRANE: Every spec view creates a K-Block.
 * Kent edits in place, changes flow through WitnessedSheaf.
 *
 * Renders spec with:
 * - K-Block isolation state badge (PRISTINE/DIRTY/STALE)
 * - Tier badge and confidence bar (from SpecGraph)
 * - Expandable edge portals (extends, implements, tests, etc.)
 * - References panel (implements, tests, extends relationships)
 * - Interactive content (AGENTESE paths, task checkboxes)
 * - Save/Discard controls when dirty
 *
 * "The spec is not description—it is generative."
 * "Specs stop being documentation and become live control surfaces."
 * "You edit a possible world until you crystallize."
 */

import { useCallback, useEffect, useState } from 'react';

import { documentApi } from '../../api/client';
import { EmpathyError } from '../../components/joy/EmpathyError';
import { GrowingContainer } from '../../components/genesis/GrowingContainer';
import { PersonalityLoading } from '../../components/joy/PersonalityLoading';

import { InteractiveDocument, type SceneGraph } from '../tokens';
import { useSpecQuery, type EdgeType } from '../useSpecNavigation';
import { useFileKBlock, type KBlockReference } from '../useKBlock';

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
// K-Block Components
// =============================================================================

interface IsolationBadgeProps {
  isolation: string;
  isDirty: boolean;
  onSave?: () => void;
  onDiscard?: () => void;
  isSaving?: boolean;
}

function IsolationBadge({ isolation, isDirty, onSave, onDiscard, isSaving }: IsolationBadgeProps) {
  return (
    <div className="spec-view__isolation" data-isolation={isolation} data-dirty={isDirty}>
      <span className="spec-view__isolation-state">{isDirty ? 'DIRTY' : isolation}</span>
      {isDirty && onSave && onDiscard && (
        <div className="spec-view__isolation-actions">
          <button
            className="spec-view__isolation-btn spec-view__isolation-btn--save"
            onClick={onSave}
            disabled={isSaving}
            title="Save changes to cosmos"
          >
            {isSaving ? 'Saving...' : 'Save'}
          </button>
          <button
            className="spec-view__isolation-btn spec-view__isolation-btn--discard"
            onClick={onDiscard}
            disabled={isSaving}
            title="Discard changes"
          >
            Discard
          </button>
        </div>
      )}
    </div>
  );
}

interface ReferencesPanelProps {
  references: KBlockReference[];
  onNavigate?: (path: string) => void;
}

function ReferencesPanel({ references, onNavigate }: ReferencesPanelProps) {
  const [expanded, setExpanded] = useState(false);

  if (references.length === 0) return null;

  // Group by kind
  const grouped = references.reduce(
    (acc, ref) => {
      if (!acc[ref.kind]) acc[ref.kind] = [];
      acc[ref.kind].push(ref);
      return acc;
    },
    {} as Record<string, KBlockReference[]>
  );

  return (
    <div className="spec-view__references">
      <button
        className="spec-view__references-toggle"
        onClick={() => setExpanded(!expanded)}
        data-expanded={expanded}
      >
        <span className="spec-view__references-icon">{expanded ? '\u25BC' : '\u25B6'}</span>
        <span className="spec-view__references-title">References</span>
        <span className="spec-view__references-count">({references.length})</span>
      </button>

      {expanded && (
        <GrowingContainer>
          <div className="spec-view__references-list">
            {Object.entries(grouped).map(([kind, refs]) => (
              <div key={kind} className="spec-view__references-group">
                <span className="spec-view__references-kind">{kind}</span>
                <ul className="spec-view__references-items">
                  {refs.map((ref, i) => (
                    <li
                      key={`${ref.target}-${i}`}
                      className="spec-view__references-item"
                      data-stale={ref.stale}
                      data-exists={ref.exists}
                    >
                      <button
                        className="spec-view__references-link"
                        onClick={() => onNavigate?.(ref.target)}
                        disabled={!ref.exists}
                        title={ref.context || undefined}
                      >
                        {ref.target}
                        {ref.stale && <span className="spec-view__references-stale">stale</span>}
                        {!ref.exists && (
                          <span className="spec-view__references-missing">missing</span>
                        )}
                      </button>
                    </li>
                  ))}
                </ul>
              </div>
            ))}
          </div>
        </GrowingContainer>
      )}
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
  const [references, setReferences] = useState<KBlockReference[]>([]);
  const [isSaving, setIsSaving] = useState(false);

  // K-Block for transactional editing
  const kblock = useFileKBlock();

  // Query SpecGraph for metadata
  useEffect(() => {
    if (path) {
      query(path);
    }
  }, [path, query]);

  // Create K-Block and fetch content when path changes
  useEffect(() => {
    let cancelled = false;

    async function initKBlock() {
      setContentLoading(true);
      setContentError(null);

      try {
        // Step 1: Create K-Block for the spec file
        const created = await kblock.create(path);

        if (cancelled) return;

        if (!created) {
          throw new Error(kblock.state.error || 'Failed to create K-Block');
        }

        // Step 2: Parse content to SceneGraph via AGENTESE self.document.parse
        const parsed = await documentApi.parse(kblock.state.content, 'COMFORTABLE');

        if (cancelled) return;

        setSceneGraph(parsed.scene_graph as SceneGraph);

        // Step 3: Fetch references
        const refs = await kblock.getReferences();
        if (!cancelled) {
          setReferences(refs);
        }
      } catch (err) {
        if (!cancelled) {
          console.error('[SpecView] Failed to initialize K-Block:', err);
          setContentError(err instanceof Error ? err.message : 'Failed to load content');
        }
      } finally {
        if (!cancelled) {
          setContentLoading(false);
        }
      }
    }

    initKBlock();
    return () => {
      cancelled = true;
      // Discard K-Block when unmounting (unless explicitly saved)
      // This is intentional: uncommitted edits are lost on navigation
      kblock.discard();
    };
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [path]);

  // Re-parse content when K-Block content changes
  useEffect(() => {
    if (!kblock.state.content) return;

    async function reparse() {
      try {
        const parsed = await documentApi.parse(kblock.state.content, 'COMFORTABLE');
        setSceneGraph(parsed.scene_graph as SceneGraph);
      } catch (err) {
        console.error('[SpecView] Failed to reparse content:', err);
      }
    }

    reparse();
  }, [kblock.state.content]);

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

  // Handle task toggle via K-Block view_edit
  const handleTaskToggle = useCallback(
    async (_newState: boolean, taskId?: string) => {
      if (!taskId || !kblock.state.blockId) return;

      try {
        // Toggle task in the content
        // For now, use the document API directly (task toggle is a special case)
        await documentApi.toggleTask({
          file_path: path,
          task_id: taskId,
        });

        // Refresh K-Block content
        await kblock.refresh();
      } catch (err) {
        console.error('[SpecView] Failed to toggle task:', err);
        throw err; // Re-throw so TaskCheckboxToken can revert
      }
    },
    [path, kblock]
  );

  // Handle save
  const handleSave = useCallback(async () => {
    setIsSaving(true);
    try {
      const result = await kblock.save('Kent saved from Membrane');
      if (!result.success) {
        console.error('[SpecView] Failed to save:', result.error);
      }
    } finally {
      setIsSaving(false);
    }
  }, [kblock]);

  // Handle discard
  const handleDiscard = useCallback(async () => {
    await kblock.discard();
    // Re-create K-Block with fresh content
    await kblock.create(path);
  }, [kblock, path]);

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
    <div className="spec-view" data-isolation={kblock.state.isolation}>
      {/* K-Block isolation badge - shows when we have a K-Block */}
      {kblock.state.blockId && (
        <IsolationBadge
          isolation={kblock.state.isolation}
          isDirty={kblock.state.isDirty}
          onSave={handleSave}
          onDiscard={handleDiscard}
          isSaving={isSaving}
        />
      )}

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

      {/* References panel - discovered from K-Block */}
      <ReferencesPanel references={references} onNavigate={onNavigate} />

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
