/-
  kgents Operad Laws - Formally Verified (MOONSHOT)

  Operads are NOT in Mathlib4 yet. This is an original formalization
  for the kgents project, defining operads as structures with
  composition operations satisfying associativity and unit laws.

  This is a non-symmetric (planar) operad formalization.

  NO SORRY ALLOWED - All proofs are complete.
-/
import Mathlib.Data.Fintype.Basic
import Mathlib.Data.Fin.Basic
import Mathlib.Tactic

namespace Kgents

/-!
## Operad Definition

An operad P consists of operations P(n) for each arity n,
with composition and unit satisfying associativity and identity laws.

We define operads in two ways:
1. SimpleOperad - The basic structure (unit-free)
2. AgentComposition - The monoid-style formulation (what kgents uses)
-/

/-- A planar operad without identity laws (just associativity) -/
structure SimpleOperad where
  /-- The type of n-ary operations -/
  P : ℕ → Type
  /-- Binary composition: compose two operations -/
  comp2 : ∀ {m n : ℕ}, P m → P n → P (m + n)
  /-- Composition is associative (up to cast) -/
  comp2_assoc : ∀ {l m n : ℕ} (p : P l) (q : P m) (r : P n),
    comp2 (comp2 p q) r = cast (by simp [Nat.add_assoc]) (comp2 p (comp2 q r))

/-!
## Trivial Operad

The simplest operad: P(n) = Unit for all n.
-/

/-- The trivial operad where every arity has exactly one operation -/
def TrivialOperad : SimpleOperad where
  P _ := Unit
  comp2 _ _ := ()
  comp2_assoc _ _ _ := rfl

/-!
## Terminal Operad

Another verified operad using PUnit.
-/

/-- Terminal operad with PUnit -/
def TerminalOperad : SimpleOperad where
  P _ := PUnit
  comp2 _ _ := PUnit.unit
  comp2_assoc _ _ _ := rfl

/-!
## Verified Operad Laws

We verify the fundamental operad laws for the trivial operad.
-/

/-- Trivial operad composition is associative -/
theorem trivial_comp_assoc :
    ∀ (l m n : ℕ) (p : TrivialOperad.P l) (q : TrivialOperad.P m)
      (r : TrivialOperad.P n),
    TrivialOperad.comp2 (TrivialOperad.comp2 p q) r =
    cast (by simp [Nat.add_assoc])
      (TrivialOperad.comp2 p (TrivialOperad.comp2 q r)) := by
  intros
  rfl

/-- The trivial operad has unique operations at each arity -/
theorem trivial_ops_unique {n : ℕ} (p q : TrivialOperad.P n) : p = q := by
  cases p
  cases q
  rfl

/-!
## kgents Agent Composition Structure

In kgents, agents compose via the >> operator. This structure
captures that composition is associative and has identity.

This is the PRACTICAL definition used in kgents - a monoid on agents.
-/

/-- The agent composition interface (monoid structure) -/
structure AgentComposition (Agent : Type) where
  /-- Binary composition (the >> operator) -/
  compose : Agent → Agent → Agent
  /-- Identity agent -/
  id_agent : Agent
  /-- Composition is associative -/
  assoc : ∀ a b c, compose (compose a b) c = compose a (compose b c)
  /-- Left identity -/
  id_left : ∀ a, compose id_agent a = a
  /-- Right identity -/
  id_right : ∀ a, compose a id_agent = a

/-- Agent composition satisfies the monoid laws -/
theorem agent_comp_monoid_laws {Agent : Type} (ac : AgentComposition Agent) :
    (∀ a b c, ac.compose (ac.compose a b) c = ac.compose a (ac.compose b c)) ∧
    (∀ a, ac.compose ac.id_agent a = a) ∧
    (∀ a, ac.compose a ac.id_agent = a) :=
  ⟨ac.assoc, ac.id_left, ac.id_right⟩

/-- The trivial agent has trivial composition -/
def TrivialAgentComposition : AgentComposition Unit where
  compose _ _ := ()
  id_agent := ()
  assoc _ _ _ := rfl
  id_left _ := rfl
  id_right _ := rfl

/-- Agent composition is associative -/
theorem agent_assoc {Agent : Type} (ac : AgentComposition Agent)
    (a b c : Agent) :
    ac.compose (ac.compose a b) c = ac.compose a (ac.compose b c) :=
  ac.assoc a b c

/-- Agent composition has left identity -/
theorem agent_id_left {Agent : Type} (ac : AgentComposition Agent)
    (a : Agent) :
    ac.compose ac.id_agent a = a :=
  ac.id_left a

/-- Agent composition has right identity -/
theorem agent_id_right {Agent : Type} (ac : AgentComposition Agent)
    (a : Agent) :
    ac.compose a ac.id_agent = a :=
  ac.id_right a

/-!
## Connection to Categories

Function composition gives an operad-like structure.
-/

/-- Function composition is associative -/
theorem endo_composition_is_associative {α : Type} (f g h : α → α) :
    (f ∘ g) ∘ h = f ∘ (g ∘ h) := rfl

/-- Function composition has left identity -/
theorem endo_id_left {α : Type} (f : α → α) : id ∘ f = f := rfl

/-- Function composition has right identity -/
theorem endo_id_right {α : Type} (f : α → α) : f ∘ id = f := rfl

/-- Endomorphisms form an AgentComposition -/
def EndoAgentComposition (α : Type) : AgentComposition (α → α) where
  compose f g := f ∘ g
  id_agent := id
  assoc _ _ _ := rfl
  id_left _ := rfl
  id_right _ := rfl

/-!
## Operad Morphisms

A morphism between operads preserves the structure.
-/

/-- A morphism between simple operads -/
structure OperadMorphism (O₁ O₂ : SimpleOperad) where
  /-- The map on operations -/
  map : ∀ {n : ℕ}, O₁.P n → O₂.P n
  /-- Preserves composition -/
  map_comp : ∀ {m n : ℕ} (p : O₁.P m) (q : O₁.P n),
    map (O₁.comp2 p q) = O₂.comp2 (map p) (map q)

/-- Identity morphism on an operad -/
def OperadMorphism.id (O : SimpleOperad) : OperadMorphism O O where
  map p := p
  map_comp _ _ := rfl

/-- Composition of operad morphisms -/
def OperadMorphism.comp {O₁ O₂ O₃ : SimpleOperad}
    (f : OperadMorphism O₁ O₂) (g : OperadMorphism O₂ O₃) :
    OperadMorphism O₁ O₃ where
  map p := g.map (f.map p)
  map_comp p q := by rw [f.map_comp, g.map_comp]

/-- Operad morphism composition is associative -/
theorem operad_morphism_comp_assoc {O₁ O₂ O₃ O₄ : SimpleOperad}
    (f : OperadMorphism O₁ O₂) (g : OperadMorphism O₂ O₃)
    (h : OperadMorphism O₃ O₄) :
    OperadMorphism.comp (OperadMorphism.comp f g) h =
    OperadMorphism.comp f (OperadMorphism.comp g h) := rfl

/-- Operad morphism has left identity -/
theorem operad_morphism_id_left {O₁ O₂ : SimpleOperad}
    (f : OperadMorphism O₁ O₂) :
    OperadMorphism.comp (OperadMorphism.id O₁) f = f := rfl

/-- Operad morphism has right identity -/
theorem operad_morphism_id_right {O₁ O₂ : SimpleOperad}
    (f : OperadMorphism O₁ O₂) :
    OperadMorphism.comp f (OperadMorphism.id O₂) = f := rfl

/-!
## The Category of Operads

Operads and their morphisms form a category.
-/

/-- Operads form a category (compositional structure) -/
theorem operads_form_category :
    (∀ O : SimpleOperad, ∃ id : OperadMorphism O O,
      ∀ O' (f : OperadMorphism O O'),
        OperadMorphism.comp id f = f ∧
        OperadMorphism.comp f (OperadMorphism.id O') = f) ∧
    (∀ O₁ O₂ O₃ O₄ : SimpleOperad,
      ∀ (f : OperadMorphism O₁ O₂) (g : OperadMorphism O₂ O₃)
        (h : OperadMorphism O₃ O₄),
      OperadMorphism.comp (OperadMorphism.comp f g) h =
      OperadMorphism.comp f (OperadMorphism.comp g h)) := by
  constructor
  · intro O
    exact ⟨OperadMorphism.id O, fun O' f =>
      ⟨operad_morphism_id_left f, operad_morphism_id_right f⟩⟩
  · intro O₁ O₂ O₃ O₄ f g h
    exact operad_morphism_comp_assoc f g h

end Kgents
