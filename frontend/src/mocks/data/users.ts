import { User } from '../../types/user';

export const mockUsers: User[] = [
  {
    id: 'user-1',
    name: 'John Admin',
    email: 'admin@example.com',
    role: 'admin',
    createdAt: '2023-01-01T00:00:00Z',
    updatedAt: '2023-01-01T00:00:00Z',
  },
  {
    id: 'user-2',
    name: 'Jane Client',
    email: 'client@example.com',
    role: 'client',
    createdAt: '2023-01-01T00:00:00Z',
    updatedAt: '2023-01-01T00:00:00Z',
  },
];
