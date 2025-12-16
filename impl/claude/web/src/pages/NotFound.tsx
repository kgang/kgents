/**
 * NotFound: 404 page with town theme.
 *
 * Displayed when user navigates to a non-existent route.
 * Keeps the personality of Agent Town with friendly messaging.
 *
 * @see plans/web-refactor/defensive-lifecycle.md
 */

import { Link } from 'react-router-dom';

/**
 * 404 Not Found page.
 *
 * Provides helpful navigation options with town-themed personality.
 */
export default function NotFound() {
  return (
    <div className="h-[calc(100vh-64px)] flex items-center justify-center bg-town-bg">
      <div className="text-center max-w-md px-4">
        {/* Icon */}
        <div className="text-8xl mb-6">🏚️</div>

        {/* Title */}
        <h1 className="text-3xl font-bold mb-3 text-white">Lost in the Wilderness</h1>

        {/* Description */}
        <p className="text-gray-400 mb-8 text-lg">
          This path leads nowhere. The town you seek lies elsewhere.
        </p>

        {/* Navigation options */}
        <div className="flex flex-col sm:flex-row gap-4 justify-center">
          <Link
            to="/"
            className="px-6 py-3 bg-town-highlight hover:bg-town-highlight/80 rounded-lg font-medium transition-colors text-white"
          >
            Return Home
          </Link>
          <Link
            to="/town/demo"
            className="px-6 py-3 bg-town-accent/50 hover:bg-town-accent/70 rounded-lg font-medium transition-colors text-gray-200"
          >
            Visit Demo Town
          </Link>
        </div>

        {/* Subtle hint */}
        <p className="text-gray-600 text-sm mt-8">
          Error 404 — Page not found
        </p>
      </div>
    </div>
  );
}
