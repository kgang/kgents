/**
 * GenesisActions - Phase 5: Departure
 *
 * "Where will you go from here?"
 *
 * Exit CTAs:
 * - Write Spec - Start creating your first specification
 * - Explore Editor - Jump into the Hypergraph Editor
 * - See Examples - View example K-Blocks and specs
 *
 * Features:
 * - Contextual summary of explored K-Block
 * - Three primary action cards with descriptions
 * - Smooth transitions and hover states
 * - Back button to return to exploration
 *
 * @see spec/protocols/genesis-clean-slate.md
 */

import { memo, useCallback } from 'react';
import { motion } from 'framer-motion';
import { useNavigate } from 'react-router-dom';
import { FileText, Layout, BookOpen, ArrowLeft, Sparkles } from 'lucide-react';
import type { CleanSlateKBlock } from '../../../api/client';

// =============================================================================
// Types
// =============================================================================

interface GenesisActionsProps {
  /** Last selected K-Block for context */
  selectedKBlock: CleanSlateKBlock | null;
  /** Go back to graph exploration */
  onBack: () => void;
}

interface ActionCardProps {
  icon: React.ReactNode;
  title: string;
  description: string;
  color: string;
  onClick: () => void;
  delay?: number;
}

// =============================================================================
// Animation Variants
// =============================================================================

const containerVariants = {
  hidden: { opacity: 0 },
  visible: {
    opacity: 1,
    transition: {
      staggerChildren: 0.15,
      delayChildren: 0.3,
    },
  },
};

const itemVariants = {
  hidden: { opacity: 0, y: 20 },
  visible: {
    opacity: 1,
    y: 0,
    transition: {
      duration: 0.5,
      ease: [0.25, 0.46, 0.45, 0.94] as const,
    },
  },
};

const cardVariants = {
  hidden: { opacity: 0, y: 30, scale: 0.95 },
  visible: (delay: number) => ({
    opacity: 1,
    y: 0,
    scale: 1,
    transition: {
      delay: delay * 0.1,
      duration: 0.5,
      ease: [0.25, 0.46, 0.45, 0.94] as const,
    },
  }),
};

// =============================================================================
// Sub-components
// =============================================================================

const ActionCard = memo(function ActionCard({
  icon,
  title,
  description,
  color,
  onClick,
  delay = 0,
}: ActionCardProps) {
  return (
    <motion.button
      type="button"
      className="genesis-actions__card"
      style={{ '--card-color': color } as React.CSSProperties}
      variants={cardVariants}
      custom={delay}
      whileHover={{
        scale: 1.03,
        boxShadow: `0 12px 40px rgba(0, 0, 0, 0.3), 0 0 30px ${color}30`,
      }}
      whileTap={{ scale: 0.98 }}
      onClick={onClick}
    >
      <div className="genesis-actions__card-icon" style={{ color }}>
        {icon}
      </div>
      <h3 className="genesis-actions__card-title">{title}</h3>
      <p className="genesis-actions__card-description">{description}</p>
      <div className="genesis-actions__card-arrow">
        <motion.span
          animate={{ x: [0, 5, 0] }}
          transition={{ duration: 1.5, repeat: Infinity, ease: 'easeInOut' }}
        >
          {'\u2192'}
        </motion.span>
      </div>
    </motion.button>
  );
});

// =============================================================================
// Main Component
// =============================================================================

export const GenesisActions = memo(function GenesisActions({
  selectedKBlock,
  onBack,
}: GenesisActionsProps) {
  const navigate = useNavigate();

  // Navigation handlers
  const handleWriteSpec = useCallback(() => {
    navigate('/world.document');
  }, [navigate]);

  const handleExploreEditor = useCallback(() => {
    navigate('/world.document');
  }, [navigate]);

  const handleSeeExamples = useCallback(() => {
    navigate('/genesis/showcase');
  }, [navigate]);

  return (
    <div className="genesis-actions">
      {/* Back Button */}
      <motion.button
        type="button"
        className="genesis-actions__back"
        initial={{ opacity: 0, x: -20 }}
        animate={{ opacity: 1, x: 0 }}
        onClick={onBack}
        whileHover={{ x: -5 }}
      >
        <ArrowLeft size={18} />
        <span>Back to Graph</span>
      </motion.button>

      {/* Main Content */}
      <motion.div
        className="genesis-actions__content"
        variants={containerVariants}
        initial="hidden"
        animate="visible"
      >
        {/* Header */}
        <motion.div className="genesis-actions__header" variants={itemVariants}>
          <motion.div
            className="genesis-actions__sparkle"
            animate={{
              rotate: [0, 10, -10, 0],
              scale: [1, 1.1, 1],
            }}
            transition={{ duration: 4, repeat: Infinity, ease: 'easeInOut' }}
          >
            <Sparkles size={32} />
          </motion.div>
          <h1 className="genesis-actions__title">Where will you go?</h1>
          <p className="genesis-actions__subtitle">
            The Constitutional Graph is your foundation. Now it's time to build.
          </p>
        </motion.div>

        {/* Context from exploration */}
        {selectedKBlock && (
          <motion.div className="genesis-actions__context" variants={itemVariants}>
            <p className="genesis-actions__context-label">You explored:</p>
            <p className="genesis-actions__context-value">{selectedKBlock.title}</p>
          </motion.div>
        )}

        {/* Action Cards */}
        <div className="genesis-actions__cards">
          <ActionCard
            icon={<FileText size={28} />}
            title="Write Spec"
            description="Start creating your first specification. Ground your ideas in constitutional principles."
            color="#c4a77d"
            onClick={handleWriteSpec}
            delay={0}
          />

          <ActionCard
            icon={<Layout size={28} />}
            title="Explore Editor"
            description="Jump into the Hypergraph Editor. Edit K-Blocks, trace derivations, witness emergence."
            color="#6b8b6b"
            onClick={handleExploreEditor}
            delay={1}
          />

          <ActionCard
            icon={<BookOpen size={28} />}
            title="See Examples"
            description="View the full Constitutional Graph. Study how the 22 K-Blocks derive from axioms."
            color="#8b7355"
            onClick={handleSeeExamples}
            delay={2}
          />
        </div>

        {/* Footer Quote */}
        <motion.div className="genesis-actions__footer" variants={itemVariants}>
          <p className="genesis-actions__quote">
            "Every K-Block you create derives from these principles.
            <br />
            The constitution is not a constraint—it's a foundation."
          </p>
        </motion.div>
      </motion.div>
    </div>
  );
});

export default GenesisActions;
