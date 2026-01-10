/-
  kgents DerivationPaths - Formally Verified

  This module formalizes the derivation path structure from kgents Zero Seed
  Galois convergence. A derivation path represents the transformation between
  artifacts across abstraction layers, with tracked semantic loss.

  Proves:
  1. Path composition is associative (source/target preservation)
  2. Identity paths satisfy left/right identity
  3. Loss is monotonic under composition
  4. Layer monotonicity is preserved
  5. Zero loss is identity for composition

  NO SORRY ALLOWED - All proofs are complete.
-/
import Mathlib.CategoryTheory.Category.Basic
import Mathlib.Data.Real.Basic
import Mathlib.Tactic

namespace Kgents.DerivationPath

/-!
## Layer Definition

The 7 layers from Zero Seed Galois convergence, ordered from most abstract
(axiom) to most concrete (representation).
-/

/-- The 7 layers from Zero Seed Galois convergence -/
inductive Layer where
  | axiom           -- L1: Zero-loss fixed points
  | value           -- L2: Low loss, principles
  | goal            -- L3: Moderate abstraction
  | spec            -- L4: Specification
  | execution       -- L5: Implementation
  | reflection      -- L6: Synthesis
  | representation  -- L7: Meta-structure
  deriving DecidableEq, Repr

/-- Layer ordering (lower = more abstract) -/
def Layer.toNat : Layer → ℕ
  | .axiom => 1
  | .value => 2
  | .goal => 3
  | .spec => 4
  | .execution => 5
  | .reflection => 6
  | .representation => 7

instance : LE Layer where le a b := a.toNat ≤ b.toNat
instance : LT Layer where lt a b := a.toNat < b.toNat

instance : DecidableRel (α := Layer) (· ≤ ·) := fun a b =>
  inferInstanceAs (Decidable (a.toNat ≤ b.toNat))

instance : DecidableRel (α := Layer) (· < ·) := fun a b =>
  inferInstanceAs (Decidable (a.toNat < b.toNat))

/-- Layer ordering is reflexive -/
theorem Layer.le_refl (a : Layer) : a ≤ a := Nat.le_refl a.toNat

/-- Layer ordering is transitive -/
theorem Layer.le_trans {a b c : Layer} (h1 : a ≤ b) (h2 : b ≤ c) : a ≤ c :=
  Nat.le_trans h1 h2

/-!
## Loss Definition

Loss represents semantic degradation during derivation.
Loss values are in [0,1], with 0 being perfect preservation and 1 being total loss.
-/

/-- Loss value in [0,1] -/
structure Loss where
  val : ℝ
  nonneg : 0 ≤ val
  bounded : val ≤ 1

/-- Zero loss (perfect preservation) -/
def Loss.zero : Loss :=
  ⟨0, le_refl 0, zero_le_one⟩

/-- One loss (complete loss) -/
def Loss.one : Loss :=
  ⟨1, zero_le_one, le_refl 1⟩

/-- Multiplicative loss composition: 1 - (1-a)*(1-b)
    This models that loss accumulates but saturates at 1.
    If a = 0, result = b. If b = 0, result = a. -/
def Loss.compose (a b : Loss) : Loss :=
  ⟨1 - (1 - a.val) * (1 - b.val),
   by -- nonneg proof: 0 ≤ 1 - (1-a)*(1-b)
     have ha : 0 ≤ 1 - a.val := by linarith [a.bounded]
     have hb : 0 ≤ 1 - b.val := by linarith [b.bounded]
     have ha' : 1 - a.val ≤ 1 := by linarith [a.nonneg]
     have hb' : 1 - b.val ≤ 1 := by linarith [b.nonneg]
     have prod_le : (1 - a.val) * (1 - b.val) ≤ 1 := by
       calc (1 - a.val) * (1 - b.val)
           ≤ 1 * (1 - b.val) := by apply mul_le_mul_of_nonneg_right ha' hb
         _ = 1 - b.val := one_mul _
         _ ≤ 1 := hb'
     linarith,
   by -- bounded proof: 1 - (1-a)*(1-b) ≤ 1
     have ha : 0 ≤ 1 - a.val := by linarith [a.bounded]
     have hb : 0 ≤ 1 - b.val := by linarith [b.bounded]
     have prod_nonneg : 0 ≤ (1 - a.val) * (1 - b.val) := mul_nonneg ha hb
     linarith⟩

/-!
## Loss Theorems
-/

/-- Zero loss is left identity for composition -/
theorem Loss.zero_compose (a : Loss) :
    (Loss.compose Loss.zero a).val = a.val := by
  simp only [Loss.compose, Loss.zero]
  ring

/-- Zero loss is right identity for composition -/
theorem Loss.compose_zero (a : Loss) :
    (Loss.compose a Loss.zero).val = a.val := by
  simp only [Loss.compose, Loss.zero]
  ring

/-- Loss composition is commutative -/
theorem Loss.compose_comm (a b : Loss) :
    (Loss.compose a b).val = (Loss.compose b a).val := by
  simp only [Loss.compose]
  ring

/-- Loss composition is associative -/
theorem Loss.compose_assoc (a b c : Loss) :
    (Loss.compose (Loss.compose a b) c).val = (Loss.compose a (Loss.compose b c)).val := by
  simp only [Loss.compose]
  ring

/-!
## Path Definition

A derivation path connects a source artifact to a target artifact,
tracking the semantic loss and layer transition.
-/

/-- Derivation path between two artifacts -/
structure Path (α : Type) where
  source : α
  target : α
  loss : Loss
  sourceLayer : Layer
  targetLayer : Layer
  layerValid : sourceLayer ≤ targetLayer  -- Derivations go "down" (abstract → concrete)

/-- Identity path (reflexivity) -/
def Path.refl (a : α) (layer : Layer) : Path α :=
  ⟨a, a, Loss.zero, layer, layer, Layer.le_refl layer⟩

/-- Path composition -/
def Path.comp (p₁ p₂ : Path α) (_h : p₁.target = p₂.source)
    (hLayer : p₁.targetLayer ≤ p₂.sourceLayer) : Path α :=
  ⟨p₁.source, p₂.target,
   Loss.compose p₁.loss p₂.loss,
   p₁.sourceLayer, p₂.targetLayer,
   Layer.le_trans p₁.layerValid (Layer.le_trans hLayer p₂.layerValid)⟩

/-!
## Path Composition Theorems
-/

/-- Composition preserves source -/
theorem comp_source (p₁ p₂ : Path α) (h : p₁.target = p₂.source)
    (hL : p₁.targetLayer ≤ p₂.sourceLayer) :
    (Path.comp p₁ p₂ h hL).source = p₁.source := rfl

/-- Composition preserves target -/
theorem comp_target (p₁ p₂ : Path α) (h : p₁.target = p₂.source)
    (hL : p₁.targetLayer ≤ p₂.sourceLayer) :
    (Path.comp p₁ p₂ h hL).target = p₂.target := rfl

/-- Composition preserves source layer -/
theorem comp_sourceLayer (p₁ p₂ : Path α) (h : p₁.target = p₂.source)
    (hL : p₁.targetLayer ≤ p₂.sourceLayer) :
    (Path.comp p₁ p₂ h hL).sourceLayer = p₁.sourceLayer := rfl

/-- Composition preserves target layer -/
theorem comp_targetLayer (p₁ p₂ : Path α) (h : p₁.target = p₂.source)
    (hL : p₁.targetLayer ≤ p₂.sourceLayer) :
    (Path.comp p₁ p₂ h hL).targetLayer = p₂.targetLayer := rfl

/-!
## Identity Laws
-/

/-- Left identity on source: refl ; p has same source as p -/
theorem refl_comp_source (p : Path α)
    (h : (Path.refl p.source p.sourceLayer).target = p.source)
    (hL : (Path.refl p.source p.sourceLayer).targetLayer ≤ p.sourceLayer) :
    (Path.comp (Path.refl p.source p.sourceLayer) p h hL).source = p.source := rfl

/-- Left identity on target: refl ; p has same target as p -/
theorem refl_comp_target (p : Path α)
    (h : (Path.refl p.source p.sourceLayer).target = p.source)
    (hL : (Path.refl p.source p.sourceLayer).targetLayer ≤ p.sourceLayer) :
    (Path.comp (Path.refl p.source p.sourceLayer) p h hL).target = p.target := rfl

/-- Left identity on loss: refl ; p has same loss as p -/
theorem refl_comp_loss (p : Path α)
    (h : (Path.refl p.source p.sourceLayer).target = p.source)
    (hL : (Path.refl p.source p.sourceLayer).targetLayer ≤ p.sourceLayer) :
    (Path.comp (Path.refl p.source p.sourceLayer) p h hL).loss.val = p.loss.val := by
  simp only [Path.comp, Path.refl]
  exact Loss.zero_compose p.loss

/-- Right identity on source: p ; refl has same source as p -/
theorem comp_refl_source (p : Path α)
    (h : p.target = (Path.refl p.target p.targetLayer).source)
    (hL : p.targetLayer ≤ (Path.refl p.target p.targetLayer).sourceLayer) :
    (Path.comp p (Path.refl p.target p.targetLayer) h hL).source = p.source := rfl

/-- Right identity on target: p ; refl has same target as p -/
theorem comp_refl_target (p : Path α)
    (h : p.target = (Path.refl p.target p.targetLayer).source)
    (hL : p.targetLayer ≤ (Path.refl p.target p.targetLayer).sourceLayer) :
    (Path.comp p (Path.refl p.target p.targetLayer) h hL).target = p.target := rfl

/-- Right identity on loss: p ; refl has same loss as p -/
theorem comp_refl_loss (p : Path α)
    (h : p.target = (Path.refl p.target p.targetLayer).source)
    (hL : p.targetLayer ≤ (Path.refl p.target p.targetLayer).sourceLayer) :
    (Path.comp p (Path.refl p.target p.targetLayer) h hL).loss.val = p.loss.val := by
  simp only [Path.comp, Path.refl]
  exact Loss.compose_zero p.loss

/-!
## Monotonicity Theorems
-/

/-- Loss is monotonic: p₁.loss ≤ (p₁ ; p₂).loss

    Proof: The composed loss is 1 - (1-a)(1-b).
    We need to show a ≤ 1 - (1-a)(1-b), i.e., (1-a)(1-b) ≤ 1-a.
    This follows since 0 ≤ 1-b ≤ 1 and 0 ≤ 1-a. -/
theorem loss_monotonic_left (p₁ p₂ : Path α) (h : p₁.target = p₂.source)
    (hL : p₁.targetLayer ≤ p₂.sourceLayer) :
    p₁.loss.val ≤ (Path.comp p₁ p₂ h hL).loss.val := by
  simp only [Path.comp, Loss.compose]
  -- Need to show: p₁.loss.val ≤ 1 - (1 - p₁.loss.val) * (1 - p₂.loss.val)
  -- Equivalently: (1 - p₁.loss.val) * (1 - p₂.loss.val) ≤ 1 - p₁.loss.val
  have h1 : 0 ≤ 1 - p₁.loss.val := by linarith [p₁.loss.bounded]
  have h2 : 1 - p₂.loss.val ≤ 1 := by linarith [p₂.loss.nonneg]
  have h3 : 0 ≤ 1 - p₂.loss.val := by linarith [p₂.loss.bounded]
  have key : (1 - p₁.loss.val) * (1 - p₂.loss.val) ≤ (1 - p₁.loss.val) * 1 := by
    apply mul_le_mul_of_nonneg_left h2 h1
  simp only [mul_one] at key
  linarith

/-- Loss is monotonic on the right: p₂.loss ≤ (p₁ ; p₂).loss -/
theorem loss_monotonic_right (p₁ p₂ : Path α) (h : p₁.target = p₂.source)
    (hL : p₁.targetLayer ≤ p₂.sourceLayer) :
    p₂.loss.val ≤ (Path.comp p₁ p₂ h hL).loss.val := by
  simp only [Path.comp, Loss.compose]
  have h1 : 0 ≤ 1 - p₂.loss.val := by linarith [p₂.loss.bounded]
  have h2 : 1 - p₁.loss.val ≤ 1 := by linarith [p₁.loss.nonneg]
  have h3 : 0 ≤ 1 - p₁.loss.val := by linarith [p₁.loss.bounded]
  have key : (1 - p₁.loss.val) * (1 - p₂.loss.val) ≤ 1 * (1 - p₂.loss.val) := by
    apply mul_le_mul_of_nonneg_right h2 h1
  simp only [one_mul] at key
  linarith

/-!
## Associativity of Path Composition (on loss values)
-/

/-- Path composition is associative on loss values -/
theorem comp_assoc_loss (p₁ p₂ p₃ : Path α)
    (h12 : p₁.target = p₂.source) (h23 : p₂.target = p₃.source)
    (hL12 : p₁.targetLayer ≤ p₂.sourceLayer) (hL23 : p₂.targetLayer ≤ p₃.sourceLayer)
    (hL12' : (Path.comp p₁ p₂ h12 hL12).targetLayer ≤ p₃.sourceLayer)
    (hL23' : p₁.targetLayer ≤ (Path.comp p₂ p₃ h23 hL23).sourceLayer) :
    (Path.comp (Path.comp p₁ p₂ h12 hL12) p₃
      (by simp only [Path.comp]; exact h23) hL12').loss.val =
    (Path.comp p₁ (Path.comp p₂ p₃ h23 hL23)
      (by simp only [Path.comp]; exact h12) hL23').loss.val := by
  simp only [Path.comp, Loss.compose]
  ring

/-!
## Layer Preservation Under Composition
-/

/-- Layer validity is preserved under composition -/
theorem comp_layer_valid (p₁ p₂ : Path α) (h : p₁.target = p₂.source)
    (hL : p₁.targetLayer ≤ p₂.sourceLayer) :
    (Path.comp p₁ p₂ h hL).sourceLayer ≤ (Path.comp p₁ p₂ h hL).targetLayer :=
  (Path.comp p₁ p₂ h hL).layerValid

/-!
## Special Cases
-/

/-- Composing with zero-loss path preserves loss on the left -/
theorem zero_loss_comp_left (p : Path α) (z : Path α)
    (hz : z.loss = Loss.zero)
    (h : z.target = p.source) (hL : z.targetLayer ≤ p.sourceLayer) :
    (Path.comp z p h hL).loss.val = p.loss.val := by
  simp only [Path.comp, hz, Loss.compose, Loss.zero]
  ring

/-- Composing with zero-loss path preserves loss on the right -/
theorem zero_loss_comp_right (p : Path α) (z : Path α)
    (hz : z.loss = Loss.zero)
    (h : p.target = z.source) (hL : p.targetLayer ≤ z.sourceLayer) :
    (Path.comp p z h hL).loss.val = p.loss.val := by
  simp only [Path.comp, hz, Loss.compose, Loss.zero]
  ring

end Kgents.DerivationPath
