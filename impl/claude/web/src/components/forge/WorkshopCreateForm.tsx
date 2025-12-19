/**
 * WorkshopCreateForm: Inline form to create a new workshop.
 *
 * Simple, focused form for workshop creation. Follows Living Earth
 * aesthetic with stone/amber palette.
 *
 * Features:
 * - Name, description, theme inputs
 * - Auto-focus on name field
 * - Create and Cancel actions
 *
 * @see docs/skills/elastic-ui-patterns.md
 */

import { useState, useEffect, useRef, FormEvent } from 'react';
import { X, Loader2 } from 'lucide-react';
import { useCreateWorkshop } from '@/hooks/useForgeQuery';
import { cn } from '@/lib/utils';

// =============================================================================
// Types
// =============================================================================

interface Workshop {
  id: string;
  name: string;
  description?: string;
  theme?: string;
}

export interface WorkshopCreateFormProps {
  /** Callback when workshop is created */
  onCreated: (workshop: Workshop) => void;
  /** Callback when form is cancelled */
  onCancel: () => void;
  /** Additional class names */
  className?: string;
}

// =============================================================================
// Theme Options
// =============================================================================

const THEMES = [
  { value: 'general', label: 'General', icon: '~' },
  { value: 'exploration', label: 'Exploration', icon: '~' },
  { value: 'implementation', label: 'Implementation', icon: '~' },
  { value: 'experiment', label: 'Experiment', icon: '~' },
  { value: 'learning', label: 'Learning', icon: '~' },
] as const;

// =============================================================================
// WorkshopCreateForm Component
// =============================================================================

export function WorkshopCreateForm({ onCreated, onCancel, className = '' }: WorkshopCreateFormProps) {
  const [name, setName] = useState('');
  const [description, setDescription] = useState('');
  const [theme, setTheme] = useState('general');
  const nameInputRef = useRef<HTMLInputElement>(null);

  const createWorkshop = useCreateWorkshop();

  // Auto-focus name field
  useEffect(() => {
    nameInputRef.current?.focus();
  }, []);

  const handleSubmit = async (e: FormEvent) => {
    e.preventDefault();
    if (!name.trim()) return;

    try {
      const result = await createWorkshop.mutateAsync({
        name: name.trim(),
        description: description.trim() || undefined,
        theme: theme || undefined,
      });

      if (result?.workshop) {
        onCreated(result.workshop as Workshop);
      }
    } catch {
      // Error handled by mutation state
    }
  };

  const isValid = name.trim().length > 0;

  return (
    <form
      onSubmit={handleSubmit}
      className={cn('bg-white rounded-lg border border-stone-200 p-4 shadow-sm', className)}
    >
      {/* Header */}
      <div className="flex items-center justify-between mb-4">
        <h3 className="font-medium text-stone-800">Create Workshop</h3>
        <button
          type="button"
          onClick={onCancel}
          className="p-1 text-stone-400 hover:text-stone-600 transition-colors"
        >
          <X className="w-4 h-4" />
        </button>
      </div>

      {/* Name Input */}
      <div className="mb-3">
        <label htmlFor="workshop-name" className="block text-xs font-medium text-stone-500 mb-1">
          Name
        </label>
        <input
          ref={nameInputRef}
          id="workshop-name"
          type="text"
          value={name}
          onChange={(e) => setName(e.target.value)}
          placeholder="My Workshop"
          className={cn(
            'w-full px-3 py-2 text-sm rounded-md border',
            'focus:outline-none focus:ring-2 focus:ring-amber-200 focus:border-amber-300',
            'border-stone-200'
          )}
        />
      </div>

      {/* Description Input */}
      <div className="mb-3">
        <label htmlFor="workshop-desc" className="block text-xs font-medium text-stone-500 mb-1">
          Description <span className="text-stone-400">(optional)</span>
        </label>
        <textarea
          id="workshop-desc"
          value={description}
          onChange={(e) => setDescription(e.target.value)}
          placeholder="What will you build in this workshop?"
          rows={2}
          className={cn(
            'w-full px-3 py-2 text-sm rounded-md border resize-none',
            'focus:outline-none focus:ring-2 focus:ring-amber-200 focus:border-amber-300',
            'border-stone-200'
          )}
        />
      </div>

      {/* Theme Selector */}
      <div className="mb-4">
        <label className="block text-xs font-medium text-stone-500 mb-2">Theme</label>
        <div className="flex flex-wrap gap-2">
          {THEMES.map((t) => (
            <button
              key={t.value}
              type="button"
              onClick={() => setTheme(t.value)}
              className={cn(
                'px-3 py-1.5 text-xs rounded-full border transition-colors',
                theme === t.value
                  ? 'bg-amber-100 border-amber-300 text-amber-800'
                  : 'bg-white border-stone-200 text-stone-600 hover:border-stone-300'
              )}
            >
              {t.label}
            </button>
          ))}
        </div>
      </div>

      {/* Error Display */}
      {createWorkshop.error && (
        <div className="mb-3 p-2 text-xs text-red-600 bg-red-50 rounded-md border border-red-200">
          {createWorkshop.error.message || 'Failed to create workshop'}
        </div>
      )}

      {/* Actions */}
      <div className="flex items-center gap-2">
        <button
          type="button"
          onClick={onCancel}
          className="flex-1 px-3 py-2 text-sm text-stone-600 hover:text-stone-800 transition-colors"
        >
          Cancel
        </button>
        <button
          type="submit"
          disabled={!isValid || createWorkshop.isPending}
          className={cn(
            'flex-1 px-3 py-2 text-sm font-medium rounded-md transition-colors',
            'bg-amber-500 text-white hover:bg-amber-600',
            'disabled:opacity-50 disabled:cursor-not-allowed'
          )}
        >
          {createWorkshop.isPending ? (
            <span className="flex items-center justify-center gap-2">
              <Loader2 className="w-4 h-4 animate-spin" />
              Creating...
            </span>
          ) : (
            'Create Workshop'
          )}
        </button>
      </div>
    </form>
  );
}

export default WorkshopCreateForm;
