/-
  kgents Natural Transformation Laws - Formally Verified

  Natural transformations satisfy the naturality condition, ensuring
  the transformation commutes with morphism mapping.

  NO SORRY ALLOWED - All proofs are complete.
-/
import Mathlib.CategoryTheory.NatTrans
import Mathlib.CategoryTheory.Functor.Category

namespace Kgents

open CategoryTheory

universe u₁ v₁ u₂ v₂

/-!
## Naturality

The fundamental property of natural transformations.
-/

/-- Naturality square: F.map f ≫ η.app Y = η.app X ≫ G.map f -/
theorem naturality {C : Type u₁} [Category.{v₁} C] {D : Type u₂} [Category.{v₂} D]
    {F G : C ⥤ D} (η : F ⟶ G) {X Y : C} (f : X ⟶ Y) :
    F.map f ≫ η.app Y = η.app X ≫ G.map f := by
  exact η.naturality f

/-- Naturality in the opposite direction -/
theorem naturality' {C : Type u₁} [Category.{v₁} C] {D : Type u₂} [Category.{v₂} D]
    {F G : C ⥤ D} (η : F ⟶ G) {X Y : C} (f : X ⟶ Y) :
    η.app X ≫ G.map f = F.map f ≫ η.app Y := by
  exact (η.naturality f).symm

/-!
## Identity Natural Transformation

The identity natural transformation is the identity on each component.
-/

/-- Identity natural transformation component -/
theorem id_nat_trans_app {C : Type u₁} [Category.{v₁} C] {D : Type u₂} [Category.{v₂} D]
    (F : C ⥤ D) (X : C) :
    (𝟙 F : F ⟶ F).app X = 𝟙 (F.obj X) := rfl

/-!
## Vertical Composition

Natural transformations compose vertically.
-/

/-- Vertical composition of natural transformations -/
theorem vcomp_app {C : Type u₁} [Category.{v₁} C] {D : Type u₂} [Category.{v₂} D]
    {F G H : C ⥤ D} (α : F ⟶ G) (β : G ⟶ H) (X : C) :
    (α ≫ β).app X = α.app X ≫ β.app X := rfl

/-- Vertical composition is associative -/
theorem vcomp_assoc {C : Type u₁} [Category.{v₁} C] {D : Type u₂} [Category.{v₂} D]
    {F G H K : C ⥤ D} (α : F ⟶ G) (β : G ⟶ H) (γ : H ⟶ K) (X : C) :
    ((α ≫ β) ≫ γ).app X = (α ≫ (β ≫ γ)).app X := by
  simp only [vcomp_app, Category.assoc]

/-- Vertical composition left identity -/
theorem vcomp_id_left {C : Type u₁} [Category.{v₁} C] {D : Type u₂} [Category.{v₂} D]
    {F G : C ⥤ D} (α : F ⟶ G) (X : C) :
    ((𝟙 F) ≫ α).app X = α.app X := by
  simp

/-- Vertical composition right identity -/
theorem vcomp_id_right {C : Type u₁} [Category.{v₁} C] {D : Type u₂} [Category.{v₂} D]
    {F G : C ⥤ D} (α : F ⟶ G) (X : C) :
    (α ≫ (𝟙 G)).app X = α.app X := by
  simp

/-!
## Horizontal Composition (Whiskering)

Natural transformations can be composed horizontally with functors.
-/

/-- Left whiskering preserves naturality -/
theorem whisker_left_naturality {C D E : Type*} [Category C] [Category D] [Category E]
    (H : E ⥤ C) {F G : C ⥤ D} (α : F ⟶ G) {X Y : E} (f : X ⟶ Y) :
    (H ⋙ F).map f ≫ α.app (H.obj Y) = α.app (H.obj X) ≫ (H ⋙ G).map f := by
  exact α.naturality (H.map f)

/-- Right whiskering preserves naturality -/
theorem whisker_right_naturality {C D E : Type*} [Category C] [Category D] [Category E]
    {F G : C ⥤ D} (α : F ⟶ G) (H : D ⥤ E) {X Y : C} (f : X ⟶ Y) :
    (F ⋙ H).map f ≫ H.map (α.app Y) = H.map (α.app X) ≫ (G ⋙ H).map f := by
  simp only [Functor.comp_map]
  rw [← H.map_comp, ← H.map_comp, α.naturality]

end Kgents
