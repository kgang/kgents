/**
 * TrailBuilderPanel - UI for creating new trails.
 *
 * "The trail creation UI should feel like curating a museum exhibit—
 * selecting artifacts, arranging them meaningfully, adding interpretive labels."
 *
 * Features:
 * - Progressive step building
 * - Edge type selection
 * - Reasoning prompts
 * - Undo/redo
 * - Topic tagging
 *
 * @see brainstorming/visual-trail-graph-r&d.md Section 2
 * @see spec/protocols/trail-protocol.md
 */

import { useState, useCallback } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import {
  useTrailBuilder,
  EDGE_TYPES,
  selectCanUndo,
  selectCanRedo,
  selectIsValid,
  getReasoningLevel,
  getReasoningPlaceholder,
  validateReasoning,
  type EdgeType,
  type TrailBuilderStep,
} from '../../stores/trailBuilder';
import { PathPicker } from './PathPicker';

// =============================================================================
// Component
// =============================================================================

interface TrailBuilderPanelProps {
  /** Callback when trail is successfully created */
  onTrailCreated?: (trailId: string) => void;
  /** Optional className */
  className?: string;
}

export function TrailBuilderPanel({
  onTrailCreated,
  className = '',
}: TrailBuilderPanelProps) {
  const {
    name,
    steps,
    topics,
    isOpen,
    isSaving,
    error,
    currentBranchId,
    open,
    close,
    setName,
    addStep,
    updateStep,
    removeStep,
    reorderSteps,
    addTopic,
    removeTopic,
    undo,
    redo,
    reset,
    save,
    branchFrom,
    switchBranch,
  } = useTrailBuilder();

  const canUndo = useTrailBuilder(selectCanUndo);
  const canRedo = useTrailBuilder(selectCanRedo);
  const isValid = useTrailBuilder(selectIsValid);

  // Path picker state
  const [showPathPicker, setShowPathPicker] = useState(false);
  const [branchFromStepId, setBranchFromStepId] = useState<string | null>(null);
  const [topicInput, setTopicInput] = useState('');

  // Handle save with reasoning validation (Session 2)
  const handleSave = useCallback(async () => {
    // Validate reasoning before save
    const validation = validateReasoning({ name, steps } as Parameters<typeof validateReasoning>[0]);

    if (!validation.canSave) {
      // Validation errors will be handled by store's save() error state
      console.warn('[TrailBuilder] Validation errors:', validation.errors);
    }

    // Show warnings in console but don't block
    if (validation.warnings.length > 0) {
      console.warn('[TrailBuilder] Validation warnings:', validation.warnings);
    }

    const trailId = await save();
    if (trailId) {
      onTrailCreated?.(trailId);
    }
  }, [save, onTrailCreated, name, steps]);

  // Handle add topic
  const handleAddTopic = useCallback(() => {
    if (topicInput.trim()) {
      addTopic(topicInput.trim());
      setTopicInput('');
    }
  }, [topicInput, addTopic]);

  // Collapsed state (just a button)
  if (!isOpen) {
    return (
      <button
        onClick={open}
        className={`
          flex items-center gap-2 px-4 py-2
          bg-gradient-to-r from-blue-600 to-blue-500
          hover:from-blue-500 hover:to-blue-400
          text-white font-medium rounded-lg
          shadow-lg shadow-blue-500/20
          transition-all
          ${className}
        `}
      >
        <span className="text-lg">+</span>
        <span>New Trail</span>
      </button>
    );
  }

  return (
    <motion.div
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
      exit={{ opacity: 0, y: 20 }}
      className={`
        bg-gray-900 border border-gray-700 rounded-lg shadow-xl
        w-[360px] max-h-[80vh] overflow-hidden flex flex-col
        relative z-20
        ${className}
      `}
    >
      {/* Header */}
      <div className="flex items-center justify-between px-4 py-3 border-b border-gray-700">
        <h3 className="font-medium text-white">New Trail</h3>
        <div className="flex items-center gap-2">
          <button
            onClick={undo}
            disabled={!canUndo}
            className="p-1.5 text-gray-400 hover:text-white disabled:opacity-30 disabled:cursor-not-allowed"
            title="Undo"
          >
            ↩
          </button>
          <button
            onClick={redo}
            disabled={!canRedo}
            className="p-1.5 text-gray-400 hover:text-white disabled:opacity-30 disabled:cursor-not-allowed"
            title="Redo"
          >
            ↪
          </button>
          <button
            onClick={close}
            className="p-1.5 text-gray-400 hover:text-white"
          >
            ×
          </button>
        </div>
      </div>

      {/* Content */}
      <div className="flex-1 overflow-y-auto p-4 space-y-4">
        {/* Error message */}
        {error && (
          <div className="p-3 bg-red-900/30 border border-red-800 rounded text-red-300 text-sm">
            {error}
          </div>
        )}

        {/* Trail name */}
        <div>
          <label className="block text-sm text-gray-400 mb-1">Name</label>
          <input
            type="text"
            value={name}
            onChange={(e) => setName(e.target.value)}
            placeholder="Understanding Auth Flow"
            className="
              w-full px-3 py-2 bg-gray-800 border border-gray-700 rounded
              text-white placeholder-gray-500
              focus:outline-none focus:border-blue-500
            "
          />
        </div>

        {/* Steps */}
        <div>
          <div className="flex items-center justify-between mb-2">
            <label className="text-sm text-gray-400">Steps</label>
            <span className="text-xs text-gray-500">{steps.length} step(s)</span>
          </div>

          <div className="space-y-2">
            <AnimatePresence mode="popLayout">
              {steps.map((step, index) => (
                <StepItem
                  key={step.id}
                  step={step}
                  allSteps={steps}
                  index={index}
                  isFirst={index === 0}
                  isBranchPoint={step.children.length > 1}
                  isCurrentBranch={currentBranchId === step.id}
                  onUpdate={(updates) => updateStep(step.id, updates)}
                  onRemove={() => removeStep(step.id)}
                  onMoveUp={() => index > 0 && reorderSteps(index, index - 1)}
                  onMoveDown={() =>
                    index < steps.length - 1 && reorderSteps(index, index + 1)
                  }
                  onBranch={() => {
                    setBranchFromStepId(step.id);
                    setShowPathPicker(true);
                  }}
                  onSwitchTo={() => switchBranch(step.id)}
                />
              ))}
            </AnimatePresence>

            {/* Add step button */}
            <button
              onClick={() => setShowPathPicker(true)}
              className="
                w-full py-2 border border-dashed border-gray-600
                rounded text-gray-400 hover:text-white hover:border-gray-500
                transition-colors flex items-center justify-center gap-2
              "
            >
              <span>+</span>
              <span>Add Step</span>
            </button>
          </div>
        </div>

        {/* Topics */}
        <div>
          <label className="block text-sm text-gray-400 mb-2">Topics</label>
          <div className="flex flex-wrap gap-1 mb-2">
            {topics.map((topic) => (
              <span
                key={topic}
                className="
                  inline-flex items-center gap-1 px-2 py-0.5
                  bg-gray-800 rounded text-sm text-gray-300
                "
              >
                {topic}
                <button
                  onClick={() => removeTopic(topic)}
                  className="text-gray-500 hover:text-red-400"
                >
                  ×
                </button>
              </span>
            ))}
          </div>
          <div className="flex gap-2">
            <input
              type="text"
              value={topicInput}
              onChange={(e) => setTopicInput(e.target.value)}
              placeholder="Add topic..."
              className="
                flex-1 px-3 py-1.5 bg-gray-800 border border-gray-700 rounded
                text-white placeholder-gray-500 text-sm
                focus:outline-none focus:border-blue-500
              "
              onKeyDown={(e) => {
                if (e.key === 'Enter') {
                  e.preventDefault();
                  handleAddTopic();
                }
              }}
            />
            <button
              onClick={handleAddTopic}
              disabled={!topicInput.trim()}
              className="
                px-3 py-1.5 bg-gray-700 hover:bg-gray-600
                rounded text-sm text-white
                disabled:opacity-50 disabled:cursor-not-allowed
              "
            >
              +
            </button>
          </div>
        </div>
      </div>

      {/* Footer */}
      <div className="flex items-center justify-between px-4 py-3 border-t border-gray-700">
        <button
          onClick={reset}
          className="text-sm text-gray-400 hover:text-white"
        >
          Reset
        </button>
        <div className="flex gap-2">
          <button
            onClick={close}
            className="px-4 py-2 text-sm text-gray-400 hover:text-white"
          >
            Cancel
          </button>
          <button
            onClick={handleSave}
            disabled={!isValid || isSaving}
            className="
              px-4 py-2 text-sm bg-blue-600 hover:bg-blue-500
              text-white rounded
              disabled:opacity-50 disabled:cursor-not-allowed
            "
          >
            {isSaving ? 'Saving...' : 'Save Trail'}
          </button>
        </div>
      </div>

      {/* Path Picker Modal */}
      <PathPicker
        isOpen={showPathPicker}
        onClose={() => {
          setShowPathPicker(false);
          setBranchFromStepId(null);
        }}
        onSelect={(path) => {
          if (branchFromStepId) {
            // Branching from an existing step
            branchFrom(branchFromStepId, path);
          } else {
            // Normal step addition
            addStep(path);
          }
          setShowPathPicker(false);
          setBranchFromStepId(null);
        }}
      />
    </motion.div>
  );
}

// =============================================================================
// Step Item Component
// =============================================================================

interface StepItemProps {
  step: TrailBuilderStep;
  /** All steps for reasoning level calculation */
  allSteps: TrailBuilderStep[];
  index: number;
  isFirst: boolean;
  isBranchPoint: boolean;
  isCurrentBranch: boolean;
  onUpdate: (updates: Partial<{ path: string; edge: EdgeType | null; reasoning: string }>) => void;
  onRemove: () => void;
  onMoveUp: () => void;
  onMoveDown: () => void;
  onBranch: () => void;
  onSwitchTo: () => void;
}

function StepItem({
  step,
  allSteps,
  index,
  isFirst,
  isBranchPoint,
  isCurrentBranch,
  onUpdate,
  onRemove,
  onMoveUp,
  onMoveDown,
  onBranch,
  onSwitchTo,
}: StepItemProps) {
  const [isExpanded, setIsExpanded] = useState(false);

  // Extract holon from path
  const holon = step.path.split('/').pop()?.split('.')[0] || step.path;

  // Reasoning level for this step (Session 2)
  const reasoningLevel = getReasoningLevel(step, allSteps);
  const isReasoningRequired = reasoningLevel === 'branch';
  const isReasoningEncouraged = reasoningLevel === 'semantic';
  const placeholder = getReasoningPlaceholder(reasoningLevel);

  return (
    <motion.div
      layout
      initial={{ opacity: 0, y: -10 }}
      animate={{ opacity: 1, y: 0 }}
      exit={{ opacity: 0, y: -10 }}
      className={`
        bg-gray-800 rounded-lg overflow-hidden
        ${isCurrentBranch ? 'ring-2 ring-purple-500/50' : ''}
        ${isBranchPoint ? 'border-l-2 border-amber-500' : ''}
      `}
    >
      {/* Header */}
      <div className="flex items-center gap-2 p-2">
        {/* Step number with branch indicator */}
        <div
          className={`
            w-6 h-6 flex items-center justify-center rounded-full text-xs
            ${isCurrentBranch ? 'bg-purple-600 text-white' : 'bg-gray-700 text-gray-300'}
          `}
          onClick={onSwitchTo}
          title={isCurrentBranch ? 'Current branch' : 'Switch to this branch'}
          style={{ cursor: 'pointer' }}
        >
          {isBranchPoint ? '⑂' : index + 1}
        </div>

        {/* Path preview */}
        <div
          className="flex-1 min-w-0 cursor-pointer"
          onClick={() => setIsExpanded(!isExpanded)}
        >
          <div className="font-medium text-white truncate">{holon}</div>
          <div className="text-xs text-gray-500 truncate">{step.path}</div>
        </div>

        {/* Actions */}
        <div className="flex items-center gap-1">
          <button
            onClick={onBranch}
            className="p-1 text-purple-400 hover:text-purple-300"
            title="Branch from here"
          >
            ⑂
          </button>
          <button
            onClick={onMoveUp}
            disabled={isFirst}
            className="p-1 text-gray-500 hover:text-white disabled:opacity-30"
            title="Move up"
          >
            ↑
          </button>
          <button
            onClick={onMoveDown}
            className="p-1 text-gray-500 hover:text-white"
            title="Move down"
          >
            ↓
          </button>
          <button
            onClick={onRemove}
            className="p-1 text-gray-500 hover:text-red-400"
            title="Remove"
          >
            ×
          </button>
        </div>
      </div>

      {/* Expanded content */}
      <AnimatePresence>
        {isExpanded && (
          <motion.div
            initial={{ height: 0 }}
            animate={{ height: 'auto' }}
            exit={{ height: 0 }}
            className="overflow-hidden"
          >
            <div className="px-2 pb-2 space-y-2">
              {/* Edge type (not for first step) */}
              {!isFirst && (
                <div>
                  <label className="block text-xs text-gray-500 mb-1">Edge</label>
                  <select
                    value={step.edge || ''}
                    onChange={(e) =>
                      onUpdate({ edge: e.target.value as EdgeType })
                    }
                    className="
                      w-full px-2 py-1.5 bg-gray-700 border border-gray-600 rounded
                      text-white text-sm
                      focus:outline-none focus:border-blue-500
                    "
                  >
                    {EDGE_TYPES.map((type) => (
                      <option key={type.value} value={type.value}>
                        {type.icon} {type.label}
                        {type.semantic && ' (semantic)'}
                      </option>
                    ))}
                  </select>
                </div>
              )}

              {/* Reasoning (Session 2: Hierarchical indicators) */}
              <div>
                <label className={`
                  block text-xs mb-1
                  ${isReasoningRequired ? 'text-amber-400' : ''}
                  ${isReasoningEncouraged ? 'text-purple-400' : ''}
                  ${!isReasoningRequired && !isReasoningEncouraged ? 'text-gray-500' : ''}
                `}>
                  {isReasoningRequired && '✦ '}
                  {isReasoningEncouraged && '☆ '}
                  Why this step?
                  {isReasoningRequired && ' (required)'}
                  {isReasoningEncouraged && ' (encouraged)'}
                </label>
                <textarea
                  value={step.reasoning}
                  onChange={(e) => onUpdate({ reasoning: e.target.value })}
                  placeholder={placeholder}
                  rows={2}
                  className={`
                    w-full px-2 py-1.5 bg-gray-700 border rounded
                    text-white text-sm placeholder-gray-500 resize-none
                    focus:outline-none
                    ${isReasoningRequired && !step.reasoning.trim()
                      ? 'border-amber-500/50 focus:border-amber-400'
                      : isReasoningEncouraged && !step.reasoning.trim()
                        ? 'border-purple-500/30 focus:border-purple-400'
                        : 'border-gray-600 focus:border-blue-500'}
                  `}
                />
              </div>
            </div>
          </motion.div>
        )}
      </AnimatePresence>

      {/* Edge badge (collapsed view) */}
      {!isExpanded && !isFirst && step.edge && (
        <div className="px-2 pb-2">
          <span className="inline-flex items-center gap-1 px-2 py-0.5 bg-gray-700 rounded text-xs text-gray-400">
            via {EDGE_TYPES.find((t) => t.value === step.edge)?.label || step.edge}
          </span>
        </div>
      )}
    </motion.div>
  );
}

export default TrailBuilderPanel;
