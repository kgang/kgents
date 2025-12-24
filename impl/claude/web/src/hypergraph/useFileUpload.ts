/**
 * useFileUpload — File upload and sovereign store ingest hook
 *
 * Handles:
 * - File upload from FileExplorer
 * - Ingest into sovereign store with witnessing
 * - Local cache fallback for offline mode
 * - Custom loadNode that checks cache first
 * - Upload status tracking (uploading → processing → ready)
 */

import { useCallback, useRef, useState, useEffect } from 'react';
import { sovereignApi } from '../api/client';
import { useGraphNode } from './useGraphNode';
import { useWitnessStream } from '../hooks/useWitnessStream';
import type { GraphNode } from './state/types';
import type { UploadedFile } from './FileExplorer';

/**
 * Upload status states:
 * - uploading: File being sent to server
 * - processing: Server analyzing/processing the document
 * - ready: Analysis complete, document ready for use
 * - failed: Upload or processing failed
 */
export type UploadStatus = 'uploading' | 'processing' | 'ready' | 'failed';

export interface UseFileUploadOptions {
  onFileReady?: (path: string) => void;
}

export interface UseFileUploadReturn {
  loadNode: (path: string) => Promise<GraphNode | null>;
  handleUploadFile: (file: UploadedFile) => Promise<void>;
  uploadStatus: Map<string, UploadStatus>;
  setUploadStatus: React.Dispatch<React.SetStateAction<Map<string, UploadStatus>>>;
}

export function useFileUpload(options: UseFileUploadOptions = {}): UseFileUploadReturn {
  const { onFileReady } = options;
  const graphNode = useGraphNode();
  const localFilesRef = useRef<Map<string, GraphNode>>(new Map());

  // Upload status tracking
  const [uploadStatus, setUploadStatus] = useState<Map<string, UploadStatus>>(new Map());

  // Listen for analysis completion events via witness stream
  const { events } = useWitnessStream();

  // Track analysis completion from SSE events
  useEffect(() => {
    // Find completed analysis events (sovereign type events with analysis completion)
    const analysisCompleted = events.filter(
      (e) =>
        e.type === 'sovereign' &&
        (e.action === 'analysis_completed' || e.action === 'analyzed')
    );

    for (const event of analysisCompleted) {
      const path = event.path;
      if (path && uploadStatus.has(path)) {
        setUploadStatus((prev) => {
          const newStatus = new Map(prev);
          newStatus.set(path, 'ready');
          return newStatus;
        });
        console.info('[useFileUpload] Analysis completed for:', path);
      }
    }
  }, [events, uploadStatus]);

  // Custom loadNode that checks local cache first, then sovereign store
  const loadNode = useCallback(
    async (path: string): Promise<GraphNode | null> => {
      // Check local cache first (for uploaded files)
      const localNode = localFilesRef.current.get(path);
      console.info('[useFileUpload] loadNode called:', {
        path,
        cacheKeys: Array.from(localFilesRef.current.keys()),
        foundInCache: !!localNode,
        hasContent: localNode?.content ? localNode.content.length : 0,
      });
      if (localNode) {
        console.info('[useFileUpload] Loading from local cache:', path, 'content length:', localNode.content?.length);
        return localNode;
      }

      // For uploaded files (uploads/ prefix), try sovereign store first
      if (path.startsWith('uploads/')) {
        try {
          console.info('[useFileUpload] Trying sovereign store for:', path);
          const entity = await sovereignApi.getEntity(path);
          if (entity && entity.content) {
            console.info('[useFileUpload] Found in sovereign store:', path, 'content length:', entity.content.length);
            const ext = path.split('.').pop()?.toLowerCase() || '';
            const kind: GraphNode['kind'] =
              ext === 'md' ? 'doc' : ext === 'py' || ext === 'ts' || ext === 'tsx' ? 'implementation' : 'unknown';

            const node: GraphNode = {
              path,
              title: path.split('/').pop()?.replace(/\.[^.]+$/, '') || path,
              kind,
              confidence: 1.0,
              content: entity.content,
              outgoingEdges: [],
              incomingEdges: [],
            };

            // Cache it for future use
            localFilesRef.current.set(path, node);
            return node;
          }
        } catch (err) {
          console.warn('[useFileUpload] Sovereign store lookup failed:', err);
        }
      }

      // Fall back to graph API (which doesn't include content for sovereignty reasons)
      console.info('[useFileUpload] Falling back to graphNode.loadNode for:', path);
      return graphNode.loadNode(path);
    },
    [graphNode]
  );

  // Handle file upload - ingest into sovereign store
  const handleUploadFile = useCallback(
    async (file: UploadedFile) => {
      const fileName = file.name;
      const uploadPath = `uploads/${fileName}`;

      console.info('[useFileUpload] File uploaded:', fileName, `(${file.content.length} bytes)`);

      // 1. Set status = "uploading"
      setUploadStatus((prev) => new Map(prev).set(uploadPath, 'uploading'));

      const createLocalNode = (path: string): GraphNode => {
        const ext = fileName.split('.').pop()?.toLowerCase() || '';
        const kind: GraphNode['kind'] =
          ext === 'md' ? 'doc' : ext === 'py' || ext === 'ts' || ext === 'tsx' ? 'implementation' : 'unknown';

        return {
          path,
          title: fileName.replace(/\.[^.]+$/, ''),
          kind,
          confidence: 1.0,
          content: file.content,
          outgoingEdges: [],
          incomingEdges: [],
        };
      };

      try {
        // Ingest into sovereign store via AGENTESE
        const ingestResult = await sovereignApi.ingest({
          path: uploadPath,
          content: file.content,
          source: 'file-upload',
        });

        console.info(
          '[useFileUpload] Ingested to sovereign store:',
          ingestResult.path,
          `v${ingestResult.version}`,
          `(${ingestResult.edge_count} edges, mark: ${ingestResult.ingest_mark_id})`
        );

        // 2. Set status = "processing" (analysis in progress)
        setUploadStatus((prev) => new Map(prev).set(ingestResult.path, 'processing'));

        // Store in local cache
        const localNode = createLocalNode(ingestResult.path);
        localFilesRef.current.set(ingestResult.path, localNode);
        console.info('[useFileUpload] Cached node:', {
          path: ingestResult.path,
          contentLength: localNode.content?.length,
          cacheSize: localFilesRef.current.size,
        });

        // Notify caller (analysis continues in background, SSE will update status to 'ready')
        onFileReady?.(ingestResult.path);
      } catch (err) {
        console.error('[useFileUpload] Failed to ingest file:', err);

        // Set status = "failed"
        setUploadStatus((prev) => new Map(prev).set(uploadPath, 'failed'));

        // Fallback: store locally if ingest fails
        const localNode = createLocalNode(uploadPath);
        localFilesRef.current.set(uploadPath, localNode);
        console.info('[useFileUpload] Cached node (fallback):', {
          path: uploadPath,
          contentLength: localNode.content?.length,
          cacheSize: localFilesRef.current.size,
        });

        // Notify caller with fallback path
        onFileReady?.(uploadPath);
      }
    },
    [onFileReady]
  );

  return { loadNode, handleUploadFile, uploadStatus, setUploadStatus };
}
