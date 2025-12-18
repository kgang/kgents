/**
 * ErrorPanel: Friendly error display for the Forge.
 *
 * Features:
 * - Clear error messaging
 * - Optional retry action
 * - Whimsical styling
 *
 * Theme: Orisinal.com aesthetic - gentle, not alarming.
 */

interface ErrorPanelProps {
  /** Error title */
  title?: string;
  /** Error message/details */
  message: string;
  /** Retry callback */
  onRetry?: () => void;
  /** Additional help text */
  helpText?: string;
}

export function ErrorPanel({
  title = 'Something went awry',
  message,
  onRetry,
  helpText,
}: ErrorPanelProps) {
  return (
    <div className="flex flex-col items-center justify-center py-12 text-center">
      {/* Icon */}
      <div className="w-16 h-16 rounded-full bg-rose-50 flex items-center justify-center mb-4">
        <span className="text-2xl text-rose-300">~</span>
      </div>

      {/* Title */}
      <h3 className="text-lg font-medium text-stone-700 mb-2">{title}</h3>

      {/* Message */}
      <p className="text-sm text-stone-500 max-w-md mb-4">{message}</p>

      {/* Help text */}
      {helpText && <p className="text-xs text-stone-400 mb-4 max-w-md">{helpText}</p>}

      {/* Retry button */}
      {onRetry && (
        <button
          onClick={onRetry}
          className="px-4 py-2 rounded-lg bg-stone-100 text-stone-600 text-sm hover:bg-stone-200 transition-colors"
        >
          Try again
        </button>
      )}
    </div>
  );
}

export default ErrorPanel;
