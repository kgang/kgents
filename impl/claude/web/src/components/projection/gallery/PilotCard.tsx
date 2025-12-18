/**
 * PilotCard: Single pilot display with projections.
 *
 * Performance: Interactive previews use lazy-loaded components.
 * @see plans/park-town-design-overhaul.md - Phase 5.2 Performance
 */

import { Suspense } from 'react';
import type { PilotResponse, GalleryCategory } from '@/api/types';
import { GALLERY_CATEGORY_CONFIG } from '@/api/types';
import { ProjectionView } from './ProjectionView';
import { LazyPolynomialPlayground, LazyOperadWiring, LazyTownLive } from './index';

interface PilotCardProps {
  pilot: PilotResponse;
  onClick?: () => void;
}

export function PilotCard({ pilot, onClick }: PilotCardProps) {
  const categoryConfig = GALLERY_CATEGORY_CONFIG[pilot.category as GalleryCategory] || {
    icon: '?',
    color: '#888',
  };

  const isInteractive = pilot.category === 'INTERACTIVE';

  // Render compact interactive preview with lazy loading
  const renderInteractivePreview = () => {
    const fallback = (
      <div className="flex items-center justify-center h-16">
        <div className="w-3 h-3 border-2 border-emerald-500/40 border-t-emerald-500 rounded-full animate-spin" />
      </div>
    );

    switch (pilot.name) {
      case 'polynomial_playground':
        return (
          <Suspense fallback={fallback}>
            <LazyPolynomialPlayground compact />
          </Suspense>
        );
      case 'operad_wiring_diagram':
        return (
          <Suspense fallback={fallback}>
            <LazyOperadWiring compact />
          </Suspense>
        );
      case 'town_live':
        return (
          <Suspense fallback={fallback}>
            <LazyTownLive compact />
          </Suspense>
        );
      default:
        return null;
    }
  };

  return (
    <div
      className={`bg-town-surface/50 border rounded-lg overflow-hidden transition-all cursor-pointer ${
        isInteractive
          ? 'border-emerald-500/40 hover:border-emerald-500/70 hover:shadow-lg hover:shadow-emerald-500/10'
          : 'border-town-accent/30 hover:border-town-accent/60'
      }`}
      onClick={onClick}
    >
      {/* Header */}
      <div className={`px-3 py-2 border-b flex items-center justify-between ${
        isInteractive ? 'border-emerald-500/20' : 'border-town-accent/20'
      }`}>
        <div className="flex items-center gap-2">
          <span
            className="text-lg"
            style={{ color: categoryConfig.color }}
            title={pilot.category}
          >
            {categoryConfig.icon}
          </span>
          <span className="font-medium text-sm truncate" title={pilot.name}>
            {pilot.name}
          </span>
        </div>
        <div className="flex gap-1">
          {isInteractive && (
            <span className="text-xs px-1.5 py-0.5 rounded bg-emerald-500/20 text-emerald-400 font-medium">
              Interactive
            </span>
          )}
          {pilot.tags.slice(0, isInteractive ? 1 : 2).map((tag) => (
            <span
              key={tag}
              className="text-xs px-1.5 py-0.5 rounded bg-town-accent/20 text-gray-400"
            >
              {tag}
            </span>
          ))}
        </div>
      </div>

      {/* Projection or Interactive Preview */}
      <div className="p-3">
        {isInteractive ? (
          <div className="min-h-[80px] flex items-center justify-center">
            {renderInteractivePreview()}
          </div>
        ) : (
          <ProjectionView projections={pilot.projections} compact />
        )}
      </div>

      {/* Footer description */}
      <div className={`px-3 py-2 border-t ${
        isInteractive ? 'border-emerald-500/20' : 'border-town-accent/20'
      }`}>
        <p className="text-xs text-gray-500 truncate" title={pilot.description}>
          {pilot.description}
        </p>
      </div>
    </div>
  );
}

export default PilotCard;
