/**
 * Zero Seed Governance Pilot
 *
 * Personal constitution building from axioms.
 * "The loss IS the layer. The fixed point IS the axiom."
 *
 * This pilot provides:
 * - Constitution view with layer visualization
 * - Amendment history tracking
 * - Axiom detection via fixed point analysis
 */

import { Routes, Route, Navigate, NavLink } from 'react-router-dom';
import { useState, useCallback } from 'react';
import {
  detectFixedPoint,
  assignLayer,
  LAYERS,
  getLayerColor,
  getLayerBorderColor,
  formatLoss,
  type FixedPointResponse,
  type LayerAssignResponse,
} from '../../api/galois';

// =============================================================================
// Layout
// =============================================================================

export function ZeroSeedLayout() {
  return (
    <div className="space-y-6">
      <div className="text-center">
        <h1 className="text-2xl font-bold text-lantern mb-2">Zero Seed Governance</h1>
        <p className="text-sand">Build your personal constitution from axioms</p>
      </div>

      {/* Navigation tabs */}
      <nav className="flex justify-center gap-4 border-b border-sage/20 pb-4">
        <TabLink to="/zero-seed" label="Constitution" end />
        <TabLink to="/zero-seed/amendments" label="Amendments" />
        <TabLink to="/zero-seed/axioms" label="Axioms" />
      </nav>

      <Routes>
        <Route index element={<ConstitutionPage />} />
        <Route path="amendments" element={<AmendmentsPage />} />
        <Route path="axioms" element={<AxiomsPage />} />
        <Route path="*" element={<Navigate to="." replace />} />
      </Routes>
    </div>
  );
}

function TabLink({ to, label, end }: { to: string; label: string; end?: boolean }) {
  return (
    <NavLink
      to={to}
      end={end}
      className={({ isActive }) =>
        `px-4 py-2 rounded-lg transition-colors ${
          isActive
            ? 'bg-sage/20 text-sage'
            : 'text-sand hover:text-lantern'
        }`
      }
    >
      {label}
    </NavLink>
  );
}

// =============================================================================
// Constitution Page
// =============================================================================

function ConstitutionPage() {
  const [selectedLayer, setSelectedLayer] = useState<number | null>(null);

  return (
    <div className="space-y-8">
      {/* Layer Pyramid Visualization */}
      <div className="max-w-3xl mx-auto">
        <h2 className="text-lg font-medium text-lantern mb-4 text-center">
          Epistemic Layer Structure
        </h2>
        <LayerPyramid
          selectedLayer={selectedLayer}
          onSelectLayer={setSelectedLayer}
        />
      </div>

      {/* Layer Details */}
      {selectedLayer && (
        <LayerDetails layer={selectedLayer} />
      )}

      {/* Constitution Summary */}
      <div className="rounded-xl border border-sage/20 p-6">
        <h3 className="text-lg font-medium text-lantern mb-4">Your Constitution</h3>
        <div className="text-center py-8 text-sand">
          <p className="mb-2">No constitution entries yet.</p>
          <p className="text-sm text-clay">
            Use the Axiom Detector in the Axioms tab to discover your fixed points.
          </p>
        </div>
      </div>
    </div>
  );
}

// =============================================================================
// Layer Pyramid Visualization
// =============================================================================

interface LayerPyramidProps {
  selectedLayer: number | null;
  onSelectLayer: (layer: number | null) => void;
}

function LayerPyramid({ selectedLayer, onSelectLayer }: LayerPyramidProps) {
  // Reverse layers so L1 (Axiom) is at the bottom
  const reversedLayers = [...LAYERS].reverse();

  return (
    <div className="flex flex-col items-center gap-1">
      {reversedLayers.map((layer, idx) => {
        const isSelected = selectedLayer === layer.number;
        // Width increases as we go down (higher layer numbers at top are narrower)
        const widthPercent = 40 + (6 - idx) * 10; // L7=40%, L1=100%

        return (
          <button
            key={layer.number}
            onClick={() => onSelectLayer(isSelected ? null : layer.number)}
            className={`
              relative py-3 rounded transition-all
              ${getLayerColor(layer.number)}
              ${isSelected ? `ring-2 ring-sage ${getLayerBorderColor(layer.number)}` : 'border border-transparent hover:border-sage/30'}
            `}
            style={{ width: `${widthPercent}%` }}
          >
            <div className="flex items-center justify-center gap-2">
              <span className="text-xs font-mono text-clay">L{layer.number}</span>
              <span className="text-sm font-medium text-lantern">{layer.name}</span>
            </div>
          </button>
        );
      })}

      {/* Base label */}
      <div className="text-xs text-clay mt-2">
        Foundation (Axioms) at base, Surface (Representation) at top
      </div>
    </div>
  );
}

// =============================================================================
// Layer Details
// =============================================================================

interface LayerDetailsProps {
  layer: number;
}

function LayerDetails({ layer }: LayerDetailsProps) {
  const layerInfo = LAYERS.find((l) => l.number === layer);
  if (!layerInfo) return null;

  return (
    <div className={`rounded-xl border p-6 ${getLayerBorderColor(layer)} ${getLayerColor(layer)}`}>
      <div className="flex items-start justify-between mb-4">
        <div>
          <h3 className="text-lg font-medium text-lantern">
            L{layer}: {layerInfo.name}
          </h3>
          <p className="text-sand text-sm">{layerInfo.description}</p>
        </div>
        <div className="text-right text-xs text-clay">
          <div>Loss Range</div>
          <div className="font-mono">
            {formatLoss(layerInfo.lossRange[0])} - {formatLoss(layerInfo.lossRange[1])}
          </div>
        </div>
      </div>

      {/* Layer-specific content placeholder */}
      <div className="text-sm text-sand border-t border-sage/20 pt-4 mt-4">
        {layer === 1 && (
          <p>
            Axioms are self-evident truths that survive the restructure-reconstitute cycle.
            They form the foundation of your constitution.
          </p>
        )}
        {layer === 2 && (
          <p>
            Values derive from axioms and express what matters most.
            They guide decision-making at higher layers.
          </p>
        )}
        {layer === 3 && (
          <p>
            Goals translate values into desired outcomes.
            They provide direction without prescribing specific actions.
          </p>
        )}
        {layer >= 4 && (
          <p>
            Higher layers become increasingly specific and context-dependent,
            derived from the stable foundations below.
          </p>
        )}
      </div>
    </div>
  );
}

// =============================================================================
// Amendments Page
// =============================================================================

function AmendmentsPage() {
  return (
    <div className="space-y-6 max-w-2xl mx-auto">
      <div className="rounded-xl border border-sage/20 p-6">
        <h2 className="text-lg font-medium text-lantern mb-4">Amendment History</h2>
        <div className="text-center py-12">
          <div className="text-4xl mb-4">Coming Soon</div>
          <p className="text-sand mb-2">
            Track how your constitution evolves over time.
          </p>
          <p className="text-sm text-clay">
            Amendments will show when axioms are added, values shift,
            or contradictions are resolved through synthesis.
          </p>
        </div>
      </div>

      {/* Preview of what amendments will look like */}
      <div className="rounded-xl border border-clay/20 p-6 opacity-60">
        <h3 className="text-sm font-medium text-clay mb-4">Preview: Amendment Format</h3>
        <div className="space-y-3 text-sm">
          <AmendmentPreview
            date="2025-12-26"
            type="addition"
            layer={1}
            content="Added axiom: Agency requires justification"
          />
          <AmendmentPreview
            date="2025-12-25"
            type="synthesis"
            layer={2}
            content="Resolved contradiction between efficiency and thoroughness"
          />
        </div>
      </div>
    </div>
  );
}

interface AmendmentPreviewProps {
  date: string;
  type: 'addition' | 'removal' | 'synthesis' | 'refinement';
  layer: number;
  content: string;
}

function AmendmentPreview({ date, type, layer, content }: AmendmentPreviewProps) {
  const typeColors = {
    addition: 'text-sage',
    removal: 'text-red-400',
    synthesis: 'text-amber',
    refinement: 'text-cyan-400',
  };

  return (
    <div className="flex items-start gap-3 p-3 rounded-lg bg-bark/50">
      <div className="text-xs text-clay font-mono">{date}</div>
      <div className="flex-1">
        <div className="flex items-center gap-2 mb-1">
          <span className={`text-xs font-medium ${typeColors[type]}`}>
            {type.toUpperCase()}
          </span>
          <span className="text-xs text-clay">L{layer}</span>
        </div>
        <p className="text-sand text-sm">{content}</p>
      </div>
    </div>
  );
}

// =============================================================================
// Axioms Page
// =============================================================================

function AxiomsPage() {
  const [input, setInput] = useState('');
  const [loading, setLoading] = useState(false);
  const [result, setResult] = useState<{
    fixedPoint: FixedPointResponse | null;
    layer: LayerAssignResponse | null;
  } | null>(null);
  const [error, setError] = useState<string | null>(null);

  const handleDetect = useCallback(async () => {
    if (!input.trim()) return;

    setLoading(true);
    setError(null);
    setResult(null);

    try {
      // Run both analyses in parallel
      const [fpResult, layerResult] = await Promise.all([
        detectFixedPoint(input.trim()),
        assignLayer(input.trim()),
      ]);

      setResult({
        fixedPoint: fpResult,
        layer: layerResult,
      });
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Analysis failed');
    } finally {
      setLoading(false);
    }
  }, [input]);

  return (
    <div className="space-y-6 max-w-2xl mx-auto">
      {/* Axiom Detector Card */}
      <div className="rounded-xl border border-amber/30 bg-amber/5 p-6">
        <h2 className="text-lg font-medium text-lantern mb-2">Axiom Detector</h2>
        <p className="text-sand text-sm mb-4">
          Enter a statement to check if it qualifies as an axiom (semantic fixed point).
        </p>

        <div className="space-y-4">
          <textarea
            value={input}
            onChange={(e) => setInput(e.target.value)}
            placeholder="Enter a statement to analyze... (e.g., 'Agency requires justification')"
            className="w-full h-24 px-4 py-3 rounded-lg bg-bark border border-sage/20 text-lantern placeholder-clay resize-none focus:outline-none focus:border-sage"
          />

          <button
            onClick={handleDetect}
            disabled={loading || !input.trim()}
            className="w-full px-6 py-3 rounded-xl bg-amber text-bark font-medium hover:bg-amber/90 transition-colors disabled:opacity-50 disabled:cursor-not-allowed"
          >
            {loading ? 'Analyzing...' : 'Detect Axiom'}
          </button>
        </div>

        {error && (
          <div className="mt-4 p-4 rounded-lg bg-red-500/10 border border-red-500/30 text-red-400">
            {error}
          </div>
        )}
      </div>

      {/* Analysis Result */}
      {result && (
        <AxiomResult result={result} content={input} />
      )}

      {/* Discovered Axioms */}
      <div className="rounded-xl border border-sage/20 p-6">
        <h2 className="text-lg font-medium text-lantern mb-4">Discovered Axioms</h2>
        <div className="text-center py-8 text-sand">
          <p className="mb-2">No axioms discovered yet.</p>
          <p className="text-sm text-clay">
            Statements with loss &lt; 1% and stability across R/C iterations qualify as axioms.
          </p>
        </div>
      </div>
    </div>
  );
}

// =============================================================================
// Axiom Result Display
// =============================================================================

interface AxiomResultProps {
  result: {
    fixedPoint: FixedPointResponse | null;
    layer: LayerAssignResponse | null;
  };
  content: string;
}

function AxiomResult({ result, content }: AxiomResultProps) {
  const { fixedPoint, layer } = result;

  if (!fixedPoint || !layer) {
    return (
      <div className="rounded-xl border border-clay/30 p-6">
        <p className="text-clay">Incomplete analysis result</p>
      </div>
    );
  }

  const isAxiom = fixedPoint.is_axiom;
  const isFixedPoint = fixedPoint.is_fixed_point;

  return (
    <div className={`rounded-xl border p-6 ${
      isAxiom
        ? 'border-emerald-500/40 bg-emerald-500/10'
        : isFixedPoint
          ? 'border-teal-500/40 bg-teal-500/10'
          : 'border-clay/30 bg-bark'
    }`}>
      {/* Header */}
      <div className="flex items-start justify-between mb-4">
        <div>
          <h3 className="text-lg font-medium text-lantern">
            {isAxiom ? 'Axiom Detected!' : isFixedPoint ? 'Fixed Point Found' : 'Not a Fixed Point'}
          </h3>
          <p className="text-sand text-sm mt-1">{content}</p>
        </div>
        <div className={`px-3 py-1 rounded-full text-xs font-medium ${
          isAxiom
            ? 'bg-emerald-500/20 text-emerald-400'
            : isFixedPoint
              ? 'bg-teal-500/20 text-teal-400'
              : 'bg-clay/20 text-clay'
        }`}>
          L{layer.layer} {layer.layer_name}
        </div>
      </div>

      {/* Metrics Grid */}
      <div className="grid grid-cols-2 md:grid-cols-4 gap-4 mb-4">
        <MetricCard
          label="Final Loss"
          value={formatLoss(fixedPoint.final_loss)}
          sublabel={isAxiom ? 'Axiom threshold: <1%' : undefined}
        />
        <MetricCard
          label="Iterations"
          value={`${fixedPoint.iterations_to_converge}`}
          sublabel={fixedPoint.iterations_to_converge === -1 ? 'Did not converge' : 'To converge'}
        />
        <MetricCard
          label="Stable"
          value={fixedPoint.stability_achieved ? 'Yes' : 'No'}
          sublabel="Under R/C cycles"
        />
        <MetricCard
          label="Confidence"
          value={formatLoss(layer.confidence)}
          sublabel={`Layer ${layer.layer}`}
        />
      </div>

      {/* Loss History Chart */}
      {fixedPoint.loss_history.length > 0 && (
        <div className="border-t border-sage/20 pt-4">
          <h4 className="text-sm font-medium text-sand mb-2">Loss History (R/C Iterations)</h4>
          <LossHistoryChart history={fixedPoint.loss_history} />
        </div>
      )}

      {/* Insight */}
      {layer.insight && (
        <div className="border-t border-sage/20 pt-4 mt-4">
          <h4 className="text-sm font-medium text-sand mb-2">Insight</h4>
          <p className="text-lantern text-sm">{layer.insight}</p>
        </div>
      )}
    </div>
  );
}

interface MetricCardProps {
  label: string;
  value: string;
  sublabel?: string;
}

function MetricCard({ label, value, sublabel }: MetricCardProps) {
  return (
    <div className="p-3 rounded-lg bg-bark/50 border border-sage/10">
      <div className="text-xs text-clay mb-1">{label}</div>
      <div className="text-lg font-medium text-lantern">{value}</div>
      {sublabel && <div className="text-xs text-clay mt-1">{sublabel}</div>}
    </div>
  );
}

// =============================================================================
// Loss History Chart
// =============================================================================

interface LossHistoryChartProps {
  history: number[];
}

function LossHistoryChart({ history }: LossHistoryChartProps) {
  const maxLoss = Math.max(...history, 0.1);
  const barWidth = 100 / history.length;

  return (
    <div className="h-24 flex items-end gap-1">
      {history.map((loss, idx) => {
        const heightPercent = (loss / maxLoss) * 100;
        const isAxiomLevel = loss < 0.01;
        const isFixedPointLevel = loss < 0.05;

        return (
          <div
            key={idx}
            className="flex-1 flex flex-col items-center gap-1"
            style={{ maxWidth: `${barWidth}%` }}
          >
            <div
              className={`w-full rounded-t transition-all ${
                isAxiomLevel
                  ? 'bg-emerald-500'
                  : isFixedPointLevel
                    ? 'bg-teal-500'
                    : 'bg-sage'
              }`}
              style={{ height: `${Math.max(heightPercent, 5)}%` }}
            />
            <div className="text-xs text-clay">{idx + 1}</div>
          </div>
        );
      })}
    </div>
  );
}
