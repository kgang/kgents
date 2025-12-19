/**
 * Forms Components Index
 *
 * Exports the Aspect Form Projection Protocol components.
 *
 * @see spec/protocols/aspect-form-projection.md
 * @see docs/skills/aspect-form-projection.md
 */

// Main orchestrator
export { AspectForm } from './AspectForm';
export type { AspectFormProps } from './AspectForm';

// Field dispatch
export { ProjectedField } from './ProjectedField';
export type { ProjectedFieldProps, FieldComponentProps } from './ProjectedField';

// Field chrome
export { FieldWrapper } from './FieldWrapper';
export type { FieldWrapperProps } from './FieldWrapper';

// Primitive fields
export * from './fields';
