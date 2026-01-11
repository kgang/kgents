/**
 * DecisionTimeline - Enhanced decision history viewer
 *
 * Features:
 * - All kg decide decisions
 * - Grouped by topic or date
 * - Shows: topic, synthesis, reasoning
 * - Links to related files and witness marks
 * - Search and filter
 *
 * STARK BIOME aesthetic: 90% steel, 10% earned glow.
 */

import { memo, useState, useMemo } from 'react';
import {
  GitBranch,
  Search,
  Tag,
  FileText,
  Bookmark,
  ChevronDown,
  ChevronRight,
  User,
  Bot,
  ArrowRight,
} from 'lucide-react';
import type { Decision } from './types';

// =============================================================================
// Types
// =============================================================================

export interface DecisionTimelineProps {
  decisions?: Decision[];
  onDecisionSelect: (id: string) => void;
  selectedDecision?: string | null;
  onNavigateToFile?: (path: string) => void;
  onNavigateToMark?: (markId: string) => void;
}

// =============================================================================
// Mock Data
// =============================================================================

const MOCK_DECISIONS: Decision[] = [
  {
    id: 'dec-1',
    timestamp: '2025-12-21T14:30:00Z',
    topic: 'Post-Extinction Architecture',
    synthesis: 'Remove Gestalt, Park, Emergence; focus on Brain, Town, Witness',
    kentView: 'Keep everything for flexibility',
    kentReasoning: 'More options means more power for different use cases',
    claudeView: 'Prune ruthlessly for clarity',
    claudeReasoning: 'Unused code is cognitive debt; clarity > optionality',
    relatedFiles: ['spec/architecture.md', 'impl/claude/services/'],
    relatedMarks: ['mark-abc', 'mark-def'],
    tags: ['architecture', 'extinction'],
  },
  {
    id: 'dec-2',
    timestamp: '2025-12-20T16:45:00Z',
    topic: 'AGENTESE Path Structure',
    synthesis: 'Use dots for context, slashes only for file paths',
    kentView: 'Consistent dot notation',
    kentReasoning: 'Dots are more natural for semantic paths',
    claudeView: 'Agreed - dots are cleaner',
    claudeReasoning: 'Dots separate concerns; slashes imply filesystem',
    relatedFiles: ['spec/protocols/agentese.md'],
    tags: ['agentese', 'protocol'],
  },
  {
    id: 'dec-3',
    timestamp: '2025-12-19T11:00:00Z',
    topic: 'DI Container Pattern',
    synthesis: 'Fail-fast at import time for required dependencies',
    kentView: 'Graceful fallbacks',
    kentReasoning: 'Partial functionality better than no functionality',
    claudeView: 'Strict validation catches bugs earlier',
    claudeReasoning: 'Silent failures are debugging nightmares',
    relatedFiles: ['impl/claude/services/providers.py', 'spec/infrastructure/di.md'],
    relatedMarks: ['mark-ghi'],
    tags: ['infrastructure', 'di'],
  },
  {
    id: 'dec-4',
    timestamp: '2025-12-18T09:15:00Z',
    topic: 'Witness Evidence Ladder',
    synthesis: 'Implement L-inf to L3 ladder with Bayesian confidence computation',
    kentView: 'Simple binary witnessed/not',
    kentReasoning: 'Easy to understand and implement',
    claudeView: 'Graded confidence reflects reality better',
    claudeReasoning: 'Different evidence types have different weights',
    relatedFiles: ['spec/protocols/witness.md'],
    tags: ['witness', 'evidence'],
  },
  {
    id: 'dec-5',
    timestamp: '2025-12-17T14:00:00Z',
    topic: 'Storage Backend',
    synthesis: 'Default to PostgreSQL with SQLAlchemy; SQLite for local dev only',
    kentView: 'SQLite for simplicity',
    kentReasoning: 'No external dependencies, zero config',
    claudeView: 'PostgreSQL for production readiness',
    claudeReasoning: 'Concurrent access, better performance, production parity',
    relatedFiles: ['spec/protocols/storage-migration.md'],
    tags: ['storage', 'infrastructure'],
  },
];

// =============================================================================
// Subcomponents
// =============================================================================

interface DecisionCardProps {
  decision: Decision;
  isSelected: boolean;
  isExpanded: boolean;
  onSelect: () => void;
  onToggleExpand: () => void;
  onNavigateToFile?: (path: string) => void;
  onNavigateToMark?: (markId: string) => void;
}

const DecisionCard = memo(function DecisionCard({
  decision,
  isSelected,
  isExpanded,
  onSelect,
  onToggleExpand,
  onNavigateToFile,
  onNavigateToMark,
}: DecisionCardProps) {
  const formatDate = (dateStr: string) => {
    const date = new Date(dateStr);
    return date.toLocaleDateString('en-US', {
      month: 'short',
      day: 'numeric',
      year: 'numeric',
    });
  };

  const formatTime = (dateStr: string) => {
    const date = new Date(dateStr);
    return date.toLocaleTimeString('en-US', {
      hour: '2-digit',
      minute: '2-digit',
    });
  };

  return (
    <div className="decision-timeline__card-wrapper">
      <button className="decision-timeline__card" data-selected={isSelected} onClick={onSelect}>
        {/* Header */}
        <div className="decision-timeline__card-header">
          <span className="decision-timeline__card-date">{formatDate(decision.timestamp)}</span>
          <span className="decision-timeline__card-time">{formatTime(decision.timestamp)}</span>
        </div>

        {/* Topic */}
        <div className="decision-timeline__card-topic">{decision.topic}</div>

        {/* Synthesis */}
        <div className="decision-timeline__card-synthesis">
          <ArrowRight size={10} className="decision-timeline__synthesis-icon" />
          {decision.synthesis}
        </div>

        {/* Tags */}
        {decision.tags && decision.tags.length > 0 && (
          <div className="decision-timeline__card-tags">
            {decision.tags.map((tag) => (
              <span key={tag} className="decision-timeline__tag">
                <Tag size={8} />
                {tag}
              </span>
            ))}
          </div>
        )}

        {/* Expand button */}
        <button
          className="decision-timeline__expand-btn"
          onClick={(e) => {
            e.stopPropagation();
            onToggleExpand();
          }}
          aria-label={isExpanded ? 'Collapse' : 'Expand'}
        >
          {isExpanded ? <ChevronDown size={12} /> : <ChevronRight size={12} />}
        </button>
      </button>

      {/* Expanded content */}
      {isExpanded && (
        <div className="decision-timeline__details">
          {/* Dialectic */}
          <div className="decision-timeline__dialectic">
            {/* Kent's view */}
            {decision.kentView && (
              <div className="decision-timeline__view decision-timeline__view--kent">
                <div className="decision-timeline__view-header">
                  <User size={12} />
                  <span>Kent</span>
                </div>
                <div className="decision-timeline__view-position">{decision.kentView}</div>
                {decision.kentReasoning && (
                  <div className="decision-timeline__view-reasoning">{decision.kentReasoning}</div>
                )}
              </div>
            )}

            {/* Claude's view */}
            {decision.claudeView && (
              <div className="decision-timeline__view decision-timeline__view--claude">
                <div className="decision-timeline__view-header">
                  <Bot size={12} />
                  <span>Claude</span>
                </div>
                <div className="decision-timeline__view-position">{decision.claudeView}</div>
                {decision.claudeReasoning && (
                  <div className="decision-timeline__view-reasoning">
                    {decision.claudeReasoning}
                  </div>
                )}
              </div>
            )}
          </div>

          {/* Related files */}
          {decision.relatedFiles && decision.relatedFiles.length > 0 && (
            <div className="decision-timeline__related">
              <span className="decision-timeline__related-label">
                <FileText size={10} />
                Related Files
              </span>
              <div className="decision-timeline__related-items">
                {decision.relatedFiles.map((path) => (
                  <button
                    key={path}
                    className="decision-timeline__related-item"
                    onClick={() => onNavigateToFile?.(path)}
                  >
                    {path}
                  </button>
                ))}
              </div>
            </div>
          )}

          {/* Related marks */}
          {decision.relatedMarks && decision.relatedMarks.length > 0 && (
            <div className="decision-timeline__related">
              <span className="decision-timeline__related-label">
                <Bookmark size={10} />
                Witness Marks
              </span>
              <div className="decision-timeline__related-items">
                {decision.relatedMarks.map((markId) => (
                  <button
                    key={markId}
                    className="decision-timeline__related-item"
                    onClick={() => onNavigateToMark?.(markId)}
                  >
                    {markId}
                  </button>
                ))}
              </div>
            </div>
          )}
        </div>
      )}
    </div>
  );
});

// =============================================================================
// Main Component
// =============================================================================

export const DecisionTimeline = memo(function DecisionTimeline({
  decisions = MOCK_DECISIONS,
  onDecisionSelect,
  selectedDecision,
  onNavigateToFile,
  onNavigateToMark,
}: DecisionTimelineProps) {
  const [searchQuery, setSearchQuery] = useState('');
  const [expandedDecisions, setExpandedDecisions] = useState<Set<string>>(new Set());
  const [tagFilter, setTagFilter] = useState<string | null>(null);

  // Get all unique tags
  const allTags = useMemo(() => {
    const tags = new Set<string>();
    decisions.forEach((d) => d.tags?.forEach((t) => tags.add(t)));
    return Array.from(tags).sort();
  }, [decisions]);

  // Filter decisions
  const filteredDecisions = useMemo(() => {
    let result = decisions;

    if (searchQuery) {
      const query = searchQuery.toLowerCase();
      result = result.filter(
        (d) =>
          d.topic.toLowerCase().includes(query) ||
          d.synthesis.toLowerCase().includes(query) ||
          d.tags?.some((t) => t.toLowerCase().includes(query))
      );
    }

    if (tagFilter) {
      result = result.filter((d) => d.tags?.includes(tagFilter));
    }

    return result;
  }, [decisions, searchQuery, tagFilter]);

  // Toggle decision expansion
  const toggleExpand = (id: string) => {
    setExpandedDecisions((prev) => {
      const next = new Set(prev);
      if (next.has(id)) {
        next.delete(id);
      } else {
        next.add(id);
      }
      return next;
    });
  };

  return (
    <div className="decision-timeline">
      {/* Header */}
      <div className="decision-timeline__header">
        <GitBranch size={14} className="decision-timeline__icon" />
        <span className="decision-timeline__title">Decisions</span>
        <span className="decision-timeline__count">{filteredDecisions.length}</span>
      </div>

      {/* Search */}
      <div className="decision-timeline__search">
        <Search size={12} className="decision-timeline__search-icon" />
        <input
          type="text"
          className="decision-timeline__search-input"
          placeholder="Search decisions..."
          value={searchQuery}
          onChange={(e) => setSearchQuery(e.target.value)}
        />
      </div>

      {/* Tag filter */}
      {allTags.length > 0 && (
        <div className="decision-timeline__tag-filter">
          <button
            className={`decision-timeline__tag-btn ${!tagFilter ? 'active' : ''}`}
            onClick={() => setTagFilter(null)}
          >
            All
          </button>
          {allTags.map((tag) => (
            <button
              key={tag}
              className={`decision-timeline__tag-btn ${tagFilter === tag ? 'active' : ''}`}
              onClick={() => setTagFilter(tag === tagFilter ? null : tag)}
            >
              {tag}
            </button>
          ))}
        </div>
      )}

      {/* Decision list */}
      <div className="decision-timeline__list">
        {filteredDecisions.length === 0 ? (
          <div className="decision-timeline__empty">
            {searchQuery ? `No decisions matching "${searchQuery}"` : 'No decisions'}
          </div>
        ) : (
          filteredDecisions.map((decision) => (
            <DecisionCard
              key={decision.id}
              decision={decision}
              isSelected={decision.id === selectedDecision}
              isExpanded={expandedDecisions.has(decision.id)}
              onSelect={() => onDecisionSelect(decision.id)}
              onToggleExpand={() => toggleExpand(decision.id)}
              onNavigateToFile={onNavigateToFile}
              onNavigateToMark={onNavigateToMark}
            />
          ))
        )}
      </div>
    </div>
  );
});

export default DecisionTimeline;
