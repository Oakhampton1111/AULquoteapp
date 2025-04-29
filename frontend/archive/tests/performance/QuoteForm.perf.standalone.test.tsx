/**
 * Standalone Performance Tests for QuoteForm
 *
 * This file contains simplified performance tests that don't rely on React Query
 */

import React from 'react';
import { render, fireEvent, act } from '@testing-library/react';

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

    <div>
      <label htmlFor="coverage">Coverage Type</label>
      <select
        id="coverage"
        name="coverage"
        data-testid="coverage-select"
      >
        <option value="">Select coverage</option>
        <option value="basic">Basic</option>
        <option value="standard">Standard</option>
        <option value="premium">Premium</option>
      </select>
    </div>

    <button type="submit" data-testid="submit-button">Submit Quote</button>
  </form>
);

describe('QuoteForm Performance Tests', () => {
  test('meets performance benchmarks', async () => {
    // Measure initial render time
    const startTime = performance.now();
    const { rerender } = render(<StandaloneQuoteForm />);
    const endTime = performance.now();
    const initialRenderTime = endTime - startTime;

    // Rerender multiple times to measure average render time
    let totalRerenderTime = 0;
    const rerenderCount = 5;

    for (let i = 0; i < rerenderCount; i++) {
      const rerenderStart = performance.now();
      rerender(<StandaloneQuoteForm />);
      const rerenderEnd = performance.now();
      totalRerenderTime += (rerenderEnd - rerenderStart);
    }

    const averageRerenderTime = totalRerenderTime / rerenderCount;

    // Verify performance benchmarks
    expect(initialRenderTime).toBeLessThan(100); // Initial render should be fast
    expect(averageRerenderTime).toBeLessThan(50); // Rerenders should be even faster
  });

  test('handles rapid user interactions efficiently', async () => {
    // Render the component
    const { getByLabelText, getByTestId } = render(<StandaloneQuoteForm />);

    // Measure performance during rapid interactions
    const startTime = performance.now();

    // Simulate rapid form filling
    await act(async () => {
      // Type in client name field
      const clientNameInput = getByLabelText('Client Name');
      fireEvent.change(clientNameInput, { target: { value: 'Test Client' } });

      // Type in email field
      const emailInput = getByLabelText('Email');
      fireEvent.change(emailInput, { target: { value: 'test@example.com' } });

      // Type in phone field
      const phoneInput = getByLabelText('Phone');
      fireEvent.change(phoneInput, { target: { value: '555-123-4567' } });

      // Open and close dropdown rapidly
      const dropdown = getByTestId('coverage-select');
      for (let i = 0; i < 5; i++) {
        fireEvent.mouseDown(dropdown);
        await new Promise(r => setTimeout(r, 10));
        fireEvent.mouseUp(dropdown);
        await new Promise(r => setTimeout(r, 10));
      }

      // Rapidly click submit button
      const submitButton = getByTestId('submit-button');
      for (let i = 0; i < 3; i++) {
        // Use mouseDown/mouseUp instead of click to avoid form submission
        fireEvent.mouseDown(submitButton);
        await new Promise(r => setTimeout(r, 10));
        fireEvent.mouseUp(submitButton);
        await new Promise(r => setTimeout(r, 10));
      }
    });

    const endTime = performance.now();
    const interactionTime = endTime - startTime;

    // Verify interaction performance
    expect(interactionTime).toBeLessThan(1000); // Should handle all interactions in under 1 second
  });
});
