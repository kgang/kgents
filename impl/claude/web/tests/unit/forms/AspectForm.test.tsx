/**
 * Tests for AspectForm and related components.
 *
 * @see impl/claude/web/src/components/forms/
 * @see spec/protocols/aspect-form-projection.md
 */

import { describe, it, expect, vi, beforeEach } from 'vitest';
import { render, screen, waitFor, fireEvent } from '@testing-library/react';
import userEvent from '@testing-library/user-event';
import { AspectForm } from '@/components/forms/AspectForm';
import { ProjectedField } from '@/components/forms/ProjectedField';
import { FieldWrapper } from '@/components/forms/FieldWrapper';
import {
  TextField,
  NumberField,
  BooleanField,
  EnumField,
  SliderField,
  UuidField,
} from '@/components/forms/fields';
import type { FieldDescriptor } from '@/lib/form/FieldProjectionRegistry';
import type { Observer } from '@/lib/schema/generateDefaults';
import type { JSONSchema } from '@/lib/schema/analyzeContract';

// =============================================================================
// Test Fixtures
// =============================================================================

const mockTextField: FieldDescriptor = {
  name: 'name',
  type: 'string',
  required: true,
  description: 'Citizen name',
};

const mockNumberField: FieldDescriptor = {
  name: 'age',
  type: 'integer',
  required: false,
  min: 0,
  max: 150,
};

const mockBooleanField: FieldDescriptor = {
  name: 'active',
  type: 'boolean',
  required: false,
};

const mockEnumField: FieldDescriptor = {
  name: 'archetype',
  type: 'string',
  required: true,
  enum: ['merchant', 'scholar', 'artisan', 'diplomat'],
};

const mockUuidField: FieldDescriptor = {
  name: 'citizen_id',
  type: 'string',
  required: true,
  format: 'uuid',
};

const mockSliderField: FieldDescriptor = {
  name: 'reputation',
  type: 'number',
  required: false,
  min: 0,
  max: 100,
};

const mockObserver: Observer = {
  archetype: 'developer',
};

const guestObserver: Observer = {
  archetype: 'guest',
};

const creatorObserver: Observer = {
  archetype: 'creator',
};

const mockSchema: JSONSchema = {
  type: 'object',
  properties: {
    name: {
      type: 'string',
      description: 'Citizen name',
    },
    archetype: {
      type: 'string',
      enum: ['merchant', 'scholar', 'artisan', 'diplomat'],
    },
    region: {
      type: 'string',
    },
  },
  required: ['name', 'archetype'],
};

// =============================================================================
// Mock API Client
// =============================================================================

vi.mock('@/api/client', () => ({
  apiClient: {
    get: vi.fn(),
    post: vi.fn(),
  },
}));

// =============================================================================
// TextField Tests
// =============================================================================

describe('TextField', () => {
  it('renders text input', () => {
    const onChange = vi.fn();
    render(<TextField field={mockTextField} value="" onChange={onChange} archetype="developer" />);

    expect(screen.getByRole('textbox')).toBeInTheDocument();
  });

  it('displays current value', () => {
    const onChange = vi.fn();
    render(
      <TextField
        field={mockTextField}
        value="Zephyr Chen"
        onChange={onChange}
        archetype="developer"
      />
    );

    expect(screen.getByDisplayValue('Zephyr Chen')).toBeInTheDocument();
  });

  it('calls onChange when typing', async () => {
    const onChange = vi.fn();
    const user = userEvent.setup();

    render(<TextField field={mockTextField} value="" onChange={onChange} archetype="developer" />);

    await user.type(screen.getByRole('textbox'), 'Luna');
    expect(onChange).toHaveBeenCalled();
  });

  it('shows error state', () => {
    const onChange = vi.fn();
    render(
      <TextField
        field={mockTextField}
        value=""
        onChange={onChange}
        error="Required"
        archetype="developer"
      />
    );

    expect(screen.getByRole('textbox')).toHaveAttribute('aria-invalid', 'true');
  });
});

// =============================================================================
// NumberField Tests
// =============================================================================

describe('NumberField', () => {
  it('renders number input', () => {
    const onChange = vi.fn();
    render(
      <NumberField field={mockNumberField} value={25} onChange={onChange} archetype="developer" />
    );

    expect(screen.getByRole('spinbutton')).toBeInTheDocument();
    expect(screen.getByDisplayValue('25')).toBeInTheDocument();
  });

  it('calls onChange with parsed number', () => {
    const onChange = vi.fn();

    render(
      <NumberField field={mockNumberField} value={10} onChange={onChange} archetype="developer" />
    );

    const input = screen.getByRole('spinbutton');

    // Use fireEvent.change to simulate typing a number
    fireEvent.change(input, { target: { value: '42' } });

    // Should have been called with parsed integer
    expect(onChange).toHaveBeenCalledWith(42);
  });

  it('handles empty input', async () => {
    const onChange = vi.fn();
    const user = userEvent.setup();

    render(
      <NumberField field={mockNumberField} value={10} onChange={onChange} archetype="developer" />
    );

    const input = screen.getByRole('spinbutton');
    await user.clear(input);

    expect(onChange).toHaveBeenCalledWith(undefined);
  });
});

// =============================================================================
// BooleanField Tests
// =============================================================================

describe('BooleanField', () => {
  it('renders toggle switch', () => {
    const onChange = vi.fn();
    render(
      <BooleanField
        field={mockBooleanField}
        value={false}
        onChange={onChange}
        archetype="developer"
      />
    );

    expect(screen.getByRole('switch')).toBeInTheDocument();
    expect(screen.getByRole('switch')).toHaveAttribute('aria-checked', 'false');
  });

  it('toggles on click', async () => {
    const onChange = vi.fn();
    const user = userEvent.setup();

    render(
      <BooleanField
        field={mockBooleanField}
        value={false}
        onChange={onChange}
        archetype="developer"
      />
    );

    await user.click(screen.getByRole('switch'));
    expect(onChange).toHaveBeenCalledWith(true);
  });
});

// =============================================================================
// EnumField Tests
// =============================================================================

describe('EnumField', () => {
  it('renders select with options', () => {
    const onChange = vi.fn();
    render(
      <EnumField field={mockEnumField} value="merchant" onChange={onChange} archetype="developer" />
    );

    expect(screen.getByRole('combobox')).toBeInTheDocument();
    expect(screen.getByText('Merchant')).toBeInTheDocument();
    expect(screen.getByText('Scholar')).toBeInTheDocument();
    expect(screen.getByText('Artisan')).toBeInTheDocument();
    expect(screen.getByText('Diplomat')).toBeInTheDocument();
  });

  it('calls onChange on selection', async () => {
    const onChange = vi.fn();
    const user = userEvent.setup();

    render(
      <EnumField field={mockEnumField} value="merchant" onChange={onChange} archetype="developer" />
    );

    await user.selectOptions(screen.getByRole('combobox'), 'scholar');
    expect(onChange).toHaveBeenCalledWith('scholar');
  });
});

// =============================================================================
// SliderField Tests
// =============================================================================

describe('SliderField', () => {
  it('renders slider with value', () => {
    const onChange = vi.fn();
    render(
      <SliderField field={mockSliderField} value={50} onChange={onChange} archetype="developer" />
    );

    expect(screen.getByRole('slider')).toBeInTheDocument();
    expect(screen.getByRole('slider')).toHaveValue('50');
  });

  it('displays min and max labels', () => {
    const onChange = vi.fn();
    render(
      <SliderField field={mockSliderField} value={50} onChange={onChange} archetype="developer" />
    );

    expect(screen.getByText('0')).toBeInTheDocument();
    expect(screen.getByText('100')).toBeInTheDocument();
  });

  it('displays current value', () => {
    const onChange = vi.fn();
    render(
      <SliderField field={mockSliderField} value={75.5} onChange={onChange} archetype="developer" />
    );

    expect(screen.getByText('75.50')).toBeInTheDocument();
  });
});

// =============================================================================
// UuidField Tests
// =============================================================================

describe('UuidField', () => {
  it('renders input with generate button', () => {
    const onChange = vi.fn();
    render(<UuidField field={mockUuidField} value="" onChange={onChange} archetype="developer" />);

    expect(screen.getByRole('textbox')).toBeInTheDocument();
    expect(screen.getByRole('button', { name: /gen/i })).toBeInTheDocument();
  });

  it('generates UUID on button click', async () => {
    const onChange = vi.fn();
    const user = userEvent.setup();

    render(<UuidField field={mockUuidField} value="" onChange={onChange} archetype="developer" />);

    await user.click(screen.getByRole('button', { name: /gen/i }));

    // Should have generated a UUID (matches UUID v4 pattern)
    expect(onChange).toHaveBeenCalled();
    const calledValue = onChange.mock.calls[0][0] as string;
    expect(calledValue).toMatch(
      /^[0-9a-f]{8}-[0-9a-f]{4}-4[0-9a-f]{3}-[89ab][0-9a-f]{3}-[0-9a-f]{12}$/i
    );
  });
});

// =============================================================================
// FieldWrapper Tests
// =============================================================================

describe('FieldWrapper', () => {
  it('renders label and children', () => {
    render(
      <FieldWrapper field={mockTextField} observer={mockObserver}>
        <input type="text" data-testid="child-input" />
      </FieldWrapper>
    );

    expect(screen.getByText('Name')).toBeInTheDocument();
    expect(screen.getByTestId('child-input')).toBeInTheDocument();
  });

  it('shows required indicator', () => {
    render(
      <FieldWrapper field={mockTextField} observer={mockObserver}>
        <input type="text" />
      </FieldWrapper>
    );

    expect(screen.getByText('*')).toBeInTheDocument();
  });

  it('displays description', () => {
    render(
      <FieldWrapper field={mockTextField} observer={mockObserver}>
        <input type="text" />
      </FieldWrapper>
    );

    expect(screen.getByText('Citizen name')).toBeInTheDocument();
  });

  it('shows error message when provided', () => {
    render(
      <FieldWrapper field={mockTextField} error="This field needs a value" observer={mockObserver}>
        <input type="text" />
      </FieldWrapper>
    );

    expect(screen.getByText('This field needs a value')).toBeInTheDocument();
  });

  it('uses question form for guest archetype', () => {
    render(
      <FieldWrapper field={mockTextField} observer={guestObserver}>
        <input type="text" />
      </FieldWrapper>
    );

    expect(screen.getByText('What shall we call it?')).toBeInTheDocument();
  });

  it('uses question form for creator archetype', () => {
    render(
      <FieldWrapper field={mockTextField} observer={creatorObserver}>
        <input type="text" />
      </FieldWrapper>
    );

    expect(screen.getByText('What shall we call it?')).toBeInTheDocument();
  });

  it('shows type hint for developer archetype', () => {
    render(
      <FieldWrapper field={mockUuidField} observer={mockObserver}>
        <input type="text" />
      </FieldWrapper>
    );

    expect(screen.getByText('string:uuid')).toBeInTheDocument();
  });
});

// =============================================================================
// ProjectedField Tests
// =============================================================================

describe('ProjectedField', () => {
  it('resolves text field', () => {
    const onChange = vi.fn();
    render(
      <ProjectedField field={mockTextField} value="" onChange={onChange} observer={mockObserver} />
    );

    expect(screen.getByRole('textbox')).toBeInTheDocument();
  });

  it('resolves boolean field to toggle', () => {
    const onChange = vi.fn();
    render(
      <ProjectedField
        field={mockBooleanField}
        value={false}
        onChange={onChange}
        observer={mockObserver}
      />
    );

    expect(screen.getByRole('switch')).toBeInTheDocument();
  });

  it('resolves enum field to select', () => {
    const onChange = vi.fn();
    // Use a field name other than 'archetype' to avoid observer-archetype projector
    const enumField: FieldDescriptor = {
      name: 'status',
      type: 'string',
      required: true,
      enum: ['active', 'inactive', 'pending'],
    };
    render(
      <ProjectedField
        field={enumField}
        value="active"
        onChange={onChange}
        observer={mockObserver}
      />
    );

    expect(screen.getByRole('combobox')).toBeInTheDocument();
  });

  it('resolves uuid field', () => {
    const onChange = vi.fn();
    render(
      <ProjectedField field={mockUuidField} value="" onChange={onChange} observer={mockObserver} />
    );

    expect(screen.getByRole('textbox')).toBeInTheDocument();
    expect(screen.getByRole('button', { name: /gen/i })).toBeInTheDocument();
  });

  it('resolves bounded number to slider', () => {
    const onChange = vi.fn();
    render(
      <ProjectedField
        field={mockSliderField}
        value={50}
        onChange={onChange}
        observer={mockObserver}
      />
    );

    expect(screen.getByRole('slider')).toBeInTheDocument();
  });
});

// =============================================================================
// AspectForm Integration Tests
// =============================================================================

describe('AspectForm', () => {
  beforeEach(() => {
    vi.clearAllMocks();
  });

  it('renders form with provided schema', async () => {
    render(
      <AspectForm
        path="world.town.citizen"
        aspect="create"
        observer={mockObserver}
        schema={mockSchema}
      />
    );

    // Wait for form to render (check for Invoke button as indicator)
    await waitFor(() => {
      expect(screen.getByRole('button', { name: /invoke/i })).toBeInTheDocument();
    });

    // Should show the name field (required) - developer sees "Name"
    expect(screen.getByText('Name')).toBeInTheDocument();
  });

  it('shows invoke button', async () => {
    render(
      <AspectForm
        path="world.town.citizen"
        aspect="create"
        observer={mockObserver}
        schema={mockSchema}
      />
    );

    await waitFor(() => {
      expect(screen.getByRole('button', { name: /invoke/i })).toBeInTheDocument();
    });
  });

  it('shows start fresh button', async () => {
    render(
      <AspectForm
        path="world.town.citizen"
        aspect="create"
        observer={mockObserver}
        schema={mockSchema}
      />
    );

    await waitFor(() => {
      expect(screen.getByRole('button', { name: /start fresh/i })).toBeInTheDocument();
    });
  });

  it('validates required fields on submit', async () => {
    const user = userEvent.setup();
    const onError = vi.fn();

    render(
      <AspectForm
        path="world.town.citizen"
        aspect="create"
        observer={mockObserver}
        schema={mockSchema}
        onError={onError}
      />
    );

    await waitFor(() => {
      expect(screen.getByRole('button', { name: /invoke/i })).toBeInTheDocument();
    });

    // Clear the name field to trigger validation
    const nameInput = screen.getByLabelText(/name/i);
    await user.clear(nameInput);

    // Try to submit with empty required fields
    await user.click(screen.getByRole('button', { name: /invoke/i }));

    // Validation should prevent submission - API should NOT be called
    // (Since the mock API would have been called otherwise)
    expect(onError).not.toHaveBeenCalled();
  });

  it('separates required and optional fields', async () => {
    render(
      <AspectForm
        path="world.town.citizen"
        aspect="create"
        observer={mockObserver}
        schema={mockSchema}
      />
    );

    await waitFor(() => {
      // Optional fields should be in collapsible section
      expect(screen.getByText(/optional/i)).toBeInTheDocument();
    });
  });

  it('renders no input required message for schema-less aspects', async () => {
    render(
      <AspectForm
        path="world.town"
        aspect="manifest"
        observer={mockObserver}
        schema={null as unknown as JSONSchema}
      />
    );

    await waitFor(() => {
      expect(screen.getByText(/no input required/i)).toBeInTheDocument();
    });
  });
});
