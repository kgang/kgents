/**
 * PersonalConstitutionBuilder - Main component for axiom discovery and constitution building.
 *
 * Design Goals:
 * - Kent sees, accepts, rejects, and evolves his personal axioms
 * - Axioms should feel discovered, not imposed
 * - Evidence-based UI (show why, not just what)
 * - Contradiction handling feels like opportunity, not problem
 *
 * Four Sections:
 * 1. Axiom Discovery - Trigger pipeline, see progress
 * 2. Axiom Review - Review candidates, accept/reject/edit
 * 3. Constitution View - Accepted axioms organized by layer
 * 4. Contradiction Detection - Show conflicts, suggest synthesis
 *
 * Philosophy:
 *   "The persona is a garden, not a museum."
 *   "Kent discovers his personal axioms. He didn't write them; he *discovered* them."
 *
 * @see stores/personalConstitutionStore.ts
 * @see services/zero_seed/axiom_discovery_pipeline.py
 */

import { useState, useCallback, useEffect } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { usePersonalConstitutionStore } from '@/stores/personalConstitutionStore';
import type { AxiomCandidate, ConstitutionalAxiom, AxiomLayer } from './types';
import { getLayerLabel, getLayerDescription } from './types';
import { AxiomCard } from './AxiomCard';
import { DiscoveryProgress } from './DiscoveryProgress';
import { ContradictionAlert } from './ContradictionAlert';
import { ConstitutionExport } from './ConstitutionExport';
import { TIMING } from '@/constants';
import './PersonalConstitutionBuilder.css';

// =============================================================================
// Types
// =============================================================================

export interface PersonalConstitutionBuilderProps {
  /** Custom className */
  className?: string;
}

type Section = 'discover' | 'review' | 'constitution' | 'contradictions';

// =============================================================================
// Sub-components
// =============================================================================

interface SectionTabsProps {
  active: Section;
  onChange: (section: Section) => void;
  pendingCount: number;
  contradictionCount: number;
  totalAxioms: number;
}

function SectionTabs({
  active,
  onChange,
  pendingCount,
  contradictionCount,
  totalAxioms,
}: SectionTabsProps) {
  const tabs: { id: Section; label: string; badge?: number }[] = [
    { id: 'discover', label: 'Discover' },
    { id: 'review', label: 'Review', badge: pendingCount },
    { id: 'constitution', label: 'Constitution', badge: totalAxioms },
    { id: 'contradictions', label: 'Tensions', badge: contradictionCount },
  ];

  return (
    <nav className="section-tabs">
      {tabs.map((tab) => (
        <button
          key={tab.id}
          className={`section-tab ${active === tab.id ? 'active' : ''}`}
          onClick={() => onChange(tab.id)}
        >
          <span className="tab-label">{tab.label}</span>
          {tab.badge !== undefined && tab.badge > 0 && (
            <span className="tab-badge">{tab.badge}</span>
          )}
        </button>
      ))}
    </nav>
  );
}

interface LayerSectionProps {
  layer: AxiomLayer;
  axioms: ConstitutionalAxiom[];
  onEdit: (axiom: AxiomCandidate | ConstitutionalAxiom) => void;
  onRemove: (axiom: ConstitutionalAxiom) => void;
}

function LayerSection({ layer, axioms, onEdit, onRemove }: LayerSectionProps) {
  if (axioms.length === 0) return null;

  return (
    <section className={`layer-section layer-${layer.toLowerCase()}`}>
      <header className="layer-header">
        <h3 className="layer-title">
          {layer} - {getLayerLabel(layer)}s
        </h3>
        <p className="layer-description">{getLayerDescription(layer)}</p>
      </header>
      <div className="layer-axioms">
        {axioms.map((axiom, index) => (
          <AxiomCard
            key={axiom.id}
            axiom={axiom}
            variant="constitutional"
            onEdit={onEdit}
            onRemove={onRemove}
            index={index}
          />
        ))}
      </div>
    </section>
  );
}

interface EditDialogProps {
  axiom: AxiomCandidate | ConstitutionalAxiom | null;
  isOpen: boolean;
  onClose: () => void;
  onSave: (content: string, notes?: string) => void;
}

function EditDialog({ axiom, isOpen, onClose, onSave }: EditDialogProps) {
  const [content, setContent] = useState('');
  const [notes, setNotes] = useState('');

  useEffect(() => {
    if (axiom) {
      const initial =
        'editedContent' in axiom && axiom.editedContent ? axiom.editedContent : axiom.content;
      setContent(initial);
      setNotes('notes' in axiom && axiom.notes ? axiom.notes : '');
    }
  }, [axiom]);

  const handleSave = useCallback(() => {
    onSave(content, notes || undefined);
    onClose();
  }, [content, notes, onSave, onClose]);

  if (!isOpen || !axiom) return null;

  return (
    <>
      <motion.div
        className="edit-backdrop"
        initial={{ opacity: 0 }}
        animate={{ opacity: 1 }}
        exit={{ opacity: 0 }}
        onClick={onClose}
      />
      <motion.div
        className="edit-dialog"
        initial={{ opacity: 0, scale: 0.95, y: 20 }}
        animate={{ opacity: 1, scale: 1, y: 0 }}
        exit={{ opacity: 0, scale: 0.95, y: 20 }}
      >
        <header className="edit-header">
          <h3>Edit Axiom</h3>
          <p className="edit-hint">Reword while preserving the core insight</p>
        </header>

        <div className="edit-form">
          <div className="edit-field">
            <label htmlFor="axiom-content">Axiom</label>
            <textarea
              id="axiom-content"
              value={content}
              onChange={(e) => setContent(e.target.value)}
              rows={3}
              placeholder="Your axiom..."
            />
          </div>

          <div className="edit-field">
            <label htmlFor="axiom-notes">Notes (optional)</label>
            <textarea
              id="axiom-notes"
              value={notes}
              onChange={(e) => setNotes(e.target.value)}
              rows={2}
              placeholder="Why this matters to you..."
            />
          </div>

          <div className="edit-original">
            <span className="original-label">Original:</span>
            <span className="original-text">{axiom.content}</span>
          </div>
        </div>

        <footer className="edit-actions">
          <button className="action-btn secondary" onClick={onClose}>
            Cancel
          </button>
          <button className="action-btn primary" onClick={handleSave} disabled={!content.trim()}>
            Save
          </button>
        </footer>
      </motion.div>
    </>
  );
}

// =============================================================================
// Main Component
// =============================================================================

export function PersonalConstitutionBuilder({ className = '' }: PersonalConstitutionBuilderProps) {
  // Store state
  const {
    isDiscovering,
    discoveryProgress,
    discoveryError,
    pendingCandidates,
    constitution,
    activeSection,
    startDiscovery,
    setActiveSection,
    acceptCandidate,
    rejectCandidate,
    editAndAccept,
    removeAxiom,
    updateAxiom,
    checkContradictions,
    exportConstitution,
    getTotalAxiomCount,
  } = usePersonalConstitutionStore();

  // Local state
  const [days, setDays] = useState(30);
  const [exportOpen, setExportOpen] = useState(false);
  const [editingAxiom, setEditingAxiom] = useState<AxiomCandidate | ConstitutionalAxiom | null>(
    null
  );
  const [expandedContradictions, setExpandedContradictions] = useState<Set<number>>(new Set());

  // Derived state
  const totalAxioms = getTotalAxiomCount();
  const contradictionCount = constitution.contradictions.length;

  // Check for contradictions when constitution changes
  useEffect(() => {
    if (totalAxioms >= 2) {
      checkContradictions();
    }
  }, [totalAxioms, checkContradictions]);

  // Handlers
  const handleDiscover = useCallback(() => {
    startDiscovery(days, 10);
  }, [days, startDiscovery]);

  const handleAccept = useCallback(
    (candidate: AxiomCandidate) => {
      acceptCandidate(candidate);
    },
    [acceptCandidate]
  );

  const handleReject = useCallback(
    (candidate: AxiomCandidate) => {
      rejectCandidate(candidate);
    },
    [rejectCandidate]
  );

  const handleEdit = useCallback((axiom: AxiomCandidate | ConstitutionalAxiom) => {
    setEditingAxiom(axiom);
  }, []);

  const handleSaveEdit = useCallback(
    (content: string, notes?: string) => {
      if (!editingAxiom) return;

      if ('status' in editingAxiom) {
        // Editing existing constitutional axiom
        updateAxiom(editingAxiom.id, {
          editedContent: content,
          notes,
          status: 'edited',
        });
      } else {
        // Editing candidate before accepting
        editAndAccept(editingAxiom, content, notes);
      }
      setEditingAxiom(null);
    },
    [editingAxiom, updateAxiom, editAndAccept]
  );

  const handleRemove = useCallback(
    (axiom: ConstitutionalAxiom) => {
      // eslint-disable-next-line no-alert
      if (
        window.confirm(`Remove "${axiom.editedContent || axiom.content}" from your constitution?`)
      ) {
        removeAxiom(axiom.id);
      }
    },
    [removeAxiom]
  );

  const handleToggleContradiction = useCallback((index: number) => {
    setExpandedContradictions((prev) => {
      const next = new Set(prev);
      if (next.has(index)) {
        next.delete(index);
      } else {
        next.add(index);
      }
      return next;
    });
  }, []);

  // Render section content
  const renderSection = () => {
    switch (activeSection) {
      case 'discover':
        return (
          <div className="section-content discover-section">
            <div className="discover-intro">
              <h2 className="intro-title">Discover Your Axioms</h2>
              <p className="intro-text">
                Analyze your recent decisions to uncover the principles you never violate. These are
                your L0 axioms - the fixed points of your decision landscape.
              </p>
              <p className="intro-quote">
                "You've made decisions this month. Here are the principles you never violated - your
                L0 axioms." He didn't write them; he <em>discovered</em> them.
              </p>
            </div>

            <div className="discover-config">
              <label className="config-label">
                <span>Analyze decisions from the past</span>
                <div className="config-input">
                  <input
                    type="number"
                    value={days}
                    onChange={(e) => setDays(Math.max(1, parseInt(e.target.value, 10) || 30))}
                    min={1}
                    max={365}
                  />
                  <span>days</span>
                </div>
              </label>
            </div>

            {isDiscovering || discoveryProgress ? (
              <DiscoveryProgress
                progress={discoveryProgress}
                isDiscovering={isDiscovering}
                error={discoveryError}
                onRetry={handleDiscover}
              />
            ) : (
              <button className="discover-btn" onClick={handleDiscover} disabled={isDiscovering}>
                <span className="btn-icon">
                  <svg width="20" height="20" viewBox="0 0 20 20" fill="none">
                    <circle cx="10" cy="10" r="7" stroke="currentColor" strokeWidth="1.5" />
                    <path
                      d="M10 6v4l3 3"
                      stroke="currentColor"
                      strokeWidth="1.5"
                      strokeLinecap="round"
                    />
                  </svg>
                </span>
                Begin Discovery
              </button>
            )}
          </div>
        );

      case 'review':
        return (
          <div className="section-content review-section">
            {pendingCandidates.length === 0 ? (
              <div className="empty-state">
                <p className="empty-title">No candidates to review</p>
                <p className="empty-text">
                  Run a discovery to find axiom candidates from your decisions.
                </p>
                <button className="action-btn primary" onClick={() => setActiveSection('discover')}>
                  Go to Discover
                </button>
              </div>
            ) : (
              <>
                <div className="review-header">
                  <h2>Review Candidates</h2>
                  <p className="review-subtitle">
                    {pendingCandidates.length} pattern{pendingCandidates.length !== 1 ? 's' : ''}{' '}
                    found. Accept the ones that resonate with you.
                  </p>
                </div>
                <div className="candidates-grid">
                  {pendingCandidates.map((candidate, index) => (
                    <AxiomCard
                      key={`${candidate.content}-${index}`}
                      axiom={candidate}
                      variant="candidate"
                      onAccept={handleAccept}
                      onReject={handleReject}
                      onEdit={handleEdit}
                      index={index}
                    />
                  ))}
                </div>
              </>
            )}
          </div>
        );

      case 'constitution':
        return (
          <div className="section-content constitution-section">
            {totalAxioms === 0 ? (
              <div className="empty-state">
                <p className="empty-title">Your constitution is empty</p>
                <p className="empty-text">
                  Accept axiom candidates to build your personal constitution.
                </p>
                <button className="action-btn primary" onClick={() => setActiveSection('review')}>
                  Review Candidates
                </button>
              </div>
            ) : (
              <>
                <header className="constitution-header">
                  <div className="constitution-info">
                    <h2>My Personal Constitution</h2>
                    <p className="constitution-meta">
                      Last updated: {new Date(constitution.lastUpdated).toLocaleDateString()}
                      {' | '}
                      {constitution.discoveryCount} discovery session
                      {constitution.discoveryCount !== 1 ? 's' : ''}
                    </p>
                  </div>
                  <button className="export-btn" onClick={() => setExportOpen(true)}>
                    <svg width="16" height="16" viewBox="0 0 16 16" fill="none">
                      <path
                        d="M8 2v8M4 6l4 4 4-4M2 12v2h12v-2"
                        stroke="currentColor"
                        strokeWidth="1.5"
                        strokeLinecap="round"
                        strokeLinejoin="round"
                      />
                    </svg>
                    Export
                  </button>
                </header>

                <LayerSection
                  layer="L0"
                  axioms={constitution.axioms}
                  onEdit={handleEdit}
                  onRemove={handleRemove}
                />
                <LayerSection
                  layer="L1"
                  axioms={constitution.values}
                  onEdit={handleEdit}
                  onRemove={handleRemove}
                />
                <LayerSection
                  layer="L2"
                  axioms={constitution.goals}
                  onEdit={handleEdit}
                  onRemove={handleRemove}
                />
              </>
            )}
          </div>
        );

      case 'contradictions':
        return (
          <div className="section-content contradictions-section">
            {constitution.contradictions.length === 0 ? (
              <div className="empty-state success">
                <p className="empty-title">No contradictions detected</p>
                <p className="empty-text">
                  Your axioms are internally consistent. Continue building!
                </p>
              </div>
            ) : (
              <>
                <div className="contradictions-header">
                  <h2>Tensions in Your Constitution</h2>
                  <p className="contradictions-subtitle">
                    These axiom pairs have conflicting implications. Consider them as opportunities
                    for deeper understanding.
                  </p>
                </div>
                <div className="contradictions-list">
                  {constitution.contradictions.map((contradiction, index) => (
                    <ContradictionAlert
                      key={`${contradiction.axiomA}-${contradiction.axiomB}`}
                      contradiction={contradiction}
                      isExpanded={expandedContradictions.has(index)}
                      onExpandedChange={() => handleToggleContradiction(index)}
                      index={index}
                    />
                  ))}
                </div>
              </>
            )}
          </div>
        );
    }
  };

  return (
    <div className={`personal-constitution-builder ${className}`}>
      {/* Header */}
      <header className="builder-header">
        <h1 className="builder-title">Personal Constitution</h1>
        <p className="builder-subtitle">Discover the principles you live by</p>
      </header>

      {/* Navigation */}
      <SectionTabs
        active={activeSection}
        onChange={setActiveSection}
        pendingCount={pendingCandidates.length}
        contradictionCount={contradictionCount}
        totalAxioms={totalAxioms}
      />

      {/* Content */}
      <AnimatePresence mode="wait">
        <motion.main
          key={activeSection}
          className="builder-main"
          initial={{ opacity: 0, y: 10 }}
          animate={{ opacity: 1, y: 0 }}
          exit={{ opacity: 0, y: -10 }}
          transition={{ duration: TIMING.quick / 1000 }}
        >
          {renderSection()}
        </motion.main>
      </AnimatePresence>

      {/* Export Dialog */}
      <ConstitutionExport
        constitution={constitution}
        isOpen={exportOpen}
        onClose={() => setExportOpen(false)}
        onExport={exportConstitution}
      />

      {/* Edit Dialog */}
      <AnimatePresence>
        {editingAxiom && (
          <EditDialog
            axiom={editingAxiom}
            isOpen={!!editingAxiom}
            onClose={() => setEditingAxiom(null)}
            onSave={handleSaveEdit}
          />
        )}
      </AnimatePresence>
    </div>
  );
}

export default PersonalConstitutionBuilder;
