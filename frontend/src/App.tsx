import React, { useEffect } from 'react';
import { BrowserRouter, Routes, Route, Navigate } from 'react-router-dom';
import { QueryClient, QueryClientProvider } from '@tanstack/react-query';
import { AuthProvider } from './services/auth/AuthContext';
import { ProtectedRoute } from './components/auth/ProtectedRoute';
import { AppLayout } from './components/layout/AppLayout';
import { LoginForm } from './components/auth/LoginForm';
import { ErrorBoundary } from './components/common/ErrorBoundary';
import { message } from 'antd';
import { monitorWebVitals } from './utils/performance';

// Admin Components
import { AdminDashboard } from './pages/admin/Dashboard';
import { UserManagement } from './components/admin/UserManagement/UserManagement';
import { RateCardManagement } from './components/admin/RateCard/RateCardManagement';

// Client Components
import { CustomerDashboard as ClientDashboard } from './pages/client/Dashboard';
import { QuoteForm } from './components/client/QuoteForm/QuoteForm';
import { QuoteList } from './components/client/QuoteList/QuoteList';
import { QuoteDetail } from './pages/client/QuoteDetail';

// Configure global message duration
message.config({
  duration: 3,
  maxCount: 3,
});

// Configure QueryClient with error handling and retries
const queryClient = new QueryClient({
  defaultOptions: {
    queries: {
      retry: 1,
      refetchOnWindowFocus: false,
      staleTime: 5 * 60 * 1000, // 5 minutes
      // Add global error handling for queries
      onError: (error) => {
        console.error('Query error:', error);
        // You could add global error handling here
      }
    },
    mutations: {
      retry: 1,
      // Add global error handling for mutations
      onError: (error) => {
        console.error('Mutation error:', error);
        // You could add global error handling here
      }
    },
  },
});

const App: React.FC = () => {
  // Initialize performance monitoring
  useEffect(() => {
    // Start monitoring web vitals
    monitorWebVitals();

    // Log initial page load time
    if (window.performance && window.performance.getEntriesByType) {
      const navigationEntries = window.performance.getEntriesByType('navigation');
      if (navigationEntries.length > 0) {
        const navigationEntry = navigationEntries[0] as PerformanceNavigationTiming;
        const pageLoadTime = navigationEntry.loadEventEnd - navigationEntry.startTime;
        console.log(`Page load time: ${pageLoadTime.toFixed(2)}ms`);
      }
    }

    // Clean up performance marks and measures on unmount
    return () => {
      performance.clearMarks();
      performance.clearMeasures();
    };
  }, []);

  return (
    <ErrorBoundary>
      <QueryClientProvider client={queryClient}>
        <AuthProvider>
          <BrowserRouter>
            <Routes>
              {/* Public Routes */}
              <Route path="/auth/login" element={<LoginForm />} />

              {/* Protected Routes */}
              <Route
                path="/"
                element={
                  <ProtectedRoute>
                    <AppLayout />
                  </ProtectedRoute>
                }
              >
                {/* Admin Routes */}
                <Route
                  path="admin"
                  element={
                    <ProtectedRoute requiredRole="admin">
                      <AdminDashboard />
                    </ProtectedRoute>
                  }
                />
                <Route
                  path="admin/users"
                  element={
                    <ProtectedRoute requiredRole="admin">
                      <UserManagement />
                    </ProtectedRoute>
                  }
                />
                <Route
                  path="admin/rates"
                  element={
                    <ProtectedRoute requiredRole="admin">
                      <RateCardManagement />
                    </ProtectedRoute>
                  }
                />

                {/* Client Routes */}
                <Route
                  path="client"
                  element={
                    <ProtectedRoute requiredRole="client">
                      <ClientDashboard />
                    </ProtectedRoute>
                  }
                />
                <Route
                  path="client/quotes/new"
                  element={
                    <ProtectedRoute requiredRole="client">
                      <QuoteForm />
                    </ProtectedRoute>
                  }
                />
                <Route
                  path="client/quotes"
                  element={
                    <ProtectedRoute requiredRole="client">
                      <QuoteList />
                    </ProtectedRoute>
                  }
                />
                <Route
                  path="client/quotes/:id"
                  element={
                    <ProtectedRoute requiredRole="client">
                      <QuoteDetail />
                    </ProtectedRoute>
                  }
                />

                {/* Default Route */}
                <Route
                  path="/"
                  element={
                    <Navigate
                      to="/admin"
                      replace
                    />
                  }
                />
              </Route>
            </Routes>
          </BrowserRouter>
        </AuthProvider>
      </QueryClientProvider>
    </ErrorBoundary>
  );
};

export default App;
