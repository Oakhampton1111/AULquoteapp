/**
 * Static Test Utilities for React components
 * 
 * This file provides utility functions and wrappers for testing React components
 * without using React hooks.
 */

import React from 'react';
import { render } from '@testing-library/react';
import { QueryClient, QueryClientProvider } from '@tanstack/react-query';
import { MemoryRouter } from 'react-router-dom';

// Create a static QueryClient for testing
const staticQueryClient = new QueryClient({
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

// Create a static wrapper component
const StaticWrapper = ({ children }: { children: React.ReactNode }) => (
  <QueryClientProvider client={staticQueryClient}>
    <MemoryRouter>
      {children}
    </MemoryRouter>
  </QueryClientProvider>
);

/**
 * Custom render function that wraps components with static providers
 */
export function renderWithStaticProviders(ui: React.ReactElement) {
  return render(ui, { wrapper: StaticWrapper });
}
