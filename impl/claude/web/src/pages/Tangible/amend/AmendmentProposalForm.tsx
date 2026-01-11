/**
 * AmendmentProposalForm - Modal form for creating new amendments
 *
 * Features:
 * - Title, description inputs
 * - Amendment type dropdown
 * - Target K-Block selector (autocomplete from codebase graph)
 * - Layer selector (L0-L4)
 * - Content editor (markdown)
 * - Reasoning textarea
 * - Principles affected checkboxes
 * - Submit as draft / Submit for review
 *
 * STARK BIOME aesthetic: 90% steel, 10% earned glow.
 */

import { memo, useState, useCallback, useMemo } from 'react';
import {
  X,
  FileText,
  Layers,
  Edit3,
  AlertTriangle,
  Check,
  ChevronDown,
  Search,
} from 'lucide-react';
import type { AmendmentType, AmendmentProposalInput } from './types';
import { AMENDMENT_TYPE_LABELS, LAYER_COLORS, LAYER_NAMES } from './types';

// =============================================================================
// Types
// =============================================================================

export interface AmendmentProposalFormProps {
  isOpen: boolean;
  onClose: () => void;
  onSubmit: (input: AmendmentProposalInput) => void;
  /** Available K-Blocks for target selection */
  kblocks?: Array<{ id: string; path: string; title: string; layer: number }>;
  /** Available principles for affected selection */
  principles?: string[];
  isLoading?: boolean;
}

interface FormState {
  title: string;
  description: string;
  amendmentType: AmendmentType;
  targetKblock: string;
  targetLayer: 0 | 1 | 2 | 3 | 4;
  proposedContent: string;
  reasoning: string;
  principlesAffected: string[];
}

const initialFormState: FormState = {
  title: '',
  description: '',
  amendmentType: 'principle_modification',
  targetKblock: '',
  targetLayer: 1,
  proposedContent: '',
  reasoning: '',
  principlesAffected: [],
};

// =============================================================================
// Mock Data
// =============================================================================

const MOCK_KBLOCKS = [
  { id: 'kb-1', path: 'spec/principles/core.md', title: 'Core Principles', layer: 1 },
  { id: 'kb-2', path: 'spec/principles/axioms.md', title: 'Axioms', layer: 0 },
  { id: 'kb-3', path: 'spec/protocols/witness.md', title: 'Witness Protocol', layer: 2 },
  { id: 'kb-4', path: 'spec/protocols/amendment.md', title: 'Amendment Protocol', layer: 2 },
  { id: 'kb-5', path: 'spec/agents/poly-agent.md', title: 'PolyAgent Spec', layer: 2 },
  { id: 'kb-6', path: 'impl/claude/services/brain/store.py', title: 'Brain Store', layer: 4 },
];

const MOCK_PRINCIPLES = [
  'composable',
  'ethical',
  'tasteful',
  'joy_inducing',
  'heterarchical',
  'generative',
  'curated',
];

// =============================================================================
// Subcomponents
// =============================================================================

interface KBlockSelectorProps {
  value: string;
  onChange: (value: string) => void;
  kblocks: Array<{ id: string; path: string; title: string; layer: number }>;
  disabled?: boolean;
}

const KBlockSelector = memo(function KBlockSelector({
  value,
  onChange,
  kblocks,
  disabled,
}: KBlockSelectorProps) {
  const [isOpen, setIsOpen] = useState(false);
  const [searchQuery, setSearchQuery] = useState('');

  const filteredKblocks = useMemo(() => {
    if (!searchQuery) return kblocks;
    const query = searchQuery.toLowerCase();
    return kblocks.filter(
      (kb) => kb.path.toLowerCase().includes(query) || kb.title.toLowerCase().includes(query)
    );
  }, [kblocks, searchQuery]);

  const selectedKblock = kblocks.find((kb) => kb.path === value);

  return (
    <div className="amendment-form__kblock-selector">
      <button
        type="button"
        className="amendment-form__kblock-trigger"
        onClick={() => !disabled && setIsOpen(!isOpen)}
        disabled={disabled}
      >
        {selectedKblock ? (
          <>
            <span
              className="amendment-form__kblock-layer"
              style={{
                color: LAYER_COLORS[selectedKblock.layer as keyof typeof LAYER_COLORS],
              }}
            >
              L{selectedKblock.layer}
            </span>
            <span className="amendment-form__kblock-title">{selectedKblock.title}</span>
            <span className="amendment-form__kblock-path">{selectedKblock.path}</span>
          </>
        ) : (
          <span className="amendment-form__kblock-placeholder">Select target K-Block...</span>
        )}
        <ChevronDown size={14} />
      </button>

      {isOpen && (
        <div className="amendment-form__kblock-dropdown">
          <div className="amendment-form__kblock-search">
            <Search size={14} />
            <input
              type="text"
              placeholder="Search K-Blocks..."
              value={searchQuery}
              onChange={(e) => setSearchQuery(e.target.value)}
              autoFocus
            />
          </div>
          <div className="amendment-form__kblock-list">
            {filteredKblocks.length === 0 ? (
              <div className="amendment-form__kblock-empty">No matching K-Blocks</div>
            ) : (
              filteredKblocks.map((kb) => (
                <button
                  key={kb.id}
                  type="button"
                  className={`amendment-form__kblock-option ${
                    value === kb.path ? 'amendment-form__kblock-option--selected' : ''
                  }`}
                  onClick={() => {
                    onChange(kb.path);
                    setIsOpen(false);
                    setSearchQuery('');
                  }}
                >
                  <span
                    className="amendment-form__kblock-layer"
                    style={{
                      color: LAYER_COLORS[kb.layer as keyof typeof LAYER_COLORS],
                    }}
                  >
                    L{kb.layer}
                  </span>
                  <div className="amendment-form__kblock-info">
                    <span className="amendment-form__kblock-title">{kb.title}</span>
                    <span className="amendment-form__kblock-path">{kb.path}</span>
                  </div>
                  {value === kb.path && <Check size={14} />}
                </button>
              ))
            )}
          </div>
        </div>
      )}
    </div>
  );
});

interface LayerSelectorProps {
  value: 0 | 1 | 2 | 3 | 4;
  onChange: (value: 0 | 1 | 2 | 3 | 4) => void;
  disabled?: boolean;
}

const LayerSelector = memo(function LayerSelector({
  value,
  onChange,
  disabled,
}: LayerSelectorProps) {
  const layers = [0, 1, 2, 3, 4] as const;

  return (
    <div className="amendment-form__layer-selector">
      {layers.map((layer) => {
        const color = LAYER_COLORS[layer];
        const name = LAYER_NAMES[layer];

        return (
          <button
            key={layer}
            type="button"
            className={`amendment-form__layer-btn ${
              value === layer ? 'amendment-form__layer-btn--active' : ''
            }`}
            style={{
              borderColor: value === layer ? color : undefined,
              color: value === layer ? color : undefined,
            }}
            onClick={() => onChange(layer)}
            disabled={disabled}
          >
            <span className="amendment-form__layer-num">L{layer}</span>
            <span className="amendment-form__layer-name">{name}</span>
          </button>
        );
      })}
    </div>
  );
});

interface PrinciplesSelectorProps {
  selected: string[];
  onChange: (selected: string[]) => void;
  principles: string[];
  disabled?: boolean;
}

const PrinciplesSelector = memo(function PrinciplesSelector({
  selected,
  onChange,
  principles,
  disabled,
}: PrinciplesSelectorProps) {
  const toggle = (principle: string) => {
    if (selected.includes(principle)) {
      onChange(selected.filter((p) => p !== principle));
    } else {
      onChange([...selected, principle]);
    }
  };

  return (
    <div className="amendment-form__principles">
      {principles.map((principle) => (
        <label key={principle} className="amendment-form__principle">
          <input
            type="checkbox"
            checked={selected.includes(principle)}
            onChange={() => toggle(principle)}
            disabled={disabled}
          />
          <span className="amendment-form__principle-name">{principle}</span>
        </label>
      ))}
    </div>
  );
});

// =============================================================================
// Main Component
// =============================================================================

export const AmendmentProposalForm = memo(function AmendmentProposalForm({
  isOpen,
  onClose,
  onSubmit,
  kblocks = MOCK_KBLOCKS,
  principles = MOCK_PRINCIPLES,
  isLoading = false,
}: AmendmentProposalFormProps) {
  const [formState, setFormState] = useState<FormState>(initialFormState);
  const [errors, setErrors] = useState<Partial<Record<keyof FormState, string>>>({});

  const updateField = useCallback(
    <K extends keyof FormState>(field: K, value: FormState[K]) => {
      setFormState((prev) => ({ ...prev, [field]: value }));
      // Clear error when field is updated
      if (errors[field]) {
        setErrors((prev) => ({ ...prev, [field]: undefined }));
      }
    },
    [errors]
  );

  const validate = useCallback((): boolean => {
    const newErrors: Partial<Record<keyof FormState, string>> = {};

    if (!formState.title.trim()) {
      newErrors.title = 'Title is required';
    }
    if (!formState.description.trim()) {
      newErrors.description = 'Description is required';
    }
    if (!formState.targetKblock) {
      newErrors.targetKblock = 'Target K-Block is required';
    }
    if (!formState.proposedContent.trim()) {
      newErrors.proposedContent = 'Proposed content is required';
    }
    if (!formState.reasoning.trim()) {
      newErrors.reasoning = 'Reasoning is required';
    }

    setErrors(newErrors);
    return Object.keys(newErrors).length === 0;
  }, [formState]);

  const handleSubmit = useCallback(
    (submitForReview: boolean) => {
      if (!validate()) return;

      const input: AmendmentProposalInput = {
        title: formState.title.trim(),
        description: formState.description.trim(),
        amendmentType: formState.amendmentType,
        targetKblock: formState.targetKblock,
        targetLayer: formState.targetLayer,
        proposedContent: formState.proposedContent,
        reasoning: formState.reasoning.trim(),
        principlesAffected: formState.principlesAffected,
        submitForReview,
      };

      onSubmit(input);
      setFormState(initialFormState);
    },
    [formState, validate, onSubmit]
  );

  const handleClose = useCallback(() => {
    setFormState(initialFormState);
    setErrors({});
    onClose();
  }, [onClose]);

  // Handle escape key
  const handleKeyDown = useCallback(
    (e: React.KeyboardEvent) => {
      if (e.key === 'Escape') {
        handleClose();
      }
    },
    [handleClose]
  );

  if (!isOpen) return null;

  return (
    <div
      className="amendment-form__overlay"
      onClick={handleClose}
      onKeyDown={handleKeyDown}
      role="dialog"
      aria-modal="true"
      aria-labelledby="amendment-form-title"
    >
      <div className="amendment-form" onClick={(e) => e.stopPropagation()}>
        <div className="amendment-form__header">
          <FileText size={16} />
          <h2 id="amendment-form-title" className="amendment-form__title">
            Propose Amendment
          </h2>
          <button className="amendment-form__close" onClick={handleClose} aria-label="Close">
            <X size={18} />
          </button>
        </div>

        <div className="amendment-form__content">
          {/* Title */}
          <div className="amendment-form__field">
            <label className="amendment-form__label">
              Title <span className="amendment-form__required">*</span>
            </label>
            <input
              type="text"
              className={`amendment-form__input ${errors.title ? 'amendment-form__input--error' : ''}`}
              placeholder="e.g., Add HETERARCHICAL principle"
              value={formState.title}
              onChange={(e) => updateField('title', e.target.value)}
              disabled={isLoading}
              autoFocus
            />
            {errors.title && <span className="amendment-form__error">{errors.title}</span>}
          </div>

          {/* Description */}
          <div className="amendment-form__field">
            <label className="amendment-form__label">
              Description <span className="amendment-form__required">*</span>
            </label>
            <textarea
              className={`amendment-form__textarea ${errors.description ? 'amendment-form__textarea--error' : ''}`}
              placeholder="Briefly describe what this amendment does..."
              value={formState.description}
              onChange={(e) => updateField('description', e.target.value)}
              disabled={isLoading}
              rows={2}
            />
            {errors.description && (
              <span className="amendment-form__error">{errors.description}</span>
            )}
          </div>

          {/* Amendment Type */}
          <div className="amendment-form__field">
            <label className="amendment-form__label">Amendment Type</label>
            <select
              className="amendment-form__select"
              value={formState.amendmentType}
              onChange={(e) => updateField('amendmentType', e.target.value as AmendmentType)}
              disabled={isLoading}
            >
              {(Object.entries(AMENDMENT_TYPE_LABELS) as [AmendmentType, string][]).map(
                ([type, label]) => (
                  <option key={type} value={type}>
                    {label}
                  </option>
                )
              )}
            </select>
          </div>

          {/* Target K-Block */}
          <div className="amendment-form__field">
            <label className="amendment-form__label">
              Target K-Block <span className="amendment-form__required">*</span>
            </label>
            <KBlockSelector
              value={formState.targetKblock}
              onChange={(value) => updateField('targetKblock', value)}
              kblocks={kblocks}
              disabled={isLoading}
            />
            {errors.targetKblock && (
              <span className="amendment-form__error">{errors.targetKblock}</span>
            )}
          </div>

          {/* Target Layer */}
          <div className="amendment-form__field">
            <label className="amendment-form__label">
              <Layers size={12} />
              Target Layer
            </label>
            <LayerSelector
              value={formState.targetLayer}
              onChange={(value) => updateField('targetLayer', value)}
              disabled={isLoading}
            />
          </div>

          {/* Proposed Content */}
          <div className="amendment-form__field amendment-form__field--large">
            <label className="amendment-form__label">
              <Edit3 size={12} />
              Proposed Content <span className="amendment-form__required">*</span>
            </label>
            <textarea
              className={`amendment-form__textarea amendment-form__textarea--code ${
                errors.proposedContent ? 'amendment-form__textarea--error' : ''
              }`}
              placeholder="Enter the proposed content (markdown)..."
              value={formState.proposedContent}
              onChange={(e) => updateField('proposedContent', e.target.value)}
              disabled={isLoading}
              rows={8}
            />
            {errors.proposedContent && (
              <span className="amendment-form__error">{errors.proposedContent}</span>
            )}
          </div>

          {/* Reasoning */}
          <div className="amendment-form__field">
            <label className="amendment-form__label">
              <AlertTriangle size={12} />
              Reasoning <span className="amendment-form__required">*</span>
            </label>
            <textarea
              className={`amendment-form__textarea ${errors.reasoning ? 'amendment-form__textarea--error' : ''}`}
              placeholder="Why is this amendment necessary? What problem does it solve?"
              value={formState.reasoning}
              onChange={(e) => updateField('reasoning', e.target.value)}
              disabled={isLoading}
              rows={3}
            />
            {errors.reasoning && <span className="amendment-form__error">{errors.reasoning}</span>}
          </div>

          {/* Principles Affected */}
          <div className="amendment-form__field">
            <label className="amendment-form__label">Principles Affected</label>
            <PrinciplesSelector
              selected={formState.principlesAffected}
              onChange={(value) => updateField('principlesAffected', value)}
              principles={principles}
              disabled={isLoading}
            />
          </div>
        </div>

        <div className="amendment-form__footer">
          <button
            type="button"
            className="amendment-form__btn amendment-form__btn--secondary"
            onClick={handleClose}
            disabled={isLoading}
          >
            Cancel
          </button>
          <button
            type="button"
            className="amendment-form__btn amendment-form__btn--draft"
            onClick={() => handleSubmit(false)}
            disabled={isLoading}
          >
            Save as Draft
          </button>
          <button
            type="button"
            className="amendment-form__btn amendment-form__btn--primary"
            onClick={() => handleSubmit(true)}
            disabled={isLoading}
          >
            <Check size={14} />
            Submit for Review
          </button>
        </div>
      </div>
    </div>
  );
});

export default AmendmentProposalForm;
