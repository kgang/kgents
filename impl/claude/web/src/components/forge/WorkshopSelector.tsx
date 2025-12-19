/**
 * WorkshopSelector: Dropdown to select or create a workshop.
 *
 * The Forge is organized into workshops - shared creative spaces
 * where Kent can group related commissions.
 *
 * Features:
 * - Dropdown of existing workshops
 * - "Create New Workshop" opens inline form
 * - "Personal Workshop" as default fallback
 * - Workshop theme/description preview
 *
 * "The workshop is the context. The commission is the intent."
 *
 * @see docs/skills/metaphysical-fullstack.md
 */

import { useState } from 'react';
import { ChevronDown, Plus, Building2, Check } from 'lucide-react';
import { useWorkshops } from '@/hooks/useForgeQuery';
import { cn } from '@/lib/utils';

// =============================================================================
// Types
// =============================================================================

interface Workshop {
  id: string;
  name: string;
  description?: string | null;
  theme?: string | null;
  is_active: boolean;
  created_at: string;
}

export interface WorkshopSelectorProps {
  /** Currently selected workshop ID */
  selected: string | null;
  /** Callback when selection changes */
  onSelect: (workshopId: string | null) => void;
  /** Callback to open create form */
  onCreateNew?: () => void;
  /** Additional class names */
  className?: string;
  /** Disable the selector */
  disabled?: boolean;
  /** Show "Personal Workshop" option */
  showPersonal?: boolean;
}

// =============================================================================
// Constants
// =============================================================================

const PERSONAL_WORKSHOP_ID = '__personal__';
const PERSONAL_WORKSHOP: Workshop = {
  id: PERSONAL_WORKSHOP_ID,
  name: 'Personal Workshop',
  description: 'Your default workspace for commissions',
  theme: 'personal',
  is_active: true,
  created_at: new Date().toISOString(),
};

// =============================================================================
// WorkshopSelector Component
// =============================================================================

export function WorkshopSelector({
  selected,
  onSelect,
  onCreateNew,
  className = '',
  disabled = false,
  showPersonal = true,
}: WorkshopSelectorProps) {
  const [isOpen, setIsOpen] = useState(false);
  const { data: workshopsData, isLoading } = useWorkshops();

  // Build workshop list with Personal option
  const allWorkshops: Workshop[] = [
    ...(showPersonal ? [PERSONAL_WORKSHOP] : []),
    ...((workshopsData?.workshops ?? []) as Workshop[]).filter((w) => w.is_active),
  ];

  // Find selected workshop
  const selectedWorkshop = selected
    ? allWorkshops.find((w) => w.id === selected) || null
    : showPersonal
      ? PERSONAL_WORKSHOP
      : null;

  const handleSelect = (workshop: Workshop | null) => {
    onSelect(workshop?.id || null);
    setIsOpen(false);
  };

  return (
    <div className={cn('relative', className)}>
      {/* Trigger Button */}
      <button
        type="button"
        onClick={() => !disabled && setIsOpen(!isOpen)}
        disabled={disabled}
        className={cn(
          'w-full flex items-center justify-between gap-2',
          'px-3 py-2.5 rounded-lg border transition-colors',
          'bg-white text-left',
          isOpen
            ? 'border-amber-300 ring-2 ring-amber-100'
            : 'border-stone-200 hover:border-stone-300',
          disabled && 'opacity-50 cursor-not-allowed'
        )}
      >
        <div className="flex items-center gap-2 min-w-0">
          <Building2 className="w-4 h-4 text-stone-400 flex-shrink-0" />
          {isLoading ? (
            <span className="text-stone-400 text-sm">Loading workshops...</span>
          ) : selectedWorkshop ? (
            <div className="min-w-0">
              <span className="text-stone-700 text-sm font-medium truncate block">
                {selectedWorkshop.name}
              </span>
              {selectedWorkshop.description && (
                <span className="text-stone-400 text-xs truncate block">
                  {selectedWorkshop.description}
                </span>
              )}
            </div>
          ) : (
            <span className="text-stone-400 text-sm">Select a workshop...</span>
          )}
        </div>
        <ChevronDown
          className={cn(
            'w-4 h-4 text-stone-400 transition-transform flex-shrink-0',
            isOpen && 'rotate-180'
          )}
        />
      </button>

      {/* Dropdown */}
      {isOpen && (
        <>
          {/* Backdrop */}
          <div className="fixed inset-0 z-10" onClick={() => setIsOpen(false)} />

          {/* Menu */}
          <div
            className={cn(
              'absolute z-20 w-full mt-1 py-1',
              'bg-white rounded-lg border border-stone-200',
              'shadow-lg max-h-60 overflow-y-auto'
            )}
          >
            {/* Create New Option */}
            {onCreateNew && (
              <button
                onClick={() => {
                  setIsOpen(false);
                  onCreateNew();
                }}
                className={cn(
                  'w-full flex items-center gap-2 px-3 py-2',
                  'text-amber-600 hover:bg-amber-50 transition-colors'
                )}
              >
                <Plus className="w-4 h-4" />
                <span className="text-sm font-medium">Create New Workshop</span>
              </button>
            )}

            {onCreateNew && allWorkshops.length > 0 && (
              <div className="border-t border-stone-100 my-1" />
            )}

            {/* Workshop Options */}
            {allWorkshops.map((workshop) => (
              <button
                key={workshop.id}
                onClick={() => handleSelect(workshop)}
                className={cn(
                  'w-full flex items-center gap-2 px-3 py-2 text-left',
                  'hover:bg-stone-50 transition-colors',
                  workshop.id === selected && 'bg-amber-50'
                )}
              >
                <Building2 className="w-4 h-4 text-stone-400 flex-shrink-0" />
                <div className="flex-1 min-w-0">
                  <span className="text-stone-700 text-sm font-medium truncate block">
                    {workshop.name}
                  </span>
                  {workshop.description && (
                    <span className="text-stone-400 text-xs truncate block">
                      {workshop.description}
                    </span>
                  )}
                </div>
                {workshop.id === selected && <Check className="w-4 h-4 text-amber-500" />}
              </button>
            ))}

            {/* Empty State */}
            {allWorkshops.length === 0 && (
              <div className="px-3 py-4 text-center">
                <p className="text-stone-400 text-sm">No workshops yet</p>
                {onCreateNew && (
                  <button
                    onClick={() => {
                      setIsOpen(false);
                      onCreateNew();
                    }}
                    className="mt-2 text-amber-600 text-sm hover:underline"
                  >
                    Create your first workshop
                  </button>
                )}
              </div>
            )}
          </div>
        </>
      )}
    </div>
  );
}

export default WorkshopSelector;
export { PERSONAL_WORKSHOP_ID };
