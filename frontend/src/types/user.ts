export interface User {
  id: string;
  name: string;
  email: string;
  role: 'admin' | 'client';
  isActive: boolean;
  createdAt: string;
  updatedAt: string;
}

export interface UserFormData {
  name: string;
  email: string;
  password?: string;
  role: 'admin' | 'client';
  isActive: boolean;
}
