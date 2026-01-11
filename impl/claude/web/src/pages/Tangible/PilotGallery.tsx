/**
 * PilotGallery - Left panel showing available pilots
 *
 * Displays the 7 pilots + custom pilots with tier filtering.
 * Follows STARK BIOME aesthetic.
 */

import { memo } from 'react';
import {
  Gem,
  Sprout,
  Gamepad2,
  Mic,
  Palette,
  Castle,
  GitBranch,
  Plus,
  Filter,
  Layers,
} from 'lucide-react';
import type { LucideIcon } from 'lucide-react';

import type { PilotMetadata, CustomPilot, PilotTier, PilotGalleryProps } from './actualize-types';
import { TIER_CONFIG } from './actualize-types';

// =============================================================================
// Icon Map
// =============================================================================

const PILOT_ICONS: Record<string, LucideIcon> = {
  gem: Gem,
  seedling: Sprout,
  'gamepad-2': Gamepad2,
  mic: Mic,
  palette: Palette,
  castle: Castle,
  'git-branch': GitBranch,
};

// =============================================================================
// Tier Filter
// =============================================================================

interface TierFilterProps {
  value: PilotTier | 'all';
  onChange: (tier: PilotTier | 'all') => void;
}

const TierFilter = memo(function TierFilter({ value, onChange }: TierFilterProps) {
  const tiers: (PilotTier | 'all')[] = ['all', 'core', 'domain', 'meta'];

  return (
    <div className="pilot-gallery__filter">
      <Filter size={12} className="pilot-gallery__filter-icon" />
      {tiers.map((tier) => (
        <button
          key={tier}
          className={`pilot-gallery__filter-btn ${value === tier ? 'pilot-gallery__filter-btn--active' : ''}`}
          onClick={() => onChange(tier)}
          style={{
            borderColor: tier !== 'all' ? TIER_CONFIG[tier].color : undefined,
          }}
        >
          {tier === 'all' ? 'All' : TIER_CONFIG[tier].label}
        </button>
      ))}
    </div>
  );
});

// =============================================================================
// Pilot Card
// =============================================================================

interface PilotCardItemProps {
  pilot: PilotMetadata | CustomPilot;
  isSelected: boolean;
  onSelect: () => void;
}

const PilotCardItem = memo(function PilotCardItem({
  pilot,
  isSelected,
  onSelect,
}: PilotCardItemProps) {
  const Icon = pilot.icon ? PILOT_ICONS[pilot.icon] || Layers : Layers;
  const tierConfig = TIER_CONFIG[pilot.tier];
  const isCustom = 'isCustom' in pilot && pilot.isCustom;

  return (
    <button
      className={`pilot-gallery__card ${isSelected ? 'pilot-gallery__card--selected' : ''}`}
      onClick={onSelect}
      style={
        {
          '--pilot-color': pilot.color || tierConfig.color,
        } as React.CSSProperties
      }
    >
      <div className="pilot-gallery__card-header">
        <Icon size={16} className="pilot-gallery__card-icon" />
        <span className="pilot-gallery__card-tier" title={tierConfig.description}>
          {tierConfig.label}
        </span>
        {isCustom && <span className="pilot-gallery__card-custom">Custom</span>}
      </div>

      <div className="pilot-gallery__card-name">{pilot.displayName}</div>

      <div className="pilot-gallery__card-personality">&quot;{pilot.personalityTag}&quot;</div>

      <div className="pilot-gallery__card-description">{pilot.description}</div>
    </button>
  );
});

// =============================================================================
// Main Component
// =============================================================================

export const PilotGallery = memo(function PilotGallery({
  pilots,
  customPilots = [],
  selectedPilot,
  onSelect,
  onNewEndeavor,
  tierFilter,
  onTierFilterChange,
}: PilotGalleryProps) {
  // Filter pilots by tier
  const filteredPilots =
    tierFilter === 'all' ? pilots : pilots.filter((p) => p.tier === tierFilter);

  const filteredCustomPilots =
    tierFilter === 'all' ? customPilots : customPilots.filter((p) => p.tier === tierFilter);

  return (
    <div className="pilot-gallery">
      <div className="pilot-gallery__header">
        <Layers size={14} />
        <span className="pilot-gallery__title">Pilots</span>
        <span className="pilot-gallery__count">
          {filteredPilots.length + filteredCustomPilots.length}
        </span>
      </div>

      <TierFilter value={tierFilter} onChange={onTierFilterChange} />

      <div className="pilot-gallery__cards">
        {/* New Endeavor Button */}
        <button className="pilot-gallery__new-btn" onClick={onNewEndeavor}>
          <Plus size={16} />
          <span>New Endeavor</span>
        </button>

        {/* Standard Pilots */}
        {filteredPilots.map((pilot) => (
          <PilotCardItem
            key={pilot.name}
            pilot={pilot}
            isSelected={selectedPilot === pilot.name}
            onSelect={() => onSelect(pilot.name)}
          />
        ))}

        {/* Custom Pilots */}
        {filteredCustomPilots.length > 0 && (
          <>
            <div className="pilot-gallery__divider">
              <span>Custom Pilots</span>
            </div>
            {filteredCustomPilots.map((pilot) => (
              <PilotCardItem
                key={pilot.name}
                pilot={pilot}
                isSelected={selectedPilot === pilot.name}
                onSelect={() => onSelect(pilot.name)}
              />
            ))}
          </>
        )}
      </div>
    </div>
  );
});

export default PilotGallery;
