/**
 * FocusPane — Context-aware content display
 *
 * Shows content appropriate to the current focus:
 * - welcome: Initial state, hints
 * - file: Source code with syntax highlighting
 * - spec: Specification markdown (SpecGraph integrated)
 * - concept: Conceptual explanation
 * - dialogue: Expanded dialogue content
 *
 * "The proof IS the decision."
 */

import type { Focus, FocusType } from './useMembrane';
import { WelcomeView, FileView, SpecView, ConceptView, GraphView } from './views';
import type { EdgeType } from './useSpecNavigation';

import './FocusPane.css';

// =============================================================================
// Types
// =============================================================================

interface FocusPaneProps {
  focus: Focus;
  onFocusChange?: (type: FocusType, path?: string) => void;
}

// =============================================================================
// Component
// =============================================================================

export function FocusPane({ focus, onFocusChange }: FocusPaneProps) {
  // Handler for navigating to specs via edge portals
  const handleSpecNavigate = (path: string) => {
    if (path.startsWith('spec/') && path.endsWith('.md')) {
      onFocusChange?.('spec', path);
    } else if (path.startsWith('impl/')) {
      onFocusChange?.('file', path);
    } else {
      // Assume it's a concept
      onFocusChange?.('concept', path);
    }
  };

  // Handler for edge clicks (implements, tests, etc.)
  const handleEdgeClick = (target: string, edge: EdgeType) => {
    // Route based on edge type and target
    if (edge === 'implements' || edge === 'tests') {
      onFocusChange?.('file', target);
    } else if (target.startsWith('spec/') || edge === 'extends' || edge === 'extended_by') {
      onFocusChange?.('spec', target);
    } else {
      onFocusChange?.('concept', target);
    }
  };

  return (
    <div className="focus-pane">
      {renderFocusContent(focus, handleSpecNavigate, handleEdgeClick)}
    </div>
  );
}

// =============================================================================
// Content Renderer
// =============================================================================

function renderFocusContent(
  focus: Focus,
  onNavigate: (path: string) => void,
  onEdgeClick: (target: string, edge: EdgeType) => void
): React.ReactNode {
  switch (focus.type) {
    case 'welcome':
      return <WelcomeView />;

    case 'file':
      if (!focus.path) {
        return <WelcomeView />;
      }
      return <FileView path={focus.path} />;

    case 'spec':
      if (!focus.path) {
        return <WelcomeView />;
      }
      return <SpecView path={focus.path} onNavigate={onNavigate} onEdgeClick={onEdgeClick} />;

    case 'concept':
      if (!focus.path) {
        return <WelcomeView />;
      }
      return <ConceptView concept={focus.path} />;

    case 'dialogue':
      // For dialogue focus, we could show an expanded view
      // For now, fall back to welcome
      return <WelcomeView />;

    case 'graph':
      return (
        <GraphView
          onSpecClick={(path) => {
            // Navigate to spec when clicking a node
            onNavigate(path);
          }}
        />
      );

    default:
      return <WelcomeView />;
  }
}
