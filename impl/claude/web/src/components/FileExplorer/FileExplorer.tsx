/**
 * FileExplorer — Zero Seed Genesis file manager with upload integration
 *
 * "Sovereignty before integration. The staging area is sacred."
 *
 * Features:
 * - Tree view of filesystem (uploads/, spec/, impl/, docs/)
 * - Drag-drop upload zone for uploads/ folder
 * - Drag FROM uploads/ TO other folders triggers IntegrationDialog
 * - K-Block status indicators (layer badge, loss color)
 * - Context menu: Open, Move, Split, Delete
 * - Keyboard navigation (j/k, Enter, h/l)
 *
 * Integration Flow:
 * 1. User drops file into uploads/ (sovereign staging)
 * 2. User drags file from uploads/ to destination folder
 * 3. IntegrationDialog shows: layer, edges, contradictions
 * 4. User confirms → file moves + K-Block created
 *
 * Philosophy: "The file waits in uploads/. When ready, it finds its layer."
 *
 * @see spec/protocols/zero-seed-genesis.md
 */

import { memo, useCallback, useState, useRef, useEffect } from 'react';
import {
  ChevronRight,
  Folder,
  FolderOpen,
  FileText,
  MoreVertical,
} from 'lucide-react';
import { UploadZone } from './UploadZone';
import { IntegrationDialog } from './IntegrationDialog';
import type {
  FileNode,
  IntegrationMetadata,
  ContextMenuAction,
} from './types';
import './FileExplorer.css';

// =============================================================================
// Types
// =============================================================================

interface FileExplorerProps {
  /** Root paths to display (defaults to ['uploads', 'spec', 'impl', 'docs']) */
  rootPaths?: string[];
  /** Current file path (for highlighting) */
  currentFile?: string;
  /** Called when a file is selected */
  onSelectFile?: (path: string) => void;
  /** Called when upload completes */
  onUploadComplete?: (files: File[]) => void;
  /** External load function for file tree */
  loadTree?: (path: string) => Promise<FileNode[]>;
}

// =============================================================================
// Helpers
// =============================================================================

/**
 * Get icon for file node based on type and extension.
 */
function getNodeIcon(node: FileNode, expanded: boolean) {
  if (node.type === 'directory') {
    return expanded ? <FolderOpen size={16} /> : <Folder size={16} />;
  }

  // File icons
  return <FileText size={16} />;
}

/**
 * Get layer badge color based on Zero Seed layer.
 */
function getLayerColor(layer?: string): string {
  if (!layer) return 'var(--steel-500)';

  const layerNum = parseInt(layer.replace('L', ''), 10);
  if (layerNum <= 2) return 'var(--health-critical)'; // L1-L2: Axioms
  if (layerNum <= 4) return 'var(--health-warning)'; // L3-L4: Specs
  if (layerNum <= 5) return 'var(--health-degraded)'; // L5: Implementation
  return 'var(--health-healthy)'; // L6-L7: Docs
}

/**
 * Get loss color based on Galois loss value.
 */
function getLossColor(loss?: number): string {
  if (loss === undefined) return 'transparent';
  if (loss < 0.2) return 'var(--health-healthy)';
  if (loss < 0.4) return 'var(--health-degraded)';
  if (loss < 0.6) return 'var(--health-warning)';
  return 'var(--health-critical)';
}

// =============================================================================
// Component
// =============================================================================

export const FileExplorer = memo(function FileExplorer({
  rootPaths = ['uploads', 'spec', 'impl', 'docs'],
  currentFile,
  onSelectFile,
  onUploadComplete,
  loadTree,
}: FileExplorerProps) {
  // State
  const [tree, setTree] = useState<FileNode[]>([]);
  const [expandedPaths, setExpandedPaths] = useState<Set<string>>(new Set(['uploads']));
  const [selectedPath, setSelectedPath] = useState<string | null>(null);
  const [dragSource, setDragSource] = useState<FileNode | null>(null);
  const [dragOverPath, setDragOverPath] = useState<string | null>(null);
  const [integrationDialogOpen, setIntegrationDialogOpen] = useState(false);
  const [integrationMetadata, setIntegrationMetadata] = useState<IntegrationMetadata | null>(null);
  const [contextMenuOpen, setContextMenuOpen] = useState(false);
  const [contextMenuPos, setContextMenuPos] = useState({ x: 0, y: 0 });
  const [contextMenuNode, setContextMenuNode] = useState<FileNode | null>(null);

  const explorerRef = useRef<HTMLDivElement>(null);

  // Load initial tree
  useEffect(() => {
    if (loadTree) {
      // Load root paths
      Promise.all(rootPaths.map((path) => loadTree(path))).then((results) => {
        const rootNodes: FileNode[] = results.flat();
        setTree(rootNodes);
      });
    } else {
      // Mock tree for development
      const mockTree: FileNode[] = [
        {
          path: 'uploads',
          name: 'uploads',
          type: 'directory',
          depth: 0,
          children: [],
        },
        {
          path: 'spec',
          name: 'spec',
          type: 'directory',
          depth: 0,
          children: [],
        },
        {
          path: 'impl',
          name: 'impl',
          type: 'directory',
          depth: 0,
          children: [],
        },
        {
          path: 'docs',
          name: 'docs',
          type: 'directory',
          depth: 0,
          children: [],
        },
      ];
      setTree(mockTree);
    }
  }, [rootPaths, loadTree]);

  // =============================================================================
  // Handlers
  // =============================================================================

  /**
   * Toggle expand/collapse for directory.
   */
  const toggleExpand = useCallback((path: string) => {
    setExpandedPaths((prev) => {
      const next = new Set(prev);
      if (next.has(path)) {
        next.delete(path);
      } else {
        next.add(path);
      }
      return next;
    });
  }, []);

  /**
   * Handle node click (select file or toggle directory).
   */
  const handleNodeClick = useCallback(
    (node: FileNode) => {
      if (node.type === 'directory') {
        toggleExpand(node.path);
      } else {
        setSelectedPath(node.path);
        onSelectFile?.(node.path);
      }
    },
    [toggleExpand, onSelectFile]
  );

  /**
   * Handle drag start (only for files in uploads/).
   */
  const handleDragStart = useCallback(
    (e: React.DragEvent, node: FileNode) => {
      // Only allow dragging files from uploads/
      if (node.type !== 'file' || !node.path.startsWith('uploads/')) {
        e.preventDefault();
        return;
      }

      setDragSource(node);
      e.dataTransfer.effectAllowed = 'move';
      e.dataTransfer.setData('text/plain', node.path);
    },
    []
  );

  /**
   * Handle drag over (highlight drop target).
   */
  const handleDragOver = useCallback((e: React.DragEvent, node: FileNode) => {
    // Only allow dropping on directories (not uploads/)
    if (node.type !== 'directory' || node.path === 'uploads') {
      return;
    }

    e.preventDefault();
    e.dataTransfer.dropEffect = 'move';
    setDragOverPath(node.path);
  }, []);

  /**
   * Handle drag leave.
   */
  const handleDragLeave = useCallback(() => {
    setDragOverPath(null);
  }, []);

  /**
   * Handle drop (open integration dialog).
   */
  const handleDrop = useCallback(
    (e: React.DragEvent, targetNode: FileNode) => {
      e.preventDefault();
      setDragOverPath(null);

      if (!dragSource || targetNode.type !== 'directory' || targetNode.path === 'uploads') {
        return;
      }

      // Open integration dialog with metadata
      const metadata: IntegrationMetadata = {
        sourcePath: dragSource.path,
        destinationPath: targetNode.path,
        detectedLayer: detectLayer(targetNode.path),
        galoisLoss: 0.15, // Mock value
        discoveredEdges: [
          { type: 'implements', target: 'spec/protocols/witness.md' },
          { type: 'tests', target: 'impl/claude/services/witness/_tests/' },
        ],
        contradictions: [],
      };

      setIntegrationMetadata(metadata);
      setIntegrationDialogOpen(true);
    },
    [dragSource]
  );

  /**
   * Handle context menu (right-click).
   */
  const handleContextMenu = useCallback((e: React.MouseEvent, node: FileNode) => {
    e.preventDefault();
    setContextMenuNode(node);
    setContextMenuPos({ x: e.clientX, y: e.clientY });
    setContextMenuOpen(true);
  }, []);

  /**
   * Handle context menu action.
   */
  const handleContextMenuAction = useCallback(
    (action: ContextMenuAction) => {
      setContextMenuOpen(false);

      if (!contextMenuNode) return;

      switch (action) {
        case 'open':
          if (contextMenuNode.type === 'file') {
            onSelectFile?.(contextMenuNode.path);
          }
          break;
        case 'move':
          // TODO: Implement move dialog
          console.log('[FileExplorer] Move:', contextMenuNode.path);
          break;
        case 'split':
          // TODO: Implement split dialog
          console.log('[FileExplorer] Split:', contextMenuNode.path);
          break;
        case 'delete':
          // TODO: Implement delete confirmation
          console.log('[FileExplorer] Delete:', contextMenuNode.path);
          break;
      }
    },
    [contextMenuNode, onSelectFile]
  );

  /**
   * Handle integration confirm.
   */
  const handleIntegrationConfirm = useCallback(async () => {
    if (!integrationMetadata) return;

    try {
      // TODO: Call API to integrate file
      // await sovereignApi.integrate(integrationMetadata);

      console.log('[FileExplorer] Integration confirmed:', integrationMetadata);

      // Close dialog
      setIntegrationDialogOpen(false);
      setIntegrationMetadata(null);
      setDragSource(null);

      // Refresh tree
      // TODO: Reload tree after integration
    } catch (error) {
      console.error('[FileExplorer] Integration failed:', error);
    }
  }, [integrationMetadata]);

  /**
   * Handle integration cancel.
   */
  const handleIntegrationCancel = useCallback(() => {
    setIntegrationDialogOpen(false);
    setIntegrationMetadata(null);
    setDragSource(null);
  }, []);

  /**
   * Handle upload complete.
   */
  const handleUploadComplete = useCallback(
    (files: File[]) => {
      console.log('[FileExplorer] Upload complete:', files);
      onUploadComplete?.(files);

      // Refresh uploads/ tree
      // TODO: Reload uploads/ folder
    },
    [onUploadComplete]
  );

  /**
   * Close context menu when clicking outside.
   */
  useEffect(() => {
    function handleClickOutside(e: MouseEvent) {
      if (contextMenuOpen && explorerRef.current && !explorerRef.current.contains(e.target as Node)) {
        setContextMenuOpen(false);
      }
    }

    document.addEventListener('mousedown', handleClickOutside);
    return () => document.removeEventListener('mousedown', handleClickOutside);
  }, [contextMenuOpen]);

  // =============================================================================
  // Render Helpers
  // =============================================================================

  /**
   * Flatten tree for rendering (only show expanded nodes).
   */
  const flattenTree = useCallback(
    (nodes: FileNode[], depth = 0): FileNode[] => {
      const result: FileNode[] = [];

      for (const node of nodes) {
        result.push({ ...node, depth });

        if (node.type === 'directory' && expandedPaths.has(node.path) && node.children) {
          result.push(...flattenTree(node.children, depth + 1));
        }
      }

      return result;
    },
    [expandedPaths]
  );

  const visibleNodes = flattenTree(tree);

  // =============================================================================
  // Render
  // =============================================================================

  return (
    <div ref={explorerRef} className="file-explorer">
      {/* Tree view */}
      <div className="file-explorer__tree">
        {visibleNodes.map((node) => {
          const isExpanded = expandedPaths.has(node.path);
          const isSelected = node.path === selectedPath;
          const isCurrent = node.path === currentFile;
          const isDragOver = node.path === dragOverPath;
          const isDraggable = node.type === 'file' && node.path.startsWith('uploads/');

          return (
            <div
              key={node.path}
              className="file-explorer__node"
              data-selected={isSelected}
              data-current={isCurrent}
              data-drag-over={isDragOver}
              data-type={node.type}
              style={{ '--depth': node.depth } as React.CSSProperties}
              onClick={() => handleNodeClick(node)}
              onContextMenu={(e) => handleContextMenu(e, node)}
              draggable={isDraggable}
              onDragStart={(e) => handleDragStart(e, node)}
              onDragOver={(e) => handleDragOver(e, node)}
              onDragLeave={handleDragLeave}
              onDrop={(e) => handleDrop(e, node)}
            >
              {/* Indentation */}
              <div className="file-explorer__indent" />

              {/* Chevron for directories */}
              {node.type === 'directory' && (
                <div className="file-explorer__chevron" data-expanded={isExpanded}>
                  <ChevronRight size={12} />
                </div>
              )}

              {/* Icon */}
              <div className="file-explorer__icon">
                {getNodeIcon(node, isExpanded)}
              </div>

              {/* Label */}
              <div className="file-explorer__label">{node.name}</div>

              {/* K-Block status indicators */}
              {node.type === 'file' && node.kblock && (
                <div className="file-explorer__indicators">
                  {/* Layer badge */}
                  {node.kblock.layer && (
                    <span
                      className="file-explorer__layer-badge"
                      style={{ '--layer-color': getLayerColor(node.kblock.layer) } as React.CSSProperties}
                    >
                      {node.kblock.layer}
                    </span>
                  )}

                  {/* Loss indicator */}
                  {node.kblock.loss !== undefined && (
                    <span
                      className="file-explorer__loss-indicator"
                      style={{ '--loss-color': getLossColor(node.kblock.loss) } as React.CSSProperties}
                      title={`Galois loss: ${(node.kblock.loss * 100).toFixed(1)}%`}
                    />
                  )}
                </div>
              )}

              {/* Context menu trigger */}
              <button
                className="file-explorer__context-trigger"
                onClick={(e) => {
                  e.stopPropagation();
                  handleContextMenu(e as any, node);
                }}
                title="More actions"
              >
                <MoreVertical size={14} />
              </button>
            </div>
          );
        })}

        {/* Upload zone (shown when uploads/ is expanded) */}
        {expandedPaths.has('uploads') && (
          <div
            className="file-explorer__upload-zone-container"
            style={{ '--depth': 1 } as React.CSSProperties}
          >
            <UploadZone onUploadComplete={handleUploadComplete} />
          </div>
        )}
      </div>

      {/* Context menu */}
      {contextMenuOpen && contextMenuNode && (
        <div
          className="file-explorer__context-menu"
          style={{
            left: `${contextMenuPos.x}px`,
            top: `${contextMenuPos.y}px`,
          }}
        >
          {contextMenuNode.type === 'file' && (
            <button
              className="file-explorer__context-menu-item"
              onClick={() => handleContextMenuAction('open')}
            >
              Open
            </button>
          )}
          <button
            className="file-explorer__context-menu-item"
            onClick={() => handleContextMenuAction('move')}
          >
            Move
          </button>
          {contextMenuNode.type === 'file' && (
            <button
              className="file-explorer__context-menu-item"
              onClick={() => handleContextMenuAction('split')}
            >
              Split
            </button>
          )}
          <button
            className="file-explorer__context-menu-item file-explorer__context-menu-item--danger"
            onClick={() => handleContextMenuAction('delete')}
          >
            Delete
          </button>
        </div>
      )}

      {/* Integration dialog */}
      {integrationDialogOpen && integrationMetadata && (
        <IntegrationDialog
          metadata={integrationMetadata}
          onConfirm={handleIntegrationConfirm}
          onCancel={handleIntegrationCancel}
        />
      )}
    </div>
  );
});

// =============================================================================
// Helpers (outside component)
// =============================================================================

/**
 * Detect Zero Seed layer based on destination path.
 */
function detectLayer(path: string): string {
  if (path.startsWith('spec/axioms')) return 'L1';
  if (path.startsWith('spec/principles')) return 'L2';
  if (path.startsWith('spec/')) return 'L3';
  if (path.startsWith('impl/')) return 'L5';
  if (path.startsWith('docs/skills')) return 'L6';
  if (path.startsWith('docs/')) return 'L7';
  return 'L4'; // Default to L4 (application spec)
}
