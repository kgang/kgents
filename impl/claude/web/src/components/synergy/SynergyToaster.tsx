/**
 * SynergyToaster - Cross-Jewel Toast Notifications
 *
 * Renders the toast container and active toasts.
 * Uses Radix UI Toast primitives with custom styling.
 *
 * Foundation 4: Make synergies visible to users.
 * The Crown is ONE engine - show the connections!
 */

import * as Toast from '@radix-ui/react-toast';
import { AnimatePresence, motion } from 'framer-motion';
import { X, ArrowRight } from 'lucide-react';
import { Link } from 'react-router-dom';
import { JEWEL_INFO } from './types';
import type { SynergyToast, SynergyToastType } from './types';
import { useSynergyToastStore } from './store';

/**
 * Toast type to icon mapping.
 */
const TYPE_STYLES: Record<
  SynergyToastType,
  { bg: string; border: string; icon: string }
> = {
  success: {
    bg: 'bg-[rgba(74,107,74,0.1)]', // life-sage with alpha
    border: 'border-[var(--color-life-sage)]',
    icon: '●',
  },
  info: {
    bg: 'bg-[rgba(74,158,255,0.1)]', // status-normal with alpha
    border: 'border-[var(--status-normal)]',
    icon: '◎',
  },
  warning: {
    bg: 'bg-[rgba(196,167,125,0.1)]', // glow-spore with alpha
    border: 'border-[var(--color-glow-spore)]',
    icon: '◇',
  },
  error: {
    bg: 'bg-[rgba(166,93,74,0.1)]', // accent-error with alpha
    border: 'border-[var(--accent-error)]',
    icon: '◆',
  },
};

/**
 * Individual synergy toast component.
 */
function SynergyToastItem({
  toast,
  onClose,
}: {
  toast: SynergyToast;
  onClose: () => void;
}) {
  const sourceInfo = JEWEL_INFO[toast.sourceJewel];
  const targetInfo = toast.targetJewel !== '*' ? JEWEL_INFO[toast.targetJewel] : null;
  const typeStyle = TYPE_STYLES[toast.type];

  return (
    <Toast.Root
      className="relative"
      duration={toast.duration}
      onOpenChange={(open) => {
        if (!open) onClose();
      }}
    >
      <motion.div
        initial={{ opacity: 0, y: 50, scale: 0.95 }}
        animate={{ opacity: 1, y: 0, scale: 1 }}
        exit={{ opacity: 0, y: 20, scale: 0.95 }}
        transition={{ duration: 0.2, ease: 'easeOut' }}
        className={`
          relative
          pointer-events-auto
          min-w-[320px] max-w-[400px]
          rounded-lg border
          ${typeStyle.bg} ${typeStyle.border}
          backdrop-blur-sm
          shadow-lg shadow-black/20
          overflow-hidden
        `}
      >
        {/* Progress bar */}
        {toast.duration && toast.duration > 0 && (
          <motion.div
            className="absolute top-0 left-0 h-0.5 bg-white/20"
            initial={{ width: '100%' }}
            animate={{ width: '0%' }}
            transition={{ duration: toast.duration / 1000, ease: 'linear' }}
          />
        )}

        <div className="p-3">
          {/* Header with jewel icons */}
          <div className="flex items-center gap-2 mb-1">
            {/* Source jewel */}
            <span className="text-lg" title={sourceInfo.name}>
              {sourceInfo.icon}
            </span>

            {/* Arrow to target */}
            {targetInfo && (
              <>
                <ArrowRight className="w-3 h-3 text-gray-500" />
                <span className="text-lg" title={targetInfo.name}>
                  {targetInfo.icon}
                </span>
              </>
            )}

            {/* Title */}
            <Toast.Title className="flex-1 text-sm font-medium text-white">
              {toast.title}
            </Toast.Title>

            {/* Close button */}
            <Toast.Close asChild>
              <button
                className="p-1 rounded hover:bg-white/10 transition-colors text-gray-400 hover:text-white"
                aria-label="Close"
              >
                <X className="w-3.5 h-3.5" />
              </button>
            </Toast.Close>
          </div>

          {/* Description */}
          {toast.description && (
            <Toast.Description className="text-xs text-gray-400 ml-7">
              {toast.description}
            </Toast.Description>
          )}

          {/* Action link */}
          {toast.action && (
            <Toast.Action asChild altText={toast.action.label}>
              <Link
                to={toast.action.href}
                className={`
                  inline-flex items-center gap-1 mt-2 ml-7
                  text-xs font-medium
                  ${sourceInfo.color}
                  hover:underline
                `}
              >
                {toast.action.label}
                <ArrowRight className="w-3 h-3" />
              </Link>
            </Toast.Action>
          )}
        </div>

        {/* Jewel color accent */}
        <div
          className={`absolute left-0 top-0 bottom-0 w-1 ${sourceInfo.bgColor.replace('/10', '/50')}`}
        />
      </motion.div>
    </Toast.Root>
  );
}

/**
 * SynergyToaster - Toast container component.
 *
 * Place this once at the root of your app to enable synergy toasts.
 * Toasts appear in the bottom-right corner.
 */
export function SynergyToaster() {
  const { toasts, removeToast } = useSynergyToastStore();

  return (
    <Toast.Provider swipeDirection="right" duration={5000}>
      <AnimatePresence mode="popLayout">
        {toasts.map((toast) => (
          <SynergyToastItem
            key={toast.id}
            toast={toast}
            onClose={() => removeToast(toast.id)}
          />
        ))}
      </AnimatePresence>

      <Toast.Viewport
        className={`
          fixed bottom-4 right-4 z-[100]
          flex flex-col-reverse gap-2
          w-auto max-w-[420px]
          outline-none
        `}
      />
    </Toast.Provider>
  );
}
