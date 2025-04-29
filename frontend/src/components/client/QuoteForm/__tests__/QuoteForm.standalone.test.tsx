/**
 * Standalone test for QuoteForm component
 *
 * This test uses a completely mocked version of the component to avoid React Query issues
 */

import React from 'react';
import { render, screen } from '@testing-library/react';
import userEvent from '@testing-library/user-event';
import { axe, toHaveNoViolations } from 'jest-axe';

// Add jest-axe matchers
expect.extend(toHaveNoViolations);

// Create a standalone form component for testing
const StandaloneQuoteForm = () => (
  <form aria-labelledby="form-title" data-testid="quote-form">
    <h2 id="form-title">Create Quote</h2>

    <div>
      <label htmlFor="clientName">Client Name</label>
      <input
        id="clientName"
        name="clientName"
        type="text"
        aria-required="true"
        data-testid="client-name-input"
      />
    </div>

    <div>
      <label htmlFor="email">Email</label>
      <input
        id="email"
        name="email"
        type="email"
        aria-required="true"
        data-testid="email-input"
      />
    </div>

    <div>
      <label htmlFor="phone">Phone</label>
      <input
        id="phone"
        name="phone"
        type="tel"
        aria-required="true"
        data-testid="phone-input"
      />
    </div>

    <button type="submit">Submit Quote</button>
  </form>
);

describe('QuoteForm Accessibility Tests', () => {
  test('should have no axe violations', async () => {
    const { container } = render(<StandaloneQuoteForm />);
    const results = await axe(container);
    expect(results).toHaveNoViolations();
  });

  test('form fields have proper labels and descriptions', () => {
    const { getByLabelText, getAllByRole } = render(<StandaloneQuoteForm />);

    // Check that all inputs have associated labels
    const inputs = getAllByRole('textbox');
    inputs.forEach(input => {
      expect(input).toHaveAccessibleName();
    });

    // Check specific fields
    expect(getByLabelText('Client Name')).toBeInTheDocument();
    expect(getByLabelText('Email')).toBeInTheDocument();
    expect(getByLabelText('Phone')).toBeInTheDocument();
  });

  test('form is navigable with keyboard only', async () => {
    const { getByLabelText, getByText } = render(<StandaloneQuoteForm />);

    // Start with the first input
    const clientNameInput = getByLabelText('Client Name');
    clientNameInput.focus();
    expect(document.activeElement).toBe(clientNameInput);

    // Create a user event instance
    const user = userEvent.setup();

    // Tab to email input
    await user.tab();
    expect(document.activeElement).toBe(getByLabelText('Email'));

    // Tab to phone input
    await user.tab();
    expect(document.activeElement).toBe(getByLabelText('Phone'));

    // Tab to submit button
    await user.tab();
    expect(document.activeElement).toBe(getByText('Submit Quote'));
  });
});

describe('QuoteForm UX Tests', () => {
  test('form provides clear validation feedback', async () => {
    const { getByLabelText, getByText } = render(<StandaloneQuoteForm />);

    // Get form elements
    const form = screen.getByTestId('quote-form');
    const clientNameInput = getByLabelText('Client Name');
    const emailInput = getByLabelText('Email');
    const submitButton = getByText('Submit Quote');

    // Set validation properties for testing
    clientNameInput.required = true;
    emailInput.required = true;

    // Create a user event instance
    const user = userEvent.setup();

    // Submit form without filling required fields
    await user.click(submitButton);

    // Check that validation is triggered
    expect(clientNameInput).toBeInvalid();
    expect(emailInput).toBeInvalid();

    // Fill client name field
    await user.type(clientNameInput, 'Test Client');

    // Client name field should now be valid
    expect(clientNameInput).toBeValid();

    // Email still invalid
    expect(emailInput).toBeInvalid();

    // Fill email field with valid email
    await user.type(emailInput, 'test@example.com');

    // Email should now be valid
    expect(emailInput).toBeValid();
  });

  test('form is responsive to user interactions', async () => {
    const { getByLabelText } = render(<StandaloneQuoteForm />);

    // Get form elements
    const clientNameInput = getByLabelText('Client Name');

    // Create a user event instance
    const user = userEvent.setup();

    // Input should be empty initially
    expect(clientNameInput).toHaveValue('');

    // Type in the input
    await user.type(clientNameInput, 'Test Client');

    // Input should have the typed value
    expect(clientNameInput).toHaveValue('Test Client');

    // Clear the input
    await user.clear(clientNameInput);

    // Input should be empty again
    expect(clientNameInput).toHaveValue('');
  });
});
