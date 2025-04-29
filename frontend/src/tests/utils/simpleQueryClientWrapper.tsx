/**
 * Simple React Query Test Wrapper
 * 
 * This file provides a simplified wrapper for testing components that use React Query.
 */

import React from 'react';
import { render } from '@testing-library/react';
import { QueryClient, QueryClientProvider } from '@tanstack/react-query';
import { MemoryRouter } from 'react-router-dom';

// Create a QueryClient for testing
const testQueryClient = new QueryClient({
  defaultOptions: {
    queries: {
      retry: false,
      cacheTime: 0,
    },
  },
  logger: {
    log: console.log,
    warn: console.warn,
    error: () => {}, // Silence errors in tests
  },
});

/**
 * Custom render function that wraps components with QueryClientProvider and MemoryRouter
 */
export const renderWithProviders = (ui: React.ReactElement) => {
  return render(
    <QueryClientProvider client={testQueryClient}>
      <MemoryRouter>
        {ui}
      </MemoryRouter>
    </QueryClientProvider>
  );
};
