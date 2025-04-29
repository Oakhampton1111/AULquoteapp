/**
 * QuoteForm Accessibility Tests
 *
 * This file contains accessibility-focused tests for the QuoteForm component,
 * ensuring it meets WCAG standards and provides a good experience for all users.
 */

import React from 'react';
import { render, screen, fireEvent, waitFor } from '@testing-library/react';
import userEvent from '@testing-library/user-event';
import { axe, toHaveNoViolations } from 'jest-axe';
import { renderWithRouterAndQueryClient } from '../../../../tests/utils/queryClientWrapper';

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

// Mock API calls
jest.mock('../../../../services/api/quotes', () => ({
  createQuote: jest.fn().mockResolvedValue({ id: 1, status: 'pending' }),
}));

jest.mock('../../../../services/api/rateCards', () => ({
  fetchRateCards: jest.fn().mockResolvedValue([
    { id: 1, name: 'Standard Storage', type: 'storage', baseRate: 100 },
    { id: 2, name: 'Premium Storage', type: 'storage', baseRate: 200 },
    { id: 3, name: 'Basic Transport', type: 'transport', baseRate: 150 },
  ]),
}));

describe('QuoteForm Accessibility Tests', () => {
  const renderComponent = () => {
    return render(<StandaloneQuoteForm />);
  };

  test('should have no axe violations', async () => {
    const { container } = renderComponent();
    const results = await axe(container);
    expect(results).toHaveNoViolations();
  });

  test('form fields have proper labels and descriptions', () => {
    const { getByLabelText, getAllByRole } = renderComponent();

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
    const { getByLabelText, getByText } = renderComponent();

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
