/**
 * BranchExplorer - Navigate the style evolution tree
 *
 * L4: Branch Visibility Law - All branches remain inspectable until collapsed.
 * L5: Iteration-Memory Law - Previous iterations preserved.
 * L2: Wildness Quarantine Law - Wild branches visible but quarantined.
 *
 * "The topology of exploration is preserved."
 */

import { useState, useMemo } from 'react';
import type { StyleBranch, Mutation } from '@kgents/shared-primitives';

interface BranchExplorerProps {
  branches: StyleBranch[];
  activeBranchId?: string;
  onSelectBranch: (branchId: string) => void;
  onSelectMutation: (mutation: Mutation) => void;
}

/**
 * Explore the style evolution branches.
 * L4: All branches visible, even collapsed ones.
 */
export function BranchExplorer({
  branches,
  activeBranchId,
  onSelectBranch,
  onSelectMutation,
}: BranchExplorerProps) {
  const [expandedBranches, setExpandedBranches] = useState<Set<string>>(
    new Set([activeBranchId || branches[0]?.id].filter(Boolean))
  );

  // Group branches by status
  const groupedBranches = useMemo(() => {
    const canonical = branches.filter((b) => b.status === 'canonical');
    const active = branches.filter((b) => b.status === 'active');
    const wild = branches.filter((b) => b.status === 'wild');
    const collapsed = branches.filter((b) => b.status === 'collapsed');

    return { canonical, active, wild, collapsed };
  }, [branches]);

  const toggleExpand = (branchId: string) => {
    setExpandedBranches((prev) => {
      const next = new Set(prev);
      if (next.has(branchId)) {
        next.delete(branchId);
      } else {
        next.add(branchId);
      }
      return next;
    });
  };

  const getBranchIcon = (status: StyleBranch['status'], isWild: boolean): string => {
    if (status === 'canonical') return '👑';
    if (status === 'wild' || isWild) return '🌀';
    if (status === 'collapsed') return '📦';
    return '🌿';
  };

  const getBranchColor = (status: StyleBranch['status'], isWild: boolean): string => {
    if (status === 'canonical') return 'text-amber-300 border-amber-500/30';
    if (status === 'wild' || isWild) return 'text-purple-300 border-purple-500/30';
    if (status === 'collapsed') return 'text-slate-400 border-slate-600';
    return 'text-green-300 border-green-500/30';
  };

  const renderBranch = (branch: StyleBranch) => {
    const isExpanded = expandedBranches.has(branch.id);
    const isActive = branch.id === activeBranchId;
    const colorClass = getBranchColor(branch.status, branch.is_wild);

    return (
      <div
        key={branch.id}
        className={`border rounded-lg overflow-hidden mb-2 ${colorClass} ${
          isActive ? 'ring-2 ring-amber-400' : ''
        }`}
      >
        {/* Branch header */}
        <div
          onClick={() => toggleExpand(branch.id)}
          className="flex items-center gap-2 p-3 cursor-pointer hover:bg-slate-700/50 transition-colors"
        >
          <span className="text-lg">{getBranchIcon(branch.status, branch.is_wild)}</span>

          <div className="flex-1 min-w-0">
            <div className="flex items-center gap-2">
              <span className="font-medium truncate">{branch.name}</span>
              {branch.is_wild && (
                <span className="text-xs bg-purple-500/20 px-1.5 py-0.5 rounded text-purple-300">
                  wild
                </span>
              )}
            </div>
            <div className="text-xs text-slate-500">
              {branch.mutations.length} mutations · Loss: {branch.average_loss.toFixed(2)}
            </div>
          </div>

          <button
            onClick={(e) => {
              e.stopPropagation();
              onSelectBranch(branch.id);
            }}
            className={`px-2 py-1 text-xs rounded transition-colors ${
              isActive
                ? 'bg-amber-500 text-slate-900'
                : 'bg-slate-600 hover:bg-slate-500 text-white'
            }`}
          >
            {isActive ? 'Active' : 'Switch'}
          </button>

          <span
            className={`transition-transform ${isExpanded ? 'rotate-180' : ''}`}
          >
            ▼
          </span>
        </div>

        {/* Mutation list (expanded) */}
        {isExpanded && branch.mutations.length > 0 && (
          <div className="border-t border-slate-700 bg-slate-800/50">
            {branch.mutations.map((mutation, index) => (
              <div
                key={mutation.id}
                onClick={() => onSelectMutation(mutation)}
                className="flex items-start gap-3 p-3 border-b border-slate-700/50 last:border-b-0 cursor-pointer hover:bg-slate-700/30 transition-colors"
              >
                {/* Timeline connector */}
                <div className="flex flex-col items-center pt-1">
                  <div
                    className={`w-2 h-2 rounded-full ${
                      mutation.status === 'accepted'
                        ? 'bg-green-400'
                        : mutation.status === 'rejected'
                        ? 'bg-red-400'
                        : 'bg-purple-400'
                    }`}
                  />
                  {index < branch.mutations.length - 1 && (
                    <div className="w-0.5 flex-1 bg-slate-600 mt-1" />
                  )}
                </div>

                {/* Mutation content */}
                <div className="flex-1 min-w-0">
                  <div className="text-sm text-slate-200 mb-1">
                    {mutation.change_description}
                  </div>

                  {mutation.rationale && (
                    <div className="text-xs text-slate-400 italic mb-1">
                      "{mutation.rationale.reason}"
                    </div>
                  )}

                  <div className="flex items-center gap-2 text-xs">
                    <span
                      className={`px-1.5 py-0.5 rounded ${
                        mutation.status === 'accepted'
                          ? 'bg-green-500/20 text-green-300'
                          : mutation.status === 'rejected'
                          ? 'bg-red-500/20 text-red-300'
                          : 'bg-purple-500/20 text-purple-300'
                      }`}
                    >
                      {mutation.status}
                    </span>
                    <span className="text-slate-500">
                      Loss: {mutation.galois_loss.toFixed(2)}
                    </span>
                  </div>
                </div>
              </div>
            ))}
          </div>
        )}

        {/* Empty state */}
        {isExpanded && branch.mutations.length === 0 && (
          <div className="p-4 text-center text-slate-500 text-sm">
            No mutations yet. This branch is waiting for exploration.
          </div>
        )}
      </div>
    );
  };

  return (
    <div className="bg-slate-800 rounded-xl p-4">
      <h3 className="text-lg font-bold text-amber-300 mb-4 flex items-center gap-2">
        <span>🌳</span> Style Branches
      </h3>

      {/* Canonical branches */}
      {groupedBranches.canonical.length > 0 && (
        <div className="mb-4">
          <div className="text-xs text-slate-500 mb-2 uppercase tracking-wide">
            Canon
          </div>
          {groupedBranches.canonical.map(renderBranch)}
        </div>
      )}

      {/* Active branches */}
      {groupedBranches.active.length > 0 && (
        <div className="mb-4">
          <div className="text-xs text-slate-500 mb-2 uppercase tracking-wide">
            Active Explorations
          </div>
          {groupedBranches.active.map(renderBranch)}
        </div>
      )}

      {/* Wild branches (L2: visible but quarantined) */}
      {groupedBranches.wild.length > 0 && (
        <div className="mb-4">
          <div className="text-xs text-purple-400 mb-2 uppercase tracking-wide flex items-center gap-2">
            <span>🌀</span> Wild Branches (quarantined)
          </div>
          {groupedBranches.wild.map(renderBranch)}
        </div>
      )}

      {/* Collapsed branches (L4: still inspectable) */}
      {groupedBranches.collapsed.length > 0 && (
        <div>
          <div className="text-xs text-slate-500 mb-2 uppercase tracking-wide">
            Archived
          </div>
          {groupedBranches.collapsed.map(renderBranch)}
        </div>
      )}

      {branches.length === 0 && (
        <div className="text-center text-slate-500 py-8">
          No branches yet. Create a character to start exploring!
        </div>
      )}
    </div>
  );
}

export default BranchExplorer;
