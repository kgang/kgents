/**
 * LoadingPanel: Gentle loading state for the Forge.
 *
 * Features:
 * - Animated indicator
 * - Optional message
 * - Whimsical styling
 *
 * Theme: Orisinal.com aesthetic - calm, anticipatory.
 */

interface LoadingPanelProps {
  /** Loading message */
  message?: string;
}

export function LoadingPanel({ message = 'Loading...' }: LoadingPanelProps) {
  return (
    <div className="flex flex-col items-center justify-center py-16 text-center">
      {/* Animated dots */}
      <div className="flex gap-1 mb-4">
        <span
          className="w-2 h-2 rounded-full bg-amber-300 animate-bounce"
          style={{ animationDelay: '0ms' }}
        />
        <span
          className="w-2 h-2 rounded-full bg-amber-300 animate-bounce"
          style={{ animationDelay: '150ms' }}
        />
        <span
          className="w-2 h-2 rounded-full bg-amber-300 animate-bounce"
          style={{ animationDelay: '300ms' }}
        />
      </div>

      {/* Message */}
      <p className="text-sm text-stone-400 italic">{message}</p>
    </div>
  );
}

export default LoadingPanel;
