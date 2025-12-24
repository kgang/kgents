/**
 * useTokenKeyboard - Vim-style keyboard navigation
 *
 * Keys:
 * - j/k: Move down/up (next/prev in row)
 * - h/l: Move left/right
 * - Enter: Open detail panel
 * - e: Open in editor
 * - /: Focus search
 * - Escape: Close panel / clear search
 * - gg: Jump to first
 * - G: Jump to last
 * - ?: Show help
 */

import { useCallback, useEffect, useRef } from 'react';
import type { TokenItem } from './types';

// =============================================================================
// Types
// =============================================================================

interface UseTokenKeyboardOptions {
  enabled: boolean;
  columns: number; // Used by caller to compute row navigation, passed for future use
  selectedId: string | null;
  filteredTokens: TokenItem[];
  onSelectNext: () => void;
  onSelectPrev: () => void;
  onSelectNextRow: () => void;
  onSelectPrevRow: () => void;
  onOpenDetail: (id: string) => void;
  onOpenEditor: (path: string) => void;
  onCloseDetail: () => void;
}

interface UseTokenKeyboardResult {
  focusSearch: () => void;
}

// =============================================================================
// Hook
// =============================================================================

export function useTokenKeyboard({
  enabled,
  columns: _columns, // Passed for potential future use in h/l navigation
  selectedId,
  filteredTokens,
  onSelectNext,
  onSelectPrev,
  onSelectNextRow,
  onSelectPrevRow,
  onOpenDetail,
  onOpenEditor,
  onCloseDetail,
}: UseTokenKeyboardOptions): UseTokenKeyboardResult {
  void _columns; // Mark as intentionally unused
  const searchFocusRef = useRef<(() => void) | null>(null);
  const lastKeyRef = useRef<string>('');
  const lastKeyTimeRef = useRef<number>(0);

  // Handle keydown
  const handleKeyDown = useCallback(
    (e: KeyboardEvent) => {
      if (!enabled) return;

      // Ignore if in an input/textarea
      const target = e.target as HTMLElement;
      if (target.tagName === 'INPUT' || target.tagName === 'TEXTAREA') return;

      const now = Date.now();
      const key = e.key;

      // Check for gg (jump to first)
      if (key === 'g' && lastKeyRef.current === 'g' && now - lastKeyTimeRef.current < 500) {
        e.preventDefault();
        if (filteredTokens.length > 0) {
          onOpenDetail(filteredTokens[0].id);
        }
        lastKeyRef.current = '';
        return;
      }

      // Track for gg
      if (key === 'g') {
        lastKeyRef.current = 'g';
        lastKeyTimeRef.current = now;
        return;
      }
      lastKeyRef.current = '';

      switch (key) {
        case 'j':
        case 'ArrowDown':
          e.preventDefault();
          onSelectNextRow();
          break;

        case 'k':
        case 'ArrowUp':
          e.preventDefault();
          onSelectPrevRow();
          break;

        case 'l':
        case 'ArrowRight':
          e.preventDefault();
          onSelectNext();
          break;

        case 'h':
        case 'ArrowLeft':
          e.preventDefault();
          onSelectPrev();
          break;

        case 'Enter':
          e.preventDefault();
          if (selectedId) {
            onOpenDetail(selectedId);
          }
          break;

        case 'e':
          e.preventDefault();
          if (selectedId) {
            onOpenEditor(selectedId);
          }
          break;

        case '/':
          e.preventDefault();
          searchFocusRef.current?.();
          break;

        case 'Escape':
          e.preventDefault();
          onCloseDetail();
          break;

        case 'G':
          e.preventDefault();
          if (filteredTokens.length > 0) {
            onOpenDetail(filteredTokens[filteredTokens.length - 1].id);
          }
          break;

        case '?':
          e.preventDefault();
          // TODO: Show help modal
          console.debug('[TokenRegistry] Help requested');
          break;
      }
    },
    [
      enabled,
      selectedId,
      filteredTokens,
      onSelectNext,
      onSelectPrev,
      onSelectNextRow,
      onSelectPrevRow,
      onOpenDetail,
      onOpenEditor,
      onCloseDetail,
    ]
  );

  // Add global listener
  useEffect(() => {
    window.addEventListener('keydown', handleKeyDown);
    return () => window.removeEventListener('keydown', handleKeyDown);
  }, [handleKeyDown]);

  // Focus search function
  const focusSearch = useCallback(() => {
    searchFocusRef.current?.();
  }, []);

  return { focusSearch };
}
