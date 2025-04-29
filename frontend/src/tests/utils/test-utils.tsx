/**
 * Test utilities for React components
 *
 * This file provides utility functions and wrappers for testing React components,
 * particularly those that use React Query.
 */

import React from 'react';
import { render, RenderOptions } from '@testing-library/react';
import { QueryClient, QueryClientProvider } from '@tanstack/react-query';
import { MemoryRouter } from 'react-router-dom';
import { ThemeProvider } from 'styled-components';

// Create a custom render function that includes providers
interface CustomRenderOptions extends RenderOptions {
  route?: string;
  queryClient?: QueryClient;
}

/**
 * Create a fresh QueryClient for testing
 */
export function createTestQueryClient() {
  return new QueryClient({
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
}

// Create a simple theme for styled-components
const theme = {
  colors: {
    primary: '#1890ff',
    secondary: '#52c41a',
    error: '#f5222d',
    background: '#ffffff',
    text: '#000000',
  },
  fonts: {
    main: 'Arial, sans-serif',
  },
  spacing: {
    small: '8px',
    medium: '16px',
    large: '24px',
  },
};

// Create a class component wrapper to avoid React hooks issues
class AllTheProviders extends React.Component<{
  children: React.ReactNode;
  queryClient: QueryClient;
  route: string;
}> {
  render() {
    const { children, queryClient, route } = this.props;
    return (
      <ThemeProvider theme={theme}>
        <QueryClientProvider client={queryClient}>
          <MemoryRouter initialEntries={[route]}>
            {children}
          </MemoryRouter>
        </QueryClientProvider>
      </ThemeProvider>
    );
  }
}

/**
 * Custom render function that wraps components with necessary providers
 */
export function renderWithProviders(
  ui: React.ReactElement,
  {
    route = '/',
    queryClient = createTestQueryClient(),
    ...renderOptions
  }: CustomRenderOptions = {}
) {
  return render(ui, {
    wrapper: ({ children }) => (
      <AllTheProviders queryClient={queryClient} route={route}>
        {children}
      </AllTheProviders>
    ),
    ...renderOptions
  });
}
