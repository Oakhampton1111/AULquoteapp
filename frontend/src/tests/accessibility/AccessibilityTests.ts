/**
 * Accessibility Test Suite
 * 
 * A comprehensive suite of tests to ensure our components meet accessibility standards.
 * This includes tests for:
 * - ARIA attributes
 * - Keyboard navigation
 * - Color contrast
 * - Screen reader compatibility
 * - Focus management
 */

import { render, RenderResult } from '@testing-library/react';
import { axe, toHaveNoViolations } from 'jest-axe';
import userEvent from '@testing-library/user-event';

// Extend Jest matchers
expect.extend(toHaveNoViolations);

/**
 * Accessibility test configuration
 */
export interface A11yTestConfig {
  // Component to test
  component: React.ReactElement;
  
  // Interactive elements to test with keyboard
  interactiveElements?: {
    selector: string;
    action: 'click' | 'input' | 'select';
    value?: string;
  }[];
  
  // Elements to check for proper ARIA attributes
  ariaElements?: {
    selector: string;
    requiredAttributes: string[];
  }[];
  
  // Color contrast pairs to check
  contrastPairs?: {
    background: string;
    foreground: string;
    minimumRatio: number;
  }[];
}

/**
 * Accessibility test results
 */
export interface A11yTestResults {
  axeViolations: number;
  keyboardAccessible: boolean;
  ariaCompliant: boolean;
  contrastCompliant: boolean;
  focusManagementCompliant: boolean;
  violations: {
    axe: any[];
    keyboard: string[];
    aria: string[];
    contrast: string[];
    focusManagement: string[];
  };
}

/**
 * Run comprehensive accessibility tests on a component
 */
export async function runA11yTests(config: A11yTestConfig): Promise<A11yTestResults> {
  const results: A11yTestResults = {
    axeViolations: 0,
    keyboardAccessible: true,
    ariaCompliant: true,
    contrastCompliant: true,
    focusManagementCompliant: true,
    violations: {
      axe: [],
      keyboard: [],
      aria: [],
      contrast: [],
      focusManagement: [],
    },
  };
  
  // Render component
  const renderResult = render(config.component);
  const { container } = renderResult;
  
  // Run axe tests
  try {
    const axeResults = await axe(container);
    results.axeViolations = axeResults.violations.length;
    results.violations.axe = axeResults.violations;
  } catch (error) {
    results.axeViolations = 1;
    results.violations.axe.push({
      id: 'axe-error',
      description: 'Error running axe tests',
      help: 'Check console for details',
      nodes: [],
    });
    console.error('Error running axe tests:', error);
  }
  
  // Test keyboard navigation
  if (config.interactiveElements) {
    for (const element of config.interactiveElements) {
      try {
        const el = container.querySelector(element.selector) as HTMLElement;
        if (!el) {
          results.keyboardAccessible = false;
          results.violations.keyboard.push(
            `Element not found: ${element.selector}`
          );
          continue;
        }
        
        // Focus the element
        el.focus();
        
        // Check if element is focused
        if (document.activeElement !== el) {
          results.keyboardAccessible = false;
          results.violations.keyboard.push(
            `Element cannot be focused: ${element.selector}`
          );
          continue;
        }
        
        // Test interaction
        switch (element.action) {
          case 'click':
            await userEvent.keyboard('{enter}');
            break;
          case 'input':
            if (element.value) {
              await userEvent.keyboard(element.value);
            }
            break;
          case 'select':
            await userEvent.keyboard('{enter}');
            await userEvent.keyboard('{arrowdown}');
            await userEvent.keyboard('{enter}');
            break;
        }
      } catch (error) {
        results.keyboardAccessible = false;
        results.violations.keyboard.push(
          `Error testing keyboard navigation for ${element.selector}: ${error}`
        );
      }
    }
  }
  
  // Test ARIA attributes
  if (config.ariaElements) {
    for (const element of config.ariaElements) {
      try {
        const el = container.querySelector(element.selector) as HTMLElement;
        if (!el) {
          results.ariaCompliant = false;
          results.violations.aria.push(
            `Element not found: ${element.selector}`
          );
          continue;
        }
        
        // Check required attributes
        for (const attr of element.requiredAttributes) {
          if (!el.hasAttribute(attr)) {
            results.ariaCompliant = false;
            results.violations.aria.push(
              `Missing required attribute ${attr} on ${element.selector}`
            );
          }
        }
      } catch (error) {
        results.ariaCompliant = false;
        results.violations.aria.push(
          `Error testing ARIA attributes for ${element.selector}: ${error}`
        );
      }
    }
  }
  
  // Test color contrast
  if (config.contrastPairs) {
    for (const pair of config.contrastPairs) {
      try {
        const contrast = getContrastRatio(pair.foreground, pair.background);
        if (contrast < pair.minimumRatio) {
          results.contrastCompliant = false;
          results.violations.contrast.push(
            `Insufficient contrast ratio: ${contrast.toFixed(2)} (required: ${pair.minimumRatio})`
          );
        }
      } catch (error) {
        results.contrastCompliant = false;
        results.violations.contrast.push(
          `Error testing contrast: ${error}`
        );
      }
    }
  }
  
  // Test focus management
  try {
    // Find all focusable elements
    const focusableElements = container.querySelectorAll(
      'button, [href], input, select, textarea, [tabindex]:not([tabindex="-1"])'
    );
    
    // Check if focus trap works correctly for modals
    const isModal = container.querySelector('[role="dialog"]') !== null;
    if (isModal && focusableElements.length > 0) {
      // Focus the first element
      (focusableElements[0] as HTMLElement).focus();
      
      // Tab to the last element
      for (let i = 0; i < focusableElements.length - 1; i++) {
        await userEvent.tab();
      }
      
      // Tab again should cycle back to first element in a modal
      await userEvent.tab();
      
      // Check if focus is back on the first element
      if (document.activeElement !== focusableElements[0]) {
        results.focusManagementCompliant = false;
        results.violations.focusManagement.push(
          'Focus is not trapped within modal dialog'
        );
      }
    }
  } catch (error) {
    results.focusManagementCompliant = false;
    results.violations.focusManagement.push(
      `Error testing focus management: ${error}`
    );
  }
  
  return results;
}

/**
 * Calculate contrast ratio between two colors
 */
function getContrastRatio(foreground: string, background: string): number {
  // Convert colors to luminance values
  const foregroundLuminance = getLuminance(foreground);
  const backgroundLuminance = getLuminance(background);
  
  // Calculate contrast ratio
  const lighter = Math.max(foregroundLuminance, backgroundLuminance);
  const darker = Math.min(foregroundLuminance, backgroundLuminance);
  
  return (lighter + 0.05) / (darker + 0.05);
}

/**
 * Calculate luminance of a color
 */
function getLuminance(color: string): number {
  // This is a simplified implementation
  // In a real app, you'd use a color library to handle all formats
  
  // Parse RGB values
  let r, g, b;
  
  if (color.startsWith('#')) {
    // Hex format
    const hex = color.slice(1);
    r = parseInt(hex.slice(0, 2), 16) / 255;
    g = parseInt(hex.slice(2, 4), 16) / 255;
    b = parseInt(hex.slice(4, 6), 16) / 255;
  } else if (color.startsWith('rgb')) {
    // RGB format
    const match = color.match(/rgb\((\d+),\s*(\d+),\s*(\d+)\)/);
    if (match) {
      r = parseInt(match[1], 10) / 255;
      g = parseInt(match[2], 10) / 255;
      b = parseInt(match[3], 10) / 255;
    } else {
      return 0;
    }
  } else {
    return 0;
  }
  
  // Apply gamma correction
  r = r <= 0.03928 ? r / 12.92 : Math.pow((r + 0.055) / 1.055, 2.4);
  g = g <= 0.03928 ? g / 12.92 : Math.pow((g + 0.055) / 1.055, 2.4);
  b = b <= 0.03928 ? b / 12.92 : Math.pow((b + 0.055) / 1.055, 2.4);
  
  // Calculate luminance
  return 0.2126 * r + 0.7152 * g + 0.0722 * b;
}

/**
 * Verify that a component meets accessibility standards
 */
export function verifyA11yCompliance(results: A11yTestResults): {
  passed: boolean;
  failures: string[];
} {
  const failures: string[] = [];
  
  // Check axe violations
  if (results.axeViolations > 0) {
    failures.push(`Component has ${results.axeViolations} axe violations`);
    
    // Add details for each violation
    results.violations.axe.forEach((violation, index) => {
      failures.push(`  ${index + 1}. ${violation.help} (${violation.id})`);
    });
  }
  
  // Check keyboard accessibility
  if (!results.keyboardAccessible) {
    failures.push('Component is not fully keyboard accessible');
    
    // Add details for each violation
    results.violations.keyboard.forEach((violation, index) => {
      failures.push(`  ${index + 1}. ${violation}`);
    });
  }
  
  // Check ARIA compliance
  if (!results.ariaCompliant) {
    failures.push('Component has ARIA compliance issues');
    
    // Add details for each violation
    results.violations.aria.forEach((violation, index) => {
      failures.push(`  ${index + 1}. ${violation}`);
    });
  }
  
  // Check contrast compliance
  if (!results.contrastCompliant) {
    failures.push('Component has color contrast issues');
    
    // Add details for each violation
    results.violations.contrast.forEach((violation, index) => {
      failures.push(`  ${index + 1}. ${violation}`);
    });
  }
  
  // Check focus management
  if (!results.focusManagementCompliant) {
    failures.push('Component has focus management issues');
    
    // Add details for each violation
    results.violations.focusManagement.forEach((violation, index) => {
      failures.push(`  ${index + 1}. ${violation}`);
    });
  }
  
  return {
    passed: failures.length === 0,
    failures,
  };
}
