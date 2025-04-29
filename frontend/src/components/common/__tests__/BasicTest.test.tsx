import React from 'react';
import { render, screen } from '@testing-library/react';

describe('Basic Test', () => {
  test('renders without crashing', () => {
    render(<div data-testid="test-element">Test Component</div>);
    expect(screen.getByTestId('test-element')).toBeInTheDocument();
  });
});
