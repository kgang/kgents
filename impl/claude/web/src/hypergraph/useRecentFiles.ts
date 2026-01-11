/**
 * useRecentFiles — Persist and manage recently opened files
 *
 * Uses localStorage for persistence across sessions.
 * Limits to 10 recent files, de-duplicates, and maintains order.
 *
 * Validates files against Director API to filter out deleted files.
 */

import { useCallback, useEffect, useRef, useState } from 'react';
import { getDocument } from '../api/director';

const STORAGE_KEY = 'kgents:recent-files';
const MAX_RECENT = 10;

export interface UseRecentFilesReturn {
  recentFiles: string[];
  addRecentFile: (path: string) => void;
  clearRecentFiles: () => void;
  removeRecentFile: (path: string) => void;
}

export function useRecentFiles(): UseRecentFilesReturn {
  const [recentFiles, setRecentFiles] = useState<string[]>(() => {
    try {
      const stored = localStorage.getItem(STORAGE_KEY);
      if (stored) {
        const parsed = JSON.parse(stored);
        if (Array.isArray(parsed)) {
          return parsed.slice(0, MAX_RECENT);
        }
      }
    } catch (e) {
      console.warn('[useRecentFiles] Failed to parse localStorage:', e);
    }
    return [];
  });

  // Track if we're currently validating to prevent infinite loops
  const isValidatingRef = useRef(false);

  // Persist to localStorage whenever recentFiles changes
  useEffect(() => {
    try {
      localStorage.setItem(STORAGE_KEY, JSON.stringify(recentFiles));
    } catch (e) {
      console.warn('[useRecentFiles] Failed to persist to localStorage:', e);
    }
  }, [recentFiles]);

  // Validate recent files against Director API on mount
  // This ensures deleted files are removed when the FileExplorer is shown
  useEffect(() => {
    async function validateRecentFiles() {
      if (recentFiles.length === 0 || isValidatingRef.current) return;

      isValidatingRef.current = true;
      const validatedPaths: string[] = [];

      for (const path of recentFiles) {
        try {
          // Try to fetch the document - if it exists, keep it
          await getDocument(path);
          validatedPaths.push(path);
        } catch (error) {
          // Document doesn't exist or API error - remove from recent
          console.info('[useRecentFiles] Removing deleted file from recent:', path);
        }
      }

      // Only update if the list changed
      if (validatedPaths.length !== recentFiles.length) {
        setRecentFiles(validatedPaths);
      }

      isValidatingRef.current = false;
    }

    validateRecentFiles();
    // Only run on mount - we don't want to validate on every recentFiles change
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, []);

  // Add a file to recent files (de-duplicates, maintains order)
  const addRecentFile = useCallback((path: string) => {
    setRecentFiles((prev) => {
      // If path is already at the top, don't create new reference
      if (prev[0] === path) {
        return prev;
      }
      // Remove if already exists
      const filtered = prev.filter((p) => p !== path);
      // Add to front
      const updated = [path, ...filtered];
      // Limit to max
      return updated.slice(0, MAX_RECENT);
    });
  }, []);

  // Remove a specific file from recent files
  const removeRecentFile = useCallback((path: string) => {
    setRecentFiles((prev) => prev.filter((p) => p !== path));
  }, []);

  // Clear all recent files
  const clearRecentFiles = useCallback(() => {
    setRecentFiles([]);
  }, []);

  return { recentFiles, addRecentFile, clearRecentFiles, removeRecentFile };
}
