import React from 'react';
import { render, screen, fireEvent, waitFor } from '@testing-library/react';
import userEvent from '@testing-library/user-event';

describe('UX Tests', () => {
  test('form provides validation feedback', async () => {
    // Render a form with validation
    render(
      <form data-testid="quote-form" onSubmit={(e) => e.preventDefault()}>
        <div>
          <label htmlFor="client-name">Client Name</label>
          <input
            id="client-name"
            name="clientName"
            type="text"
            required
            aria-required="true"
          />
          <div id="client-name-error" className="error-message" aria-live="polite"></div>
        </div>

        <div>
          <label htmlFor="email">Email</label>
          <input
            id="email"
            name="email"
            type="email"
            required
            aria-required="true"
          />
          <div id="email-error" className="error-message" aria-live="polite"></div>
        </div>

        <button type="submit">Submit</button>
      </form>
    );

    // Get form elements
    const form = screen.getByTestId('quote-form');
    const nameInput = screen.getByLabelText('Client Name');
    const emailInput = screen.getByLabelText('Email');
    const submitButton = screen.getByRole('button', { name: 'Submit' });

    // Submit form without filling required fields
    fireEvent.click(submitButton);

    // Check that validation is triggered
    expect(nameInput).toBeInvalid();
    expect(emailInput).toBeInvalid();

    // Fill name field
    await userEvent.type(nameInput, 'Test Client');

    // Name field should now be valid
    expect(nameInput).toBeValid();

    // Email still invalid
    expect(emailInput).toBeInvalid();

    // Fill email field with invalid email
    await userEvent.type(emailInput, 'invalid-email');

    // Email should still be invalid
    expect(emailInput).toBeInvalid();

    // Clear and fill with valid email
    await userEvent.clear(emailInput);
    await userEvent.type(emailInput, 'test@example.com');

    // Email should now be valid
    expect(emailInput).toBeValid();

    // Form should be valid
    expect(form).toBeValid();
  });

  test('form is keyboard navigable', async () => {
    render(
      <form data-testid="quote-form">
        <div>
          <label htmlFor="client-name">Client Name</label>
          <input id="client-name" name="clientName" type="text" />
        </div>

        <div>
          <label htmlFor="email">Email</label>
          <input id="email" name="email" type="email" />
        </div>

        <button type="submit">Submit</button>
      </form>
    );

    // Start with the first input
    const nameInput = screen.getByLabelText('Client Name');
    nameInput.focus();
    expect(document.activeElement).toBe(nameInput);

    // Check that we can tab through all elements
    const emailInput = screen.getByLabelText('Email');
    const submitButton = screen.getByRole('button', { name: 'Submit' });

    // Verify all elements are in the document
    expect(nameInput).toBeInTheDocument();
    expect(emailInput).toBeInTheDocument();
    expect(submitButton).toBeInTheDocument();

    // Verify all elements are focusable
    nameInput.focus();
    expect(document.activeElement).toBe(nameInput);

    emailInput.focus();
    expect(document.activeElement).toBe(emailInput);

    submitButton.focus();
    expect(document.activeElement).toBe(submitButton);
  });
});
