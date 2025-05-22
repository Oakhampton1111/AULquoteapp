import React from 'react';
import { useAuth } from '../hooks/useAuth';
import { AdminDashboard } from './admin/Dashboard';
import { CustomerDashboard } from './client/Dashboard';

/**
 * Dashboard page that renders the appropriate dashboard
 * based on the current user's role.
 */
export const Dashboard: React.FC = () => {
  const { user } = useAuth();

  if (!user) {
    return null;
  }

  const isAdmin = Array.isArray((user as any).roles)
    ? (user as any).roles.includes('admin')
    : (user as any).role === 'admin';

  return isAdmin ? <AdminDashboard /> : <CustomerDashboard />;
};
