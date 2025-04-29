// jest-dom adds custom jest matchers for asserting on DOM nodes.
// allows you to do things like:
// expect(element).toHaveTextContent(/react/i)
// learn more: https://github.com/testing-library/jest-dom
import '@testing-library/jest-dom';
import { configure } from '@testing-library/react';
import { QueryClient } from '@tanstack/react-query';

// Configure testing library
configure({
  testIdAttribute: 'data-testid',
});

// Mock window.matchMedia
Object.defineProperty(window, 'matchMedia', {
  writable: true,
  value: jest.fn().mockImplementation(query => ({
    matches: false,
    media: query,
    onchange: null,
    addListener: jest.fn(), // Deprecated
    removeListener: jest.fn(), // Deprecated
    addEventListener: jest.fn(),
    removeEventListener: jest.fn(),
    dispatchEvent: jest.fn(),
  })),
});

// Mock window.getComputedStyle
window.getComputedStyle = jest.fn().mockImplementation((element, pseudoElt) => {
  return {
    getPropertyValue: jest.fn(prop => {
      // Return default values for commonly used properties
      if (prop === 'width') return '100px';
      if (prop === 'height') return '100px';
      if (prop === 'background-color') return 'rgb(255, 255, 255)';
      if (prop === 'color') return 'rgb(0, 0, 0)';
      if (prop === 'font-size') return '16px';
      if (prop === 'margin') return '0px';
      if (prop === 'padding') return '0px';
      if (prop === 'border') return '0px';
      return '';
    }),
  };
});

// Mock ResizeObserver
global.ResizeObserver = jest.fn().mockImplementation(() => ({
  observe: jest.fn(),
  unobserve: jest.fn(),
  disconnect: jest.fn(),
}));

// Mock IntersectionObserver
global.IntersectionObserver = jest.fn().mockImplementation(() => ({
  observe: jest.fn(),
  unobserve: jest.fn(),
  disconnect: jest.fn(),
}));

// Suppress React 18 console errors in tests
const originalConsoleError = console.error;
console.error = (...args) => {
  if (
    typeof args[0] === 'string' &&
    (args[0].includes('ReactDOM.render is no longer supported') ||
      args[0].includes('Invalid hook call') ||
      args[0].includes('Cannot read properties of null (reading') ||
      args[0].includes('Warning: An update to') ||
      args[0].includes('not wrapped in act') ||
      args[0].includes('Error: Not implemented: window.computedStyle'))
  ) {
    return;
  }
  originalConsoleError(...args);
};

// Mock Ant Design components

// Mock Ant Design message component
jest.mock('antd/es/message', () => ({
  success: jest.fn(),
  error: jest.fn(),
  info: jest.fn(),
  warning: jest.fn(),
  loading: jest.fn(),
}));

// Mock Ant Design modal.confirm
jest.mock('antd/es/modal/confirm', () => ({
  confirm: jest.fn(({ onOk }) => {
    if (onOk) onOk();
    return { destroy: jest.fn() };
  }),
}));

// IntersectionObserver and ResizeObserver are already mocked above

// Mock window.scrollTo
window.scrollTo = jest.fn();

// Mock performance API
Object.defineProperty(window, 'performance', {
  writable: true,
  value: {
    getEntriesByType: jest.fn().mockReturnValue([]),
    mark: jest.fn(),
    measure: jest.fn(),
    now: jest.fn().mockReturnValue(Date.now()),
  },
});

// Mock html-to-image library
jest.mock('html-to-image', () => ({
  toPng: jest.fn().mockResolvedValue('data:image/png;base64,mockImageData'),
  toJpeg: jest.fn().mockResolvedValue('data:image/jpeg;base64,mockImageData'),
  toBlob: jest.fn().mockResolvedValue(new Blob(['mockImageData'], { type: 'image/png' })),
  toCanvas: jest.fn().mockResolvedValue(document.createElement('canvas')),
  toPixelData: jest.fn().mockResolvedValue(new Uint8ClampedArray([0, 0, 0, 0])),
  toSvg: jest.fn().mockResolvedValue('data:image/svg+xml;base64,mockImageData'),
}));
