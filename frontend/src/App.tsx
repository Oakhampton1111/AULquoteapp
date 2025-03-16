import React from 'react';
import { BrowserRouter, Routes, Route, Navigate } from 'react-router-dom';
import { QueryClient, QueryClientProvider } from '@tanstack/react-query';
import { ReactQueryDevtools } from '@tanstack/react-query-devtools';
import { AuthProvider } from './services/auth/AuthContext';
import { ProtectedRoute } from './components/auth/ProtectedRoute';
import { AppLayout } from './components/layout/AppLayout';
import { LoginForm } from './components/auth/LoginForm';
import { ErrorBoundary } from './components/common/ErrorBoundary';
import { message } from 'antd';

// Admin Components
import { AdminDashboard } from './pages/admin/Dashboard';
import { UserManagement } from './components/admin/UserManagement/UserManagement';
import { RateCardManagement } from './components/admin/RateCard/RateCardManagement';

// Client Components
import { ClientDashboard } from './pages/client/Dashboard';
import { QuoteForm } from './components/client/QuoteForm/QuoteForm';
import { QuoteList } from './components/client/QuoteList/QuoteList';

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
    },
    mutations: {
      retry: 1,
    },
  },
});

const App: React.FC = () => {
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
        <ReactQueryDevtools initialIsOpen={false} />
      </QueryClientProvider>
    </ErrorBoundary>
  );
};

export default App;
