/**
 * GallerySection - Gallery shortcuts in navigation tree
 *
 * Provides quick access to system routes (/_/) not AGENTESE paths.
 *
 * @see NavigationTree.tsx
 */

import { Layers } from 'lucide-react';

// =============================================================================
// Types
// =============================================================================

interface Gallery {
  route: string;
  label: string;
}

export interface GallerySectionProps {
  currentRoute: string;
  onNavigate: (route: string) => void;
}

// =============================================================================
// Constants
// =============================================================================

const GALLERIES: Gallery[] = [
  { route: '/_/gallery', label: 'Projection Gallery' },
  { route: '/_/gallery/layout', label: 'Layout Gallery' },
  { route: '/_/gallery/interactive-text', label: 'Interactive Text' },
  { route: '/_/docs/agentese', label: 'AGENTESE Explorer' },
  { route: '/_/canvas', label: 'Collaborative Canvas' },
];

// =============================================================================
// Component
// =============================================================================

export function GallerySection({ currentRoute, onNavigate }: GallerySectionProps) {
  return (
    <div className="border-t border-gray-700/50 pt-3">
      <h3 className="px-3 mb-2 text-xs font-medium text-gray-500 uppercase tracking-wider">
        Gallery
      </h3>
      <div className="space-y-0.5">
        {GALLERIES.map((gallery) => {
          const isActive = currentRoute === gallery.route;
          return (
            <button
              key={gallery.route}
              onClick={() => onNavigate(gallery.route)}
              className={`
                w-full flex items-center gap-2 px-3 py-1.5 text-sm
                hover:bg-gray-700/50 transition-colors rounded-md
                ${isActive ? 'bg-gray-700/70 text-white' : 'text-gray-300'}
              `}
            >
              <Layers className="w-4 h-4 text-gray-400" />
              <span>{gallery.label}</span>
            </button>
          );
        })}
      </div>
    </div>
  );
}

export default GallerySection;
