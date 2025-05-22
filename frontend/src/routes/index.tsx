import React from 'react';
import { createBrowserRouter, RouteObject } from 'react-router-dom';
import { AppLayout } from '../components/layout/AppLayout';
import { crmRoutes } from './crm.routes';
import { Dashboard } from '../pages/Dashboard';
import { Navigate } from 'react-router-dom';

// Import other route groups here
// import { quoteRoutes } from './quote.routes';
// import { customerRoutes } from './customer.routes';

const routes: RouteObject[] = [
  {
    path: '/',
    element: <AppLayout />,
    children: [
      {
        index: true,
        element: <Navigate to="/dashboard" replace />,
      },
      {
        path: '/dashboard',
        element: <Dashboard />,
      },
      ...crmRoutes,
      // ...quoteRoutes,
      // ...customerRoutes,
    ],
  },
];

export const router = createBrowserRouter(routes);
