/**
 * NotFound: 404 page.
 *
 * Displayed when user navigates to a non-existent route.
 * Neutral tone — clear and direct.
 *
 * @see spec/protocols/agentese-as-route.md
 */

import { Link } from 'react-router-dom';
import { MapPin } from 'lucide-react';

/**
 * 404 Not Found page.
 *
 * Neutral messaging with helpful navigation options.
 */
export default function NotFound() {
  return (
    <div className="h-[calc(100vh-64px)] flex items-center justify-center bg-town-bg">
      <div className="text-center max-w-md px-4">
        {/* Icon - Lucide, not emoji */}
        <div className="flex justify-center mb-6">
          <MapPin className="w-16 h-16 text-gray-500" strokeWidth={1.5} />
        </div>

        {/* Title - neutral */}
        <h1 className="text-3xl font-bold mb-3 text-white">Page Not Found</h1>

        {/* Description - actionable */}
        <p className="text-gray-400 mb-8 text-lg">
          This page does not exist. Check the URL or navigate home.
        </p>

        {/* Navigation options */}
        <div className="flex flex-col sm:flex-row gap-4 justify-center">
          <Link
            to="/"
            className="px-6 py-3 bg-town-highlight hover:bg-town-highlight/80 rounded-lg font-medium transition-colors text-white"
          >
            Go Home
          </Link>
          <Link
            to="/concept.cockpit"
            className="px-6 py-3 bg-town-accent/50 hover:bg-town-accent/70 rounded-lg font-medium transition-colors text-gray-200"
          >
            Open Cockpit
          </Link>
        </div>

        {/* Error code */}
        <p className="text-gray-600 text-sm mt-8">404</p>
      </div>
    </div>
  );
}
