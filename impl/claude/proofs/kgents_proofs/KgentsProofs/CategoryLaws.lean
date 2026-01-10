/-
  kgents Categorical Laws - Formally Verified

  These theorems extract the fundamental categorical laws from Mathlib's
  Category structure and provide explicit witnesses for kgents verification.

  NO SORRY ALLOWED - All proofs are complete.
-/
import Mathlib.CategoryTheory.Category.Basic

namespace Kgents

open CategoryTheory

universe u v

/-!
## Composition Laws

The three fundamental laws of category composition.
-/

/-- Composition is associative: (f ≫ g) ≫ h = f ≫ (g ≫ h) -/
theorem comp_assoc {C : Type u} [Category.{v} C] {W X Y Z : C}
    (f : W ⟶ X) (g : X ⟶ Y) (h : Y ⟶ Z) :
    (f ≫ g) ≫ h = f ≫ (g ≫ h) := by
  exact Category.assoc f g h

/-- Left identity: 𝟙 X ≫ f = f -/
theorem id_comp {C : Type u} [Category.{v} C] {X Y : C}
    (f : X ⟶ Y) :
    𝟙 X ≫ f = f := by
  exact Category.id_comp f

/-- Right identity: f ≫ 𝟙 Y = f -/
theorem comp_id {C : Type u} [Category.{v} C] {X Y : C}
    (f : X ⟶ Y) :
    f ≫ 𝟙 Y = f := by
  exact Category.comp_id f

/-!
## Derived Laws

Additional useful lemmas derived from the fundamental laws.
-/

/-- Left cancellation: if e ≫ f = f and f is a morphism, e acts like identity on f -/
theorem left_cancel_id {C : Type u} [Category.{v} C] {X Y : C}
    (e : X ⟶ X) (f : X ⟶ Y) (h : e ≫ f = f) :
    e ≫ f = f := h

/-- Composition of three morphisms (explicit associativity witness) -/
theorem comp_three {C : Type u} [Category.{v} C] {V W X Y Z : C}
    (f : V ⟶ W) (g : W ⟶ X) (h : X ⟶ Y) (k : Y ⟶ Z) :
    ((f ≫ g) ≫ h) ≫ k = f ≫ (g ≫ (h ≫ k)) := by
  simp only [Category.assoc]

/-- Identity composed with identity is identity -/
theorem id_comp_id {C : Type u} [Category.{v} C] {X : C} :
    (𝟙 X) ≫ (𝟙 X) = 𝟙 X := by
  simp

end Kgents
