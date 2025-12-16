/**
 * ProjectionView: Tab-based view of CLI/HTML/JSON projections.
 */

import { useState } from 'react';
import type { PilotProjections } from '@/api/types';

type ProjectionTab = 'cli' | 'html' | 'json';

interface ProjectionViewProps {
  projections: PilotProjections;
  defaultTab?: ProjectionTab;
  compact?: boolean;
}

export function ProjectionView({ projections, defaultTab = 'cli', compact = false }: ProjectionViewProps) {
  const [activeTab, setActiveTab] = useState<ProjectionTab>(defaultTab);

  const tabClass = (tab: ProjectionTab) =>
    `px-2 py-1 text-xs font-medium rounded transition-colors ${
      activeTab === tab
        ? 'bg-town-accent/40 text-white'
        : 'text-gray-400 hover:text-gray-200 hover:bg-town-accent/20'
    }`;

  return (
    <div className="flex flex-col h-full">
      {/* Tabs */}
      <div className="flex gap-1 mb-2">
        <button onClick={() => setActiveTab('cli')} className={tabClass('cli')}>
          CLI
        </button>
        <button onClick={() => setActiveTab('html')} className={tabClass('html')}>
          HTML
        </button>
        <button onClick={() => setActiveTab('json')} className={tabClass('json')}>
          JSON
        </button>
      </div>

      {/* Content */}
      <div
        className={`flex-1 overflow-auto ${compact ? 'min-h-[60px]' : 'min-h-[100px]'}`}
      >
        {activeTab === 'cli' && <CliView content={projections.cli} />}
        {activeTab === 'html' && <HtmlView content={projections.html} />}
        {activeTab === 'json' && <JsonView content={projections.json} />}
      </div>
    </div>
  );
}

function CliView({ content }: { content: string }) {
  return (
    <pre className="font-mono text-sm bg-gray-900/80 rounded p-2 text-green-400 whitespace-pre-wrap break-all overflow-x-auto">
      {content}
    </pre>
  );
}

function HtmlView({ content }: { content: string }) {
  return (
    <div
      className="bg-gray-800/50 rounded p-2 text-sm kgents-projection"
      dangerouslySetInnerHTML={{ __html: content }}
    />
  );
}

function JsonView({ content }: { content: Record<string, unknown> }) {
  const [expanded, setExpanded] = useState(false);

  const jsonStr = JSON.stringify(content, null, expanded ? 2 : 0);
  const isLong = jsonStr.length > 100;

  return (
    <div className="relative">
      <pre className="font-mono text-xs bg-gray-900/80 rounded p-2 text-blue-300 whitespace-pre-wrap break-all overflow-x-auto">
        {expanded ? jsonStr : jsonStr.slice(0, 200) + (isLong ? '...' : '')}
      </pre>
      {isLong && (
        <button
          onClick={() => setExpanded(!expanded)}
          className="absolute top-1 right-1 text-xs text-gray-500 hover:text-gray-300"
        >
          {expanded ? '[-]' : '[+]'}
        </button>
      )}
    </div>
  );
}

export default ProjectionView;
