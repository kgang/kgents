/**
 * DesignSystemPage — Categorical Design Language System
 *
 * The concept.design node exposes the three orthogonal design functors:
 * - Layout[D]: split, stack, drawer, float
 * - Content[D]: degrade, compose
 * - Motion[M]: breathe, pop, shake, shimmer, chain, parallel
 *
 * Core Insight: UI = Layout[D] ∘ Content[D] ∘ Motion[M]
 *
 * Features:
 * - Operad visualizations with composition grammar
 * - Live law verification (click to verify)
 * - Operation documentation
 *
 * "Daring, bold, creative, opinionated but not gaudy"
 *
 * AGENTESE Route: /concept.design
 *
 * @see agents/design/operad.py
 * @see protocols/agentese/contexts/design.py
 */

import { useState, useCallback } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import {
  Boxes,
  Layers,
  Type,
  Sparkles,
  CheckCircle2,
  XCircle,
  AlertCircle,
  ChevronRight,
  Play,
  RefreshCw,
} from 'lucide-react';
import { useAgentese, useAgenteseMutation } from '@/hooks/useAgentesePath';
import { Breathe } from '@/components/joy';

// =============================================================================
// Types
// =============================================================================

interface OperadManifest {
  name: string;
  operations: string[];
  law_count: number;
}

interface Operation {
  arity: number;
  signature: string;
  description: string;
}

interface Law {
  name: string;
  equation: string;
  description: string;
}

interface LawVerification {
  law: string;
  status: 'passed' | 'structural' | 'failed' | 'skipped';
  passed: boolean;
  message: string;
}

type OperadKey = 'layout' | 'content' | 'motion' | 'operad';

// =============================================================================
// Constants
// =============================================================================

const OPERAD_CONFIG: Record<
  OperadKey,
  {
    path: string;
    label: string;
    icon: typeof Boxes;
    color: string;
    bgColor: string;
    description: string;
  }
> = {
  layout: {
    path: 'concept.design.layout',
    label: 'Layout',
    icon: Boxes,
    color: 'text-blue-400',
    bgColor: 'bg-blue-500/10 border-blue-500/20',
    description: 'split, stack, drawer, float',
  },
  content: {
    path: 'concept.design.content',
    label: 'Content',
    icon: Type,
    color: 'text-amber-400',
    bgColor: 'bg-amber-500/10 border-amber-500/20',
    description: 'degrade, compose',
  },
  motion: {
    path: 'concept.design.motion',
    label: 'Motion',
    icon: Sparkles,
    color: 'text-purple-400',
    bgColor: 'bg-purple-500/10 border-purple-500/20',
    description: 'breathe, pop, shake, shimmer',
  },
  operad: {
    path: 'concept.design.operad',
    label: 'Unified',
    icon: Layers,
    color: 'text-cyan-400',
    bgColor: 'bg-cyan-500/10 border-cyan-500/20',
    description: 'Layout ∘ Content ∘ Motion',
  },
};

// =============================================================================
// Sub-Components
// =============================================================================

function OperadCard({
  operadKey,
  manifest,
  isSelected,
  onClick,
}: {
  operadKey: OperadKey;
  manifest: OperadManifest | null;
  isSelected: boolean;
  onClick: () => void;
}) {
  const config = OPERAD_CONFIG[operadKey];
  const Icon = config.icon;

  return (
    <motion.button
      whileHover={{ scale: 1.02 }}
      whileTap={{ scale: 0.98 }}
      onClick={onClick}
      className={`
        relative p-4 rounded-xl border transition-all text-left w-full
        ${isSelected ? `${config.bgColor} ${config.color}` : 'bg-gray-800/40 border-gray-700/50 text-gray-400 hover:border-gray-600'}
      `}
    >
      <div className="flex items-center gap-3">
        <div className={`p-2 rounded-lg ${isSelected ? config.bgColor : 'bg-gray-700/50'}`}>
          <Icon className={`w-5 h-5 ${isSelected ? config.color : 'text-gray-500'}`} />
        </div>
        <div className="flex-1 min-w-0">
          <h3 className={`font-medium ${isSelected ? 'text-white' : 'text-gray-300'}`}>
            {config.label} Operad
          </h3>
          <p className="text-xs text-gray-500 truncate">{config.description}</p>
        </div>
        {manifest && (
          <div className="text-right">
            <div className="text-sm font-medium">{manifest.operations.length}</div>
            <div className="text-xs text-gray-600">ops</div>
          </div>
        )}
        <ChevronRight
          className={`w-4 h-4 transition-transform ${isSelected ? 'rotate-90' : ''}`}
        />
      </div>
    </motion.button>
  );
}

function OperationList({ operations }: { operations: Record<string, Operation> | null }) {
  if (!operations || Object.keys(operations).length === 0) {
    return <div className="text-gray-500 text-sm p-4">No operations available</div>;
  }

  return (
    <div className="divide-y divide-gray-700/50">
      {Object.entries(operations).map(([name, op]) => (
        <div key={name} className="p-4">
          <div className="flex items-center gap-2 mb-1">
            <code className="text-cyan-400 font-mono text-sm">{name}</code>
            <span className="text-xs text-gray-600 px-1.5 py-0.5 bg-gray-700/50 rounded">
              arity: {op.arity}
            </span>
          </div>
          <p className="text-sm text-gray-400">{op.description}</p>
          {op.signature && (
            <code className="text-xs text-gray-500 mt-1 block">{op.signature}</code>
          )}
        </div>
      ))}
    </div>
  );
}

function LawList({
  laws,
  verificationResults,
}: {
  laws: Law[] | null;
  verificationResults: LawVerification[] | null;
}) {
  if (!laws || laws.length === 0) {
    return <div className="text-gray-500 text-sm p-4">No laws defined</div>;
  }

  const getVerification = (lawName: string) => {
    return verificationResults?.find((v) => v.law === lawName);
  };

  return (
    <div className="divide-y divide-gray-700/50">
      {laws.map((law) => {
        const verification = getVerification(law.name);
        const StatusIcon = verification
          ? verification.passed
            ? CheckCircle2
            : verification.status === 'structural'
              ? AlertCircle
              : XCircle
          : null;

        return (
          <div key={law.name} className="p-4">
            <div className="flex items-center gap-2 mb-1">
              <span className="text-purple-400 font-medium text-sm">{law.name}</span>
              {StatusIcon && (
                <StatusIcon
                  className={`w-4 h-4 ${
                    verification?.passed
                      ? 'text-green-400'
                      : verification?.status === 'structural'
                        ? 'text-amber-400'
                        : 'text-red-400'
                  }`}
                />
              )}
            </div>
            <code className="text-xs text-cyan-300/80 font-mono block mb-1">
              {law.equation}
            </code>
            <p className="text-sm text-gray-500">{law.description}</p>
            {verification && verification.message && (
              <p className="text-xs text-gray-600 mt-1">{verification.message}</p>
            )}
          </div>
        );
      })}
    </div>
  );
}

// =============================================================================
// Main Component
// =============================================================================

export default function DesignSystemPage() {
  const [selectedOperad, setSelectedOperad] = useState<OperadKey>('operad');
  const [activeTab, setActiveTab] = useState<'operations' | 'laws'>('operations');
  const [verificationResults, setVerificationResults] = useState<LawVerification[] | null>(null);

  const config = OPERAD_CONFIG[selectedOperad];

  // Fetch manifest for all operads (for card display)
  const { data: layoutManifest } = useAgentese<OperadManifest>('concept.design.layout');
  const { data: contentManifest } = useAgentese<OperadManifest>('concept.design.content');
  const { data: motionManifest } = useAgentese<OperadManifest>('concept.design.motion');
  const { data: unifiedManifest } = useAgentese<OperadManifest>('concept.design.operad');

  const manifests: Record<OperadKey, OperadManifest | null> = {
    layout: layoutManifest,
    content: contentManifest,
    motion: motionManifest,
    operad: unifiedManifest,
  };

  // Fetch operations for selected operad
  const { data: operations, isLoading: operationsLoading } = useAgentese<
    Record<string, Operation>
  >(config.path, { aspect: 'operations' });

  // Fetch laws for selected operad
  const { data: laws, isLoading: lawsLoading } = useAgentese<Law[]>(config.path, {
    aspect: 'laws',
  });

  // Verify mutation
  const verifyMutation = useAgenteseMutation<
    undefined,
    { all_passed?: boolean; results?: LawVerification[] } | LawVerification[]
  >(`${config.path}:verify`);

  const handleVerify = useCallback(async () => {
    setVerificationResults(null);
    const result = await verifyMutation.mutate(undefined);
    if (result) {
      // Handle both unified operad (with all_passed) and individual operads (array)
      if (Array.isArray(result)) {
        setVerificationResults(result);
      } else if (result.results) {
        setVerificationResults(result.results);
      }
    }
  }, [verifyMutation]);

  const handleOperadSelect = useCallback((key: OperadKey) => {
    setSelectedOperad(key);
    setVerificationResults(null);
    setActiveTab('operations');
  }, []);

  return (
    <div className="flex flex-col h-full bg-gray-900 text-gray-100">
      {/* Header */}
      <div className="flex items-center justify-between px-6 py-4 border-b border-gray-700/50 bg-gray-800/40">
        <div className="flex items-center gap-3">
          <Breathe intensity={0.3} speed="slow">
            <div className="p-2.5 rounded-xl bg-gradient-to-br from-blue-500/20 to-purple-500/20 border border-blue-500/30">
              <Layers className="w-6 h-6 text-blue-400" />
            </div>
          </Breathe>
          <div>
            <h1 className="text-lg font-semibold text-white">Design Language System</h1>
            <p className="text-xs text-gray-500">UI = Layout[D] ∘ Content[D] ∘ Motion[M]</p>
          </div>
        </div>
      </div>

      {/* Main Content */}
      <div className="flex-1 flex overflow-hidden">
        {/* Left Panel: Operad Selector */}
        <div className="w-80 p-4 border-r border-gray-700/50 overflow-y-auto space-y-3">
          <div className="text-xs text-gray-600 uppercase tracking-wider mb-3">
            Design Operads
          </div>
          {(Object.keys(OPERAD_CONFIG) as OperadKey[]).map((key) => (
            <OperadCard
              key={key}
              operadKey={key}
              manifest={manifests[key]}
              isSelected={selectedOperad === key}
              onClick={() => handleOperadSelect(key)}
            />
          ))}

          <div className="pt-4 border-t border-gray-700/50 mt-4">
            <div className="p-4 rounded-xl bg-gray-800/40 border border-gray-700/50">
              <h3 className="text-sm font-medium text-gray-300 mb-2">Core Insight</h3>
              <p className="text-xs text-gray-500">
                Three orthogonal dimensions compose to build any UI. Each dimension has its own
                operad with composition grammar.
              </p>
              <div className="mt-3 space-y-1">
                <div className="text-xs text-gray-600">
                  <span className="text-blue-400">Layout[D]</span> — Where things go
                </div>
                <div className="text-xs text-gray-600">
                  <span className="text-amber-400">Content[D]</span> — What to show
                </div>
                <div className="text-xs text-gray-600">
                  <span className="text-purple-400">Motion[M]</span> — How to animate
                </div>
              </div>
            </div>
          </div>
        </div>

        {/* Right Panel: Details */}
        <div className="flex-1 flex flex-col overflow-hidden">
          {/* Tab Header */}
          <div className="flex items-center justify-between p-4 border-b border-gray-700/50">
            <div className="flex gap-2">
              <button
                onClick={() => setActiveTab('operations')}
                className={`px-4 py-2 rounded-lg text-sm font-medium transition-colors ${
                  activeTab === 'operations'
                    ? 'bg-gray-700 text-white'
                    : 'text-gray-400 hover:text-gray-200'
                }`}
              >
                Operations
              </button>
              <button
                onClick={() => setActiveTab('laws')}
                className={`px-4 py-2 rounded-lg text-sm font-medium transition-colors ${
                  activeTab === 'laws'
                    ? 'bg-gray-700 text-white'
                    : 'text-gray-400 hover:text-gray-200'
                }`}
              >
                Laws ({laws?.length ?? 0})
              </button>
            </div>

            {activeTab === 'laws' && (
              <button
                onClick={handleVerify}
                disabled={verifyMutation.isLoading}
                className="flex items-center gap-2 px-4 py-2 bg-cyan-600 hover:bg-cyan-500 disabled:bg-gray-700 text-white rounded-lg text-sm transition-colors"
              >
                {verifyMutation.isLoading ? (
                  <RefreshCw className="w-4 h-4 animate-spin" />
                ) : (
                  <Play className="w-4 h-4" />
                )}
                Verify Laws
              </button>
            )}
          </div>

          {/* Content */}
          <div className="flex-1 overflow-y-auto">
            <AnimatePresence mode="wait">
              {activeTab === 'operations' ? (
                <motion.div
                  key="operations"
                  initial={{ opacity: 0, x: -20 }}
                  animate={{ opacity: 1, x: 0 }}
                  exit={{ opacity: 0, x: 20 }}
                >
                  {operationsLoading ? (
                    <div className="flex items-center justify-center h-64">
                      <RefreshCw className="w-6 h-6 text-gray-500 animate-spin" />
                    </div>
                  ) : (
                    <OperationList operations={operations} />
                  )}
                </motion.div>
              ) : (
                <motion.div
                  key="laws"
                  initial={{ opacity: 0, x: -20 }}
                  animate={{ opacity: 1, x: 0 }}
                  exit={{ opacity: 0, x: 20 }}
                >
                  {lawsLoading ? (
                    <div className="flex items-center justify-center h-64">
                      <RefreshCw className="w-6 h-6 text-gray-500 animate-spin" />
                    </div>
                  ) : (
                    <LawList laws={laws} verificationResults={verificationResults} />
                  )}
                </motion.div>
              )}
            </AnimatePresence>
          </div>

          {/* Verification Summary */}
          {verificationResults && verificationResults.length > 0 && (
            <div className="p-4 border-t border-gray-700/50 bg-gray-800/40">
              <div className="flex items-center gap-4">
                <div className="flex items-center gap-2">
                  <CheckCircle2 className="w-4 h-4 text-green-400" />
                  <span className="text-sm text-gray-400">
                    {verificationResults.filter((v) => v.passed).length} passed
                  </span>
                </div>
                <div className="flex items-center gap-2">
                  <AlertCircle className="w-4 h-4 text-amber-400" />
                  <span className="text-sm text-gray-400">
                    {verificationResults.filter((v) => v.status === 'structural').length}{' '}
                    structural
                  </span>
                </div>
                <div className="flex items-center gap-2">
                  <XCircle className="w-4 h-4 text-red-400" />
                  <span className="text-sm text-gray-400">
                    {verificationResults.filter((v) => !v.passed && v.status !== 'structural').length}{' '}
                    failed
                  </span>
                </div>
              </div>
            </div>
          )}
        </div>
      </div>
    </div>
  );
}
