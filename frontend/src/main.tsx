import { StrictMode } from 'react'
import { createRoot } from 'react-dom/client'
import { ConfigProvider } from 'antd'
import { appTheme } from './styles/theme'
import { GlobalStyles } from './styles/GlobalStyles'
import App from './App.tsx'
import ErrorBoundary from './components/common/ErrorBoundary'

// Initialize MSW in development mode
if (import.meta.env.DEV && import.meta.env.VITE_USE_MOCKS === 'true') {
  import('./mocks/browser').then(({ worker }) => {
    worker.start()
  })
}

// Initialize error tracking service in production
if (process.env.NODE_ENV === 'production') {
  // Example: Initialize Sentry
  // import * as Sentry from '@sentry/react';
  // Sentry.init({
  //   dsn: import.meta.env.VITE_SENTRY_DSN,
  //   integrations: [new Sentry.BrowserTracing()],
  //   tracesSampleRate: 1.0,
  // });
}

createRoot(document.getElementById('root')!).render(
  <StrictMode>
    <ErrorBoundary>
      <ConfigProvider theme={appTheme}>
        <GlobalStyles />
        <App />
      </ConfigProvider>
    </ErrorBoundary>
  </StrictMode>,
)
