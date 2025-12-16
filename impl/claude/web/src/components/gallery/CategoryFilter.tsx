/**
 * CategoryFilter: Category tabs for filtering gallery pilots.
 */

import type { GalleryCategory } from '@/api/types';
import { GALLERY_CATEGORY_CONFIG } from '@/api/types';

interface CategoryFilterProps {
  categories: GalleryCategory[];
  activeCategory: GalleryCategory | 'ALL';
  onChange: (category: GalleryCategory | 'ALL') => void;
  counts?: Partial<Record<GalleryCategory, number>>;
}

export function CategoryFilter({
  categories,
  activeCategory,
  onChange,
  counts,
}: CategoryFilterProps) {
  const tabClass = (active: boolean) =>
    `px-3 py-1.5 text-sm font-medium rounded-lg transition-colors flex items-center gap-1.5 ${
      active
        ? 'bg-town-accent/40 text-white'
        : 'text-gray-400 hover:text-gray-200 hover:bg-town-accent/20'
    }`;

  return (
    <div className="flex flex-wrap gap-2">
      {/* All tab */}
      <button
        onClick={() => onChange('ALL')}
        className={tabClass(activeCategory === 'ALL')}
      >
        <span>All</span>
        {counts && (
          <span className="text-xs opacity-60">
            ({Object.values(counts).reduce((a, b) => a + b, 0)})
          </span>
        )}
      </button>

      {/* Category tabs */}
      {categories.map((category) => {
        const config = GALLERY_CATEGORY_CONFIG[category];
        return (
          <button
            key={category}
            onClick={() => onChange(category)}
            className={tabClass(activeCategory === category)}
          >
            <span style={{ color: config.color }}>{config.icon}</span>
            <span>{category}</span>
            {counts && counts[category] !== undefined && (
              <span className="text-xs opacity-60">({counts[category]})</span>
            )}
          </button>
        );
      })}
    </div>
  );
}

export default CategoryFilter;
