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

import { useCallback, useEffect, useMemo, useRef, useState } from 'react';

import { documentApi, sovereignApi } from '../../api/client';
import { EmpathyError } from '../../components/joy/EmpathyError';
import { GrowingContainer } from '../../components/genesis/GrowingContainer';
import { PersonalityLoading } from '../../components/joy/PersonalityLoading';

import { InteractiveDocument, type SceneGraph } from '../tokens';
import { useSpecQuery, type EdgeType } from '../useSpecNavigation';
import { useFileKBlock, type KBlockReference, type KBlockCreateResult } from '../useKBlock';
import { useWitnessStream, type WitnessEvent } from '../useWitnessStream';
import { EditPane } from './EditPane';

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
// Witness Components
// =============================================================================

interface WitnessPaneProps {
  events: WitnessEvent[];
  connected: boolean;
  onReconnect: () => void;
}

function WitnessPane({ events, connected, onReconnect }: WitnessPaneProps) {
  const [expanded, setExpanded] = useState(false);

  if (events.length === 0 && connected) {
    return null; // Nothing to show
  }

  return (
    <div className="spec-view__witness" data-connected={connected}>
      <button
        className="spec-view__witness-toggle"
        onClick={() => setExpanded(!expanded)}
        data-expanded={expanded}
      >
        <span className="spec-view__witness-icon">{expanded ? '\u25BC' : '\u25B6'}</span>
        <span className="spec-view__witness-title">Witness Stream</span>
        <span className="spec-view__witness-status" data-connected={connected}>
          {connected ? '\u25CF' : '\u25CB'}
        </span>
        {events.length > 0 && <span className="spec-view__witness-count">({events.length})</span>}
      </button>

      {!connected && (
        <button className="spec-view__witness-reconnect" onClick={onReconnect}>
          Reconnect
        </button>
      )}

      {expanded && (
        <GrowingContainer>
          <ul className="spec-view__witness-list">
            {events.slice(0, 10).map((event) => (
              <li key={event.id} className="spec-view__witness-event" data-type={event.type}>
                <span className="spec-view__witness-event-type">{event.type}</span>
                <span className="spec-view__witness-event-action">
                  {event.action || event.content || event.insight || 'Event'}
                </span>
                {event.reasoning && (
                  <span className="spec-view__witness-event-reasoning">{event.reasoning}</span>
                )}
                <span className="spec-view__witness-event-time">
                  {event.timestamp.toLocaleTimeString()}
                </span>
              </li>
            ))}
            {events.length > 10 && (
              <li className="spec-view__witness-more">+{events.length - 10} more events</li>
            )}
          </ul>
        </GrowingContainer>
      )}
    </div>
  );
}

// =============================================================================
// Error/Loading/NotIngested State Components (Extracted for complexity)
// =============================================================================

interface SpecErrorViewProps {
  error: string;
}

function SpecErrorView({ error }: SpecErrorViewProps) {
  return (
    <div className="spec-view spec-view--error">
      <EmpathyError type="notfound" title="Spec not accessible" subtitle={error} />
    </div>
  );
}

function SpecLoadingView() {
  return (
    <div className="spec-view spec-view--loading">
      <PersonalityLoading jewel="brain" action="analyze" size="md" />
    </div>
  );
}

interface SpecNotIngestedViewProps {
  path: string;
  ingestHint: string;
  ingestError: string | null;
  isIngesting: boolean;
  fileInputRef: React.RefObject<HTMLInputElement>;
  onIngestFile: (e: React.ChangeEvent<HTMLInputElement>) => void;
}

function SpecNotIngestedView({
  path,
  ingestHint,
  ingestError,
  isIngesting,
  fileInputRef,
  onIngestFile,
}: SpecNotIngestedViewProps) {
  return (
    <div className="spec-view spec-view--not-ingested">
      <div className="spec-view__not-ingested">
        <div className="spec-view__not-ingested-icon">📦</div>
        <h3 className="spec-view__not-ingested-title">Content Not Ingested</h3>
        <p className="spec-view__not-ingested-message">
          This document hasn't been uploaded to the sovereign store yet.
        </p>
        <div className="spec-view__not-ingested-path">
          <code>{path}</code>
        </div>
        <div className="spec-view__not-ingested-hint">{ingestHint}</div>
        {ingestError && <div className="spec-view__not-ingested-error">{ingestError}</div>}
        <div className="spec-view__not-ingested-actions">
          <input
            type="file"
            ref={fileInputRef}
            onChange={onIngestFile}
            accept=".md,.txt,.markdown"
            style={{ display: 'none' }}
          />
          <button
            className="spec-view__upload-btn"
            onClick={() => fileInputRef.current?.click()}
            disabled={isIngesting}
          >
            {isIngesting ? 'Uploading...' : 'Upload Content'}
          </button>
        </div>
      </div>
    </div>
  );
}

// =============================================================================
// Header Components (Extracted for complexity)
// =============================================================================

interface SpecHeaderProps {
  node: {
    title: string;
    path: string;
    tier: string;
    confidence: number;
    agentese_path?: string;
    derives_from: string[];
  } | null;
  path: string;
  showMetadata: boolean;
  onNavigate?: (path: string) => void;
}

function SpecHeader({ node, path, showMetadata, onNavigate }: SpecHeaderProps) {
  if (showMetadata && node) {
    return (
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
    );
  }

  return (
    <header className="spec-view__header">
      <div className="spec-view__title-row">
        <h2 className="spec-view__title">{path.split('/').pop()}</h2>
      </div>
      <div className="spec-view__meta">
        <span className="spec-view__path">{path}</span>
      </div>
    </header>
  );
}

// =============================================================================
// Content Components (Extracted for complexity)
// =============================================================================

interface SpecContentProps {
  editMode: boolean;
  editContent: string;
  contentLoading: boolean;
  contentError: string | null;
  sceneGraph: SceneGraph | null;
  path: string;
  isApplyingEdit: boolean;
  onEditChange: (content: string) => void;
  onApplyEdit: () => void;
  onCancelEdit: () => void;
  onEnterEdit: () => void;
  onTokenNavigate: (agentesePath: string) => void;
  onTaskToggle: (newState: boolean, taskId?: string) => Promise<void>;
}

function SpecContent({
  editMode,
  editContent,
  contentLoading,
  contentError,
  sceneGraph,
  path,
  isApplyingEdit,
  onEditChange,
  onApplyEdit,
  onCancelEdit,
  onEnterEdit,
  onTokenNavigate,
  onTaskToggle,
}: SpecContentProps) {
  if (editMode) {
    return (
      <EditPane
        content={editContent}
        onChange={onEditChange}
        onSave={onApplyEdit}
        onCancel={onCancelEdit}
        isSaving={isApplyingEdit}
        path={path}
      />
    );
  }

  if (contentLoading) {
    return <div className="spec-view__content-loading">Loading content...</div>;
  }

  if (contentError) {
    return (
      <div className="spec-view__content-error">
        <p>Failed to load content</p>
        <p className="spec-view__content-hint">{contentError}</p>
      </div>
    );
  }

  if (sceneGraph) {
    return (
      <>
        <InteractiveDocument
          sceneGraph={sceneGraph}
          onNavigate={onTokenNavigate}
          onToggle={onTaskToggle}
          className="spec-view__interactive"
        />
        <button
          className="spec-view__edit-btn"
          onClick={onEnterEdit}
          title="Edit this spec (enters K-Block isolation)"
        >
          Edit
        </button>
      </>
    );
  }

  return (
    <div className="spec-view__content-empty">
      <p>Content not available</p>
      <p className="spec-view__content-hint">Use edge portals above to navigate the spec graph</p>
    </div>
  );
}

// =============================================================================
// Helper: Parse AGENTESE path to navigation target
// =============================================================================

function parseAgentesePath(agentesePath: string, onNavigate?: (path: string) => void): void {
  const parts = agentesePath.split('.');
  const context = parts[0]; // self, world, concept, void, time
  const isConcept = context === 'concept' && parts[1];

  if (isConcept) {
    onNavigate?.(`concept/${parts.slice(1).join('/')}`);
  } else {
    console.info('[SpecView] Navigate to AGENTESE path:', agentesePath);
    onNavigate?.(agentesePath);
  }
}

// =============================================================================
// Helper: Extract error message from unknown error
// =============================================================================

function getErrorMessage(err: unknown, fallback: string): string {
  return err instanceof Error ? err.message : fallback;
}

// =============================================================================
// Hook: Edit mode handlers (extracted to reduce main component complexity)
// =============================================================================

interface EditHandlers {
  handleEnterEdit: () => void;
  handleApplyEdit: () => Promise<void>;
  handleCancelEdit: () => void;
  editMode: boolean;
  editContent: string;
  isApplyingEdit: boolean;
  setEditContent: (content: string) => void;
}

function useEditMode(
  kblock: ReturnType<typeof useFileKBlock>,
  setSceneGraph: (graph: SceneGraph | null) => void
): EditHandlers {
  const [editMode, setEditMode] = useState(false);
  const [editContent, setEditContent] = useState('');
  const [isApplyingEdit, setIsApplyingEdit] = useState(false);

  const handleEnterEdit = useCallback(() => {
    setEditContent(kblock.state.content);
    setEditMode(true);
  }, [kblock.state.content]);

  const handleApplyEdit = useCallback(async () => {
    if (!kblock.state.blockId) return;

    setIsApplyingEdit(true);
    try {
      const result = await kblock.viewEdit('prose', editContent, 'Kent edited in Membrane');
      if (result.success) {
        setEditMode(false);
        const parsed = await documentApi.parse(editContent, 'COMFORTABLE');
        setSceneGraph(parsed.scene_graph as SceneGraph);
      } else {
        console.error('[SpecView] Failed to apply edit:', result.error);
      }
    } finally {
      setIsApplyingEdit(false);
    }
  }, [kblock, editContent, setSceneGraph]);

  const handleCancelEdit = useCallback(() => {
    setEditMode(false);
    setEditContent('');
  }, []);

  return {
    handleEnterEdit,
    handleApplyEdit,
    handleCancelEdit,
    editMode,
    editContent,
    isApplyingEdit,
    setEditContent,
  };
}

// =============================================================================
// Hook: Ingest handlers (extracted to reduce main component complexity)
// =============================================================================

interface IngestHandlers {
  handleIngestFile: (e: React.ChangeEvent<HTMLInputElement>) => Promise<void>;
  isIngesting: boolean;
  ingestError: string | null;
  fileInputRef: React.RefObject<HTMLInputElement>;
  clearIngestState: () => void;
}

function useIngestHandlers(
  path: string,
  kblock: ReturnType<typeof useFileKBlock>,
  setNotIngested: (value: boolean) => void,
  setIngestHint: (value: string) => void
): IngestHandlers {
  const [isIngesting, setIsIngesting] = useState(false);
  const [ingestError, setIngestError] = useState<string | null>(null);
  const fileInputRef = useRef<HTMLInputElement>(null);

  const handleIngestFile = useCallback(
    async (e: React.ChangeEvent<HTMLInputElement>) => {
      const file = e.target.files?.[0];
      if (!file) return;

      setIsIngesting(true);
      setIngestError(null);

      try {
        const content = await file.text();
        const result = await sovereignApi.ingest({ path, content, source: 'webapp-upload' });
        if (result.version) {
          setNotIngested(false);
          setIngestHint('');
          await kblock.create(path);
        }
      } catch (err) {
        console.error('[SpecView] Ingest failed:', err);
        setIngestError(getErrorMessage(err, 'Failed to ingest file'));
      } finally {
        setIsIngesting(false);
        if (fileInputRef.current) fileInputRef.current.value = '';
      }
    },
    [path, kblock, setNotIngested, setIngestHint]
  );

  const clearIngestState = useCallback(() => {
    setIngestError(null);
  }, []);

  return { handleIngestFile, isIngesting, ingestError, fileInputRef, clearIngestState };
}

// =============================================================================
// Hook: Content loading (extracted to reduce main component complexity)
// =============================================================================

interface ContentLoaderState {
  sceneGraph: SceneGraph | null;
  setSceneGraph: (graph: SceneGraph | null) => void;
  contentLoading: boolean;
  contentError: string | null;
  notIngested: boolean;
  ingestHint: string;
  setNotIngested: (value: boolean) => void;
  setIngestHint: (value: string) => void;
}

function useContentLoader(
  path: string,
  kblockCreate: (path: string) => Promise<KBlockCreateResult>
): ContentLoaderState {
  const [sceneGraph, setSceneGraph] = useState<SceneGraph | null>(null);
  const [contentLoading, setContentLoading] = useState(false);
  const [contentError, setContentError] = useState<string | null>(null);
  const [notIngested, setNotIngested] = useState(false);
  const [ingestHint, setIngestHint] = useState<string>('');

  useEffect(() => {
    let cancelled = false;

    async function loadContent() {
      setContentLoading(true);
      setContentError(null);
      setNotIngested(false);
      setIngestHint('');

      try {
        const result = await kblockCreate(path);
        if (cancelled) return;

        if (result.not_ingested) {
          setNotIngested(true);
          setIngestHint(result.ingest_hint || 'Upload content via File Picker');
          setContentLoading(false);
          return;
        }

        if (!result.success || !result.content) {
          throw new Error(result.error || 'Failed to create K-Block');
        }

        const parsed = await documentApi.parse(result.content, 'COMFORTABLE');
        if (!cancelled) setSceneGraph(parsed.scene_graph as SceneGraph);
      } catch (err) {
        if (!cancelled) {
          console.error('[SpecView] Failed to load content:', err);
          setContentError(getErrorMessage(err, 'Failed to load content'));
        }
      } finally {
        if (!cancelled) setContentLoading(false);
      }
    }

    loadContent();
    return () => {
      cancelled = true;
    };
  }, [path, kblockCreate]);

  return {
    sceneGraph,
    setSceneGraph,
    contentLoading,
    contentError,
    notIngested,
    ingestHint,
    setNotIngested,
    setIngestHint,
  };
}

// =============================================================================
// Hook: K-Block actions (save, discard, toggle) - extracted for complexity
// =============================================================================

interface KBlockActions {
  handleSave: () => Promise<void>;
  handleDiscard: () => Promise<void>;
  handleTaskToggle: (newState: boolean, taskId?: string) => Promise<void>;
  handleTokenNavigate: (agentesePath: string) => void;
  isSaving: boolean;
}

function useKBlockActions(
  path: string,
  kblock: ReturnType<typeof useFileKBlock>,
  onNavigate?: (path: string) => void
): KBlockActions {
  const [isSaving, setIsSaving] = useState(false);

  const handleSave = useCallback(async () => {
    setIsSaving(true);
    try {
      const result = await kblock.save('Kent saved from Membrane');
      if (!result.success) console.error('[SpecView] Failed to save:', result.error);
    } finally {
      setIsSaving(false);
    }
  }, [kblock]);

  const handleDiscard = useCallback(async () => {
    await kblock.discard();
    await kblock.create(path);
  }, [kblock, path]);

  const handleTaskToggle = useCallback(
    async (_newState: boolean, taskId?: string) => {
      const canToggle = taskId && kblock.state.blockId;
      if (!canToggle) return;

      try {
        await documentApi.toggleTask({ file_path: path, task_id: taskId });
        await kblock.refresh();
      } catch (err) {
        console.error('[SpecView] Failed to toggle task:', err);
        throw err;
      }
    },
    [path, kblock]
  );

  const handleTokenNavigate = useCallback(
    (agentesePath: string) => parseAgentesePath(agentesePath, onNavigate),
    [onNavigate]
  );

  return { handleSave, handleDiscard, handleTaskToggle, handleTokenNavigate, isSaving };
}

// =============================================================================
// Main Component
// =============================================================================

export function SpecView({ path, onNavigate, onEdgeClick }: SpecViewProps) {
  const { spec, loading, error, query } = useSpecQuery();
  const [references, _setReferences] = useState<KBlockReference[]>([]);

  // K-Block for transactional editing
  const kblock = useFileKBlock();

  // Content loading (extracted hook)
  const contentState = useContentLoader(path, kblock.create);

  // Edit mode handlers (extracted hook)
  const editHandlers = useEditMode(kblock, contentState.setSceneGraph);

  // Ingest handlers (extracted hook)
  const ingestHandlers = useIngestHandlers(
    path,
    kblock,
    contentState.setNotIngested,
    contentState.setIngestHint
  );

  // K-Block actions (extracted hook)
  const kblockActions = useKBlockActions(path, kblock, onNavigate);

  // Witness stream for real-time events
  const witness = useWitnessStream();

  // Filter witness events for current path
  const pathEvents = useMemo(
    () => witness.events.filter((e) => e.path === path || !e.path),
    [witness.events, path]
  );

  // Query SpecGraph for metadata
  useEffect(() => {
    if (path) query(path);
  }, [path, query]);

  // Compute render state (reduces branching in main function)
  const hasContent = contentState.sceneGraph !== null;
  const hasSpec = spec !== null;
  const shouldShowError = Boolean(error) && !hasContent && !contentState.contentLoading;
  const shouldShowLoading = loading && !hasContent;

  // Early return: Error state
  if (shouldShowError && error) return <SpecErrorView error={error} />;

  // Early return: Loading state
  if (shouldShowLoading) return <SpecLoadingView />;

  // Early return: Not ingested state
  if (contentState.notIngested) {
    return (
      <SpecNotIngestedView
        path={path}
        ingestHint={contentState.ingestHint}
        ingestError={ingestHandlers.ingestError}
        isIngesting={ingestHandlers.isIngesting}
        fileInputRef={ingestHandlers.fileInputRef}
        onIngestFile={ingestHandlers.handleIngestFile}
      />
    );
  }

  return (
    <SpecViewMain
      path={path}
      spec={spec}
      hasSpec={hasSpec}
      kblock={kblock}
      kblockActions={kblockActions}
      editHandlers={editHandlers}
      contentState={contentState}
      witness={witness}
      pathEvents={pathEvents}
      references={references}
      onNavigate={onNavigate}
      onEdgeClick={onEdgeClick}
    />
  );
}

// =============================================================================
// Main Render Component (extracted to reduce SpecView complexity)
// =============================================================================

interface SpecViewMainProps {
  path: string;
  spec: ReturnType<typeof useSpecQuery>['spec'];
  hasSpec: boolean;
  kblock: ReturnType<typeof useFileKBlock>;
  kblockActions: KBlockActions;
  editHandlers: EditHandlers;
  contentState: ContentLoaderState;
  witness: ReturnType<typeof useWitnessStream>;
  pathEvents: WitnessEvent[];
  references: KBlockReference[];
  onNavigate?: (path: string) => void;
  onEdgeClick?: (target: string, edge: EdgeType) => void;
}

function SpecViewMain({
  path,
  spec,
  hasSpec,
  kblock,
  kblockActions,
  editHandlers,
  contentState,
  witness,
  pathEvents,
  references,
  onNavigate,
  onEdgeClick,
}: SpecViewMainProps) {
  const hasKBlock = Boolean(kblock.state.blockId);
  const showWitnessPane = witness.connected || pathEvents.length > 0;
  const node = spec?.node ?? null;
  const edges = spec?.edges ?? {};
  const tokens = spec?.tokens ?? {};

  return (
    <div className="spec-view" data-isolation={kblock.state.isolation}>
      {hasKBlock && (
        <IsolationBadge
          isolation={kblock.state.isolation}
          isDirty={kblock.state.isDirty}
          onSave={kblockActions.handleSave}
          onDiscard={kblockActions.handleDiscard}
          isSaving={kblockActions.isSaving}
        />
      )}

      <SpecHeader node={node} path={path} showMetadata={hasSpec} onNavigate={onNavigate} />

      {hasSpec && <TokenBadges tokens={tokens} />}

      {hasSpec && <EdgePortals edges={edges} onNavigate={onNavigate} onEdgeClick={onEdgeClick} />}

      <ReferencesPanel references={references} onNavigate={onNavigate} />

      {showWitnessPane && (
        <WitnessPane
          events={pathEvents}
          connected={witness.connected}
          onReconnect={witness.reconnect}
        />
      )}

      <div className="spec-view__content">
        <SpecContent
          editMode={editHandlers.editMode}
          editContent={editHandlers.editContent}
          contentLoading={contentState.contentLoading}
          contentError={contentState.contentError}
          sceneGraph={contentState.sceneGraph}
          path={path}
          isApplyingEdit={editHandlers.isApplyingEdit}
          onEditChange={editHandlers.setEditContent}
          onApplyEdit={editHandlers.handleApplyEdit}
          onCancelEdit={editHandlers.handleCancelEdit}
          onEnterEdit={editHandlers.handleEnterEdit}
          onTokenNavigate={kblockActions.handleTokenNavigate}
          onTaskToggle={kblockActions.handleTaskToggle}
        />
      </div>
    </div>
  );
}
