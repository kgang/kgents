/**
 * Portal — Inline edge expansion
 *
 * "Navigation IS expansion" — see target content inline without losing context.
 *
 * Animations:
 * - 250ms ease-out for height/opacity on open
 * - 200ms ease-in for collapse
 */

import { memo } from 'react';
import { motion } from 'framer-motion';
import type { PortalState } from '../state/types';

interface PortalProps {
  portal: PortalState;
}

export const Portal = memo(function Portal({ portal }: PortalProps) {
  return (
    <motion.div
      className="portal"
      initial={{ height: 0, opacity: 0 }}
      animate={{ height: 'auto', opacity: 1 }}
      exit={{ height: 0, opacity: 0 }}
      transition={{
        height: { duration: 0.25, ease: 'easeOut' },
        opacity: { duration: 0.2, ease: 'easeOut' },
      }}
      style={{ overflow: 'hidden' }}
    >
      <div className="portal__border" />
      {portal.loading ? (
        <div className="portal__loading">
          <div className="portal__spinner" />
          <span>Loading...</span>
        </div>
      ) : portal.targetNode ? (
        <div className="portal__content">
          <div className="portal__header">
            <span className="portal__title">{portal.targetNode.title}</span>
            <span className="portal__path">{portal.targetNode.path}</span>
            {portal.targetNode.tier && (
              <span className="portal__tier" data-tier={portal.targetNode.tier}>
                {portal.targetNode.tier}
              </span>
            )}
          </div>
          <pre className="portal__body">{portal.targetNode.content || '(empty)'}</pre>
        </div>
      ) : (
        <div className="portal__error">Failed to load portal content</div>
      )}
    </motion.div>
  );
});
