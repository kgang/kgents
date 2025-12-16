/**
 * ArtisanGrid: Grid display of available artisans.
 *
 * Allows single or multiple selection depending on mode.
 */

import { useState, useEffect } from 'react';
import { ArtisanCard } from './ArtisanCard';
import { atelierApi, type Artisan } from '@/api/atelier';

interface ArtisanGridProps {
  /** Allow selecting multiple artisans */
  multiSelect?: boolean;
  /** Currently selected artisan(s) */
  selected?: string[];
  /** Callback when selection changes */
  onSelect?: (selected: string[]) => void;
  /** Disable all selections */
  disabled?: boolean;
}

export function ArtisanGrid({
  multiSelect = false,
  selected = [],
  onSelect,
  disabled = false,
}: ArtisanGridProps) {
  const [artisans, setArtisans] = useState<Artisan[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  // Fetch artisans on mount
  useEffect(() => {
    async function fetchArtisans() {
      try {
        setLoading(true);
        const response = await atelierApi.getArtisans();
        setArtisans(response.data.artisans);
        setError(null);
      } catch (err) {
        setError('Failed to load artisans');
        console.error('[ArtisanGrid] Error:', err);
      } finally {
        setLoading(false);
      }
    }
    fetchArtisans();
  }, []);

  // Handle artisan click
  const handleClick = (artisan: Artisan) => {
    if (disabled) return;

    const name = artisan.name.toLowerCase().replace(/^the\s+/, '');

    if (multiSelect) {
      // Toggle selection
      const newSelected = selected.includes(name)
        ? selected.filter((n) => n !== name)
        : [...selected, name];
      onSelect?.(newSelected);
    } else {
      // Single selection
      onSelect?.(selected.includes(name) ? [] : [name]);
    }
  };

  // Check if artisan is selected
  const isSelected = (artisan: Artisan) => {
    const name = artisan.name.toLowerCase().replace(/^the\s+/, '');
    return selected.includes(name);
  };

  if (loading) {
    return (
      <div className="flex items-center justify-center p-8 text-stone-400">
        <span className="animate-pulse">gathering the artisans...</span>
      </div>
    );
  }

  if (error) {
    return (
      <div className="flex items-center justify-center p-8 text-red-400">
        {error}
      </div>
    );
  }

  return (
    <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-4">
      {artisans.map((artisan) => (
        <ArtisanCard
          key={artisan.name}
          artisan={artisan}
          selected={isSelected(artisan)}
          onClick={() => handleClick(artisan)}
          disabled={disabled}
        />
      ))}
    </div>
  );
}

export default ArtisanGrid;
