import React from 'react';
import { render } from '@testing-library/react';
import { axe, toHaveNoViolations } from 'jest-axe';

// Add jest-axe matchers
expect.extend(toHaveNoViolations);

describe('Accessibility Tests', () => {
  test('form has no accessibility violations', async () => {
    const { container } = render(
      <form aria-labelledby="form-title">
        <h2 id="form-title">Quote Form</h2>
        
        <div>
          <label htmlFor="client-name">Client Name</label>
          <input 
            id="client-name" 
            name="clientName" 
            type="text" 
            aria-required="true"
          />
        </div>
        
        <div>
          <label htmlFor="email">Email</label>
          <input 
            id="email" 
            name="email" 
            type="email" 
            aria-required="true"
          />
        </div>
        
        <button type="submit">Submit</button>
      </form>
    );
    
    // Run axe accessibility tests
    const results = await axe(container);
    expect(results).toHaveNoViolations();
  });
});
