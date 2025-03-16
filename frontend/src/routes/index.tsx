import React from 'react';
import { createBrowserRouter, RouteObject } from 'react-router-dom';
import { AppLayout } from '../components/layout/AppLayout';
import { crmRoutes } from './crm.routes';

// Import other route groups here
// import { quoteRoutes } from './quote.routes';
// import { customerRoutes } from './customer.routes';

const routes: RouteObject[] = [
  {
    path: '/',
    element: <AppLayout />,
    children: [
      {
        path: '/',
        element: <div>Dashboard</div>, // TODO: Add Dashboard component
      },
      ...crmRoutes,
      // ...quoteRoutes,
      // ...customerRoutes,
    ],
  },
];

export const router = createBrowserRouter(routes);
