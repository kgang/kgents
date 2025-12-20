/**
 * ToolsSection - Tools shortcuts in navigation tree
 *
 * Provides quick access to AGENTESE tool paths.
 *
 * @see NavigationTree.tsx
 */

import { GitBranch, type LucideIcon } from 'lucide-react';

// =============================================================================
// Types
// =============================================================================

interface Tool {
  path: string;
  label: string;
  icon: LucideIcon;
}

export interface ToolsSectionProps {
  currentPath: string;
  onNavigate: (path: string) => void;
}

// =============================================================================
// Constants
// =============================================================================

const TOOLS: Tool[] = [{ path: 'time.differance', label: 'Diff\u00e9rance', icon: GitBranch }];

// =============================================================================
// Component
// =============================================================================

export function ToolsSection({ currentPath, onNavigate }: ToolsSectionProps) {
  return (
    <div className="border-t border-gray-700/50 pt-3">
      <h3 className="px-3 mb-2 text-xs font-medium text-gray-500 uppercase tracking-wider">
        Tools
      </h3>
      <div className="space-y-0.5">
        {TOOLS.map((tool) => {
          const isActive = currentPath === tool.path || currentPath.startsWith(`${tool.path}.`);
          const Icon = tool.icon;
          return (
            <button
              key={tool.path}
              onClick={() => onNavigate(tool.path)}
              className={`
                w-full flex items-center gap-2 px-3 py-1.5 text-sm
                hover:bg-gray-700/50 transition-colors rounded-md
                ${isActive ? 'bg-gray-700/70 text-white' : 'text-gray-300'}
              `}
            >
              <Icon className="w-4 h-4 text-amber-400" />
              <span>{tool.label}</span>
              <span className="ml-auto text-xs text-gray-500 font-mono">{tool.path}</span>
            </button>
          );
        })}
      </div>
    </div>
  );
}

export default ToolsSection;
