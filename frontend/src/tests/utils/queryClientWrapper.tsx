/**
 * React Query Test Wrapper
 * 
 * This file provides utilities for testing components that use React Query.
 */

import React from 'react';
import { render } from '@testing-library/react';
import { QueryClient, QueryClientProvider } from '@tanstack/react-query';
import { MemoryRouter } from 'react-router-dom';

// Create a new QueryClient for each test
const createTestQueryClient = () => new QueryClient({
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
 * Wrapper component for testing components that use React Query
 */
export const QueryClientWrapper: React.FC<{ children: React.ReactNode }> = ({ children }) => {
  // Create a new QueryClient instance for each test
  const queryClient = React.useState(() => createTestQueryClient())[0];

  return (
    <QueryClientProvider client={queryClient}>
      {children}
    </QueryClientProvider>
  );
};

/**
 * Wrapper component for testing components that use React Query and React Router
 */
export const RouterQueryClientWrapper: React.FC<{ 
  children: React.ReactNode;
  initialRoute?: string;
}> = ({ children, initialRoute = '/' }) => {
  // Create a new QueryClient instance for each test
  const queryClient = React.useState(() => createTestQueryClient())[0];

  return (
    <QueryClientProvider client={queryClient}>
      <MemoryRouter initialEntries={[initialRoute]}>
        {children}
      </MemoryRouter>
    </QueryClientProvider>
  );
};

/**
 * Custom render function that wraps components with QueryClientWrapper
 */
export const renderWithQueryClient = (ui: React.ReactElement) => {
  return render(ui, {
    wrapper: QueryClientWrapper,
  });
};

/**
 * Custom render function that wraps components with RouterQueryClientWrapper
 */
export const renderWithRouterAndQueryClient = (
  ui: React.ReactElement,
  { initialRoute = '/' } = {}
) => {
  return render(ui, {
    wrapper: ({ children }) => (
      <RouterQueryClientWrapper initialRoute={initialRoute}>
        {children}
      </RouterQueryClientWrapper>
    ),
  });
};
