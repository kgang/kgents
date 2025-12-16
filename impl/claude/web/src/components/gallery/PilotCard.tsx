/**
 * PilotCard: Single pilot display with projections.
 */

import type { PilotResponse, GalleryCategory } from '@/api/types';
import { GALLERY_CATEGORY_CONFIG } from '@/api/types';
import { ProjectionView } from './ProjectionView';

interface PilotCardProps {
  pilot: PilotResponse;
  onClick?: () => void;
}

export function PilotCard({ pilot, onClick }: PilotCardProps) {
  const categoryConfig = GALLERY_CATEGORY_CONFIG[pilot.category as GalleryCategory] || {
    icon: '?',
    color: '#888',
  };

  return (
    <div
      className="bg-town-surface/50 border border-town-accent/30 rounded-lg overflow-hidden hover:border-town-accent/60 transition-colors cursor-pointer"
      onClick={onClick}
    >
      {/* Header */}
      <div className="px-3 py-2 border-b border-town-accent/20 flex items-center justify-between">
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
          {pilot.tags.slice(0, 2).map((tag) => (
            <span
              key={tag}
              className="text-xs px-1.5 py-0.5 rounded bg-town-accent/20 text-gray-400"
            >
              {tag}
            </span>
          ))}
        </div>
      </div>

      {/* Projection */}
      <div className="p-3">
        <ProjectionView projections={pilot.projections} compact />
      </div>

      {/* Footer description */}
      <div className="px-3 py-2 border-t border-town-accent/20">
        <p className="text-xs text-gray-500 truncate" title={pilot.description}>
          {pilot.description}
        </p>
      </div>
    </div>
  );
}

export default PilotCard;
