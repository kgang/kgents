import { useCallback, useState } from 'react';
import type { DialecticDecision } from './types/dialectic';

interface UseEditorPanelsReturn {
  // Command line
  commandLineVisible: boolean;
  setCommandLineVisible: (visible: boolean) => void;

  // Help
  helpVisible: boolean;
  setHelpVisible: (visible: boolean) => void;
  toggleHelp: () => void;

  // Confidence breakdown
  confidenceVisible: boolean;
  setConfidenceVisible: (visible: boolean) => void;
  toggleConfidence: () => void;

  // Dialectic modals
  dialecticModalOpen: boolean;
  setDialecticModalOpen: (open: boolean) => void;
  dialogueViewOpen: boolean;
  setDialogueViewOpen: (open: boolean) => void;
  decisionStreamOpen: boolean;
  setDecisionStreamOpen: (open: boolean) => void;
  toggleDecisionStream: () => void;
  vetoPanelOpen: boolean;
  setVetoPanelOpen: (open: boolean) => void;

  // Selected decision
  selectedDecision: DialecticDecision | null;
  setSelectedDecision: (decision: DialecticDecision | null) => void;

  // Analysis quadrant
  analysisQuadrantOpen: boolean;
  setAnalysisQuadrantOpen: (open: boolean) => void;
  toggleAnalysisQuadrant: () => void;

  // Proof panel
  proofPanelOpen: boolean;
  setProofPanelOpen: (open: boolean) => void;
  toggleProofPanel: () => void;

  // All panels closed check (for keyboard handling)
  allPanelsClosed: boolean;
}

export function useEditorPanels(): UseEditorPanelsReturn {
  // Command line
  const [commandLineVisible, setCommandLineVisible] = useState(false);

  // Help
  const [helpVisible, setHelpVisible] = useState(false);
  const toggleHelp = useCallback(() => setHelpVisible(prev => !prev), []);

  // Confidence
  const [confidenceVisible, setConfidenceVisible] = useState(false);
  const toggleConfidence = useCallback(() => setConfidenceVisible(prev => !prev), []);

  // Dialectic
  const [dialecticModalOpen, setDialecticModalOpen] = useState(false);
  const [dialogueViewOpen, setDialogueViewOpen] = useState(false);
  const [decisionStreamOpen, setDecisionStreamOpen] = useState(false);
  const toggleDecisionStream = useCallback(() => setDecisionStreamOpen(prev => !prev), []);
  const [vetoPanelOpen, setVetoPanelOpen] = useState(false);
  const [selectedDecision, setSelectedDecision] = useState<DialecticDecision | null>(null);

  // Analysis
  const [analysisQuadrantOpen, setAnalysisQuadrantOpen] = useState(false);
  const toggleAnalysisQuadrant = useCallback(() => setAnalysisQuadrantOpen(prev => !prev), []);

  // Proof
  const [proofPanelOpen, setProofPanelOpen] = useState(false);
  const toggleProofPanel = useCallback(() => setProofPanelOpen(prev => !prev), []);

  // Check if all panels are closed (useful for keyboard handling)
  const allPanelsClosed = !commandLineVisible &&
                          !helpVisible &&
                          !dialecticModalOpen &&
                          !dialogueViewOpen;

  return {
    commandLineVisible,
    setCommandLineVisible,
    helpVisible,
    setHelpVisible,
    toggleHelp,
    confidenceVisible,
    setConfidenceVisible,
    toggleConfidence,
    dialecticModalOpen,
    setDialecticModalOpen,
    dialogueViewOpen,
    setDialogueViewOpen,
    decisionStreamOpen,
    setDecisionStreamOpen,
    toggleDecisionStream,
    vetoPanelOpen,
    setVetoPanelOpen,
    selectedDecision,
    setSelectedDecision,
    analysisQuadrantOpen,
    setAnalysisQuadrantOpen,
    toggleAnalysisQuadrant,
    proofPanelOpen,
    setProofPanelOpen,
    toggleProofPanel,
    allPanelsClosed,
  };
}
