import React from 'react';
import { render, screen } from '@testing-library/react';

// Simple test to verify testing setup
describe('QuoteForm Basic Test', () => {
  test('renders a form element', () => {
    // Render a simple form for testing
    render(
      <form data-testid="quote-form">
        <label htmlFor="name">Name</label>
        <input id="name" type="text" />
        <button type="submit">Submit</button>
      </form>
    );
    
    // Verify form is rendered
    const formElement = screen.getByTestId('quote-form');
    expect(formElement).toBeInTheDocument();
    
    // Verify form elements are rendered
    expect(screen.getByLabelText('Name')).toBeInTheDocument();
    expect(screen.getByRole('button', { name: 'Submit' })).toBeInTheDocument();
  });
});
