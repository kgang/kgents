/-
  kgents Functor Laws - Formally Verified

  Functors preserve the categorical structure: identity and composition.
  These theorems extract functor laws from Mathlib's Functor structure.

  NO SORRY ALLOWED - All proofs are complete.
-/
import Mathlib.CategoryTheory.Functor.Basic

namespace Kgents

open CategoryTheory

universe u₁ v₁ u₂ v₂

/-!
## Functor Preservation Laws

Functors must preserve identity and composition.
-/

/-- Functors preserve identity: F.map (𝟙 X) = 𝟙 (F.obj X) -/
theorem functor_map_id {C : Type u₁} [Category.{v₁} C] {D : Type u₂} [Category.{v₂} D]
    (F : C ⥤ D) (X : C) :
    F.map (𝟙 X) = 𝟙 (F.obj X) := by
  exact F.map_id X

/-- Functors preserve composition: F.map (f ≫ g) = F.map f ≫ F.map g -/
theorem functor_map_comp {C : Type u₁} [Category.{v₁} C] {D : Type u₂} [Category.{v₂} D]
    (F : C ⥤ D) {X Y Z : C} (f : X ⟶ Y) (g : Y ⟶ Z) :
    F.map (f ≫ g) = F.map f ≫ F.map g := by
  exact F.map_comp f g

/-!
## Functor Composition Laws

Functors compose, and composition respects the functor laws.
-/

/-- Identity functor preserves objects -/
theorem id_functor_obj {C : Type u₁} [Category.{v₁} C] (X : C) :
    (𝟭 C).obj X = X := rfl

/-- Identity functor preserves morphisms -/
theorem id_functor_map {C : Type u₁} [Category.{v₁} C] {X Y : C} (f : X ⟶ Y) :
    (𝟭 C).map f = f := rfl

/-- Functor composition on objects -/
theorem comp_functor_obj {C : Type u₁} [Category.{v₁} C]
    {D : Type u₂} [Category.{v₂} D]
    {E : Type*} [Category E]
    (F : C ⥤ D) (G : D ⥤ E) (X : C) :
    (F ⋙ G).obj X = G.obj (F.obj X) := rfl

/-- Functor composition on morphisms -/
theorem comp_functor_map {C : Type u₁} [Category.{v₁} C]
    {D : Type u₂} [Category.{v₂} D]
    {E : Type*} [Category E]
    (F : C ⥤ D) (G : D ⥤ E) {X Y : C} (f : X ⟶ Y) :
    (F ⋙ G).map f = G.map (F.map f) := rfl

/-!
## Functor Composition Associativity

Functor composition is associative.
-/

/-- Functor composition is associative on objects -/
theorem functor_assoc_obj {C D E F : Type*} [Category C] [Category D] [Category E] [Category F]
    (G : C ⥤ D) (H : D ⥤ E) (K : E ⥤ F) (X : C) :
    ((G ⋙ H) ⋙ K).obj X = (G ⋙ (H ⋙ K)).obj X := rfl

/-- Functor composition is associative on morphisms -/
theorem functor_assoc_map {C D E F : Type*} [Category C] [Category D] [Category E] [Category F]
    (G : C ⥤ D) (H : D ⥤ E) (K : E ⥤ F) {X Y : C} (f : X ⟶ Y) :
    ((G ⋙ H) ⋙ K).map f = (G ⋙ (H ⋙ K)).map f := rfl

end Kgents
