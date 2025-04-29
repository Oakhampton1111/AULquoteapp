/**
 * Test Wrapper Component
 * 
 * This component provides all necessary providers for testing React components,
 * including React Query, React Router, and any other context providers needed.
 */

import React from 'react';
import { QueryClient, QueryClientProvider } from '@tanstack/react-query';
import { MemoryRouter } from 'react-router-dom';

// Create a client for React Query
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

interface TestWrapperProps {
  children: React.ReactNode;
  initialRoute?: string;
}

/**
 * TestWrapper component that provides all necessary context providers for tests
 */
export const TestWrapper: React.FC<TestWrapperProps> = ({ 
  children, 
  initialRoute = '/' 
}) => {
  // Create a new QueryClient for each test
  const queryClient = React.useMemo(() => createTestQueryClient(), []);

  return (
    <QueryClientProvider client={queryClient}>
      <MemoryRouter initialEntries={[initialRoute]}>
        {children}
      </MemoryRouter>
    </QueryClientProvider>
  );
};

/**
 * Custom render function that wraps components with TestWrapper
 */
export const renderWithTestWrapper = (
  ui: React.ReactElement,
  { initialRoute = '/', ...options }: { initialRoute?: string } = {}
) => {
  const Wrapper = ({ children }: { children: React.ReactNode }) => (
    <TestWrapper initialRoute={initialRoute}>{children}</TestWrapper>
  );

  return {
    ...render(ui, { wrapper: Wrapper, ...options }),
  };
};

// Import from testing-library to avoid having to import it separately
import { render } from '@testing-library/react';
