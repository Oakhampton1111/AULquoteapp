import { setupWorker } from 'msw';
import { handlers } from './handlers';

// This configures a Service Worker with the given request handlers.
export const worker = setupWorker(...handlers);

// Initialize the MSW worker when in development mode
if (import.meta.env.DEV && import.meta.env.VITE_USE_MOCKS === 'true') {
  worker.start({
    onUnhandledRequest: 'bypass', // Don't warn about unhandled requests
  });
  console.log('🔶 Mock Service Worker started');
}
