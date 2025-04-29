/**
 * Enhanced Quote Form Tests
 * 
 * Comprehensive tests for the EnhancedQuoteForm component covering:
 * - Functionality
 * - Accessibility
 * - Performance
 * - User experience
 */

import React from 'react';
import { render, screen, fireEvent, waitFor } from '@testing-library/react';
import userEvent from '@testing-library/user-event';
import { QueryClient, QueryClientProvider } from '@tanstack/react-query';
import { MemoryRouter } from 'react-router-dom';
import { EnhancedQuoteForm } from '../EnhancedQuoteForm';
import { axe } from 'jest-axe';
import { ThemeProvider } from 'styled-components';
import { ConfigProvider } from 'antd';
import { appTheme } from '../../../../styles/theme';
import { 
  testUserFlow, 
  testFormInteraction,
  verifyUXBenchmarks 
} from '../../../../tests/ux/UXTestFramework';
import { 
  runA11yTests, 
  verifyA11yCompliance 
} from '../../../../tests/accessibility/AccessibilityTests';
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

// Mock hooks
jest.mock('../../../../hooks/useMediaQuery', () => ({
  useMediaQuery: jest.fn().mockReturnValue(false),
}));

jest.mock('../../../../hooks/useFormProgress', () => ({
  useFormProgress: () => ({
    saveProgress: jest.fn(),
    loadProgress: jest.fn().mockReturnValue(null),
    clearProgress: jest.fn(),
  }),
}));

// Mock react-router-dom
jest.mock('react-router-dom', () => ({
  ...jest.requireActual('react-router-dom'),
  useNavigate: () => jest.fn(),
}));

describe('EnhancedQuoteForm', () => {
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

  const renderComponent = () => {
    return render(
      <QueryClientProvider client={queryClient}>
        <ConfigProvider theme={appTheme}>
          <ThemeProvider theme={{ token: appTheme.token }}>
            <MemoryRouter>
              <EnhancedQuoteForm />
            </MemoryRouter>
          </ThemeProvider>
        </ConfigProvider>
      </QueryClientProvider>
    );
  };

  describe('Functionality Tests', () => {
    test('renders all form steps correctly', async () => {
      renderComponent();
      
      // Initial step should be visible
      expect(screen.getByText('Client Information')).toBeInTheDocument();
      
      // Navigate to next step
      fireEvent.click(screen.getByText('Next'));
      
      // Should show validation errors
      await waitFor(() => {
        expect(screen.getByText('Please enter client name')).toBeInTheDocument();
      });
      
      // Fill required fields
      await userEvent.type(screen.getByLabelText('Client Name'), 'Test Client');
      await userEvent.type(screen.getByLabelText('Email'), 'test@example.com');
      await userEvent.type(screen.getByLabelText('Phone'), '555-123-4567');
      
      // Navigate to next step
      fireEvent.click(screen.getByText('Next'));
      
      // Vehicle details step should be visible
      await waitFor(() => {
        expect(screen.getByText('Vehicle Details')).toBeInTheDocument();
      });
    });
    
    test('handles form submission correctly', async () => {
      const { createQuote } = require('../../../../services/api/quotes');
      renderComponent();
      
      // Fill all steps and submit
      // Step 1: Client Info
      await userEvent.type(screen.getByLabelText('Client Name'), 'Test Client');
      await userEvent.type(screen.getByLabelText('Email'), 'test@example.com');
      await userEvent.type(screen.getByLabelText('Phone'), '555-123-4567');
      fireEvent.click(screen.getByText('Next'));
      
      // Step 2: Vehicle Details
      await waitFor(() => {
        expect(screen.getByText('Vehicle Details')).toBeInTheDocument();
      });
      
      await userEvent.type(screen.getByLabelText('Make'), 'Toyota');
      await userEvent.type(screen.getByLabelText('Model'), 'Camry');
      await userEvent.type(screen.getByLabelText('Year'), '2022');
      await userEvent.type(screen.getByLabelText('VIN'), '1HGCM82633A123456');
      fireEvent.click(screen.getByText('Next'));
      
      // Step 3: Coverage
      await waitFor(() => {
        expect(screen.getByText('Coverage Details')).toBeInTheDocument();
      });
      
      // Select coverage type
      const coverageSelect = screen.getByLabelText('Coverage Type');
      fireEvent.mouseDown(coverageSelect);
      await waitFor(() => {
        fireEvent.click(screen.getByText('Standard Storage - $100/month'));
      });
      
      await userEvent.type(screen.getByLabelText('Duration (months)'), '12');
      
      // Mock date picker
      const datePicker = screen.getByLabelText('Start Date');
      fireEvent.mouseDown(datePicker);
      fireEvent.click(document.querySelector('.ant-picker-cell-today'));
      
      fireEvent.click(screen.getByText('Next'));
      
      // Step 4: Review
      await waitFor(() => {
        expect(screen.getByText('Review Quote')).toBeInTheDocument();
      });
      
      // Submit form
      fireEvent.click(screen.getByText('Submit Quote'));
      
      // Check if API was called
      await waitFor(() => {
        expect(createQuote).toHaveBeenCalled();
      });
    });
    
    test('shows loading state while fetching data', () => {
      // Mock loading state
      jest.spyOn(require('@tanstack/react-query'), 'useQuery').mockImplementation(() => ({
        isLoading: true,
        error: null,
        data: null,
      }));
      
      renderComponent();
      
      expect(screen.getByText('Loading rate information...')).toBeInTheDocument();
    });
    
    test('shows error state when API fails', () => {
      // Mock error state
      jest.spyOn(require('@tanstack/react-query'), 'useQuery').mockImplementation(() => ({
        isLoading: false,
        error: new Error('Failed to load'),
        data: null,
      }));
      
      renderComponent();
      
      expect(screen.getByText('Error Loading Data')).toBeInTheDocument();
      expect(screen.getByText('We couldn\'t load the necessary data. Please try again later.')).toBeInTheDocument();
    });
    
    test('shows success state after submission', async () => {
      renderComponent();
      
      // Mock successful submission
      jest.spyOn(require('@tanstack/react-query'), 'useMutation').mockImplementation(() => ({
        mutateAsync: jest.fn().mockResolvedValue({ id: 1 }),
        isLoading: false,
      }));
      
      // Set submitted state
      const setIsSubmittedSpy = jest.spyOn(React, 'useState');
      setIsSubmittedSpy.mockImplementationOnce(() => [true, jest.fn()]);
      
      // Re-render with success state
      renderComponent();
      
      expect(screen.getByText('Quote Created Successfully!')).toBeInTheDocument();
      expect(screen.getByText('Your quote has been submitted and is being processed.')).toBeInTheDocument();
    });
  });
  
  describe('Accessibility Tests', () => {
    test('has no accessibility violations', async () => {
      const { container } = renderComponent();
      const results = await axe(container);
      expect(results).toHaveNoViolations();
    });
    
    test('form is keyboard navigable', async () => {
      renderComponent();
      
      // Focus first input
      const clientNameInput = screen.getByLabelText('Client Name');
      clientNameInput.focus();
      expect(document.activeElement).toBe(clientNameInput);
      
      // Tab to next input
      userEvent.tab();
      expect(document.activeElement).toBe(screen.getByLabelText('Email'));
      
      // Tab to next input
      userEvent.tab();
      expect(document.activeElement).toBe(screen.getByLabelText('Phone'));
      
      // Tab to next button
      userEvent.tab();
      expect(document.activeElement).toBe(screen.getByText('Next'));
      
      // Activate button with keyboard
      fireEvent.keyDown(document.activeElement, { key: 'Enter' });
      
      // Should show validation errors
      await waitFor(() => {
        expect(screen.getByText('Please enter client name')).toBeInTheDocument();
      });
    });
    
    test('form errors are properly associated with inputs', async () => {
      renderComponent();
      
      // Submit form without filling required fields
      fireEvent.click(screen.getByText('Next'));
      
      // Wait for validation errors
      await waitFor(() => {
        const errorMessages = screen.getAllByText(/Please enter/);
        expect(errorMessages.length).toBeGreaterThan(0);
      });
      
      // Check that error messages are properly associated with inputs
      const clientNameInput = screen.getByLabelText('Client Name');
      const clientNameError = screen.getByText('Please enter client name');
      
      expect(clientNameInput).toHaveAttribute('aria-invalid', 'true');
      expect(clientNameInput.parentElement.parentElement).toContainElement(clientNameError);
    });
    
    test('meets comprehensive accessibility standards', async () => {
      const results = await runA11yTests({
        component: (
          <QueryClientProvider client={queryClient}>
            <ConfigProvider theme={appTheme}>
              <ThemeProvider theme={{ token: appTheme.token }}>
                <MemoryRouter>
                  <EnhancedQuoteForm />
                </MemoryRouter>
              </ThemeProvider>
            </ConfigProvider>
          </QueryClientProvider>
        ),
        interactiveElements: [
          { selector: 'input[name="clientName"]', action: 'input', value: 'Test Client' },
          { selector: 'button[aria-label="Next step"]', action: 'click' },
        ],
        ariaElements: [
          { selector: 'form', requiredAttributes: ['aria-label'] },
          { selector: 'input[name="clientName"]', requiredAttributes: ['aria-required'] },
        ],
      });
      
      const compliance = verifyA11yCompliance(results);
      expect(compliance.passed).toBe(true);
    });
  });
  
  describe('Performance Tests', () => {
    test('renders efficiently', async () => {
      const results = await runPerformanceTests({
        component: (
          <QueryClientProvider client={queryClient}>
            <ConfigProvider theme={appTheme}>
              <ThemeProvider theme={{ token: appTheme.token }}>
                <MemoryRouter>
                  <EnhancedQuoteForm />
                </MemoryRouter>
              </ThemeProvider>
            </ConfigProvider>
          </QueryClientProvider>
        ),
        renderCount: 3,
      });
      
      const benchmarkResults = verifyPerformanceBenchmarks(results);
      expect(benchmarkResults.passed).toBe(true);
    });
    
    test('handles form interactions efficiently', async () => {
      renderComponent();
      
      const startTime = performance.now();
      
      // Fill out form fields
      await userEvent.type(screen.getByLabelText('Client Name'), 'Test Client');
      await userEvent.type(screen.getByLabelText('Email'), 'test@example.com');
      await userEvent.type(screen.getByLabelText('Phone'), '555-123-4567');
      
      // Navigate to next step
      fireEvent.click(screen.getByText('Next'));
      
      const endTime = performance.now();
      const interactionTime = endTime - startTime;
      
      // Interaction should be fast
      expect(interactionTime).toBeLessThan(500);
    });
  });
  
  describe('User Experience Tests', () => {
    test('provides clear validation feedback', async () => {
      renderComponent();
      
      // Submit form without filling required fields
      fireEvent.click(screen.getByText('Next'));
      
      // Wait for validation errors
      await waitFor(() => {
        const errorMessages = screen.getAllByText(/Please enter/);
        expect(errorMessages.length).toBeGreaterThan(0);
      });
      
      // Fill one field and check that its error disappears
      await userEvent.type(screen.getByLabelText('Client Name'), 'Test Client');
      
      // Error for client name should disappear
      await waitFor(() => {
        expect(screen.queryByText('Please enter client name')).not.toBeInTheDocument();
      });
      
      // Other errors should still be visible
      expect(screen.getByText('Please enter email address')).toBeInTheDocument();
    });
    
    test('saves and restores form progress', async () => {
      // Mock form progress hooks
      const mockSaveProgress = jest.fn();
      const mockLoadProgress = jest.fn().mockReturnValue({
        clientName: 'Saved Client',
        email: 'saved@example.com',
        phone: '555-987-6543',
      });
      
      jest.mock('../../../../hooks/useFormProgress', () => ({
        useFormProgress: () => ({
          saveProgress: mockSaveProgress,
          loadProgress: mockLoadProgress,
          clearProgress: jest.fn(),
        }),
      }));
      
      // Re-render with mocked hooks
      renderComponent();
      
      // Check that saved values are loaded
      await waitFor(() => {
        expect(screen.getByLabelText('Client Name')).toHaveValue('Saved Client');
        expect(screen.getByLabelText('Email')).toHaveValue('saved@example.com');
        expect(screen.getByLabelText('Phone')).toHaveValue('555-987-6543');
      });
      
      // Update a field and check that progress is saved
      await userEvent.clear(screen.getByLabelText('Client Name'));
      await userEvent.type(screen.getByLabelText('Client Name'), 'Updated Client');
      
      await waitFor(() => {
        expect(mockSaveProgress).toHaveBeenCalled();
      });
    });
    
    test('meets UX benchmarks for form completion', async () => {
      renderComponent();
      
      const metrics = await testFormInteraction(
        'form',
        {
          'Client Name': 'Test Client',
          'Email': 'test@example.com',
          'Phone': '555-123-4567',
        },
        'Next',
        [
          // Validation checks
          async () => {
            const emailInput = screen.getByLabelText('Email');
            const emailValue = (emailInput as HTMLInputElement).value;
            return emailValue.includes('@') && emailValue.includes('.');
          },
        ]
      );
      
      const result = verifyUXBenchmarks(metrics);
      expect(result.passed).toBe(true);
    });
  });
});
