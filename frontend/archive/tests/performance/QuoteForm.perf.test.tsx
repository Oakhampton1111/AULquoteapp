/**
 * QuoteForm Performance Tests
 * 
 * This file contains performance-focused tests for the QuoteForm component,
 * ensuring it meets our performance benchmarks for rendering and interaction.
 */

import React from 'react';
import { QueryClient, QueryClientProvider } from '@tanstack/react-query';
import { MemoryRouter } from 'react-router-dom';
import { QuoteForm } from '../QuoteForm';
import { 
  runPerformanceTests, 
  verifyPerformanceBenchmarks 
} from '../../../../tests/performance/PerformanceTests';

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

describe('QuoteForm Performance Tests', () => {
  let queryClient: QueryClient;

  beforeEach(() => {
    queryClient = new QueryClient({
      defaultOptions: {
        queries: {
          retry: false,
          cacheTime: 0,
        },
      },
    });
  });

  const getComponent = (props = {}) => (
    <QueryClientProvider client={queryClient}>
      <MemoryRouter>
        <QuoteForm {...props} />
      </MemoryRouter>
    </QueryClientProvider>
  );

  test('meets performance benchmarks', async () => {
    const results = await runPerformanceTests({
      component: getComponent(),
      renderCount: 5,
      propsUpdates: [
        { initialValues: { clientName: 'Test Client' } },
        { initialValues: { clientName: 'Test Client', email: 'test@example.com' } },
        { initialValues: { clientName: 'Test Client', email: 'test@example.com', phone: '555-123-4567' } },
      ],
      networkRequests: [
        '/api/rateCards',
        '/api/quotes',
      ],
      animationSelectors: [
        '.ant-form-item-explain-error', // Error animation
        '.ant-select-dropdown', // Dropdown animation
      ],
    });

    const benchmarkResults = verifyPerformanceBenchmarks(results);
    expect(benchmarkResults.passed).toBe(true);
    if (!benchmarkResults.passed) {
      console.error('Performance benchmark failures:', benchmarkResults.failures);
    }
  });

  test('renders efficiently with different data sizes', async () => {
    // Test with small dataset
    const smallDataResults = await runPerformanceTests({
      component: getComponent(),
      renderCount: 3,
    });

    // Mock a larger dataset
    jest.mock('../../../../services/api/rateCards', () => ({
      fetchRateCards: jest.fn().mockResolvedValue(
        Array(50).fill(0).map((_, i) => ({
          id: i + 1,
          name: `Rate Card ${i + 1}`,
          type: i % 2 === 0 ? 'storage' : 'transport',
          baseRate: 100 + i * 10,
        }))
      ),
    }));

    // Test with large dataset
    const largeDataResults = await runPerformanceTests({
      component: getComponent(),
      renderCount: 3,
    });

    // Verify that performance doesn't degrade significantly with larger data
    expect(largeDataResults.initialRenderTime).toBeLessThan(
      smallDataResults.initialRenderTime * 2
    );
    
    expect(largeDataResults.averageRenderTime).toBeLessThan(
      smallDataResults.averageRenderTime * 2
    );
  });

  test('handles rapid user interactions efficiently', async () => {
    // This test simulates rapid user interactions to ensure the component
    // doesn't degrade in performance during heavy user activity
    
    const component = getComponent();
    const { container } = render(component);
    
    // Measure performance during rapid interactions
    const startTime = performance.now();
    
    // Simulate rapid form filling
    await act(async () => {
      // Type in client name field
      const clientNameInput = container.querySelector('input[name="clientName"]');
      if (clientNameInput) {
        fireEvent.change(clientNameInput, { target: { value: 'Test Client' } });
      }
      
      // Type in email field
      const emailInput = container.querySelector('input[name="email"]');
      if (emailInput) {
        fireEvent.change(emailInput, { target: { value: 'test@example.com' } });
      }
      
      // Type in phone field
      const phoneInput = container.querySelector('input[name="phone"]');
      if (phoneInput) {
        fireEvent.change(phoneInput, { target: { value: '555-123-4567' } });
      }
      
      // Open and close dropdown rapidly
      const dropdown = container.querySelector('select');
      if (dropdown) {
        for (let i = 0; i < 5; i++) {
          fireEvent.mouseDown(dropdown);
          await new Promise(r => setTimeout(r, 10));
          fireEvent.mouseUp(dropdown);
          await new Promise(r => setTimeout(r, 10));
        }
      }
      
      // Rapidly click submit button
      const submitButton = container.querySelector('button[type="submit"]');
      if (submitButton) {
        for (let i = 0; i < 3; i++) {
          fireEvent.click(submitButton);
          await new Promise(r => setTimeout(r, 10));
        }
      }
    });
    
    const endTime = performance.now();
    const interactionTime = endTime - startTime;
    
    // Verify interaction performance
    expect(interactionTime).toBeLessThan(1000); // Should handle all interactions in under 1 second
  });
});

// Helper functions
import { render, fireEvent, act } from '@testing-library/react';
