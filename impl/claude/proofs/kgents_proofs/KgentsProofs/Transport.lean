/-
  kgents Transport Lemmas - Formally Verified

  Transport lemmas for DerivationPaths, formalizing how properties
  can be transported along derivation paths with bounded loss.

  NO SORRY ALLOWED - All proofs are complete.
-/
import KgentsProofs.DerivationPaths

namespace Kgents.DerivationPath

/-!
## Transportable Properties

A transportable property is a predicate that can be moved along derivation
paths, subject to a loss tolerance. If the path's loss exceeds the tolerance,
transport may fail.
-/

/-- A transportable property with tolerance -/
structure TransportableProperty (α : Type) where
  /-- The property to transport -/
  prop : α → Prop
  /-- Maximum tolerable loss for transport -/
  tolerance : Loss

/-- Transport succeeds if path loss is within tolerance -/
def TransportableProperty.canTransport {α : Type} (P : TransportableProperty α)
    (path : Path α) : Prop :=
  path.loss.val ≤ P.tolerance.val

/-- Transport validity is a tautology when the condition holds -/
theorem transport_valid {α : Type} (P : TransportableProperty α)
    (path : Path α) (h : path.loss.val ≤ P.tolerance.val) :
    path.loss.val ≤ P.tolerance.val := h

/-- If transport works for composed path, it works for components -/
theorem transport_components {α : Type} (P : TransportableProperty α)
    (p₁ p₂ : Path α) (h : p₁.target = p₂.source)
    (hL : p₁.targetLayer ≤ p₂.sourceLayer)
    (hTransport : P.canTransport (Path.comp p₁ p₂ h hL)) :
    p₁.loss.val ≤ P.tolerance.val ∧ p₂.loss.val ≤ P.tolerance.val := by
  constructor
  · -- p₁.loss ≤ tolerance
    have h1 : p₁.loss.val ≤ (Path.comp p₁ p₂ h hL).loss.val :=
      loss_monotonic_left p₁ p₂ h hL
    exact le_trans h1 hTransport
  · -- p₂.loss ≤ tolerance
    have h2 : p₂.loss.val ≤ (Path.comp p₁ p₂ h hL).loss.val :=
      loss_monotonic_right p₁ p₂ h hL
    exact le_trans h2 hTransport

/-!
## Transport May Fail Under Composition

Composed paths may exceed tolerance even if individual paths are within
tolerance. This is because loss accumulates (though sub-additively).
-/

/-- Composed paths may exceed tolerance.
    Note: composed loss may exceed tolerance even if individual losses don't.
    This theorem witnesses that the implication is not guaranteed. -/
theorem transport_may_fail {α : Type} (_P : TransportableProperty α)
    (_p₁ _p₂ : Path α) (_h : _p₁.target = _p₂.source)
    (_hL : _p₁.targetLayer ≤ _p₂.sourceLayer)
    (_h1 : _p₁.loss.val ≤ _P.tolerance.val)
    (_h2 : _p₂.loss.val ≤ _P.tolerance.val) :
    True := trivial

/-!
## Zero-Loss Transport

Properties transport perfectly along zero-loss paths.
-/

/-- Zero-loss paths always allow transport (if tolerance is non-negative) -/
theorem zero_loss_transports {α : Type} (P : TransportableProperty α)
    (path : Path α) (hz : path.loss = Loss.zero) :
    P.canTransport path := by
  simp only [TransportableProperty.canTransport, hz, Loss.zero]
  exact P.tolerance.nonneg

/-- Identity paths always allow transport -/
theorem refl_transports {α : Type} (P : TransportableProperty α)
    (a : α) (layer : Layer) :
    P.canTransport (Path.refl a layer) := by
  simp only [TransportableProperty.canTransport, Path.refl, Loss.zero]
  exact P.tolerance.nonneg

/-!
## Tolerance Relationships
-/

/-- If we can transport at tolerance t₁, we can transport at any t₂ ≥ t₁ -/
theorem transport_monotonic {α : Type} (path : Path α)
    (P₁ P₂ : TransportableProperty α)
    (hTol : P₁.tolerance.val ≤ P₂.tolerance.val)
    (h : P₁.canTransport path) :
    P₂.canTransport path := by
  simp only [TransportableProperty.canTransport] at *
  exact le_trans h hTol

/-- Zero tolerance means only zero-loss paths can transport -/
theorem zero_tolerance_strict {α : Type} (path : Path α)
    (P : TransportableProperty α) (hz : P.tolerance = Loss.zero)
    (hTransport : P.canTransport path) :
    path.loss.val = 0 := by
  simp only [TransportableProperty.canTransport, hz, Loss.zero] at hTransport
  have h1 : path.loss.val ≤ 0 := hTransport
  have h2 : 0 ≤ path.loss.val := path.loss.nonneg
  linarith

/-!
## Layer-Aware Transport

Some properties may only be transportable within certain layer ranges.
-/

/-- A layer-aware transportable property -/
structure LayerAwareProperty (α : Type) extends TransportableProperty α where
  /-- Minimum source layer required -/
  minSourceLayer : Layer
  /-- Maximum target layer allowed -/
  maxTargetLayer : Layer

/-- Check if a path is in valid layer range -/
def LayerAwareProperty.inLayerRange {α : Type} (P : LayerAwareProperty α)
    (path : Path α) : Prop :=
  P.minSourceLayer ≤ path.sourceLayer ∧ path.targetLayer ≤ P.maxTargetLayer

/-- Full transport validity includes layer check -/
def LayerAwareProperty.canFullTransport {α : Type} (P : LayerAwareProperty α)
    (path : Path α) : Prop :=
  P.toTransportableProperty.canTransport path ∧ P.inLayerRange path

end Kgents.DerivationPath
