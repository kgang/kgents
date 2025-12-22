/**
 * AspectPanel - Actions you can DO on a path.
 *
 * "Aspects are ACTIONS, not form fields"
 *
 * Each aspect is a button that invokes it. Examples from metadata
 * become one-click presets. Ghost aspects (not available to current
 * observer) are shown grayed with hover explanation.
 *
 * Now with Umwelt animations: when the observer changes, aspects
 * animate in/out based on whether they're newly revealed or hidden.
 *
 * @see plans/umwelt-visualization.md
 */

import { useState, useCallback, useMemo } from 'react';
import { motion } from 'framer-motion';
import {
  Play,
  Eye,
  Zap,
  RefreshCw,
  Sparkles,
  AlertTriangle,
  Lock,
  ChevronDown,
  type LucideIcon,
} from 'lucide-react';
import type { Density } from '@/hooks/useDesignPolynomial';
import type { PathMetadata, AspectSchema } from './useAgenteseDiscovery';
import type { Observer } from './ObserverPicker';
import { Shimmer, useMotionPreferences } from '@/components/joy';
import { useUmweltSafe, UMWELT_MOTION, UMWELT_DENSITY_CONFIG } from './umwelt';

// =============================================================================
// Types
// =============================================================================

interface AspectPanelProps {
  path: string;
  metadata: PathMetadata;
  schema?: Record<string, AspectSchema>;
  selectedAspect: string;
  observer: Observer;
  onInvoke: (aspect: string, payload?: unknown) => void;
  density: Density;
  compact?: boolean;
}

// =============================================================================
// Aspect Styling
// =============================================================================

interface AspectStyle {
  icon: LucideIcon;
  color: string;
  bgColor: string;
}

const ASPECT_STYLES: Record<string, AspectStyle> = {
  manifest: { icon: Eye, color: 'text-cyan-400', bgColor: 'bg-cyan-500/10' },
  witness: { icon: Eye, color: 'text-blue-400', bgColor: 'bg-blue-500/10' },
  invoke: { icon: Zap, color: 'text-amber-400', bgColor: 'bg-amber-500/10' },
  create: { icon: Sparkles, color: 'text-green-400', bgColor: 'bg-green-500/10' },
  update: { icon: RefreshCw, color: 'text-violet-400', bgColor: 'bg-violet-500/10' },
  delete: { icon: AlertTriangle, color: 'text-red-400', bgColor: 'bg-red-500/10' },
};

const DEFAULT_STYLE: AspectStyle = {
  icon: Play,
  color: 'text-steel-zinc',
  bgColor: 'bg-steel-zinc/10',
};

function getAspectStyle(aspect: string): AspectStyle {
  // Check for exact match
  if (aspect in ASPECT_STYLES) return ASPECT_STYLES[aspect];

  // Check for suffix match
  for (const [key, style] of Object.entries(ASPECT_STYLES)) {
    if (aspect.endsWith(key) || aspect.includes(key)) {
      return style;
    }
  }

  return DEFAULT_STYLE;
}

// =============================================================================
// Component
// =============================================================================

export function AspectPanel({
  path,
  metadata,
  schema,
  selectedAspect,
  observer,
  onInvoke,
  density,
  compact = false,
}: AspectPanelProps) {
  const [loadingAspect, setLoadingAspect] = useState<string | null>(null);
  const [expandedExamples, setExpandedExamples] = useState<Set<string>>(new Set());

  // Motion preferences and umwelt context
  const { shouldAnimate } = useMotionPreferences();
  const umwelt = useUmweltSafe();

  // Get animation config for density
  const animConfig = UMWELT_DENSITY_CONFIG[density];

  // Extract aspects from metadata
  const aspects = useMemo(() => {
    return metadata.aspects || ['manifest'];
  }, [metadata]);

  // Check if an aspect is being revealed/hidden in current transition
  const getAspectAnimationState = useCallback(
    (aspect: string): 'revealed' | 'hidden' | 'unchanged' => {
      if (!umwelt || !umwelt.isTransitioning) return 'unchanged';

      const key = `${path}:${aspect}`;
      if (umwelt.revealingAspects.has(key)) return 'revealed';
      if (umwelt.hidingAspects.has(key)) return 'hidden';
      return 'unchanged';
    },
    [umwelt, path]
  );

  // Check if aspect is available to current observer
  const isAspectAvailable = useCallback(
    (aspect: string): { available: boolean; reason?: string } => {
      // For now, all aspects are available if you have read capability
      // More sophisticated logic would check effects against capabilities
      const hasRead = observer.capabilities.includes('read');
      const hasWrite = observer.capabilities.includes('write');
      const hasAdmin = observer.capabilities.includes('admin');

      // Mutations require write
      if (['create', 'update', 'delete'].some((m) => aspect.includes(m))) {
        if (!hasWrite) {
          return { available: false, reason: 'Requires write capability' };
        }
      }

      // Admin aspects
      if (aspect.includes('admin') || aspect.includes('govern')) {
        if (!hasAdmin) {
          return { available: false, reason: 'Requires admin capability' };
        }
      }

      if (!hasRead) {
        return { available: false, reason: 'Requires read capability' };
      }

      return { available: true };
    },
    [observer]
  );

  // Handle aspect invocation
  const handleInvoke = useCallback(
    async (aspect: string, payload?: unknown) => {
      setLoadingAspect(aspect);
      try {
        await onInvoke(aspect, payload);
      } finally {
        setLoadingAspect(null);
      }
    },
    [onInvoke]
  );

  // Get examples for an aspect
  const getAspectExamples = useCallback(
    (aspect: string) => {
      if (!metadata.examples) return [];
      return metadata.examples.filter((ex) => ex.aspect === aspect);
    },
    [metadata.examples]
  );

  // Toggle example expansion
  const toggleExamples = useCallback((aspect: string) => {
    setExpandedExamples((prev) => {
      const next = new Set(prev);
      if (next.has(aspect)) {
        next.delete(aspect);
      } else {
        next.add(aspect);
      }
      return next;
    });
  }, []);

  // Animation variants for aspect buttons
  const getAspectVariants = (aspectAnimState: 'revealed' | 'hidden' | 'unchanged', idx: number) => {
    if (!shouldAnimate || aspectAnimState === 'unchanged') {
      return {};
    }

    const staggerDelay = animConfig.stagger ? idx * (animConfig.staggerDelay / 1000) : 0;

    if (aspectAnimState === 'revealed') {
      return {
        initial: {
          opacity: 0,
          scale: UMWELT_MOTION.revealScale.from,
          filter: 'brightness(1.5)',
        },
        animate: {
          opacity: 1,
          scale: UMWELT_MOTION.revealScale.to,
          filter: 'brightness(1)',
          transition: {
            duration: UMWELT_MOTION.standard / 1000,
            delay: staggerDelay,
            ease: UMWELT_MOTION.enter,
          },
        },
      };
    }

    if (aspectAnimState === 'hidden') {
      return {
        initial: { opacity: 1, scale: 1 },
        animate: {
          opacity: UMWELT_MOTION.ghostOpacity,
          scale: UMWELT_MOTION.hideScale.to,
          filter: 'grayscale(0.8)',
          transition: {
            duration: UMWELT_MOTION.standard / 1000,
            delay: staggerDelay,
            ease: UMWELT_MOTION.exit,
          },
        },
      };
    }

    return {};
  };

  // Compact mode: horizontal chip layout
  if (compact) {
    return (
      <div className="flex flex-wrap gap-2">
        {aspects.map((aspect, idx) => {
          const style = getAspectStyle(aspect);
          const { available, reason } = isAspectAvailable(aspect);
          const isLoading = loadingAspect === aspect;
          const isSelected = selectedAspect === aspect;
          const Icon = available ? style.icon : Lock;
          const animState = getAspectAnimationState(aspect);
          const variants = getAspectVariants(animState, idx);

          return (
            <motion.button
              key={aspect}
              {...(Object.keys(variants).length > 0 ? variants : {})}
              onClick={() => available && handleInvoke(aspect)}
              disabled={!available || isLoading}
              title={reason}
              className={`
                flex items-center gap-1.5 px-3 py-1.5 rounded-full text-sm
                transition-colors
                ${
                  isSelected
                    ? `${style.bgColor} ${style.color} ring-1 ring-current/50`
                    : available
                      ? 'bg-steel-slate/50 text-steel-zinc hover:bg-steel-gunmetal/50'
                      : 'bg-steel-carbon/50 text-steel-gunmetal cursor-not-allowed'
                }
              `}
            >
              {isLoading ? (
                <motion.span
                  animate={{ rotate: 360 }}
                  transition={{ duration: 1, repeat: Infinity, ease: 'linear' }}
                >
                  <RefreshCw className="w-3 h-3" />
                </motion.span>
              ) : (
                <Icon className="w-3 h-3" />
              )}
              <span>{aspect}</span>
            </motion.button>
          );
        })}
      </div>
    );
  }

  // Full mode: vertical list with examples
  return (
    <div className="h-full flex flex-col">
      <div className="p-4 border-b border-steel-gunmetal">
        <h3 className="text-sm font-medium text-steel-zinc uppercase tracking-wider">Actions</h3>
        <p className="text-xs text-steel-zinc mt-1">{path}</p>
      </div>

      <div className="flex-1 overflow-y-auto p-3 space-y-2">
        {aspects.map((aspect, idx) => {
          const style = getAspectStyle(aspect);
          const { available, reason } = isAspectAvailable(aspect);
          const isLoading = loadingAspect === aspect;
          const isSelected = selectedAspect === aspect;
          const examples = getAspectExamples(aspect);
          const hasExamples = examples.length > 0;
          const showExamples = expandedExamples.has(aspect);
          const Icon = available ? style.icon : Lock;
          const animState = getAspectAnimationState(aspect);
          const variants = getAspectVariants(animState, idx);

          return (
            <motion.div key={aspect} {...(Object.keys(variants).length > 0 ? variants : {})}>
              {/* Aspect button */}
              <button
                onClick={() => available && handleInvoke(aspect)}
                disabled={!available || isLoading}
                title={reason}
                className={`
                  w-full flex items-center gap-3 p-3 rounded-lg text-left
                  transition-colors group
                  ${
                    isSelected
                      ? `${style.bgColor} ring-1 ring-${style.color.replace('text-', '')}/30`
                      : available
                        ? 'hover:bg-steel-slate/30'
                        : 'opacity-50 cursor-not-allowed'
                  }
                `}
              >
                {/* Icon */}
                <div
                  className={`
                    w-10 h-10 rounded-lg flex items-center justify-center
                    ${style.bgColor}
                  `}
                >
                  {isLoading ? (
                    <motion.span
                      animate={{ rotate: 360 }}
                      transition={{ duration: 1, repeat: Infinity, ease: 'linear' }}
                    >
                      <RefreshCw className={`w-5 h-5 ${style.color}`} />
                    </motion.span>
                  ) : (
                    <Icon className={`w-5 h-5 ${style.color}`} />
                  )}
                </div>

                {/* Label and description */}
                <div className="flex-1 min-w-0">
                  <div className={`font-medium ${isSelected ? style.color : 'text-white'}`}>
                    {aspect}
                  </div>
                  {!available && reason && <div className="text-xs text-steel-zinc">{reason}</div>}
                </div>

                {/* Examples toggle */}
                {hasExamples && (
                  <button
                    onClick={(e) => {
                      e.stopPropagation();
                      toggleExamples(aspect);
                    }}
                    className="p-1 hover:bg-steel-gunmetal/50 rounded transition-colors"
                  >
                    <ChevronDown
                      className={`w-4 h-4 text-steel-zinc transition-transform ${
                        showExamples ? 'rotate-180' : ''
                      }`}
                    />
                  </button>
                )}
              </button>

              {/* Examples */}
              {hasExamples && showExamples && (
                <motion.div
                  initial={{ height: 0, opacity: 0 }}
                  animate={{ height: 'auto', opacity: 1 }}
                  className="ml-4 mt-1 space-y-1 overflow-hidden"
                >
                  {examples.map((example, i) => (
                    <button
                      key={i}
                      onClick={() => handleInvoke(aspect, example.payload)}
                      className="w-full flex items-center gap-2 p-2 pl-4 rounded-lg
                                 text-left text-sm bg-steel-slate/30 hover:bg-steel-slate/50
                                 transition-colors border-l-2 border-steel-gunmetal"
                    >
                      <Play className="w-3 h-3 text-cyan-400 flex-shrink-0" />
                      <span className="text-steel-zinc truncate">
                        {example.description || `Example ${i + 1}`}
                      </span>
                    </button>
                  ))}
                </motion.div>
              )}
            </motion.div>
          );
        })}
      </div>

      {/* Schema preview (for spacious) */}
      {density === 'spacious' && schema && selectedAspect && schema[selectedAspect] && (
        <div className="border-t border-steel-gunmetal p-4">
          <h4 className="text-xs font-medium text-steel-zinc uppercase mb-2">Schema</h4>
          <Shimmer active={false}>
            <pre className="text-xs text-steel-zinc overflow-auto max-h-32 bg-steel-carbon/50 rounded p-2">
              {JSON.stringify(schema[selectedAspect], null, 2)}
            </pre>
          </Shimmer>
        </div>
      )}
    </div>
  );
}

export default AspectPanel;
