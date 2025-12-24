/**
 * useRecentFiles — Persist and manage recently opened files
 *
 * Uses localStorage for persistence across sessions.
 * Limits to 10 recent files, de-duplicates, and maintains order.
 */

import { useCallback, useEffect, useState } from 'react';

const STORAGE_KEY = 'kgents:recent-files';
const MAX_RECENT = 10;

export interface UseRecentFilesReturn {
  recentFiles: string[];
  addRecentFile: (path: string) => void;
  clearRecentFiles: () => void;
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

  // Persist to localStorage whenever recentFiles changes
  useEffect(() => {
    try {
      localStorage.setItem(STORAGE_KEY, JSON.stringify(recentFiles));
    } catch (e) {
      console.warn('[useRecentFiles] Failed to persist to localStorage:', e);
    }
  }, [recentFiles]);

  // Add a file to recent files (de-duplicates, maintains order)
  const addRecentFile = useCallback((path: string) => {
    setRecentFiles((prev) => {
      // Remove if already exists
      const filtered = prev.filter((p) => p !== path);
      // Add to front
      const updated = [path, ...filtered];
      // Limit to max
      return updated.slice(0, MAX_RECENT);
    });
  }, []);

  // Clear all recent files
  const clearRecentFiles = useCallback(() => {
    setRecentFiles([]);
  }, []);

  return { recentFiles, addRecentFile, clearRecentFiles };
}
