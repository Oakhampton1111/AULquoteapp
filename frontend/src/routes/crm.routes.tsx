import React from 'react';
import { RouteObject } from 'react-router-dom';
import { CRMDashboard } from '../components/crm/Reports/CRMDashboard';
import { CustomerProfile } from '../components/crm/CustomerProfile/CustomerProfile';
import { KanbanBoard } from '../components/crm/KanbanBoard/KanbanBoard';
import { CustomerList } from '../components/crm/CustomerList/CustomerList';

export const crmRoutes: RouteObject[] = [
  {
    path: '/crm',
    children: [
      {
        path: 'dashboard',
        element: <CRMDashboard />,
      },
      {
        path: 'customers',
        element: <CustomerList />,
      },
      {
        path: 'customers/:id',
        element: <CustomerProfile />,
      },
      {
        path: 'deals',
        element: <KanbanBoard />,
      },
    ],
  },
];
